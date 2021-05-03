from .base import db
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime


class EdmontonWeather(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    current_condition = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=False)
    temperature = db.Column(db.Float, unique=False, nullable=False)
    pressure = db.Column(db.Float, unique= False, nullable=False)
    humidity = db.Column(db.Integer,unique=False,nullable=False)
    wind_speed = db.Column(db.Integer,unique=False,nullable=False)
    wind_deg = db.Column(db.Integer,unique=False,nullable=False)
    clouds = db.Column(db.Integer,unique=False,nullable=False)
    sunrise = db.Column(db.Integer,unique=False,nullable=False)
    sunset = db.Column(db.Integer,unique=False,nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
