from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
database_url = "postgresql://neondb_owner:npg_34wpvyFdbiVR@ep-black-silence-a8jvy9i1-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)