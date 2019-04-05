from io import BytesIO
from os import remove

from flask import Flask, render_template, redirect, session, flash, \
    send_file, jsonify, request
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
app.config['JSON_AS_ASCII'] = False

Bootstrap(app)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

render_template_old = render_template
search_request = ''


@login_manager.user_loader
def load_user(user_id):
    return None


def render_template(html, **kwargs):
    searchform = SearchForm()
    return render_template_old(html, searchform=searchform, **kwargs)


# database begins
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(240), unique=False, nullable=False)
    full_name = db.Column(db.String(240), unique=False, nullable=False)
    have_image = db.Column(db.Boolean(), default=False)
    description = db.Column(db.String(1024), unique=False, nullable=True)
    image_extension = db.Column(db.String(120), unique=False, nullable=False,
                                default='')

    def __repr__(self):
        return '{}|||{}|||{}|||{}'.format(
            self.id, self.display_name, self.full_name, self.description)


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
    return


def add_author(display_name, full_name, description, image):
    if type(image).__name__ == 'FileStorage':
        image_data = image.read()
        image_name = image.filename
        has_image = True
    else:
        has_image = False
    if has_image:
        if '.' in image_name:
            extension = image_name.split('.')[-1]
        else:
            extension = ''
    else:
        extension = ''
    author = Author(display_name=display_name, full_name=full_name,
                    have_image=has_image, image_extension=extension,
                    description=description)
    db.session.add(author)
    db.session.commit()
    if has_image:
        self_id = str(author.id)
        with open(
                '{}'.format(
                    'static/author_img/{}.{}'.format(self_id, extension)),
                'wb') as saving_image:
            saving_image.write(image_data)
    return


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
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        book = Book.query.filter_by(id=id).first()
        with open(book.file_name, 'wb') as file:
            file.write(book.book_file)


def get_book(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        book = Book.query.filter_by(id=id).first()
        return book


def delete_book(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        book = Book.query.filter_by(id=id).delete()
        db.session.commit()  # db.session.delete(user)


def author_exists(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        exists = Author.query.filter_by(id=id).scalar() is not None
        return exists
    return False


def book_exists(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        exists = Book.query.filter_by(id=id).scalar() is not None
        return exists
    return False


def user_exists(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        exists = User.query.filter_by(id=id).scalar() is not None
        return exists
    return False


def get_username(id):
    if str(id).isdigit():
        try:
            id = int(id)
        except ValueError as ve:
            print(ve)
        username = User.query.filter_by(id=id).username is not None
        return username
    return 'No_such_username'


def check_user_privileges():
    if 'username' in session:
        user = User.query.filter(User.username == session['username']).first()
        session['is_admin'] = user.is_admin


db.create_all()


# database ends.


# API classes

class Books(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('book_id', required=False)

    def get(self):
        args = self.parser.parse_args()
        books = Book.query.all()
        # books = list(map(lambda x: str(x), books))
        if args.get('book_id') is None:
            books1 = {}
            for book in books:
                books1[book.id] = {
                    'title': book.title,
                    'author': book.author,
                    'username': book.username,
                }
            return jsonify({'books': books1})
        else:
            if book_exists(args.get('book_id')):
                book = Book.query.filter_by(
                    id=int((args.get('book_id')))).first()
                books1 = {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'username': book.username,
                }
                return jsonify({'books': books1})


class BookSearch(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('request', required=True)

    def get(self):
        args = self.parser.parse_args()
        request1 = str(args['request'])
        books = []
        if request1 != '':
            books = Book.query.filter(
                Book.title.ilike(f'%{request1.lower()}%') | Book.author.ilike(
                    f'%{request1.lower()}%') | Book.title.ilike(
                    f'%{request1.upper()}%') | Book.author.ilike(
                    f'%{request1.upper()}%'))
            books = books.order_by(Book.author).all()
            n = len(books)
            i = 0
            while i < n:
                if books.count(books[i]) >= 2:
                    books.remove(books[i])
                    n -= 1
                    i -= 1
                i += 1

            books1 = []
            for book in books:
                books1.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'username': book.username,
                })
            return jsonify({'books': books1})
        else:
            return jsonify({'error': 'empty request'})


class DownloadBook(Resource):
    def get(self, book_id):
        if book_exists(book_id):
            book = Book.query.filter_by(id=book_id).first()
            data = book.book_file
            file_name = book.file_name
            return jsonify({'file_name': file_name, 'data': data})
        return jsonify({'error': 'book with such id is not found'})


api.add_resource(Books, '/books/')
api.add_resource(BookSearch, '/booksearch')
api.add_resource(DownloadBook, '/download_book/<book_id>')


# API done


@app.route('/set_user_admin/<user_id>')
def set_user_admin(user_id):
    if not session['is_admin']:
        abort(403, message="Эта страница доступна только администратору")
        return redirect('/')
    if user_exists(user_id):
        make_user_admin(int(user_id))
    flash('Пользователю успешно предоставлены права администратора')
    check_user_privileges()
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


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    if author_exists(author_id):
        try:
            id = int(author_id)
        except ValueError as ve:
            print(ve)
        author = Author.query.filter_by(id=id).first()
        if author.have_image:
            image = str(author.id) + '.' + author.image_extension
            image = 'static/author_img/' + image
            remove(image)
        author = Author.query.filter_by(id=id).delete()
        db.session.commit()
        flash('Автор успешно удалён')
    return redirect('/')


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
    check_user_privileges()
    search_request = ''
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
    check_user_privileges()
    request1 = str(request.args['request'])
    form = SearchForm()
    books = []
    if request1 != '':
        global search_request
        search_request = request1[:]
        books = Book.query.filter(
            Book.title.ilike(f'%{request1.lower()}%') | Book.author.ilike(
                f'%{request1.lower()}%') | Book.title.ilike(
            f'%{request1.upper()}%') | Book.author.ilike(
            f'%{request1.upper()}%'))
        books = books.order_by(Book.author).all()
        books = list(map(lambda x: str(x).split('|||'), books))
        n = len(books)
        i = 0
        while i < n:
            if books.count(books[i]) >= 2:
                books.remove(books[i])
                n -= 1
                i -= 1
            i += 1

        authors = Author.query.filter(
            Author.full_name.ilike(
                f'%{request1}%') | Author.display_name.ilike(
                f'%{request1}%'))
        authors = authors.order_by(Author.display_name).all()
        authors = list(map(lambda x: str(x).split('|||'), authors))
        n = len(authors)
        i = 0
        while i < n:
            if authors.count(authors[i]) >= 2:
                authors.remove(authors[i])
                n -= 1
                i -= 1
            i += 1

    return render_template('search.html', form=form, books=books,
                           authors=authors,
                           title='Поиск')


@app.route('/book_edit/<book_id>', methods=['GET', 'POST'])
def book_edit(book_id):
    check_user_privileges()
    if not book_exists(book_id) or not session['is_admin']:
        if search_request != '':
            return redirect('search?request={}'.format(search_request))
        else:
            return redirect('/index')
    book = Book.query.filter_by(id=book_id).first()
    form = BookEditForm()
    if form.validate_on_submit():
        book = Book.query.filter_by(id=book_id).first()
        book.author = form.author.data
        book.title = form.title.data
        db.session.flush()
        db.session.commit()
        if search_request != '':
            return redirect('search?request={}'.format(search_request))
        else:
            return redirect('/index')
    form.title.data = book.title
    form.author.data = book.author
    return render_template('book_edit.html', title='Редактирование книги',
                           form=form)


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
    session['is_admin'] = False
    return redirect('/')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if 'username' in session:
        return redirect('/')
    form = SignUpForm()
    user_name1 = form.username.data
    email1 = form.email.data
    password1 = form.password.data
    password_repeat = form.password_repeat.data
    if form.submit.data:
        user_name_free = False if list(
            User.query.filter(User.username == user_name1)) else True
        email_free = False if list(
            User.query.filter(User.email == email1)) else True
        if user_name_free and email_free:
            if password_repeat == password1:
                register_user(user_name1, email1, password1)
                flash('Вы успешно зарегестрированы.')
                return redirect("/login")
            else:
                flash('Введённые пароли не совпадают')
        else:
            flash('Имя пользователя или почта заняты.')
    return render_template('sign_up.html', title='Регистрация', form=form)


@app.route('/all_users')
def all_users():
    if not session['is_admin']:
        abort(403, message="Эта страница доступна только администратору")
        return redirect('/')
    users = User.query.all()
    users = list(map(lambda x: str(x).split('|||'), users))
    return render_template('all_users.html', title='Список пользователей',
                           users=users)


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
                           form=form, username=session['username'])


@app.route('/register_author', methods=['GET', 'POST'])
def register_author():
    if 'username' not in session:
        return redirect('/login')
    form = AuthorRegisterForm()
    if form.validate_on_submit():
        add_author(form.display_name.data, form.full_name.data,
                   form.description.data, form.image.data)
        flash('Автор успешно добавлен.')
        return redirect("/index")
    return render_template('register_author.html', title='Добавление автора',
                           form=form, username=session['username'])


@app.route('/author/<id>', methods=['GET'])
def author_page(id):
    if not author_exists(int(id)):
        flash('Автора с таким id не существует.')
        return redirect('/')
    check_user_privileges()
    author = Author.query.filter_by(id=id).first()
    if author.have_image:
        image = str(author.id) + '.' + author.image_extension
        image = '/static/author_img/' + image
    else:
        image = '/static/author_img/default.png'
    author_names = author.display_name.split() + author.full_name.split()
    books = []
    for name in author_names:
        if len(name) >= 3:
            books += Book.query.filter(Book.author.ilike(f'%{name}%')).all()
    books = list(map(lambda x: str(x).split('|||'), books))
    n = len(books)
    i = 0
    while i < n:
        if books.count(books[i]) >= 2:
            books.remove(books[i])
            n -= 1
            i -= 1
        i += 1
    if '\n\n' in author.description:
        description = author.description.split('\n')
    else:
        description = [author.description]
    return render_template('author.html', title=author.display_name,
                           full_name=author.full_name, image=image,
                           description=description, books=books,
                           id=author.id)


if __name__ == '__main__':
    '''Чтобы сделать пользователя админом вызовите следующую функцию'''
    # make_user_admin(User.query.filter_by(username='username_here').first().id)
    '''Для доступа к серверу на текущей машине
     переходить по адресу localhost'''
    app.run(port=8080, host='0.0.0.0')
