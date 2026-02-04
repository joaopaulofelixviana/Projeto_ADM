# Sistema Administrativo Integrado (SAI)

## Sobre o Projeto

O **Sistema Administrativo Integrado (SAI)** é uma aplicação **Full-Stack em Python**, desenvolvida para centralizar e automatizar processos corporativos. O foco é eliminar o trabalho manual repetitivo, reduzir erros operacionais e fornecer inteligência de dados através de dashboards interativos.

O projeto foi modernizado para uma **arquitetura monolítica simplificada**, onde interface, lógica de negócio e banco de dados operam de forma integrada e performática, facilitando o deploy e a manutenção.

---

## Funcionalidades

### Segurança e Acesso

- **Autenticação Segura:** Sistema de login próprio com hash de senha (SHA-256).
- **Controle de Sessão:** Gerenciamento de estado para manter o usuário logado durante o uso.
- **Admin Padrão:** Criação automática de usuário administrador na primeira execução.

### Inteligência de Negócios (BI)

- **Dashboard Interativo:** Visualização de dados em tempo real.
- **Gráficos Dinâmicos:** Implementados com Plotly para análise visual de métricas.
- **Tabelas de Dados:** Visualização e filtragem de clientes e processos.

### Automação e Arquivos

- **Consolidação de Dados:** Unificação de planilhas Excel e CSV.
- **Gestão de Documentos:** Leitura e processamento de PDFs (com `pypdf`).
- **Cobrança Inteligente:** Automação de lógica para envio de cobranças (Simulação).
- **CRUD Completo:** Cadastro, leitura e gestão de Clientes e Usuários.

---

## 🛠 Tecnologias Utilizadas

O projeto utiliza uma stack moderna e direta em Python:

- **Linguagem:** Python 3.12+
- **Core Framework:** Streamlit (Interface e Controle de Estado)
- **Manipulação de Dados:** Pandas
- **Banco de Dados:** SQLite (Arquivo local `sistema_local.db`)
- **Visualização:** Plotly
- **Processamento de Arquivos:** PyPDF, OpenPyXL
- **Criptografia:** Hashlib (Biblioteca padrão)

---

## Instalação e Execução Local

Siga os passos abaixo para rodar o projeto no seu computador:

1. **Clone o repositório**

   ```bash
   git clone [https://github.com/SEU_USUARIO/SEU_PROJETO.git](https://github.com/SEU_USUARIO/SEU_PROJETO.git)
   cd SEU_PROJETO

### Executar os testes

```bash
python -m pytest --cov=.

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
python create_db.py

# Execute a aplicação 
python -m streamlit run dashboard.py
