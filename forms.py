from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class BookUploadForm(FlaskForm):
    author = StringField('Автор книги', validators=[DataRequired()])
    title = TextAreaField('Название книги', validators=[DataRequired()])
    file = FileField('Файл не выбран', validators=[FileRequired()])
    submit = SubmitField('Загрузить')
