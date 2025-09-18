from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL from environment variable or default
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/edutrack")

# Create engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,  # Default number of connections to keep open
    max_overflow=10,  # Maximum number of connections to create above pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes to avoid stale connections
    pool_pre_ping=True,  # Test connections before using them to avoid broken connections
    poolclass=QueuePool  # Use QueuePool for connection pooling
)

# Add event listeners for connection pool
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out")

@event.listens_for(engine, "checkin")
def checkin(dbapi_connection, connection_record):
    logger.debug("Database connection checked in")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session with error handling and retries
def get_db():
    db = SessionLocal()
    try:
        # Test connection before using it
        db.execute("SELECT 1")
        yield db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        # Close the errored connection
        db.close()
        # Try one more time with a fresh connection
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            logger.info("Database reconnection successful")
            yield db
        except Exception as retry_error:
            logger.error(f"Database reconnection failed: {retry_error}")
            raise
    finally:
        db.close()