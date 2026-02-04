# =========================
# IMPORTAÇÕES
# =========================
import sqlite3
import os
from passlib.context import CryptContext


# =========================
# CONFIGURAÇÃO DE SEGURANÇA
# =========================
# Criptografia de senha utilizando bcrypt (padrão de mercado)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# CRIAÇÃO DO BANCO DE DADOS
# =========================
def create_database():
    """
    Cria o banco de dados SQLite e suas tabelas principais.
    Caso o banco ou as tabelas já existam, nada será sobrescrito.
    """
    db_path = 'sistema_adm.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Verificando tabelas...")

    # Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    # --- O banco é criado automaticamente, o que permite rodar o projeto do zero sem configuração manual ---

    # Tabela de Clientes (Essa é a nova!)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'Ativo',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Criar admin se não existir
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        senha_hash = pwd_context.hash("admin123")
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('admin', 'admin@empresa.com', senha_hash, 'admin'))
        print("✅ Usuário admin criado.")

    # Finaliza e salva alterações
    conn.commit()
    conn.close()
    print("✅ Banco de dados pronto!")

# =========================
# EXECUÇÃO DIRETA DO SCRIPT
# =========================
if __name__ == "__main__":
    """
    Permite executar este arquivo diretamente para criar o banco
    antes de iniciar a API.
    """
    create_database()
