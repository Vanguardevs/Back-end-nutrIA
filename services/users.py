from database.database import get_bd
from sqlalchemy import text

def get_user():
    with get_bd() as db:
        response = db.execute(text("select * from usuarios "))
        user = response.fetchone()
        if user:
            return dict(user._mapping)