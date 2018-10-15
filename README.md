# Flask "Book Review" Page
This repository contain complete Flask Web Application for book cataloging with own database and review section.

## What's inside?
Inside this repo, you can find 3 main files - `application.py`, `import.py` and `create_database.py`.
### application.py

This is Flask file for using web app with possibility of:
* log in and log out
* register new user
* keep track of user's session
* search books by title, author and ISBN in one form, that appears <u>only for logged users</u>
* book page as a hyperlink from search results, that contains details of books, rating from GoodRead and all comments from app site
* make comments in all book pages (<u>one comment per user for every book</u>)
* simple API, sending back JSON file with info about asked ISBN (if present in attached database)

### import.py

This is python script, importing CSV data from `books.csv` file (*a 5000 book database available in this project*) to database located on Heroku's PostgreSQL.

### create_database

This is python script creating all databases necessary in this project.


## Technologies used
* **Backend** - Flask (Python)

* **Frontend** - Bootstrap 4, Jinja2, HTML, CSS

* **Database** - SQLAlchemy (*Python*), PostgreSQL, Heroku

All database - related operation in Flask was implemented using raw SQL commands.


## How to use?

1. Start project on Heroku and get ([<u>for free</u>](http://www.heroku.com)) database URL.
2. Get key from GoodRead's API ([<u>free too</u>](http://www.goodreads.com/api)).
3. *[optional]* Add your books to `books.csv` database.
4. Run `create_database.py`  (<u>remember to insert your database URL</u>).
5. Run `import.py` (<u>remember to insert your database URL and API_key</u>)
4. Start server from `application.py`.
5. Go to server IP page (something like `127.0.0.1:500`).

Database URL and API-Key should be paste in following lines:

`app.config["SQLALCHEMY_DATABASE_URI"] = "YOUR_DATABASE_URL_HERE"
`    
`goodreads_key = "YOU_KEY_HERE"
`

## Using API
App contain simple API, that can be accessible via a **GET** request to `/API/ISBN` route, where `ISBN` is an ISBN number of book. In this scenario, page will  return a JSON response containing the books title, author, publication date, ISBN number, review count, and average score. If book is in database, it should return error page.
