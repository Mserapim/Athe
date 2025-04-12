# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from contrib.utils import getLogger
from planejamento.contrato.models import AgreementSupervisor, MinuteSupervisor

log = getLogger(__name__)


@receiver(m2m_changed, sender=AgreementSupervisor.classifications.through)
def change_classification_agreementsupervidor(sender, instance, action, **kwargs):
    if action in ("pre_remove", "pre_clear"):
        raise Exception(
            "Uma vez cadastrado o fiscal, não é mais possível realizar alterações nos campos servidor, tipo e classificação"
        )


@receiver(m2m_changed, sender=MinuteSupervisor.classifications.through)
def change_classification_minutesupervisor(sender, instance, action, **kwargs):
    if action in ("pre_remove", "pre_clear"):
        raise Exception(
            "Uma vez cadastrado o fiscal, não é mais possível realizar alterações nos campos servidor, tipo e classificação"
        )
