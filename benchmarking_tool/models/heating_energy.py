from .base import db

class HeatingEnergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heating_energy = db.Column(db.String(200), unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))