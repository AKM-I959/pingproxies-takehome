import os
from sqlmodel import create_engine, Session

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('POSTGRES_PORT', '5432')
database = os.getenv('DB_NAME')

dbURL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(dbURL)

def get_db():
    with Session(engine) as session:
        yield session
