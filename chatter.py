from app import create_app, db
from app.models import *


app = create_app("development")
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()
