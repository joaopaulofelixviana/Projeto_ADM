import streamlit as st
import time

st.set_page_config(page_title="Sistema Administrativo", layout="wide", page_icon="🏢")

# --- SISTEMA DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False

def check_password():
    st.title("Acesso Restrito")
    senha = st.text_input("Digite sua senha de acesso:", type="password")
    if st.button("Entrar"):
        if senha == "admin123": # <--- SUA SENHA AQUI
            st.session_state["logado"] = True
            st.success("Logado com sucesso!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Senha incorreta.")

if not st.session_state["logado"]:
    check_password()
    st.stop() # PARA TUDO AQUI SE NÃO TIVER LOGADO

# ==================================================
# SE PASSOU DO LOGIN, O CÓDIGO ABAIXO É EXECUTADO:
# ==================================================

# Sidebar com logo e menu
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.markdown("### Bem-vindo, Administrador")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

# Título Principal
st.title("Automação de Processos Administrativos")
st.markdown("Elimine tarefas repetitivas, reduza erros humanos e otimize seu tempo.")

st.divider()

# Layout de Colunas para os Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.info("**Relatórios Automatizados**")
    st.write("Consolidação de planilhas e Dashboard Gerencial de Vendas.")
    if st.button("Acessar Relatórios"):
        st.switch_page("pages/1_Relatorios.py")

with col2:
    st.warning("**Cobrança Automática**")
    st.write("Envio automático de e-mails personalizados para inadimplentes.")
    if st.button("Acessar Cobrança"):
        st.switch_page("pages/2_Cobranca.py")

with col3:
    st.error("**Organizador de Documentos**")
    st.write("Organização inteligente de notas fiscais e contratos.")
    if st.button("Acessar Organizador"):
        st.switch_page("pages/3_Organizador.py")

st.divider()