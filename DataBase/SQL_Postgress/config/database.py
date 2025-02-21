from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
database_url = os.getenv("neon_tech_URI")
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)