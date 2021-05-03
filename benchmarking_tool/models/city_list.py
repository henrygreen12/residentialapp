from .base import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(200), unique = True)
