from .base import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



class RecommendedAppliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appliance_name = db.Column(db.String(300), unique=False, nullable=False)
    appliance_type = db.Column(db.String(300), unique=False, nullable=False)
    rated_power = db.Column(db.Float, unique=False, nullable=False)
    reason = db.Column(db.String(200), unique=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
