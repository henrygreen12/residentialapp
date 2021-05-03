from .base import db

class ResponseQuote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	quote_id = db.Column(db.String(200), unique=False)
	quote_type = db.Column(db.String(200), unique=False)
	price = db.Column(db.String(200), unique=False)
	time_due = db.Column(db.DateTime)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=False)
	contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'))