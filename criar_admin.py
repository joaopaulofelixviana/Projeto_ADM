# Biblioteca usada para fazer requisições HTTP (GET, POST, PUT, DELETE)
# Aqui ela simula um frontend ou um cliente externo
import requests


# =========================
# ENDEREÇO DO BACKEND
# =========================

# URL da rota de cadastro do usuário
# Esse endereço aponta para a API publicada no Render
url = "https://projeto-adm.onrender.com/register"


# =========================
# DADOS DO USUÁRIO
# =========================

# Dados que serão enviados no corpo da requisição (JSON)
# Representa o usuário que queremos cadastrar no sistema
dados = {
    "username": "admin",
    "email": "admin@email.com",
    "password": "123",  # Senha que será criptografada no backend
    "role": "admin"
}


# Exibe no terminal o que o script está tentando fazer
print(f"Tentando criar usuário em: {url}...")


# =========================
# ENVIO DA REQUISIÇÃO
# =========================

try:
    # Envia uma requisição POST para o backend
    # O parâmetro json=dados transforma automaticamente o dicionário em JSON
    response = requests.post(url, json=dados)
    
    # Verifica se o status HTTP indica sucesso
    # 200 ou 201 significam que o usuário foi criado corretamente
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCESSO! Usuário 'admin' criado com a senha '123'.")
    
    # Caso contrário, exibe o código do erro e a resposta da API
    else:
        print(f"❌ ERRO ({response.status_code}): {response.text}")
        

# =========================
# TRATAMENTO DE ERRO
# =========================

except Exception as e:
    # Captura erros de conexão, servidor fora do ar, DNS, etc
    print(f"❌ Erro de conexão: {e}")