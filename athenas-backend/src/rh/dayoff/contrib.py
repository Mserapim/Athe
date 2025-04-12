# -.- coding: utf-8 -.-
from django.contrib.auth.models import User
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger


log = getLogger(__name__)


def is_current_user_system():
    """Este método verifica se o usuário corrente é o athenas. Utiliza get_current_user

    Returns:
        bool
    """
    return get_current_user() == User.objects.get(username="athenas")


def is_current_user_admin():
    """Este método verifica se o usuário corrente é admin. Utiliza get_current_user

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.dayoffadmin")


def is_current_user_immediate_chief(employee):
    return employee.is_immediate_chief(employee_from_user(get_current_user()))


def is_current_user_mediate_chief(employee):
    return employee.is_mediate_chief(employee_from_user(get_current_user()))


def has_perm_homologate_batch_admin():
    """Este método verifica se o usuário possui permissão para homologar a escala.

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.dayoffadmin")


def has_perm_homologate_admin():
    """Este método verifica se o usuário possui permissão para homologar a escala.

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.dayoffadmin")


def has_perm_homologate():
    """Este método verifica se o usuário possui permissão para homologar.

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.can_homologate")


def user_has_perm_authorize_admin():
    """Este método verifica se o usuário possui permissão para autorizar no ato da alteração.

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.dayoffadmin")


def has_perm_cancel_admin():
    """Este método verifica se o usuário possui permissão para autorizar no ato da alteração.

    Returns:
        bool
    """
    return get_current_user().has_perm("dayoff.dayoffadmin")


def has_perm_mediate_chief(user=None):
    """Este método verifica se o usuário possui permissão para autorizar no ato da alteração.

    Returns:
        bool
    """
    user = get_current_user() if not user else user
    return user.has_perm("dayoff.can_authorize_mediate_chief")


def has_perm_block_unblock_ap():
    return get_current_user().has_perm(
        "dayoff.can_block_ap"
    ) and get_current_user().has_perm("dayoff.can_unblock_ap")


def has_perm_super_delete(user=None):
    """Este método verifica se o usuário possui permissão para autorizar no ato da alteração.

    Returns:
        bool
    """
    user = get_current_user() if not user else user
    return user.has_perm("dayoff.can_super_delete")
