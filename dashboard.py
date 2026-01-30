import streamlit as st
import requests
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Sistema Administrativo", page_icon="🏢", layout="wide")

# dashboard.py

# COMENTE A LINHA ANTIGA
# API_URL = "http://127.0.0.1:8000"

# COLOQUE A NOVA (Copie exatamente o link da sua imagem)
API_URL = "https://projeto-adm.onrender.com"

# --- FUNÇÕES DE CONEXÃO ---
def login(username, password):
    try:
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        st.error("Erro: Não foi possível conectar ao servidor. Verifique se o backend está rodando!")
        return None

def get_clients(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/clients", headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def add_client(token, name, email, phone):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "email": email, "phone": phone}
    response = requests.post(f"{API_URL}/clients", json=data, headers=headers)
    return response

# --- LÓGICA DA TELA ---

# Verifica se já existe um token na sessão (memória do navegador)
if 'token' not in st.session_state:
    st.session_state['token'] = None

# TELA DE LOGIN (Se não tiver token, mostra isso)
if st.session_state['token'] is None:
    st.title("Acesso ao Sistema")
    col1, col2 = st.columns([1, 2]) # Ajuste visual
    with col1:
        st.markdown("Entre com suas credenciais para acessar o painel administrativo.")
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema", type="primary"):
            data = login(user, pwd)
            if data:
                st.session_state['token'] = data['access_token']
                st.rerun() # Recarrega a página para entrar
            else:
                st.error("Usuário ou senha incorretos!")

# TELA PRINCIPAL (Se tiver token, mostra o menu)
else:
    # Menu Lateral
    st.sidebar.title("Menu Admin")
    st.sidebar.write(f"Logado como: **Admin**")
    menu = st.sidebar.radio("Navegação", ["Dashboard Clientes", "Novo Cadastro", "Sair"])

    # 1. VISUALIZAR CLIENTES
    if menu == "Dashboard Clientes":
        st.title("Carteira de Clientes")
        st.write("Lista completa de clientes ativos no sistema.")
        
        clients_data = get_clients(st.session_state['token'])
        
        if clients_data:
            # Cria uma tabela bonita com Pandas
            df = pd.DataFrame(clients_data, columns=["ID", "Nome", "Email", "Telefone", "Status", "Data Criação"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cliente cadastrado ainda.")

    # 2. CADASTRAR CLIENTE
    elif menu == "Novo Cadastro":
        st.title("Novo Cliente")
        st.write("Preencha os dados abaixo para adicionar um novo registro.")
        
        with st.form("new_client_form"):
            name = st.text_input("Nome Completo")
            col_a, col_b = st.columns(2)
            with col_a:
                email = st.text_input("Email Corporativo")
            with col_b:
                phone = st.text_input("Telefone / WhatsApp")
            
            submit = st.form_submit_button("💾 Salvar Cliente")

            if submit:
                res = add_client(st.session_state['token'], name, email, phone)
                if res.status_code == 201:
                    st.success("Cliente cadastrado com sucesso!")
                elif res.status_code == 401:
                    st.error("Sua sessão expirou. Faça login novamente.")
                else:
                    st.error(f"Erro ao cadastrar: {res.text}")

    # 3. LOGOUT
    elif menu == "Sair":
        st.session_state['token'] = None
        st.rerun()