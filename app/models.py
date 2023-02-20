from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask_login import UserMixin


class Message(db.Model):
    """Sqlalchemy message class"""
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime())
    text = db.Column(db.Text())
    sender_id = db.Column(db.Integer)
    reciever_id = db.Column(db.Integer)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"))


class Chat(db.Model):
    """Sqlalchemy chat class"""
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    user_one_id = db.Column(db.Integer)
    user_two_id = db.Column(db.Integer)
    chat_reciever_id = db.Column(db.Integer)
    messages = db.relationship("Message", backref="chat")


class User(db.Model, UserMixin):
    """Sqlalchemy user class"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")


    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        """Compare inputted password with password in database"""
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
