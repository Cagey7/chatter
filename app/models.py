from app import db


class User(db.Model):
    """Sqlalchemy user class"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

    messages = db.relationship("Message", backref="user")
    chats_user_one = db.relationship("Chat", backref="user_one", uselist=False)
    chats_user_two = db.relationship("Chat", backref="user_two", uselist=False)
    message_reciever = db.relationship("Message", backref="reciever", uselist=False)
    message_sender = db.relationship("Message", backref="sender", uselist=False)

class Message(db.Model):
    """Sqlalchemy message class"""
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Date)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reciever_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"))


class Chat(db.Model):
    """Sqlalchemy chat class"""
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    user_one_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_two_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    chat_reciever_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    messages = db.relationship("Chat", backref="message")
