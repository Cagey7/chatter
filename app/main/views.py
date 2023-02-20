from flask import render_template, flash
from flask_login import login_required
from . import main


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
