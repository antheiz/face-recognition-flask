from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3,max=20,message='username minimal 3 huruf')])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password',message='password salah, silakan coba lagi')])
    daftar = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    masuk = SubmitField('Login')

class PersonalForm(FlaskForm):
    foto = FileField('Upload Foto', validators=[FileAllowed(['jpg','png', 'jpeg']), FileRequired()])
    upload = SubmitField('Upload')