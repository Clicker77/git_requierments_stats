from app.database import db

requirements_project = db.Table(
    'requirements_project',
    db.Model.metadata,
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirements.id'), primary_key=True)
)