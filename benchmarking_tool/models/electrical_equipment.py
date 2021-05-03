from .base import db


class ElectricalEquipment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    lights = db.Column(db.Integer,unique=False,nullable=False)
    computers = db.Column(db.Integer,unique=False,nullable=False)
    game_consoles = db.Column(db.Integer,unique=False,nullable=False)
    wifi_routers = db.Column(db.Integer,unique=False,nullable=False)
    printers = db.Column(db.Integer,unique=False,nullable=False)
    cell_phone_chargers = db.Column(db.Integer,unique=False,nullable=False)
    space_heater = db.Column(db.Integer,unique=False,nullable=False)
    fridge = db.Column(db.Integer,unique=False,nullable=False)
    mini_fridge = db.Column(db.Integer,unique=False,nullable=False)
    microwave = db.Column(db.Integer,unique=False,nullable=False)
    applicanes = db.Column(db.Integer,unique=False,nullable=False)
    ceiling_fans = db.Column(db.Integer,unique=False,nullable=False)
    top_loading_freezer = db.Column(db.Integer,unique=False,nullable=False)
    stand_up_freezer = db.Column(db.Integer,unique=False,nullable=False)
    air_conditioner = db.Column(db.Integer,unique=False,nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
