from app.database import db
from app.models.requirement_project import requirements_project

class Requirement(db.Model):
    """
    Model representing a Python package requirement
    """
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    version = db.Column(db.String(50))
    
    projects = db.relationship(
        'Project',
        secondary=requirements_project,
        back_populates='requirements'
    )
    
    def __init__(self, name: str, version: str = None):
        self.name = name
        self.version = version
    
    def __repr__(self):
        if self.version:
            return f'<Requirement {self.name}=={self.version}>'
        return f'<Requirement {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version
        }
