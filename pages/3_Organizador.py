import streamlit as st
from pypdf import PdfReader
import re
import io
import zipfile

st.set_page_config(page_title="Organizador de Documentos", layout="wide")

st.title("Organizador de Documentos")
st.markdown("Faça upload de Notas Fiscais ou Contratos (PDF) para renomeação automática.")

# Upload de arquivos
uploaded_pdfs = st.file_uploader(
    "Arraste seus documentos PDF aqui", 
    type=['pdf'], 
    accept_multiple_files=True
)

if uploaded_pdfs:
    st.divider()
    st.subheader("Análise dos Arquivos")
    
    arquivos_processados = []

    # Cria uma tabela para mostrar o "Antes e Depois"
    for file in uploaded_pdfs:
        try:
            # Ler o PDF
            reader = PdfReader(file)
            texto_completo = ""
            for page in reader.pages:
                texto_completo += page.extract_text()
            
            # --- INTELIGÊNCIA (REGEX) ---
            # Tenta achar um valor monetário (ex: R$ 1.500,00)
            busca_valor = re.search(r'R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})', texto_completo)
            valor_encontrado = busca_valor.group(1).replace('.', '').replace(',', '.') if busca_valor else "0.00"
            
            # Tenta achar uma data (ex: 20/01/2024)
            busca_data = re.search(r'\d{2}/\d{2}/\d{4}', texto_completo)
            data_encontrada = busca_data.group(0).replace('/', '-') if busca_data else "Data_Nao_Encontrada"
            
            # Define o novo nome
            novo_nome = f"NF_{data_encontrada}_Valor_{valor_encontrado}.pdf"
            
            arquivos_processados.append({
                "Nome Original": file.name,
                "Valor Identificado": f"R$ {valor_encontrado}",
                "Novo Nome Sugerido": novo_nome,
                "Conteudo": file.getvalue()
            })
            
        except Exception as e:
            st.error(f"Erro ao ler {file.name}: {e}")

    # Mostra a tabela de resultados
    if arquivos_processados:
        df_resultados = st.dataframe(
            arquivos_processados, 
            column_config={
                "Conteudo": None # Esconde a coluna de dados binários
            },
            use_container_width=True
        )

        st.success("Arquivos processados! Pronto para baixar organizado.")

        # --- BOTÃO DE DOWNLOAD (ZIP) ---
        # Cria um arquivo ZIP em memória com todos os PDFs renomeados
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for arq in arquivos_processados:
                # Adiciona cada arquivo no zip com o NOVO nome
                zf.writestr(arq["Novo Nome Sugerido"], arq["Conteudo"])

        st.download_button(
            label="Baixar Tudo Organizado (.zip)",
            data=zip_buffer.getvalue(),
            file_name="Documentos_Organizados.zip",
            mime="application/zip",
            type="primary"
        )