from .base import db

class Quote(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	quote_type = db.Column(db.String(200), unique=False)
	response1 = db.Column(db.String(200), unique=False)
	response2 = db.Column(db.String(200), unique=False)
	time_due = db.Column(db.DateTime)
	video_name = db.Column(db.String(100), unique=False)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    
	def video_url(self):
		return f"video/{self.video_name}"