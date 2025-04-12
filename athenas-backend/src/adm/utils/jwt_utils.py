import jwt
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings

# Chave secreta usada para assinar o token (substitua por algo seguro)
SECRET_KEY = settings.JWT_SECRET_KEY


def gerar_token_jwt(usuario, data_limite=None, gerar_unico=False):
    # Informações básicas do payload
    payload = {
        "usuario": usuario,
    }

    # Adiciona o campo 'exp' caso tenha sido fornecida uma data_limite
    if data_limite:
        if isinstance(data_limite, datetime):
            payload["exp"] = int(
                data_limite.timestamp()
            )  # Usando timestamp para consistência
        else:
            data_limite_dt = datetime.combine(data_limite, datetime.min.time())
            payload["exp"] = int(data_limite_dt.timestamp())

    # Se 'gerar_unico' for True, adiciona o campo 'iat' para tornar o token único
    if gerar_unico:
        payload["iat"] = datetime.utcnow()  # Data/hora de geração (Issued At)

    # Gera o token JWT
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    return token


def verificar_token_jwt(token):
    try:
        # Decodifica o token usando a chave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Retorna o usuário se o token for válido
        return {"status": "válido", "usuario": payload["usuario"]}

    except ExpiredSignatureError:
        # Retorna uma mensagem se o token expirou
        return {"status": "expirado", "mensagem": "O token já expirou."}

    except InvalidTokenError:
        # Retorna uma mensagem se o token for inválido
        return {"status": "inválido", "mensagem": "Token inválido."}
