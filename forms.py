from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email


class BookUploadForm(FlaskForm):
    author = StringField('Автор книги', validators=[DataRequired()])
    title = TextAreaField('Название книги', validators=[DataRequired()])
    file = FileField('Файл не выбран', validators=[FileRequired()])
    submit = SubmitField('Загрузить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class SignUpForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Почта', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_repeat = PasswordField('Повтор пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class SearchForm(FlaskForm):
    request = StringField('Поиск', validators=[DataRequired()])


class AuthorRegisterForm(FlaskForm):
    display_name = StringField('Краткое имя', validators=[DataRequired()])
    full_name = TextAreaField('Полное имя', validators=[DataRequired()])
    description = TextAreaField('Биография', validators=[DataRequired()])
    image = FileField('Фото')
    submit = SubmitField('Добавить')
