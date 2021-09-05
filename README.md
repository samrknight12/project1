# Project 1

# Check Out The Video Walkthrough of This Project!
[Watch the Video!!](https://www.youtube.com/watch?v=L1DGxleCbxw "Video Here!")

In index.html there is the homepage where you can choose to login or sign up. If signup is chosen the signup.html page appears and asks for a username, password, password confirmation, first name, and last name. The application checks if the username is available. If it is the user is redirected to the login page and their info is stored in the database. The login.html page appears and asks the user to submit their username and password. The application checks if these are correct, if not an error page appears. If they are correct then the search.html page appears. The search.html page asks the user to input an isbn, author, or title. They are then redirected to books.html where a list of books appears that match or slightly match the users input. After each book there is a link to rate the book. If clicked it takes the user to a rating.html page where they can see the Google books API ratings and number of ratings, they can input their own rating and comment, and they can see other users ratings and comments.

The databases are books, users, reviews. In books there is an ISBN column which is the primary key, a title column, an author column, and a year column. In user there is a user id as the primary key, username column, password column, first name column, and last name column. In reviews there is a review ID as primary key, a rating column, a comment column, an isbn column, and a foreign key column for the users ID. 
ENGO 551
