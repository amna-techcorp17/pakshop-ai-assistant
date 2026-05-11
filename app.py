from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os

from auth import (
    register_user, login_user, create_token, verify_token,
    get_user_sessions, create_session, delete_session,
    save_message, get_messages, is_first_session
)
from graph import run_agent

app = FastAPI(title="PakShop AI", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files & index.html
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "PakShop AI Backend Running"}

# ── MODELS ──
class RegisterModel(BaseModel):
    name: str
    email: str
    password: str

class LoginModel(BaseModel):
    email: str
    password: str

class ChatModel(BaseModel):
    message: str
    session_id: Optional[int] = None
    # FIX: full chat_history from frontend for context
    chat_history: Optional[List[Dict[str, str]]] = []
    # FIX: user_id to track same user
    user_id: Optional[str] = None

class SessionCreate(BaseModel):
    message: str

# ── AUTH ENDPOINTS ──
@app.post("/register")
def register(data: RegisterModel):
    result = register_user(data.name, data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    token = create_token(result["user_id"], result["email"])
    return {"token": token, "name": result["name"], "email": result["email"]}

@app.post("/login")
def login(data: LoginModel):
    result = login_user(data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    token = create_token(result["user_id"], result["email"])
    return {"token": token, "name": result["name"], "email": result["email"]}

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    result = verify_token(token)
    if not result["valid"]:
        return None
    return result

# ── SESSION ENDPOINTS ──
@app.get("/sessions")
def list_sessions(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sessions = get_user_sessions(user["user_id"])
    return {"sessions": [{"id": s[0], "name": s[1], "created_at": s[2]} for s in sessions]}

@app.post("/sessions/create")
def new_session(data: SessionCreate, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session_id = create_session(user["user_id"], data.message)
    return {"session_id": session_id}

@app.get("/sessions/{session_id}/messages")
def session_messages(session_id: int, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    msgs = get_messages(session_id)
    return {"messages": msgs}

@app.delete("/sessions/{session_id}")
def remove_session(session_id: int, user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    delete_session(session_id, user["user_id"])
    return {"success": True}

# ── CHAT ENDPOINT ──
@app.post("/chat")
def chat(data: ChatModel, user=Depends(get_current_user)):
    """
    Main chat endpoint.
    
    FIX 1: Full chat_history from frontend passed to agent for full context.
    FIX 2: is_first_message tracked via session — only True for very first message.
    FIX 3: user_id passed so agent knows it's the same user.
    """
    
    # Determine if this is the first message of the session
    is_first = False
    
    if user and data.session_id:
        # For logged-in users: check if session has any messages yet
        existing = get_messages(data.session_id)
        is_first = len(existing) == 0
    else:
        # For guests: check if chat_history has only 1 message (the current one)
        hist = data.chat_history or []
        user_msgs = [m for m in hist if m.get("role") == "user"]
        is_first = len(user_msgs) <= 1
    
    # Run agent with full chat history
    result = run_agent(
        user_message=data.message,
        chat_history=data.chat_history or [],
        is_first_message=is_first,
        user_id=data.user_id or (user["email"] if user else None)
    )
    
    # Save messages to DB if logged in
    if user and data.session_id:
        save_message(data.session_id, "user", data.message)
        save_message(
            data.session_id,
            "assistant",
            result["response"],
            result.get("platform_links")
        )
    
    return {
        "response": result["response"],
        "platform_links": result.get("platform_links"),
        "platforms_searched": result.get("platforms_searched", [])
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)