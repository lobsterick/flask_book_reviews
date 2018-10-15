import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://xemwreuheugywl:0627c446dabea810bbdc8a40fa520abc97d2e9f4a810fa92dd34f084f546bf8c@ec2-23-23-80-20.compute-1.amazonaws.com:5432/d79jvs5qaaj3ol")
db = scoped_session(sessionmaker(bind=engine))


def main():
    book_csv = open("books.csv")
    reader = csv.reader(book_csv)
    for isbn, title, author, publication_year in reader:
        db.execute("INSERT INTO books (isbn, title, author, publication_year) VALUES (:isbn, :title, :author, :publication_year)",
                   {"isbn": isbn, "title": title, "author": author, "publication_year": publication_year})
        print(f"Added book ISBN: {isbn} ({title})")
    db.commit()

if __name__ == "__main__":
    main()
