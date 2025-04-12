from rh.pvf.const import *
from rh.pvf.apiv2.utils.approval import approver_button_request, belongs_group_dgp
from rh.pvf.utils.acoes_vdf import get_objeto_acao

from contrib.utils import getLogger


log = getLogger(__name__)


class BaseAcao(object):
    """Classe responsável por retornar as ações da solicitação do vdf"""

    @classmethod
    def retorna_acoes_dgp(cls, grupo_dgp, solicitacao):
        """
        Retorna as ações pertencentes ao grupo DGP
        Params:
        - grupo_dgp (str): informano o grupo DGP.
        - solicitacao (object): objeto da solicitação
        Retorno:
            (list) - Uma lista com as ações do grupo DGP

        """
        if (
            grupo_dgp
            and solicitacao.status
            not in [
                STS_EFFECTIVE,
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
                STS_EFETIVACAO_AUTOMATICA,
            ]
            and solicitacao.request_type
            not in [
                REQUEST_TYPE_PROGRESSION_H,
                REQUEST_TYPE_PROGRESSION_V,
                REQUEST_TYPE_CUMULATIVE_EXERCISE,
                REQUEST_TYPE_DESBLOQUEIO_TELETRABALHO,
            ]
        ):
            return [
                get_objeto_acao(ACTION_CANCEL, ACTION_KEY_CANCEL, desabilitado=False),
                get_objeto_acao(
                    ACTION_ANNOTATION, ACTION_KEY_DGP_OBSERVATION, desabilitado=False
                ),
            ]
        return []

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.step_current == REQUEST_STEP_CORREGEDORIES_ADVISORY:
                return [
                    get_objeto_acao(
                        ACTION_ANNOTATION, ACTION_KEY_ANNOTATION, desabilitado=False
                    )
                ]
            elif solicitacao.status == STS_WAI_SUBS_SCIENCE:
                return [
                    get_objeto_acao(
                        ACTION_CONFIRM_SCIENCE, ACTION_KEY_SCIENCE, desabilitado=False
                    )
                ]
            elif solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(ACTION_DEFER, ACTION_KEY_DEFER, desabilitado=False),
                    get_objeto_acao(ACTION_REJECT, ACTION_KEY_DENY, desabilitado=False),
                ]
            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    )
                ]
        return []

    @classmethod
    def retorna_acoes_solicitacao(cls, solicitacao, servidor):
        acoes = []
        grupo_dgp = belongs_group_dgp(servidor)
        aprovador_solicitacao = approver_button_request(solicitacao, servidor)
        acoes.extend(cls.retorna_acoes_dgp(grupo_dgp, solicitacao))
        acoes.extend(cls.retorna_acoes_aprovador(aprovador_solicitacao, solicitacao))
        return acoes


class AcoesAfastamento(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de afastamento"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.step_current == REQUEST_STEP_APPROVER:
                return [
                    get_objeto_acao(
                        ACTION_CONFIRM_SCIENCE, ACTION_KEY_SCIENCE, desabilitado=False
                    )
                ]
            elif solicitacao.step_current == REQUEST_STEP_CORREGEDORIES_ADVISORY:
                return [
                    get_objeto_acao(
                        ACTION_ANNOTATION, ACTION_KEY_ANNOTATION, desabilitado=False
                    )
                ]
            elif solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(ACTION_DEFER, ACTION_KEY_DEFER, desabilitado=False),
                    get_objeto_acao(ACTION_REJECT, ACTION_KEY_DENY, desabilitado=False),
                ]
            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    )
                ]
        return []


class AcoesTeletrabalho(BaseAcao):
    """Classe responsável por retornar as ações da solicitação do Teletrabalho"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_APPROVER, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesFolhaPonto(BaseAcao):
    """Classe responsável por retornar as ações da solicitação do folha ponto"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_APPROVER, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]

            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_RETURN_APPROVER,
                        ACTION_KEY_RETURN_APPROVER,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesProgressaoH(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de progressão
    Horizontal
    """

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                    get_objeto_acao(ACTION_REJECT, ACTION_KEY_DENY, desabilitado=False),
                ]
        return []


class AcoesProgressaoV(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de progressão
    Vertical
    """

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status != STS_EFFECTIVE:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_APPROVER, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesPlantao(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de Plantão"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(
                        ACTION_CONFIRM_DUTY, ACTION_KEY_DEFER, desabilitado=False
                    ),
                    get_objeto_acao(
                        ACTION_NO_CONFIRM_DUTY, ACTION_KEY_DENY, desabilitado=False
                    ),
                ]

            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPROVER,
                        ACTION_KEY_RETURN_APPROVER,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesExercicioCumulativo(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de Exercicio
    Cumulativo
    """

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(ACTION_DEFER, ACTION_KEY_DEFER, desabilitado=False),
                    get_objeto_acao(
                        ACTION_ANNOTATION,
                        ACTION_KEY_DGP_OBSERVATION,
                        desabilitado=False,
                    ),
                ]
            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                acoes = []
                acoes += [
                    get_objeto_acao(
                        ACTION_RETURN_APPROVER,
                        ACTION_KEY_RETURN_APPROVER,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_ANNOTATION,
                        ACTION_KEY_DGP_OBSERVATION,
                        desabilitado=False,
                    ),
                ]
                if solicitacao.pvfexerciciocumulativo.substituicoes.filter(
                    consolidated=True
                ).exists():
                    acoes.append(
                        get_objeto_acao(
                            ACTION_CONSOLIDATED,
                            ACTION_KEY_CONSOLIDATED,
                            desabilitado=True,
                        )
                    )
                    acoes.append(
                        get_objeto_acao(
                            ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                        )
                    )
                else:
                    acoes.append(
                        get_objeto_acao(
                            ACTION_CONSOLIDATED,
                            ACTION_KEY_CONSOLIDATED,
                            desabilitado=False,
                        )
                    )
                    acoes.append(
                        get_objeto_acao(
                            ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=True
                        )
                    )
                return acoes
        return []


class AcoesSolicitacaoAuxCrecheDepenIR(BaseAcao):
    """Classe responsável por retornar as ações da solicitação do auxilio creche e dependente de IR"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesDesbloqueioTeletrabalho(BaseAcao):
    """Classe responsável por retornar as ações do desbloqueio do teletrabalho"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_APPROVER:
                return [
                    get_objeto_acao(
                        ACTION_SEND_SUB, ACTION_KEY_SEND_SUB, desabilitado=False
                    ),
                    get_objeto_acao(
                        ACTION_ANNOTATION,
                        ACTION_KEY_DGP_OBSERVATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(ACTION_DEFER, ACTION_KEY_DEFER, desabilitado=False),
                ]
            elif solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(ACTION_REJECT, ACTION_KEY_DENY, desabilitado=False),
                    get_objeto_acao(
                        ACTION_ANNOTATION,
                        ACTION_KEY_DGP_OBSERVATION,
                        desabilitado=False,
                    ),
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                ]
        return []


class AcoesCreditoDispensaEleitoral(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de crédito de dispensa eleitoral"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        if aprovador_solicitacao:
            if solicitacao.status == STS_WAI_EFFECTIVENESS:
                return [
                    get_objeto_acao(
                        ACTION_EFFECTIVENESS, ACTION_KEY_DEFER, desabilitado=False
                    ),
                    get_objeto_acao(
                        ACTION_RETURN_APPLICANT,
                        ACTION_KEY_RETURN_APPLICATION,
                        desabilitado=False,
                    ),
                ]
        return []


class AcoesVendaPlantoes(BaseAcao):
    """Classe responsável por retornar as ações da solicitação de venda de plantões"""

    @classmethod
    def retorna_acoes_aprovador(cls, aprovador_solicitacao, solicitacao):
        return []
