import google.generativeai as gemini
from pydantic import BaseModel
import os
import firebase_admin
from google.generativeai.types import FunctionDeclaration, Tool
from firebase.firebase_config import firebase_admin, db

admin = firebase_admin

# API_KEY = "AIzaSyC-9oOoUxE0v13DNuE37qBzClAfhJrxRJs"

API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY)

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

def indentificar_tipo_refeicao(hora: str) -> str:
    hora_int = int(hora.split(':')[0])
    if 6 <= hora_int < 11:
        return "Café Da Manhã"
    elif 11 <= hora_int < 15:
        return "Almoço"
    elif 15 <= hora_int < 19:
        return "Lanche"
    else:
        return "Jantar"

def validar_e_formatar_horario(hora: str) -> str:
    """
    Valida e formata o horário no formato HH:MM.
    :param hora: Horário fornecido pelo usuário.
    :return: Horário formatado no formato HH:MM ou levanta uma exceção se inválido.

    """
    try:
        partes = hora.split(":")
        if len(partes) != 2:
            raise ValueError("Formato de horário inválido. Use HH:MM.")

        hora_int = int(partes[0])
        minuto_int = int(partes[1])

        if not (0 <= hora_int < 24) or not (0 <= minuto_int < 60):
            raise ValueError("Horário fora dos limites válidos.")

        return f"{hora_int:02}:{minuto_int:02}"
    except Exception as e:
        raise ValueError(f"Erro ao validar o horário: {str(e)}")

async def salvar_agenda(refeicao, hora, id_user):
    """
    Salva o agendamento no banco de dados Firebase.
    :param refeicao: Nome da refeição.
    :param hora: Horário agendado no formato "HH:mm".
    :param id_user: ID do usuário.

    """
    try:
        hora_formatada = validar_e_formatar_horario(hora)

        tipo_refeicao = indentificar_tipo_refeicao(hora_formatada)
        if not refeicao or not hora:
            print("❌ Erro: Refeição ou hora não informados.")
            return
        
        prompt = f"Calcule as calorias para a refeição '{refeicao}'"
        model = gemini.GenerativeModel("gemini-1.5-flash", system_instruction="Você deve apenas retornar numero")
        gemini_response = await model.generate_content_async(prompt)

        calorias = gemini_response.text.strip()
        if not calorias.isdigit():
            return "Erro ao calcular as calorias. Resposta inválida do Gemini."

        calorias = int(calorias)

        ref = db.reference(f"users/{id_user}/diaries")

        novo_agendamento = {
            "tipo_refeicao": tipo_refeicao,
            "refeicao": refeicao,
            "hora": hora_formatada,
            "calorias": calorias,
            "progress": {
                "0": False,
                "1": False,
                "2": False,
                "3": False,
                "4": False,
                "5": False,
                "6": False
            }
        }

        ref.push(novo_agendamento)

        print(f"✅ Agendamento salvo para o usuário {id_user}")
    except ValueError as e:
        print(f"❌ Erro ao salvar agendamento: {str(e)}")


class Pergunta(BaseModel):
    pergunta: str
    id_user: str

async def read_root(question: Pergunta):
    ref = db.reference(f"users/{question.id_user}")
    dados = ref.get()

    # Carrega o histórico como lista
    history_ref = db.reference(f"users/{question.id_user}/history")
    data_history = history_ref.get() or []

    # Garante que data_history é uma lista
    if not isinstance(data_history, list):
        data_history = []

    # Converte o histórico para o formato esperado pelo Gemini
    gemini_history = []
    for item in data_history:
        if "pergunta" in item and "resposta" in item:
            gemini_history.append({"role": "user", "parts": [item["pergunta"]]})
            gemini_history.append({"role": "model", "parts": [item["resposta"]]})

    system_instruction = (
        f"Você é uma assistente nutricional de um aplicativo chamado NutrIA, esse é seu nome. "
        f"Sempre lembre o usuário de checar um nutricionista real. "
        f"Responda objetivamente e apenas sobre nutrição. "
        f"Dados do usuário: nome: {dados['nome']}, idade: {dados['idade']}, peso: {dados['peso']}, altura: {dados['altura']}, sexo: {dados['sexo']}, objetivo: {dados['objetivo']}.\n"
    )

    if question.pergunta == "/lailson":
        return {"resposta":"🦧"}

    if question.pergunta == "/kauan":
        return {"resposta":"Modo Autista ativado! 🦖"}

    model = gemini.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_instruction,
        tools=[Tool(function_declarations=[schedule_meeting_function])],
    )

    chat = model.start_chat(history=gemini_history)

    resposta = await chat.send_message_async(
        question.pergunta,
        generation_config=gemini.GenerationConfig(max_output_tokens=5000, temperature=0.1)
    )

    data_history.append({
        "pergunta": question.pergunta,
        "resposta": resposta.text
    })

    history_ref.set(data_history)

    parts = resposta.candidates[0].content.parts
    if parts and hasattr(parts[0], "function_call"):
        function_call = parts[0].function_call
        args = function_call.args
        print("🧠 IA interpretou:", args)

        if args:
            try:
                await salvar_agenda(**args, id_user=question.id_user)
                return {
                    "resposta": "Agendado com sucesso!"
                }
            except Exception as e:
                print(f"❌ Erro ao agendar: {str(e)}")
                return {
                    "resposta": f"Erro ao agendar: {str(e)}"
                }

    return {
        "pergunta": question.pergunta,
        "resposta": resposta.text
    }
