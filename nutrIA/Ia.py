import google.generativeai as gemini
from pydantic import BaseModel
import os

class Pergunta(BaseModel):
    pergunta: str


# "AIzaSyC-9oOoUxE0v13DNuE37qBzClAfhJrxRJs"

API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY);
meta = "ficar musculoso"
model = gemini.GenerativeModel("gemini-1.5-flash", system_instruction=f"Você é uma assistente nutricional de um aplicativo chamado NutrIA e esse é seu nome. Você auxiliará o usuário e terá que ser simples e direta. Apenas isso.")
# Ia = modelo.generate_content("Qual dia de hoje?")
chat = model.start_chat(history=[])

chat = model.start_chat(history=[])

async def read_root(question: Pergunta):
    resposta = await chat.send_message_async(question.pergunta, generation_config=gemini.GenerationConfig(max_output_tokens=100,temperature=0.1))
    return {"pergunta": question.pergunta, "resposta": resposta.text}
