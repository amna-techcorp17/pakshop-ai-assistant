from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from auth import (register_user, login_user, create_token, verify_token,
                  get_user_sessions, create_session, delete_session,
                  save_message, get_messages, is_first_session)
load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class RegisterData(BaseModel):
    name: str
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class Message(BaseModel):
    role: str
    content: str

class Query(BaseModel):
    message: str
    session_id: Optional[int] = None
    chat_history: Optional[List[Message]] = []

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/register")
def register(data: RegisterData):
    result = register_user(data.name, data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    token = create_token(result["user_id"], result["email"])
    return {"token": token, "name": result["name"], "email": result["email"]}

@app.post("/login")
def login(data: LoginData):
    result = login_user(data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    token = create_token(result["user_id"], result["email"])
    return {"token": token, "name": result["name"], "email": result["email"]}

@app.get("/sessions")
def get_sessions(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    sessions = get_user_sessions(payload["user_id"])
    return {"sessions": [{"id": s[0], "name": s[1], "created_at": s[2]} for s in sessions]}

@app.post("/sessions/create")
def new_session(query: Query, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    session_id = create_session(payload["user_id"], query.message)
    return {"session_id": session_id}

@app.delete("/sessions/{session_id}")
def remove_session(session_id: int, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    delete_session(session_id, payload["user_id"])
    return {"success": True}

@app.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: int, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload["valid"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    messages = get_messages(session_id)
    return {"messages": messages}

@app.post("/chat")
async def chat(query: Query, authorization: str = Header(None)):
    from graph import app as graph_app
    
    is_logged_in = False
    user_id = None
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        if payload["valid"]:
            is_logged_in = True
            user_id = payload["user_id"]

    history_str = ""
    if query.chat_history:
        for msg in query.chat_history[-6:]:
            role = "User" if msg.role == "user" else "Assistant"
            history_str += role + ": " + msg.content[:300] + "\n"

    first_time = is_first_session(user_id) if user_id else True

    result = graph_app.invoke({
        "query": query.message,
        "chat_history": history_str,
        "route": None,
        "search_results": None,
        "platforms_searched": None,
        "platform_links": None,
        "customer_needs": None,
        "comparison_result": None,
        "response": None,
        "evaluation": None
    })

    response = result.get("response", "")
    platform_links = result.get("platform_links", {})
    platforms_searched = result.get("platforms_searched", [])

    if is_logged_in and query.session_id:
        save_message(query.session_id, "user", query.message)
        save_message(query.session_id, "assistant", response, platform_links)

    return {
        "response": response,
        "platform_links": platform_links,
        "platforms_searched": platforms_searched,
        "is_first_time": first_time
    }