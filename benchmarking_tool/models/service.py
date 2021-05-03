from .base import db
from sqlalchemy.dialects import postgresql as pg

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), unique=False)