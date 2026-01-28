import sqlite3
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_database():
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

    conn.commit()
    conn.close()
    print("✅ Banco de dados pronto!")

if __name__ == "__main__":
    create_database()