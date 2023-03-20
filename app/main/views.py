from flask import render_template, redirect, url_for, session
from flask_login import login_required, current_user
from . import main
from .forms import *
from datetime import datetime


@main.route("/", methods=["GET", "POST"])
def index():
    form = NewMessageForm()
    try:
        my_unanswered_msg = Message.query \
                                    .filter_by(id=WaitingMessage.message_id) \
                                    .filter_by(sender_id=current_user.id) \
                                    .all() \
                                    .__len__()
        if my_unanswered_msg >= 6:
            msg = "Ваши сообщения уже ожидают ответа от новых пользователей"
            return render_template("index.html", msg=msg)
    except:
        pass
    
    if form.validate_on_submit():
        # added new message to messages table
        message = Message(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            text=form.msg_text.data,
                            sender_id=current_user.id)
        db.session.add(message)
        db.session.commit()

        # added same message in waiting_messages table
        waitingMessage = WaitingMessage(message_id=message.id)
        db.session.add(waitingMessage)
        db.session.commit()                              

        try:
            # get all users with whom the given user is already chatting
            user_one_ids = [chat.user_one_id 
                            for chat 
                            in Chat.query.filter_by(user_two_id=current_user.id).all()]
            user_two_ids = [chat.user_two_id 
                            for chat 
                            in Chat.query.filter_by(user_one_id=current_user.id).all()]
            ignore_users = list(set(user_one_ids).union(user_two_ids))
            ignore_users.append(current_user.id)

            # generate new message for user and create chat
            received_message = Message.query \
                                .filter_by(id=WaitingMessage.message_id) \
                                .filter(Message.sender_id.notin_(ignore_users)) \
                                .order_by(Message.time) \
                                .first()
            sender_id = received_message.sender_id
            receiver_id = current_user.id
            chat = Chat(user_one_id=sender_id,
                        user_two_id=receiver_id)
            db.session.add(chat)
            db.session.commit()

            # change data of sended message
            received_message.receiver_id = current_user.id
            received_message.chat_id = chat.id
            db.session.commit()

            # delete waiting message
            del_waiting_message = WaitingMessage.query \
                                    .filter_by(message_id=received_message.id) \
                                    .first()
            db.session.delete(del_waiting_message)
            db.session.commit()
        except:
            return render_template("chat.html", no_users="Нет доступных пользователей")

        return redirect(url_for("main.chat", chat_id=chat.id))
    return render_template("index.html", form=form)


@main.route("/chat/<chat_id>", methods=["GET", "POST"])
@login_required
def chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first()
    messages = chat.messages
    return render_template("chat.html", messages=messages)


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
