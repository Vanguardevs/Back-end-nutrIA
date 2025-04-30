from database.database import get_bd
from sqlalchemy import text

def get_user(email, password):
    with get_bd() as db:
        response = db.execute(
            text("select * from usuarios where email = :email and senha = :password"),
            {"email": email, "password": password}
        )
        user = response.fetchone()
        if user:
            return dict(user._mapping)

def post_user(name, email, password, idade, sexo, tipo_usuario, objetivo):
    with get_bd() as db:
        script = text("insert into usuarios(nome,email,senha,idade,sexo,tipo_usuario,objetivo) values (:name, :email, :password, :idade, :sexo, :tipo_usuario, :objetivo)")
        db.execute(script, {"name": name, "email": email, "password": password, "idade": idade, "sexo": sexo, "tipo_usuario": tipo_usuario, "objetivo": objetivo})
        db.commit()
        print("User criado com sucesso!")

