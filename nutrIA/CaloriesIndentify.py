from firebase_admin import credentials, initialize_app, db
import google.generativeai as gemini
import os
from pydantic import BaseModel

class DataDiary(BaseModel):
    id_user: str
    alimento: str
    horario: str

admin = firebase_admin

cred = credentials.Certificate("/etc/secrets/nutria.json")

admin.initialize_app(cred,{
    'databaseURL': 'https://nutria-eafaa-default-rtdb.firebaseio.com/'
})

API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY);
model = gemini.GenerativeModel(
    "gemini-1.5-flash", 
    system_instruction="APENAS RETORNE NUMERO, SEMPRE!."
    )


def Indentifer(data: DataDiary):
    response = await model.generate_content_async(f"Qual a quantidade calórica do {data.alimento}")

    if response:
        ref = db.reference(f"users/{data.id_user}/diaries")

        novo_alimento = {
            "alimento": data.alimento,
            "horario": data.horario,
            "calorias": response.text
        }

        ref.push(novo_alimento)
        print(f"✅ Alimento salvo para o usuário {data.id_user}")
        return

    return{"ERROR": "ERROR" }