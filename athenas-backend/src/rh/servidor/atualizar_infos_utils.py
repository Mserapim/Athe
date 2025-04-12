from django.contrib.auth.models import User

from rh.gfp.models import Servidor
from rh.models import PessoaFisica


def verificar_infos_para_atualizar(servidor, username_mastiff):
    atualizar_verificado_mastiff = False
    atualizar_username_servidor_antigo = False
    atualizar_username_servidor = False

    if (
        servidor.verificado_mastiff is False
        and servidor.user.username == username_mastiff
    ):
        atualizar_verificado_mastiff = True
    elif username_mastiff is not None and servidor.user.username != username_mastiff:
        atualizar_verificado_mastiff = True
        atualizar_username_servidor = True

        q_user_username_mastiff = User.objects.filter(
            username=username_mastiff
        ).exclude(servidor=servidor)
        if q_user_username_mastiff.exists():
            atualizar_username_servidor_antigo = True

    return {
        "atualizar_verificado_mastiff": atualizar_verificado_mastiff,
        "atualizar_username_servidor_antigo": atualizar_username_servidor_antigo,
        "atualizar_username_servidor": atualizar_username_servidor,
    }


def atualizar_infos(servidor, infos_mastiff, infos_atualizar):
    if infos_atualizar["atualizar_username_servidor_antigo"]:
        User.objects.filter(username=infos_mastiff["username"]).exclude(
            servidor=servidor
        ).update(username=f"{infos_mastiff['username']}_bkp")

    if infos_atualizar["atualizar_verificado_mastiff"]:
        Servidor.objects.filter(pk=servidor.pk).update(verificado_mastiff=True)

    if infos_atualizar["atualizar_username_servidor"]:
        User.objects.filter(pk=servidor.user.pk).update(
            username=infos_mastiff["username"]
        )
        PessoaFisica.objects.filter(pk=servidor.pessoa_fisica.pk).update(
            email_institucional=infos_mastiff["email"]
        )

    if not servidor.id_usuario_mastiff:
        Servidor.objects.filter(pk=servidor.pk).update(
            id_usuario_mastiff=infos_mastiff["id_usuario_mastiff"]
        )
