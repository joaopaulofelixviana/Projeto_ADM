# =========================
# IMPORTAÇÕES
# =========================
import sqlite3
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext


# =========================
# INICIALIZAÇÃO DA API
# =========================
# O FastAPI já gera automaticamente a documentação (Swagger),
# facilitando testes, manutenção e entendimento da API.
app = FastAPI(
    title="Sistema Administrativo API",
    description="API conectada a banco de dados real com autenticação segura",
    version="1.0.0"
)


# =========================
# CONFIGURAÇÕES DE SEGURANÇA
# =========================

# Criptografia de senha usando bcrypt (padrão de mercado)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define onde o token será enviado (rota de login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# =========================
# MODELOS DE DADOS (Pydantic)
# =========================
# Garantem validação e segurança dos dados recebidos pela API
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str


# =========================
# CONEXÃO COM O BANCO DE DADOS
# =========================
def get_db_connection():
    """
    Cria e retorna uma conexão com o banco SQLite.
    O código verifica o caminho do banco para garantir compatibilidade
    tanto em ambiente local quanto em produção.
    """
    db_path = 'backend/sistema_adm.db'
    if not os.path.exists(db_path):
        db_path = 'sistema_adm.db'

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn


# =========================
# FUNÇÃO DE SEGURANÇA (VALIDAÇÃO DO TOKEN)
# =========================
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Função responsável por validar o token de acesso.
    Caso o token seja inválido, o acesso à rota é bloqueado.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # O token representa o usuário autenticado
    cursor.execute(
        "SELECT username, email, role FROM users WHERE username = ?",
        (token,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# =========================
# ROTAS GERAIS
# =========================
@app.get("/")
def read_root():
    """
    Rota raiz para verificação rápida do status da API.
    """
    return {"status": "online", "banco": "Conectado 🟢"}


@app.get("/users")
def get_users():
    """
    Lista todos os usuários cadastrados.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")


# =========================
# ROTA DE CADASTRO DE USUÁRIO
# =========================
@app.post("/register", status_code=201)
def create_user(user: UserCreate):
    """
    Cria um novo usuário com senha criptografada.
    Nenhuma senha é armazenada em texto puro.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criptografa a senha antes de salvar no banco
    hashed_password = pwd_context.hash(user.password)

    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (user.username, user.email, hashed_password, 'user')
        )
        conn.commit()
        conn.close()

        return {"mensagem": f"Usuário {user.username} criado com sucesso!"}

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Usuário ou email já cadastrado."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ROTA DE LOGIN (GERAÇÃO DE TOKEN)
# =========================
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Realiza autenticação do usuário.
    Se as credenciais forem válidas, retorna um token de acesso.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Busca o usuário pelo username
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (form_data.username,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")

    # Verifica se a senha informada corresponde ao hash armazenado
    if not pwd_context.verify(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")

    # Retorna o token de acesso
    return {
        "access_token": user['username'],
        "token_type": "bearer"
    }


# =========================
# ROTA PROTEGIDA (USUÁRIO LOGADO)
# =========================
@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado.
    Só pode ser acessada com token válido.
    """
    return {
        "msg": "Você entrou na área protegida!",
        "usuario": current_user['username'],
        "cargo": current_user['role'],
        "email": current_user['email']
    }


# =========================
# ROTAS DE CLIENTES (CRUD)
# =========================
@app.post("/clients", status_code=201)
def add_client(
    client: ClientCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Cadastra um novo cliente.
    Apenas usuários autenticados podem acessar.
    """
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


@app.get("/clients")
def list_clients(current_user: dict = Depends(get_current_user)):
    """
    Lista todos os clientes cadastrados.
    Acesso restrito a usuários autenticados.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients
