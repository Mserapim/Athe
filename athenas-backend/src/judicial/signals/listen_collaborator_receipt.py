# -*- coding: utf-8 -*-

from django.dispatch import receiver
from django.db.models.signals import post_save
from edocs.protocolo.models import Movimentacao
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(post_save, sender=Movimentacao)
def fill_receipt_of_collaborator(sender, instance, signal, **kargs):
    request_collaboration = getattr(instance, "requestcollaboration", None)

    if request_collaboration and instance.data_recebimento:
        request_collaboration.received_at = instance.data_recebimento
        request_collaboration.received_by = instance.servidor_destino.user
        request_collaboration.save()
