from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class Message(db.Model):
    """Sqlalchemy message class"""
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(), default=datetime(2023, 1, 1, 0, 0, 0))
    text = db.Column(db.Text())
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"))
    seen = db.Column(db.Boolean, default=False)


class Chat(db.Model):
    """Sqlalchemy chat class"""
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    user_one_id = db.Column(db.Integer) #sender
    user_two_id = db.Column(db.Integer) #receiver
    messages = db.relationship("Message", backref="chat")


class User(db.Model, UserMixin):
    """Sqlalchemy user class"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime(2023, 1, 1, 0, 0, 0))


    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")


    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        """Compare inputted password with password in database"""
        return check_password_hash(self.password_hash, password)


    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})


    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.commit()
        return True


class WaitingMessage(db.Model):
    """Sqlalchemy waiting message class"""
    __tablename__ = "waiting_messages"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
