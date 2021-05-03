from .base import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



class Appliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appliance_name = db.Column(db.String(300), unique=False, nullable=False)
    appliance_type = db.Column(db.String(300), unique=False, nullable=False)
    category_appliance = db.Column(db.String(300), unique=False, nullable=False)
    rated_power = db.Column(db.Float, unique=False, nullable=False)
    usage_time = db.Column(db.Float, unique=False, nullable=False)
    photo_id = db.Column(db.String(300), unique=False, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)



    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
