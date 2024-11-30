from flask import Flask
from flask_migrate import Migrate
from celery import Celery
from app.config import Config
from app.database import db, init_db
from app.models.requirement_project import requirements_project
from app.models.project import Project
from app.models.requirement import Requirement

__all__ = ['Project', 'Requirement', 'requirements_project']

migrate = Migrate()

def create_celery(app):
    celery_app = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    return celery_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    init_db(app)
    migrate.init_app(app, db)
    
    return app

app = create_app(Config)
celery_app = create_celery(app)
from app.api.routes import api
app.register_blueprint(api)