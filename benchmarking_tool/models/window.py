from .base import db

class Window(db.Model): 
	id = db.Column(db.Integer, primary_key=True)
	length = db.Column(db.Integer, unique=False)
	height = db.Column(db.Integer, unique=False)
	location = db.Column(db.String(200), unique=False)
	room_type = db.Column(db.String(200),unique=False)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))