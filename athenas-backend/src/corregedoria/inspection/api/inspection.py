# -*- coding: utf-8 -*-
import json
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user, person_from_user
from contrib.middleware import get_current_user
from standard.models import Configuration
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.template import loader, Context
from datetime import datetime
from decimal import Decimal, ROUND_UP
from corregedoria.inspection.models import (
    Inspection,
    ExecutionOrganManagement,
    PublicAttendance,
    OutCourtLawsuitControl,
    CourtLawsuitControl,
    CourtLawsuitCount,
    OutCourtLawsuitElectoralCount,
    OutCourtLawsuitCount,
    AnalysisPerformanceInAudiences,
    AnalysisPerformanceInPlenarySessionOfTheJury,
    StructureDeficiency,
    RegisteredPublicAttendanceNumber,
    QualitativeAnalysisOfThePartsCivilCourtLawsuit,
    QualitativeAnalysisOfThePartsCriminalCourtLawsuit,
    QualitativeAnalysisOfThePartsOutCourtLawsuit,
    QualitativeAnalysisOfThePartsElectoral,
    PromptnessCourtLawsuit,
    PromptnessOutCourtLawsuit,
    PromptnessUpperManagement,
    HarmedCalculation,
    GeneralObservations,
    Sign,
    ProceduralMovement,
    MemberOrgan,
    OperatingStructure,
    StructureEquipment,
    StructureGeneralStatus,
    AdministrativeOrganizationOperatingHours,
    AdministrativeOrganizationAttendanceHours,
    AdministrativeOrganizationRegistrationSystem,
    AdministrativeOrganizationProceduresInProgress,
    AdministrativeOrganizationArchivedProcedures,
    AdministrativeOrganizationGeneralStatus,
    Performance,
)
from corregedoria.models import ConfigScoreTable, BandScoreTable
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
from rh.models import Lotacao
from judicial.models import ExecutionOrgan

log = getLogger(__name__)


class INSPECTIONInspection(RestfulDRY):
    _model = Inspection
    force_upper = False

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "execution_organ__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("corregedoria.inspection.inspection.Manage")')

    def get_query(self):
        query = super(INSPECTIONInspection, self).get_query()
        return query.distinct()

    def do_filter(self, query, force_filter=None):
        """Aplica o filtro na query.

        :param query: QuerySet a ser aplicada um filtro.

        :returns: QuerySet com filtro aplicado.

        Parâmetros do Request.Method
        filter deve ser uma lista de dicionários com as seguintes chaves
        filter=[{'stage':____,'property':____,'value':____},{...}]
        stage deve ser um inteiro, zero ou positivo para utilizar filter, ou negativo para utilizar exclude
        dicionários com stage iguais serão tratados com "OR",
        dicionários com stage diferentes serão tratados com "AND"
        """

        def fn(f):
            return {f.get("property"): self._filter_eval_value(f.get("value"))}

        try:
            flist = None
            if not force_filter:
                flist = json.loads(self.get_params().get("filter", "[]"))
            else:
                flist = force_filter
        except KeyError as e:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % e
            )
        except Exception as e:
            log.exception(e)
            raise (e)
        else:
            # log.debug(flist)
            stages = {}
            for f in flist:
                stage = int(f.get("stage", 0) or 0)
                stage_list = stages.get(stage, [])
                stage_list.append(f)
                stages.update({stage: stage_list})

            query_Q = Q()

            for key in sorted(stages.keys()):
                stage_list = stages.get(key)
                fquery = None

                for part in stage_list:
                    fquery = Q(fquery | Q(**fn(part))) if fquery else Q(**fn(part))

                if fquery is not None:
                    if key >= 0:
                        query_Q.add(fquery, fquery.connector)
                    else:
                        query_Q.add(~fquery, fquery.connector)

        return query.filter(query_Q)

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONInspection, self).model_to_dict(instance)
        atual_employee = employee_from_user(get_current_user())
        prosecutor = instance.inspector_prosecutors.filter(pk=atual_employee.pk).first()
        _dict_.update(
            {
                "icons": instance.icons,
                "inspection_date_initial_formatted": instance.inspection_date_initial_formatted,
                "inspection_date_final_formatted": instance.inspection_date_final_formatted,
                "electoral_applicable_bool": (
                    False
                    if instance.electoral_applicable == 2
                    else (True if instance.electoral_applicable == 1 else None)
                ),
                "final_score": str(instance.final_score),
                "inspector_general_bool": instance.inspector_general == atual_employee,
                "inspector_prosecutor_bool": instance.inspector_prosecutors.filter(
                    pk=atual_employee.pk
                ).exists(),
                "inspector_prosecutor_unicode": str(prosecutor),
                "inspector_prosecutor_pk": prosecutor.pk if prosecutor else None,
                "execution_organ_instance": (
                    instance.execution_organ.instancia.pk
                    if instance.execution_organ.instancia
                    else None
                ),
                "execution_organ_slugify": slugify(instance.execution_organ),
                "structuregeneralstatus": (
                    instance.structuregeneralstatus.status
                    if StructureGeneralStatus.objects.filter(
                        inspection__pk=instance.pk
                    ).exists()
                    else 0
                ),
                "administrativeorganizationgeneralstatus": (
                    instance.administrativeorganizationgeneralstatus.status
                    if AdministrativeOrganizationGeneralStatus.objects.filter(
                        inspection__pk=instance.pk
                    ).exists()
                    else 0
                ),
                "registration_type": (
                    instance.administrativeorganizationregistrationsystem.registration_type
                    if AdministrativeOrganizationRegistrationSystem.objects.filter(
                        inspection__pk=instance.pk
                    ).exists()
                    else 0
                ),
                "atual_employee": atual_employee.pk,
            }
        )
        return _dict_

    def get_employee(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            execution_organ_id = (
                int(params.get("execution_organ"))
                if params.get("execution_organ") != ""
                else 0
            )
            execution_organ = Lotacao.objects.filter(pk=execution_organ_id).first()
            if execution_organ:
                if execution_organ.responsavel:
                    ret = execution_organ.responsavel.pk
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                employee=(
                    execution_organ.responsavel.pk
                    if execution_organ.responsavel
                    else ""
                ),
            )
        self.renderer(rst)

    def get_holder_employee(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            execution_organ_id = (
                int(params.get("execution_organ"))
                if params.get("execution_organ") != ""
                else 0
            )
            execution_organ = Lotacao.objects.filter(pk=execution_organ_id).first()
            if execution_organ:
                if execution_organ.owner:
                    ret = execution_organ.owner.first().pk
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                holder_employee=ret if execution_organ else "",
            )
        self.renderer(rst)

    def get_area_of_action(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            execution_organ_id = (
                int(params.get("execution_organ"))
                if params.get("execution_organ") != ""
                else 0
            )
            execution_organ = ExecutionOrgan.objects.filter(
                pk=execution_organ_id
            ).first()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                area_of_action=(
                    execution_organ.occupation_area if execution_organ else ""
                ),
            )
        self.renderer(rst)

    def get_assignment(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            execution_organ_id = (
                int(params.get("execution_organ"))
                if params.get("execution_organ") != ""
                else 0
            )
            execution_organ = ExecutionOrgan.objects.filter(
                pk=execution_organ_id
            ).first()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="sucesso",
                assignment=execution_organ.attribution if execution_organ else "",
            )
        self.renderer(rst)

    def int2bool(self, b):
        boolean = None
        if b == 1:
            boolean = None
        else:
            if b == "2":
                boolean = True
            else:
                if b == "3":
                    boolean = False
        return boolean

    def bool2int(self, b):
        integer = None
        if b is None:
            integer = 1
        else:
            if b is True:
                integer = 2
            else:
                if b is False:
                    integer = 3
        return integer

    def getRegularityOfService(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "eom_organization": (
                            inspection.executionorganmanagement.organization
                            if ExecutionOrganManagement.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "eom_observation": (
                            inspection.executionorganmanagement.observation
                            if ExecutionOrganManagement.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_record_type": (
                            inspection.publicattendance.record_type
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_apps": (
                            inspection.publicattendance.apps
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_others": (
                            inspection.publicattendance.others
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_opening_date": (
                            (
                                None
                                if inspection.publicattendance.opening_date is None
                                else inspection.publicattendance.opening_date.strftime(
                                    "%d/%m/%Y"
                                )
                            )
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_has_openind_term": (
                            self.bool2int(inspection.publicattendance.has_openind_term)
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_has_numeration": (
                            self.bool2int(inspection.publicattendance.has_numeration)
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_has_signed_sheets": (
                            self.bool2int(inspection.publicattendance.has_signed_sheets)
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_ordered": (
                            self.bool2int(inspection.publicattendance.ordered)
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "pa_observation": (
                            inspection.publicattendance.observation
                            if PublicAttendance.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_record_type": (
                            inspection.outcourtlawsuitcontrol.record_type
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_apps": (
                            inspection.outcourtlawsuitcontrol.apps
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_others": (
                            inspection.outcourtlawsuitcontrol.others
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_opening_date": (
                            (
                                None
                                if inspection.outcourtlawsuitcontrol.opening_date
                                is None
                                else inspection.outcourtlawsuitcontrol.opening_date.strftime(
                                    "%d/%m/%Y"
                                )
                            )
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_has_openind_term": (
                            self.bool2int(
                                inspection.outcourtlawsuitcontrol.has_openind_term
                            )
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_has_numeration": (
                            self.bool2int(
                                inspection.outcourtlawsuitcontrol.has_numeration
                            )
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_has_signed_sheets": (
                            self.bool2int(
                                inspection.outcourtlawsuitcontrol.has_signed_sheets
                            )
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_ordered": (
                            self.bool2int(inspection.outcourtlawsuitcontrol.ordered)
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsc_observation": (
                            inspection.outcourtlawsuitcontrol.observation
                            if OutCourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_record_type": (
                            inspection.courtlawsuitcontrol.record_type
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_apps": (
                            inspection.courtlawsuitcontrol.apps
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_others": (
                            inspection.courtlawsuitcontrol.others
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_opening_date": (
                            (
                                None
                                if inspection.courtlawsuitcontrol.opening_date is None
                                else inspection.courtlawsuitcontrol.opening_date.strftime(
                                    "%d/%m/%Y"
                                )
                            )
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_has_openind_term": (
                            self.bool2int(
                                inspection.courtlawsuitcontrol.has_openind_term
                            )
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_has_numeration": (
                            self.bool2int(inspection.courtlawsuitcontrol.has_numeration)
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_has_signed_sheets": (
                            self.bool2int(
                                inspection.courtlawsuitcontrol.has_signed_sheets
                            )
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_ordered": (
                            self.bool2int(inspection.courtlawsuitcontrol.ordered)
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsc_observation": (
                            inspection.courtlawsuitcontrol.observation
                            if CourtLawsuitControl.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_number_of_processes_pending_citation_urgent": (
                            inspection.courtlawsuitcount.number_of_processes_pending_citation_urgent
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_number_of_processes_pending_citation": (
                            inspection.courtlawsuitcount.number_of_processes_pending_citation
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_number_of_processes_pending_science": (
                            inspection.courtlawsuitcount.number_of_processes_pending_science
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_processes_with_open_deadline": (
                            inspection.courtlawsuitcount.processes_with_open_deadline
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_expired_deadline_the_last_30_days": (
                            inspection.courtlawsuitcount.expired_deadline_the_last_30_days
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_expired_deadline_more_than_30_days_ago": (
                            inspection.courtlawsuitcount.expired_deadline_more_than_30_days_ago
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_expired_deadline_in_the_period_of_inspection": (
                            inspection.courtlawsuitcount.expired_deadline_in_the_period_of_inspection
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "clsct_observation": (
                            inspection.courtlawsuitcount.observation
                            if CourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsect_number_of_procedures_in_progress": (
                            inspection.outcourtlawsuitelectoralcount.number_of_procedures_in_progress
                            if OutCourtLawsuitElectoralCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsect_number_of_procedures_in_arrears": (
                            inspection.outcourtlawsuitelectoralcount.number_of_procedures_in_arrears
                            if OutCourtLawsuitElectoralCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsect_correctly_registered_procedures": (
                            self.bool2int(
                                inspection.outcourtlawsuitelectoralcount.correctly_registered_procedures
                            )
                            if OutCourtLawsuitElectoralCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsect_observation": (
                            inspection.outcourtlawsuitelectoralcount.observation
                            if OutCourtLawsuitElectoralCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_procedures_in_progress": (
                            inspection.outcourtlawsuitcount.number_of_procedures_in_progress
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_procedures_in_arrears": (
                            inspection.outcourtlawsuitcount.number_of_procedures_in_arrears
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_correctly_registered_procedures": (
                            self.bool2int(
                                inspection.outcourtlawsuitcount.correctly_registered_procedures
                            )
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_public_civil_actions_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_public_civil_actions_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_acp_administrative_dishonesty": (
                            inspection.outcourtlawsuitcount.number_of_acp_administrative_dishonesty
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_recommendations_issued_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_recommendations_issued_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_conduct_adjustment_terms_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_conduct_adjustment_terms_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_public_audiences_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_public_audiences_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_procedures_instituted_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_procedures_instituted_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_number_of_procedures_archived_in_the_last_year": (
                            inspection.outcourtlawsuitcount.number_of_procedures_archived_in_the_last_year
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "oclsct_observation": (
                            inspection.outcourtlawsuitcount.observation
                            if OutCourtLawsuitCount.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "apia_processes_analyzed_in_the_previous_inspection": (
                            self.bool2int(
                                inspection.analysisperformanceinaudiences.processes_analyzed_in_the_previous_inspection
                            )
                            if AnalysisPerformanceInAudiences.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "apia_survey_in_randomly_chosen_processes": (
                            self.bool2int(
                                inspection.analysisperformanceinaudiences.survey_in_randomly_chosen_processes
                            )
                            if AnalysisPerformanceInAudiences.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "apia_observation": (
                            inspection.analysisperformanceinaudiences.observation
                            if AnalysisPerformanceInAudiences.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "apijts_analysis": (
                            inspection.analysisperformanceinplenarysessionofthejury.analysis
                            if AnalysisPerformanceInPlenarySessionOfTheJury.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getStructure(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "est_deficiency": (
                            inspection.structuredeficiency.deficiency
                            if StructureDeficiency.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getPromptnessScore(self, inspection=None):
        pcl = Decimal(
            inspection.promptnesscourtlawsuit.score
            if PromptnessCourtLawsuit.objects.filter(inspection=inspection).exists()
            else 0
        )
        pocl = Decimal(
            inspection.promptnessoutcourtlawsuit.score
            if PromptnessOutCourtLawsuit.objects.filter(inspection=inspection).exists()
            else 0
        )
        pum = Decimal(
            inspection.promptnessuppermanagement.score
            if PromptnessUpperManagement.objects.filter(inspection=inspection).exists()
            else 0
        )
        score = (pcl + pocl) / 2 + pum
        inspection.promptness_score = score.quantize(Decimal(".01"), rounding=ROUND_UP)
        inspection.save()
        return score.quantize(Decimal(".01"), rounding=ROUND_UP)

    def getFunctionalPerformance(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                registeredpublicattendancenumber = (
                    inspection.registeredpublicattendancenumber
                    if RegisteredPublicAttendanceNumber.objects.filter(
                        inspection=inspection
                    ).first()
                    else None
                )
                qualitativeanalysisofthepartscivilcourtlawsuit = (
                    QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).first()
                )
                qualitativeanalysisofthepartscriminalcourtlawsuit = (
                    QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).first()
                )
                qualitativeanalysisofthepartsoutcourtlawsuit = (
                    QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).first()
                )
                qualitativeanalysisofthepartselectoral = (
                    QualitativeAnalysisOfThePartsElectoral.objects.filter(
                        inspection=inspection
                    ).first()
                )
                harmedcalculation = HarmedCalculation.objects.filter(
                    inspection=inspection
                ).first()
                data.append(
                    {
                        "operability_score": str(inspection.operability_score),
                        "dpl_average": (
                            str(inspection.registeredpublicattendancenumber.average)
                            if registeredpublicattendancenumber
                            else None
                        ),
                        "dpl_score": (
                            inspection.registeredpublicattendancenumber.score
                            if registeredpublicattendancenumber
                            else None
                        ),
                        "qapccl_applicable": (
                            self.bool2int(
                                qualitativeanalysisofthepartscivilcourtlawsuit.applicable
                            )
                            if qualitativeanalysisofthepartscivilcourtlawsuit
                            else None
                        ),
                        "qapccl_no_parts_to_analyze": (
                            self.bool2int(
                                qualitativeanalysisofthepartscivilcourtlawsuit.no_parts_to_analyze
                            )
                            if qualitativeanalysisofthepartscivilcourtlawsuit
                            else None
                        ),
                        "qapccl_score": (
                            str(qualitativeanalysisofthepartscivilcourtlawsuit.score)
                            if qualitativeanalysisofthepartscivilcourtlawsuit
                            else None
                        ),
                        "qapcrcl_applicable": (
                            self.bool2int(
                                qualitativeanalysisofthepartscriminalcourtlawsuit.applicable
                            )
                            if qualitativeanalysisofthepartscriminalcourtlawsuit
                            else None
                        ),
                        "qapcrcl_no_parts_to_analyze": (
                            self.bool2int(
                                qualitativeanalysisofthepartscriminalcourtlawsuit.no_parts_to_analyze
                            )
                            if qualitativeanalysisofthepartscriminalcourtlawsuit
                            else None
                        ),
                        "qapcrcl_score": (
                            str(qualitativeanalysisofthepartscriminalcourtlawsuit.score)
                            if qualitativeanalysisofthepartscriminalcourtlawsuit
                            else None
                        ),
                        "qapocl_applicable": (
                            self.bool2int(
                                qualitativeanalysisofthepartsoutcourtlawsuit.applicable
                            )
                            if qualitativeanalysisofthepartsoutcourtlawsuit
                            else None
                        ),
                        "qapocl_no_parts_to_analyze": (
                            self.bool2int(
                                qualitativeanalysisofthepartsoutcourtlawsuit.no_parts_to_analyze
                            )
                            if qualitativeanalysisofthepartsoutcourtlawsuit
                            else None
                        ),
                        "qapocl_score": (
                            str(qualitativeanalysisofthepartsoutcourtlawsuit.score)
                            if qualitativeanalysisofthepartsoutcourtlawsuit
                            else None
                        ),
                        "qape_applicable": (
                            self.bool2int(
                                qualitativeanalysisofthepartselectoral.applicable
                            )
                            if qualitativeanalysisofthepartselectoral
                            else None
                        ),
                        "qape_no_parts_to_analyze": (
                            self.bool2int(
                                qualitativeanalysisofthepartselectoral.no_parts_to_analyze
                            )
                            if qualitativeanalysisofthepartselectoral
                            else None
                        ),
                        "qape_score": (
                            str(qualitativeanalysisofthepartselectoral.score)
                            if qualitativeanalysisofthepartselectoral
                            else None
                        ),
                        "promptness_score": str(inspection.promptness_score),
                        "pcl_percentual": (
                            str(inspection.promptnesscourtlawsuit.percentual)
                            if PromptnessCourtLawsuit.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "pcl_score": (
                            str(inspection.promptnesscourtlawsuit.score)
                            if PromptnessCourtLawsuit.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "pocl_percentual": (
                            str(inspection.promptnessoutcourtlawsuit.percentual)
                            if PromptnessOutCourtLawsuit.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "pocl_score": (
                            str(inspection.promptnessoutcourtlawsuit.score)
                            if PromptnessOutCourtLawsuit.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "pum_percentual": (
                            str(inspection.promptnessuppermanagement.percentual)
                            if PromptnessUpperManagement.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "pum_score": (
                            str(inspection.promptnessuppermanagement.score)
                            if PromptnessUpperManagement.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "final_score": str(inspection.final_score),
                        "hc_harmedcalculation": (
                            self.bool2int(harmedcalculation.harmedcalculation)
                            if harmedcalculation
                            else None
                        ),
                        "hc_justification": (
                            harmedcalculation.justification
                            if harmedcalculation
                            else None
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getProcuratorate(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "ins_tj_session": self.bool2int(inspection.tj_session),
                        "ins_tj_sessions_civil": inspection.tj_sessions_civil,
                        "ins_tj_sessions_criminal": inspection.tj_sessions_criminal,
                        "ins_tj_sessions_administrative": inspection.tj_sessions_administrative,
                        "ins_collegiate_organ_session": self.bool2int(
                            inspection.collegiate_organ_session
                        ),
                        "ins_number_collegiate_organ_session": inspection.number_collegiate_organ_session,
                        "ins_commissions_session": self.bool2int(
                            inspection.commissions_session
                        ),
                        "mp_observation": (
                            inspection.proceduralmovement.observation
                            if ProceduralMovement.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getScoreValue(self, score_table, percentual):
        ret = 0
        scoretable = ConfigScoreTable.objects.filter(
            score_table=score_table, active=True
        ).first()
        if scoretable:
            band = (
                BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=percentual,
                )
                .filter(Q(Q(end_value__isnull=True) | Q(end_value__gte=percentual)))
                .first()
            )
            if band:
                ret = band.score
        return ret

    def getPromptnessCalcScore(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            table = params.get("table")
            cfg = Configuration.get_or_create("corregedoria")
            score_table = int(cfg.get(table, 0))
            percentual = params.get("percentual")
            if percentual != "":
                score = self.getScoreValue(score_table, percentual)
                if table == "var_promptness_courtlawsuit":
                    if PromptnessCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).exists():
                        pcl = PromptnessCourtLawsuit.objects.filter(
                            inspection=inspection
                        ).first()
                    else:
                        pcl = PromptnessCourtLawsuit()
                    pcl.inspection = inspection
                    pcl.score_table = score_table
                    pcl.percentual = percentual
                    pcl.score = score
                    pcl.save()
                if table == "var_promptness_outcourtlawsuit":
                    if PromptnessOutCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).exists():
                        pocl = PromptnessOutCourtLawsuit.objects.filter(
                            inspection=inspection
                        ).first()
                    else:
                        pocl = PromptnessOutCourtLawsuit()
                    pocl.inspection = inspection
                    pocl.score_table = score_table
                    pocl.percentual = percentual
                    pocl.score = score
                    pocl.save()
                if table == "var_promptness_uppermanagement":
                    if PromptnessUpperManagement.objects.filter(
                        inspection=inspection
                    ).exists():
                        pum = PromptnessUpperManagement.objects.filter(
                            inspection=inspection
                        ).first()
                    else:
                        pum = PromptnessUpperManagement()
                    pum.inspection = inspection
                    pum.score_table = score_table
                    pum.percentual = percentual
                    pum.score = score
                    pum.save()
            else:
                score = None
                if table == "var_promptness_courtlawsuit":
                    if PromptnessCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).exists():
                        PromptnessCourtLawsuit.objects.filter(
                            inspection=inspection
                        ).delete()
                if table == "var_promptness_outcourtlawsuit":
                    if PromptnessOutCourtLawsuit.objects.filter(
                        inspection=inspection
                    ).exists():
                        PromptnessOutCourtLawsuit.objects.filter(
                            inspection=inspection
                        ).delete()
                if table == "var_promptness_uppermanagement":
                    if PromptnessUpperManagement.objects.filter(
                        inspection=inspection
                    ).exists():
                        PromptnessUpperManagement.objects.filter(
                            inspection=inspection
                        ).delete()
            promptnessscore = self.getPromptnessScore(inspection=inspection)
            data = []
            if inspection:
                data.append(
                    {
                        "score": str(score),
                        "promptness_score": str(promptnessscore),
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=1,
                collection=data,
            )
        return self.renderer(rst)

    def getGeneralData(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append({})
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getOperatingStructure(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "os_location": (
                            inspection.operatingstructure.location
                            if OperatingStructure.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "os_deficiency": (
                            inspection.structuredeficiency.deficiency
                            if StructureDeficiency.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "os_structuregeneralstatus": (
                            inspection.structuregeneralstatus.status
                            if StructureGeneralStatus.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getAdministrativeOrganization(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "ao_operate_schedule1_initial": (
                            inspection.administrativeorganizationoperatinghours.operate_schedule1_initial
                            if AdministrativeOrganizationOperatingHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_operate_schedule1_final": (
                            inspection.administrativeorganizationoperatinghours.operate_schedule1_final
                            if AdministrativeOrganizationOperatingHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_operate_schedule2_initial": (
                            inspection.administrativeorganizationoperatinghours.operate_schedule2_initial
                            if AdministrativeOrganizationOperatingHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_operate_schedule2_final": (
                            inspection.administrativeorganizationoperatinghours.operate_schedule2_final
                            if AdministrativeOrganizationOperatingHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "aooh_observation": (
                            inspection.administrativeorganizationoperatinghours.observation
                            if AdministrativeOrganizationOperatingHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "daily_attendance": (
                            inspection.administrativeorganizationattendancehours.daily_attendance
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "days_of_attendance_per_week": (
                            inspection.administrativeorganizationattendancehours.days_of_attendance_per_week
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_attendance_schedule1_initial": (
                            inspection.administrativeorganizationattendancehours.attendance_schedule1_initial
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_attendance_schedule1_final": (
                            inspection.administrativeorganizationattendancehours.attendance_schedule1_final
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_attendance_schedule2_initial": (
                            inspection.administrativeorganizationattendancehours.attendance_schedule2_initial
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_attendance_schedule2_final": (
                            inspection.administrativeorganizationattendancehours.attendance_schedule2_final
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "aoah_observation": (
                            inspection.administrativeorganizationattendancehours.observation
                            if AdministrativeOrganizationAttendanceHours.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_registration_type": (
                            inspection.administrativeorganizationregistrationsystem.registration_type
                            if AdministrativeOrganizationRegistrationSystem.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "aors_observation": (
                            inspection.administrativeorganizationregistrationsystem.observation
                            if AdministrativeOrganizationRegistrationSystem.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                        "ao_administrativeorganizationgeneralstatus": (
                            inspection.administrativeorganizationgeneralstatus.status
                            if AdministrativeOrganizationGeneralStatus.objects.filter(
                                inspection=inspection
                            ).exists()
                            is True
                            else None
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getPerformance(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "prf_performance": (
                            inspection.performance.performance
                            if Performance.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getGeneralObservations(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "go_generalobservations": (
                            inspection.generalobservations.observation
                            if GeneralObservations.objects.filter(
                                inspection=inspection
                            ).exists()
                            else None
                        ),
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getRecommendations(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def getAttachments(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            inspection = self.get_query().get(id=params.get("inspection_id"))
            data = []
            if inspection:
                data.append(
                    {
                        "final_score": str(inspection.final_score),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("inspection_id")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def validateData(self, data=[]):
        return True

    def checkInt(self, integer):
        ret_integer = integer if integer != "" else 0
        return ret_integer

    def saveExecutionOrganManagement(self, data):
        if self.validateData():
            if ExecutionOrganManagement.objects.filter(
                inspection=data["inspection"]
            ).exists():
                e = ExecutionOrganManagement.objects.get(inspection=data["inspection"])
            else:
                e = ExecutionOrganManagement()
            e.inspection = data["inspection"]
            e.organization = data["organization"]
            e.observation = data["observation"]
            e.save()

    def savePublicAttendance(self, data):
        if self.validateData():
            if PublicAttendance.objects.filter(inspection=data["inspection"]).exists():
                p = PublicAttendance.objects.get(inspection=data["inspection"])
            else:
                p = PublicAttendance()
            p.inspection = data["inspection"]
            p.record_type = data["record_type"]
            p.apps = data["apps"]
            p.others = data["others"]
            p.opening_date = (
                datetime.strptime(data["opening_date"], "%d/%m/%Y").date()
                if data["opening_date"] != ""
                else None
            )
            p.has_openind_term = data["has_openind_term"]
            p.has_numeration = data["has_numeration"]
            p.has_signed_sheets = data["has_signed_sheets"]
            p.ordered = data["ordered"]
            p.observation = data["observation"]
            p.save()

    def saveOutCourtLawsuitControl(self, data):
        if self.validateData():
            if OutCourtLawsuitControl.objects.filter(
                inspection=data["inspection"]
            ).exists():
                o = OutCourtLawsuitControl.objects.get(inspection=data["inspection"])
            else:
                o = OutCourtLawsuitControl()
            o.inspection = data["inspection"]
            o.record_type = data["record_type"]
            o.apps = data["apps"]
            o.others = data["others"]
            o.opening_date = (
                datetime.strptime(data["opening_date"], "%d/%m/%Y").date()
                if data["opening_date"] != ""
                else None
            )
            o.has_openind_term = data["has_openind_term"]
            o.has_numeration = data["has_numeration"]
            o.has_signed_sheets = data["has_signed_sheets"]
            o.ordered = data["ordered"]
            o.observation = data["observation"]
            o.save()

    def saveCourtLawsuitControl(self, data):
        if self.validateData():
            if CourtLawsuitControl.objects.filter(
                inspection=data["inspection"]
            ).exists():
                c = CourtLawsuitControl.objects.get(inspection=data["inspection"])
            else:
                c = CourtLawsuitControl()
            c.inspection = data["inspection"]
            c.record_type = data["record_type"]
            c.apps = data["apps"]
            c.others = data["others"]
            c.opening_date = (
                datetime.strptime(data["opening_date"], "%d/%m/%Y").date()
                if data["opening_date"] != ""
                else None
            )
            c.has_openind_term = data["has_openind_term"]
            c.has_numeration = data["has_numeration"]
            c.has_signed_sheets = data["has_signed_sheets"]
            c.ordered = data["ordered"]
            c.observation = data["observation"]
            c.save()

    def saveCourtLawsuitCount(self, data):
        if self.validateData():
            if CourtLawsuitCount.objects.filter(inspection=data["inspection"]).exists():
                c = CourtLawsuitCount.objects.get(inspection=data["inspection"])
            else:
                c = CourtLawsuitCount()
            c.inspection = data["inspection"]
            c.number_of_processes_pending_citation_urgent = self.checkInt(
                data["number_of_processes_pending_citation_urgent"]
            )
            c.number_of_processes_pending_citation = self.checkInt(
                data["number_of_processes_pending_citation"]
            )
            c.number_of_processes_pending_science = self.checkInt(
                data["number_of_processes_pending_science"]
            )
            c.processes_with_open_deadline = self.checkInt(
                data["processes_with_open_deadline"]
            )
            c.expired_deadline_the_last_30_days = self.checkInt(
                data["expired_deadline_the_last_30_days"]
            )
            c.expired_deadline_more_than_30_days_ago = self.checkInt(
                data["expired_deadline_more_than_30_days_ago"]
            )
            c.expired_deadline_in_the_period_of_inspection = self.checkInt(
                data["expired_deadline_in_the_period_of_inspection"]
            )
            c.observation = data["observation"]
            c.save()

    def saveOutCourtLawsuitElectoralCount(self, data):
        if self.validateData():
            if OutCourtLawsuitElectoralCount.objects.filter(
                inspection=data["inspection"]
            ).exists():
                o = OutCourtLawsuitElectoralCount.objects.get(
                    inspection=data["inspection"]
                )
            else:
                o = OutCourtLawsuitElectoralCount()
            o.inspection = data["inspection"]
            o.number_of_procedures_in_progress = self.checkInt(
                data["number_of_procedures_in_progress"]
            )
            o.number_of_procedures_in_arrears = self.checkInt(
                data["number_of_procedures_in_arrears"]
            )
            o.correctly_registered_procedures = data["correctly_registered_procedures"]
            o.observation = data["observation"]
            o.save()

    def saveOutCourtLawsuitCount(self, data):
        if self.validateData():
            if OutCourtLawsuitCount.objects.filter(
                inspection=data["inspection"]
            ).exists():
                o = OutCourtLawsuitCount.objects.get(inspection=data["inspection"])
            else:
                o = OutCourtLawsuitCount()

            for key, value in data.items():
                setattr(o, key, value)

            o.save()

    def saveAnalysisPerformanceInAudiences(self, data):
        if self.validateData():
            if AnalysisPerformanceInAudiences.objects.filter(
                inspection=data["inspection"]
            ).exists():
                a = AnalysisPerformanceInAudiences.objects.get(
                    inspection=data["inspection"]
                )
            else:
                a = AnalysisPerformanceInAudiences()
            a.inspection = data["inspection"]
            a.processes_analyzed_in_the_previous_inspection = data[
                "processes_analyzed_in_the_previous_inspection"
            ]
            a.survey_in_randomly_chosen_processes = data[
                "survey_in_randomly_chosen_processes"
            ]
            a.observation = data["observation"]
            a.save()

    def saveAnalysisPerformanceInPlenarySessionOfTheJury(self, data):
        if self.validateData():
            if AnalysisPerformanceInPlenarySessionOfTheJury.objects.filter(
                inspection=data["inspection"]
            ).exists():
                a = AnalysisPerformanceInPlenarySessionOfTheJury.objects.get(
                    inspection=data["inspection"]
                )
            else:
                a = AnalysisPerformanceInPlenarySessionOfTheJury()
            a.inspection = data["inspection"]
            a.analysis = data["analysis"]
            a.save()

    def saveStructureDeficiency(self, data):
        if self.validateData():
            if StructureDeficiency.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = StructureDeficiency.objects.get(inspection=data["inspection"])
            else:
                s = StructureDeficiency()
            s.inspection = data["inspection"]
            s.deficiency = data["deficiency"]
            s.save()

    def saveQualitativeAnalysisOfThePartsCivilCourtLawsuit(self, data):
        if self.validateData():
            if QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
                inspection=data["inspection"]
            ).exists():
                q = QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.get(
                    inspection=data["inspection"]
                )
            else:
                q = QualitativeAnalysisOfThePartsCivilCourtLawsuit()
            q.inspection = data["inspection"]
            q.applicable = data["applicable"]
            q.no_parts_to_analyze = data["no_parts_to_analyze"]
            q.save()

    def saveQualitativeAnalysisOfThePartsCriminalCourtLawsuit(self, data):
        if self.validateData():
            if QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
                inspection=data["inspection"]
            ).exists():
                q = QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.get(
                    inspection=data["inspection"]
                )
            else:
                q = QualitativeAnalysisOfThePartsCriminalCourtLawsuit()
            q.inspection = data["inspection"]
            q.applicable = data["applicable"]
            q.no_parts_to_analyze = data["no_parts_to_analyze"]
            q.save()

    def saveQualitativeAnalysisOfThePartsOutCourtLawsuit(self, data):
        if self.validateData():
            if QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
                inspection=data["inspection"]
            ).exists():
                q = QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.get(
                    inspection=data["inspection"]
                )
            else:
                q = QualitativeAnalysisOfThePartsOutCourtLawsuit()
            q.inspection = data["inspection"]
            q.applicable = data["applicable"]
            q.no_parts_to_analyze = data["no_parts_to_analyze"]
            q.save()

    def saveQualitativeAnalysisOfThePartsElectoral(self, data):
        if self.validateData():
            if QualitativeAnalysisOfThePartsElectoral.objects.filter(
                inspection=data["inspection"]
            ).exists():
                q = QualitativeAnalysisOfThePartsElectoral.objects.get(
                    inspection=data["inspection"]
                )
            else:
                q = QualitativeAnalysisOfThePartsElectoral()
            q.inspection = data["inspection"]
            q.applicable = data["applicable"]
            q.no_parts_to_analyze = data["no_parts_to_analyze"]
            q.save()

    def savePromptnessCourtLawsuit(self, data):
        if self.validateData():
            if PromptnessCourtLawsuit.objects.filter(
                inspection=data["inspection"]
            ).exists():
                pcl = PromptnessCourtLawsuit.objects.get(inspection=data["inspection"])
            else:
                pcl = PromptnessCourtLawsuit()
            pcl.inspection = data["inspection"]
            pcl.percentual = data["percentual"]
            pcl.save()

    def saveHarmedCalculation(self, data):
        if self.validateData():
            if HarmedCalculation.objects.filter(inspection=data["inspection"]).exists():
                h = HarmedCalculation.objects.get(inspection=data["inspection"])
            else:
                h = HarmedCalculation()
            h.inspection = data["inspection"]
            h.harmedcalculation = data["harmedcalculation"]
            h.justification = data["justification"]
            h.save()

    def saveGeneralObservations(self, data):
        if self.validateData():
            if GeneralObservations.objects.filter(
                inspection=data["inspection"]
            ).exists():
                go = GeneralObservations.objects.get(inspection=data["inspection"])
            else:
                go = GeneralObservations()
            go.inspection = data["inspection"]
            go.observation = data["observation"]
            go.save()

    def saveProcuratorate(self, data):
        if self.validateData():
            inspection = data["inspection"]
            inspection.tj_session = data["tj_session"]
            inspection.tj_sessions_civil = data["tj_sessions_civil"]
            inspection.tj_sessions_criminal = data["tj_sessions_criminal"]
            inspection.tj_sessions_administrative = data["tj_sessions_administrative"]
            inspection.collegiate_organ_session = data["collegiate_organ_session"]
            inspection.number_collegiate_organ_session = data[
                "number_collegiate_organ_session"
            ]
            inspection.commissions_session = data["commissions_session"]
            inspection.save()
            if ProceduralMovement.objects.filter(
                inspection=data["inspection"]
            ).exists():
                mp = ProceduralMovement.objects.get(inspection=data["inspection"])
            else:
                mp = ProceduralMovement()
            mp.inspection = data["inspection"]
            mp.observation = data["observation"]
            mp.save()

    def saveOperatingStructure(self, data):
        if self.validateData():
            if OperatingStructure.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = OperatingStructure.objects.get(inspection=data["inspection"])
            else:
                s = OperatingStructure()
            s.inspection = data["inspection"]
            s.location = data["location"]
            s.save()

    def saveStructureGeneralStatus(self, data):
        if self.validateData():
            if StructureGeneralStatus.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = StructureGeneralStatus.objects.get(inspection=data["inspection"])
            else:
                s = StructureGeneralStatus()
            s.inspection = data["inspection"]
            s.status = self.checkInt(data["structuregeneralstatus"])
            s.save()

    def saveAdministrativeOrganizationOperatingHours(self, data):
        if self.validateData():
            if AdministrativeOrganizationOperatingHours.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = AdministrativeOrganizationOperatingHours.objects.get(
                    inspection=data["inspection"]
                )
            else:
                s = AdministrativeOrganizationOperatingHours()
            s.inspection = data["inspection"]
            s.operate_schedule1_initial = data["operate_schedule1_initial"]
            s.operate_schedule1_final = data["operate_schedule1_final"]
            s.operate_schedule2_initial = data["operate_schedule2_initial"]
            s.operate_schedule2_final = data["operate_schedule2_final"]
            s.observation = data["observation"]
            s.save()

    def saveAdministrativeOrganizationAttendanceHours(self, data):
        if self.validateData():
            if AdministrativeOrganizationAttendanceHours.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = AdministrativeOrganizationAttendanceHours.objects.get(
                    inspection=data["inspection"]
                )
            else:
                s = AdministrativeOrganizationAttendanceHours()
            s.inspection = data["inspection"]
            s.daily_attendance = data["daily_attendance"]
            s.days_of_attendance_per_week = self.checkInt(
                data["days_of_attendance_per_week"]
            )
            s.attendance_schedule1_initial = data["attendance_schedule1_initial"]
            s.attendance_schedule1_final = data["attendance_schedule1_final"]
            s.attendance_schedule2_initial = data["attendance_schedule2_initial"]
            s.attendance_schedule2_final = data["attendance_schedule2_final"]
            s.observation = data["observation"]
            s.save()

    def saveAdministrativeOrganizationRegistrationSystem(self, data):
        if self.validateData():
            if AdministrativeOrganizationRegistrationSystem.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = AdministrativeOrganizationRegistrationSystem.objects.get(
                    inspection=data["inspection"]
                )
            else:
                s = AdministrativeOrganizationRegistrationSystem()
            s.inspection = data["inspection"]
            s.registration_type = self.checkInt(data["registration_type"])
            s.observation = data["observation"]
            s.save()

    def saveAdministrativeOrganizationGeneralStatus(self, data):
        if self.validateData():
            if AdministrativeOrganizationGeneralStatus.objects.filter(
                inspection=data["inspection"]
            ).exists():
                s = AdministrativeOrganizationGeneralStatus.objects.get(
                    inspection=data["inspection"]
                )
            else:
                s = AdministrativeOrganizationGeneralStatus()
            s.inspection = data["inspection"]
            s.status = self.checkInt(data["administrativeorganizationgeneralstatus"])
            s.save()

    def savePerformance(self, data):
        if self.validateData():
            if Performance.objects.filter(inspection=data["inspection"]).exists():
                s = Performance.objects.get(inspection=data["inspection"])
            else:
                s = Performance()
            s.inspection = data["inspection"]
            s.performance = data["performance"]
            s.save()

    def save(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = self.request.POST
            frame = params.get("frame")
            inspection = self.get_query().get(id=params.get("inspection_id"))
            if inspection.inspection_type == 1:
                instance = int(params.get("instance"))
                if instance == 1:
                    if frame == "regularityofservices" or frame == "":
                        dataExecutionOrganManagement = {
                            "inspection": inspection,
                            "organization": params.get("eom_organization"),
                            "observation": params.get("eom_observation"),
                        }
                        self.saveExecutionOrganManagement(dataExecutionOrganManagement)
                    if frame == "regularityofservices" or frame == "":
                        dataPublicAttendance = {
                            "inspection": inspection,
                            "record_type": params.get("pa_record_type"),
                            "apps": params.get("pa_apps"),
                            "others": params.get("pa_others"),
                            "opening_date": params.get("pa_opening_date"),
                            "has_openind_term": self.int2bool(
                                params.get("pa_has_openind_term")
                            ),
                            "has_numeration": self.int2bool(
                                params.get("pa_has_numeration")
                            ),
                            "has_signed_sheets": self.int2bool(
                                params.get("pa_has_signed_sheets")
                            ),
                            "ordered": self.int2bool(params.get("pa_ordered")),
                            "observation": params.get("pa_observation"),
                        }
                        self.savePublicAttendance(dataPublicAttendance)
                    if frame == "regularityofservices" or frame == "":
                        dataOutCourtLawsuitControl = {
                            "inspection": inspection,
                            "record_type": params.get("oclsc_record_type"),
                            "apps": params.get("oclsc_apps"),
                            "others": params.get("oclsc_others"),
                            "opening_date": params.get("oclsc_opening_date"),
                            "has_openind_term": self.int2bool(
                                params.get("oclsc_has_openind_term")
                            ),
                            "has_numeration": self.int2bool(
                                params.get("oclsc_has_numeration")
                            ),
                            "has_signed_sheets": self.int2bool(
                                params.get("oclsc_has_signed_sheets")
                            ),
                            "ordered": self.int2bool(params.get("oclsc_ordered")),
                            "observation": params.get("oclsc_observation"),
                        }
                        self.saveOutCourtLawsuitControl(dataOutCourtLawsuitControl)
                    if frame == "regularityofservices" or frame == "":
                        dataCourtLawsuitControl = {
                            "inspection": inspection,
                            "record_type": params.get("clsc_record_type"),
                            "apps": params.get("clsc_apps"),
                            "others": params.get("clsc_others"),
                            "opening_date": params.get("clsc_opening_date"),
                            "has_openind_term": self.int2bool(
                                params.get("clsc_has_openind_term")
                            ),
                            "has_numeration": self.int2bool(
                                params.get("clsc_has_numeration")
                            ),
                            "has_signed_sheets": self.int2bool(
                                params.get("clsc_has_signed_sheets")
                            ),
                            "ordered": self.int2bool(params.get("clsc_ordered")),
                            "observation": params.get("clsc_observation"),
                        }
                        self.saveCourtLawsuitControl(dataCourtLawsuitControl)
                    if frame == "regularityofservices" or frame == "":
                        dataCourtLawsuitCount = {
                            "inspection": inspection,
                            "number_of_processes_pending_citation_urgent": params.get(
                                "clsct_number_of_processes_pending_citation_urgent"
                            ),
                            "number_of_processes_pending_citation": params.get(
                                "clsct_number_of_processes_pending_citation"
                            ),
                            "number_of_processes_pending_science": params.get(
                                "clsct_number_of_processes_pending_science"
                            ),
                            "processes_with_open_deadline": params.get(
                                "clsct_processes_with_open_deadline"
                            ),
                            "expired_deadline_the_last_30_days": params.get(
                                "clsct_expired_deadline_the_last_30_days"
                            ),
                            "expired_deadline_more_than_30_days_ago": params.get(
                                "clsct_expired_deadline_more_than_30_days_ago"
                            ),
                            "expired_deadline_in_the_period_of_inspection": params.get(
                                "clsct_expired_deadline_in_the_period_of_inspection"
                            ),
                            "observation": params.get("clsct_observation"),
                        }
                        self.saveCourtLawsuitCount(dataCourtLawsuitCount)
                    if frame == "regularityofservices" or frame == "":
                        dataOutCourtLawsuitElectoralCount = {
                            "inspection": inspection,
                            "number_of_procedures_in_progress": params.get(
                                "oclsect_number_of_procedures_in_progress"
                            ),
                            "number_of_procedures_in_arrears": params.get(
                                "oclsect_number_of_procedures_in_arrears"
                            ),
                            "correctly_registered_procedures": self.int2bool(
                                params.get("oclsect_correctly_registered_procedures")
                            ),
                            "observation": params.get("oclsect_observation"),
                        }
                        self.saveOutCourtLawsuitElectoralCount(
                            dataOutCourtLawsuitElectoralCount
                        )
                    if frame == "regularityofservices" or frame == "":
                        dataOutCourtLawsuitCount = {
                            "inspection": inspection,
                            "number_of_procedures_in_progress": self.checkInt(
                                params.get("oclsct_number_of_procedures_in_progress")
                            ),
                            "number_of_procedures_in_arrears": self.checkInt(
                                params.get("oclsct_number_of_procedures_in_arrears")
                            ),
                            "correctly_registered_procedures": self.int2bool(
                                params.get("oclsct_correctly_registered_procedures")
                            ),
                            "number_of_public_civil_actions_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_public_civil_actions_in_the_last_year"
                                )
                            ),
                            "number_of_recommendations_issued_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_recommendations_issued_in_the_last_year"
                                )
                            ),
                            "number_of_conduct_adjustment_terms_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_conduct_adjustment_terms_in_the_last_year"
                                )
                            ),
                            "number_of_tac_administrative_dishonesty": self.checkInt(
                                params.get(
                                    "oclsct_number_of_tac_administrative_dishonesty"
                                )
                            ),
                            "number_of_acp_administrative_dishonesty": self.checkInt(
                                params.get(
                                    "oclsct_number_of_acp_administrative_dishonesty"
                                )
                            ),
                            "number_of_public_audiences_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_public_audiences_in_the_last_year"
                                )
                            ),
                            "number_of_procedures_instituted_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_procedures_instituted_in_the_last_year"
                                )
                            ),
                            "number_of_procedures_archived_in_the_last_year": self.checkInt(
                                params.get(
                                    "oclsct_number_of_procedures_archived_in_the_last_year"
                                )
                            ),
                            "observation": params.get("oclsct_observation"),
                        }
                        self.saveOutCourtLawsuitCount(dataOutCourtLawsuitCount)
                    if frame == "regularityofservices" or frame == "":
                        dataAnalysisPerformanceInAudiences = {
                            "inspection": inspection,
                            "processes_analyzed_in_the_previous_inspection": self.int2bool(
                                params.get(
                                    "apia_processes_analyzed_in_the_previous_inspection"
                                )
                            ),
                            "survey_in_randomly_chosen_processes": self.int2bool(
                                params.get("apia_survey_in_randomly_chosen_processes")
                            ),
                            "observation": params.get("apia_observation"),
                        }
                        self.saveAnalysisPerformanceInAudiences(
                            dataAnalysisPerformanceInAudiences
                        )
                    if frame == "regularityofservices" or frame == "":
                        dataAnalysisPerformanceInPlenarySessionOfTheJury = {
                            "inspection": inspection,
                            "analysis": params.get("apijts_analysis"),
                        }
                        self.saveAnalysisPerformanceInPlenarySessionOfTheJury(
                            dataAnalysisPerformanceInPlenarySessionOfTheJury
                        )
                    if frame == "functionalperformance" or frame == "":
                        dataQualitativeAnalysisOfThePartsCivilCourtLawsuit = {
                            "inspection": inspection,
                            "applicable": self.int2bool(
                                params.get("qapccl_applicable")
                            ),
                            "no_parts_to_analyze": self.int2bool(
                                params.get("qapccl_no_parts_to_analyze")
                            ),
                        }
                        self.saveQualitativeAnalysisOfThePartsCivilCourtLawsuit(
                            dataQualitativeAnalysisOfThePartsCivilCourtLawsuit
                        )
                    if frame == "functionalperformance" or frame == "":
                        dataQualitativeAnalysisOfThePartsCriminalCourtLawsuit = {
                            "inspection": inspection,
                            "applicable": self.int2bool(
                                params.get("qapcrcl_applicable")
                            ),
                            "no_parts_to_analyze": self.int2bool(
                                params.get("qapcrcl_no_parts_to_analyze")
                            ),
                        }
                        self.saveQualitativeAnalysisOfThePartsCriminalCourtLawsuit(
                            dataQualitativeAnalysisOfThePartsCriminalCourtLawsuit
                        )
                    if frame == "functionalperformance" or frame == "":
                        dataQualitativeAnalysisOfThePartsOutCourtLawsuit = {
                            "inspection": inspection,
                            "applicable": self.int2bool(
                                params.get("qapocl_applicable")
                            ),
                            "no_parts_to_analyze": self.int2bool(
                                params.get("qapocl_no_parts_to_analyze")
                            ),
                        }
                        self.saveQualitativeAnalysisOfThePartsOutCourtLawsuit(
                            dataQualitativeAnalysisOfThePartsOutCourtLawsuit
                        )
                    if frame == "functionalperformance" or frame == "":
                        dataQualitativeAnalysisOfThePartsElectoral = {
                            "inspection": inspection,
                            "applicable": self.int2bool(params.get("qape_applicable")),
                            "no_parts_to_analyze": self.int2bool(
                                params.get("qape_no_parts_to_analyze")
                            ),
                        }
                        self.saveQualitativeAnalysisOfThePartsElectoral(
                            dataQualitativeAnalysisOfThePartsElectoral
                        )
                    if frame == "functionalperformance" or frame == "":
                        dataHarmedCalculation = {
                            "inspection": inspection,
                            "harmedcalculation": self.int2bool(
                                params.get("hc_harmedcalculation")
                            ),
                            "justification": params.get("hc_justification"),
                        }
                        self.saveHarmedCalculation(dataHarmedCalculation)
                if instance == 2:
                    if frame == "procuratorate" or frame == "":
                        dataProcuratorate = {
                            "inspection": inspection,
                            "tj_session": self.int2bool(params.get("ins_tj_session")),
                            "tj_sessions_civil": params.get("ins_tj_sessions_civil"),
                            "tj_sessions_criminal": params.get(
                                "ins_tj_sessions_criminal"
                            ),
                            "tj_sessions_administrative": params.get(
                                "ins_tj_sessions_administrative"
                            ),
                            "collegiate_organ_session": self.int2bool(
                                params.get("ins_collegiate_organ_session")
                            ),
                            "number_collegiate_organ_session": params.get(
                                "ins_number_collegiate_organ_session"
                            ),
                            "commissions_session": self.int2bool(
                                params.get("ins_commissions_session")
                            ),
                            "observation": params.get("mp_observation"),
                        }
                        self.saveProcuratorate(dataProcuratorate)
                    if frame == "regularityofservices" or frame == "":
                        dataProcuratorate = {
                            "inspection": inspection,
                            "tj_session": self.int2bool(params.get("ins_tj_session")),
                            "tj_sessions_civil": params.get("ins_tj_sessions_civil"),
                            "tj_sessions_criminal": params.get(
                                "ins_tj_sessions_criminal"
                            ),
                            "tj_sessions_administrative": params.get(
                                "ins_tj_sessions_administrative"
                            ),
                            "collegiate_organ_session": self.int2bool(
                                params.get("ins_collegiate_organ_session")
                            ),
                            "number_collegiate_organ_session": params.get(
                                "ins_number_collegiate_organ_session"
                            ),
                            "commissions_session": self.int2bool(
                                params.get("ins_commissions_session")
                            ),
                            "observation": params.get("mp_observation"),
                        }
                        self.saveProcuratorate(dataProcuratorate)
                if frame == "structure" or frame == "":
                    dataStructureDeficiency = {
                        "inspection": inspection,
                        "deficiency": params.get("est_deficiency"),
                    }
                    self.saveStructureDeficiency(dataStructureDeficiency)
                if frame == "generalobservations" or frame == "":
                    dataGeneralObservations = {
                        "inspection": inspection,
                        "observation": params.get("go_generalobservations"),
                    }
                    self.saveGeneralObservations(dataGeneralObservations)
            if inspection.inspection_type in [2, 3]:
                if frame == "operatingstructure" or frame == "":
                    dataOperatingStructure = {
                        "inspection": inspection,
                        "location": params.get("os_location"),
                    }
                    self.saveOperatingStructure(dataOperatingStructure)
                    dataStructureDeficiency = {
                        "inspection": inspection,
                        "deficiency": params.get("os_deficiency"),
                    }
                    self.saveStructureDeficiency(dataStructureDeficiency)
                    dataStructureGeneralStatus = {
                        "inspection": inspection,
                        "structuregeneralstatus": params.get(
                            "os_structuregeneralstatus"
                        ),
                    }
                    self.saveStructureGeneralStatus(dataStructureGeneralStatus)
                if frame == "administrativeorganization" or frame == "":
                    dataAdministrativeOrganizationOperatingHours = {
                        "inspection": inspection,
                        "operate_schedule1_initial": params.get(
                            "ao_operate_schedule1_initial"
                        ),
                        "operate_schedule1_final": params.get(
                            "ao_operate_schedule1_final"
                        ),
                        "operate_schedule2_initial": params.get(
                            "ao_operate_schedule2_initial"
                        ),
                        "operate_schedule2_final": params.get(
                            "ao_operate_schedule2_final"
                        ),
                        "observation": params.get("aooh_observation"),
                    }
                    self.saveAdministrativeOrganizationOperatingHours(
                        dataAdministrativeOrganizationOperatingHours
                    )

                    dataAdministrativeOrganizationAttendanceHours = {
                        "inspection": inspection,
                        "daily_attendance": params.get("daily_attendance", "off")
                        == "on",
                        "days_of_attendance_per_week": params.get(
                            "days_of_attendance_per_week"
                        ),
                        "attendance_schedule1_initial": params.get(
                            "ao_attendance_schedule1_initial"
                        ),
                        "attendance_schedule1_final": params.get(
                            "ao_attendance_schedule1_final"
                        ),
                        "attendance_schedule2_initial": params.get(
                            "ao_attendance_schedule2_initial"
                        ),
                        "attendance_schedule2_final": params.get(
                            "ao_attendance_schedule2_final"
                        ),
                        "observation": params.get("aoah_observation"),
                    }
                    self.saveAdministrativeOrganizationAttendanceHours(
                        dataAdministrativeOrganizationAttendanceHours
                    )
                    dataAdministrativeOrganizationRegistrationSystem = {
                        "inspection": inspection,
                        "registration_type": params.get("ao_registration_type"),
                        "observation": params.get("aors_observation"),
                    }
                    self.saveAdministrativeOrganizationRegistrationSystem(
                        dataAdministrativeOrganizationRegistrationSystem
                    )
                    dataAdministrativeOrganizationGeneralStatus = {
                        "inspection": inspection,
                        "administrativeorganizationgeneralstatus": params.get(
                            "ao_administrativeorganizationgeneralstatus"
                        ),
                    }
                    self.saveAdministrativeOrganizationGeneralStatus(
                        dataAdministrativeOrganizationGeneralStatus
                    )
                if frame == "performance" or frame == "":
                    dataPerformance = {
                        "inspection": inspection,
                        "performance": params.get("prf_performance"),
                    }
                    self.savePerformance(dataPerformance)
                if frame == "generalobservations" or frame == "":
                    dataGeneralObservations = {
                        "inspection": inspection,
                        "observation": params.get("go_generalobservations"),
                    }
                    self.saveGeneralObservations(dataGeneralObservations)
            inspection.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Inspeção persistida com sucesso.")
        return self.renderer(rst)

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            inspection = Inspection.objects.filter(
                pk=int(params.get("inspection", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=inspection.rendered)
        self.renderer(rst)

    def get_signs(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection_id = (
                int(params.get("inspection_id"))
                if params.get("inspection_id") != ""
                else 0
            )
            atual_employee = employee_from_user(get_current_user())
            data = []
            count = 0
            ig_sign = Sign.objects.filter(
                inspection__pk=inspection_id, profile=1
            ).first()
            ip_sign = Sign.objects.filter(
                inspection__pk=inspection_id, profile=2, employee=atual_employee
            ).first()
            data.append(
                {
                    "ig_sign_at": (
                        ig_sign.created_at.strftime("%d/%m/%Y %H:%M:%S")
                        if ig_sign
                        else None
                    ),
                    "ig_dispatch": ig_sign.dispatch if ig_sign else None,
                    "ip_sign_at": (
                        ip_sign.created_at.strftime("%d/%m/%Y %H:%M:%S")
                        if ip_sign
                        else None
                    ),
                    "ip_dispatch": ip_sign.dispatch if ip_sign else None,
                }
            )
            if ig_sign or ip_sign:
                count = 1
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=count,
                collection=data,
            )
        return self.renderer(rst)

    def saveSign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection_id = (
                int(params.get("inspection_id"))
                if params.get("inspection_id") != ""
                else 0
            )
            inspection = Inspection.objects.get(pk=inspection_id)
            dispatch = ""
            profile = None
            inspector_general_bool = params.get("inspector_general_bool") == "true"
            if inspector_general_bool:
                profile = 1
                dispatch = params.get("ig_dispatch")
                employee = inspection.inspector_general.pk
            inspector_prosecutor_bool = (
                params.get("inspector_prosecutor_bool") == "true"
            )
            if inspector_prosecutor_bool:
                profile = 2
                dispatch = params.get("ip_dispatch")
                employee = (
                    int(params.get("employee"))
                    if params.get("employee") != ""
                    else None
                )
            sign = Sign()
            sign.inspection = inspection
            sign.employee_id = employee
            sign.dispatch = dispatch
            sign.profile = profile
            sign.save()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção/Correição assinada com sucesso.",
            )
        return self.renderer(rst)

    def removeSign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection_id = (
                int(params.get("inspection_id"))
                if params.get("inspection_id") != ""
                else 0
            )
            atual_employee = employee_from_user(get_current_user())
            profile = None
            inspector_general_bool = params.get("inspector_general_bool") == "true"
            if inspector_general_bool:
                profile = 1
            inspector_prosecutor_bool = (
                params.get("inspector_prosecutor_bool") == "true"
            )
            if inspector_prosecutor_bool:
                profile = 2

            Sign.remove_sign(
                inspection=inspection_id, profile=profile, employee=atual_employee
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Remoção da assinatura realizada com sucesso.",
            )
        return self.renderer(rst)

    def reloadData(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection = Inspection.objects.filter(
                pk=int(params.get("inspection", 0) or 0)
            ).first()
            item = params.get("item", "all")

            if item == "employees":
                inspection.reload_data_employees()
            elif item == "accumulates":
                inspection.reload_accumulations()
            elif item == "address":
                inspection.reload_data_address()
            elif item == "lawsuit":
                inspection.reload_data_lawsuit()
            elif item == "all":
                inspection.reloadData()

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados da Inspeção recarregados com sucesso.",
            )
        return self.renderer(rst)

    def finalize(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection = Inspection.objects.filter(
                pk=int(params.get("inspection", 0) or 0)
            ).first()
            inspection.finalize()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção finaliza com sucesso.",
            )
        return self.renderer(rst)

    def communication(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            inspection = Inspection.objects.filter(
                pk=int(params.get("inspection", 0) or 0)
            ).first()
            inspection.send_communication()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção remetida com sucesso.",
            )
        return self.renderer(rst)

    def communication_cpjcsmp(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            ret = None
            params = self.request.POST
            list_inspection = Inspection.objects.filter(
                pk__in=params.get("list_inspection", 0).split(",")
            )
            var_length = len(list_inspection)
            var_report = ""
            link = []
            for inspection in list_inspection:
                if inspection.inspection_type == 1:
                    var_report = (
                        "/to/mpe/corregedoria/inspection/inspection_report"
                        if inspection.execution_organ.instancia.pk == 1
                        else "/to/mpe/corregedoria/inspection/inspection_report_procuratorate"
                    )
                if inspection.inspection_type == 2:
                    var_report = "/to/mpe/corregedoria/inspection/inspection_report_especialgroup"
                if inspection.inspection_type == 3:
                    var_report = "/to/mpe/corregedoria/inspection/inspection_report_auxiliarorgan"
                ll = {
                    "var_report": var_report,
                    "var_slug_name": inspection.execution_organ.order_nome,
                    "var_name": inspection.execution_organ.nome,
                    "var_inspection": inspection.pk,
                }
                link.append(ll)
            subject = "Relatório de Inspeção/Correição"
            loc_origin = Lotacao.objects.get(pk=457)
            resp_origin = loc_origin.responsavel
            data = [
                loader.get_template("inspection/communication_cpjcsmp.html").render(
                    {
                        "inspector_general": resp_origin,
                        "link": link,
                        "var_length": var_length,
                    }
                )
            ]
            message = "".join(data).replace("\n", "")
            protocol = Protocolo.docketing(
                subject=subject,
                document_type=TipoDocumento.objects.get(pk=94),
                interested=person_from_user(resp_origin.user),
                home_court=loc_origin,
                content=message,
            )
            current = Movimentacao.inbox_queryset().get(protocolo=protocol)
            current.do_send(
                # _FIXME_ Evitar o uso direto de pk.
                location_destination=[455, 456],
                employee_origin=employee_from_user(get_current_user()),
                physical=False,
                opinion=True,
            )
            for inspection in list_inspection:
                inspection.communication_cpjcsmp()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção remetida com sucesso.",
            )
        return self.renderer(rst)
