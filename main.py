from fastapi import FastAPI
from pydantic import BaseModel
from nutrIA.Ia import read_root;
import os
from fastapi.middleware.cors import CORSMiddleware
from nutrIA.CheckCalories import check_calories_function

app = FastAPI();

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Isso aqui permite que o front-end acesse o back-end.


class Pergunta(BaseModel):
    pergunta: str
    id_user: str

class CalorieRequest(BaseModel):
    tipo_refeicao: str
    horario: str
    refeicao: str
    id_user: str

@app.post("/calories")
async def check_calories(request: CalorieRequest):
    response = await check_calories_function(
        tipo_refeicao=request.tipo_refeicao,
        horario=request.horario,
        refeicao=request.refeicao,
        id_user=request.id_user
    )
    if(response):
        return {"message": response}

@app.post("/question")
async def read_question(question: Pergunta):
    response = await read_root(question)
    if(response):
        return {"message": response}

@app.post("/dadosUser")
async def verUsuario():
    user = await verUser();
    if(user):
        return {"user": user}

@app.get("/on")
async def ligarRener():
    return {"message":"render on"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port);
