from flask import render_template, redirect, url_for, Response, stream_with_context, abort, flash
from sqlalchemy import desc
import json
from flask_login import login_required, current_user
from . import main
from .forms import *
from datetime import datetime, timedelta
import time
import pytz

almaty_tz = pytz.timezone("Asia/Almaty")


@main.route("/", methods=["GET", "POST"])
def index():
    form = NewMessageForm()
    try:
        # check if user have to much unanswered messages
        my_unanswered_msg = Message.query.filter_by(id=WaitingMessage.message_id) \
                                    .filter_by(sender_id=current_user.id).all().__len__()
        if my_unanswered_msg >= 6:
            msg = "Ваши сообщения уже ожидают ответа от новых пользователей"
            return render_template("index.html", msg=msg)
    except:
        pass
    
    if form.validate_on_submit():
        # added new message to messages table
        message = Message(time=datetime.now(almaty_tz).strftime('%Y-%m-%d %H:%M:%S'),
                            text=form.msg_text.data,
                            sender_id=current_user.id)
        db.session.add(message)
        db.session.commit()

        # update last seen of current user
        user = User.query.filter_by(id=current_user.id).first()
        user.last_seen = datetime.now(almaty_tz).strftime('%Y-%m-%d %H:%M:%S')
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
            
            minetes_list = [3, 30, 180, 4320, 44640]

            # generate new message for user and create chat
            for minetes in minetes_list:
                time_ago = datetime.now(almaty_tz) - timedelta(minutes=minetes)
                received_message = Message.query \
                    .filter_by(id=WaitingMessage.message_id) \
                    .filter(Message.sender_id.notin_(ignore_users)) \
                    .filter(Message.sender_id.in_(
                        [user.id for user in User.query \
                            .filter(User.last_seen >= time_ago) \
                            .filter(User.id.notin_([current_user.id])) \
                            .all()])) \
                    .order_by(Message.time) \
                    .first()                                                                                               
                if received_message:
                    break
            
            if not received_message:
                received_message = Message.query.filter_by(id=WaitingMessage.message_id) \
                    .filter(Message.sender_id.notin_(ignore_users)) \
                    .order_by(Message.time).first()
            
            sender_id = received_message.sender_id
            receiver_id = current_user.id
            chat = Chat(user_one_id=sender_id, user_two_id=receiver_id)
            db.session.add(chat)
            db.session.commit()

            # change data of sended message
            received_message.receiver_id = current_user.id
            received_message.chat_id = chat.id
            received_message.seen = True
            db.session.commit()

            # delete waiting message
            del_waiting_message = WaitingMessage.query \
                                    .filter_by(message_id=received_message.id).first()
            db.session.delete(del_waiting_message)
            db.session.commit()
        except:
            return render_template("chat.html", no_users="Нет доступных пользователей")

        return redirect(url_for("main.chat", chat_id=chat.id))
    return render_template("index.html", form=form)


@main.route("/between_chat", methods=["GET", "POST"])
@login_required
def between_chat():
    try:
        chat_id = Message.query.filter_by(seen=False, receiver_id=current_user.id). \
                                            order_by(Message.time).first().chat_id
    except:
         return redirect(url_for("main.index"))
    return redirect(url_for("main.chat", chat_id=chat_id))


@main.route("/chat/<int:chat_id>", methods=["GET", "POST"])
@login_required
def chat(chat_id):
    form = MessageForm()
    chat = Chat.query.filter_by(id=chat_id).first()
    try:
        # allow only two users to enter chat
        if not (chat.user_one_id == current_user.id 
                or chat.user_two_id == current_user.id):
            abort(404)
    except:
        abort(404)
    
    # get all messages
    messages = chat.messages

    # change status of unseen messages
    unseen_messages = Message.query.filter_by(chat_id=chat_id, seen=False, \
                                              receiver_id=current_user.id).all()
    for unseen_message in unseen_messages:
        unseen_message.seen = True
    db.session.commit()

    # get id of user who received message
    if current_user.id == chat.user_one_id:
        form.receiver_id.data = chat.user_two_id
    else:
        form.receiver_id.data = chat.user_one_id
    form.chat_id.data = chat_id
    return render_template("chat.html", messages=messages, form=form)


@main.route("/replies", methods=["GET", "POST"])
@login_required
def replies():
    user_one_ids = Chat.query.filter_by(user_two_id=current_user.id).all()
    user_two_ids =  Chat.query.filter_by(user_one_id=current_user.id).all()
    chats = user_one_ids + user_two_ids
    unanswered_chats = []
    for chat in chats:
        receiver_id = chat.messages[-1].receiver_id
        if receiver_id == current_user.id:
            message = Message.query.filter_by(chat_id=chat.id).order_by(desc(Message.time)).first().text
            if len(message) > 30:
                message = message[:30]+"..."
            unanswered_chats.append((chat.id, message))

    return render_template("replies.html", unanswered_chats=unanswered_chats)


@main.route("/send_message", methods=["POST"])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        # check if user already sended message
        last_message = Message.query.filter_by(chat_id=form.chat_id.data). \
                                order_by(desc(Message.time)).first()
        if last_message.sender_id != current_user.id:
            # add new message to database
            message = Message(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                text=form.msg_text.data, sender_id=current_user.id,
                                receiver_id=form.receiver_id.data,
                                chat_id=form.chat_id.data, seen=False)
            db.session.add(message)

            # change status of unseen messages
            user = User.query.filter_by(id=current_user.id).first()
            user.last_seen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
        else:
            return redirect(url_for("main.chat", chat_id=form.chat_id.data))
    return redirect(url_for("main.chat", chat_id=form.chat_id.data))


@main.route("/listen")
@login_required
def listen():
    def stream():
        while True:
            # check for new messages
            len_chats = len(Message.query.filter_by(seen=False, receiver_id=current_user.id) \
                            .order_by(Message.time).all())
            chats = {"len_chats": len_chats}
            if chats:
                yield f"data: {json.dumps(chats)}\n\n"
            time.sleep(0.1)
    return Response(stream_with_context(stream()), mimetype="text/event-stream")


@main.route("/delete_chat/<int:chat_id>")
@login_required
def delete_chat(chat_id):
    chat = Chat.query.filter_by(id=chat_id).first()
    messages = Message.query.filter_by(chat_id=chat_id).all()
    db.session.delete(chat)
    for message in messages:
        db.session.delete(message)
    db.session.commit()
    return redirect(url_for("main.index"))
