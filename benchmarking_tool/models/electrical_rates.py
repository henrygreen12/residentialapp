from .base import db
from sqlalchemy.orm import column_property


class ElectricalRates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    retailer = db.Column(db.String(300), unique=False, nullable=False)
    plan_details = db.Column(db.String(300), unique=False, nullable=False)
    pricing = db.Column(db.String(300), unique=False, nullable=False)
    contract_length = db.Column(db.String(300), unique=False, nullable=False)
    early_exit_fee = db.Column(db.Float, unique=False, nullable=False)
    retail_admin_fee = db.Column(db.Float, unique=False, nullable=False)
    retailer_charge = db.Column(db.Float, unique=False, nullable=False)
    variable_distribution = db.Column(db.Float, unique=False, nullable=False)
    fixed_distribution = db.Column(db.Float, unique=False, nullable=False)
    varible_transmission = db.Column(db.Float, unique=False, nullable=False)
    balancing_pool_rate_rider = db.Column(db.Float, unique=False, nullable=False)

    per_kwh_rate_rider = db.Column(db.Float, unique=False, nullable=False)
    transmission_rate_rider = db.Column(db.Float, unique=False, nullable=False)
    local_access_fee = db.Column(db.Float, unique=False, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    variable = column_property((variable_distribution + varible_transmission+balancing_pool_rate_rider+per_kwh_rate_rider+retailer_charge)/100)
    fixed= column_property((local_access_fee+retail_admin_fee)+(fixed_distribution *30))
    variable_gst = column_property(((variable_distribution + varible_transmission+balancing_pool_rate_rider+per_kwh_rate_rider+retailer_charge)/100)*0.05)
    fixed_gst=column_property(((local_access_fee+retail_admin_fee)+(fixed_distribution *30))*0.05)

    city = db.Column(db.String(100), unique=False, nullable=False)
    month = db.Column(db.Integer, unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)

    total_rate = db.Column(db.Float, unique=False, nullable=True) # redundant data. should remove during code review
