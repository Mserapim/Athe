from standard.models import ConfigPoint
import ipaddress
from contrib.utils import getLogger

log = getLogger(__name__)


def check_ipaddress(ip):
    """
    Verifica se um endereço IP é válido.
    Args:
        ip (str): O endereço IP a ser verificado.
    Returns:
        bool: True se o IP for válido, False caso contrário.
    """
    for config in ConfigPoint.objects.filter():
        if ipaddress.ip_address(ip) in ipaddress.ip_network(config.network, False):
            return True
    return False


def get_ipaddress(request):
    """
    Obtém o endereço IP da requisição.
    Args:
        request (HttpRequest): O objeto HttpRequest da requisição.
    Returns:
        str: O endereço IP da requisição, ou None se não for possível determiná-lo.
    """
    ip = None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def validate_ip_address(ip):
    """
    Valida se um endereço IP é válido.
    Args:
        ip (str): O endereço IP a ser validado.
    Returns:
        bool: True se o IP for válido, Exception caso contrário.
    """
    if not check_ipaddress(ip):
        raise Exception(f"{ip} - IP inválido para registro de ponto.")
    return True
