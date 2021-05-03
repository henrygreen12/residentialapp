from .base import db

class RecommendedHeatingEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btu_input = db.Column(db.Integer, unique=False)
    btu_output = db.Column(db.Integer, unique=False)
    efficiency = db.Column(db.Integer, unique=False)

    type_heating = db.Column(db.String(200), unique=False)
    name_plate = db.Column(db.String(200), unique=False)
    reason = db.Column(db.String(200), unique=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
