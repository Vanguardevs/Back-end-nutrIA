from fastapi import FastAPI
from pydantic import BaseModel
from database.Get.getUser import verUser
from nutrIA.Ia import read_root

app = FastAPI()

class Pergunta(BaseModel):
    pergunta: str

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