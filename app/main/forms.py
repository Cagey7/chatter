from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired
from app.models import *


class NewMessageForm(FlaskForm):
    msg_text = TextAreaField("Новое сообщение", validators=[DataRequired("Введите сообщение")])
    submit = SubmitField("Отправить")


class MessageForm(FlaskForm):
    msg_text = TextAreaField("Ответить", validators=[DataRequired("Введите сообщение")])
    chat_id = HiddenField()
    receiver_id = HiddenField()
    submit = SubmitField("Отправить")
