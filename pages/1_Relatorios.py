import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Relatórios & Dashboard", layout="wide")

st.title("Relatórios Inteligentes")
st.markdown("Faça upload das planilhas de vendas para gerar insights e unificar arquivos.")

# Upload
uploaded_files = st.file_uploader(
    "Solte suas planilhas de Vendas aqui (Excel/CSV)", 
    accept_multiple_files=True, 
    type=["xlsx", "csv"]
)

if uploaded_files:
    # --- PROCESSAMENTO DOS ARQUIVOS ---
    all_data = []
    for file in uploaded_files:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            all_data.append(df)
        except Exception as e:
            st.error(f"Erro ao ler {file.name}: {e}")

    if all_data:
        # Junta tudo num só
        consolidado = pd.concat(all_data, ignore_index=True)
        
        st.success(f"{len(uploaded_files)} arquivos processados e unificados!")
        
        st.divider()
        st.subheader("Dashboard Gerencial")

        # Padroniza nomes das colunas
        consolidado.columns = [c.capitalize() for c in consolidado.columns]
        colunas_existentes = consolidado.columns.tolist()
        
        # Tenta identificar colunas automaticamente
        col_valor = next((c for c in ['Valor', 'Total', 'Venda', 'Receita'] if c in colunas_existentes), None)
        col_vendedor = next((c for c in ['Vendedor', 'Funcionario', 'Representante'] if c in colunas_existentes), None)
        col_regiao = next((c for c in ['Regiao', 'Estado', 'Uf', 'Cidade'] if c in colunas_existentes), None)

        if col_valor:
            # Métricas (KPIs)
            kpi1, kpi2, kpi3 = st.columns(3)
            total_vendas = consolidado[col_valor].sum()
            media_vendas = consolidado[col_valor].mean()
            
            kpi1.metric("Faturamento Total", f"R$ {total_vendas:,.2f}")
            kpi2.metric("Ticket Médio", f"R$ {media_vendas:,.2f}")
            kpi3.metric("Transações", len(consolidado))
            
            st.markdown("---")
            
            graf1, graf2 = st.columns(2)
            
            # Gráfico 1: Vendas por Vendedor com Linha de Meta
            if col_vendedor:
                vendas_por_vendedor = consolidado.groupby(col_vendedor)[col_valor].sum().reset_index()
                fig_bar = px.bar(vendas_por_vendedor, x=col_vendedor, y=col_valor, title="🏆 Top Vendedores", color=col_valor)
                
                # ADICIONANDO LINHA DE META (Média + 10%)
                meta = vendas_por_vendedor[col_valor].mean() * 1.1
                fig_bar.add_hline(y=meta, line_dash="dot", annotation_text="Meta Sugerida", line_color="red")
                
                graf1.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfico 2: Pizza por Região
            if col_regiao:
                vendas_por_regiao = consolidado.groupby(col_regiao)[col_valor].sum().reset_index()
                fig_pie = px.pie(vendas_por_regiao, names=col_regiao, values=col_valor, title="🌍 Faturamento por Região")
                graf2.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.warning("Não encontramos uma coluna de 'Valor' (R$) para gerar gráficos.")

        # --- NOVA FUNCIONALIDADE: DOWNLOAD ---
        st.divider()
        st.subheader("Baixar Dados Consolidados")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            consolidado.to_excel(writer, index=False, sheet_name='Dados_Consolidados')
            
        st.download_button(
            label="📥 Baixar Planilha Unificada (.xlsx)",
            data=output.getvalue(),
            file_name="Relatorio_Final_Consolidado.xlsx",
            mime="application/vnd.ms-excel",
            type="primary"
        )

        with st.expander("Ver Tabela Completa"):
            st.dataframe(consolidado, use_container_width=True)

else:
    # MODO DEMONSTRAÇÃO (Sem arquivos)
    st.info("👆 Faça o upload para ver seus dados. Veja abaixo um exemplo do Dashboard:")
    
    dados_demo = {
        "Vendedor": ["Ana", "Carlos", "Ana", "Beatriz", "Carlos", "Beatriz"],
        "Região": ["Sul", "Sudeste", "Sul", "Nordeste", "Sudeste", "Nordeste"],
        "Valor": [1200.50, 3400.00, 800.00, 5600.00, 2100.00, 1200.00]
    }
    df_demo = pd.DataFrame(dados_demo)
    
    col1, col2 = st.columns(2)
    fig_demo = px.bar(df_demo, x="Vendedor", y="Valor", title="Demonstração: Vendas por Vendedor", color="Vendedor")
    col1.plotly_chart(fig_demo, use_container_width=True)