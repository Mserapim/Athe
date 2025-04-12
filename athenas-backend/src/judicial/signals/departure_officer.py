# -.- coding: utf-8 -.-
from rh.afastamento.models import (
    BaseLicencaAfastamento,
    FeriasAfastamento,
    Viagem,
    Recesso,
)
from rh.afastamento.models import LicencaSaude3Dias, LicencaSaudeJuntaMedica
from rh.afastamento.models import (
    LicencaDoencaPessoaFamilia,
    LicencaMaternidade,
    LicencaAdocao,
)
from rh.afastamento.models import (
    LicencaAfastamentoConjuge,
    LicencaServicoMilitar,
    LicencaAtividadePolitica,
)
from rh.afastamento.models import (
    LicencaCapacitacao,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
)
from rh.afastamento.models import (
    AfastamentoOutroOrgao,
    AfastamentoMandatoEletivo,
    AfastamentoEstudar,
)
from rh.afastamento.models import (
    AfastamentoMissao,
    AfastamentoEleitoral,
    AfastamentoServirJuri,
)
from rh.afastamento.models import (
    AfastamentoTreinamento,
    AfastamentoDeslocamento,
    AfastamentoCompeticao,
)
from rh.afastamento.models import (
    AfastamentoCursoConcurso,
    AfastamentoPrisao,
    AusenciaDoacaoSangue,
)
from rh.afastamento.models import AfastamentoSuspensao, AfastamentoComparecimentoJuizo
from rh.afastamento.models import (
    AusenciaEleitor,
    AusenciaCasamento,
    AusenciaNascimento,
    AusenciaFalecimento,
)
from rh.afastamento.models import (
    AusenciaConclusao,
    FolgaEleitoral,
    LicencaSaude30Dias,
    AtuacaoGrupoTrabalho,
)
from rh.afastamento.models import (
    DesempenhoFuncao,
    Plantao,
    FolgaCompensacao,
    FolgaAniversario,
)
from rh.const import ACTIVE, FINISHED
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from contrib.utils import getLogger

log = getLogger(__name__)


# @receiver(post_save, sender=FeriasAfastamento)
# @receiver(post_save, sender=Viagem)
# @receiver(post_save, sender=Recesso)
# @receiver(post_save, sender=FolgaEleitoral)
# @receiver(post_save, sender=FolgaAniversario)
# @receiver(post_save, sender=FolgaCompensacao)
# # @receiver(post_save, sender=AtuacaoGrupoTrabalho)
# # @receiver(post_save, sender=DesempenhoFuncao)
# @receiver(post_save, sender=Plantao)
# @receiver(post_save, sender=LicencaSaude3Dias)
# @receiver(post_save, sender=LicencaSaude30Dias)
# @receiver(post_save, sender=LicencaSaudeJuntaMedica)
# @receiver(post_save, sender=LicencaDoencaPessoaFamilia)
# @receiver(post_save, sender=LicencaMaternidade)
# @receiver(post_save, sender=LicencaAdocao)
# @receiver(post_save, sender=LicencaAfastamentoConjuge)
# @receiver(post_save, sender=LicencaServicoMilitar)
# @receiver(post_save, sender=LicencaAtividadePolitica)
# @receiver(post_save, sender=LicencaCapacitacao)
# @receiver(post_save, sender=LicencaInteresseParticular)
# @receiver(post_save, sender=LicencaMandatoClassista)
# @receiver(post_save, sender=AfastamentoOutroOrgao)
# @receiver(post_save, sender=AfastamentoMandatoEletivo)
# @receiver(post_save, sender=AfastamentoEstudar)
# @receiver(post_save, sender=AfastamentoMissao)
# @receiver(post_save, sender=AfastamentoEleitoral)
# @receiver(post_save, sender=AfastamentoServirJuri)
# @receiver(post_save, sender=AfastamentoTreinamento)
# @receiver(post_save, sender=AfastamentoDeslocamento)
# @receiver(post_save, sender=AfastamentoCompeticao)
# @receiver(post_save, sender=AfastamentoCursoConcurso)
# @receiver(post_save, sender=AfastamentoPrisao)
# @receiver(post_save, sender=AfastamentoSuspensao)
# @receiver(post_save, sender=AfastamentoComparecimentoJuizo)
# @receiver(post_save, sender=AusenciaDoacaoSangue)
# @receiver(post_save, sender=AusenciaEleitor)
# @receiver(post_save, sender=AusenciaCasamento)
# @receiver(post_save, sender=AusenciaNascimento)
# @receiver(post_save, sender=AusenciaFalecimento)
# @receiver(post_save, sender=AusenciaConclusao)
# def update_officer_diligence(sender, instance, **kargs):
#     #FIXME: REESCREVER IMPLEMENTAÇÃO DA ATUALIZAÇÃO DO AFASTAMENTO E VOLTAR IMPLEMENTAÇÃO PARA JUDICIAL
#     pass
#     # if hasattr(instance.servidor, 'officerdiligence'):
#     #     status = 1
#     #     if instance.estado == ACTIVE:
#     #         status = 2
#     #     log.debug(instance.get_alteracao_display())
#     #     log.debug(instance.get_estado_display())
#     #     log.debug('status')
#     #     log.debug(status)
#     #     log.debug('instance.servidor.officerdiligence.status')
#     #     log.debug(instance.servidor.officerdiligence.status)
#     #     if instance.servidor.officerdiligence.status != status:
#     #         try:
#     #             with transaction.atomic():
#     #                 instance.servidor.officerdiligence.status = status
#     #                 instance.servidor.officerdiligence.save()
#     #         except Exception as err:
#     #             log.exception(err)
