import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database connection URL: postgresql://<user>:<password>@<host>:<port>/<db_name>
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:12345678@localhost:5432/expense_tracker"
)

# Create the database engine
engine = create_engine(DATABASE_URL)

# Factory for creating database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models (User, Expense, AuditLog) will inherit from
Base = declarative_base()

# FastAPI Dependency: provides a session to a route and closes it when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()