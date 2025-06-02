from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_url = os.getenv("Database_URL")
# db_url = "postgresql://neondb_owner:npg_E3GqnPKW7tSA@ep-proud-king-a8tbl209-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)