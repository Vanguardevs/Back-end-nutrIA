import psycopg

async def verUser():
    try:
        with psycopg.connect("dbname=TesteBD user=postgres password=admin") as conn:
            with conn.cursor() as cur:
                cur.execute("select * from tbl_user")
                user = cur.fetchall()
                return user
    except Exception as error:
        print("Error ao retornar o dado: " + error)