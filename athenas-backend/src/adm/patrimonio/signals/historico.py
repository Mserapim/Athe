# -*- coding: utf-8 -*-
from adm.patrimonio.models import Patrimonio, PatrimonioHistorico
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from django.db.models.signals import post_save
from django.dispatch import receiver

log = getLogger(__name__)


@receiver(post_save, sender=Patrimonio)
def logger(sender, instance, **kargs):
    if instance.changed is True:
        log.info("Patrimonio %(plaqueta)s foi modificado", vars(instance))
        ph = PatrimonioHistorico(**instance.old_fields)
        ph.who = get_current_user()
        instance.historico.add(ph, bulk=False)
