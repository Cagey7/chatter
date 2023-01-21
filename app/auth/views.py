from . import auth


@auth.route("/login", methods=["GET", "POST"])
def login():
    return "Login"


@auth.route("/register", methods=["GET", "POST"])
def register():
    return "Register"
