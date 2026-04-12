from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password_hash = db.Column(db.String(256),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    documents = db.relationship('Document', backref='owner', lazy=True, cascade="all, delete-orphan")

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
    
class Requirement(db.Model):
    """Upgraded from 'task'. this now holds the intelligence metrics evaluated by multi-agent system."""
    __tablename__ = 'requirements'
    id = db.Column(db.Integer,primary_key=True)
    document_id = db.Column(db.Integer,db.ForeignKey('documents.id'),nullable=False)

    # Phase 2 & 3 :Structured Requirements
    feature = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(50), default='Medium')
    constraints = db.Column(db.Text, nullable=True)
    dependencies = db.Column(db.Text, nullable=True)
    
    # Phase 4: Vagueness Detection
    clarity_score = db.Column(db.Float, nullable=True) # E.g., 0.1 to 1.0
    ambiguous_terms = db.Column(db.Text, nullable=True) # Stored as comma-separated or JSON string
    missing_info = db.Column(db.Text, nullable=True)
    
    # Phase 5: Clarification Engine
    clarification_questions = db.Column(db.Text, nullable=True) # Stored as JSON string list
    
    # Phase 6: Feasibility
    feasibility = db.Column(db.String(50), nullable=True)
    risks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
