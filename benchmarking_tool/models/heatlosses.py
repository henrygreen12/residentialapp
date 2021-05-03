from .base import db

class HeatLosses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallheatloss = db.Column(db.String(200), unique=False, nullable=False)
    windowheatloss = db.Column(db.String(200), unique=False, nullable=False)
    roofheatloss = db.Column(db.String(200), unique=False, nullable=False)
    totalheatloss = db.Column(db.String(200), unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))