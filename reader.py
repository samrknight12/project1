import csv
import os

from sqlalchemy import create_engine
from sqlalchemy import scoped_session, sessionmaker

engine=create_engine(os.getenv("postgres://loabxdcstohnws:7636fb070d8cc3d4683aeb4ae1067b28ee54d30cf4a225cec1b0273a6228b6ea@ec2-54-90-13-87.compute-1.amazonaws.com:5432/d3ghm5lvd0pnil"))
db=scoped_session(sessionmaker(bind=engine))

def main():
    f=open("books.csv")
    reader=csv.reader(f)
    for origin, destination, duration in reader:
        db.execute("INSERT INTO books (isbn, title, author, yer) VALUE (:isbn, :title, :author, :yer)",
            {"isbn": isbn, "title": title, "author": author, "yer": yer})
    db.commit()

if __name__ == "__main__":
    main()
