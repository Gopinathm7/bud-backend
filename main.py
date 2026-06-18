from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat import get_response, set_companion_mode, get_stats
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    user_id: str
    message: str
    role: str = 'friend'

class ModeRequest(BaseModel):
    user_id: str
    mode: str

@app.get("/")
def root():
    return {"status": "Bud is alive 🟢"}

@app.post("/chat")
async def chat(msg: Message):
    response = get_response(msg.user_id, msg.message, msg.role)
    return {"response": response}

@app.post("/mode")
async def change_mode(req: ModeRequest):
    result = set_companion_mode(req.user_id, req.mode)
    return {"result": result}

@app.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    stats = get_stats(user_id)
    facts = supabase.table("user_facts") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .execute()
    stats["memory_count"] = facts.count if facts.count else 0
    return stats