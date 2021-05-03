from .base import db


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setPoint =db.Column(db.String, unique=False, nullable=True)
    thermostatNight = db.Column(db.String(200), unique=False, nullable=True)
    heatedGarage = db.Column(db.String(200), unique=False, nullable=True)
    stoveType = db.Column(db.String(200), unique=False, nullable=True)
    clothesDryerType = db.Column(db.String(200), unique=False, nullable=True)
    waterHeaterType = db.Column(db.String(200), unique=False, nullable=True)
    furnaceType = db.Column(db.String(200), unique=False, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    hotWaterUsage = db.Column(db.String(200), unique=False, nullable=True)
    houseStories = db.Column(db.String(200), unique=False, nullable=True)
    numOfPeople = db.Column(db.String(200), unique=False, nullable=True)
    laundryUsage = db.Column(db.String(200), unique=False, nullable=True)
    dishWasher = db.Column(db.String(200), unique=False, nullable=True)
    cookFrequency = db.Column(db.String(200), unique=False, nullable=True)
    microwaveFrequency = db.Column(db.String(200), unique=False, nullable=True)
