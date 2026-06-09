from app import db
from datetime import datetime
from app.models.requirement import Requirement

class Document(db.Model):  # for storing the document uploaded by user to be processed 
    __tablename__ = 'documents'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    file_path = db.Column(db.String(255),nullable=False)
    status = db.Column(db.String(50),default='UPLOADED')
    raw_text = db.Column(db.Text,nullable=True)
    srs_draft = db.Column(db.Text,nullable=True)

    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    requirements = db.relationship('Requirement',backref='document',lazy=True,cascade='all,delete-orphan')
    
