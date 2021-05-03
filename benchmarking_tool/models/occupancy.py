from .base import db


class Occupancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hours_per_week = db.Column(db.Integer, unique=False, nullable=False)
    occupants = db.Column(db.Integer, unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))