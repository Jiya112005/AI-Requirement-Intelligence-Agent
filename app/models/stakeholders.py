from app import db
from datetime import datetime 

class Stakeholder(db.Model):
    __tablename__ = 'stakeholders'
    id = db.Column(db.Integer,primary_key=True)
    role = db.Column(db.String(150),nullable=False)
    perspective = db.Column(db.Text,nullable=True)
    concerns = db.Column(db.Text,nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    requirement_links = db.relationship('RequirementStakeholder',backref='stakeholder',lazy=True,cascade='all,delete-orphan')    
