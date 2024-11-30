from datetime import datetime
from app.database import db
from app.models.requirement_project import requirements_project

class Project(db.Model):
    """
    Model representing a GitHub project
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    last_update_date = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with requirements through the association table
    requirements = db.relationship(
        'Requirement',
        secondary=requirements_project,
        back_populates='projects'
    )
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def add_requirement(self, requirement):
        """Add a requirement to the project if it doesn't exist"""
        if requirement not in self.requirements:
            self.requirements.append(requirement)
    
    def remove_requirement(self, requirement):
        """Remove a requirement from the project"""
        if requirement in self.requirements:
            self.requirements.remove(requirement)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_update_date': self.last_update_date.isoformat(),
            'requirements': [req.to_dict() for req in self.requirements]
        }