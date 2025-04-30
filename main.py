from fastapi import FastAPI;
from pydantic import BaseModel;
from ChatBot.Ia import read_root;
import os;
from fastapi.middleware.cors import CORSMiddleware;
from controller.cadastro import create_user as new_user;
from controller.dadosUser import verUser as get_user;

app = FastAPI();

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Isso aqui permite que o front-end acesse o back-end.


class Pergunta(BaseModel):
    pergunta: str

class DadosUser(BaseModel):
    name: str
    email: str
    password: str
    idade: int
    sexo: str
    tipo_usuario: str
    objetivo: str

@app.post("/question")
async def read_question(question: Pergunta):
    response = await read_root(question)
    if(response):
        return {"message": response}
    
@app.get("/verUsuarios/{email}/{senha}")
async def root(email: str, senha: str):
    user = get_user(email, senha)
    return {"message": user}

@app.post("/criarUsuario")
def create_user(user: DadosUser):
    res = new_user(user.name, user.email, user.password, user.idade, user.sexo, user.tipo_usuario, user.objetivo)
    return {"message":res}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port);