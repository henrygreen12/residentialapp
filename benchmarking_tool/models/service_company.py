from .base import db
from .company import *
from .service import *

service_company = db.Table('service_company',
 			db.Column('company_id', db.Integer, db.ForeignKey('company.id')),
			db.Column('service_id', db.Integer, db.ForeignKey('service.id'))
			)