# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import (
    BenefitMovement,
    CargaHoraria,
    CargoQuadro,
    DeclaracaoAtividade,
    Dependencia,
    DocsDadosEspecificos,
    Documento,
    Endereco,
    MovimentacaoAposentadoria,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoRemocaoMembro,
    MovimentacaoRequisicao,
    MovimentacaoReversao,
    MovimentacaoTitularizacao,
    NaturalPersonHistory,
    PessoaFisica,
    PossessionCollaborator,
    PossessionTrainee,
    RequestMove,
    Servidor,
    Telefone,
    TerminationBenefitMovement,
)
from rh.ponto.models import Falta

"""
    Sinais relacionados ao módulo RH.
    Todas implementações foram colocadas nos modelos.
    Dessa forma as ações de um modelo que podem ser disparadas por um sinal continuam no próprio modelo.
    Todos sinais são obrigatórios.
"""

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_delete, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoReconducao)
@receiver(post_delete, sender=MovimentacaoReconducao)
@receiver(post_save, sender=MovimentacaoPromocao)
@receiver(post_delete, sender=MovimentacaoPromocao)
@receiver(post_save, sender=MovimentacaoReadaptacao)
@receiver(post_delete, sender=MovimentacaoReadaptacao)
@receiver(post_save, sender=MovimentacaoReintegracao)
@receiver(post_delete, sender=MovimentacaoReintegracao)
@receiver(post_save, sender=MovimentacaoRemocaoMembro)
@receiver(post_delete, sender=MovimentacaoRemocaoMembro)
@receiver(post_save, sender=MovimentacaoReversao)
@receiver(post_delete, sender=MovimentacaoReversao)
@receiver(post_save, sender=MovimentacaoTitularizacao)
@receiver(post_delete, sender=MovimentacaoTitularizacao)
@receiver(post_save, sender=RequestMove)
@receiver(post_delete, sender=RequestMove)
@receiver(post_save, sender=PossessionTrainee)
@receiver(post_delete, sender=PossessionTrainee)
@receiver(post_save, sender=PossessionCollaborator)
@receiver(post_delete, sender=PossessionCollaborator)
@receiver(post_save, sender=BenefitMovement)
@receiver(post_delete, sender=BenefitMovement)
def atualiza_cache_ativo(sender, instance, **kargs):
    """
    Atualiza o @ativo do Servidor.
    """
    instance.servidor.update_dates()
    instance.servidor.atualiza_cache_ativo()
    instance.servidor.update_bond()
    call_update_vacancy_number_filled_from_chart(instance)


def call_update_vacancy_number_filled_from_chart(instance):
    if hasattr(instance, "quadro"):
        CargoQuadro.update_vacancy_number_filled_from_chart(instance.quadro)


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoReconducao)
def atualiza_cache_tipo(sender, instance, **kargs):
    """
    Atualiza o @tipo sempre que o servidor tiver uma posse nova
    Se o servidor tiver pelo menos um cargo do tipo 'M' (membro),
    tipo recebe 'M', caso contrário recebe 'S' ou 'E' para estagiário.
    """
    instance.servidor.atualiza_cache_tipo()


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoRequisicao)
@receiver(post_save, sender=PossessionTrainee)
@receiver(post_save, sender=PossessionCollaborator)
@receiver(post_save, sender=BenefitMovement)
def atualiza_cache_categoria(sender, instance, **kargs):
    """
    Atualiza a categoria do servidor.
    """
    instance.servidor._update_type_by_possession()


@receiver(post_save, sender=MovimentacaoPosse)
def set_data_referencia_ferias(sender, instance, **kargs):
    """
    Atualiza data de atuação de férias, em Servidor, caso esteja None.
    O valor aplicado será a data de exercício da MovimentacaoPosse.
    """
    instance.servidor.set_data_referencia_ferias(instance.data_exercicio)
    # os novos terão que ter suas configurações de previdência adicionadas manualmente
    # instance.servidor.set_organ_social_security(instance)


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_delete, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoAposentadoria)
@receiver(post_delete, sender=MovimentacaoAposentadoria)
@receiver(post_save, sender=TerminationBenefitMovement)
@receiver(post_delete, sender=TerminationBenefitMovement)
def atualizar_posse_ativo(sender, instance, **kargs):
    FALECIMENTO = 7
    instance.movimentacao_posse.set_data_desligamento()
    if instance.tipo_desligamento == FALECIMENTO:
        instance.servidor.pessoa_fisica.set_data_obito(instance.data_desligamento)
    call_update_vacancy_number_filled_from_chart(instance.movimentacao_posse)
    instance.servidor.update_dates()


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoAposentadoria)
def run_termination_process(sender, instance, **kargs):
    instance.run_termination_process()


@receiver(post_delete, sender=MovimentacaoDesligamento)
def remove_data_obito(sender, instance, **kargs):
    instance.servidor.pessoa_fisica.set_data_obito()


@receiver(m2m_changed, sender=PessoaFisica.necessidades_especiais.through)
def atualiza_cache_necessidade_especial(sender, instance, action, **kargs):
    if isinstance(instance, PessoaFisica) and (
        action == "post_add" or action == "post_remove"
    ):
        instance.atualiza_cache_necessidade_especial()


@receiver(post_save, sender=DeclaracaoAtividade)
def declaration_activity_update_active(sender, instance, **kargs):
    instance.update_active()


@receiver(m2m_changed, sender=PessoaFisica.documento.through)
def validate_document_not_unique(sender, instance, action, **kargs):
    """
    SINAL sem isolamento pois é utilizado para validação de unicidade.
    """
    if action == "pre_add":
        naturalpersons = []
        documents = []
        if isinstance(instance, PessoaFisica):
            naturalpersons.append(instance.pk)
            documents = kargs.get("pk_set")
        else:
            documents.append(instance.pk)
            naturalpersons = kargs.get("pk_set")

        for document in Documento.objects.filter(pk__in=documents):
            document.validate_document_not_unique(naturalpersons)


@receiver(post_save, sender=CargaHoraria)
def update_missing(sender, instance, **kargs):
    Falta.update_missing(instance)


@receiver(post_delete, sender=CargaHoraria)
def fill_workload(sender, instance, **kargs):
    Falta.fill_workload(employee=[instance.servidor.pk])


@receiver(post_save, sender=MovimentacaoReconducao)
def progression_generator(sender, instance, **kargs):
    instance.progression_generator()


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoReconducao)
def update_workload(sender, instance, **kargs):
    CargaHoraria.create_workload_by_possession(instance.servidor)


def update_natural_person_rg_issuer(sender, instance, action=None, **kargs):
    if isinstance(instance, DocsDadosEspecificos) and action == "post_add":
        instance.update_natural_person_cache()


@receiver(post_save, sender=DocsDadosEspecificos)
def update_natural_person_rg_issuer_docs(sender, instance, **kargs):
    update_natural_person_rg_issuer(sender, instance, action="post_add", **kargs)


@receiver(m2m_changed, sender=Documento.dados_especificos.through)
def update_natural_person_rg_issuer_doc(sender, instance, action=None, **kargs):
    update_natural_person_rg_issuer(sender, instance, action=action, **kargs)


# @receiver(post_save, sender=Endereco)
# @receiver(post_save, sender=Telefone)
# @receiver(post_save, sender=PessoaFisica)
# @receiver(post_save, sender=Dependencia)
# @receiver(post_save, sender=Servidor)
# @receiver(post_save, sender=Documento)
# @receiver(post_save, sender=DocsDadosEspecificos)
# def history_employee(sender, instance, **kargs):
#     if isinstance(instance, Servidor):
#         instance = instance.pessoa_fisica
#     if isinstance(instance, Documento):
#         instance = instance.naturalpersons.first()
#     if isinstance(instance, DocsDadosEspecificos):
#         instance = PessoaFisica.objects.filter(
#             pk__in=set(instance.documentos.values_list("naturalpersons", flat=True))
#         ).last()
#     transaction.on_commit(lambda: NaturalPersonHistory.write_history(instance))
