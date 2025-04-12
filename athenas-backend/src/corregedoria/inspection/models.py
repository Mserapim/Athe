# -*- coding: utf-8 -*-
import re
import json
import calendar

from datetime import datetime, date
from decimal import Decimal

from django.template import loader, Context
from django.db import models
from django.db.models import Avg, Q, Sum
from django.contrib.auth.models import User

from standard.models import AuditTimestampModel, Choice, Configuration
from contrib.utils import getLogger, employee_from_user, person_from_user
from contrib.middleware import get_current_user
from edocs.protocolo.models import Protocolo, Movimentacao, TipoDocumento
from rh.models import (
    Lotacao as Location,
    Servidor as Employee,
    MovimentacaoPessoal,
    MovimentacaoPosse,
    MovimentacaoSubstituicao as Replacement,
    ServidorLotacao,
)
from rh.cif.models import Teaching as Docencia, AddressCif
from ged.models import Arquivo
from judicial.models import LegalClass, LegalMatter, LegalMoviment, OutCourtLawsuit
from raf.models import Activity

from corregedoria.utils import format_category_employee
from corregedoria.models import (
    ConfigScoreTable,
    BandScoreTable,
    ConfigLinkInspectionRAF,
)
from corregedoria.cirdir.models import (
    Teaching as TeachingCirdir,
    Address as AddressCirdir,
)


log = getLogger(__name__)


class Inspection(AuditTimestampModel):
    """
    Inspecao/Correicao realizadas pela Corregedoria-geral do MPE/TO
    """

    inspection_date_initial = models.DateField(null=True, blank=True)
    inspection_date_final = models.DateField(null=True, blank=True)
    notice = models.CharField(max_length=100)
    publication = models.CharField(max_length=100)
    inspector_general = models.ForeignKey(
        Employee, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    inspector_prosecutor = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    inspector_prosecutors = models.ManyToManyField(
        Employee, related_name="inspector_prosecutors", blank=True
    )
    area_of_action = models.CharField(max_length=1000, null=True, blank=True)
    assignment = models.CharField(max_length=1000, null=True, blank=True)
    employee = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    responsible = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    holder_employee = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    residence = models.BooleanField(default=False)
    accumulates = models.BooleanField(default=False, null=True, blank=True)
    replacements = models.BooleanField(default=False, null=True, blank=True)
    attendance = models.BooleanField(default=False)
    teaching = models.BooleanField(default=False, null=True, blank=True)
    execution_organ = models.ForeignKey(
        Location, related_name="inspections", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    last_inspection_date = models.DateField(null=True, blank=True)
    titular_employee = models.BooleanField(default=False, null=True, blank=True)
    daily_attendance = models.BooleanField(default=False)
    days_of_attendance_per_week = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    attendance_schedule1_inital = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule1_final = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule2_inital = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule2_final = models.CharField(max_length=5, null=True, blank=True)
    observation = models.TextField(null=True, blank=True)
    list_months = models.CharField(max_length=300, null=True, blank=True)
    electoral_applicable = models.SmallIntegerField(default=2, null=True, blank=True)
    electoral_electoralzone = models.CharField(max_length=50, null=True, blank=True)
    electoral_designation = models.CharField(max_length=100, null=True, blank=True)
    electoral_initialbiennium = models.CharField(max_length=50, null=True, blank=True)
    electoral_finalbiennium = models.CharField(max_length=50, null=True, blank=True)
    operability_score = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, null=True, blank=True
    )
    promptness_score = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, null=True, blank=True
    )
    tj_session = models.BooleanField(null=True, blank=True)
    tj_sessions_civil = models.SmallIntegerField(default=0, null=True, blank=True)
    tj_sessions_criminal = models.SmallIntegerField(default=0, null=True, blank=True)
    tj_sessions_administrative = models.SmallIntegerField(
        default=0, null=True, blank=True
    )
    collegiate_organ_session = models.BooleanField(null=True, blank=True)
    number_collegiate_organ_session = models.SmallIntegerField(
        default=0, null=True, blank=True
    )
    commissions_session = models.BooleanField(null=True, blank=True)
    finalized = models.BooleanField(default=False, null=True, blank=True)
    finalized_at = models.DateField(null=True, blank=True)
    communicated_organ_execution = models.BooleanField(
        default=False, null=True, blank=True
    )
    communicated_organ_execution_at = models.DateField(null=True, blank=True)
    communicated_cpjcsmp = models.BooleanField(default=False, null=True, blank=True)
    communicated_cpjcsmp_at = models.DateField(null=True, blank=True)

    inspection_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "INSPECTION_TYPE"),
        verbose_name="Tipo de Inspeção",
        default=1,
    )
    cache_rendered = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-inspection_date_initial", "execution_organ"]
        verbose_name = "Inspeção/Correição"

    def __str__(self):
        return "%s (%s a %s)" % (
            self.execution_organ.nome,
            self.inspection_date_initial_formatted,
            self.inspection_date_final_formatted,
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.signs.all().count() == 0:
            item = {
                "title": "Em edição",
                "iconCls": "icon-judicial icon-ejud-edition-mode",
            }
        if self.signs.all().count() == 1:
            item = {
                "title": "Assinado",
                "iconCls": "icon-judicial icon-ejud-interested",
            }
        if self.signs.all().count() >= 2:
            item = {
                "title": "Assinado",
                "iconCls": "icon-judicial icon-ejud-manifestation-direct",
            }
        rst.append(item)
        if self.communicated_organ_execution:
            item = {
                "title": "Remetido ao Órgão Inspecionado em <b>"
                + self.communicated_organ_execution_at.strftime("%d/%m/%Y")
                + "</b>",
                "iconCls": "icon-crgmpe icon-crgmpe-send-mail",
            }
            rst.append(item)
        if self.communicated_cpjcsmp:
            item = {
                "title": "Remetido ao CPJ e CSMP em <b>"
                + self.communicated_cpjcsmp_at.strftime("%d/%m/%Y")
                + "</b>",
                "iconCls": "icon-crgmpe icon-crgmpe-mail",
            }
            rst.append(item)
        if self.finalized:
            item = {
                "title": "Finalizado em <b>"
                + self.finalized_at.strftime("%d/%m/%Y")
                + "</b>",
                "iconCls": "icon-judicial icon-ejud-read-only",
            }
            rst.append(item)
        return rst

    @property
    def inspection_date_initial_formatted(self):
        return self.inspection_date_initial.strftime("%d/%m/%Y")

    @property
    def inspection_date_final_formatted(self):
        return self.inspection_date_final.strftime("%d/%m/%Y")

    @property
    def final_score(self):
        ret = (self.operability_score if self.operability_score else 0) + (
            self.promptness_score if self.promptness_score else 0
        )
        if HarmedCalculation.objects.filter(inspection=self).exists():
            if self.harmedcalculation.harmedcalculation is True:
                ret = "PREJUDICADO"
        return ret

    @property
    def has_signature(self):
        return self.signs.exists()

    @property
    def rendered(self):
        data = (
            self._renderer_document if not self.cache_rendered else self.cache_rendered
        )
        return data

    @property
    def _renderer_document(self):
        var_tiles = ""
        if self.inspection_type:
            if self.inspection_type == 1:
                if self.execution_organ.instancia.pk == 1:
                    var_tiles = "inspection/inspection_executionorgan.html"
                else:
                    var_tiles = (
                        "inspection/inspection_executionorgan_procuratorate.html"
                    )
            if self.inspection_type == 2:
                var_tiles = "inspection/inspection_especialgroup.html"
            if self.inspection_type == 3:
                var_tiles = "inspection/inspection_auxiliaryorgan.html"
            tpl = loader.get_template(var_tiles)
            return tpl.render(
                {
                    "inspection": self,
                    "rpa": RegistrationPublicAttendance.objects.filter(inspection=self),
                    "broclc": BookOfRegisterOutCourtLawsuitControl.objects.filter(
                        inspection=self
                    ),
                    "brclc": BookOfRegisterCourtLawsuitControl.objects.filter(
                        inspection=self
                    ),
                    "rclr": RegistrationCourtLawsuitReceived.objects.filter(
                        inspection=self
                    ),
                    "rclrt": RegistrationCourtLawsuitReturned.objects.filter(
                        inspection=self
                    ),
                    "rcler": RegistrationCourtLawsuitElectoralReceived.objects.filter(
                        inspection=self
                    ),
                    "rclert": RegistrationCourtLawsuitElectoralReturned.objects.filter(
                        inspection=self
                    ),
                    "pfapia": ProcessesForAnalysisPerformanceInAudiences.objects.filter(
                        inspection=self
                    ),
                    "see": StructureEffectiveEmployees.objects.filter(inspection=self),
                    "sce": StructureCommissionedEmployees.objects.filter(
                        inspection=self
                    ),
                    "sexe": StructureExternalEmployees.objects.filter(inspection=self),
                    "sep": StructureExternalPeoples.objects.filter(inspection=self),
                    "qapccl": QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
                        inspection=self
                    ).first(),
                    "pfqapccl": ProcForQualAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
                        inspection=self
                    ),
                    "qapcrcl": QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
                        inspection=self
                    ).first(),
                    "pfqapcrcl": ProcForQualAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
                        inspection=self
                    ),
                    "qapocl": QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
                        inspection=self
                    ).first(),
                    "pfqapocl": ProcForQualAnalysisOfThePartsOutCourtLawsuit.objects.filter(
                        inspection=self
                    ),
                    "qape": QualitativeAnalysisOfThePartsElectoral.objects.filter(
                        inspection=self
                    ).first(),
                    "pfqape": ProcForQualAnalysisOfThePartsElectoral.objects.filter(
                        inspection=self
                    ),
                    "rec": Recommendations.objects.filter(inspection=self),
                    "attach_rs": Attachments.objects.filter(
                        inspection=self, area=1
                    ).order_by("attachment_type", "description"),
                    "attach_e": Attachments.objects.filter(
                        inspection=self, area=2
                    ).order_by("attachment_type", "description"),
                    "attach_df": Attachments.objects.filter(
                        inspection=self, area=3
                    ).order_by("attachment_type", "description"),
                    "attach_og": Attachments.objects.filter(
                        inspection=self, area=4
                    ).order_by("attachment_type", "description"),
                    "attach_r": Attachments.objects.filter(
                        inspection=self, area=5
                    ).order_by("attachment_type", "description"),
                    "attach_a": Attachments.objects.filter(
                        inspection=self, area=6
                    ).order_by("attachment_type", "description"),
                    "pm": ProceduralMovement.objects.filter(inspection=self).first(),
                    "pmr": ProceduralMovementReceived.objects.filter(inspection=self),
                    "pmrt": ProceduralMovementReturned.objects.filter(inspection=self),
                    "pmo": ProceduralMovementOutCourtLawsuit.objects.filter(
                        inspection=self
                    ),
                    "pfqapp": ProcForQualAnalysisOfThePartsProcuratorate.objects.filter(
                        inspection=self
                    ),
                    "sign_inspector_prosecutor": Sign.objects.filter(
                        inspection=self, profile=2
                    ).first(),
                    "sign_inspector_prosecutors": Sign.objects.filter(
                        inspection=self, profile=2
                    ),
                    "sign_inspector_general": Sign.objects.filter(
                        inspection=self, profile=1
                    ).first(),
                    "membersorgan": MemberOrgan.objects.filter(inspection=self),
                    "equipmentsorgan": StructureEquipment.objects.filter(
                        inspection=self
                    ),
                    "operatingstructure": OperatingStructure.objects.filter(
                        inspection=self
                    ).first(),
                    "structuregeneralstatus": StructureGeneralStatus.objects.filter(
                        inspection=self
                    ).first(),
                    "administrativeorganizationregistrationsystem": AdministrativeOrganizationRegistrationSystem.objects.filter(
                        inspection=self
                    ).first(),
                    "attach_administrativeorganization": Attachments.objects.filter(
                        inspection=self, area=8
                    ).order_by("attachment_type", "description"),
                    "existingregisters": ExistingRegisters.objects.filter(
                        inspection=self
                    ),
                    "administrativeorganizationgeneralstatus": AdministrativeOrganizationGeneralStatus.objects.filter(
                        inspection=self
                    ).first(),
                    "performance": Performance.objects.filter(inspection=self).first(),
                    "attach_performance": Attachments.objects.filter(
                        inspection=self, area=9
                    ).order_by("attachment_type", "description"),
                    "administrativeorganizationproceduresinprogress": AdministrativeOrganizationProceduresInProgress.objects.filter(
                        inspection=self
                    ),
                    "administrativeorganizationarchivedprocedures": AdministrativeOrganizationArchivedProcedures.objects.filter(
                        inspection=self
                    ),
                    "administrativeorganizationoperatinghours": AdministrativeOrganizationOperatingHours.objects.filter(
                        inspection=self
                    ).first(),
                    "administrativeorganizationattendancehours": AdministrativeOrganizationAttendanceHours.objects.filter(
                        inspection=self
                    ).first(),
                }
            )

    def addMonths(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def getPeriodInspection(self, qtd):
        final_date = self.inspection_date_initial
        initial_date = self.addMonths(final_date, -1 * qtd)
        total_months = qtd
        list_months = []
        d = initial_date
        for i in range(1, total_months + 1):
            list_months.append({"month": d.month, "year": d.year})
            d = self.addMonths(d, 1)
        return list_months

    def calcOperabilityScore(self):
        soma = Decimal(0.00)
        qtd_items = 0
        media = Decimal(0.00)
        score = Decimal(0.00)
        registeredpublicattendancenumber = (
            RegisteredPublicAttendanceNumber.objects.filter(inspection=self).first()
        )
        qualitativeanalysisofthepartscivilcourtlawsuit = (
            QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
                inspection=self
            ).first()
        )
        qualitativeanalysisofthepartscriminalcourtlawsuit = (
            QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
                inspection=self
            ).first()
        )
        qualitativeanalysisofthepartsoutcourtlawsuit = (
            QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
                inspection=self
            ).first()
        )
        qualitativeanalysisofthepartselectoral = (
            QualitativeAnalysisOfThePartsElectoral.objects.filter(
                inspection=self
            ).first()
        )
        if qualitativeanalysisofthepartscivilcourtlawsuit:
            if (
                qualitativeanalysisofthepartscivilcourtlawsuit.applicable
                and qualitativeanalysisofthepartscivilcourtlawsuit.no_parts_to_analyze
            ):
                qtd_items = qtd_items + 1
                soma = soma + qualitativeanalysisofthepartscivilcourtlawsuit.score
        if (
            qualitativeanalysisofthepartscriminalcourtlawsuit
            and qualitativeanalysisofthepartscriminalcourtlawsuit.no_parts_to_analyze
        ):
            if qualitativeanalysisofthepartscriminalcourtlawsuit.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qualitativeanalysisofthepartscriminalcourtlawsuit.score
        if (
            qualitativeanalysisofthepartsoutcourtlawsuit
            and qualitativeanalysisofthepartsoutcourtlawsuit.no_parts_to_analyze
        ):
            if qualitativeanalysisofthepartsoutcourtlawsuit.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qualitativeanalysisofthepartsoutcourtlawsuit.score
        if (
            qualitativeanalysisofthepartselectoral
            and qualitativeanalysisofthepartselectoral.no_parts_to_analyze
        ):
            if qualitativeanalysisofthepartselectoral.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qualitativeanalysisofthepartselectoral.score
        if qtd_items > 0:
            media = Decimal(soma / qtd_items)
        score = media
        if registeredpublicattendancenumber:
            score = registeredpublicattendancenumber.score + media
        return score

    # def _query_person_struture(self, kind=[]):
    #     return MovimentacaoPessoal.objects.filter(
    #         ~Q(movimentacaoposse__quadro__cargo__indicativo='M') &
    #         Q(
    #             movimentacaoposse__isnull=False,
    #             movimentacaoposse__quadro__cargo__tipo_lei_cargo__in=kind
    #         )
    #     ).filter(
    #         Q(
    #             movimentacaoposse__lotacoes__lotacao=self.execution_organ,
    #             movimentacaoposse__lotacoes__designacao=True
    #         ) &
    #         Q(
    #             Q(movimentacaoposse__lotacoes__data_vigencia_inicio__lte=self.inspection_date_initial) &
    #             Q(movimentacaoposse__lotacoes__data_vigencia_fim__gte=self.inspection_date_initial) |
    #             Q(movimentacaoposse__lotacoes__data_vigencia_fim__isnull=True)
    #         )
    #     )

    def _query_person_struture(self, kind=[]):
        return MovimentacaoPessoal.objects.filter(
            ~Q(movimentacaoposse__quadro__cargo__indicativo="M")
            & Q(movimentacaoposse__isnull=False, servidor__type_by_possession__in=kind)
        ).filter(
            Q(
                movimentacaoposse__lotacoes__lotacao=self.execution_organ,
                movimentacaoposse__lotacoes__designacao=True,
            )
            & Q(
                Q(
                    movimentacaoposse__lotacoes__data_vigencia_inicio__lte=self.inspection_date_initial
                )
                & Q(
                    movimentacaoposse__lotacoes__data_vigencia_fim__gte=self.inspection_date_initial
                )
                | Q(movimentacaoposse__lotacoes__data_vigencia_fim__isnull=True)
            )
        )

    def saveStructureEmployees(self):

        StructureEffectiveEmployees.objects.filter(inspection=self).delete()
        StructureCommissionedEmployees.objects.filter(inspection=self).delete()
        StructureExternalEmployees.objects.filter(inspection=self).delete()
        StructureExternalPeoples.objects.filter(inspection=self).delete()

        # EFE - SERVIDOR EFETIVO *
        # ECM - SERVIDOR EFETIVO E COMISSIONADO *
        # EFC - SERVIDOR EFETIVO COM FUNÇÃO CONFIANÇA *
        query_efetivo = self._query_person_struture(kind=["EFE", "ECM", "EFC"])

        for mp in (query_efetivo).distinct():
            structureeffectiveemployee = StructureEffectiveEmployees()
            structureeffectiveemployee.inspection = self
            structureeffectiveemployee.effective_employee = mp
            structureeffectiveemployee.save()

        # CMS - SERVIDOR COMISSIONADO
        # RCM - SERVIDOR REQUISITADO COMISSIONADO *
        # RFC - SERVIDOR REQUISITADO COM FUNÇÃO CONFIANÇA *
        query_comissao = self._query_person_struture(kind=["CMS", "RCM", "RFC"])

        for mp in (query_comissao).distinct():
            structurecommissionedemployee = StructureCommissionedEmployees()
            structurecommissionedemployee.inspection = self
            structurecommissionedemployee.commissioned_employee = mp
            structurecommissionedemployee.save()

        # REQ - SERVIDOR REQUISITADO *
        # CTR - SERVIDOR CONTRATADO
        # EST - ESTAGIÁRIO *
        # TCR - TERCEIRIZADO *
        # VOL - VOLUNTÁRIO *
        query_acordo = self._query_person_struture(
            kind=["REQ", "RCM", "RFC", "CTR", "EST", "TCR", "VOL"]
        )

        # FIXME: APÓS TESTE REMOVER
        # query_estagiario = MovimentacaoPessoal.objects.filter(
        #     Q(
        #         declaracaoatividade__isnull=False,
        #         declaracaoatividade__lotacao__in=[self.execution_organ]
        #     )
        # ).filter(
        #     ~Q(
        #         Q(declaracaoatividade__data_exercicio__gte=self.inspection_date_initial) |
        #         Q(declaracaoatividade__data_encerramento__lte=self.inspection_date_initial)
        #     )
        # )
        # for mp in (query_acordo | query_estagiario).distinct():
        for mp in query_acordo.distinct():
            structureexternalpeople = StructureExternalPeoples()
            structureexternalpeople.inspection = self
            structureexternalpeople.name = mp.servidor.pessoa_fisica.nome

            # mov = (getattr(mp, 'requestmove', None) or getattr(mp, 'movimentacaoposse', None))

            if hasattr(mp, "requestmove"):
                structureexternalpeople.function = mp.requestmove.description_possession
            elif mp.movimentacaoposse:
                mov = mp.movimentacaoposse
                structureexternalpeople.function = (
                    mov.quadro.cargo.nome if mov.quadro else mov.description_possession
                )

            structureexternalpeople.category = format_category_employee(
                kind=mp.servidor.categoria_cache
            )
            structureexternalpeople.personal_movement = mp
            structureexternalpeople.save()

    def saveAccumulations(self, refs):
        Accumulations.objects.filter(inspection=self).delete()
        lista = []
        accumulate = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ms = ServidorLotacao.objects.filter(
                Q(
                    Q(servidor=self.employee)
                    & Q(designacao=True)
                    & Q(~Q(lotacao=self.execution_organ) & ~Q(from_substitution=True))
                    & Q(
                        Q(data_vigencia_inicio__lte=d)
                        & Q(
                            Q(data_vigencia_fim__gte=d)
                            | Q(data_vigencia_fim__isnull=True)
                        )
                    )
                )
            ).order_by("data_vigencia_inicio")

            if ms:
                for s in ms:
                    if s.id not in lista:
                        lista.append(s.id)
                        accumulates = Accumulations()
                        accumulates.inspection = self
                        accumulates.accumulation = s
                        accumulates.save()
                        accumulate = True
        return accumulate

    def saveReplacements(self, refs):
        Replacements.objects.filter(inspection=self).delete()
        lista = []
        replace = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ms = (
                Replacement.objects.filter(servidor=self.employee)
                .filter(
                    Q(
                        Q(data_inicio__lte=d)
                        & Q(Q(data_fim__gte=d) | Q(data_fim__isnull=True))
                    )
                )
                .order_by("data_inicio")
            )
            if ms:
                for s in ms:
                    if s.id not in lista:
                        lista.append(s.id)
                        replacement = Replacements()
                        replacement.inspection = self
                        replacement.replacement = s
                        replacement.save()
                        replace = True
        return replace

    def saveAddress(self, refs):
        Address.objects.filter(inspection=self).delete()
        lista = []
        outside = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ct = AddressCif.objects.filter(
                member__employee__servidor=self.employee
            ).filter(
                Q(
                    Q(refperiod_address__start_date__lte=d)
                    & Q(refperiod_address__end_date__gte=d)
                    | Q(refperiod_address__end_date__isnull=True)
                )
            )
            if ct:
                for s in ct:
                    if s.ref_address.id not in lista:
                        lista.append(s.ref_address.id)
                        address = Address()
                        address.inspection = self
                        address.address = s
                        address.save()
                        if s.authorization_reside_outside:
                            outside = True
        return False if outside else True

    def saveAddressCirdir(self, refs):
        Address.objects.filter(inspection=self).delete()
        lista = []
        outside = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ct = AddressCirdir.objects.filter(
                controlinformation__employee=self.employee
            ).filter(updated_at__year__gte=d.year)
            for s in ct:
                if s.ref_address.id not in lista:
                    lista.append(s.ref_address.id)
                    address = Address()
                    address.inspection = self
                    address.address_cirdir = s
                    address.save()
                    if s.authorization_reside_outside:
                        outside = True
        return False if outside else True

    def saveTeaching(self, refs):
        Teaching.objects.filter(inspection=self).delete()
        lista = []
        teach = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ct = Docencia.objects.filter(
                member__employee__servidor=self.employee
            ).filter(
                Q(Q(start_date__lte=d) & Q(end_date__gte=d) | Q(end_date__isnull=True))
            )
            if ct:
                for s in ct:
                    if s.validade_excercises_teaching():
                        if s.id not in lista:
                            lista.append(s.id)
                            teaching = Teaching()
                            teaching.inspection = self
                            teaching.teaching = s
                            teaching.save()
                            teach = True
        return teach

    def saveTeachingCirdir(self, refs):
        Teaching.objects.filter(inspection=self).delete()
        lista = []
        teach = False
        for r in refs:
            d = datetime(r["year"], r["month"], 1)
            ct = TeachingCirdir.objects.filter(
                controlinformation__employee=self.employee
            ).filter(
                Q(Q(start_date__lte=d) & Q(end_date__gte=d) | Q(end_date__isnull=True))
            )
            for s in ct:
                if s.id not in lista and s.validate_exercises_teaching():
                    lista.append(s.id)
                    teaching = Teaching()
                    teaching.inspection = self
                    teaching.teaching_cirdir = s
                    teaching.save()
                    teach = True
        return teach

    def saveRegistrationPublicAttendance(self, refs):
        RegistrationPublicAttendance.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_registerpublicattendance", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            registrationpublicattendance = RegistrationPublicAttendance.objects.filter(
                inspection=self, year=r["year"]
            ).first()
            if registrationpublicattendance is None:
                registrationpublicattendance = RegistrationPublicAttendance()
                registrationpublicattendance.inspection = self
            registrationpublicattendance.year = r["year"]
            if r["month"] == 1:
                registrationpublicattendance.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                registrationpublicattendance.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                registrationpublicattendance.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                registrationpublicattendance.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                registrationpublicattendance.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                registrationpublicattendance.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                registrationpublicattendance.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                registrationpublicattendance.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                registrationpublicattendance.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                registrationpublicattendance.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                registrationpublicattendance.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                registrationpublicattendance.amount_december = (
                    register["total"] if register["total"] else 0
                )
            registrationpublicattendance.save()
        if (
            RegisteredPublicAttendanceNumber.objects.filter(inspection=self).exists()
            is False
        ):
            registeredpublicattendancenumber = RegisteredPublicAttendanceNumber()
            registeredpublicattendancenumber.inspection = self
        else:
            registeredpublicattendancenumber = (
                RegisteredPublicAttendanceNumber.objects.filter(inspection=self).first()
            )
        registeredpublicattendancenumber.save()

    def saveRegistrationCourtLawsuitReceived(self, refs):
        RegistrationCourtLawsuitReceived.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitreceived", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            registrationcourtlawsuitreceived = (
                RegistrationCourtLawsuitReceived.objects.filter(
                    inspection=self, year=r["year"]
                ).first()
            )
            if registrationcourtlawsuitreceived is None:
                registrationcourtlawsuitreceived = RegistrationCourtLawsuitReceived()
                registrationcourtlawsuitreceived.inspection = self
            registrationcourtlawsuitreceived.year = r["year"]
            if r["month"] == 1:
                registrationcourtlawsuitreceived.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                registrationcourtlawsuitreceived.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                registrationcourtlawsuitreceived.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                registrationcourtlawsuitreceived.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                registrationcourtlawsuitreceived.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                registrationcourtlawsuitreceived.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                registrationcourtlawsuitreceived.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                registrationcourtlawsuitreceived.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                registrationcourtlawsuitreceived.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                registrationcourtlawsuitreceived.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                registrationcourtlawsuitreceived.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                registrationcourtlawsuitreceived.amount_december = (
                    register["total"] if register["total"] else 0
                )
            registrationcourtlawsuitreceived.save()

    def saveRegistrationCourtLawsuitReturned(self, refs):
        RegistrationCourtLawsuitReturned.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitreturned", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            registrationcourtlawsuitreturned = (
                RegistrationCourtLawsuitReturned.objects.filter(
                    inspection=self, year=r["year"]
                ).first()
            )
            if registrationcourtlawsuitreturned is None:
                registrationcourtlawsuitreturned = RegistrationCourtLawsuitReturned()
                registrationcourtlawsuitreturned.inspection = self
            registrationcourtlawsuitreturned.year = r["year"]
            if r["month"] == 1:
                registrationcourtlawsuitreturned.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                registrationcourtlawsuitreturned.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                registrationcourtlawsuitreturned.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                registrationcourtlawsuitreturned.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                registrationcourtlawsuitreturned.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                registrationcourtlawsuitreturned.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                registrationcourtlawsuitreturned.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                registrationcourtlawsuitreturned.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                registrationcourtlawsuitreturned.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                registrationcourtlawsuitreturned.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                registrationcourtlawsuitreturned.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                registrationcourtlawsuitreturned.amount_december = (
                    register["total"] if register["total"] else 0
                )
            registrationcourtlawsuitreturned.save()

    def saveRegistrationCourtLawsuitElectoralReceived(self, refs):
        RegistrationCourtLawsuitElectoralReceived.objects.filter(
            inspection=self
        ).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitelectoralreceived", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            registrationcourtlawsuitelectoralreceived = (
                RegistrationCourtLawsuitElectoralReceived.objects.filter(
                    inspection=self, year=r["year"]
                ).first()
            )
            if registrationcourtlawsuitelectoralreceived is None:
                registrationcourtlawsuitelectoralreceived = (
                    RegistrationCourtLawsuitElectoralReceived()
                )
                registrationcourtlawsuitelectoralreceived.inspection = self
            registrationcourtlawsuitelectoralreceived.year = r["year"]
            if r["month"] == 1:
                registrationcourtlawsuitelectoralreceived.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                registrationcourtlawsuitelectoralreceived.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                registrationcourtlawsuitelectoralreceived.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                registrationcourtlawsuitelectoralreceived.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                registrationcourtlawsuitelectoralreceived.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                registrationcourtlawsuitelectoralreceived.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                registrationcourtlawsuitelectoralreceived.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                registrationcourtlawsuitelectoralreceived.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                registrationcourtlawsuitelectoralreceived.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                registrationcourtlawsuitelectoralreceived.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                registrationcourtlawsuitelectoralreceived.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                registrationcourtlawsuitelectoralreceived.amount_december = (
                    register["total"] if register["total"] else 0
                )
            registrationcourtlawsuitelectoralreceived.save()

    def saveRegistrationCourtLawsuitElectoralReturned(self, refs):
        RegistrationCourtLawsuitElectoralReturned.objects.filter(
            inspection=self
        ).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitelectoralreturned", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            registrationcourtlawsuitelectoralreturned = (
                RegistrationCourtLawsuitElectoralReturned.objects.filter(
                    inspection=self, year=r["year"]
                ).first()
            )
            if registrationcourtlawsuitelectoralreturned is None:
                registrationcourtlawsuitelectoralreturned = (
                    RegistrationCourtLawsuitElectoralReturned()
                )
                registrationcourtlawsuitelectoralreturned.inspection = self
            registrationcourtlawsuitelectoralreturned.year = r["year"]
            if r["month"] == 1:
                registrationcourtlawsuitelectoralreturned.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                registrationcourtlawsuitelectoralreturned.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                registrationcourtlawsuitelectoralreturned.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                registrationcourtlawsuitelectoralreturned.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                registrationcourtlawsuitelectoralreturned.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                registrationcourtlawsuitelectoralreturned.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                registrationcourtlawsuitelectoralreturned.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                registrationcourtlawsuitelectoralreturned.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                registrationcourtlawsuitelectoralreturned.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                registrationcourtlawsuitelectoralreturned.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                registrationcourtlawsuitelectoralreturned.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                registrationcourtlawsuitelectoralreturned.amount_december = (
                    register["total"] if register["total"] else 0
                )
            registrationcourtlawsuitelectoralreturned.save()

    def getDataOutCourtLawsuitCount(self, refs, var):
        lista = []
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get(var, 0))
        )
        activities = []
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                    for a in acts:
                        activities.append(a["pk"])
        return activities

    def saveDataOutCourtLawsuit(self, refs):
        OutCourtLawsuitCount.objects.filter(inspection=self).delete()
        ocs = OutCourtLawsuit.objects.filter(
            location=self.execution_organ,
            closed_by__isnull=True,
            removed_by__isnull=True,
            attached_lawsuit=None,
        )
        procedures_in_progress = ocs.count()
        procedures_in_arrears = 0
        for oc in ocs:
            if oc.deadline is not None and oc.deadline < 0:
                procedures_in_arrears = procedures_in_arrears + 1

        # Aguardnado implementacao de Classe em CERTIDAO DE JUDICIALIZACAO (e-EXT) para contagem das ACPs ACPIA
        # acp = Activity.objects.filter(pk__in=self.getDataOutCourtLawsuitCount(refs, 'var_number_of_public_civil_actions')).aggregate(total=Sum('amount_submitted'))
        public_civil_actions_in_the_last_year = 0  # acp['total'] if acp['total'] else 0
        # acpad = Activity.objects.filter(pk__in=self.getDataOutCourtLawsuitCount(refs, 'var_number_of_acp_admin_dishonesty')).aggregate(total=Sum('amount_submitted'))
        acp_administrative_dishonesty = 0  # acpad['total'] if acpad['total'] else 0

        ri = Activity.objects.filter(
            pk__in=self.getDataOutCourtLawsuitCount(
                refs, "var_number_of_recommendations_issued"
            )
        ).aggregate(total=Sum("amount_submitted"))
        recommendations_issued_in_the_last_year = ri["total"] if ri["total"] else 0
        tac = Activity.objects.filter(
            pk__in=self.getDataOutCourtLawsuitCount(
                refs, "var_number_of_conduct_adjustment_terms"
            )
        ).aggregate(total=Sum("amount_submitted"))
        conduct_adjustment_terms_in_the_last_year = tac["total"] if tac["total"] else 0
        apub = Activity.objects.filter(
            pk__in=self.getDataOutCourtLawsuitCount(
                refs, "var_number_of_public_audiences"
            )
        ).aggregate(total=Sum("amount_submitted"))
        public_audiences_in_the_last_year = apub["total"] if apub["total"] else 0
        pily = Activity.objects.filter(
            pk__in=self.getDataOutCourtLawsuitCount(
                refs, "var_number_of_procedures_instituted"
            )
        ).aggregate(total=Sum("amount_submitted"))
        procedures_instituted_in_the_last_year = pily["total"] if pily["total"] else 0
        pa = Activity.objects.filter(
            pk__in=self.getDataOutCourtLawsuitCount(
                refs, "var_number_of_procedures_archived"
            )
        ).aggregate(total=Sum("amount_submitted"))
        procedures_archived_in_the_last_year = pa["total"] if pa["total"] else 0
        outcourtlawsuitcount = OutCourtLawsuitCount.objects.filter(
            inspection=self
        ).first()
        if outcourtlawsuitcount is None:
            outcourtlawsuitcount = OutCourtLawsuitCount()
            outcourtlawsuitcount.inspection = self
        outcourtlawsuitcount.number_of_procedures_in_progress = procedures_in_progress
        outcourtlawsuitcount.number_of_procedures_in_arrears = procedures_in_arrears
        outcourtlawsuitcount.number_of_public_civil_actions_in_the_last_year = (
            public_civil_actions_in_the_last_year
        )
        outcourtlawsuitcount.number_of_acp_administrative_dishonesty = (
            acp_administrative_dishonesty
        )
        outcourtlawsuitcount.number_of_recommendations_issued_in_the_last_year = (
            recommendations_issued_in_the_last_year
        )
        outcourtlawsuitcount.number_of_conduct_adjustment_terms_in_the_last_year = (
            conduct_adjustment_terms_in_the_last_year
        )
        outcourtlawsuitcount.number_of_public_audiences_in_the_last_year = (
            public_audiences_in_the_last_year
        )
        outcourtlawsuitcount.number_of_procedures_instituted_in_the_last_year = (
            procedures_instituted_in_the_last_year
        )
        outcourtlawsuitcount.number_of_procedures_archived_in_the_last_year = (
            procedures_archived_in_the_last_year
        )
        outcourtlawsuitcount.save()

    def saveProceduralMovementReceived(self, refs):
        ProceduralMovementReceived.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitreceived", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            proceduralmovementreceived = ProceduralMovementReceived.objects.filter(
                inspection=self, year=r["year"]
            ).first()
            if proceduralmovementreceived is None:
                proceduralmovementreceived = ProceduralMovementReceived()
                proceduralmovementreceived.inspection = self
            proceduralmovementreceived.year = r["year"]
            if r["month"] == 1:
                proceduralmovementreceived.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                proceduralmovementreceived.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                proceduralmovementreceived.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                proceduralmovementreceived.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                proceduralmovementreceived.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                proceduralmovementreceived.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                proceduralmovementreceived.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                proceduralmovementreceived.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                proceduralmovementreceived.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                proceduralmovementreceived.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                proceduralmovementreceived.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                proceduralmovementreceived.amount_december = (
                    register["total"] if register["total"] else 0
                )
            proceduralmovementreceived.save()

    def saveProceduralMovementReturned(self, refs):
        ProceduralMovementReturned.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_courtlawsuitreturned", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            proceduralmovementreturned = ProceduralMovementReturned.objects.filter(
                inspection=self, year=r["year"]
            ).first()
            if proceduralmovementreturned is None:
                proceduralmovementreturned = ProceduralMovementReturned()
                proceduralmovementreturned.inspection = self
            proceduralmovementreturned.year = r["year"]
            if r["month"] == 1:
                proceduralmovementreturned.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                proceduralmovementreturned.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                proceduralmovementreturned.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                proceduralmovementreturned.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                proceduralmovementreturned.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                proceduralmovementreturned.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                proceduralmovementreturned.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                proceduralmovementreturned.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                proceduralmovementreturned.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                proceduralmovementreturned.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                proceduralmovementreturned.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                proceduralmovementreturned.amount_december = (
                    register["total"] if register["total"] else 0
                )
            proceduralmovementreturned.save()

    def saveProceduralMovementOutCourtLawsuit(self, refs):
        ProceduralMovementOutCourtLawsuit.objects.filter(inspection=self).delete()
        cfg = Configuration.get_or_create("corregedoria")
        links = ConfigLinkInspectionRAF.objects.filter(
            inspection_table=int(cfg.get("var_number_of_procedures_instituted", 0))
        )
        for r in refs:
            query = Activity.objects.filter(
                workerlocation__raf__month=r["month"],
                workerlocation__raf__year=r["year"],
                workerlocation__location=self.execution_organ,
            ).values("pk")
            activities = []
            for l in links:
                if l.raf_item:
                    acts = query.filter(item=l.raf_item, subitem=l.raf_subitem)
                else:
                    acts = query.filter(subitem=l.raf_subitem)
                for a in acts:
                    activities.append(a["pk"])
            register = Activity.objects.filter(pk__in=activities).aggregate(
                total=Sum("amount_submitted")
            )
            proceduralmovementoutcourtlawsuit = (
                ProceduralMovementOutCourtLawsuit.objects.filter(
                    inspection=self, year=r["year"]
                ).first()
            )
            if proceduralmovementoutcourtlawsuit is None:
                proceduralmovementoutcourtlawsuit = ProceduralMovementOutCourtLawsuit()
                proceduralmovementoutcourtlawsuit.inspection = self
            proceduralmovementoutcourtlawsuit.year = r["year"]
            if r["month"] == 1:
                proceduralmovementoutcourtlawsuit.amount_january = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 2:
                proceduralmovementoutcourtlawsuit.amount_february = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 3:
                proceduralmovementoutcourtlawsuit.amount_march = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 4:
                proceduralmovementoutcourtlawsuit.amount_april = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 5:
                proceduralmovementoutcourtlawsuit.amount_may = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 6:
                proceduralmovementoutcourtlawsuit.amount_june = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 7:
                proceduralmovementoutcourtlawsuit.amount_july = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 8:
                proceduralmovementoutcourtlawsuit.amount_august = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 9:
                proceduralmovementoutcourtlawsuit.amount_september = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 10:
                proceduralmovementoutcourtlawsuit.amount_october = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 11:
                proceduralmovementoutcourtlawsuit.amount_november = (
                    register["total"] if register["total"] else 0
                )
            if r["month"] == 12:
                proceduralmovementoutcourtlawsuit.amount_december = (
                    register["total"] if register["total"] else 0
                )
            proceduralmovementoutcourtlawsuit.save()

    def reloadData(self):
        if not self.has_signature:
            self.titular_employee = (
                True if self.employee == self.holder_employee else False
            )
            self.saveStructureEmployees()
            self.accumulates = self.saveAccumulations(self.getPeriodInspection(6))
            self.replacements = self.saveReplacements(self.getPeriodInspection(6))
            self.teaching = self.saveTeachingCirdir(self.getPeriodInspection(6))
            self.residence = self.saveAddressCirdir(self.getPeriodInspection(6))
            if self.execution_organ.instancia.pk == 1:
                self.saveRegistrationPublicAttendance(self.getPeriodInspection(6))
                self.saveRegistrationCourtLawsuitReceived(self.getPeriodInspection(6))
                self.saveRegistrationCourtLawsuitReturned(self.getPeriodInspection(6))
                self.saveRegistrationCourtLawsuitElectoralReceived(
                    self.getPeriodInspection(6)
                )
                self.saveRegistrationCourtLawsuitElectoralReturned(
                    self.getPeriodInspection(6)
                )
                self.saveDataOutCourtLawsuit(self.getPeriodInspection(12))
            if self.execution_organ.instancia.pk == 2:
                self.saveProceduralMovementReceived(self.getPeriodInspection(6))
                self.saveProceduralMovementReturned(self.getPeriodInspection(6))
                self.saveProceduralMovementOutCourtLawsuit(self.getPeriodInspection(6))
            self.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def reload_data_address(self):
        try:
            if self.has_signature:
                raise Exception("Inspeção/Correição já assinada, edição não permitida.")
            self.residence = self.saveAddressCirdir(self.getPeriodInspection(6))
            self.save()
        except Exception as e:
            raise e

    def reload_data_lawsuit(self):
        try:
            if not self.has_signature:
                if self.execution_organ.instancia.pk == 1:
                    self.saveRegistrationPublicAttendance(self.getPeriodInspection(6))
                    self.saveRegistrationCourtLawsuitReceived(
                        self.getPeriodInspection(6)
                    )
                    self.saveRegistrationCourtLawsuitReturned(
                        self.getPeriodInspection(6)
                    )
                    self.saveRegistrationCourtLawsuitElectoralReceived(
                        self.getPeriodInspection(6)
                    )
                    self.saveRegistrationCourtLawsuitElectoralReturned(
                        self.getPeriodInspection(6)
                    )
                    self.saveDataOutCourtLawsuit(self.getPeriodInspection(12))
                    self.save()

                if self.execution_organ.instancia.pk == 2:
                    self.saveProceduralMovementReceived(self.getPeriodInspection(6))
                    self.saveProceduralMovementReturned(self.getPeriodInspection(6))
                    self.saveProceduralMovementOutCourtLawsuit(
                        self.getPeriodInspection(6)
                    )
                    self.save()
            else:
                raise Exception("Inspeção/Correição já assinada, edição não permitida.")
        except Exception as e:
            raise e

    def reload_accumulations(self):
        try:
            if self.has_signature:
                raise Exception("Inspeção/Correição já assinada, edição não permitida.")
            self.accumulates = self.saveAccumulations(self.getPeriodInspection(6))
            self.replacements = self.saveReplacements(self.getPeriodInspection(6))
            self.save()
        except Exception as e:
            raise e

    def reload_data_employees(self):
        try:
            if self.has_signature:
                raise Exception("Inspeção/Correição já assinada, edição não permitida.")
            self.saveStructureEmployees()
        except Exception as e:
            raise e

    def save(self, *args, **kargs):
        if not self.has_signature:
            created = False
            if self.pk is None:
                created = True
            self.attendance = True
            self.list_months = self.getPeriodInspection(6)
            super(Inspection, self).save(*args, **kargs)
            if self.inspection_type == 1:
                self.titular_employee = (
                    True if self.employee == self.holder_employee else False
                )
                if created is True:
                    self.saveStructureEmployees()
                    self.accumulates = self.saveAccumulations(
                        self.getPeriodInspection(6)
                    )
                    self.replacements = self.saveReplacements(
                        self.getPeriodInspection(6)
                    )
                    self.teaching = self.saveTeachingCirdir(self.getPeriodInspection(6))
                    self.residence = self.saveAddressCirdir(self.getPeriodInspection(6))
                    if self.execution_organ.instancia.pk == 1:
                        self.saveRegistrationPublicAttendance(
                            self.getPeriodInspection(6)
                        )
                        self.saveRegistrationCourtLawsuitReceived(
                            self.getPeriodInspection(6)
                        )
                        self.saveRegistrationCourtLawsuitReturned(
                            self.getPeriodInspection(6)
                        )
                        self.saveRegistrationCourtLawsuitElectoralReceived(
                            self.getPeriodInspection(6)
                        )
                        self.saveRegistrationCourtLawsuitElectoralReturned(
                            self.getPeriodInspection(6)
                        )
                        self.saveDataOutCourtLawsuit(self.getPeriodInspection(12))
                    if self.execution_organ.instancia.pk == 2:
                        self.saveProceduralMovementReceived(self.getPeriodInspection(6))
                        self.saveProceduralMovementReturned(self.getPeriodInspection(6))
                        self.saveProceduralMovementOutCourtLawsuit(
                            self.getPeriodInspection(6)
                        )
                self.operability_score = self.calcOperabilityScore()
                super(Inspection, self).save(*args, **kargs)
            else:
                if created is True:
                    self.saveStructureEmployees()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def finalize(self):
        if self.signs.all().count() == 0:
            raise Exception(
                "Inspeção/Correição não assinada, finalização não permitida."
            )
        if self.finalized:
            raise Exception("Inspeção/Correição já finalizada.")
        self.finalized = True
        self.finalized_at = datetime.now()
        super(Inspection, self).save()

    def communication(self):
        if self.signs.all().count() == 0:
            raise Exception("Inspeção/Correição não assinada, envio não permitido.")
        self.communicated_organ_execution = True
        self.communicated_organ_execution_at = datetime.now()
        super(Inspection, self).save()

    def communication_cpjcsmp(self):
        if self.signs.all().count() == 0:
            raise Exception("Inspeção/Correição não assinada, envio não permitido.")
        self.communicated_cpjcsmp = True
        self.communicated_cpjcsmp_at = datetime.now()
        super(Inspection, self).save()

    def send_communication(self):
        employee_list = []

        if self.signs.all().count() == 0:
            raise Exception("Inspeção/Correição não assinada, remessa não permitida.")
        if self.finalized:
            raise Exception("Inspeção/Correição já finalizada.")

        if self.employee is None and self.inspection_type == 1:
            raise Exception(
                "Não é possível enviar a comomunicação, pois o destinatário não foi especificado."
            )
        elif self.employee:
            employee_list.append(self.employee)

        if (
            not MemberOrgan.objects.filter(inspection=self).exists()
            and self.inspection_type != 1
        ):
            raise Exception(
                "Órgão Auxiliar/Grupo Especial. Não é possível enviar a comunicação, pois o destinatário não foi especificado."
            )
        else:
            for m in MemberOrgan.objects.filter(inspection=self):
                if m.employee:
                    employee_list.append(m.employee)

        for employee in employee_list:
            loc_origin = Location.objects.get(pk=457)
            resp_origin = loc_origin.responsavel

            params_to_template = {
                "inspector_general": resp_origin,
                "execution_organ": self.execution_organ,
                "recipient": employee,
            }

            template = loader.get_template("inspection/communication.html")
            data = [template.render(params_to_template)]
            message = "".join(data).replace("\n", "")

            params_to_edoc = {
                "subject": "Relatório de Inspeção/Correição",
                "interested": resp_origin,
                "origin": loc_origin,
                "content": message,
                "person_destination": employee.pessoa_fisica.pk,
            }

            protocol = self._send_edoc_to(**params_to_edoc)
        self.communication()

    def delete(self, *args, **kargs):
        if self.signs.all().count() == 0:
            super(Inspection, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def notify_delay(self, new_message=None, deadline=None):
        if self.finalized:
            raise Exception("Inspeção/Correição já finalizada.")
        cfg = Configuration.get_or_create("corregedoria")

        subject = "Cumprimento das Recomendações de Inspeção"
        template = loader.get_template("recommendation/notification.html")

        loc_origin = Location.objects.get(pk=457)
        resp_origin = loc_origin.responsavel

        params_to_edoc = {
            "subject": subject,
            "interested": resp_origin,
            "origin": loc_origin,
            "content": None,
            "person_destination": None,
        }

        params_to_template = {
            "inspector_general": resp_origin,
            "execution_organ": self.execution_organ,
        }

        if new_message:
            params_to_template.update({"message": new_message})

        if self.execution_organ.responsavel:
            params_to_template.update({"recipient": self.execution_organ.responsavel})
            data = [template.render(params_to_template)]
            message = "".join(data).replace("\n", "")
            params_to_edoc.update(
                {
                    "content": message,
                    "person_destination": self.execution_organ.responsavel.pessoa_fisica.pk,
                }
            )
            protocol = self._send_edoc_to(**params_to_edoc)
            self._create_notification_history(protocol, deadline)
        elif self.execution_organ.employee_workplaces_responsible:
            for sl in self.execution_organ.employee_workplaces_responsible:
                params_to_template.update({"recipient": sl.servidor})
                data = [template.render(params_to_template)]
                message = "".join(data).replace("\n", "")
                params_to_edoc.update(
                    {
                        "content": message,
                        "person_destination": sl.servidor.pessoa_fisica.pk,
                    }
                )
                protocol = self._send_edoc_to(**params_to_edoc)
                self._create_notification_history(protocol, deadline)
        else:
            raise Exception(
                "Não foi possível enviar a notificação, pois não há responsável definido para {}".format(
                    self.execution_organ.nome
                )
            )

    def _send_edoc_to(self, subject, interested, origin, content, person_destination):
        protocol = Protocolo.docketing(
            subject=subject,
            document_type=TipoDocumento.objects.get(pk=94),
            interested=person_from_user(interested.user),
            home_court=origin,
            content=content,
        )
        current = Movimentacao.inbox_queryset().get(protocolo=protocol)
        current.do_send(
            person_destination=person_destination,
            employee_origin=employee_from_user(get_current_user()),
            physical=False,
            opinion=True,
        )
        return protocol

    def _create_notification_history(self, protocol, deadline):
        history = NotificationHistory()
        history.inspection = self
        history.protocol = protocol
        history.deadline = deadline
        history.save()
        return history

    def update_cache_rendered(self):
        """atualiza cache renderizado do conteudo"""
        content = self._renderer_document if self.has_signature else None
        self.__class__.objects.filter(pk=self.pk).update(cache_rendered=content)

    def get_accumulation_execution_organ(self):
        return self.accumulation.filter(
            accumulation__lotacao__executionorgan__isnull=False
        )

    def get_accumulation_others_organs(self):
        return self.accumulation.filter(
            accumulation__lotacao__executionorgan__isnull=True
        )

    def get_replacement(self):
        return self.replacement.filter()

    def has_accumulation_or_replacement(self):
        return (
            self.get_accumulation_execution_organ().exists()
            or self.get_replacement().exists()
        )


class Accumulations(AuditTimestampModel):
    """
    Lista de substituicoes do membro inspecionado no periodo da inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="accumulation", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    accumulation = models.ForeignKey(
        ServidorLotacao, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Lista de substituições do membro inspecionado no período da inspeção."
        )

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Accumulations, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Accumulations, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Replacements(AuditTimestampModel):
    """
    Lista de substituicoes do membro inspecionado no periodo da inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="replacement", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    replacement = models.ForeignKey(
        Replacement, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Lista de substituições do membro inspecionado no período da inspeção."
        )

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Replacements, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Replacements, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Address(AuditTimestampModel):
    """
    Lista de enderecos do membro inspecionado no periodo da inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="addresses", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    address = models.ForeignKey(
        AddressCif, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    address_cirdir = models.ForeignKey(
        AddressCirdir, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Lista de endereços do membro inspecionado no período da inspeção."
        )

    @property
    def get_address(self):
        return self.address_cirdir if self.address is None else self.address

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Address, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Address, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Teaching(AuditTimestampModel):
    """
    Lista de docencias do membro inspecionado no periodo da inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="teachings", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    teaching = models.ForeignKey(
        Docencia, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    teaching_cirdir = models.ForeignKey(
        TeachingCirdir,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Lista de docências do membro inspecionado no período da inspeção."
        )

    @property
    def get_teaching(self):
        return self.teaching_cirdir if self.teaching is None else self.teaching

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Teaching, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Teaching, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ExecutionOrganManagement(AuditTimestampModel):
    """
    Gestao do Orgao de Execucao

    ORGANIZATION values:
        1 - Não informado
        2 - Adequada
        3 - Regular
        4 - Inadequada
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    organization = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "ORGANIZATION"),
        verbose_name="Organização",
        default=1,
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Gestão do Órgão de Execução"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ExecutionOrganManagement, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ExecutionOrganManagement, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class BaseInspection(AuditTimestampModel):
    """
    RECORD_TYPE values:
        1 - Não informado
        2 - Informatizado
        3 - Livro Convencional
        4 - Fichas
        5 - Outros
        6 - Não possui
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    record_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "RECORD_TYPE"),
        verbose_name="Tipo de Registro",
        default=1,
    )
    apps = models.CharField(max_length=100, null=True, blank=True)
    others = models.CharField(max_length=100, null=True, blank=True)
    opening_date = models.DateField(null=True, blank=True)
    has_openind_term = models.BooleanField(default=True, null=True, blank=True)
    has_numeration = models.BooleanField(default=True, null=True, blank=True)
    has_signed_sheets = models.BooleanField(default=True, null=True, blank=True)
    ordered = models.BooleanField(default=True, null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class PublicAttendance(BaseInspection):
    """
    Atendimento ao Publico
    """

    class Meta:
        verbose_name = "Atendimento ao Público"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PublicAttendance, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PublicAttendance, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class MonthlyRecords(AuditTimestampModel):
    """
    Registros mensais
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    year = models.SmallIntegerField()
    amount_january = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_february = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_march = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_april = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_may = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_june = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_july = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_august = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_september = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_october = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_november = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    amount_december = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_january = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_february = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_march = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_april = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_may = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_june = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_july = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_august = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_september = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_october = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_november = models.SmallIntegerField(
        null=True,
        blank=True,
    )
    raf_amount_december = models.SmallIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def sum_amount(self):
        sem1 = (
            (self.amount_january if self.amount_january else 0)
            + (self.amount_february if self.amount_february else 0)
            + (self.amount_march if self.amount_march else 0)
            + (self.amount_april if self.amount_april else 0)
            + (self.amount_may if self.amount_may else 0)
            + (self.amount_june if self.amount_june else 0)
        )
        sem2 = (
            (self.amount_july if self.amount_july else 0)
            + (self.amount_august if self.amount_august else 0)
            + (self.amount_september if self.amount_september else 0)
            + (self.amount_october if self.amount_october else 0)
            + (self.amount_november if self.amount_november else 0)
            + (self.amount_december if self.amount_december else 0)
        )
        return sem1 + sem2


class ProceduralMovement(AuditTimestampModel):
    """
    Movimentacao processual da Procuradoria
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "MOviemntação processual da Procuradoria"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovement, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovement, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProceduralMovementReceived(MonthlyRecords):
    """
    Registro de Processos Judiciais Recebidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Recebidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementReceived, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementReceived, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProceduralMovementReturned(MonthlyRecords):
    """
    Registro de Processos Judiciais Recebidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Recebidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementReturned, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementReturned, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProceduralMovementOutCourtLawsuit(MonthlyRecords):
    """
    Registro de Processos Judiciais Recebidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Recebidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementOutCourtLawsuit, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProceduralMovementOutCourtLawsuit, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegistrationPublicAttendance(MonthlyRecords):
    """
    Registro de Atendimento ao Publico
    """

    class Meta:
        verbose_name = "Atendimento ao Público"

    def value_month(self, rpa, month):
        v = {
            1: rpa.amount_january,
            2: rpa.amount_february,
            3: rpa.amount_march,
            4: rpa.amount_april,
            5: rpa.amount_may,
            6: rpa.amount_june,
            7: rpa.amount_july,
            8: rpa.amount_august,
            9: rpa.amount_september,
            10: rpa.amount_october,
            11: rpa.amount_november,
            12: rpa.amount_december,
        }
        return v.get(month)

    def average(self):
        items = []
        for y in RegistrationPublicAttendance.objects.filter(
            inspection=self.inspection
        ):
            for x in range(1, 13):
                n = self.value_month(y, x)
                if n != None and n >= 0:
                    items.append(n)
        s = Decimal(0)
        for i in items:
            s = s + i
        avg = s / len(items)
        return avg

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationPublicAttendance, self).save(*args, **kargs)
            if RegisteredPublicAttendanceNumber.objects.filter(
                inspection=self.inspection
            ).exists():
                rpan = RegisteredPublicAttendanceNumber.objects.filter(
                    inspection=self.inspection
                ).first()
            else:
                rpan = RegisteredPublicAttendanceNumber()
                rpan.inspection = self.inspection
            rpan.average = self.average()
            rpan.save()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            rpan = RegisteredPublicAttendanceNumber.objects.filter(
                inspection=self.inspection
            ).first()
            super(RegistrationPublicAttendance, self).delete(*args, **kargs)
            if RegistrationPublicAttendance.objects.filter(
                inspection=self.inspection
            ).exists():
                rpan.average = self.average()
                rpan.save()
            else:
                rpan.delete()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class OutCourtLawsuitControl(BaseInspection):
    """
    Controle de Procedimentos Extrajudiciais
    """

    class Meta:
        verbose_name = "Controle de Procedimentos Extrajudiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitControl, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitControl, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class BookOfRegisterLawsuitControl(AuditTimestampModel):
    """
    Controle de Registro dos Procedimentos Extrajudiciais
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    book = models.CharField(max_length=100)
    opening_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True


class BookOfRegisterOutCourtLawsuitControl(BookOfRegisterLawsuitControl):
    """
    Controle de Registro dos Procedimentos Extrajudiciais
    """

    class Meta:
        verbose_name = "Controle de Registro dos Procedimentos Extrajudiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(BookOfRegisterOutCourtLawsuitControl, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(BookOfRegisterOutCourtLawsuitControl, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class CourtLawsuitControl(BaseInspection):
    """
    Controle de Procedimentos Judiciais
    """

    class Meta:
        verbose_name = "Controle de Procedimentos Judiciais"


class BookOfRegisterCourtLawsuitControl(BookOfRegisterLawsuitControl):
    """
    Controle de Registro dos Procedimentos Judiciais
    """

    class Meta:
        verbose_name = "Controle de Registro dos Procedimentos Judiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(BookOfRegisterCourtLawsuitControl, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(BookOfRegisterCourtLawsuitControl, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class CourtLawsuitCount(AuditTimestampModel):
    """
    Quantidade de Processos Judiciais
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    number_of_processes_pending_citation_urgent = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_processes_pending_citation = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_processes_pending_science = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    processes_with_open_deadline = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    expired_deadline_the_last_30_days = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    expired_deadline_more_than_30_days_ago = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    expired_deadline_in_the_period_of_inspection = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Quantidade de Processos Judiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(CourtLawsuitCount, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(CourtLawsuitCount, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegistrationCourtLawsuitReceived(MonthlyRecords):
    """
    Registro de Processos Judiciais Recebidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Recebidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitReceived, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitReceived, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegistrationCourtLawsuitReturned(MonthlyRecords):
    """
    Registro de Processos Judiciais Devolvidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Devolvidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitReturned, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitReturned, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class OutCourtLawsuitElectoralCount(AuditTimestampModel):
    """
    Quantidade de Processos Extrajudiciais Eleitorais
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    number_of_procedures_in_progress = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_procedures_in_arrears = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    correctly_registered_procedures = models.BooleanField(
        default=True, null=True, blank=True
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Quantidade de Processos Extrajudiciais Eleitorais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitElectoralCount, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitElectoralCount, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegistrationCourtLawsuitElectoralReceived(MonthlyRecords):
    """
    Registro de Processos Judiciais Eleitorais Recebidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Eleitorais Recebidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitElectoralReceived, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitElectoralReceived, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegistrationCourtLawsuitElectoralReturned(MonthlyRecords):
    """
    Registro de Processos Judiciais Eleitorais Devolvidos
    """

    class Meta:
        verbose_name = "Registro de Processos Judiciais Eleitorais Devolvidos"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitElectoralReturned, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegistrationCourtLawsuitElectoralReturned, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class OutCourtLawsuitCount(AuditTimestampModel):
    """
    Quantidade de Processos Extrajudiciais
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    number_of_procedures_in_progress = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_procedures_in_arrears = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    correctly_registered_procedures = models.BooleanField(
        default=True, null=True, blank=True
    )
    number_of_public_civil_actions_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_acp_administrative_dishonesty = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_recommendations_issued_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_conduct_adjustment_terms_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_public_audiences_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_procedures_instituted_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    number_of_procedures_archived_in_the_last_year = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Quantidade de Processos Extrajudiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitCount, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OutCourtLawsuitCount, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AnalysisPerformanceInAudiences(AuditTimestampModel):
    """
    Analise da Atuacao nas Audiencias
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    processes_analyzed_in_the_previous_inspection = models.BooleanField(
        null=True, blank=True
    )
    survey_in_randomly_chosen_processes = models.BooleanField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Análise da Atuação nas Audiências"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AnalysisPerformanceInAudiences, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AnalysisPerformanceInAudiences, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProcessesForAnalysisPerformanceInAudiences(AuditTimestampModel):
    """
    Analise da Atuacao nas Audiencias

    ACTION_TYPE values:
        1 - Não informado
        2 - Acao Civil Publica
        3 - Acao Penal
        4 - Acao de Alimentos
        5 - Acao de Adocao
        6 - etc (necessario levar com na corregedoria a lista completa (ou mais completa possivel))

    AUDIENCE_TYPE values:
        1 - Não informado
        2 - Conciacao
        3 - Preliminar
        4 - Instrucao e julgamento
        5 - etc (necessario levar com na corregedoria a lista completa (ou mais completa possivel))
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action_type = models.ForeignKey(
        LegalClass, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action_number = models.CharField(max_length=100, null=True, blank=True)
    audience_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "AUDIENCE_TYPE"),
        verbose_name="Tipo de Audiência",
        default=1,
    )
    intimation = models.BooleanField(default=True)
    presence = models.BooleanField(default=True)
    questions = models.BooleanField(default=True)
    oral_manifestation = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Análise da Atuação nas Audiências"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcessesForAnalysisPerformanceInAudiences, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcessesForAnalysisPerformanceInAudiences, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AnalysisPerformanceInPlenarySessionOfTheJury(AuditTimestampModel):
    """
    Analise da Atuacao nas Audiencias
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    analysis = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Análise da Atuação nas Audiências"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AnalysisPerformanceInPlenarySessionOfTheJury, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AnalysisPerformanceInPlenarySessionOfTheJury, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureEffectiveEmployees(AuditTimestampModel):
    """
    Descricao da Estrutura do Orgao Inspecionado - Servidores Efetivos
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    effective_employee = models.ForeignKey(
        MovimentacaoPessoal, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Descrição da Estrutura do Órgão Inspecionado - Servidores Efetivos"
        )

    def get_employee_possition(self):
        if self.effective_employee.servidor.posses.exists():
            return (
                self.effective_employee.servidor.posses.order_by("data_exercicio")
                .last()
                .quadro.cargo
            )
        else:
            return self.effective_employee.movimentacaoposse.quadro.cargo

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureEffectiveEmployees, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureEffectiveEmployees, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureCommissionedEmployees(AuditTimestampModel):
    """
    Descricao da Estrutura do Orgao Inspecionado - Servidores Comissionados
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    commissioned_employee = models.ForeignKey(
        MovimentacaoPessoal, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Descrição da Estrutura do Órgão Inspecionado - Servidores Comissionados"
        )

    def get_employee_possition(self):
        if self.commissioned_employee.servidor.posses.exists():
            return (
                self.commissioned_employee.servidor.posses.order_by("data_exercicio")
                .last()
                .quadro.cargo
            )
        else:
            return self.commissioned_employee.movimentacaoposse.quadro.cargo

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureCommissionedEmployees, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureCommissionedEmployees, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureExternalEmployees(AuditTimestampModel):
    """
    Descricao da Estrutura do Orgao Inspecionado - Servidores Externos
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    external_employee = models.ForeignKey(
        MovimentacaoPessoal, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Descrição da Estrutura do Órgão Inspecionado - Servidores Externos"
        )

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureExternalEmployees, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureExternalEmployees, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureExternalPeoples(AuditTimestampModel):
    """
    Registro de Pessoal Externo do Orgao Inspecionado, nao cadastrado no Athenas
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    name = models.CharField(max_length=300)
    function = models.CharField(max_length=300, null=True, blank=True)
    category = models.CharField(max_length=300, null=True, blank=True)
    personal_movement = models.ForeignKey(
        MovimentacaoPessoal,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Registro de Pessoal Externo do Orgão Inspecionado, não cadastrado no Athenas"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureExternalPeoples, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureExternalPeoples, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureDeficiency(AuditTimestampModel):
    """
    Descricao da Estrutura do Orgao Inspecionado - Deficiencias
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    deficiency = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Descrição da Estrutura do Órgão Inspecionado - Deficiencias"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureDeficiency, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureDeficiency, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class RegisteredPublicAttendanceNumber(AuditTimestampModel):
    """
    Calculo da media de atendimentos por mes
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    score_table = models.IntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("corregedoria", "SCORE_TABLE"),
        verbose_name="Tabela de Cálculo",
        default=1,
    )
    average = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    score = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Cálculo da média do atendimentos por mês"

    def getScoreValue(self):
        ret = 0
        cfg = Configuration.get_or_create("corregedoria")
        scoretable = ConfigScoreTable.objects.filter(
            score_table=int(cfg.get("var_public_attendance", 0)), active=True
        ).first()
        if scoretable:
            band = (
                BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=self.average,
                )
                .filter(Q(Q(end_value__gte=self.average) | Q(end_value__isnull=True)))
                .first()
            )
            if band:
                ret = band.score
        return ret

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.score = self.getScoreValue()
            super(RegisteredPublicAttendanceNumber, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(RegisteredPublicAttendanceNumber, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class QualitativeAnalysisOfTheParts(AuditTimestampModel):
    """
    Analise qualitativa das pecas
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    applicable = models.BooleanField(default=False, null=True, blank=True)
    no_parts_to_analyze = models.BooleanField(default=False, null=True, blank=True)
    score = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        abstract = True
        verbose_name = "Análise qualitativa das peças"


class ProcForQualAnalysisOfTheParts(AuditTimestampModel):
    """
    Processos para analise qualitativa das pecas
    """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action_type = models.ForeignKey(
        LegalClass, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    action_number = models.CharField(max_length=100, null=True, blank=True)
    part_type = models.ForeignKey(
        LegalMoviment, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    report = models.CharField(max_length=2000, null=True, blank=True)
    report_score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    basis = models.CharField(max_length=2000, null=True, blank=True)
    basis_score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    proof = models.CharField(max_length=2000, null=True, blank=True)
    proof_score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    convincily = models.CharField(max_length=2000, null=True, blank=True)
    convincily_score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    redaction = models.CharField(max_length=2000, null=True, blank=True)
    redaction_score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    score = models.DecimalField(
        null=True, blank=True, max_digits=4, decimal_places=2, default=0
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = "Processos para análise qualitativa das peças"

    def calcScore(self):
        self.score = (
            (self.report_score if self.report_score else 0)
            + (self.basis_score if self.basis_score else 0)
            + (self.proof_score if self.proof_score else 0)
            + (self.convincily_score if self.convincily_score else 0)
            + (self.redaction_score if self.redaction_score else 0)
        )


class ProcForQualAnalysisOfThePartsProcuratorate(ProcForQualAnalysisOfTheParts):
    """
    Processos para Analise qualitativa das pecas de Procuradorias
    """

    class Meta:
        verbose_name = "Processos para Análise qualitativa das peças de Procuradorias"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.calcScore()
            super(ProcForQualAnalysisOfThePartsProcuratorate, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcForQualAnalysisOfThePartsProcuratorate, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class QualitativeAnalysisOfThePartsCivilCourtLawsuit(QualitativeAnalysisOfTheParts):
    """
    Analise qualitativa das pecas de Processos Judiciais Civeis
    """

    class Meta:
        verbose_name = "Análise qualitativa das peças de Processos Judiciais Cíveis"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsCivilCourtLawsuit, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsCivilCourtLawsuit, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProcForQualAnalysisOfThePartsCivilCourtLawsuit(ProcForQualAnalysisOfTheParts):
    """
    Processos para Analise qualitativa das pecas de Processos Judiciais Civeis
    """

    class Meta:
        verbose_name = (
            "Processos para Análise qualitativa das peças de Processos Judiciais Cíveis"
        )

    def update_avg(self):
        avg = ProcForQualAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).aggregate(Avg("score"))
        qapccl = QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        if qapccl is None:
            qapccl = QualitativeAnalysisOfThePartsCivilCourtLawsuit()
            qapccl.inspection = self.inspection
        qapccl.applicable = True
        qapccl.no_parts_to_analyze = True
        qapccl.score = avg["score__avg"] if avg["score__avg"] else 0
        qapccl.save()

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.calcScore()
            super(ProcForQualAnalysisOfThePartsCivilCourtLawsuit, self).save(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcForQualAnalysisOfThePartsCivilCourtLawsuit, self).delete(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class QualitativeAnalysisOfThePartsCriminalCourtLawsuit(QualitativeAnalysisOfTheParts):
    """
    Analise qualitativa das pecas de Processos Judiciais Criminais
    """

    class Meta:
        verbose_name = "Análise qualitativa das peças de Processos Judiciais Criminais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsCriminalCourtLawsuit, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsCriminalCourtLawsuit, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProcForQualAnalysisOfThePartsCriminalCourtLawsuit(ProcForQualAnalysisOfTheParts):
    """
    Processos para Analise qualitativa das pecas de Processos Judiciais Criminais
    """

    class Meta:
        verbose_name = "Processos para Análise qualitativa das peças de Processos Judiciais Criminais"

    def update_avg(self):
        avg = ProcForQualAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).aggregate(Avg("score"))
        qapcrcl = QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        if qapcrcl is None:
            qapcrcl = QualitativeAnalysisOfThePartsCriminalCourtLawsuit()
            qapcrcl.inspection = self.inspection
        qapcrcl.applicable = True
        qapcrcl.no_parts_to_analyze = True
        qapcrcl.score = avg["score__avg"] if avg["score__avg"] else 0
        qapcrcl.save()

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.calcScore()
            super(ProcForQualAnalysisOfThePartsCriminalCourtLawsuit, self).save(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcForQualAnalysisOfThePartsCriminalCourtLawsuit, self).delete(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class QualitativeAnalysisOfThePartsOutCourtLawsuit(QualitativeAnalysisOfTheParts):
    """
    Analise qualitativa das pecas de Procedimentos Extrajudiciais
    """

    class Meta:
        verbose_name = "Análise qualitativa das peças de Procedimentos Extrajudiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsOutCourtLawsuit, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsOutCourtLawsuit, self).delete(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProcForQualAnalysisOfThePartsOutCourtLawsuit(ProcForQualAnalysisOfTheParts):
    """
    Processos para Analise qualitativa das pecas de Procedimentos Extrajudiciais
    """

    class Meta:
        verbose_name = "Processos para Análise qualitativa das peças de Procedimentos Extrajudiciais"

    def update_avg(self):
        avg = ProcForQualAnalysisOfThePartsOutCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).aggregate(Avg("score"))
        qapocl = QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        if qapocl is None:
            qapocl = QualitativeAnalysisOfThePartsOutCourtLawsuit()
            qapocl.inspection = self.inspection
        qapocl.applicable = True
        qapocl.no_parts_to_analyze = True
        qapocl.score = avg["score__avg"] if avg["score__avg"] else 0
        qapocl.save()

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.calcScore()
            super(ProcForQualAnalysisOfThePartsOutCourtLawsuit, self).save(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcForQualAnalysisOfThePartsOutCourtLawsuit, self).delete(
                *args, **kargs
            )
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class QualitativeAnalysisOfThePartsElectoral(QualitativeAnalysisOfTheParts):
    """
    Analise qualitativa das pecas de Processos Eleitorais
    """

    class Meta:
        verbose_name = "Análise qualitativa das peças de Processos Eleitorais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsElectoral, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(QualitativeAnalysisOfThePartsElectoral, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ProcForQualAnalysisOfThePartsElectoral(ProcForQualAnalysisOfTheParts):
    """
    Processos para Analise qualitativa das pecas de Processos Eleitorais
    """

    class Meta:
        verbose_name = (
            "Prorcessos para Análise qualitativa das peças de Processos Eleitorais"
        )

    def update_avg(self):
        avg = ProcForQualAnalysisOfThePartsElectoral.objects.filter(
            inspection=self.inspection
        ).aggregate(Avg("score"))
        qape = QualitativeAnalysisOfThePartsElectoral.objects.filter(
            inspection=self.inspection
        ).first()
        if qape is None:
            qape = QualitativeAnalysisOfThePartsElectoral()
            qape.inspection = self.inspection
        qape.applicable = True
        qape.no_parts_to_analyze = True
        qape.score = avg["score__avg"] if avg["score__avg"] else 0
        qape.save()

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            self.calcScore()
            super(ProcForQualAnalysisOfThePartsElectoral, self).save(*args, **kargs)
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ProcForQualAnalysisOfThePartsElectoral, self).delete(*args, **kargs)
            self.update_avg()
            self.inspection.save()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Promptness(AuditTimestampModel):
    """
    Avaliacao de Presteza
    """

    score_table = models.IntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("corregedoria", "SCORE_TABLE"),
        verbose_name="Tabela de Cálculo",
        default=2,
    )
    percentual = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    score = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True
        verbose_name = "Avaliação de Presteza"


class PromptnessCourtLawsuit(Promptness):
    """
    Avaliacao de Presteza em feitos Judiciais
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Avaliacao de Presteza em feitos Judiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessCourtLawsuit, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessCourtLawsuit, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class PromptnessOutCourtLawsuit(Promptness):
    """
    Avaliacao de Presteza em feitos Extrajudiciais
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Avaliacao de Presteza em feitos Extrajudiciais"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessOutCourtLawsuit, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessOutCourtLawsuit, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class PromptnessUpperManagement(Promptness):
    """
    Avaliacao de Presteza no atendimento as determinacoes da Administracao Superior e da Ouvidoria
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Avaliacao de Presteza as determinações da Administração Superior e da Ouvidoria"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessUpperManagement, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(PromptnessUpperManagement, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class GeneralObservations(AuditTimestampModel):
    """
    Observacoes gerais na inspecao
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Observações gerais na inspeção"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(GeneralObservations, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(GeneralObservations, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Recommendations(AuditTimestampModel):
    """
    Recomendacoes na inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="recommendations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    recommendation = models.TextField(null=True, blank=True)
    waiting_response = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)
    deadline_origin = models.DateField(null=True, blank=True)
    finalized_at = models.DateField(null=True, blank=True)
    finalized = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]
        verbose_name = "Recomendações gerais na inspeção"

    @property
    def rendered(self):
        tpl = loader.get_template("recommendation/recommendation.html")
        return tpl.render(
            {
                "recommendation": self,
                "delayoftime": DeadlineRecommendation.objects.filter(
                    recommendation=self, extension=True
                ),
                "response": DeadlineRecommendation.objects.filter(
                    recommendation=self
                ).filter(~Q(extension=True)),
            }
        )

    @property
    def last_deadlinerecommendation(self):
        return self.deadlines.last()

    @property
    def atual_deadline(self):
        return (
            self.last_deadlinerecommendation.deadline
            if self.last_deadlinerecommendation
            and self.last_deadlinerecommendation.deadline
            and self.last_deadlinerecommendation.signdecision_at
            else self.deadline
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.atual_deadline and self.finalized is not True:
            if self.atual_deadline >= datetime.now().date():
                item = {
                    "title": "No prazo ({})".format(
                        self.atual_deadline.strftime("%d/%m/%Y")
                    ),
                    "iconCls": "icon-judicial icon-ejud-outlawcortsuit-have-time",
                }
            elif self.waiting_response:
                item = {
                    "title": "Fora do prazo ({})".format(
                        self.atual_deadline.strftime("%d/%m/%Y")
                    ),
                    "iconCls": "icon-judicial icon-ejud-outlawcortsuit-not-have-time",
                }
            rst.append(item)
        if self.finalized:
            item = {
                "title": "Finalizado",
                "iconCls": "icon-judicial icon-ejud-read-only",
            }
            rst.append(item)
        if self.last_deadlinerecommendation:
            # tipo
            if self.last_deadlinerecommendation.extension is True:
                msg = "Pedido de Dilação de Prazo"
                icon = "icon-core icon-core-calendar-plus"
            else:
                msg = "Informação de cumprimento"
                icon = "icon-judicial icon-ejud-triage-effectivate"
            if self.finalized is not True:
                # verificar se esta em edicao
                if self.last_deadlinerecommendation.sent is not True:
                    item = {
                        "title": msg + " - Em edição",
                        "iconCls": "icon-judicial icon-ejud-edition-mode",
                    }
                # verificar se resposta/pedido de dilacao foi enviado
                if self.last_deadlinerecommendation.sent is True:
                    item = {"title": msg + " - Enviada para análise", "iconCls": icon}
                if self.last_deadlinerecommendation.signdecision_by:
                    item = {
                        "title": msg + " - Decisão enviada.",
                        "iconCls": "icon-core icon-core-success",
                    }
                rst.append(item)
        # verificar se foi respondido
        return rst

    def finalize(self, *args, **kargs):
        super(Recommendations, self).save(*args, **kargs)

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Recommendations, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Recommendations, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class DeadlineRecommendation(AuditTimestampModel):
    """
    Recomendacoes na inspecao
    """

    recommendation = models.ForeignKey(
        Recommendations, related_name="deadlines", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    sent = models.BooleanField(default=False)
    extension = models.BooleanField(default=False)
    response = models.TextField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    decision = models.TextField(null=True, blank=True)
    decision_at = models.DateField(null=True, blank=True)
    signdecision_by = models.ForeignKey(
        User, null=True, blank=True, related_name="sign_by", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    signdecision_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Recomendações gerais na inspeção"

    @property
    def sent_by(self):
        ret = Employee.objects.filter(user=self.created_by).first()
        return ret.pessoa_fisica.nome

    def save(self, *args, **kargs):
        super(DeadlineRecommendation, self).save(*args, **kargs)
        notifications = NotificationHistory.objects.filter(
            inspection=self.recommendation.inspection, created_at__lt=self.created_at
        ).exclude(responded=True)
        for notification in notifications:
            notification.responded = True
            notification.save()


class DeadlineRecommendationAttachments(AuditTimestampModel):
    """
    Arquivos anexados na solicitacao de dilacao de prazo
    """

    inspection = models.ForeignKey(
        Inspection, default=0, related_name="arquivos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="deadline_file",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Arquivo anexados na solicitação de dilação de prazo e outros"

    def save(self, *args, **kargs):
        super(DeadlineRecommendationAttachments, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        super(DeadlineRecommendationAttachments, self).delete(*args, **kargs)


class Attachments(AuditTimestampModel):
    """
    Arquivos anexados na inspecao
    """

    inspection = models.ForeignKey(
        Inspection, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    area = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "AREA"),
        verbose_name="ÁREA",
        default=1,
    )
    attachment_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "ATTACHMENT_TYPE"),
        verbose_name="TIPO DE ANEXO",
        default=1,
    )
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="inspection_file",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Arquivo anexados na inspeção"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Attachments, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Attachments, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class HarmedCalculation(AuditTimestampModel):
    """
    Informacao sobre PREJUIZO para calculo da nota final
    """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    harmedcalculation = models.BooleanField(default=False, null=True, blank=True)
    justification = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Informação sobre PREJUÍZO para cálculo da Nota Final"

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(HarmedCalculation, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    def delete(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(HarmedCalculation, self).delete(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Sign(AuditTimestampModel):
    """
    Assinaturas do Promotor-corregedor e do Corregedor-geral
    """

    inspection = models.ForeignKey(
        Inspection, related_name="signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Employee,
        related_name="employee_signs",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    dispatch = models.TextField(null=True, blank=True)
    profile = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "PROFILE"),
        verbose_name="TIPO",
        default=1,
    )

    class Meta:
        verbose_name = "Assinaturas do Promotor-corregedor e do Corregedor-geral"

    @classmethod
    def remove_sign(cls, inspection, profile, employee):
        try:
            sign = cls.objects.filter(
                inspection__pk=inspection, profile=profile, employee=employee
            ).first()
            inspection = Inspection.objects.get(pk=inspection)
            sign.delete()
            inspection.update_cache_rendered()
        except Exception as e:
            raise e

    def save(self, *args, **kargs):
        if (
            self.inspection.signs.all().count()
            < self.inspection.inspector_prosecutors.all().count() + 1
        ):
            super(Sign, self).save(*args, **kargs)
            self.inspection.update_cache_rendered()
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class NotificationHistory(AuditTimestampModel):
    """
    Historio de notificacoes por atraso.
    """

    inspection = models.ForeignKey(
        Inspection, related_name="notificationhistory", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    protocol = models.ForeignKey(
        Protocolo, related_name="notificationhistory", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    deadline = models.DateField(null=True, blank=True)
    responded = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Histório de notificações por atraso."
        permissions = (
            ("notification_deadline_monitor", "Monitor de Notificação Vencidas"),
        )

    def save(self, *args, **kargs):
        if self.inspection.finalized:
            raise Exception("Inspeção/Correição já finalizada.")
        else:
            super(NotificationHistory, self).save(*args, **kargs)


class MemberOrgan(AuditTimestampModel):
    """ """

    inspection = models.ForeignKey(
        Inspection, related_name="in_member_organ", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Employee, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    member_role = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "MEMBER_ROLE"),
        verbose_name="Papel",
        default=1,
    )
    exclusive = models.BooleanField(default=False)
    needs_exclusivity = models.BooleanField(default=False)
    justify = models.TextField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(MemberOrgan, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class OperatingStructure(AuditTimestampModel):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    location = models.CharField(max_length=500)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(OperatingStructure, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class StructureEquipment(AuditTimestampModel):
    """ """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    equipment = models.CharField(max_length=500)
    amount = models.SmallIntegerField(null=True, blank=True)
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "STATUS_EQUIPMENT"),
        verbose_name="Estado",
        default=1,
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureEquipment, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class GeneralStatus(AuditTimestampModel):
    """ """

    status = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "GENERAL_STATUS"),
        verbose_name="Estado",
        default=1,
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class StructureGeneralStatus(GeneralStatus):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(StructureGeneralStatus, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AdministrativeOrganizationOperatingHours(AuditTimestampModel):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    operate_schedule1_initial = models.CharField(max_length=5, null=True, blank=True)
    operate_schedule1_final = models.CharField(max_length=5, null=True, blank=True)
    operate_schedule2_initial = models.CharField(max_length=5, null=True, blank=True)
    operate_schedule2_final = models.CharField(max_length=5, null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationOperatingHours, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")

    @property
    def office_hour(self):
        return "{}-{} {}-{}".format(
            self.operate_schedule1_initial,
            self.operate_schedule1_final,
            self.operate_schedule2_initial,
            self.operate_schedule2_final,
        )


class AdministrativeOrganizationAttendanceHours(AuditTimestampModel):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    daily_attendance = models.BooleanField(default=False, null=True, blank=True)
    days_of_attendance_per_week = models.SmallIntegerField(
        null=True, blank=True, default=0
    )
    attendance_schedule1_initial = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule1_final = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule2_initial = models.CharField(max_length=5, null=True, blank=True)
    attendance_schedule2_final = models.CharField(max_length=5, null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationAttendanceHours, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AdministrativeOrganizationRegistrationSystem(AuditTimestampModel):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    registration_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "REGISTRATION_TYPE"),
        verbose_name="Tipo de Registro",
        default=1,
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationRegistrationSystem, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class ExistingRegisters(AuditTimestampModel):
    """ """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    register = models.CharField(max_length=500, null=True, blank=True)
    registration_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("inspection", "REGISTRATION_TYPE"),
        verbose_name="Tipo de Registro",
        default=1,
    )
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(ExistingRegisters, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AdministrativeOrganizationProcedures(AuditTimestampModel):
    """ """

    number = models.CharField(max_length=30, null=True, blank=True)
    taxonomy_class = models.ForeignKey(
        LegalClass, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    taxonomy_matter = models.ForeignKey(
        LegalMatter, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    matter = models.TextField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class AdministrativeOrganizationProceduresInProgress(
    AdministrativeOrganizationProcedures
):
    """ """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    instauration_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationProceduresInProgress, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AdministrativeOrganizationArchivedProcedures(
    AdministrativeOrganizationProcedures
):
    """ """

    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    instauration_date = models.DateField(null=True, blank=True)
    archived_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationArchivedProcedures, self).save(
                *args, **kargs
            )
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class AdministrativeOrganizationGeneralStatus(GeneralStatus):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(AdministrativeOrganizationGeneralStatus, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")


class Performance(AuditTimestampModel):
    """ """

    inspection = models.OneToOneField(
        Inspection, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    performance = models.TextField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = ""

    def save(self, *args, **kargs):
        if self.inspection.signs.all().count() == 0:
            super(Performance, self).save(*args, **kargs)
        else:
            raise Exception("Inspeção/Correição já assinada, edição não permitida.")
