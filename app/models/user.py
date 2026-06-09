from app import db
from datetime import datetime
from app.models.document import Document

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password_hash = db.Column(db.String(256),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    documents = db.relationship('Document', backref='owner', lazy=True, cascade="all, delete-orphan")