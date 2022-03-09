from email.policy import default
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    foto = db.Column(db.String(30), nullable=False, default='default.png')
    password = db.Column(db.Text, nullable=False)

    def __str__(self):
        return self.username