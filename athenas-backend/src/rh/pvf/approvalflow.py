from rh.pvf.const import *
from contrib.utils import getLogger


log = getLogger(__name__)


class ApprovalFlow(object):
    """
    Classe base responsável por realizar o fluxo de aprovação
    """

    @classmethod
    def approval_flow(cls, request):
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS:
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_approver(self, request, server_approver):
        """
        Retorna o aprovador correspondente de cada etapa do fluxo de aprovação
        """
        approver = server_approver.get("approver")
        if approver:
            return request.get_immediate_boss(request.employee)
        else:
            return approver

    def get_step_approver(self, request):
        pass


class ServerApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação de servidor
    """

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        if not request.step_current:
            if not request.book_usufructs and request.request_type in [
                REQUEST_TYPE_SCHEDULE
            ]:
                return SERVER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
            elif request.get_portal_approver(request.employee):
                if not request.get_portal_approver_capacity(request.employee):
                    return SERVER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
                else:
                    return SERVER_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)

            else:
                return SERVER_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)

        else:
            next = SERVER_APPROVAL_FLOWER.get(request.step_current)
            if next is None:
                return SERVER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
            return SERVER_APPROVAL_FLOWER.get(next["next_step"])


class MemberApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação de membros
    """

    @classmethod
    def approval_flow(cls, request, substitutes, indemnified, partial_indemnity):
        has_substitute = request.has_substitute(substitutes)
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS:
            request.status = STS_EFFECTIVE
            return request
        member_approver = obj.get_step_approver(
            request, has_substitute, indemnified, substitutes, partial_indemnity
        )
        request.approver = obj.get_approver(request, member_approver, substitutes)
        request.step_current = member_approver.get("step_current")
        request.status = member_approver.get("status")
        return request

    def get_approver(self, request, member_approver, substitutes):
        """retorna o aprovador correspondente de cada etapa do fluxo de aprovação de membros"""
        approver = member_approver.get("approver")
        if approver:
            return request.get_substitute_approver(substitutes)
        else:
            return approver

    def get_step_approver(
        self, request, has_substitute, indemnified, substitutes, partial_indemnity
    ):
        """retorna qual a próxima etapa do fluxo de aprovação de membros"""
        if request.request_type in [
            REQUEST_TYPE_SCHEDULE,
            REQUEST_TYPE_RETIFICATION,
            REQUEST_TYPE_ABSENCE,
        ]:
            return self.get_step_approver_schedule(
                request, indemnified, substitutes, has_substitute, partial_indemnity
            )
        else:
            return self.get_step_approver_not_schedule(request)

    def get_step_approver_schedule(
        self, request, indemnified, substitutes, has_substitute, partial_indemnity
    ):
        """retorna qual a próxima etapa do fluxo de aprovação de membros para solicitações de usufrutos e afastamentos"""
        if indemnified:
            return self.get_step_approver_indemnified(request)
        elif (
            not request.book_usufructs
            and request.sale_usufructs
            and not indemnified
            and not partial_indemnity
        ):
            return self.get_step_approver_indemnified(request)
        else:
            return self.get_step_approver_not_indemnified(
                request, has_substitute, substitutes, partial_indemnity
            )

    def get_step_approver_not_schedule(self, request):
        """retorna qual a próxima etapa do fluxo de aprovação de membros exceto usufrutos e afastamentos"""
        if not request.step_current:
            if request.request_type not in [REQUEST_TYPE_CANCELLATION]:
                return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
            else:
                if request.usufruct.activity.configuration.sub_type_of_usufruct in [
                    COMP_CLEARANCE_MEMBERS,
                    COMP_VACATION_MEMBERS,
                    SUBSTITUTE_PROMOTER_CONTEST,
                ]:
                    return MEMBER_APPROVAL_FLOWER.get(
                        REQUEST_STEP_CORREGEDORIES_ADVISORY
                    )
                return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)

        elif (
            request.request_type in [REQUEST_TYPE_CANCELLATION]
            and request.step_current == REQUEST_STEP_CORREGEDORATION
        ):
            return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
        else:
            next = MEMBER_APPROVAL_FLOWER.get(request.step_current)
            return MEMBER_APPROVAL_FLOWER.get(next["next_step"])

    def get_step_approver_not_indemnified(
        self, request, has_substitute, substitutes, partial_indemnity
    ):
        """retorna qual a próxima etapa do fluxo de aprovação de membros para solicitações não indenizados ou indenizados parcialmente"""
        if has_substitute and not request.step_current:
            return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        elif not has_substitute and not request.step_current:
            return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_CORREGEDORIES_ADVISORY)
        else:
            if (
                request.step_current == REQUEST_STEP_CORREGEDORATION
                and not partial_indemnity
            ):
                return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
            else:
                if request.status == STS_WAI_SUBS_SCIENCE:
                    if request.get_substitute_approver(substitutes):
                        return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
                    else:
                        next = MEMBER_APPROVAL_FLOWER.get(request.step_current)
                        return MEMBER_APPROVAL_FLOWER.get(next["next_step"])
                elif (
                    request.request_type == REQUEST_TYPE_RETIFICATION
                    and request.step_current == REQUEST_STEP_CORREGEDORATION
                ):
                    return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
                else:
                    next = MEMBER_APPROVAL_FLOWER.get(request.step_current)
                    return MEMBER_APPROVAL_FLOWER.get(next["next_step"])

    def get_step_approver_indemnified(self, request):
        """retorna qual a próxima etapa do fluxo de aprovação de membros para solicitações totalmente indenizadas"""
        if not request.step_current:
            return MEMBER_APPROVAL_FLOWER.get(REQUEST_STEP_PGJ)
        else:
            next = MEMBER_APPROVAL_FLOWER.get(request.step_current)
            return MEMBER_APPROVAL_FLOWER.get(next["next_step"])


class ManagerApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação de membros da administração superior
    """

    @classmethod
    def approval_flow(cls, request, substitutes):
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS:
            request.status = STS_EFFECTIVE
            return request
        manager_approver = obj.get_step_approver(request, substitutes)
        request.approver = obj.get_substitute_approver(
            request, substitutes, manager_approver
        )
        request.step_current = manager_approver.get("step_current")
        request.status = manager_approver.get("status")
        return request

    def get_substitute_approver(self, request, substitutes, manager_approver):
        """Retorna o aprovador conforme o fluxo de aprovação"""
        if substitutes == None or not substitutes["substitutes"]:
            return manager_approver.get("approver")
        else:
            return request.get_substitute_approver(substitutes)

    def get_step_approver(self, request, substitutes):
        """retorna qual a próxima etapa do fluxo de aprovação de membros da administração superior"""
        if not request.step_current:
            if substitutes is not None and substitutes["substitutes"]:
                return MANAGER_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
            return MANAGER_APPROVAL_FLOWER.get(REQUEST_STEP_PGJ)
        elif request.step_current == REQUEST_STEP_APPROVER:
            return MANAGER_APPROVAL_FLOWER.get(REQUEST_STEP_PGJ)
        else:
            if request.request_type in [
                REQUEST_TYPE_SCHEDULE,
                REQUEST_TYPE_RETIFICATION,
                REQUEST_TYPE_ABSENCE,
            ]:

                next = MANAGER_APPROVAL_FLOWER.get(request.step_current)
                return MANAGER_APPROVAL_FLOWER.get(next["next_step"])
            elif request.request_type == REQUEST_TYPE_CANCELLATION:
                if (
                    request.portalcancelschedule.usufruct.activity.configuration.sub_type_of_usufruct
                    in [
                        COMP_CLEARANCE_MEMBERS,
                        COMP_VACATION_MEMBERS,
                        SUBSTITUTE_PROMOTER_CONTEST,
                    ]
                ):
                    next = MANAGER_APPROVAL_FLOWER.get(request.step_current)
                    return MANAGER_APPROVAL_FLOWER.get(next["next_step"])
                else:
                    return MANAGER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
            else:
                return MANAGER_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)


class InternApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação de estagiários
    """

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de estagiários
        """
        if not request.step_current:
            return INTERN_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        else:
            next = INTERN_APPROVAL_FLOWER.get(request.step_current)
            return INTERN_APPROVAL_FLOWER.get(next["next_step"])


class PointSheetApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação do envio do folha ponto
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if (
            request.status == STS_WAI_EFFECTIVENESS
            and action == REQUEST_ACT_EFFECTIVENESS
        ):
            request.status = STS_EFFECTIVE
            request.approver = None
            return request
        if action == REQUEST_ACT_AUTOMATIC_APPROVER:
            request.status = STS_EFFECTIVE
            request.approver = None
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        if not request.step_current:
            return POINT_SHEET_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return POINT_SHEET_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPROVER:
            return POINT_SHEET_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        else:
            next = POINT_SHEET_APPROVAL_FLOWER.get(request.step_current)
            return POINT_SHEET_APPROVAL_FLOWER.get(next["next_step"])


class TeleWorkApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação do envio mensal do teletrabalho
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if request.status == STS_WAI_APPROVER and action == REQUEST_ACT_APPROVER:
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_approver(self, request, server_approver):
        """
        Retorna o aprovador correspondente de cada etapa do fluxo de aprovação de servidores
        """
        approver = server_approver.get("approver")
        if approver:
            from rh.pvf.models import SendingTelework

            tele_approver = SendingTelework.objects.get(
                pk=request.pk
            ).work_plan.aprovador
            if not tele_approver:
                return request.get_immediate_boss(request.employee)
            return tele_approver

        else:
            return approver

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        if not request.step_current:
            return TELE_WORK_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return TELE_WORK_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        else:
            next = TELE_WORK_APPROVAL_FLOWER.get(request.step_current)
            return TELE_WORK_APPROVAL_FLOWER.get(next["next_step"])


class DutyApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação da confirmação de plantão servidores
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if (
            request.status == STS_WAI_EFFECTIVENESS
            and action != REQUEST_ACT_RETURN_APPROVER
        ):
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        if not request.step_current:
            return DUTY_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        if action == REQUEST_ACT_RETURN_APPROVER:
            return DUTY_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        else:
            next = DUTY_APPROVAL_FLOWER.get(request.step_current)
            return DUTY_APPROVAL_FLOWER.get(next["next_step"])


class BloodDonationApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação aprovação de Doação de Sangue
    """

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        return {
            "approver": None,
            "step_current": REQUEST_STEP_DGP,
            "status": STS_WAI_EFFECTIVENESS,
            "next_step": None,
        }


class ProgressionApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação da solicitação de Progressão Vertical
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS and action == REQUEST_ACT_DEFER:
            request.status = STS_EFFECTIVE
            return request
        progression_approver = obj.get_step_approver(request, action)
        request.step_current = progression_approver.get("step_current")
        request.approver = obj.get_approver(request, progression_approver)
        request.status = progression_approver.get("status")
        return request

    def get_approver(self, request, progression_approver):
        from rh.pvf.models import PortalRequestProgression

        """ 
            Retorna o aprovador correspondente de cada etapa do fluxo de aprovação 
        """
        approver = progression_approver.get("approver")
        if approver:
            return None  # Será atribuído aos grupos ASS_JUR e PROG_DG
        else:
            return approver

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação
        """
        if not request.step_current:
            return PROGRESSION_V_APPROVAL_FLOWER.get(REQUEST_STEP_JURIDICAL_ADVISORY_1)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return PROGRESSION_V_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        else:
            next = PROGRESSION_V_APPROVAL_FLOWER.get(request.step_current)
            return PROGRESSION_V_APPROVAL_FLOWER.get(next["next_step"])


class ProgressionHApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação da solicitação de Progressão Horizontal
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS and action == REQUEST_ACT_DEFER:
            request.status = STS_EFFECTIVE
            return request
        progression_approver = obj.get_step_approver(request, action)
        request.step_current = progression_approver.get("step_current")
        request.approver = obj.get_approver(request, progression_approver)
        request.status = progression_approver.get("status")
        return request

    def get_approver(self, request, progression_approver):
        """
        Retorna o aprovador correspondente de cada etapa do fluxo de aprovação
        """
        approver = progression_approver.get("approver")
        if approver:
            return None  # Será atribuído ao grupo GER_DEV
        else:
            return approver

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação
        """
        if not request.step_current:
            return PROGRESSION_H_APPROVAL_FLOWER.get(REQUEST_STEP_GER_DEV)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return PROGRESSION_H_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPROVER:
            return PROGRESSION_H_APPROVAL_FLOWER.get(REQUEST_STEP_GER_DEV)
        else:
            next = PROGRESSION_H_APPROVAL_FLOWER.get(request.step_current)
            return PROGRESSION_H_APPROVAL_FLOWER.get(next["next_step"])


class ExercicioCumulativoApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação da venda de exercicio cumulativo
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()

        if (
            request.status == STS_WAI_EFFECTIVENESS
            and action != REQUEST_ACT_RETURN_APPROVER
        ):
            request.status = STS_EFFECTIVE
            request.approver = None
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo de aprovação de servidores
        """
        if not request.step_current:
            return EXERCISE_CUMULATIVE_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return EXERCISE_CUMULATIVE_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        if action == REQUEST_ACT_RETURN_APPROVER:
            return EXERCISE_CUMULATIVE_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
        else:
            next = EXERCISE_CUMULATIVE_APPROVAL_FLOWER.get(request.step_current)
            return EXERCISE_CUMULATIVE_APPROVAL_FLOWER.get(next["next_step"])


class CancelamentoTeletrabalhoApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de cancelamento de teletrabalho
    """

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo de cancelamento de teletrabalho
        """
        if not request.step_current:
            return CANCELAMENTO_TELETRABALHO_APPROVAL_FLOWER.get(REQUEST_STEP_APPROVER)
        else:
            next = CANCELAMENTO_TELETRABALHO_APPROVAL_FLOWER.get(request.step_current)
            return CANCELAMENTO_TELETRABALHO_APPROVAL_FLOWER.get(next["next_step"])


class RelatorioSemestralTeletrabalhoApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação do relatório semestral do
    Teletrabalho
    """

    @classmethod
    def approval_flow(cls, request):
        request.status = STS_EFFECTIVE
        request.step_current = REQUEST_STEP_APPROVER
        return request


class SolicitacaoCreditoFolgaApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo da solicitacao de crédito de folgas
    """

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo da solicitacao de crédito de folgas
        """
        return SOLICITACAO_CREDITO_FOLGA_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)


class SolicitacaoAuxCrecheDepenIRApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo da solicitacao de auxilio creche e dependente de IR
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if (
            request.status == STS_WAI_EFFECTIVENESS
            and action != REQUEST_ACT_RETURN_APPLICANT
        ):
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo
        """
        if not request.step_current:
            return SOLICITACAO_AUX_CRECHE_DEPEN_IR_FLOWER.get(REQUEST_STEP_DGP)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return SOLICITACAO_AUX_CRECHE_DEPEN_IR_FLOWER.get(REQUEST_STEP_STAND)
        else:
            next = SOLICITACAO_AUX_CRECHE_DEPEN_IR_FLOWER.get(request.step_current)
            return SOLICITACAO_AUX_CRECHE_DEPEN_IR_FLOWER.get(next["next_step"])


class DesbloqueioTeletrabalhoApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de desbloqueio do teletrabalho
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if request.status == STS_WAI_EFFECTIVENESS:
            request.status = STS_EFFECTIVE
            return request
        if action == REQUEST_ACT_DEFER:
            request.status = STS_EFFECTIVE
            request.approver = None
            return request
        server_approver = obj.get_step_approver(request)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo desbloqueio do teletrabalho
        """
        if not request.step_current:
            return DESBLOQUEIO_TELETRABALHO_APPROVAL_FLOWER.get(REQUEST_STEP_GER_DEV)
        else:
            next = DESBLOQUEIO_TELETRABALHO_APPROVAL_FLOWER.get(request.step_current)
            return DESBLOQUEIO_TELETRABALHO_APPROVAL_FLOWER.get(next["next_step"])


class CreditoDispensaEleitoralApprovalFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de crédito de dispensa eleitoral
    """

    @classmethod
    def approval_flow(cls, request, action):
        obj = cls()
        if (
            request.status == STS_WAI_EFFECTIVENESS
            and action != REQUEST_ACT_RETURN_APPLICANT
        ):
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request, action)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request, action):
        """
        Retorna qual a próxima etapa do fluxo crédito de dispensa eleitoral
        """
        if not request.step_current:
            return CREDITO_DISPENSA_ELEITORAL_APPROVAL_FLOWER.get(REQUEST_STEP_DGP)
        if action == REQUEST_ACT_RETURN_APPLICANT:
            return CREDITO_DISPENSA_ELEITORAL_APPROVAL_FLOWER.get(REQUEST_STEP_STAND)
        else:
            next = CREDITO_DISPENSA_ELEITORAL_APPROVAL_FLOWER.get(request.step_current)
            return CREDITO_DISPENSA_ELEITORAL_APPROVAL_FLOWER.get(next["next_step"])


class SolicitacaoVendaPlantaoFlow(ApprovalFlow):
    """
    Classe responsável por realizar o fluxo de aprovação da venda de plantões
    """

    @classmethod
    def approval_flow(cls, request):
        obj = cls()
        if request.status == STS_EFETIVACAO_AUTOMATICA:
            request.status = STS_EFFECTIVE
            return request
        server_approver = obj.get_step_approver(request)
        request.approver = obj.get_approver(request, server_approver)
        request.step_current = server_approver.get("step_current")
        request.status = server_approver.get("status")
        return request

    def get_step_approver(self, request):
        """
        Retorna qual a próxima etapa do fluxo da solicitacao de venda de plantões
        """
        return SOLICITACAO_VENDA_PLANTOES_FLOWER.get(REQUEST_STEP_EFETIVACAO_AUTOMATICA)
