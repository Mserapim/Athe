from app.settings import MASTIFF_URL_SERVER, CROWD_SESSION_NAME
from requests.auth import HTTPBasicAuth
import requests
import json


def get_permission(request, app):
    """Busca as permissẽos do usuário logado no Mastiff

    Returns:
       dict:
    """
    token = request.COOKIES.get(CROWD_SESSION_NAME, None)
    request_mastiff = requests.get(
        f"{MASTIFF_URL_SERVER}/{app}/{request.user.username}",
        auth=HTTPBasicAuth(CROWD_SESSION_NAME, token),
    )
    content = json.loads(request_mastiff.content)
    return content
