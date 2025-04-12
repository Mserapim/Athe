# -*- coding: utf-8 -*-
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from judicial.models import Ordinace
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(m2m_changed, sender=Ordinace.legalgrounds.through)
def validate_can_change_ordinace(instance, action, **kwargs):
    if action in ("pre_remove", "pre_add") and instance.read_only:
        raise Exception("Não posso modificar um documento que já foi assinado.")
