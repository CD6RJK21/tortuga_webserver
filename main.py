from io import BytesIO

from flask import Flask, render_template, redirect, session, flash, \
    send_file, jsonify
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, logout_user
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from forms import *

app = Flask(__name__)
app.secret_key = '0bcfb47472328e90fbf26d4ef88d9d90'
app.config['SECRET_KEY'] = '0bcfb47472328e90fbf26d4ef88d9d90'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

render_template_old = render_template


@login_manager.user_loader
def load_user(user_id):
    return None


def render_template(html, **kwargs):
    searchform1 = SearchForm()
    return render_template_old(html, searchform=searchform1, **kwargs)


# database begins
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_active = True

    def __repr__(self):
        return '{}|||{}|||{}'.format(
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
        return '{}|||{}|||{}|||{}'.format(
            self.author, self.title, self.username, self.id)


def register_user(username1, email1, password1):
    user = User(username=username1, email=email1,
                password_hash=generate_password_hash(password1))
    db.session.add(user)
    db.session.commit()


def make_user_admin(id):
    if User.query.filter_by(id=id).all():
        User.query.filter_by(id=id).first().is_admin = True
        db.session.commit()
    return


def upload_book(username1, title1, author1, book_file1):
    author_free = False if list(
        Book.query.filter(Book.author == author1)) else True
    title_free = False if list(
        Book.query.filter(Book.title == title1)) else True
    if author_free or title_free:
        book_data = book_file1.read()
        book_name = book_file1.filename
        book = Book(username=username1, title=title1, author=author1,
                    book_file=book_data, file_name=book_name)
        db.session.add(book)
        db.session.commit()
    else:
        return 'Book already in db.'


def download_book(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    book = Book.query.filter_by(id=id).first()
    with open(book.file_name, 'wb') as file:
        file.write(book.book_file)


def get_book(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    book = Book.query.filter_by(id=id).first()
    return book


def delete_book(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    book = Book.query.filter_by(id=id).delete()
    db.session.commit()  # db.session.delete(user)


def book_exists(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    exists = Book.query.filter_by(id=id).scalar() is not None
    return exists


def user_exists(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    exists = User.query.filter_by(id=id).scalar() is not None
    return exists


def get_username(id):
    try:
        id = int(id)
    except ValueError as ve:
        print(ve)
    username = User.query.filter_by(id=id).username is not None
    return username


db.create_all()


# database ends.


# REST classes

class Books(Resource):
    def get(self, book_id):
        if book_exists(book_id):
            books = get_book(book_id)
            books = str(books)
            return jsonify({'books': books})

    def delete(self, book_id):
        if book_exists(book_id):
            delete_book(book_id)
            return jsonify({'success': 'OK'})


class BooksList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('author', required=True)
    parser.add_argument('username', required=True)

    def get(self):
        books = Book.query.all()
        books = list(map(lambda x: str(x), books))
        return jsonify({'books': books})

    def post(self):
        pass
        # args = self.parser.parse_args()
        # news = NewsModel(db.get_connection())
        # upload_book()
        # news.insert(args['title'], args['content'], args['user_id'])
        # return jsonify({'success': 'OK'})


class BookSearch(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('request', required=True)

    def get(self, request):
        form = SearchForm()
        books = Book.query.all()
        books = list(map(lambda x: str(x), books))
        books = Book.query.filter(
            Book.title.ilike(f'%{request}%') | Book.author.ilike(
                f'%{request}%'))
        books = books.order_by(Book.author).all()
        for book in books:
            if books.count(book) >= 2:
                books.remove(book)
        books = list(map(lambda x: str(x).split('|||'), books))
        return jsonify({'books': books})

    # return render_template('search.html', form=form, books=books, title='Поиск')

    def post(self):
        pass


@app.errorhandler(404)
def abort_if_page_notfound(page_id):
    abort(404, message="Page {} not found".format(page_id))
    print(page_id)


api.add_resource(BooksList, '/books')
api.add_resource(Books, '/books/<int:book_id>')
api.add_resource(BookSearch, '/booksearch/<request>')


# REST done


@app.route('/set_user_admin/<user_id>')
def set_user_admin(user_id):
    if not session['is_admin']:
        abort(403, message="Эта страница доступна только администратору")
        return redirect('/')
    if user_exists(user_id):
        make_user_admin(int(user_id))
    flash('Пользователю успешно предоставлены права администратора')
    return redirect('/all_users')


@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    if user_exists(user_id):
        try:
            id = int(user_id)
        except ValueError as ve:
            print(ve)
        if id == session['user_id']:
            return redirect('/all_users')
        user = User.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Пользователь успешно удалён')
    return redirect('/all_users')


@app.route('/download_file/<book_id>')
def download_file(book_id):
    book = Book.query.filter_by(id=int(book_id)).first()
    return send_file(BytesIO(book.book_file),
                     attachment_filename=book.file_name, as_attachment=True)


@app.route('/delete_file/<book_id>')
def delete_file(book_id):
    delete_book(int(book_id))
    flash('Книга удалена')
    return redirect('/index')


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return render_template('index.html', username='Гость',
                               title='Главная страница')
    else:
        if User.query.filter_by(id=session.get('user_id')).first().is_admin:
            session['is_admin'] = True
        books = Book.query.filter(
            Book.username == session['username']).order_by(Book.author).all()
        books = list(map(lambda x: str(x).split('|||'), books))
        return render_template('index.html', username=session['username'],
                               title='Главная страница', books=books)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    request = form.request.data
    books = []
    if request != '':
        books = Book.query.filter(
            Book.title.ilike(f'%{request}%') | Book.author.ilike(
                f'%{request}%'))
        books = books.order_by(Book.author).all()
        for book in books:
            if books.count(book) >= 2:
                books.remove(book)
        books = list(map(lambda x: str(x).split('|||'), books))
    return render_template('search.html', form=form, books=books,
                           title='Поиск')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')
    form = LoginForm()
    user_name1 = form.username.data
    password1 = form.password.data
    if form.validate_on_submit():
        user = User.query.filter(User.username == user_name1)
        user = list(user)
        if user:
            user = user[0]
            if user.check_password(password1):
                login_user(user)
                flash('Вы успешно вошли в систему.')
                session['username'] = user_name1
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                return redirect("/index")
            else:
                flash('Неверный логин или пароль.', 'error')
        else:
            flash('Неверный логин или пароль.', 'error')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    if 'username' in session:
        logout_user()
        session.pop('username', 0)
        session.pop('user_id', 0)
        session.pop('is_admin', 0)
    return redirect('/')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if 'username' in session:
        return redirect('/')
    form = SignUpForm()
    user_name1 = form.username.data
    email1 = form.email.data
    password1 = form.password.data
    if form.submit.data:
        user_name_free = False if list(
            User.query.filter(User.username == user_name1)) else True
        email_free = False if list(
            User.query.filter(User.email == email1)) else True
        if user_name_free and email_free:
            register_user(user_name1, email1, password1)
            flash('Вы успешно зарегестрированы.')
            return redirect("/login")
        else:
            flash('Имя пользователя или почта заняты.')
    return render_template('sign_up.html', title='Регистрация', form=form)


@app.route('/all_users')
def all_users():
    if not session['is_admin']:
        abort(403, message="Эта страница доступна только администратору")
        return redirect('/')
    users = User.query.all()
    users = list(map(lambda x: str(x), users))
    users1, users2 = [], []
    col = 1
    for user in users:
        user = user.split('|||')
        if col == 1:
            users1.append(user)
        else:
            users2.append(user)
        col = (col + 1) % 2
    return render_template('all_users.html', title='Список пользователей',
                           users1=users1, users2=users2)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    form = BookUploadForm()
    if form.validate_on_submit():
        author_free = False if list(
            Book.query.filter(Book.author == form.author.data)) else True
        title_free = False if list(
            Book.query.filter(Book.title == form.title.data)) else True
        if title_free or author_free:
            upload_book(session['username'], form.title.data, form.author.data,
                        form.file.data)
            flash('Книга успешно загружена.')
            return redirect("/index")
        else:
            flash('Такая книга уже есть.')
    return render_template('upload.html', title='Загрузка книги',
                           form=form, username='Adasd')  # session['username']


if __name__ == '__main__':
    # make_user_admin(User.query.filter_by(username='username_here').first().id)
    app.run(port=8080, host='127.0.0.1')
