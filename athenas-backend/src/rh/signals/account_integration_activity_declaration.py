# -*- coding: utf-8 -*-

import json

from django.db.models.signals import pre_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import DeclaracaoAtividade
from rh.task.account_integration import account_integration_proxy

log = getLogger(__name__)


@receiver(pre_save, sender=DeclaracaoAtividade)
def account_integration_activity_declaration_changes(sender, instance, *args, **kwargs):
    changed = False

    log.info(
        "Avaliando modifiações significativas no Servidor %s",
        instance.servidor.matricula,
    )
    if instance.pk:
        if getattr(instance, "__changed_tag", False):
            changed = True
        else:
            pass
            older = DeclaracaoAtividade.objects.get(pk=instance.pk)
            changed = instance.ativo != older.ativo
    else:
        instance.__changed_tag = True

    if changed and not getattr(instance, "__sended_tag", False):
        log.info(
            "Informar ao integrador de contas mudança no Servidor %s.",
            instance.servidor.matricula,
        )
        instance.__sended_tag = True
        account_integration_proxy.delay(
            instance.servidor.pk,
            json.dumps(
                {
                    "servidor_id": instance.servidor.pk,
                    "activity_declaration_id": instance.pk,
                    "method": "WORKPLACE",
                    "active": instance.ativo,
                }
            ),
        )
    else:
        log.info(
            "Sem mudança significativa no Servidor %s.", instance.servidor.matricula
        )
