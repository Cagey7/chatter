from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    """Flask wtf login class"""
    email = StringField("Электронная почта", validators=[DataRequired("Введите электронную почту"), Email("Неправильный формат электронной почты")])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    """Flask wtf registration class"""
    email = StringField("Электронная почта", validators=[DataRequired(), Email("Неправильный формат электронной почты")])
    password = PasswordField("Пароль", validators=[DataRequired(), EqualTo("confirm_password", message="Пароли не совпадают")])
    confirm_password = PasswordField("Подтвердите пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")
