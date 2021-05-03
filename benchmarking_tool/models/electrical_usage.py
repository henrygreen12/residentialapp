from .base import db
from datetime import datetime

class ElectricalUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumption = db.Column(db.Float, unique=False)
    cost = db.Column(db.Float, unique=False)
    electrical_file = db.Column(db.String(200),unique=True, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
