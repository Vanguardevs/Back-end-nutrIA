import google.generativeai as gemini
from pydantic import BaseModel
import os
from firebase.firebase_config import firebase_admin, db, credentials
from google.generativeai.types import FunctionDeclaration, Tool

admin = firebase_admin

# API_KEY = "AIzaSyC-9oOoUxE0v13DNuE37qBzClAfhJrxRJs"

API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY)

async def check_calories_function(tipo_refeicao: str, horario: str, refeicao: str, id_user: str) -> str:
    try:
        prompt = f"Calcule as calorias para a refeição '{refeicao}'"
        model = gemini.GenerativeModel("gemini-1.5-flash", system_instruction="Você deve apenas retornar numero")
        gemini_response = await model.generate_content_async(prompt)

        calorias = gemini_response.text.strip()
        if not calorias.isdigit():
            return "Erro ao calcular as calorias. Resposta inválida do Gemini."

        calorias = int(calorias)

        ref = db.reference(f"users/{id_user}/diaries")
        ref.push({
            "tipo_refeicao": tipo_refeicao,
            "horario": horario,
            "refeicao": refeicao,
            "calorias": calorias,
            "progress":{
                "0": False,
                "1": False,
                "2": False,
                "3": False,
                "4": False,
                "5": False,
                "6": False
            }
        })

        return f"Calorias calculadas e salvas com sucesso: {calorias}"

    except Exception as e:
        return f"Erro ao calcular as calorias: {str(e)}"
