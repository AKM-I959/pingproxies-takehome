import os
from sqlmodel import create_engine, Session

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('POSTGRES_PORT', '5432')
database = os.getenv('DB_NAME')

dbURL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Currently I have a single database connection.
# SQLModel engine is just a wrapper of an sqlalchemy engine.
# Has default pooling parameters -> could potentially change these?

engine = create_engine(dbURL)

def get_db():
    with Session(engine) as session:
        yield session