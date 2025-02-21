from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://neondb_owner:npg_E3GqnPKW7tSA@ep-proud-king-a8tbl209-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)