# =========================
# IMPORTAÇÕES
# =========================
import sqlite3
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

# --- CAMINHO ABSOLUTO DO BANCO DE DADOS (CORREÇÃO CRÍTICA) ---
# Isso garante que o banco seja criado SEMPRE no mesmo lugar, não importa onde o Render rode o comando.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_adm.db")

# --- CONFIGURAÇÃO CORS ---
origins = ["*"] # Liberando geral para garantir que funcione primeiro
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURANÇA ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- MODELOS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str

# --- CONEXÃO ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH) # Usa o caminho fixo
    conn.row_factory = sqlite3.Row
    return conn

# --- ROTA DE EMERGÊNCIA PARA CRIAR TABELAS ---
@app.get("/criar_banco")
def criar_banco_manual():
    """
    Acesse essa rota pelo navegador para FORÇAR a criação das tabelas
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabela Users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                role TEXT
            )
        ''')

        # Tabela Clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        return {"status": "SUCESSO", "msg": "Tabelas criadas!", "caminho_banco": DB_PATH}
    except Exception as e:
        return {"status": "ERRO", "msg": str(e)}

# --- EXECUTA NA INICIALIZAÇÃO TAMBÉM ---
criar_banco_manual()


# =========================
# ROTAS DO SISTEMA
# =========================

@app.get("/")
def read_root():
    return {"status": "online", "banco_local": DB_PATH}

@app.post("/register", status_code=201)
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (user.username, user.email, hashed_password, 'user')
        )
        conn.commit()
        conn.close()
        return {"mensagem": f"Usuário {user.username} criado!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not pwd_context.verify(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    
    return {"access_token": user['username'], "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, role FROM users WHERE username = ?", (token,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user

@app.post("/clients", status_code=201)
def add_client(client: ClientCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", 
                   (client.name, client.email, client.phone))
    conn.commit()
    conn.close()
    return {"msg": "Cliente cadastrado!"}

@app.get("/clients")
def list_clients(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients