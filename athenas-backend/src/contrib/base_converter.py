import base64
import os
import re


ALPHABET = "$@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def baseN_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return "".join(arr)


def baseN_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = strlen - (idx + 1)
        num += alphabet.index(char) * (base**power)
        idx += 1

    return num


def image_to_base64(image_path):
    """conveter uma imagem em base64
    Arguments:
    - image_path
    """
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode("utf-8")
            return base64_encoded


def str_to_bool(val):
    """Converte uma representação de string de um bool para verdadeiro (True) ou falso (False).

    Valores verdadeiros são 'y', 'yes', 't', 'true', 'on' e '1'; valores falsos
    são 'n', 'no', 'f', 'false', 'off' e '0'. Levanta ValueError se
    'val' for qualquer outra coisa.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("Valor inválido para booleano: %r" % (val,))


def normalizar_nome(nome):
    """Função que substitui caracteres especiais por "_"
    Arguments:
    - nome - string
    """
    nome_normalizado = re.sub(r"[^a-zA-Z0-9_]", "_", nome)
    return nome_normalizado


def formatar_hora_timedelta(timedelta):
    """Função que fomarta um date timedelta ex: 16:00:00
    Arguments:
    - timedelta
    Returns:
    - hora formatada (str)
    """
    total_segundos = abs(int(timedelta.total_seconds()))
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    formato_hora = f"{horas:02}:{minutos:02}:{segundos:02}"
    if timedelta.total_seconds() < 0:
        formato_hora = f"-{formato_hora}"

    return formato_hora
