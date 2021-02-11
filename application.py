import os, json

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    #homepage
    return render_template("index.html")




@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
    #If user is logging in
    if request.method=="POST":
        #get username and password from form
        uname=request.form.get("username")
        passw=request.form.get("password")
        temp=db.execute("SELECT * FROM users WHERE username = :username AND pass = :pass",{"username":uname, "pass":passw})
        temp2=temp.fetchone()
        #start a session for the user
        session["uid"]=temp2[0]
        #see if password and username are correct
        if db.execute("SELECT * FROM users WHERE username = :username AND pass = :pass",{"username":uname, "pass":passw}).rowcount ==1:
            return redirect("/lookup")
        return render_template("error.html", message="Username or Password is not correct")
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    #if the user is inputing data
    if request.method=="POST":
    #see if the firstname is a string
        first_name=request.form.get("fname")
        try:
            first_name=str(first_name)
        except ValueError:
            return render_template("error.html", message="Invalid First Name")

        #see if the lastname is a string
        last_name=request.form.get("lname")
        try:
            last_name=str(last_name)
        except ValueError:
            return render_template("error.html", message="Invalid Last Name")

        #Check if passwords match
        passw=request.form.get("password")
        cpass=request.form.get("confpassword")
        try:
            passw==cpass
        except ValueError:
            return render_template("error.html", message="Passwords Don't Match")

            #See if username exsist, if not add user to data base
        uname=request.form.get("username")
        if db.execute("SELECT * FROM users WHERE username = :username",{"username":uname}).rowcount >0:
            return render_template("error.html", message="Username is already taken")
        db.execute("INSERT INTO users (username, pass, fname, lname) VALUES (:uname, :passw, :first_name, :last_name)",
                {"uname": uname,"passw": passw, "first_name": first_name, "last_name": last_name})
        db.commit()

        return redirect("/login")
    #if user method is GET
    else:
        return render_template("signup.html")

@app.route("/lookup")
def lookup():
    return render_template("lookup.html")

@app.route("/search", methods=["GET"])
def search():

    #get search result and make it so it doesnt have to be exactly right
    searched= "%"+request.args.get("searched")+"%"

    #Check to see if any books match if not return error page
    if db.execute("SELECT isbn, title, author, yer FROM books WHERE isbn LIKE :searched OR title LIKE :searched OR author LIKE :searched LIMIT 5",{"searched": searched}).rowcount ==0:
        return render_template ("error.html", message="No books found")
    #find the books from the data base and store info
    data=db.execute("SELECT isbn, title, author, yer FROM books WHERE isbn LIKE :searched OR title LIKE :searched OR author LIKE :searched LIMIT 5",
                {"searched": searched})
    #Get every result
    books=data.fetchall()
    return render_template("books.html",books=books)


@app.route("/rating/<isbn>", methods=["GET","POST"])
def rating(isbn):

    if request.method=="POST":
        userRating=request.form.get("UserRatings")
        userComment=request.form.get("UserComment")
        isbbn=request.form.get("ConfirmISBN")
        uid=session["uid"]
        user=uid


        #see if the user has reviewed this book before
        if db.execute("SELECT * FROM reviews WHERE uid = :uid AND isbn = :isbn", {"uid":uid,"isbn":isbbn}).rowcount >0:
            return render_template("error.html",message="You cant review a book more than once")

        #insert rating and comment for book into reviews db
        db.execute("INSERT INTO reviews (rating, com, uid, isbn) VALUES (:userRating, :userComment, :uid, :isbn)",
                { "userRating": userRating, "userComment": userComment, "uid":uid, "isbn": isbbn})
        db.commit()

        return redirect("/lookup")

    else:
        #Get all book info based on primary key isbn
        temp=db.execute("SELECT isbn, title, author, yer FROM books WHERE isbn=:isbn",{"isbn":isbn})

        books=temp.fetchall()

        #get api info
        temp1="isbn:"
        temp2=str(isbn)
        val=temp1+temp2
        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": val})
        if res.status_code !=200:
            raise Exception ("ERROR: API Not Successful")
        data=res.json()
        try:
            averageRating=data["items"][0]["volumeInfo"]["averageRating"]
            ratingsCount=data["items"][0]["volumeInfo"]["ratingsCount"]
        except KeyError:
            averageRating="Not Available"
            ratingsCount="Not Available"


        #get other users Reviews
        temp2=db.execute("SELECT * FROM reviews WHERE isbn=:isbn",{"isbn":books[0][0]})
        reviews=temp2.fetchall()


        return render_template("rating.html",books=books,averageRating=averageRating,ratingsCount=ratingsCount, reviews=reviews)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route("/api/<isbn>")
def api(isbn):
    #Get all info about book and rating
    information=db.execute("SELECT isbn, title, author, yer  FROM books WHERE isbn = :isbn", {"isbn":isbn})
    information=information.fetchall()
    rate=db.execute("SELECT * FROM reviews WHERE isbn=:isbn",{"isbn":isbn})
    ratingCount=rate.rowcount
    ratingCount=int(ratingCount)
    rrr=db.execute("SELECT AVG(rating) FROM reviews WHERE isbn=:isbn",{"isbn":isbn})
    b=rrr.fetchall()
    #make avg rating a string
    a=str(b[0][0])
    #if isbn is an sbn then make an isbn10
    if len(isbn)==9:
        isbn="0"+isbn
    isbn=str(isbn)
    #if isbn is isbn10 then make isbn13
    if len(isbn) ==10:
        isbntemp1="978"
        isbntemp2=isbn[:-1]
        isbn13=isbntemp1+isbntemp2
        checkdig=0
        for x in range(len(isbn13)):
            intt=int(isbn13[x])
            if x%2!=0:
                checkdig=checkdig+(intt*1)
            if x%2==0:
                checkdig=checkdig+(intt*3)
        fincheck=10-(checkdig%10)
        fincheck=str(fincheck)
        isbn13=isbn13+fincheck
        isbn10=isbn
    #if isbn is isbn13 then make isbn 10
    if len(isbn)==13:
        #get rid of first 3 dig
        isbn10=isbn[3:]
        #get rid of check dig
        isbn10=isbn10[:-1]
        checkdig=0
        for t in range(len(isbn10)):
            intt=int(isbn10[t])
            checkdig=checkdig+((10-t)*intt)
        fincheck=11-(checkdig%11)
        fincheck=str(fincheck)
        if fincheck==10:
            isbn10=isbn10+"X"
        else:
            isbn10=isbn10+fincheck
        isbn13=isbn


    #avgRating=summation/ratingCount
    for info in information:
        for rat in b:
            return jsonify({
                    "title":info['title'],
                    "author":info['author'],
                    "publishedDate":info['yer'],
                    "ISBN_10":isbn10,
                    "ISBN_13":isbn13,
                    "reviewCount":ratingCount,
                    "averageRating":a

                })
