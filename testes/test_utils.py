from utils import hash_senha, verificar_senha

def test_hash_senha():
    senha = "123456"
    senha_hash = hash_senha(senha)
    assert senha != senha_hash

def test_verificar_senha():
    senha = "123456"
    senha_hash = hash_senha(senha)
    assert verificar_senha(senha, senha_hash)
