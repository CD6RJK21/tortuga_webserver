from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email


class BookUploadForm(FlaskForm):
    author = StringField('Автор книги', validators=[DataRequired()])
    title = TextAreaField('Название книги', validators=[DataRequired()])
    file = FileField('Файл не выбран', validators=[FileRequired()])
    submit = SubmitField('Загрузить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignUpForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Почта', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
