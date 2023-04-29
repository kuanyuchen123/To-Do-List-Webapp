from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100))
    status = db.Column(db.Integer())
    owner_id = db.Column(db.Integer())