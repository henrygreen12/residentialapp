from .base import db

class DHW(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    btu_output = db.Column(db.Integer, unique=False)
    volume = db.Column(db.Integer, unique=False)
    year_built = db.Column(db.Integer, unique=False)
    unique_photo_id = db.Column(db.Integer,unique=False)
    dhw_file = db.Column(db.String(50),unique=True, nullable=True)
    name_plate = db.Column(db.String(200), unique=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    