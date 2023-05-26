from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models import *


class RegistrationForm(FlaskForm):
    """Flask wtf registration class"""
    email = StringField("Электронная почта", validators=[DataRequired("Введите электронную почту"), 
                                                         Email("Неправильный формат электронной почты"),
                                                         Length(max=120)], render_kw={"autofocus": True})
    password = PasswordField("Пароль", validators=[DataRequired("Введите пароль"), 
                                                   EqualTo("confirm_password", message="Пароли не совпадают"),
                                                   Length(min=8, max=30, message="Пароль должен содержать от 8 до 30 символов")])
    confirm_password = PasswordField("Подтвердите пароль", validators=[DataRequired("Подтвердите пароль")])
    submit = SubmitField("Зарегистрироваться")


    def validate_email(self, field):
        """Checks if email is already taken"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Элетронная почта уже занята.")


class LoginForm(FlaskForm):
    """Flask wtf login class"""
    email = StringField("Электронная почта", validators=[DataRequired("Введите электронную почту")], render_kw={"autofocus": True})
    password = PasswordField("Пароль", validators=[DataRequired("Введите пароль")])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class ChangePasswordForm(FlaskForm):
    """Flask wtf change password class"""
    old_password = PasswordField("Старый пароль", validators=[DataRequired("Введите страый пароль")])
    password = PasswordField("Новый пароль", validators=[DataRequired("Введите новый пароль"), 
                                                   EqualTo("confirm_password", message="Пароли не совпадают"),
                                                   Length(min=8, max=20, message="Пароль должен содержать от 8 до 20 символов")])
    confirm_password = PasswordField("Подтвердите пароль", validators=[DataRequired("Подтвердите пароль")])    
    submit = SubmitField("Подтвердить")


class ChangeEmailForm(FlaskForm):
    """Flask wtf change email class"""
    email = StringField("Электронная почта", validators=[DataRequired("Введите электронную почту"), 
                                                         Email("Неправильный формат электронной почты"),
                                                         Length(max=120)])
    submit = SubmitField("Подтвердить")
    
    
    def validate_email(self, field):
        """Checks if email is already taken"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Электронная почта уже занята")


class ResetPasswordForm(FlaskForm):
    """Flask wth reset password class"""
    password = PasswordField("Пароль", validators=[DataRequired(), EqualTo("confirm_password", message="Пароли не совпадают")])
    confirm_password = PasswordField("Подтвердите пароль", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class PassrecoveryForm(FlaskForm):
    """Flask wth reset password class"""
    email = StringField("Электронная почта", validators=[DataRequired(), Length(1, 64), Email("Неверный формат электронной почты")])
    submit = SubmitField("Подтвердить")
