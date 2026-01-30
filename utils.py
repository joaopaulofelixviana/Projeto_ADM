from werkzeug.security import generate_password_hash, check_password_hash

def hash_senha(senha: str) -> str:
    return generate_password_hash(senha)

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    return check_password_hash(senha_hash, senha_digitada)
