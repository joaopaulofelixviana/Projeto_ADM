# Sistema Administrativo Integrado (SAI)

## Sobre o Projeto

O **Sistema Administrativo Integrado (SAI)** é uma aplicação desenvolvida em **Python**, com foco na automação de processos administrativos, visando a redução de trabalho manual, aumento de produtividade e mitigação de erros operacionais.

O projeto segue uma **arquitetura modular**, separando responsabilidades entre interface de usuário, regras de negócio e persistência de dados, facilitando a manutenção e evolução do sistema.

---

## Funcionalidades

- **Autenticação de Usuários**
  - Sistema de login com **armazenamento seguro de senhas utilizando hash**.
  - Controle de acesso por sessão.

- **Relatórios Gerenciais**
  - Dashboard interativo com indicadores (KPIs).
  - Gráficos dinâmicos para análise de dados.

- **Consolidação de Dados**
  - Importação e unificação automática de múltiplas planilhas Excel e CSV.

- **Cobrança Inteligente**
  - Envio de e-mails personalizados.
  - Seleção de tom de voz conforme perfil do cliente.

- **Organização de Arquivos**
  - Renomeação automática de PDFs com uso de RegEx e OCR.

---

## Arquitetura do Projeto

A aplicação foi estruturada em camadas, seguindo boas práticas de desenvolvimento:

- **Interface (Frontend):** Desenvolvida com Streamlit, responsável pela interação com o usuário.
- **Camada de Negócio:** Processamento das regras e validações do sistema.
- **Persistência de Dados:** Banco de dados relacional para armazenamento seguro das informações.

Apesar de utilizar Python no frontend, o Streamlit gera **HTML e CSS dinamicamente**, sendo executado no navegador do usuário.

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.12+
- **Frontend:** Streamlit
- **Visualização de Dados:** Plotly, Pandas
- **Banco de Dados:** SQLite (com planejamento de migração para PostgreSQL)
- **Manipulação de Arquivos:** PyPDF, OpenPyXL, XlsxWriter
- **Testes:** Pytest, Pytest-Cov
- **Segurança:** Werkzeug (hash de senha)

---

## Segurança

- As senhas dos usuários são armazenadas utilizando **hash criptográfico**, garantindo que nenhuma senha seja salva em texto puro.
- O acesso às funcionalidades do sistema é protegido por controle de sessão.

---

## Operações CRUD

O sistema implementa operações de **CRUD (Create, Read, Update, Delete)** para gerenciamento dos dados, seguindo princípios REST internamente na aplicação.

---

## Testes Automatizados

Foram implementados **testes automatizados** utilizando **Pytest**, garantindo maior confiabilidade do sistema.

### Executar os testes

```bash
python -m pytest --cov=.
