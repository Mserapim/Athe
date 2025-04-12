# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.pvf.models import PortalRequest
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger
from contrib.decorator import login_required
from django.db.models import Q
from standard.models import Choice
from rh.models import CargaHoraria, ServidorLotacao
from rh.pvf.models import PortalRequestUsufruct
from rh.gfp.models import MovimentacaoProgressao
from rh.pvf.const import *
from rh.dayoff.const import USU_HOMOLOGATED, USU_SOLD, USU_ENJOYING, USU_ENJOYED

log = getLogger(__name__)


class PortalRequestApi(RestfulDRY):

    _model = PortalRequest

    full_text_index = (
        "approver__pessoa_fisica__nome__icontains",
        "approver__matricula__icontains",
        "pk__icontains",
    )

    def get_employee(self):
        return employee_from_user(get_current_user())

    def get_query(self):
        query = super(PortalRequestApi, self).get_query()
        return query.filter(employee=self.get_employee()).exclude(
            request_type__in=[REQUEST_TYPE_SERVER_DUTY, REQUEST_TYPE_PROGRESSION_V]
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            """Ext._create("rh.pvf.portalrequest.Manage", {
                configuration:"%s",
                employee_id:"%s",
                responsible:"%s",
                type_employee:"%s",
                genre:"%s",
                start_date_workload:"%s",
                exercise_one:"%s",
                cancel_status:"%s",
                cancel_usufruct:"%s",
                retification_status:"%s",
                movimentacoes_posse:"%s",
                retification_usufruct:"%s",
                telework_pending:"%s",
                is_workplan:"%s",
                amount_past_days_for_cancel:"%s",
                type_by_possession:"%s",
                employee_schooling:"%s",
                possible_levels:"%s",                
                })"""
            % (
                self.configuration_group(),
                self.get_employee().pk,
                self.get_responsible(),
                self.get_type_employee(),
                self.get_employee().pessoa_fisica.sexo,
                self.get_date_current_workload(self.get_employee()),
                self.get_exercise_one(),
                self.cancel_status(),
                self.cancel_usufruct(),
                self.retification_status(),
                self.get_replaceable_list(self.get_employee()),
                self.retification_usufruct(),
                self.get_telework_pending(),
                self.get_is_workplan(),
                self.get_amount_past_days_for_cancel(),
                self.get_employee().type_by_possession,
                self.get_employee_schooling(),
                self.get_possible_levels(),
            )
        )

    def get_employee_schooling(self):
        progressao = self.get_progression()
        if progressao:
            return progressao.referencia_nivel2d.estrutura_salarial.pk
        else:
            return None

    def get_possible_levels(self):
        progressao = self.get_progression()
        if progressao:
            nivel_atual = progressao.referencia_nivel2d.horizontal
            if nivel_atual == "A":
                niveis = ["B", "C", "D"]
            elif nivel_atual == "B":
                niveis = ["C", "D"]
            elif nivel_atual == "C":
                niveis = ["D"]
            else:
                niveis = []
            return niveis
        else:
            return None

    def get_progression(self):
        servidor = employee_from_user(get_current_user())
        return MovimentacaoProgressao.objects.filter(
            servidor=servidor, ativo=True
        ).first()

    def get_type_employee(self):
        type_by_possession = self.get_employee().type_by_possession
        if type_by_possession in ["EFE", "CMS", "ECM", "EFC"]:
            return "S"
        elif type_by_possession in ["EST", "RES"]:
            return "E"
        elif type_by_possession in ["MBR", "MEL", "MEC"]:
            return "M"
        return self.get_employee().tipo

    def get_replaceable_list(self, employee):
        """
        Função que retorna lista contendo pk's de ServidorLotacao, filtrando as locais opcionais, se o cargo é substituível e se são designações.
        """

        choices = Choice.objects.filter(
            name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
        ).values_list("label")

        lotacoes_exclude_id = (
            ServidorLotacao.objects.filter(
                servidor=employee,
                ativo=True,
                designacao=True,
                movimentacao_posse__quadro__cargo__configs__replaceable=True,
            )
            .exclude(lotacao__pk__in=[int(x[0]) for x in choices])
            .values_list("pk")
        )
        return [x[0] for x in lotacoes_exclude_id]

    def get_date_current_workload(self, employee):
        workload = (
            CargaHoraria.objects.filter(servidor=employee)
            .order_by("-data_inicio")
            .first()
        )
        if workload:
            return workload.data_inicio
        else:
            return 0

    def configuration_group(self):
        """Retorna as configurações dos períodos aquisitivo disponíveis"""
        return PortalRequestUsufruct.configuration_group()

    def get_amount_past_days_for_cancel(self):
        amount_past_days = 0
        try:
            amount_past_days = Choice.objects.get(
                name="VDF_AMOUNT_PAST_DAYS_FOR_CANCEL_AND_RETIFICATION", active=True
            ).value
        except Exception as err:
            log.error(err)
        return amount_past_days

    def get_responsible(self):
        """Verifica se o servidor possui cargo de substituível"""

        exercise = None
        if self.get_employee().tipo == "M":
            choices = Choice.objects.filter(
                name="VDF_OPTIONAL_SUBSTITUTE_LOCAL", active=True
            ).values_list("label")

            exercise = ServidorLotacao.objects.filter(
                servidor=self.get_employee(),
                ativo=True,
                designacao=True,
                responsible=True,
                owner=True,
            ).exclude(lotacao__pk__in=[int(x[0]) for x in choices])
        else:
            exercise = ServidorLotacao.objects.filter(
                ativo=True,
                designacao=True,
                servidor=self.get_employee(),
                movimentacao_posse__quadro__cargo__chefia=True,
            )

        if exercise:
            return True
        else:
            return False

    def get_exercise_one(self):
        """Retorna o exercício do servidor caso possua somente uma designação"""
        exercise = None
        if self.get_employee().tipo == "M":
            exercise = ServidorLotacao.objects.filter(
                ativo=True,
                designacao=True,
                servidor=self.get_employee(),
                responsible=True,
                owner=True,
            )
        else:
            exercise = ServidorLotacao.objects.filter(
                ativo=True,
                designacao=True,
                servidor=self.get_employee(),
                movimentacao_posse__quadro__cargo__chefia=True,
            )

        if exercise:
            if len(exercise) == 1:
                return exercise.first().pk
            else:
                return ""
        else:
            return ""

    def cancel_status(self):
        """Retorna o status do usufruto que poderá ser cancelado pela solicitação"""
        return [USU_HOMOLOGATED, USU_SOLD, USU_ENJOYING, USU_ENJOYED]

    def retification_status(self):
        """Retorna o status do usufruto que poderá ser retificado pela solicitação"""
        return [USU_HOMOLOGATED, USU_SOLD]

    def retification_usufruct(self):
        """Retorna o tipo de usufrutos poderãos ser retificados."""
        return [REGULAR_VACATIONS, INDIVIDUAL_VACATION]

    def cancel_usufruct(self):
        """Retorna o tipo de usufrutos poderão ser cancelados."""
        try:
            list_exclude_usufruct = Choice.objects.filter(
                name="PVF_SUB_CONFIGURATION_EXCLUDE_CANCEL_USUFRUCT", active=True
            ).values_list("value")
            list_of_cancelable_usufructs = (
                Choice.objects.filter(name="SUB_CONFIGURATION_CHOICE", active=True)
                .exclude(value__in=[x[0] for x in list_exclude_usufruct])
                .values_list("value")
            )
            return [x[0] for x in list_of_cancelable_usufructs]
        except Exception as e:
            log.error(e)

    def get_telework_pending(self):
        return PortalRequest.telework_pending()

    def get_is_workplan(self):
        return PortalRequest.is_workplan()

    def model_to_dict(self, instance):
        _dict_ = super(PortalRequestApi, self).model_to_dict(instance)
        _dict_.update(
            type_of_request=instance.type_of_request,
            type_of_usufruct_id=instance.type_of_usufruct_id,
            acquisitive_period=instance.acquisitive_period,
            # acquisitive_period_id=instance.acquisitive_period_id,
            custom_approver_current=instance.set_custom_approver,
            # check_status_update = instance.check_status_update,
            # date_work_load = instance.start_date_workload,
            # new_workload = instance.new_workload,
            # to_workload = instance.new_workload_display,
            # old_workload = instance.current_workload_display,
            # usufruct_cancel = instance.get_usufruct_cancel_id,
            effective_or_canceled=instance.request_effective_or_canceled,
            has_substitute=instance.have_substitute,
            # usufructs_retification = instance.get_usufructs_retification_ids,
            # path_datail_window=instance.path_detail_window,
            start_date_absence=instance.start_date_absence,
            end_date_absence=instance.end_date_absence,
            # days_absence = instance.days_absence,
            # get_medical_certificate = instance.get_medical_certificate,
            # get_blood_donation_comprovation = instance.get_blood_donation_comprovation,
            # dependent_family = instance.get_dependent_family,
            degree_kinship=instance.get_degree_kinship,
            # curse=instance.get_curse,
            # institution = instance.get_institution,
            # political_party= instance.get_political_party,
            # elective_office=instance.get_elective_office,
            # location = instance.get_location,
            dependent=instance.get_dependent,
            # birth_certificate = instance.get_birth_certificate,
            # is_childcare_assistence=instance.get_is_childcare_assistence,
            # is_incoming_tax=instance.get_is_incoming_tax,
            dependent_type=instance.get_dependent_type,
            # is_awaiting_completion= instance.is_awaiting_completion,
            # is_awaiting_completion_prog_h = instance.is_awaiting_completion_prog_h,
            # death_certificate= instance.get_death_certificate,
            family_bond=instance.get_family_bond,
            person=instance.get_person,
            # marriage_certificate=instance.get_marriage_certificate,
            # person_partner=instance.get_person_partner,
            parcel_number=instance.get_parcel_number,
            # is_request_substitute = instance.is_request_substitute,
            reference_month=instance.get_reference_month,
            reference_year=instance.get_reference_year,
            current_work_plan_start_date=instance.get_current_work_plan_start_date,
            current_work_plan_end_date=instance.get_current_work_plan_end_date,
            plan_work_id=instance.get_plan_work_id,
            # plan_work_presential=instance.get_plan_work_presential,
            daily_workload=instance.daily_workload,
            # duty_id = instance.get_duty_id,
            solicitation=True,
            # progression=instance.get_progression_h_id,
            # config=instance.get_config_h_id,
            # publication=instance.get_publication_h_id,
            employee_schooling=self.get_employee_schooling(),
            possible_levels=self.get_possible_levels(),
            # hours=instance.get_hours,
            # cid=instance.get_cid_code,
        )

        return _dict_

    @login_required("JSON")
    def cancel(self, args=[]):
        """Cancelar uma Solicitação"""
        rst = {"message": "nada foi feito ainda.", "success": False}

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para cancelar %s."
                    % self.Model._meta.object_name
                )
            else:
                request = self._model.objects.get(pk=self.request.POST.get("pk"))
                request.cancel(status=STS_CANCELED_APPLICANT)
                # if  hasattr(request,'sendingtimesheet'):
                #     request.sendingtimesheet.pvf_request_justification.update(cancelado=True)

                rst.update(success=True, message="Procedimento realizado com sucesso.")
        except Exception as e:
            rst.update(message="{}".format(e))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PortalwaitingApproval(RestfulDRY):

    _model = PortalRequest

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
        "pk__icontains",
    )

    def get_employee(self):
        return employee_from_user(get_current_user())

    def get_query(self):
        query = super().get_query()
        belongs_group = self.belongs_group()

        if (
            GROUP_SERVER in belongs_group
            or GROUP_MEMBER in belongs_group
            or GROUP_AUDIT in belongs_group
        ):
            return query.distinct()
        elif GROUP_ASS_COGER in belongs_group or GROUP_COGER in belongs_group:
            return query.filter(
                Q(approver__pk=self.get_employee().pk)
                | Q(portal_request_substitute__substitute__pk=self.get_employee().pk)
                | Q(
                    step_current__in=[
                        REQUEST_STEP_CORREGEDORIES_ADVISORY,
                        REQUEST_STEP_CORREGEDORATION,
                        REQUEST_STEP_PGJ,
                    ]
                )
                | Q(status__in=[STS_WAI_SUBS_SCIENCE])
                | Q(portalrequesthistory__group__in=list(self.get_employee_approver()))
                | Q(portalrequesthistory__user=get_current_user())
                & Q(
                    portalrequesthistory__action__in=[
                        REQUEST_ACT_DEFER,
                        REQUEST_ACT_INDEFER,
                        REQUEST_ACT_SCIENCE,
                        REQUEST_ACT_ANNOTATION,
                        REQUEST_ACT_EFFECTIVENESS,
                    ]
                )
            ).distinct()
        else:
            return query.filter(
                Q(approver__pk=self.get_employee().pk)
                | Q(portal_request_substitute__substitute__pk=self.get_employee().pk)
                | Q(step_current__in=self.group_list())
                | Q(portalrequesthistory__group__in=list(self.get_employee_approver()))
                | Q(portalrequesthistory__user=get_current_user())
                & Q(
                    portalrequesthistory__action__in=[
                        REQUEST_ACT_DEFER,
                        REQUEST_ACT_INDEFER,
                        REQUEST_ACT_SCIENCE,
                        REQUEST_ACT_ANNOTATION,
                        REQUEST_ACT_EFFECTIVENESS,
                    ]
                )
            ).distinct()

    def get_employee_approver(self):
        """Retorna o(s) grupo(s) em que o servidor está vinculado"""
        employee = self.get_employee()
        groups = {}
        for group in employee.user.groups.all():
            groups[group.name] = group.name

        return groups

    def group_list(self):
        """Retorna uma lista dos steps relacionados aos grupos de aprovação VDF"""
        groups = self.get_employee_approver()
        groups_list = []
        for group in groups:
            groups_list.append(REQUEST_STEP_GROUP.get(group, 0))

        return groups_list

    def setPrefilterEmployee(self):
        groups = self.get_employee_approver()
        if GROUPS_PVF["GM"] in groups:
            return "M"
        elif GROUPS_PVF["GS"] in groups:
            return "S"
        elif GROUPS_PVF["COGER"] in groups:
            return "M"
        elif GROUPS_PVF["ASS_COGER"] in groups:
            return "M"
        else:
            return "All"

    def setPrefilterStatus(self):
        groups = self.get_employee_approver()
        status = []
        for step in groups:
            status = status + REQUEST_STATUS_GROUP.get(step, [])

        status = list(set(status))
        return status

    def group_list_all(self):
        """Retorna uma lista de todos eteps VDF"""
        groups_list = []
        for group in REQUEST_STEP:
            groups_list.append(REQUEST_STEP.get(group, 0))

        return groups_list

    def belongs_group(self):
        """Verifica se o servidor pertence ao determinado grupo de acesso geral"""
        groups = self.get_employee_approver()
        belongs = []
        groups_filters = [
            GROUPS_PVF["GS"],
            GROUPS_PVF["GM"],
            GROUPS_PVF["COGER"],
            GROUPS_PVF["ASS_COGER"],
            GROUPS_PVF["AUDIT"],
        ]
        for group in groups:
            if group in groups_filters:
                belongs.append(group)
        return belongs

    def belongs_group_dgp(self):
        """Verifica se o servidor pertence ao grupo Gerência de Membros ou Servidores"""
        groups = self.belongs_group()
        if GROUPS_PVF["GM"] in groups:
            return GROUPS_PVF["GM"]
        if GROUPS_PVF["GS"] in groups:
            return GROUPS_PVF["GS"]
        return ""

    def belongs_group_progression(self):
        """Verifica se o servidor pertence ao grupo Aprovação de Solicitação de Progressão"""
        groups = self.get_employee_approver()
        if GROUPS_PVF["ASS_JUR_1"] in groups:
            return GROUPS_PVF["ASS_JUR_1"]
        if GROUPS_PVF["PROG_DG"] in groups:
            return GROUPS_PVF["PROG_DG"]
        if GROUPS_PVF["ASS_JUR_2"] in groups:
            return GROUPS_PVF["ASS_JUR_2"]
        return ""

    def get_status_hidden(self):
        """Retorna os steps ao qual não será permitido deferir, indeferir e efetivar"""
        status_hidden = [
            STS_EFFECTIVE,
            STS_REJECTED,
            STS_CANCELED_DGP,
            STS_CANCELED_APPLICANT,
        ]
        return status_hidden

    def approver_button_request(self, instance):
        """Retorna se o servidor é aprovador do step atual"""
        if (
            instance.step_current in self.group_list()
            or instance.approver == self.get_employee()
            or self.get_employee().pk in self.get_substitutes_approver(instance)
        ):
            return True
        else:
            return False

    def has_substitute(self, instance):
        substitute = self._model.objects.filter(
            Q(pk=instance.pk)
            & Q(status=STS_WAI_SUBS_SCIENCE)
            & Q(portal_request_substitute__substitute=self.get_employee())
        )
        if substitute:
            return True
        else:
            return False

    def get_substitutes_approver(self, instance):
        """Retorna lista com os 'pks' dos servidores 'substitutos'"""

        if not self.has_substitute:
            return []
        science_ids = instance.portalrequesthistory_set.filter(
            action=REQUEST_ACT_SCIENCE
        ).values_list("user__servidor__pk", flat=True)
        science_ids = list(science_ids)

        pr_substitute = instance.portal_request_substitute.exclude(
            substitute__pk__in=set(science_ids)
        )
        if pr_substitute:
            return list(pr_substitute.values_list("substitute__pk", flat=True))
        else:
            return []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            """Ext._create("rh.pvf.waitingapproval.Manage", {
                employee_id: "%s",
                groups: "%s",
                group_all:"%s",
                group_dgp:"%s",
                filter_employee:"%s",
                filter_status:"%s",
                type_employee:"%s",
                status_hidden:"%s",
                group_progression:"%s"})"""
            % (
                self.get_employee().pk,
                self.group_list(),
                self.group_list_all(),
                self.belongs_group_dgp(),
                self.setPrefilterEmployee(),
                self.setPrefilterStatus(),
                self.get_employee().tipo,
                self.get_status_hidden(),
                self.belongs_group_progression(),
            )
        )

    def model_to_dict(self, instance):
        _dict_ = super(PortalwaitingApproval, self).model_to_dict(instance)
        _dict_.update(
            days_awaiting_approval=instance.days_awaiting_approval,
            type_of_request=instance.type_of_request,
            acquisitive_period=instance.acquisitive_period,
            type_of_usufruct_id=instance.type_of_usufruct_id,
            custom_approver_current=instance.set_custom_approver,
            approver_request=self.approver_button_request(instance),
            # date_work_load = instance.start_date_workload,
            # to_workload = instance.new_workload_display,
            # old_workload = instance.current_workload_display,
            # buttons=instance.buttons_approver,
            # usufruct_cancel = instance.get_usufruct_cancel_id,
            has_substitute=instance.have_substitute,
            # usufructs_retification = instance.get_usufructs_retification_ids,
            # path_datail_window=instance.path_detail_window,
            start_date_absence=instance.start_date_absence,
            end_date_absence=instance.end_date_absence,
            # days_absence = instance.days_absence,
            # get_medical_certificate = instance.get_medical_certificate,
            # dependent_family = instance.get_dependent_family,
            degree_kinship=instance.get_degree_kinship,
            # curse=instance.get_curse,
            # institution = instance.get_institution,
            # political_party= instance.get_political_party,
            # elective_office=instance.get_elective_office,
            # location = instance.get_location,
            dependent=instance.get_dependent,
            # birth_certificate = instance.get_birth_certificate,
            # is_childcare_assistence=instance.get_is_childcare_assistence,
            # is_incoming_tax=instance.get_is_incoming_tax,
            dependent_type=instance.get_dependent_type,
            # is_awaiting_completion= instance.is_awaiting_completion,
            # is_awaiting_completion_prog_h = instance.is_awaiting_completion_prog_h,
            # death_certificate= instance.get_death_certificate,
            # family_bond=instance.get_family_bond,
            person=instance.get_person,
            # marriage_certificate=instance.get_marriage_certificate,
            # get_blood_donation_comprovation = instance.get_blood_donation_comprovation,
            # person_partner=instance.get_person_partner,
            parcel_number=instance.get_parcel_number,
            # is_request_substitute = instance.is_request_substitute,
            reference_month=instance.get_reference_month,
            reference_year=instance.get_reference_year,
            current_work_plan_start_date=instance.get_current_work_plan_start_date,
            current_work_plan_end_date=instance.get_current_work_plan_end_date,
            plan_work_id=instance.get_plan_work_id,
            # plan_work_presential=instance.get_plan_work_presential,
            # duty_id = instance.get_duty_id,
            solicitation=False,
            # progression=instance.get_progression_h_id,
            # config=instance.get_config_h_id,
            # publication=instance.get_publication_h_id,
            # hours=instance.get_hours,
            # cid=instance.get_cid_code,
        )

        return _dict_

    @login_required("JSON")
    def authorize_request(self, args=[]):
        """Realiza as operações do fluxo de aprovação (deferir, indeferir, efetivar, cancelar, ciência e anotar)"""
        rst = {"message": "nada foi feito ainda.", "success": False}

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para deferir/indeferir %s."
                    % self.Model._meta.object_name
                )
            else:
                value = self.request.POST.get("action")
                request = self._model.objects.get(pk=int(self.request.POST.get("pk")))
                publication = self.request.POST.get("publication")
                observation = self.request.POST.get("observation")
                if value == "defer":
                    request.defered(observation, publication)

                elif value == "deny":
                    request.denyed(observation)

                elif value == "science":
                    request.science(observation, user=get_current_user())

                elif value == "annotation":
                    request.annoted(observation)

                elif value == "dgp_observation":
                    request.dgp_annoted_observation(observation)

                elif value == "return_applicant":
                    request.return_applicant(observation)

                elif value == "return_approver":
                    request.return_approver(observation)

                elif value == "cancel":
                    request.cancel(
                        observation=observation, status=STS_CANCELED_DGP, validate=False
                    )
                    if request.sendingtimesheet:
                        request.sendingtimesheet.pvf_request_justification.update(
                            cancelado=True
                        )

                rst.update(success=True, message="Procedimento realizado com sucesso.")

        except Exception as e:
            rst.update(message="{}".format(e))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
