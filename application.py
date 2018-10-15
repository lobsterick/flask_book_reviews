from flask import Flask, session, request, render_template, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"] = "YOUR_DATABASE_URL_HERE"
goodreads_key = "YOU_KEY_HERE"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form["username"]
    password = request.form["password"]

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
        return render_template("index.html", info_type="error", info_text="Invalid user name")
    elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                    {"username": username, "password": password}).rowcount == 1:
        session['logged_in'] = True
        session["username"] = username
        return render_template("index.html", info_type="succes", info_text="You are logged in now!")
    else:
        return render_template("index.html", info_type="error", info_text="Invalid password")


@app.route("/logout")
def logout():
    if session.get('logged_in'):
        session["username"] = None
        session['logged_in'] = False
        return render_template("index.html", info_type="neutral", info_text="You have been logged out succesfully!")
    else:
        return redirect(url_for('home'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if session.get('logged_in'):
            return render_template("index.html", info_type="error", info_text="You are already registered! How do you managed to get here?!")
        else:
            return render_template("registration.html")

    if request.method == "POST":
        new_username = request.form["new_username"]
        new_password = request.form["new_password"]

        if db.execute("SELECT * FROM users WHERE username = :username", {"username": new_username}).rowcount != 0:
            return render_template("registration.html", info_type="neutral", info_text="This nickname is already taken.")

        try:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :usrpassword)", {'username': new_username, 'usrpassword': new_password})
            db.commit()
        except Exception:
            return render_template("registration.html", info_type="neutral", info_text="Something goes horribly wrong when trying add new user. Try again.")

        return render_template("index.html", info_type="succes", info_text="You have been added to our users. Congratulation! Now you can log in.")


@app.route("/search", methods=['POST'])
def search():
    if session.get('logged_in'):
        search_phrase = request.form["search"]
        finded = db.execute("SELECT * FROM books WHERE title LIKE :phrase OR isbn LIKE :phrase OR author like :phrase", {"phrase": f"%{search_phrase}%"}).fetchall()
        return render_template("search_result.html", search_phrase=search_phrase, results=finded)
    else:
        return render_template("index.html", info_type="error", info_text="You must first log in to preform search.")


@app.route("/book/<isbn>")
def book_page(isbn):
    if session.get('logged_in'):
        is_commented_already = db.execute("SELECT * FROM comments WHERE author = :username AND isbn = :isbn", {"username": session["username"], "isbn": isbn}).rowcount
        if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 1:
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
            if db.execute("SELECT * FROM comments WHERE isbn = :isbn", {"isbn": isbn}).rowcount != 0:
                comments = db.execute("SELECT * FROM comments WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
                comments_numbers = len(comments)
                comments_avg = db.execute("SELECT AVG(rating) FROM comments WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
                comments_avg = round(comments_avg[0], 2)
            else:
                comments = None
                comments_numbers = "no"
                comments_avg = "N/A"
            goodreads_response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreads_key, "isbns": isbn})
            if goodreads_response.status_code == 200:
                goodreads_info = goodreads_response.json()
                goodreads_rating = goodreads_info['books'][0]['average_rating']
                goodreads_rating_voters_number = goodreads_info['books'][0]['work_ratings_count']

                return render_template("book_page.html", book=book, comments=comments, is_commented = is_commented_already, goodreads_rating=goodreads_rating, goodreads_rating_voters_number=goodreads_rating_voters_number, user=session["username"], comments_numbers=comments_numbers, comments_avg=comments_avg)

            else:

                return render_template("book_page.html", book=book, comments=comments, is_commented =is_commented_already, comments_numbers=comments_numbers, comments_avg=comments_avg)

        else:
            return render_template("index.html", info_type="error", info_text="There is no book associated with providen ISBN.")
    return render_template("index.html", info_type="error", info_text="You must first log in to use our database.")


@app.route("/book/<isbn>/addcomment", methods=["POST"])
def add_comment(isbn):
    if session.get('logged_in'):
        new_comment_rating = request.form["new_rating"]
        new_comment_body = request.form["new_comment_body"]
        new_comment_author = session["username"]
        if db.execute("SELECT * FROM comments WHERE author = :username AND isbn = :isbn", {"username": new_comment_body, "isbn": isbn}).rowcount == 0:
            try:
                db.execute("INSERT INTO comments (isbn, author, rating, comment_body) VALUES (:isbn, :author, :rating, :comment_body)",
                           {'isbn': isbn, 'author': new_comment_author, 'rating': new_comment_rating, 'comment_body': new_comment_body})
                db.commit()
                return redirect(f"/book/{isbn}")
            except Exception:
                return render_template("index.html", info_type="neutral", info_text="Something goes horribly wrong when adding comment. Try again later.")
        else:
            render_template("index.html", info_type="neutral", info_text="You already comment this movie, but the real question here is - how did you manage to achieve this endpoint?!?")

    else:
        return render_template("index.html", info_type="error", info_text="You must first log in to add comment.")


@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    if db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 1:
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        comments = db.execute("SELECT * FROM comments WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
        comments_numbers = len(comments)
        comments_avg = db.execute("SELECT AVG(rating) FROM comments WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        comments_avg = float(round(comments_avg[0], 2))

        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.publication_year,
            "isbn": isbn,
            "review_count": comments_numbers,
            "average_score": comments_avg
        })
    else:
        return jsonify({"error": "Invalid isbn"}), 404

