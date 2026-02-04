import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema ADM", layout="wide")

# --- BANCO DE DADOS LOCAL (Tudo acontece aqui) ---
def get_connection():
    # Cria o banco 'sistema_local.db' direto na pasta do projeto
    conn = sqlite3.connect("sistema_local.db")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    ''')
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    
    # Cria usuário ADMIN padrão se não existir (admin / 123)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Senha "123" criptografada (hash simples para facilitar)
        senha_hash = hashlib.sha256("123".encode()).hexdigest()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', senha_hash, 'admin'))
    
    conn.commit()
    conn.close()

# Inicializa o banco assim que abre
init_db()

# --- FUNÇÕES DE LÓGICA ---
def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    senha_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, senha_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def add_client(name, email, phone):
    conn = get_connection()
    conn.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
    conn.commit()
    conn.close()

def get_clients():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM clients", conn)
    conn.close()
    return df

# --- CONTROLE DE SESSÃO (LOGIN) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ================================
# TELA DE LOGIN
# ================================
if not st.session_state["logged_in"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Acesso ao Sistema")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary"):
            user = check_login(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun() # Recarrega a página para entrar
            else:
                st.error("Usuário ou senha incorretos!")
                st.info("Dica: admin / 123")

# ================================
# TELA PRINCIPAL (DASHBOARD)
# ================================
else:
    # Barra Lateral
    with st.sidebar:
        st.write(f"👤 Olá, **{st.session_state['username']}**")
        if st.button("Sair"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.title("🚀 Painel Administrativo")
    
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Novo Cadastro"])
    
    with tab1:
        st.subheader("Clientes Cadastrados")
        df = get_clients()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum cliente cadastrado ainda.")
            
    with tab2:
        st.subheader("Cadastrar Novo Cliente")
        with st.form("form_cliente"):
            name = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            phone = st.text_input("Telefone")
            submitted = st.form_submit_button("Salvar Cliente")
            
            if submitted:
                if name and email:
                    add_client(name, email, phone)
                    st.success("Cliente salvo com sucesso!")
                    # Pequeno hack para atualizar a tabela na outra aba
                else:
                    st.warning("Preencha pelo menos Nome e E-mail.")