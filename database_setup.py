import sqlite3

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('sistema_adm.db')
cursor = conn.cursor()

print("🔌 Conectado ao Banco de Dados SQLite...")

# --- 1. TABELA DE USUÁRIOS (Autenticação) ---
# Armazena quem pode acessar. A senha será Hash (criptografada) no futuro.
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user', -- 'admin' ou 'user'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# --- 2. TABELA DE CLIENTES (Normalização) ---
# Separamos os dados do cliente para não repetir em cada fatura.
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# --- 3. TABELA DE FATURAS/COBRANÇAS (Operações) ---
# Aqui usamos Chave Estrangeira (Foreign Key) para ligar ao cliente.
cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'Pendente', -- 'Pago', 'Pendente', 'Atrasado'
    due_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (id)
);
''')

print("✅ Tabelas criadas com sucesso (Modelo Físico implementado)!")

# --- DADOS INICIAIS (SEED) ---
# Vamos inserir um usuário Admin padrão para você testar depois
try:
    # Senha "admin123" simulada (em produção usaremos hash real)
    cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)", 
                   ('admin', 'admin@empresa.com', 'admin123', 'admin'))
    print("👤 Usuário Admin criado.")
except sqlite3.IntegrityError:
    print("ℹ️ Usuário Admin já existe.")

conn.commit()
conn.close()