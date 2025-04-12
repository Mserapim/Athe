# -*- coding: utf-8 -*-
from django.db.models.signals import pre_save
from judicial.models import Manifestation, RejectionFact
from contrib.utils import getLogger
from django.dispatch import receiver

log = getLogger(__name__)


@receiver(pre_save, sender=Manifestation)
def manifestation_signed(instance, **kwargs):
    older = None
    instance.who_type = int(instance.who_type or 0)

    if instance.pk:
        older = Manifestation.objects.get(pk=instance.pk)

    if older and older.signed_by != instance.signed_by:
        log.info("A manifestação foi assinada")
        if isinstance(older.reference.my_origin, RejectionFact) and older.who_type == 1:
            log.info(
                "Identificada manifestação do interessado contra o arquivamento da noticia d fato."
            )
            instance.reference.my_origin.imtimate_accused()
