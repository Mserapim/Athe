# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.afastamento.models import (
    AfastamentoPrisao,
    AfastamentoSuspensao,
    LicencaAfastamentoConjuge,
    LicencaInteresseParticular,
)
from rh.apd.models import PeriodicEvaluationPerformance
from rh.models import MovimentacaoAposentadoria, MovimentacaoDesligamento

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoAposentadoria)
def signals_apd_movimentacao_desligamento(sender, instance=None, **kargs):
    try:
        with transaction.atomic():
            log.info(">>> DESLIGAMENTO EM GESTOR DE ESTÁGIO PROBATÓRIO >>>>>>>>>>>>>")
            for ped in PeriodicEvaluationPerformance.objects.filter(
                employee=instance.movimentacao_posse, status=1
            ):
                ped.status = 2
                ped.save()
    except Exception as err:
        log.exception(err)


@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=LicencaInteresseParticular)
@receiver(post_save, sender=AfastamentoSuspensao)
def signal_post_save_afastamento_apd(sender, instance=None, **kargs):
    log.info(">>>>>>>>>>>>>>>>> RECALCULANDO SUPENSOES DA APD <<<<<<<<<<<<<<<<<<<<<<")
    try:
        with transaction.atomic():
            apd = PeriodicEvaluationPerformance.objects.get(
                employee__servidor=instance.servidor,
                employee__quadro__cargo__tipo_lei_cargo="EF",
                status=1,
            )
            apd.days_suspended_cron()

    except PeriodicEvaluationPerformance.DoesNotExist:
        log.info("Servidor %s não possui dados em APD." % instance.servidor)
    except Exception as err:
        log.exception(err)
