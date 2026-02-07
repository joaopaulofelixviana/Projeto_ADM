# =========================
# IMPORTAÇÕES
# =========================

# Biblioteca padrão do Python para trabalhar com banco de dados SQLite
import sqlite3

# Biblioteca para manipular caminhos e diretórios do sistema operacional
import os

# FastAPI é o framework principal para criação da API
from fastapi import FastAPI, HTTPException, Depends

# Classes usadas para autenticação via OAuth2 (login com token)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Middleware que permite comunicação entre frontend e backend (CORS)
from fastapi.middleware.cors import CORSMiddleware

# BaseModel valida e tipa os dados recebidos nas requisições
from pydantic import BaseModel

# Biblioteca para criptografia segura de senhas
from passlib.context import CryptContext


# =========================
# INICIALIZAÇÃO DA API
# =========================

# Cria a aplicação FastAPI
app = FastAPI()


# =========================
# CONFIGURAÇÃO DO BANCO DE DADOS
# =========================

# Define o diretório base do projeto
# Isso evita erros em deploy (ex: Render), garantindo sempre o mesmo caminho
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminho absoluto para o banco SQLite
DB_PATH = os.path.join(BASE_DIR, "sistema_adm.db")


# =========================
# CONFIGURAÇÃO CORS
# =========================

# Libera acesso de qualquer origem (ideal para testes e frontend separado)
origins = ["*"]

# Adiciona o middleware de CORS à aplicação
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# CONFIGURAÇÕES DE SEGURANÇA
# =========================

# Define o algoritmo de hash para senhas (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define o esquema de autenticação baseado em token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# =========================
# MODELOS DE DADOS (Pydantic)
# =========================

# Modelo para criação de usuários
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Modelo para cadastro de clientes
class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str


# =========================
# CONEXÃO COM O BANCO
# =========================

# Função reutilizável para conectar ao banco de dados
def get_db_connection():
    # Conecta usando o caminho absoluto
    conn = sqlite3.connect(DB_PATH)
    
    # Permite acessar colunas pelo nome (ex: user["username"])
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# ROTA DE EMERGÊNCIA – CRIAÇÃO DAS TABELAS
# =========================

@app.get("/criar_banco")
def criar_banco_manual():
    """
    Essa rota força a criação das tabelas no banco.
    É útil em ambientes de deploy ou primeira execução.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Criação da tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                role TEXT
            )
        ''')

        # Criação da tabela de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT
            )
        ''')
        
        # Salva as alterações
        conn.commit()
        conn.close()

        return {
            "status": "SUCESSO",
            "msg": "Tabelas criadas com sucesso",
            "caminho_banco": DB_PATH
        }
    except Exception as e:
        return {"status": "ERRO", "msg": str(e)}


# Executa automaticamente a criação do banco ao iniciar a API
criar_banco_manual()


# =========================
# ROTAS DO SISTEMA
# =========================

# Rota raiz para verificar se a API está online
@app.get("/")
def read_root():
    return {"status": "online", "banco_local": DB_PATH}


# =========================
# CADASTRO DE USUÁRIO
# =========================

@app.post("/register", status_code=201)
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Criptografa a senha antes de salvar
    hashed_password = pwd_context.hash(user.password)

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (user.username, user.email, hashed_password, 'user')
        )
        conn.commit()
        conn.close()

        return {"mensagem": f"Usuário {user.username} criado com sucesso!"}

    # Tratamento de erro para usuário duplicado
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuário já existe.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# LOGIN E GERAÇÃO DE TOKEN
# =========================

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Busca o usuário pelo username
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    # Verifica se usuário existe e se a senha está correta
    if not user or not pwd_context.verify(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    # Retorna um token simples (username)
    return {"access_token": user['username'], "token_type": "bearer"}


# =========================
# DEPENDÊNCIA DE AUTENTICAÇÃO
# =========================

async def get_current_user(token: str = Depends(oauth2_scheme)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # O token representa o username
    cursor.execute("SELECT username, email, role FROM users WHERE username = ?", (token,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")

    return user


# =========================
# ROTAS PROTEGIDAS – CLIENTES
# =========================

# Cadastro de clientes (somente usuário autenticado)
@app.post("/clients", status_code=201)
def add_client(client: ClientCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
        (client.name, client.email, client.phone)
    )

    conn.commit()
    conn.close()
    return {"msg": "Cliente cadastrado com sucesso!"}


# Listagem de clientes (rota protegida)
@app.get("/clients")
def list_clients(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()

    conn.close()
    return clients