# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, pre_delete, post_delete
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.afastamento.models import (
    AfastamentoComparecimentoJuizo,
    AfastamentoCandidatura,
    AfastamentoCompeticao,
    AfastamentoCursoConcurso,
    AfastamentoDeslocamento,
    AfastamentoDisponibilidade,
    HealthPrevent,
    AfastamentoEleitoral,
    AfastamentoEstudar,
    AfastamentoMandatoEletivo,
    AfastamentoMissao,
    AfastamentoOutroOrgao,
    AfastamentoPrisao,
    AfastamentoServirJuri,
    AfastamentoSuspensao,
    AfastamentoTreinamento,
    AtuacaoGrupoTrabalho,
    AusenciaCasamento,
    AusenciaConclusao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
    AusenciaFalecimento,
    AusenciaNascimento,
    BancoDeHoras,
    BaseLicencaAfastamento,
    DesempenhoFuncao,
    FeriasAfastamento,
    FolgaAniversario,
    FolgaCompensacao,
    FolgaEleitoral,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaDoencaPessoaFamilia,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    LicencaMaternidade,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
    Plantao,
    Recesso,
    Viagem,
    AwardLicense,
)
from rh.models import (
    MovimentacaoAposentadoria,
    MovimentacaoDesligamento,
    MovimentacaoSubstituicao,
    Prorrogacao,
    ServidorLotacao,
)
from rh.signals.situacao_funcional import create_functional_status

log = getLogger(__name__)


@receiver(post_save, sender=FeriasAfastamento)
@receiver(post_save, sender=Viagem)
@receiver(post_save, sender=Recesso)
@receiver(post_save, sender=FolgaEleitoral)
@receiver(post_save, sender=FolgaAniversario)
@receiver(post_save, sender=FolgaCompensacao)
@receiver(post_save, sender=BancoDeHoras)
@receiver(post_save, sender=AtuacaoGrupoTrabalho)
@receiver(post_save, sender=DesempenhoFuncao)
@receiver(post_save, sender=Plantao)
@receiver(post_save, sender=LicencaSaude3Dias)
@receiver(post_save, sender=LicencaSaude30Dias)
@receiver(post_save, sender=LicencaSaudeJuntaMedica)
@receiver(post_save, sender=LicencaDoencaPessoaFamilia)
@receiver(post_save, sender=LicencaMaternidade)
@receiver(post_save, sender=LicencaAdocao)
@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaServicoMilitar)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaCapacitacao)
@receiver(post_save, sender=LicencaInteresseParticular)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=AwardLicense)
@receiver(post_save, sender=AfastamentoDisponibilidade)
@receiver(post_save, sender=HealthPrevent)
@receiver(post_save, sender=AfastamentoOutroOrgao)
@receiver(post_save, sender=AfastamentoMandatoEletivo)
@receiver(post_save, sender=AfastamentoEstudar)
@receiver(post_save, sender=AfastamentoMissao)
@receiver(post_save, sender=AfastamentoEleitoral)
@receiver(post_save, sender=AfastamentoServirJuri)
@receiver(post_save, sender=AfastamentoTreinamento)
@receiver(post_save, sender=AfastamentoDeslocamento)
@receiver(post_save, sender=AfastamentoCompeticao)
@receiver(post_save, sender=AfastamentoCursoConcurso)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=AfastamentoSuspensao)
@receiver(post_save, sender=AfastamentoComparecimentoJuizo)
@receiver(post_save, sender=AfastamentoCandidatura)
@receiver(post_save, sender=AusenciaDoacaoSangue)
@receiver(post_save, sender=AusenciaEleitor)
@receiver(post_save, sender=AusenciaCasamento)
@receiver(post_save, sender=AusenciaNascimento)
@receiver(post_save, sender=AusenciaFalecimento)
@receiver(post_save, sender=AusenciaConclusao)
@receiver(post_save, sender=Prorrogacao)
@receiver(m2m_changed, sender=BaseLicencaAfastamento.prorrogacao.through)
def atualizar_data_fim_afastamento(sender, instance, **kargs):
    departure = None
    if kargs.get("action") in ("post_remove", "post_add") or ("action" not in kargs):
        if isinstance(instance, Prorrogacao):
            if instance.afastamento.exists():
                departure = instance.afastamento.get().instancia_modelo
        else:
            departure = instance

        if departure:
            if departure.update_date_end:
                departure.set_data_fim_por_prorrogacao(departure)
            if kargs.get("action") == "post_remove" and departure:
                departure.unset_data_fim_por_prorrogacao(departure)
            departure.anotacao_post_save()


@receiver(pre_delete, sender=Prorrogacao)
def pre_delete_pronlogation(sender, instance, **kargs):
    departure = None
    if instance.afastamento.exists():
        departure = instance.afastamento.get().instancia_modelo
        departure.set_data_fim_por_prorrogacao(departure, exclude=[instance.pk])


@receiver(m2m_changed, sender=BaseLicencaAfastamento.designation_exercise.through)
def update_estado(sender, instance, **kargs):
    """
     py:function:: update_estado(sender, instance, **kargs)

    This methods calls update_estado to each ServidorLotacao adds to DesempenhoFuncao.

    :param cls sender: The modelclass sender
    :param object instance: The model instance
    :param dict kargs: The dict default
    """
    try:
        log.debug("m2m_changed BaseLicencaAfastamento.designation_exercise.through")
        # log.debug(kargs.get('action'))
        if kargs.get("action") in ("post_add", "post_remove"):
            ServidorLotacao.update_work_assignment_from_departure(
                instance.instancia_modelo
            )
            # log.debug(kargs.get('model'))
            for pk in kargs.get("pk_set"):
                # log.debug('\n\n\n==================== \n SAVE \n\n\n====================')
                # log.debug(unicode(kargs.get('model').objects.get(pk=pk)))
                with transaction.atomic():
                    base = kargs.get("model").objects.get(pk=pk)
                    base.from_substitution = False
                    if kargs.get("action") == "post_remove":
                        base.changed_by_departure = None
                    base.save()
    except Exception as err:
        log.exception(err)


@receiver(post_save, sender=FeriasAfastamento)
@receiver(post_save, sender=Viagem)
@receiver(post_save, sender=Recesso)
@receiver(post_save, sender=FolgaEleitoral)
@receiver(post_save, sender=FolgaAniversario)
@receiver(post_save, sender=FolgaCompensacao)
@receiver(post_save, sender=BancoDeHoras)
@receiver(post_save, sender=AtuacaoGrupoTrabalho)
@receiver(post_save, sender=DesempenhoFuncao)
@receiver(post_save, sender=Plantao)
@receiver(post_save, sender=LicencaSaude3Dias)
@receiver(post_save, sender=LicencaSaude30Dias)
@receiver(post_save, sender=LicencaSaudeJuntaMedica)
@receiver(post_save, sender=LicencaDoencaPessoaFamilia)
@receiver(post_save, sender=LicencaMaternidade)
@receiver(post_save, sender=LicencaAdocao)
@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaServicoMilitar)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaCapacitacao)
@receiver(post_save, sender=LicencaInteresseParticular)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=AwardLicense)
@receiver(post_save, sender=AfastamentoDisponibilidade)
@receiver(post_save, sender=HealthPrevent)
@receiver(post_save, sender=AfastamentoOutroOrgao)
@receiver(post_save, sender=AfastamentoMandatoEletivo)
@receiver(post_save, sender=AfastamentoEstudar)
@receiver(post_save, sender=AfastamentoMissao)
@receiver(post_save, sender=AfastamentoEleitoral)
@receiver(post_save, sender=AfastamentoServirJuri)
@receiver(post_save, sender=AfastamentoTreinamento)
@receiver(post_save, sender=AfastamentoDeslocamento)
@receiver(post_save, sender=AfastamentoCompeticao)
@receiver(post_save, sender=AfastamentoCursoConcurso)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=AfastamentoSuspensao)
@receiver(post_save, sender=AfastamentoComparecimentoJuizo)
@receiver(post_save, sender=AfastamentoCandidatura)
@receiver(post_save, sender=AusenciaDoacaoSangue)
@receiver(post_save, sender=AusenciaEleitor)
@receiver(post_save, sender=AusenciaCasamento)
@receiver(post_save, sender=AusenciaNascimento)
@receiver(post_save, sender=AusenciaFalecimento)
@receiver(post_save, sender=AusenciaConclusao)
def atualizar_estado(sender, instance, **kargs):
    instance.call_update_vacation_reference_from_employee()
    # FIXME: REESCREVER IMPLEMENTAÇÃO DA ATUALIZAÇÃO DO AFASTAMENTO E VOLTAR IMPLEMENTAÇÃO PARA JUDICIAL
    if hasattr(instance.servidor, "officerdiligence"):
        from rh.const import ACTIVE

        status = 1
        if instance.estado == ACTIVE:
            status = 2
        officer = instance.servidor.officerdiligence
        if not officer.is_removed and officer.status != status:
            try:
                with transaction.atomic():
                    officer.status = status
                    officer.save()
            except Exception as err:
                log.exception(err)

    # BaseLicencaAfastamento.atualizar_estado(instance=instance)  # changed
    BaseLicencaAfastamento.alteracao_ferias(afastamento=instance)
    if not isinstance(instance, Viagem):
        create_functional_status(sender, instance, **kargs)
    MovimentacaoSubstituicao.update_from_departure(instance)
    ServidorLotacao.update_work_assignment_from_departure(instance.instancia_modelo)


@receiver(pre_delete, sender=FeriasAfastamento)
@receiver(pre_delete, sender=Viagem)
@receiver(pre_delete, sender=Recesso)
@receiver(pre_delete, sender=FolgaEleitoral)
@receiver(pre_delete, sender=FolgaAniversario)
@receiver(pre_delete, sender=FolgaCompensacao)
@receiver(pre_delete, sender=BancoDeHoras)
@receiver(pre_delete, sender=AtuacaoGrupoTrabalho)
@receiver(pre_delete, sender=DesempenhoFuncao)
@receiver(pre_delete, sender=Plantao)
@receiver(pre_delete, sender=LicencaSaude3Dias)
@receiver(pre_delete, sender=LicencaSaude30Dias)
@receiver(pre_delete, sender=LicencaSaudeJuntaMedica)
@receiver(pre_delete, sender=LicencaDoencaPessoaFamilia)
@receiver(pre_delete, sender=LicencaMaternidade)
@receiver(pre_delete, sender=LicencaAdocao)
@receiver(pre_delete, sender=LicencaAfastamentoConjuge)
@receiver(pre_delete, sender=LicencaServicoMilitar)
@receiver(pre_delete, sender=LicencaAtividadePolitica)
@receiver(pre_delete, sender=LicencaCapacitacao)
@receiver(pre_delete, sender=LicencaInteresseParticular)
@receiver(pre_delete, sender=LicencaMandatoClassista)
@receiver(pre_delete, sender=AwardLicense)
@receiver(pre_delete, sender=AfastamentoDisponibilidade)
@receiver(pre_delete, sender=HealthPrevent)
@receiver(pre_delete, sender=AfastamentoOutroOrgao)
@receiver(pre_delete, sender=AfastamentoMandatoEletivo)
@receiver(pre_delete, sender=AfastamentoEstudar)
@receiver(pre_delete, sender=AfastamentoMissao)
@receiver(pre_delete, sender=AfastamentoEleitoral)
@receiver(pre_delete, sender=AfastamentoServirJuri)
@receiver(pre_delete, sender=AfastamentoTreinamento)
@receiver(pre_delete, sender=AfastamentoDeslocamento)
@receiver(pre_delete, sender=AfastamentoCompeticao)
@receiver(pre_delete, sender=AfastamentoCursoConcurso)
@receiver(pre_delete, sender=AfastamentoPrisao)
@receiver(pre_delete, sender=AfastamentoSuspensao)
@receiver(pre_delete, sender=AfastamentoComparecimentoJuizo)
@receiver(pre_delete, sender=AfastamentoCandidatura)
@receiver(pre_delete, sender=AusenciaDoacaoSangue)
@receiver(pre_delete, sender=AusenciaEleitor)
@receiver(pre_delete, sender=AusenciaCasamento)
@receiver(pre_delete, sender=AusenciaNascimento)
@receiver(pre_delete, sender=AusenciaFalecimento)
@receiver(pre_delete, sender=AusenciaConclusao)
def employee_workplace_set_changed_by_departure(sender, instance, **kargs):
    """
    NÃO FUNCIONA POIS O .DELETE NÃO ESTÁ SENDO CHAMADO.

    @DEPRECATED IN FAVOR OF ServidorLotacao.update_work_assignment_from_departure
    """
    pass


@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=LicencaInteresseParticular)
def encerrar_lotacao(sender, instance, **kargs):
    log.debug(">>>>>>>>>>> ENCERRAR LOTACAO <<<<<<<<<<<<")
    try:
        if (
            not instance.servidor.membro
            and instance.servidor._raw_locations(
                date=instance.data_inicio, option=1
            ).exists()
        ):
            workplace = instance.servidor._raw_locations(
                date=instance.data_inicio, option=1
            ).first()
            if not workplace.data_vigencia_fim:
                workplace.data_vigencia_fim = instance.data_inicio
                workplace.save()
    except Exception as e:
        raise e
