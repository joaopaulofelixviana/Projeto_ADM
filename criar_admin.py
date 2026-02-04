import requests

# Endereço do seu backend no Render
url = "https://projeto-adm.onrender.com/register"

# Dados do usuário que vamos criar
dados = {
    "username": "admin",
    "email": "admin@email.com",
    "password": "123",  # Sua senha
    "role": "admin"
}

print(f"Tentando criar usuário em: {url}...")

try:
    # Envia o comando para criar o usuário
    response = requests.post(url, json=dados)
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCESSO! Usuário 'admin' criado com a senha '123'.")
    else:
        print(f"❌ ERRO ({response.status_code}): {response.text}")
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")