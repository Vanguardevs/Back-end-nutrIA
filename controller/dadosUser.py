from services.users import get_user

def verUser(email: str, password: str):
    try:
        resp = get_user(email,password)
        return {"message": resp}
    except Exception as e:
        return {"error": str(e)}