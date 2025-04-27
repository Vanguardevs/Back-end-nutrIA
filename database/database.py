from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

db = create_engine("postgresql://postgres:admin@localhost:5432/nutria")

SeesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)

@contextmanager
def get_bd():
    db = SeesionLocal()
    try:
        yield db
    finally:
        db.close()