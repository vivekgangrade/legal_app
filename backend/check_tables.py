from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/legal_db")
engine = create_engine(DATABASE_URL)

try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
except Exception as e:
    print(f"Error connecting: {e}")
