from .base import db

class ApplianceStatic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appliance_name = db.Column(db.String(300), unique=False, nullable=False)
    category = db.Column(db.String(300), unique=False, nullable=False)
    power = db.Column(db.Float, unique=False, nullable=False)




