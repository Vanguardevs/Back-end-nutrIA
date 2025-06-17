import google.generativeai as gemini
from pydantic import BaseModel
import os
import firebase_admin
from firebase.firebase_config import db
from google.generativeai.types import FunctionDeclaration, Tool

# Inicialização do Firebase
admin = firebase_admin

# Configuração da API Gemini
API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY)

# 🛠️ Função para agendar refeições, com múltiplos agendamentos
schedule_meeting_function = FunctionDeclaration(
    name="schedule_meeting",
    description="Agendar uma ou mais refeições do usuário, incluindo horário e descrição.",
    parameters={
        "type": "object",
        "properties": {
            "agendamentos": {
                "type": "array",
                "description": "Lista de refeições a serem agendadas.",
                "items": {
                    "type": "object",
                    "properties": {
                        "refeicao": {
                            "type": "string",
                            "description": "Descrição da refeição. Ex: 'Sanduíche com queijo'."
                        },
                        "hora": {
                            "type": "string",
                            "description": "Horário no formato HH:MM. Ex: '19:40'."
                        }
                    },
                    "required": ["refeicao", "hora"]
                }
            }
        },
        "required": ["agendamentos"]
    }
)

# 🔍 Função para determinar o tipo de refeição com base na hora
def identificar_tipo_refeicao(hora: str) -> str:
    hora_int = int(hora.split(':')[0])
    if 5 <= hora_int < 11:
        return "Café da Manhã"
    elif 11 <= hora_int < 15:
        return "Almoço"
    elif 15 <= hora_int < 18:
        return "Lanche"
    else:
        return "Jantar"

# ⏰ Valida e formata horário
def validar_e_formatar_horario(hora: str) -> str:
    try:
        partes = hora.split(":")
        if len(partes) != 2:
            raise ValueError("Formato inválido. Use HH:MM.")

        hora_int = int(partes[0])
        minuto_int = int(partes[1])

        if not (0 <= hora_int < 24) or not (0 <= minuto_int < 60):
            raise ValueError("Horário fora dos limites válidos.")

        return f"{hora_int:02}:{minuto_int:02}"
    except Exception as e:
        raise ValueError(f"Erro ao validar o horário: {str(e)}")

# 🔥 Função que salva os agendamentos no Firebase
async def salvar_agenda(agendamentos, id_user):
    try:
        ref = db.reference(f"users/{id_user}/diaries")

        for agendamento in agendamentos:
            refeicao = agendamento.get('refeicao')
            hora = validar_e_formatar_horario(agendamento.get('hora'))

            if not refeicao or not hora:
                raise ValueError("Refeição e hora são obrigatórios.")

            tipo_refeicao = identificar_tipo_refeicao(hora)

            # Calcula calorias via IA (substituir por TBCA futuramente)
            prompt = f"Calcule as calorias para a refeição '{refeicao}'. Apenas me retorne um número inteiro, sem nenhuma palavra."
            model = gemini.GenerativeModel("gemini-1.5-flash", system_instruction="Retorne apenas um número inteiro representando calorias.")
            gemini_response = await model.generate_content_async(prompt)

            calorias = gemini_response.text.strip()
            if not calorias.isdigit():
                calorias = 0  # Fallback se a IA não responder corretamente

            calorias = int(calorias)

            novo_agendamento = {
                "tipo_refeicao": tipo_refeicao,
                "refeicao": refeicao,
                "hora": hora,
                "calorias": calorias,
                "progress": {
                    "0": False, "1": False, "2": False,
                    "3": False, "4": False, "5": False, "6": False
                }
            }

            ref.push(novo_agendamento)
            print(f"✅ Agendamento salvo: {refeicao} às {hora}")

        return "Agendamento(s) salvo(s) com sucesso!"

    except ValueError as e:
        print(f"❌ Erro: {str(e)}")
        raise

# 🎯 Classe para input de pergunta
class Pergunta(BaseModel):
    pergunta: str
    id_user: str

# 🤖 Função principal da IA
async def read_root(question: Pergunta):
    ref = db.reference(f"users/{question.id_user}")
    dados = ref.get()

    if not dados:
        return {"resposta": "Usuário não encontrado."}

    model = gemini.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=(
            f"Você é a NutrIA, uma assistente nutricional. "
            f"Ajude {dados['nome']} (idade: {dados['idade']} anos, peso: {dados['peso']} kg, altura: {dados['altura']} cm, "
            f"sexo: {dados['sexo']}, objetivo: {dados['objetivo']}) a agendar refeições, calcular calorias, "
            f"e fornecer orientações nutricionais simples. "
            f"Nunca responda perguntas que não sejam relacionadas à nutrição, alimentação, hábitos saudáveis ou agendamento de refeições."
        ),
        tools=[Tool(function_declarations=[schedule_meeting_function])]
    )

    resposta = await model.generate_content_async(
        question.pergunta,
        generation_config=gemini.GenerationConfig(max_output_tokens=5000, temperature=0.1)
    )

    # Verifica se a IA quer chamar uma função
    parts = resposta.candidates[0].content.parts
    if parts and hasattr(parts[0], "function_call"):
        function_call = parts[0].function_call
        args = function_call.args
        print("🧠 IA interpretou:", args)

        if args and 'agendamentos' in args:
            try:
                await salvar_agenda(agendamentos=args['agendamentos'], id_user=question.id_user)
                return {"resposta": "✅ Agendamento(s) realizado(s) com sucesso!"}
            except Exception as e:
                print(f"❌ Erro ao agendar: {str(e)}")
                return {"resposta": f"Erro ao agendar: {str(e)}"}

    return {
        "pergunta": question.pergunta,
        "resposta": resposta.text.strip()
    }
