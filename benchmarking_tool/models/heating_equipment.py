from .base import db

class HeatingEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btu_input = db.Column(db.Integer, unique=False)
    btu_output = db.Column(db.Integer, unique=False)
    efficiency = db.Column(db.Integer, unique=False)

    type_heating = db.Column(db.String(200), unique=False)
    unique_photo_id = db.Column(db.String(50),unique=False)
    furnace_file = db.Column(db.String(50),unique=True)
    name_plate = db.Column(db.String(200), unique=False)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
