# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from judicial.models import PartLawsuitAccess
from rh.models import Lotacao, Servidor
from contrib.utils import getLogger
from django.dispatch import receiver
from django.contrib.auth.models import User
from contrib.middleware import set_current_user, get_current_user


log = getLogger(__name__)


@receiver(post_save, sender=Lotacao)
def confidential_lawsuit_permission(instance, **kwargs):
    try:
        current_user = get_current_user()
        diff = instance.diff

        if not diff:
            log.debug("Lotacao atualizada. Mas não ocorreu mudança do responsável.")
        else:
            old_boss = diff.get("responsavel_id")[0]
            new_boss = diff.get("responsavel_id")[1]

            new_boss = Servidor.objects.get(pk=new_boss) if new_boss else None
            old_boss = Servidor.objects.get(pk=old_boss) if old_boss else None

            if new_boss:
                log.debug(
                    "Realizando troca das permissões de acesso aos processos com sigilo."
                )
                set_current_user(User.objects.get(username="athenas"))
                PartLawsuitAccess.swap_permission_access(
                    location=instance, new_employee=new_boss, old_employee=old_boss
                )

    except Exception as e:
        log.info("Ocorreu um erro.")
        log.exception(e)

    finally:

        set_current_user(current_user)
