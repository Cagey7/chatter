from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from . import auth
from .forms import *
from ..email import send_email


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, not form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Неверная электронная почта или пароль")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(), password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/change_password", methods=["POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if not user.verify_password(form.old_password.data):
            flash("Неправильный старый пароль", "password_messages")
            return redirect(url_for("auth.profile"))
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash("Ваш пароль изменён", "password_messages")
    else:
        for errors in form.errors.values():
            flash(errors[0], "password_messages")
    return redirect(url_for("auth.profile"))


@auth.route("/change_email", methods=["POST"])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.add(current_user)
        db.session.commit()
        flash("Ваша электронная почта изменена", "email_messages")
    else:
        for errors in form.errors.values():
            flash(errors[0], "email_messages")
    return redirect(url_for("auth.profile"))

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form_psswd = ChangePasswordForm()
    form_email = ChangeEmailForm()
    return render_template("auth/profile.html", form_psswd=form_psswd, form_email=form_email)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PassrecoveryForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(form.email.data, "Восстановление пароля", "mail/reset", token=token)
            return render_template("auth/resetmessage.html")
        else:
            flash("Неверная электронная почта")
            return redirect(url_for("auth.password_reset_request"))
    return render_template("auth/resetrequest.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash("Ваш пароль был изменён")
            return redirect(url_for("auth.login"))
        else:
            flash("Ваш токен устарел, попробуйте еще раз")
            return redirect(url_for("auth.login"))
    return render_template("auth/reset.html", form=form, token=token)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
