from .base import db

class ApplianceCompanies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(300), unique=False, nullable=False)


