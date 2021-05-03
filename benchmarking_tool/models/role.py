from .base import db

class Role(db.Model):
	id = db.Column(db.Integer(),primary_key=True)
	name = db.Column(db.String(80),unique=True)
	users = db.relationship('User',backref="role")

	def __repr__(self):
		return f"{self.name}"