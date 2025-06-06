import google.generativeai as gemini
from pydantic import BaseModel
import os
import firebase_admin
from firebase_admin import db, credentials
from google.generativeai.types import FunctionDeclaration, Tool


admin = firebase_admin

# cred = credentials.Certificate("./nutrIA/nutria.json")

cred = credentials.Certificate("/etc/secrets/nutria.json")

admin.initialize_app(cred,{
    'databaseURL': 'https://nutria-eafaa-default-rtdb.firebaseio.com/'
})


schedule_meeting_function = FunctionDeclaration(
    name="schedule_meeting",
    description="Agendar alimentação do usuário, Refeição, hora",
    parameters={
        "type": "object",
        "properties": {
            "refeicao":{
                "type": "string",
                "description": "quero comer Sanduíche"
            },
            "hora":{
                "type": "string",
                "description": "comer às 19:40"
            }
        },
        "required": ["refeicao", "hora"],
    },


)

def salvar_agenda(refeicao, hora, id_user):
    ref = db.reference(f"users/{id_user}/diaries")

    novo_agendamento = {
        "refeicao": refeicao,
        "hora": hora
    }

    ref.push(novo_agendamento)
    print(f"✅ Agendamento salvo para o usuário {id_user}")



class Pergunta(BaseModel):
    pergunta: str
    id_user: str



# def getDados(id_user:str):
#     ref = db.reference(f"users/{id_user}")
#     dados = ref.get();
#     if dados:
#         return dados;
#     else: 
#         return

# dados:Pergunta
# dados_user = getDados(dados.id_user)
# meta = dados_user["objetivo"]


# API_KEY = "AIzaSyC-9oOoUxE0v13DNuE37qBzClAfhJrxRJs"

API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY);

# Ia = modelo.generate_content("Qual dia de hoje?")
# chat = model.start_chat(history=[])

async def read_root(question: Pergunta):

    ref = db.reference(f"users/{question.id_user}")
    dados = ref.get();


    model = gemini.GenerativeModel(
    "gemini-2.0-flash", 
    system_instruction=f"Você é uma assistente nutricional de um aplicativo chamado NutrIA e esse é seu nome. Você apenas auxiliará o usuário e terá que ser e direta. Não responda perguntas além de nutricionismo. nome do usuário: {dados['nome']}, idade: {dados['idade']}, peso: {dados['peso']}, altura: {dados['altura']}, sexo: {dados['sexo']}, objetivo: {dados['objetivo']}",
    tools=[Tool(function_declarations=[schedule_meeting_function])]
    )

    resposta = await model.generate_content_async(
        question.pergunta,
        generation_config=gemini.GenerationConfig(max_output_tokens=5000, temperature=0.1)
    )


    # # Verifica se a IA quer chamar uma função
    parts = resposta.candidates[0].content.parts
    if parts and hasattr(parts[0], "function_call"):
        function_call = parts[0].function_call
        args = function_call.args
        print("🧠 IA interpretou:", args)
        
        # Chama a função real com os dados e o id_user
        if args:
            salvar_agenda(**args, id_user=question.id_user)
            return{
                "resposta": {"Agendado com sucesso!"}
            }
        elif not args:
            return{"resposta": {"Não foi possível agendar."}}

    return {
        "pergunta": question.pergunta,
        "resposta": resposta.text
    }
