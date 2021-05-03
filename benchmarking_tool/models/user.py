from .base import db
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from .role import *
from .customer import *
from .messages import *
from .contractor import *


class User(db.Model,UserMixin):
	id = db.Column(db.Integer(),primary_key=True)
	email = db.Column(db.String(200), unique=False, nullable=False)
	first_name = db.Column(db.String(200), unique=False, nullable=True)
	last_name = db.Column(db.String(200), unique=False, nullable=True)
	phone_number = db.Column(db.String(200), unique=False, nullable=True)
	password = db.Column(db.String(200),unique=True, nullable=False)
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	customer = db.relationship('Customer',backref='user',uselist=False)
	contractor = db.relationship('Contractor',backref='user',uselist=False)
	messages = db.relationship('Messages', uselist=False,backref="user")

	def __repr__(self):
		return f"{self.first_name} {self.last_name}"

	def is_admin(self):
		role = Role.query.get(self.role_id)
		if role == None:
			return False
		return role.name == 'Admin'

	def get_reset_token(self,expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'])
		return s.dumps({'user_id':self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id )
