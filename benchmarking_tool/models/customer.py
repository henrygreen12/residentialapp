from .base import db
from datetime import datetime
from .dhw import *
from .electrical_usage import *
from .electrical_equipment import *
from .gas_usage import *
from .heating_equipment import *
from .occupancy import *
from .water_usage import *
from .user import *
from .role import *
from .equipment import *
from .survey import *
from .window import *
from .appliances import *
from .appliance_static import *
from .appliance_companies import *
from .electrical_rates import *
from .issue_static import *
from .city_list import *
from .messages import *
from .quote import *
from .recommendedappliance import *
from .recommendedheatingequipment import *
from .recommendeddhw import *


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(200), unique=False)
    address = db.Column(db.String(200), unique=False)
    city = db.Column(db.String(200), unique=False)
    postal_code = db.Column(db.String(200), unique=False)
    square_footage = db.Column(db.Float,unique=False)
    secret_code = db.Column(db.String(200), unique=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    tax_year = db.Column(db.Integer,unique=False)
    year_built = db.Column(db.Integer,unique=False)
    building_description = db.Column(db.String(200), unique=False)
    building_meter = db.Column(db.Float,unique=False)
    building_feet = db.Column(db.Float,unique=False)
    garage = db.Column(db.Boolean,unique=False)
    fireplace = db.Column(db.Boolean,unique=False)
    basement = db.Column(db.Boolean,unique=False)
    basement_development = db.Column(db.Boolean,unique=False)
    assessment = db.Column(db.Integer,unique=False)
    latitude = db.Column(db.Float,unique=False)
    longitude = db.Column(db.Float,unique=False)
    electrical_usage = db.relationship('ElectricalUsage', uselist=False,backref="customer")
    gas_usage = db.relationship('GasUsage', uselist=False,backref="customer")
    water_usage = db.relationship('WaterUsage',uselist=False,backref="customer")
    occupancy = db.relationship('Occupancy', uselist=False,backref="customer")
    heating_equipment = db.relationship('HeatingEquipment', uselist=False,backref="customer")
    dhw_equipment = db.relationship('DHW', uselist=False,backref="customer")
    electrical_equipment = db.relationship('ElectricalEquipment', uselist=False,backref="customer")
    equipment = db.relationship('Equipment', uselist=False,backref="customer")
    survey = db.relationship('Survey',uselist=False,backref="customer")
    window =db.relationship('Window',uselist=False,backref="customer")
    appliances = db.relationship('Appliance', uselist=False,backref="customer")
    quote = db.relationship('Quote', uselist=False,backref="customer")
    messages = db.relationship('Messages', uselist=False,backref="customer")
    recommendedappliance = db.relationship('RecommendedAppliance', uselist=False,backref="customer")
    recommendedheatingequipment = db.relationship('RecommendedHeatingEquipment', uselist=False,backref="customer")
    recommendeddhw = db.relationship('RecommendedDHW', uselist=False,backref="customer")
    #dimension of home assumptions
    first_story_sf = db.Column(db.Float,unique=False)
    second_story_sf = db.Column(db.Float,unique=False)
    third_story_sf = db.Column(db.Float,unique=False)
    basement_sf = db.Column(db.Float,unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)



