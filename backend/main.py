import sqlite3
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI(
    title="Sistema Administrativo API",
    description="API conectada ao Banco de Dados Real com Login Seguro",
    version="1.0.0"
)

# --- CONFIGURAÇÕES DE SEGURANÇA ---
# 1. Criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Onde o sistema vai procurar o token (na rota /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- MODELOS DE DADOS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# ADICIONE ISSO AQUI EMBAIXO:
class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str

# --- FUNÇÃO DE CONEXÃO COM O BANCO ---
def get_db_connection():
    db_path = 'backend/sistema_adm.db'
    if not os.path.exists(db_path):
        db_path = 'sistema_adm.db'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# --- SEGURANÇA: Função que verifica se o token é válido ---
# (ADICIONADO AGORA: O "Segurança" da balada)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca o usuário usando o token (que por enquanto é o username)
    cursor.execute("SELECT username, email, role FROM users WHERE username = ?", (token,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# --- ROTAS GERAIS ---
@app.get("/")
def read_root():
    return {"status": "online", "banco": "Conectado 🟢"}

@app.get("/users")
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")

# --- ROTA DE CADASTRO (Criptografada) ---
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
        return {"mensagem": f"Usuário {user.username} criado com sucesso!"}
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário ou Email já cadastrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROTA DE LOGIN (Gera o Token) ---
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Busca o usuário pelo nome
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()
    
    # 2. Se não achar usuário, erro
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    # 3. Verifica se a senha bate com o Hash do banco
    senha_correta = pwd_context.verify(form_data.password, user['password_hash'])
    
    if not senha_correta:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    # 4. Retorna o token de acesso
    return {"access_token": user['username'], "token_type": "bearer"}

# --- ROTA PROTEGIDA (Área VIP) ---
# (ADICIONADO AGORA: Só entra com Login)
@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "msg": "Você entrou na área VIP!",
        "usuario": current_user['username'],
        "cargo": current_user['role'],
        "email": current_user['email']
    }
# --- ROTAS DE CLIENTES (CRUD) ---

# 1. Adicionar Cliente (Só logado)
@app.post("/clients", status_code=201)
def add_client(client: ClientCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
            (client.name, client.email, client.phone)
        )
        conn.commit()
        conn.close()
        return {"msg": "Cliente cadastrado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Listar Clientes (Só logado)
@app.get("/clients")
def list_clients(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients