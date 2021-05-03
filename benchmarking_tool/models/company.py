from .base import db
from .service_company import *
from .service import *
from sqlalchemy.dialects import postgresql as pg
from .response_quote import *

class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), unique=False, nullable=False)
	email_company = db.Column(db.String(200), unique=False, nullable=False)
	address = db.Column(db.String(200), unique=False)
	postal_code = db.Column(db.String(200), unique=False)
	phone_number = db.Column(db.String(200), unique=False)
	code = db.Column(db.String(200), unique=True)
	customer_base = db.Column(pg.ARRAY(db.String, dimensions=1), nullable=True)
	contractor = db.relationship('Contractor',backref='company',uselist=False)
	services_areas = db.Column(pg.ARRAY(db.String, dimensions=1), nullable=True)
	response_quote = db.relationship('ResponseQuote',backref='company',uselist=False)
	services = db.relationship('Service',secondary=service_company,backref=db.backref('companies',lazy='dynamic'))


	def __repr__(self):
		return f"{self.name}"