import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("YOUR_DATABASE_URL_HERE")
db = scoped_session(sessionmaker(bind=engine))

generate_user = 1
generate_books = 1
generate_comments = 1


def main():
    if generate_user == 1:
        engine.execute('''
            CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR NOT NULL,
            password VARCHAR NOT NULL)''')

        print("User Database Maked!")
        engine.execute('''INSERT INTO users (username, password) VALUES ('admin', 'password')''')


    if generate_books == 1:
        engine.execute('''
            CREATE TABLE books (
            book_id SERIAL PRIMARY KEY,
            isbn VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            publication_year INTEGER NOT NULL)''')
        print("Book Database Maked!")

    if generate_comments == 1:
        engine.execute('''
        CREATE TABLE comments (
        comment_id SERIAL PRIMARY KEY,
        isbn VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        rating INTEGER NOT NULL,
        comment_body VARCHAR NOT NULL)''')
        print("Comments Database Maked!")


if __name__ == "__main__":
    main()
