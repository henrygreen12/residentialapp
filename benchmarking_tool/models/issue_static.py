from .base import db

class IssueStatic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(300), unique=False, nullable=False)
    issue_detection_1 = db.Column(db.String(300), unique=False, nullable=False)
    issue_detection_2 = db.Column(db.String(300), unique=False, nullable=False)
    issue_detection_3 = db.Column(db.String(300), unique=False, nullable=False)
    issue_detection_4 = db.Column(db.String(300), unique=False, nullable=False)

