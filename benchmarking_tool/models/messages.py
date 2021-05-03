from .base import db

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(400), unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    recipient = db.Column(db.String(80),unique = False)