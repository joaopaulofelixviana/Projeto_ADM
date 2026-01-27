import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Cobrança Automática", layout="wide")

st.title("Cobrança Automática")
st.markdown("Gerencie inadimplência e envie lembretes personalizados.")

# DADOS FICTÍCIOS
dados = {
    "Cliente": ["TechFlow Ltda", "Empresa Digital SA", "Inovação Tech", "Solutions Corp", "Smart Business"],
    "Valor": [12500.00, 5300.00, 15100.00, 3200.00, 8200.00],
    "Atraso": [5, 2, 15, 42, 22],
    "Email": ["financeiro@techflow.com", "contato@empresa.sa", "fin@inovacao.tech", "adm@solutions.com", "sb@smart.com"]
}
df = pd.DataFrame(dados)

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Inadimplentes", len(df))
col2.metric("Valor Total em Aberto", f"R$ {df['Valor'].sum():,.2f}")
col3.metric("Média de Atraso", f"{int(df['Atraso'].mean())} dias")

st.divider()

# TABELA INTERATIVA
st.subheader("Lista de Clientes Pendentes")

# Checkbox para selecionar todos
todos = st.checkbox("Selecionar Todos")

if todos:
    selecionados = df
else:
    # Seleção manual (multiselect simulado)
    clientes_selecionados = st.multiselect(
        "Selecione os clientes para cobrar:", 
        df["Cliente"].tolist()
    )
    selecionados = df[df["Cliente"].isin(clientes_selecionados)]

st.dataframe(
    selecionados if not selecionados.empty else df, 
    use_container_width=True,
    hide_index=True
)

st.divider()

# --- ÁREA DE CONFIGURAÇÃO DO ENVIO (NOVA) ---
if not selecionados.empty:
    st.subheader("⚙️ Configuração do Disparo")
    
    col_msg, col_preview = st.columns([1, 2])
    
    with col_msg:
        st.markdown("**Personalização**")
        tom_voz = st.radio(
            "Escolha o Tom de Voz:", 
            ["Amigável", "Corporativo", "Incisivo"]
        )
    
    # Lógica do texto baseada no tom
    if tom_voz == "Amigável":
        assunto = "Lembrete gentil sobre sua fatura"
        texto_base = "Olá! Notamos que sua fatura venceu recentemente. Sabemos que a correria do dia a dia acontece. Segue a 2ª via!"
    elif tom_voz == "Corporativo":
        assunto = "Aviso de Pendência Financeira"
        texto_base = "Prezados, informamos que consta em aberto o título em nosso sistema. Solicitamos a regularização o mais breve possível."
    else:
        assunto = "URGENTE: Regularização de Débito"
        texto_base = "Aviso Final: O não pagamento do valor pendente acarretará na suspensão imediata dos serviços contratados."

    with col_preview:
        st.markdown("**Prévia da Mensagem:**")
        st.info(f"**Assunto:** {assunto}\n\n**Corpo:**\n{texto_base}")

    # BOTÃO DE ENVIO
    if st.button(f"Enviar E-mails para {len(selecionados)} clientes", type="primary"):
        progress_text = "Conectando ao servidor de e-mail..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.02) # Simula o envio
            my_bar.progress(percent_complete + 1, text="Enviando...")
            
        time.sleep(1)
        my_bar.empty()
        st.success(f"Sucesso! {len(selecionados)} e-mails enviados no tom '{tom_voz}'.")
        st.balloons()
else:
    st.info("Selecione pelo menos um cliente acima para habilitar o envio.")