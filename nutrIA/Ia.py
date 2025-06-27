import google.generativeai as gemini
from pydantic import BaseModel
import os
import firebase_admin
from google.generativeai.types import FunctionDeclaration, Tool
from firebase.firebase_config import firebase_admin, db
import re

admin = firebase_admin

API_KEY = "AIzaSyAqBpci6y0BYtrKhiLLlhQg77lLI6X8QnE"

# API_KEY = os.getenv("GEMINI_API")
gemini.configure(api_key=API_KEY)

Food_scheduling = FunctionDeclaration(
    name="Food_scheduling",
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

update_name_function = FunctionDeclaration(
    name="update_name",
    description="Atualizar nome do usuário",
    parameters={
        "type": "object",
        "properties": {
            "nome":{
                "type": "string",
                "description": "Vitor"
            },
        },
        "required": ["nome"],
    },
)

update_peso_function = FunctionDeclaration(
    name="update_peso",
    description="Atualizar peso do usuário",
    parameters={
        "type": "object",
        "properties": {
            "peso":{
                "type": "string",
                "description": "65"
            },
        },
        "required": ["peso"],
    },
)

update_height_function = FunctionDeclaration(
    name="update_altura",
    description="Atualizar altura do usuário",
    parameters={
        "type": "object",
        "properties": {
            "altura":{
                "type": "string",
                "description": "1.70"
            },
        },
        "required": ["altura"],
    },
)

calcular_calorias_function = FunctionDeclaration(
    name="calcular_calorias",
    description="Calcule as calorias diárias com base no peso, altura, idade e sexo",
    parameters={
        "type": "object",
        "properties": {
            "peso": {
                "type": "string",
                "description": "Peso do usuário em kg"
            },
            "altura": {
                "type": "string",
                "description": "Altura do usuário em metros"
            },
            "idade": {
                "type": "string",
                "description": "Idade do usuário em anos"
            },
            "sexo": {
                "type": "string",
                "description": "Sexo do usuário (masculino ou feminino)"
            },
            "objetivo": {
                "type": "string",
                "description": "objetivo do usuário (opcional)"
            }
        },
        "required": ["peso", "altura", "idade", "sexo", "objetivo"],
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
        return {"resposta":"Agendado com sucesso!"}
    except ValueError as e:
        print(f"❌ Erro ao salvar agendamento: {str(e)}")
        return {"resposta":"Erro ao agendar, tente novamente."}

class Pergunta(BaseModel):
    pergunta: str
    id_user: str

async def read_root(question: Pergunta):
    
    ref = db.reference(f"users/{question.id_user}")
    dados = ref.get()

    # # Carrega o histórico como lista
    # history_ref = db.reference(f"users/{question.id_user}/history")
    # data_history = history_ref.get() or []

    # # Garante que data_history é uma lista
    # if not isinstance(data_history, list):
    #     data_history = []

    # # Converte o histórico para o formato esperado pelo Gemini
    # gemini_history = []
    # for item in data_history:
    #     if "pergunta" in item and "resposta" in item:
    #         gemini_history.append({"role": "user", "parts": [item["pergunta"]]})
    #         gemini_history.append({"role": "model", "parts": [item["resposta"]]})


    system_instruction = (
        f"Você é uma assistente nutricional de um aplicativo chamado NutrIA. "
        f"Sempre que o usuário informar dados como nome, peso ou altura, utilize as funções disponíveis para atualizar essas informações no sistema, ao invés de apenas responder em texto. "
        f"Sempre lembre o usuário de checar um nutricionista real. "
        f"Responda objetivamente e apenas sobre nutrição. "
        f"Dados do usuário: nome: {dados['nome']}, idade: {dados['idade']}, peso: {dados['peso']}, altura: {dados['altura']}, sexo: {dados['sexo']}, objetivo: {dados['objetivo']}.\n"
    )

#-----------------------------------------------------------------------------------------------------#
    if question.pergunta == "/lailson":
        return {"resposta":"🦧"}

    if question.pergunta == "/kauan":
        return {"resposta":"Modo Autista ativado! 🦖"}

#-----------------------------------------------------------------------------------------------------#


    model = gemini.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_instruction,
        tools=[Tool(function_declarations=[Food_scheduling, update_name_function, update_peso_function, update_height_function, calcular_calorias_function])],
    )

    resposta = await model.generate_content_async(
        question.pergunta,
        generation_config=gemini.GenerationConfig(
            max_output_tokens=5000,
            temperature=0.2,
        )
    )

    # chat = model.start_chat(history=gemini_history)

    # resposta = await chat.send_message_async(
    #     question.pergunta,
    #     generation_config=gemini.GenerationConfig(max_output_tokens=5000, temperature=0.2)
    # )

    # data_history.append({
    #     "pergunta": question.pergunta,
    #     "resposta": resposta.text
    # })

    # history_ref.set(data_history)

    parts = resposta.candidates[0].content.parts
    if parts and hasattr(parts[0], "function_call"):
        function_call = parts[0].function_call
        args = function_call.args
        function_name = function_call.name
        print("🧠 IA interpretou:", args, "Função:", function_name)

        if args:
            try:
                if function_name == "Food_scheduling" and "refeicao" in args and "hora" in args:
                    resp = await salvar_agenda(**args, id_user=question.id_user)
                    print("✅ Agendamento realizado com sucesso!")
                    return {"resposta": resp["resposta"]}
                
                elif function_name == "update_name" and "nome" in args:
                    try:
                        ref = db.reference(f"users/{question.id_user}")
                        ref.update({"nome": args["nome"]})
                        print("✅ Nome atualizado com sucesso!")
                        return {"resposta": "Nome atualizado com sucesso!"}
                    except Exception as e:
                        print(f"❌ Erro ao atualizar nome: {str(e)}")
                        return {"resposta": "Erro ao atualizar nome, tente novamente."}
                
                elif function_name == "update_peso" and "peso" in args:
                    try:
                        ref = db.reference(f"users/{question.id_user}")
                        ref.update({"peso": args["peso"]})
                        print("✅ Peso atualizado com sucesso!")
                        return {"resposta": "Peso atualizado com sucesso!"}
                    except Exception as e:
                        print(f"❌ Erro ao atualizar peso: {str(e)}")
                        return {"resposta": "Erro ao atualizar peso, tente novamente."}
                    
                elif function_name == "update_altura" and "altura" in args:
                    try:
                        ref = db.reference(f"users/{question.id_user}")
                        ref.update({"altura": args["altura"]})
                        print("✅ Altura atualizada com sucesso!")
                        return {"resposta": "Altura atualizada com sucesso!"}
                    except Exception as e:
                        print(f"❌ Erro ao atualizar altura: {str(e)}")
                        return {"resposta": "Erro ao atualizar altura, tente novamente."}
                
                elif function_name == "calcular_calorias" and all(k in args for k in ["peso", "altura", "idade", "sexo"]):
                    try:
                        peso = args["peso"]
                        altura = args["altura"]
                        idade = args["idade"]
                        sexo = args["sexo"]
                        meta = args["objetivo"]

                        prompt = f"Calcule as calorias diárias para um usuário com peso {peso} kg, altura {altura} m, idade {idade} anos e sexo {sexo} e que possui uma meta de {meta}."
                        model_calorias = gemini.GenerativeModel("gemini-1.5-flash", system_instruction="Você deve apenas retornar numero")
                        gemini_response = await model_calorias.generate_content_async(prompt)

                        calorias = gemini_response.text.strip()
                        if not calorias.isdigit():
                            return {"resposta": "Erro ao calcular as calorias. Resposta inválida do Gemini."}

                        calorias = int(calorias)
                        print(f"✅ Calorias calculadas: {calorias}")
                        return {"resposta": f"As calorias diárias recomendadas são: {calorias} kcal."}
                    except Exception as e:
                        print(f"❌ Erro ao calcular calorias: {str(e)}")
                        return {"resposta": "Erro ao calcular calorias, tente novamente."}

                else:
                    return {"resposta": "Pedido não reconhecido ou dados inválidos, Tente novamente"}
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
                return {
                    "resposta": f"Erro: {str(e)}"
                }

    try:
        parts = resposta.candidates[0].content.parts
        resposta_texto = ""
        for part in parts:
            if hasattr(part, "text"):
                resposta_texto += part.text

        # Tenta identificar atualização de peso na resposta textual
        match = re.search(r"atualizar seu peso para (\d+)", resposta_texto)
        if match:
            novo_peso = match.group(1)
            ref = db.reference(f"users/{question.id_user}")
            ref.update({"peso": novo_peso})
            print("✅ Peso atualizado via resposta textual!")
        
        if not resposta_texto:
            resposta_texto = "Não foi possível interpretar a resposta da IA."
    except Exception:
        resposta_texto = "Não foi possível interpretar a resposta da IA."

    return {
        "pergunta": question.pergunta,
        "resposta": resposta_texto
    }
