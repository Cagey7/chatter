from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField 
from wtforms.validators import DataRequired
from app.models import *


class NewMessageForm(FlaskForm):
    msg_text = TextAreaField("Введите сообщение для отправки", validators=[DataRequired("Введите сообщение")])
    submit = SubmitField("Отправить")
