from fastapi import FastAPI;
from pydantic import BaseModel;
from ChatBot.Ia import read_root;
import os;
from fastapi.middleware.cors import CORSMiddleware;
from services.users import get_user

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

@app.post("/question")
async def read_question(question: Pergunta):
    response = await read_root(question)
    if(response):
        return {"message": response}
    
@app.get("/verUsuarios")
async def root():
    user = get_user()
    return {"message": user}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port);