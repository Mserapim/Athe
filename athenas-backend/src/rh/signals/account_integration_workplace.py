# -*- coding: utf-8 -*-

import json
from datetime import date

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import ServidorLotacao
from rh.task.account_integration import account_integration_proxy

log = getLogger(__name__)


def is_active(workplace):
    if workplace.data_vigencia_fim and workplace.data_vigencia_fim < date.today():
        return False
    else:
        return True


@receiver(pre_save, sender=ServidorLotacao)
@receiver(post_save, sender=ServidorLotacao)
def account_integration_workplace_changes(sender, instance, *args, **kwargs):
    changed = False

    log.info(
        'Avaliando modificações nos locais de trabalho para "%s"', instance.servidor
    )

    if instance.pk:
        if getattr(instance, "__changed_tag", False):
            changed = True
        else:
            older = ServidorLotacao.objects.get(pk=instance.pk)
            changed = is_active(instance) != is_active(older)
    else:
        instance.__changed_tag = True

    if changed and not getattr(instance, "__sended_tag", False):
        log.info(
            'Informar ao integrador de contas mudança no Servidor "%s".',
            instance.servidor,
        )
        instance.__sended_tag = True
        account_integration_proxy.delay(
            instance.servidor.pk,
            json.dumps(
                {
                    "servidor_id": instance.servidor.pk,
                    "workplace_id": instance.pk,
                    "method": "WORKPLACE",
                    "active": is_active(instance),
                }
            ),
        )
    else:
        log.info(
            "Sem mudança significativa no Servidor %s.", instance.servidor.matricula
        )
