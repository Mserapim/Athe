# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import PeriodoRequisicao, RequestMove

log = getLogger(__name__)


@receiver(post_save, sender=RequestMove)
def create_first_period(sender, instance, **kargs):
    transaction.on_commit(lambda: instance.create_first_period())


@receiver(post_save, sender=PeriodoRequisicao)
@receiver(post_delete, sender=PeriodoRequisicao)
def update_request_move(sender, instance, **kargs):
    transaction.on_commit(lambda: instance.request_move.update_request_move())
