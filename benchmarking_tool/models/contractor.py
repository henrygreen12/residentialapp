from .base import db

class Contractor(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	phone_number = db.Column(db.String(200), unique=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
	response_quote = db.relationship('ResponseQuote',backref='contractor',uselist=False)