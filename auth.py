from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3, json

SECRET_KEY = "pak-commerce-secret-key-2026"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_auth_db():
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, email TEXT UNIQUE,
                  password TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, session_name TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER, role TEXT, content TEXT,
                  platform_links TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def register_user(name, email, password):

    # DEBUG
    print("RAW PASSWORD:", repr(password))

    # force string cleanup
    password = str(password).strip()

    if len(password) < 8:
        return {"success": False, "error": "Password too short (min 8 chars)"}

    if len(password.encode('utf-8')) > 72:
        return {"success": False, "error": "Password too long (max 72 bytes)"}

    if len(password.encode('utf-8')) > 72:
        return {"success": False, "error": "Password too long (max 72 bytes)"}

    try:
        conn = sqlite3.connect('pakcommerce.db')
        c = conn.cursor()

        hashed = pwd_context.hash(password)

        c.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            (name, email, hashed, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )

        conn.commit()
        user_id = c.lastrowid
        conn.close()

        return {
            "success": True,
            "user_id": user_id,
            "name": name,
            "email": email
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    
def login_user(email, password):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    if not user or not pwd_context.verify(password, user[3]):
        return {"success": False, "error": "Invalid email or password"}
    return {"success": True, "user_id": user[0], "name": user[1], "email": user[2]}

def create_token(user_id, email):
    expire = datetime.utcnow() + timedelta(days=30)
    data = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "user_id": int(payload["sub"]), "email": payload["email"]}
    except JWTError:
        return {"valid": False}

def get_user_sessions(user_id):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("SELECT id, session_name, created_at FROM sessions WHERE user_id=? ORDER BY id DESC", (user_id,))
    sessions = c.fetchall()
    conn.close()
    return sessions

def create_session(user_id, name):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    keywords = ' '.join(name.split()[:3]) + '...'
    c.execute("INSERT INTO sessions (user_id, session_name, created_at) VALUES (?, ?, ?)",
              (user_id, keywords, datetime.now().strftime("%Y-%m-%d %H:%M")))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def delete_session(session_id, user_id):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id=? AND user_id=?", (session_id, user_id))
    conn.commit()
    conn.close()

def save_message(session_id, role, content, platform_links=None):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, platform_links, timestamp) VALUES (?, ?, ?, ?, ?)",
              (session_id, role, content, json.dumps(platform_links) if platform_links else None,
               datetime.now().strftime("%H:%M")))
    conn.commit()
    conn.close()

def get_messages(session_id):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("SELECT role, content, platform_links FROM messages WHERE session_id=? ORDER BY id", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "platform_links": json.loads(r[2]) if r[2] else None} for r in rows]

def is_first_session(user_id):
    conn = sqlite3.connect('pakcommerce.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM sessions WHERE user_id=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count <= 1

init_auth_db()