# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import (
    InativacaoCargoMembro,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReconducao,
    MovimentacaoRemocaoMembro,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    MovimentacaoTitularizacao,
    OrgaoGeral,
    RequestMove,
    ServidorLotacao,
)

log = getLogger(__name__)


# @feature_flag_arquimedes
# def _arquimedes_add_employee_workplace(*args, **kwargs):
#     from rh.signals.arquimedes import arquimedes_add_employee_workplace
#     arquimedes_add_employee_workplace(*args, **kwargs)


# @feature_flag_arquimedes
# def _arquimedes_delete_employee_workplace(*args, **kwargs):
#     from rh.signals.arquimedes import arquimedes_delete_employee_workplace
#     arquimedes_delete_employee_workplace(*args, **kwargs)


@receiver(post_save, sender=ServidorLotacao)
def atualizar_ativo(sender, instance, **kwargs):
    instance._update_owner_field()
    instance.atualiza_cache_ativo()
    instance.call_update_from_departure()


# @receiver(post_save, sender=MovimentacaoRemocaoMembro)
# @receiver(post_save, sender=MovimentacaoPromocao)
# @receiver(post_save, sender=MovimentacaoTitularizacao)
# @receiver(post_save, sender=MovimentacaoPosse)
# def mudanca_lotacao(sender, instance, **kwargs):
#     ServidorLotacao.lotacao_por_provimento(instance)


# @receiver(post_save, sender=MovimentacaoPosse)
# @receiver(post_save, sender=MovimentacaoReconducao)
# @receiver(post_save, sender=MovimentacaoRemocaoMembro)
# @receiver(post_save, sender=MovimentacaoPromocao)
# @receiver(post_save, sender=MovimentacaoTitularizacao)
# @receiver(post_save, sender=RequestMove)
# def set_responsabilidade(sender, instance, **kargs):
#     """
#         A partir do cadastro de responsabilidade do cargo sobre uma lotação,
#         o servidor que assumir este cargo deverá ser designado como responsável
#         daquele departamento.
#     """
#     instance.update_workplace_responsible_by_provision()


@receiver(post_save, sender=MovimentacaoSubstituicao)
@receiver(post_save, sender=MovimentacaoSubstituicaoMembro)
def atualizar_responsavel(sender, instance, **kargs):
    MovimentacaoSubstituicao.call_update_responsible_workplace(instance=instance)
    instance.alteracao_ferias()


@receiver(pre_delete, sender=MovimentacaoSubstituicao)
@receiver(pre_delete, sender=MovimentacaoSubstituicaoMembro)
def remover_responsavel(sender, instance, **kargs):
    MovimentacaoSubstituicao.call_update_responsible_workplace(
        instance=instance, delete=True
    )
    ServidorLotacao.objects.filter(substitution_substituted=instance).update(
        from_substitution=False
    )


@receiver(post_delete, sender=MovimentacaoSubstituicao)
@receiver(post_delete, sender=MovimentacaoSubstituicaoMembro)
def substitution_update_work_assignment_from_departure(sender, instance, **kargs):
    if instance.can_run_process:
        ServidorLotacao.update_work_assignment_from_departure(
            instance.afastamento.instancia_modelo
        )


@receiver(post_save, sender=InativacaoCargoMembro)
@receiver(post_delete, sender=InativacaoCargoMembro)
def inactivation_update_work_assignment_from_departure(sender, instance, **kargs):
    ServidorLotacao.update_work_assignment_from_departure(
        instance.afastamento.instancia_modelo
    )


@receiver(post_delete, sender=OrgaoGeral)
def update_cache_identifier(sender, instance, **kargs):
    if not instance.cache_identifier:
        OrgaoGeral.objects.filter(pk=instance.pk).update(cache_identifier=instance.pk)
