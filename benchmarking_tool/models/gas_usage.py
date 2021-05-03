from .base import db


class GasUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    consumption = db.Column(db.Integer, unique=False)
    cost = db.Column(db.Float, unique=False)
    account_number =db.Column(db.Integer, unique=False)
    meter_number = db.Column(db.String(200), unique=False)
    site_id = db.Column(db.Integer, unique=False)
    month = db.Column(db.String(200), unique=False)
    year = db.Column(db.Integer, unique=False)
    gas_file = db.Column(db.String(50),unique=True, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
