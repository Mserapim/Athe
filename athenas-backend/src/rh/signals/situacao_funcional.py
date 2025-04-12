# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELADO, SUSPENSAO
from rh.models import (
    MovimentacaoAposentadoria,
    MovimentacaoAproveitamento,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoRemocaoMembro,
    MovimentacaoReversao,
    MovimentacaoTitularizacao,
    PossessionResident,
    RequestMove,
    PossessionCollaborator,
    PossessionTrainee,
    SituacaoFuncional,
    BenefitMovement,
)

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoAposentadoria)
@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoRemocaoMembro)
@receiver(post_save, sender=MovimentacaoTitularizacao)
@receiver(post_save, sender=MovimentacaoPromocao)
@receiver(post_save, sender=MovimentacaoAproveitamento)
@receiver(post_save, sender=MovimentacaoReadaptacao)
@receiver(post_save, sender=MovimentacaoReconducao)
@receiver(post_save, sender=MovimentacaoReintegracao)
@receiver(post_save, sender=MovimentacaoReversao)
@receiver(post_save, sender=RequestMove)
@receiver(post_save, sender=PossessionTrainee)
@receiver(post_save, sender=PossessionResident)
@receiver(post_save, sender=PossessionCollaborator)
@receiver(post_save, sender=BenefitMovement)
def create_functional_status(sender, instance, **kargs):
    """
    Este sinal é responsável por criar a situação funcional do servidor.
    """
    employee, date_start, date_end, situation, instance = (
        SituacaoFuncional.prepare_parameter_functional_status(instance)
    )
    try:
        SituacaoFuncional.create_functional_status(
            employee=employee,
            date_start=date_start,
            date_end=date_end,
            situation=situation,
            instance=instance,
        )
    except Exception as err:
        log.exception(err)


@receiver(pre_delete, sender=MovimentacaoRemocaoMembro)
@receiver(pre_delete, sender=MovimentacaoTitularizacao)
@receiver(pre_delete, sender=MovimentacaoPromocao)
@receiver(pre_delete, sender=MovimentacaoAproveitamento)
@receiver(pre_delete, sender=MovimentacaoReadaptacao)
@receiver(pre_delete, sender=MovimentacaoReconducao)
@receiver(pre_delete, sender=MovimentacaoReintegracao)
@receiver(pre_delete, sender=MovimentacaoReversao)
@receiver(pre_delete, sender=PossessionTrainee)
@receiver(pre_delete, sender=PossessionResident)
@receiver(pre_delete, sender=PossessionCollaborator)
@receiver(pre_delete, sender=MovimentacaoDesligamento)
@receiver(pre_delete, sender=MovimentacaoAposentadoria)
@receiver(pre_delete, sender=BenefitMovement)
@receiver(pre_delete, sender=MovimentacaoPosse)
@receiver(pre_delete, sender=RequestMove)
# @receiver(pre_delete, sender=BaseLicencaAfastamento)
def apagar_situacao_funcional(sender, instance, **kargs):
    try:
        employee, date_start, date_end, situation, instance = (
            SituacaoFuncional.prepare_parameter_functional_status(instance)
        )
        log.debug("%s %s %s %s" % (employee, date_start, date_end, situation))
        SituacaoFuncional.delete_functional_status(
            employee=employee,
            date_start=date_start,
            date_end=date_end,
            situation=situation,
            instance=instance,
        )
    except Exception as err:
        log.exception(err)


@receiver(post_save, sender=SituacaoFuncional)
def call_manager_situations(sender, instance, **kargs):
    SituacaoFuncional._manager_situations(employee=instance.servidor)
