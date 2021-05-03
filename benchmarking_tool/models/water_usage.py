from .base import db


class WaterUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_number = db.Column(db.String(200), unique=False, nullable=False)
    usage = db.Column(db.Integer, unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    