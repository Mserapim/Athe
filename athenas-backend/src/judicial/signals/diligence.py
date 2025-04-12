# -*- coding: utf-8 -*-
from django.db.models.signals import pre_save
from judicial.models import Diligence, JudicialDiligence
from contrib.utils import getLogger
from django.dispatch import receiver

log = getLogger(__name__)


def manifestation_def_deadline(judicial_diligence):
    deadline = int(judicial_diligence.deadline or 0)

    if deadline > 0:
        for manifestation in judicial_diligence.has_manifestations.filter(
            signed_by=None
        ):
            manifestation.def_deadline(deadline)


@receiver(pre_save, sender=Diligence)
@receiver(pre_save, sender=JudicialDiligence)
def diligence_delivered(instance, **kwargs):
    older = None
    instance.delivery_status = int(instance.delivery_status or 0)

    if instance.pk:
        older = Diligence.objects.get(pk=instance.pk)

    if (
        older
        and older.delivery_status != instance.delivery_status
        and instance.is_delivery_status_awaiting_answer
    ):
        log.info("Foi detectado a entrega da diligência %s", instance)
        if hasattr(instance, "judicialdiligence"):
            log.info("A diligência é uma diligência Judicial")
            manifestation_def_deadline(instance.judicialdiligence)
