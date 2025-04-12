# -*- coding: utf-8 -*-

import json

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import Servidor
from rh.task.account_integration import account_integration_proxy

log = getLogger(__name__)


@receiver(pre_save, sender=Servidor)
@receiver(post_save, sender=Servidor)
def account_integration_employee_changes(sender, instance, *args, **kwargs):
    changed = False

    log.info("Avaliando modifiações significativas no Servidor %s", instance.matricula)
    if instance.pk:
        if getattr(instance, "__changed_tag", False):
            changed = True
        else:
            older = Servidor.objects.get(pk=instance.pk)
            changed = instance.ativo != older.ativo
    else:
        instance.__changed_tag = True

    if changed and not getattr(instance, "__sended_tag", False):
        log.info(
            "Informar ao integrador de contas mudança no Servidor %s.",
            instance.matricula,
        )
        instance.__sended_tag = True
        account_integration_proxy.delay(
            instance.pk,
            json.dumps(
                {
                    "servidor_id": instance.pk,
                    "method": "ACTIVATE" if instance.ativo else "INACTIVATE",
                }
            ),
        )
    else:
        log.info("Sem mudança significativa no Servidor %s.", instance.matricula)
