from app import db
from datetime import datetime 
from app.models.stakeholders import Stakeholder

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
    stakeholder_links = db.relationship('RequirementStakeholder',backref='requirement',lazy=True,cascade='all, delete-orphan')
    
    # Phase 6: Feasibility
    feasibility = db.Column(db.String(50), nullable=True)
    risks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class RequirementStakeholder(db.Model):
    __tablename__ = "requirement_stakeholders"
    id = db.Column(db.Integer, primary_key=True)
    requirement_id = db.Column(db.Integer,db.ForeignKey("requirements.id"),nullable=False)
    stakeholder_id = db.Column(db.Integer,db.ForeignKey("stakeholders.id"),nullable=False)
    # Future Intelligence Fields
    influence_level = db.Column(db.String(50),nullable=True)
    ownership_type = db.Column(db.String(50),nullable=True)
    notes = db.Column(db.Text,nullable=True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

