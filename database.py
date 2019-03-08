from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, session


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<User {} {} {}>'.format(
            self.id, self.username, self.email)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    title = db.Column(db.String(500), unique=False, nullable=False)
    author = db.Column(db.String(120), unique=False, nullable=False)
    book_file = db.Column(db.LargeBinary(), nullable=False)
    file_name = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<Book {} {} {} {}>'.format(
            self.id, self.username, self.title, self.author)


def register_user(username1, email1, password1):
    user = User(username=username1, email=email1, password_hash=generate_password_hash(password1))
    db.session.add(user)
    db.session.commit()


def add_book(username1, title1, author1, book_file1):
    book_data = book_file1.read()
    book_name = book_file1.filename
    book = Book(username=username1, title=title1, author=author1, book_file=book_data, file_name=book_name)
    db.session.add(book)
    db.session.commit()


def download_book(id):
    book = Book.query.filter_by(id=id).first()
    with open(book.file_name, 'wb') as file:
        file.write(book.book_file)


db.create_all()
# download_book(4)
# with open('IMG_20160607_211335.jpg', 'rb') as file:
#     add_book('asdsafs11f', 'asdf44sdf', 'sadfsadf', file)


