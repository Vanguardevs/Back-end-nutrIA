import google.generativeai as gemini
from pydantic import BaseModel

class Pergunta(BaseModel):
    pergunta: str

API_KEY = "AIzaSyC-9oOoUxE0v13DNuE37qBzClAfhJrxRJs"
gemini.configure(api_key=API_KEY);
meta = "ficar musculoso"
model = gemini.GenerativeModel("gemini-1.5-flash", system_instruction=f"Você é uma assistente nutricional de um aplicativo chamado NutrIA e esse é seu nome e você auxiliará o usuário com base na meta de {meta}, apenas isso.")
# Ia = modelo.generate_content("Qual dia de hoje?")
chat = model.start_chat(history=[])

chat = model.start_chat(history=[])

async def read_root(question: Pergunta):
    resposta = await chat.send_message_async(question.pergunta, generation_config=gemini.GenerationConfig(max_output_tokens=150,temperature=0.2))
    return {"pergunta": question.pergunta, "resposta": resposta.text}
