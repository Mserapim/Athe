# -*- coding: utf-8 -*-
from django.db.models.signals import pre_save
from django.dispatch import receiver
from judicial.tac.models import Activity, ActivityHistory
from contrib.utils import getLogger
from contrib.middleware import get_current_user

log = getLogger(__name__)


@receiver(pre_save, sender=Activity)
def logger(sender, instance, **kargs):
    if instance.changed is True:
        # log.info('Activity %(tac)s foi modificado', vars(instance))
        log.info(">> Aplicando historico de atividades <<")
        ah = ActivityHistory(**instance.old_fields)
        ah.author = get_current_user()
        instance.activity_history.add(ah)
