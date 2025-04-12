# -*- coding: utf-8 -*-

from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import MovimentacaoRequisicao, PeriodoRequisicao

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoRequisicao)
@receiver(post_save, sender=PeriodoRequisicao)
def sinal_atualiza_requisicao(sender, instance, **kargs):
    requisicao = None
    if isinstance(instance, MovimentacaoRequisicao):
        requisicao = instance
        requisicao.create_period_first(
            data_inicio=requisicao.data_inicio,
            data_fim=requisicao.data_fim,
            publicacao=requisicao.publicacao_movimentacao,
        )
    elif isinstance(instance, PeriodoRequisicao):
        requisicao = instance.requisicao
    if requisicao:
        MovimentacaoRequisicao.atualiza_requisicao(requisicao)
        MovimentacaoRequisicao.atualiza_data_inicio_fim(requisicao)
