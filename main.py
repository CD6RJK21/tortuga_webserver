from flask import Flask, request, render_template, redirect, session, flash
from flask_login import login_user, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *


app = Flask(__name__)
app.secret_key = '0bcfb47472328e90fbf26d4ef88d9d90'
app.config['SECRET_KEY'] = '0bcfb47472328e90fbf26d4ef88d9d90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

render_template_old = render_template

@login_manager.user_loader
def load_user(user_id):
    return None


# database begins
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=False, nullable=False)
    is_active = True

    def __repr__(self):
        return '<User {} {} {}>'.format(
            self.id, self.username, self.email)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    title = db.Column(db.String(500), unique=False, nullable=False)
    author = db.Column(db.String(120), unique=False, nullable=False)
    book_file = db.Column(db.LargeBinary(), nullable=False)
    file_name = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return '<Book {} {} {}>'.format(
            self.title, self.author, self.username)


def register_user(username1, email1, password1):
    user = User(username=username1, email=email1, password_hash=generate_password_hash(password1))
    db.session.add(user)
    db.session.commit()


def upload_book(username1, title1, author1, book_file1):
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
# database ends.


def render_template(html, **kwargs):
    searchform1 = SearchForm()
    return render_template_old(html, searchform=searchform1, **kwargs)


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return render_template('index.html', username='Гость')
    else:
        return render_template('index.html', username=session['username'])


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    request = form.request.data
    books = []
    books = Book.query.filter(Book.title.like('%' + request + '%'))
    books = Book.query.filter(Book.author.like('%' + request + '%'))
    books = list(books.order_by(Book.author).all())
    for book in books:
        if books.count(book) >= 2:
            books.remove(book)
    return render_template('search.html', form=form, books=books)
    # return render_template('courselist.html', courses = courses)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name1 = form.username.data
    password1 = form.password.data
    remember_me = form.remember_me.data
    if form.validate_on_submit():
        user = User.query.filter(User.username == user_name1)
        user = list(user)
        if user:
            user = user[0]
            if user.check_password(password1):
                login_user(user, remember=remember_me)
                flash('Вы успешно вошли в систему.')
                session['username'] = user_name1
                session['user_id'] = user.id
                return redirect("/index")
            else:
                flash('Неверный логин или пароль.', 'error')
        else:
            flash('Неверный логин или пароль.', 'error')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    user_name1 = form.username.data
    email1 = form.email.data
    password1 = form.password.data
    if form.submit.data:
        user_name_free = False if list(User.query.filter(User.username == user_name1)) else True
        email_free = False if list(User.query.filter(User.email == email1)) else True
        if user_name_free and email_free:
            register_user(user_name1, email1, password1)
            flash('Вы успешно зарегестрированы.')
            return redirect("/index")
        else:
            flash('Имя пользователя или почта заняты.')
    return render_template('sign_up.html', title='Регистрация', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    form = BookUploadForm()
    if form.validate_on_submit():
        upload_book('Adasd', form.title.data, form.author.data, form.file.data)  # TODO: make login page
        return redirect("/index")
    return render_template('upload.html', title='Загрузка книги',
                           form=form, username='Adasd')  # session['username']


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
