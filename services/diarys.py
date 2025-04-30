from database.database import get_bd

def get_diary(email):
    with get_bd() as db:
        response = db.execute(
            text("select * from diario where email = :email"),
            {"email": email}
        )
        diary = response.fetchall()
        if diary:
            return [dict(d._mapping) for d in diary]