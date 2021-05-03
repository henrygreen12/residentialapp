from .base import db

class RecommendedDHW(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btu_output = db.Column(db.Integer, unique=False)
    volume = db.Column(db.Integer, unique=False)
    year_built = db.Column(db.Integer, unique=False)
    name_plate = db.Column(db.String(200), unique=False)
    reason = db.Column(db.String(200), unique=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    