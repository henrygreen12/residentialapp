from .base import db

class FurnaceAssumptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btu_rating = db.Column(db.String(200), unique=False, nullable=False)
    efficiency = db.Column(db.String(200), unique=False, nullable=False)
    thermostat = db.Column(db.String(200), unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))