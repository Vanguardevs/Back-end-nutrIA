from services.users import get_user, post_user

def create_user(name, email, password, idade, sexo, tipo_usuario, objetivo):

    if not name or not email or not password or not idade or not sexo or not tipo_usuario or not objetivo:
        return {"error": "Todos os campos são obrigatórios."}
    
    if idade < 13:
        return {"error": "Idade mínima é 13 anos."}
    
    if len(password) < 8:
        return {"error": "A senha deve ter pelo menos 8 caracteres ou superior."}
    

    try:
        post_user(name, email, password, idade, sexo, tipo_usuario, objetivo)
        return {"message": "Usuário criado com sucesso!"}
    except Exception as e:
        return {"error": str(e)}
