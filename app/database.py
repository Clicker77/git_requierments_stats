from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def get_engine(app):
    """Create SQLAlchemy engine with proper configuration"""
    return create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        pool_size=app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_size'],
        pool_timeout=app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_timeout'],
        pool_recycle=app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_recycle'],
        max_overflow=app.config['SQLALCHEMY_ENGINE_OPTIONS']['max_overflow']
    )

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    try:
        engine = get_engine(app)
        # Create scoped session factory
        db.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        
        with app.app_context():
            # Create all tables
            inspector = db.inspect(engine)
            existing_tables = inspector.get_table_names()
            # logger.info(f"Existing tables: {existing_tables}")
            db.create_all()
            existing_tables = inspector.get_table_names()
            # logger.info(f"Existing tables: {existing_tables}")
            db.session.commit()  # Ensure changes are committed
            
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

def get_db():
    """Get the database instance"""
    return db

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

def handle_db_error(func):
    """Decorator to handle database errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            db.session.rollback()
            raise DatabaseError(f"Database operation failed: {str(e)}")
    return wrapper