# -*- coding: utf-8 -*-
import calendar
import json
from datetime import date, datetime
from decimal import Decimal

from django.db import models
from django.db.models import Avg, Q, Sum
from django.template import Context, loader

from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, getLogger
from corregedoria.inspection.models import (
    Inspection,
    PromptnessCourtLawsuit,
    PromptnessOutCourtLawsuit,
    QualitativeAnalysisOfThePartsCivilCourtLawsuit,
    QualitativeAnalysisOfThePartsCriminalCourtLawsuit,
    QualitativeAnalysisOfThePartsElectoral,
    QualitativeAnalysisOfThePartsOutCourtLawsuit,
)
from corregedoria.models import BandScoreTable, ConfigScoreTable
from rh.afastamento.models import AfastamentoEstudar
from rh.models import MovimentacaoPromocao, MovimentacaoRemocaoMembro
from rh.models import Servidor as Employee
from rh.models import ServidorLotacao as EmployeeLocation
from standard.models import AuditTimestampModel, Choice, Configuration

log = getLogger(__name__)


class Prontuary(AuditTimestampModel):
    """
    Prontuario Eletronico dos Membros
    """

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Prontuário Eletrônico dos Membros"

    @property
    def rendered(self):
        inspectionlink = InspectionLink.objects.filter(
            prontuary=self, active=True
        ).first()
        listindication = ListIndication.objects.filter(prontuary=self).first()
        institutionalparticipation = InstitutionalParticipation.objects.filter(
            prontuary=self
        ).first()
        coursesparticipation = CoursesParticipation.objects.filter(
            prontuary=self
        ).first()
        exerciseinrole = ExerciseInRole.objects.filter(prontuary=self).first()
        performanceparticulardifficulty = (
            PerformanceParticularDifficulty.objects.filter(prontuary=self).first()
        )
        trainingimprovement = TrainingImprovement.objects.filter(prontuary=self).first()
        institutionalcontribution = InstitutionalContribution.objects.filter(
            prontuary=self
        ).first()
        integratestrategicworkgroup = IntegrateStrategicWorkGroup.objects.filter(
            prontuary=self
        ).first()
        integrateworkgroup = IntegrateWorkGroup.objects.filter(prontuary=self).first()
        values = {
            "prontuary": self,
            "foto_link": (
                self.employee.pessoa_fisica.foto.resizelink((85, 115))
                if self.employee.pessoa_fisica.foto
                else ""
            ),
        }
        if inspectionlink:
            values.update(inspectionlink.rendered_values())
        if listindication:
            values.update(listindication.rendered_values())
        if institutionalparticipation:
            values.update(institutionalparticipation.rendered_values())
        if coursesparticipation:
            values.update(coursesparticipation.rendered_values())
        if exerciseinrole:
            values.update(exerciseinrole.rendered_values())
        if performanceparticulardifficulty:
            values.update(performanceparticulardifficulty.rendered_values())
        if trainingimprovement:
            values.update(trainingimprovement.rendered_values())
        if institutionalcontribution:
            values.update(institutionalcontribution.rendered_values())
        if integratestrategicworkgroup:
            values.update(integratestrategicworkgroup.rendered_values())
        if integrateworkgroup:
            values.update(integrateworkgroup.rendered_values())
        tpl = loader.get_template("prontuary/prontuary.html")
        return tpl.render(
            # Context(values)
            values
            # Aparentemente, a versão do Django foi alterada e
            # , consequentemente o sistema apresentava a seguinte
            # mensagem ao executar Context(values):
            # TypeError: context must be a dict rather than Context.
            # Ao pesquisar na internet - Stackoverflow, recebi a informação
            # de que In Django 1.8+, the template's render method takes a
            # dictionary for the context parameter. Support for passing a Context
            # instance is deprecated, and gives an error in Django 1.10+.
            # Dessa forma, a fim de reestabelecer a funcionalida do sistema,
            # Alterei o retorno de Context(values) para um dicionário comum.
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.employee.is_ativo():
            item = {"title": "Ativo", "iconCls": "icon-crgmpe icon-crgmpe-man-hat"}
        else:
            item = {"title": "Inativo", "iconCls": "icon-crgmpe icon-crgmpe-man-red"}
        rst.append(item)
        return rst

    @property
    def get_registrofuncional(self):
        return ""

    @property
    def get_cargo(self):
        ret = ""
        p = self.employee.posses.filter(quadro__cargo__carreira=2).last()
        if p.quadro.cargo.instancia:
            if p.quadro.cargo.instancia.pk == 1:
                ret = "PROMOTOR DE JUSTIÇA"
            if p.quadro.cargo.instancia.pk == 2:
                ret = "PROCURADOR DE JUSTIÇA"
        else:
            ret = "PROMOTOR DE JUSTIÇA SUBSTITUTO"
        return ret

    @property
    def get_prole(self):
        return self.employee.dependentes.filter(tipo=3)

    @property
    def get_nomeacao(self):
        return self.employee.posses.filter(
            tipo_movcarreira="NOMEACAO", quadro__cargo__carreira=2
        ).first()

    @property
    def get_atualcargo(self):
        return self.employee.posses.filter(quadro__cargo__carreira=2).last()

    @property
    def get_criterio(self):
        mov = None
        p = self.employee.posses.filter(quadro__cargo__carreira=2).last()
        if p.tipo_movcarreira == "PROMOCAO":
            mov = MovimentacaoPromocao.objects.filter(pk=p.pk).first()
        if p.tipo_movcarreira == "REMOCAO":
            mov = MovimentacaoRemocaoMembro.objects.filter(pk=p.pk).first()
        criterio = mov.get_criterio_display() if mov else None
        return criterio

    @property
    def get_inicioentrancia(self):
        entranciaatual = (
            self.employee.posses.filter(quadro__cargo__carreira=2)
            .last()
            .quadro.cargo.entrancia.pk
            if self.employee.posses.filter(quadro__cargo__carreira=2)
            .last()
            .quadro.cargo.entrancia
            else 0
        )
        return self.employee.posses.filter(
            quadro__cargo__carreira=2, quadro__cargo__entrancia__pk=entranciaatual
        ).first()

    @property
    def get_vitaliciamento(self):
        ret = (
            "%s (%s)"
            % (
                self.generaldata.vitality_date.strftime("%d/%m/%Y"),
                self.generaldata.vitality_doc,
            )
            if self.generaldata
            else None
        )
        return ret

    @property
    def get_titularizacao(self):
        return self.employee.posses.filter(
            tipo_movcarreira="TITULARIZACAO", quadro__cargo__carreira=2
        ).first()

    @property
    def get_inspection(self):
        inspection = self.inspectionlink.filter(active=True)
        return inspection

    @property
    def get_lastmeritoriousness(self):
        return self.employee.posses.filter(
            Q(movimentacaopromocao__criterio=2)
            | Q(movimentacaoremocaomembro__criterio=2)
        ).last()


class GeneralData(AuditTimestampModel):
    """
    Dados gerais para o Prontuario Eletronico dos Membros
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    vitality_date = models.DateField(null=True, blank=True)
    vitality_doc = models.CharField(max_length=100, null=True, blank=True)
    seniority_position = models.IntegerField(null=True, blank=True)
    ordinance_seniority_position = models.CharField(
        max_length=500, null=True, blank=True
    )
    public_service_time = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Prontuário Eletrônico dos Membros"


class InspectionLink(AuditTimestampModel):
    """
    Vinculo de Inspeccoes/Correicoes ao Prontuario Eletronico dos Membros
    """

    prontuary = models.ForeignKey(
        Prontuary, related_name="inspections", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    inspection = models.ForeignKey(
        Inspection, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    active = models.BooleanField(default=False, null=True, blank=True)
    alter_justify = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = (
            "Vínculo de Inspecções/Correições ao Prontuário Eletrônico dos Membros"
        )

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/functionalperformance/inspection.html")
        return tpl.render(self.rendered_values())

    def rendered_values(self):
        qapccl = QualitativeAnalysisOfThePartsCivilCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        qapcrcl = QualitativeAnalysisOfThePartsCriminalCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        qapocl = QualitativeAnalysisOfThePartsOutCourtLawsuit.objects.filter(
            inspection=self.inspection
        ).first()
        qape = QualitativeAnalysisOfThePartsElectoral.objects.filter(
            inspection=self.inspection
        ).first()
        soma = Decimal(0.00)
        qtd_items = 0
        qap_avg = Decimal(0.00)
        if qapccl:
            if qapccl.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qapccl.score
        if qapcrcl:
            if qapcrcl.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qapcrcl.score
        if qapocl:
            if qapocl.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qapocl.score
        if qape:
            if qape.applicable:
                qtd_items = qtd_items + 1
                soma = soma + qape.score
        if qtd_items > 0:
            qap_avg = Decimal(soma / qtd_items)
        pcl = Decimal(
            self.inspection.promptnesscourtlawsuit.score
            if PromptnessCourtLawsuit.objects.filter(
                inspection=self.inspection
            ).exists()
            else 0
        )
        pocl = Decimal(
            self.inspection.promptnessoutcourtlawsuit.score
            if PromptnessOutCourtLawsuit.objects.filter(
                inspection=self.inspection
            ).exists()
            else 0
        )
        plawsuit_avg = (pcl + pocl) / 2
        ret = {
            "inspection": self.inspection,
            "qapccl": qapccl,
            "qapcrcl": qapcrcl,
            "qapocl": qapocl,
            "qape": qape,
            "qap_avg": qap_avg,
            "plawsuit_avg": plawsuit_avg,
        }
        return ret

    def mark_inspection(self):
        insps = InspectionLink.objects.filter(prontuary=self.prontuary).exclude(
            pk=self.pk
        )
        insps.update(active=False)
        self.active = True
        self.save()


class TimeRegister(AuditTimestampModel):
    """
    Registra um periodo especifico (data_inicio e data_fim) para uma condicao especifica e satisfeita
    """

    date_initial = models.DateField(null=True, blank=True)
    date_final = models.DateField(null=True, blank=True)
    total_days = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = "Registra um período (data_inicio e data_fim) para uma condição específica é satisfesta"


class Cumulation(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Cumulacao
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Representação do que foi alcançado pelo membro no item Cumulação"
        )

    @property
    def total_days(self):
        ret = self.listcumulations.filter(active=True).aggregate(
            total=Sum("total_days")
        )["total"]
        ret = ret if ret else 0
        return ret

    @property
    def total_months(self):
        days = self.total_days
        months = round(days / 30.0, 2)
        return months

    @property
    def get_score(self):
        ret = 0
        cfg = Configuration.get_or_create("corregedoria")
        scoretable = ConfigScoreTable.objects.filter(
            score_table=int(cfg.get("var_functionalperformance_cumulation", 0)),
            active=True,
        ).first()
        if scoretable:
            band = (
                BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=self.total_months,
                )
                .filter(
                    Q(Q(end_value__gte=self.total_months) | Q(end_value__isnull=True))
                )
                .first()
            )
            if band:
                ret = band.score
        return ret


class ListCumulation(TimeRegister):
    """
    Registro das Cumulacoes identificadas para o membro
    """

    cumulation = models.ForeignKey(
        Cumulation, related_name="listcumulations", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    real_cumulation = models.BooleanField(default=False, null=True, blank=True)
    active = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        ordering = ["date_initial", "date_final"]
        verbose_name = "Registro das cumulações identificadas para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/functionalperformance/cumulation.html")
        return tpl.render(
            {
                "listcumulation": self,
                "detaillistcumulation": DetailListCumulation.objects.filter(
                    listcumulation=self
                ),
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.active:
            item = {
                "title": "Vinculado ao Prontuário",
                "iconCls": "icon-crgmpe icon-crgmpe-success",
            }
        else:
            item = {
                "title": "Não vinculado ao Prontuário",
                "iconCls": "icon-crgmpe icon-crgmpe-delete",
            }
        rst.append(item)
        if self.real_cumulation:
            item = {"title": "Cumulação", "iconCls": "icon-crgmpe icon-crgmpe-add"}
        else:
            item = {"title": "Subsituição", "iconCls": "icon-crgmpe icon-crgmpe-users"}
        rst.append(item)
        return rst

    def mark_realcumulation(self):
        self.real_cumulation = True
        self.save()

    def mark_activecumulation(self):
        if self.active is True:
            self.active = False
        else:
            self.active = True
        self.save()


class DetailListCumulation(AuditTimestampModel):
    """
    Detalhamento das cumulacoes identificadas para o membro
    """

    listcumulation = models.ForeignKey(
        ListCumulation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    employeelocation = models.ForeignKey(
        EmployeeLocation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = [
            "employeelocation__data_vigencia_inicio",
            "employeelocation__data_vigencia_fim",
        ]
        verbose_name = "Detalhamento das cumulações identificadas para o membro"


class ListIndication(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Indicacao em Lista
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Representação do que foi alcançado pelo membro no item Indicação em Lista"
        )

    def get_lists(self, criteria=None):
        group = DetailListIndication.objects.filter(
            listindication=self, criteria=criteria
        ).order_by("date_edital")
        if criteria:
            group = group.filter(criteria=criteria)
        lc = []
        la = []
        for item in group:
            if item.list_figuration == 2:
                lc.append(item)
                la.append(item)
            else:
                lc = []
        ret = []
        ret.append(lc)
        ret.append(la)
        return ret

    def get_score(self, criteria):
        total = self.get_totallist(criteria)
        return 10 if total > 2 else total * 5

    def get_totallist(self, criteria):
        count = DetailListIndication.objects.filter(
            listindication=self, criteria=criteria, list_figuration=2
        ).count()
        return count

    def get_consecutivenesslist(self, criteria):
        count = len(self.get_lists(criteria)[0])
        if count == 1:
            count = 0
        return count

    def get_alternancelist(self, criteria):
        count = len(self.get_lists(criteria)[1])
        if count == 1:
            count = 0
        return count

    def rendered_values(self):
        ret = {
            "alternancelist_promocao": self.get_alternancelist(criteria=1),
            "alternancelist_remocao": self.get_alternancelist(criteria=2),
            "consecutivenesslist_promocao": self.get_consecutivenesslist(criteria=1),
            "consecutivenesslist_remocao": self.get_consecutivenesslist(criteria=2),
            "totallist_promocao": self.get_totallist(criteria=1),
            "totallist_remocao": self.get_totallist(criteria=2),
            "score_promocao": self.get_score(criteria=1),
            "score_remocao": self.get_score(criteria=2),
        }
        return ret


class DetailListIndication(AuditTimestampModel):
    """
    Inscricoes em concursos, bem como as indicacoes em lista de Promocao e Remocao para o membro
    """

    listindication = models.ForeignKey(
        ListIndication, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    edital = models.CharField(max_length=100, null=True, blank=True)
    date_edital = models.DateField(null=True, blank=True)
    list_figuration = models.SmallIntegerField(null=True, blank=True, default=1)
    criteria = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("prontuary", "CRITERIA"),
        verbose_name="Critério de Merecimento",
        default=1,
    )

    class Meta:
        ordering = ["-date_edital"]
        verbose_name = "Inscrições em concursos, bem como as indicações em lista de Promoção e Remoção para o membro"

    def __str__(self):
        return "%s de %s" % (self.edital, self.date_edital.strftime("%d/%m/%Y"))

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/individualperformance/listindication.html")
        return tpl.render(
            {
                "detaillistindication": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.list_figuration == 2:
            if self.criteria == 1:
                item = {
                    "title": "Figurou em lista: PROMOÇÃO",
                    "iconCls": "icon-crgmpe icon-crgmpe-people-blue",
                }
            if self.criteria == 2:
                item = {
                    "title": "Figurou em lista: REMOÇÃO",
                    "iconCls": "icon-crgmpe icon-crgmpe-people-green",
                }
            rst.append(item)
        return rst

    def mark_activedetaillistindication(self):
        self.active = True
        self.save()


class AttachmentsListIndication(AuditTimestampModel):
    """
    Anexos referentes as Inscricoes em concursos, bem como as indicacoes em lista de Promocao e Remocao para o membro
    """

    detaillistindication = models.ForeignKey(
        DetailListIndication, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes às Inscrições em concursos, bem como as indicações em lista de Promoção e Remoção para o membro"

    def mark_activedetaillistindication(self):
        if self.list_figuration == 2:
            self.active = True
            self.save()
        else:
            raise Exception(
                "Não é possível ativar essa inscrição, pois há a identificação que o membro figurou em lista."
            )


class InstitutionalParticipation(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Participacao Institucional
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Participação Institucional"

    def rendered_values(self):
        ret = {
            "institutionalparticipation": self,
            "detailinstitutionalparticipations": DetailInstitutionalParticipation.objects.filter(
                institutionalparticipation=self
            ),
        }
        return ret

    @property
    def get_score(self):
        total = DetailInstitutionalParticipation.objects.filter(
            institutionalparticipation=self, used_edital=None, validated=2
        ).aggregate(total=Sum("score"))["total"]
        if total is None:
            total = 0
        return 10 if total > 10 else total


class DetailInstitutionalParticipation(AuditTimestampModel):
    """
    Participacoes instituicionais registradas para o membro
    """

    institutionalparticipation = models.ForeignKey(
        InstitutionalParticipation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    contribution = models.CharField(max_length=1000, null=True, blank=True)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    score = models.IntegerField(null=True, blank=True, default=0)
    validated = models.SmallIntegerField(null=True, blank=True, default=1)

    class Meta:
        verbose_name = "Participações instituicionais registradas para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/institutionalparticipation.html"
        )
        return tpl.render(
            {
                "detailinstitutionalparticipation": self,
            }
        )

    def save(self, *args, **kargs):
        if self.validated == 2:
            self.score = 2
        else:
            self.score = 0
        super(DetailInstitutionalParticipation, self).save(*args, **kargs)


class AttachmentsDetailInstitutionalParticipation(AuditTimestampModel):
    """
    Anexos referentes as participacoes instituicionais do membro
    """

    detailinstitutionalparticipation = models.ForeignKey(
        DetailInstitutionalParticipation,
        related_name="attachments",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes as participações instituicionais do membro"


class CoursesParticipation(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Frequencia e Aproveitamento em Cursos
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Frequência e Aproveitamento em Cursos"

    def rendered_values(self):
        ret = {
            "coursesparticipation": self,
            "detailcoursesparticipations": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self
            ).order_by("used_edital", "course_level", "-date_course"),
            "detailcoursesparticipations_doctorate": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, course_level=1
            ).order_by(
                "-used_edital", "course_level", "-date_course"
            ),
            "detailcoursesparticipations_masters": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, course_level=2
            ).order_by(
                "-used_edital", "course_level", "-date_course"
            ),
            "detailcoursesparticipations_specialization": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, course_level=3
            ).order_by(
                "-used_edital", "course_level", "-date_course"
            ),
            "detailcoursesparticipations_cesaf": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, course_level=4
            ).order_by(
                "-used_edital", "course_level", "-date_course"
            ),
            "detailcoursesparticipations_improvement": DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, course_level=5
            ).order_by(
                "-used_edital", "course_level", "-date_course"
            ),
        }
        return ret

    @property
    def total_hours_cesaf(self):
        return DetailCoursesParticipation.objects.filter(
            coursesparticipation=self, course_level=4, validated=2, used_edital=None
        ).aggregate(total=Sum("workload"))["total"]

    @property
    def get_score(self):
        score_cesaf = self.total_hours_cesaf // 180 if self.total_hours_cesaf else 0
        total = (
            DetailCoursesParticipation.objects.filter(
                coursesparticipation=self, validated=2, used_edital=None
            )
            .exclude(course_level=4)
            .aggregate(total=Sum("score"))["total"]
        )
        total = total if total else 0 + score_cesaf
        return total


class DetailCoursesParticipation(AuditTimestampModel):
    """
    Cursos registrados para o membro
    """

    coursesparticipation = models.ForeignKey(
        CoursesParticipation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    course_level = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("prontuary", "COURSE_LEVEL"),
        verbose_name="Critério de Merecimento",
        default=1,
    )
    course = models.CharField(max_length=1000, null=True, blank=True)
    date_course = models.DateField(null=True, blank=True)
    workload = models.IntegerField(null=True, blank=True, default=0)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    studydepartures = models.ManyToManyField(
        AfastamentoEstudar, related_name="departures"
    )
    validated = models.SmallIntegerField(null=True, blank=True, default=2)
    score = models.SmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        ordering = ["used_edital", "course_level", "-date_course"]
        verbose_name = "Cursos registrados para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/coursesparticipation.html"
        )
        return tpl.render(
            {
                "detailcoursesparticipation": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.validated == 2:
            if self.used_edital is not None:
                item = {
                    "title": "Utilizado em: <b>%s</b>" % self.used_edital,
                    "iconCls": "icon-crgmpe icon-crgmpe-minus",
                }
            else:
                item = {
                    "title": "Não utilizado",
                    "iconCls": "icon-crgmpe icon-crgmpe-add",
                }
            rst.append(item)
        else:
            item = {
                "title": "Não homologado para pontuação",
                "iconCls": "icon-crgmpe icon-crgmpe-delete",
            }
            rst.append(item)
        return rst

    def get_departure_days(self):
        soma = 0
        for data in self.studydepartures.all():
            dr = NewDateRange(data.data_inicio, data.data_fim)
            soma = soma + dr.days
        return soma

    def check_score(self):
        ret = True
        departure_days = self.get_departure_days()
        var = ""
        query = None
        if self.course_level == 1:
            var = "var_coursesparticipation_doctorate"
        if self.course_level == 2:
            var = "var_coursesparticipation_masters"
        if self.course_level == 3:
            var = "var_coursesparticipation_specialization"
        if self.course_level == 5:
            var = "var_coursesparticipation_improvement"
        cfg = Configuration.get_or_create("corregedoria")
        scoretable = ConfigScoreTable.objects.filter(
            score_table=int(cfg.get(var, 0)), active=True
        ).first()
        if scoretable:
            if self.course_level in [1, 2]:
                query = BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=departure_days,
                ).filter(
                    Q(Q(end_value__gte=departure_days) | Q(end_value__isnull=True))
                )
            if self.course_level in [3, 5]:
                query = BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=self.workload,
                ).filter(Q(Q(end_value__gte=self.workload) | Q(end_value__isnull=True)))
            band = query.first()
            if band:
                if self.score > band.score:
                    ret = False
        if self.course_level == 5:
            pass
        return ret

    def save(self, *args, **kargs):
        if self.pk:
            if self.check_score() is False:
                raise Exception(
                    "A pontuação atribuída não está de acordo com a regulamentação vigente."
                )
        super(DetailCoursesParticipation, self).save(*args, **kargs)


class AttachmentsDetailCoursesParticipation(AuditTimestampModel):
    """
    Anexos referentes as participacoes em cursos do membro
    """

    detailcoursesparticipation = models.ForeignKey(
        DetailCoursesParticipation, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes as participações em cursos do membro"


class ExerciseInRole(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "exerciseinrole": self,
            "detailexerciseinroles": DetailExerciseInRole.objects.filter(
                exerciseinrole=self
            ),
        }
        return ret

    @property
    def get_score(self):
        total = DetailExerciseInRole.objects.filter(
            exerciseinrole=self, validated=2, used_edital=None
        ).aggregate(total=Sum("score"))["total"]
        total = total if total else 0
        return total


class BaseDesignation(AuditTimestampModel):
    """ """

    designation = models.ForeignKey(
        EmployeeLocation,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    role = models.CharField(max_length=500, null=True, blank=True)
    date_initial = models.DateField(null=True, blank=True)
    date_final = models.DateField(null=True, blank=True)
    act_initial = models.CharField(max_length=500, null=True, blank=True)
    act_final = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = ""


class DetailExerciseInRole(BaseDesignation):
    """ """

    exerciseinrole = models.ForeignKey(
        ExerciseInRole, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    validated = models.SmallIntegerField(null=True, blank=True, default=2)
    score = models.SmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/individualperformance/exerciseinrole.html")
        return tpl.render(
            {
                "detailexerciseinrole": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.validated == 2:
            if self.used_edital is not None:
                item = {
                    "title": "Utilizado em: <b>%s</b>" % self.used_edital,
                    "iconCls": "icon-crgmpe icon-crgmpe-minus",
                }
            else:
                item = {
                    "title": "Não utilizado",
                    "iconCls": "icon-crgmpe icon-crgmpe-add",
                }
            rst.append(item)
        else:
            item = {
                "title": "Não homologado para pontuação",
                "iconCls": "icon-crgmpe icon-crgmpe-delete",
            }
            rst.append(item)
        return rst

    def save(self, *args, **kargs):
        # if self.pk is None:
        #     if self.publication_type == 1:
        #         self.score = 10
        super(DetailExerciseInRole, self).save(*args, **kargs)


class AttachmentsDetailExerciseInRole(AuditTimestampModel):
    """ """

    detailexerciseinrole = models.ForeignKey(
        DetailExerciseInRole, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class TrainingImprovement(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Aprimoramento de Formacao Juridica e Profissional
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Aprimoramento de Formação Jurídica e Profissional"

    def rendered_values(self):
        ret = {
            "trainingimprovement": self,
            "detailtrainingimprovement": DetailTrainingImprovement.objects.filter(
                trainingimprovement=self
            ).order_by("used_edital", "publication_type", "-date_publication"),
        }
        return ret

    @property
    def get_score(self):
        total = DetailTrainingImprovement.objects.filter(
            trainingimprovement=self, validated=2, used_edital=None
        ).aggregate(total=Sum("score"))["total"]
        total = total if total else 0
        return total


class DetailTrainingImprovement(AuditTimestampModel):
    """
    Publicacoes registrados para o membro
    """

    trainingimprovement = models.ForeignKey(
        TrainingImprovement, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    publication_type = models.SmallIntegerField(
        null=True,
        blank=True,
        choices=Choice.get_choices_for("prontuary", "PUBLICATION_TYPE"),
        verbose_name="Tipo de Publicação",
        default=1,
    )
    publication = models.CharField(max_length=1000, null=True, blank=True)
    date_publication = models.DateField(null=True, blank=True)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    validated = models.SmallIntegerField(null=True, blank=True, default=2)
    score = models.SmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        ordering = ["publication_type", "-date_publication"]
        verbose_name = "Publicações registrados para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/trainingimprovement.html"
        )
        return tpl.render(
            {
                "detailtrainingimprovement": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.publication_type is not None:
            if self.publication_type == 1:
                item = {"title": "Livro", "iconCls": "icon-crgmpe icon-crgmpe-book"}
            if self.publication_type == 2:
                item = {"title": "Artigo", "iconCls": "icon-crgmpe icon-crgmpe-reports"}
            rst.append(item)
        if self.used_edital is not None:
            item = {
                "title": "Utilizado em: <b>%s</b>" % self.used_edital,
                "iconCls": "icon-crgmpe icon-crgmpe-info",
            }
            rst.append(item)
        return rst

    def save(self, *args, **kargs):
        if self.pk is None:
            if self.publication_type == 1:
                self.score = 10
        if self.publication_type == 2:
            if self.score > 5:
                raise Exception(
                    "O valor atribuído a publicação ultrapassa a nota máxima (5 pontos)."
                )
        super(DetailTrainingImprovement, self).save(*args, **kargs)


class AttachmentsDetailTrainingImprovement(AuditTimestampModel):
    """
    Anexos referentes ao Aprimoramento e Formacao Juridica e Profissional
    """

    detailtrainingimprovement = models.ForeignKey(
        DetailTrainingImprovement, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = (
            "Anexos referentes ao Aprimoramento e Formação Jurídica e Profissional"
        )


class PerformanceParticularDifficulty(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Atuacao em Comarca de Particular Dificuldade
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Atuação em Comarca de Particular Dificuldade"

    def rendered_values(self):
        ret = {
            "performanceparticulardifficulty": self,
        }
        return ret

    @property
    def total_days(self):
        ret = 0
        for data in self.detailsperformance.all():
            if data.used_edital is None:
                ret = ret + data.total_days
        return ret

    @property
    def total_months(self):
        days = self.total_days
        months = round(days / 30.0, 2)
        return months

    @property
    def get_score(self):
        ret = 0
        cfg = Configuration.get_or_create("corregedoria")
        scoretable = ConfigScoreTable.objects.filter(
            score_table=int(cfg.get("var_performance_particular_difficulty", 0)),
            active=True,
        ).first()
        if scoretable:
            band = (
                BandScoreTable.objects.filter(
                    active=True,
                    configscoretable=scoretable,
                    initial_value__lte=self.total_months,
                )
                .filter(
                    Q(Q(end_value__gte=self.total_months) | Q(end_value__isnull=True))
                )
                .first()
            )
            if band:
                ret = band.score
        return ret


class DetailPerformanceParticularDifficulty(AuditTimestampModel):
    """
    Atuacoes em Comarcas de Particular Dificuldade registrados para o membro
    """

    performanceparticulardifficulty = models.ForeignKey(
        PerformanceParticularDifficulty,
        related_name="detailsperformance",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    employeelocation = models.ForeignKey(
        EmployeeLocation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    score = models.SmallIntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = (
            "Atuações em Comarcas de Particular Dificuldade registrados para o membro"
        )

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/performanceparticulardifficulty.html"
        )
        return tpl.render(
            {
                "detailperformanceparticulardifficulty": self,
            }
        )

    @property
    def employeelocation_description(self):
        return "%s: %s à %s" % (
            self.employeelocation.lotacao,
            DateUtils.date_to_str(self.employeelocation.data_vigencia_inicio),
            (
                DateUtils.date_to_str(self.employeelocation.data_vigencia_fim)
                if self.employeelocation.data_vigencia_fim
                else "----"
            ),
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        if self.used_edital is not None:
            item = {
                "title": "Utilizado em: <b>%s</b>" % self.used_edital,
                "iconCls": "icon-crgmpe icon-crgmpe-info",
            }
            rst.append(item)
        return rst

    @property
    def total_days(self):
        dr = NewDateRange(
            self.employeelocation.data_vigencia_inicio,
            (
                self.employeelocation.data_vigencia_fim
                if self.employeelocation.data_vigencia_fim
                else datetime.now().date()
            ),
        )
        return dr.days


class InstitutionalContribution(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Contribuicao para Execucao dos Programas de Atuacao, Metas Institucionais e Projetos Especiais
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Contribuição para Execução dos Programas de Atuação, Metas Institucionais e Projetos Especiais"

    def rendered_values(self):
        ret = {
            "institutionalcontribution": self,
            "detailinstitutionalcontributions": DetailInstitutionalContribution.objects.filter(
                institutionalcontribution=self
            ),
        }
        return ret

    @property
    def get_score(self):
        total = DetailInstitutionalContribution.objects.filter(
            institutionalcontribution=self
        ).aggregate(total=Sum("score"))["total"]
        return total if total else 0


class DetailInstitutionalContribution(AuditTimestampModel):
    """
    Contribuicoes instituicionais registradas para o membro
    """

    institutionalcontribution = models.ForeignKey(
        InstitutionalContribution, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    contribution = models.CharField(max_length=1000, null=True, blank=True)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    score = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = "Contribuições instituicionais registradas para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/institutionalcontribution.html"
        )
        return tpl.render(
            {
                "detailinstitutionalcontribution": self,
            }
        )

    def save(self, *args, **kargs):
        super(DetailInstitutionalContribution, self).save(*args, **kargs)


class AttachmentsDetailInstitutionalContribution(AuditTimestampModel):
    """
    Anexos referentes as contribuicoes instituicionais do membro
    """

    detailinstitutionalcontribution = models.ForeignKey(
        DetailInstitutionalContribution,
        related_name="attachments",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes as contribuições instituicionais do membro"


class IntegrateStrategicWorkGroup(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Integrar Grupo de Trabalho, Comissao ou Comite estrategicos instituicionais
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Integrar Grupo de Trabalho, Comissão ou Comitê estratégicos instituicionais"

    def rendered_values(self):
        ret = {
            "integratestrategicworkgroup": self,
            "detailintegratestrategicworkgroups": DetailIntegrateStrategicWorkGroup.objects.filter(
                integratestrategicworkgroup=self
            ),
        }
        return ret

    @property
    def get_score(self):
        total = DetailIntegrateStrategicWorkGroup.objects.filter(
            integratestrategicworkgroup=self
        ).aggregate(total=Sum("score"))["total"]
        return total if total else 0


class DetailIntegrateStrategicWorkGroup(AuditTimestampModel):
    """
    Participacao em Grupos de Trabalhos Estrategicos registradas para o membro
    """

    integratestrategicworkgroup = models.ForeignKey(
        IntegrateStrategicWorkGroup, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    workgroup = models.CharField(max_length=1000, null=True, blank=True)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    score = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = (
            "Participação em Grupos de Trabalhos Estratégicos registradas para o membro"
        )

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/integratestrategicworkgroup.html"
        )
        return tpl.render(
            {
                "detailintegratestrategicworkgroup": self,
            }
        )

    def save(self, *args, **kargs):
        super(DetailIntegrateStrategicWorkGroup, self).save(*args, **kargs)


class AttachmentsDetailIntegrateStrategicWorkGroup(AuditTimestampModel):
    """
    Anexos referentes as participacoes do membro em Grupos de Trabalho Estrategicos
    """

    detailintegratestrategicworkgroup = models.ForeignKey(
        DetailIntegrateStrategicWorkGroup,
        related_name="attachments",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes as participações do membro em Grupos de Trabalho Estratégicos"


class IntegrateWorkGroup(AuditTimestampModel):
    """
    Representacao do que foi alcancado pelo membro no item Integrar Grupo de Trabalho, Comissao ou Comite atualmente existentes, em exercicio, no ambito da Instituicao
    """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Representação do que foi alcançado pelo membro no item Integrar Grupo de Trabalho, Comissão ou Comitê atualmente existentes, em exercício, no âmbito da Instituição"

    def rendered_values(self):
        ret = {
            "integrateworkgroup": self,
            "detailintegrateworkgroups": DetailIntegrateWorkGroup.objects.filter(
                integrateworkgroup=self
            ),
        }
        return ret

    @property
    def get_score(self):
        total = DetailIntegrateWorkGroup.objects.filter(
            integrateworkgroup=self
        ).aggregate(total=Sum("score"))["total"]
        return total if total else 0


class DetailIntegrateWorkGroup(AuditTimestampModel):
    """
    Participacao em Grupos de Trabalhos Insitucionais registradas para o membro
    """

    integrateworkgroup = models.ForeignKey(
        IntegrateWorkGroup, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    workgroup = models.CharField(max_length=1000, null=True, blank=True)
    used_edital = models.ForeignKey(
        DetailListIndication,
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    score = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        verbose_name = "Participação em Grupos de Trabalhos Institucionais registradas para o membro"

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/individualperformance/integrateworkgroup.html"
        )
        return tpl.render(
            {
                "detailintegrateworkgroup": self,
            }
        )

    def save(self, *args, **kargs):
        super(DetailIntegrateWorkGroup, self).save(*args, **kargs)


class AttachmentsDetailIntegrateWorkGroup(AuditTimestampModel):
    """
    Anexos referentes as participacoes do membro em Grupos de Trabalho Institucionais
    """

    detailintegrateworkgroup = models.ForeignKey(
        DetailIntegrateWorkGroup, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Anexos referentes as participações do membro em Grupos de Trabalho Institucionais"


class Promotion(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "promotion": self,
        }
        return ret


class DetailPromotion(BaseDesignation):
    """ """

    promotion = models.ForeignKey(
        Promotion, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/movement/promotion.html")
        return tpl.render(
            {
                "detailpromotion": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailPromotion, self).save(*args, **kargs)


class AttachmentsDetailPromotion(AuditTimestampModel):
    """ """

    detailpromotion = models.ForeignKey(
        DetailPromotion, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Removal(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "removal": self,
        }
        return ret


class DetailRemoval(BaseDesignation):
    """ """

    removal = models.ForeignKey(
        Removal, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/movement/removal.html")
        return tpl.render(
            {
                "detailremoval": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailRemoval, self).save(*args, **kargs)


class AttachmentsDetailRemoval(AuditTimestampModel):
    """ """

    detailremoval = models.ForeignKey(
        DetailRemoval, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Permutation(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "permutation": self,
        }
        return ret


class DetailPermutation(BaseDesignation):
    """ """

    permutation = models.ForeignKey(
        Permutation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/movement/permutation.html")
        return tpl.render(
            {
                "detailpermutation": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailPermutation, self).save(*args, **kargs)


class AttachmentsDetailPermutation(AuditTimestampModel):
    """ """

    detailpermutation = models.ForeignKey(
        DetailPermutation, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Exercise(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "exercise": self,
        }
        return ret


class DetailExercise(BaseDesignation):
    """ """

    exercise = models.ForeignKey(
        Exercise, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/designation/exercise.html")
        return tpl.render(
            {
                "detailexercise": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailExercise, self).save(*args, **kargs)


class AttachmentsDetailExercise(AuditTimestampModel):
    """ """

    detailexercise = models.ForeignKey(
        DetailExercise, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Replacement(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "replacement": self,
        }
        return ret


class DetailReplacement(BaseDesignation):
    """ """

    replacement = models.ForeignKey(
        Replacement, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/designation/replacement.html")
        return tpl.render(
            {
                "detailreplacement": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailReplacement, self).save(*args, **kargs)


class AttachmentsDetailReplacement(AuditTimestampModel):
    """ """

    detailreplacement = models.ForeignKey(
        DetailReplacement, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class DesignationCumulation(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "designationcumulation": self,
        }
        return ret


class DetailDesignationCumulation(BaseDesignation):
    """ """

    designationcumulation = models.ForeignKey(
        DesignationCumulation, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/career/designation/designationcumulation.html"
        )
        return tpl.render(
            {
                "detaildesignationcumulation": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailDesignationCumulation, self).save(*args, **kargs)


class AttachmentsDetailDesignationCumulation(AuditTimestampModel):
    """ """

    detaildesignationcumulation = models.ForeignKey(
        DetailDesignationCumulation,
        related_name="attachments",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class PartiesHearings(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "partieshearings": self,
        }
        return ret


class DetailPartiesHearings(BaseDesignation):
    """ """

    partieshearings = models.ForeignKey(
        PartiesHearings, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/designation/partieshearings.html")
        return tpl.render(
            {
                "detailpartieshearings": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailPartiesHearings, self).save(*args, **kargs)


class AttachmentsDetailPartiesHearings(AuditTimestampModel):
    """ """

    detailpartieshearings = models.ForeignKey(
        DetailPartiesHearings, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class AdministrativeFunction(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "administrativefunction": self,
        }
        return ret


class DetailAdministrativeFunction(BaseDesignation):
    """ """

    administrativefunction = models.ForeignKey(
        AdministrativeFunction, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template(
            "prontuary/career/designation/administrativefunction.html"
        )
        return tpl.render(
            {
                "detailadministrativefunction": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailAdministrativeFunction, self).save(*args, **kargs)


class AttachmentsDetailAdministrativeFunction(AuditTimestampModel):
    """ """

    detailadministrativefunction = models.ForeignKey(
        DetailAdministrativeFunction,
        related_name="attachments",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class JointAction(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "jointaction": self,
        }
        return ret


class DetailJointAction(BaseDesignation):
    """ """

    jointaction = models.ForeignKey(
        JointAction, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/designation/jointaction.html")
        return tpl.render(
            {
                "detailjointaction": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailJointAction, self).save(*args, **kargs)


class AttachmentsDetailJointAction(AuditTimestampModel):
    """ """

    detailjointaction = models.ForeignKey(
        DetailJointAction, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Exoneration(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "exoneration": self,
        }
        return ret


class DetailExoneration(BaseDesignation):
    """ """

    exoneration = models.ForeignKey(
        Exoneration, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/termination/exoneration.html")
        return tpl.render(
            {
                "detailexoneration": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailExoneration, self).save(*args, **kargs)


class AttachmentsDetailExoneration(AuditTimestampModel):
    """ """

    detailexoneration = models.ForeignKey(
        DetailExoneration, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Retirement(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "retirement": self,
        }
        return ret


class DetailRetirement(BaseDesignation):
    """ """

    retirement = models.ForeignKey(
        Retirement, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/termination/retirement.html")
        return tpl.render(
            {
                "detailretirement": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailRetirement, self).save(*args, **kargs)


class AttachmentsDetailRetirement(AuditTimestampModel):
    """ """

    detailretirement = models.ForeignKey(
        DetailRetirement, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Departure(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "departure": self,
        }
        return ret


class DetailDeparture(BaseDesignation):
    """ """

    departure = models.ForeignKey(
        Departure, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/others/departure.html")
        return tpl.render(
            {
                "detaildeparture": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailDeparture, self).save(*args, **kargs)


class AttachmentsDetailDeparture(AuditTimestampModel):
    """ """

    detaildeparture = models.ForeignKey(
        DetailDeparture, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Availability(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "availability": self,
        }
        return ret


class DetailAvailability(BaseDesignation):
    """ """

    availability = models.ForeignKey(
        Availability, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/others/availability.html")
        return tpl.render(
            {
                "detailavailability": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailAvailability, self).save(*args, **kargs)


class AttachmentsDetailAvailability(AuditTimestampModel):
    """ """

    detailavailability = models.ForeignKey(
        DetailAvailability, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""


class Punishment(AuditTimestampModel):
    """ """

    prontuary = models.OneToOneField(
        Prontuary, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""

    def rendered_values(self):
        ret = {
            "punishment": self,
        }
        return ret


class DetailPunishment(BaseDesignation):
    """ """

    punishment = models.ForeignKey(
        Punishment, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["date_initial", "role"]
        verbose_name = ""

    @property
    def rendered(self):
        tpl = loader.get_template("prontuary/career/others/punishment.html")
        return tpl.render(
            {
                "detailpunishment": self,
            }
        )

    @property
    def icons(self):
        return self.icons_status

    @property
    def icons_status(self):
        item = None
        rst = []
        # if self.validated == 2:
        #     if self.used_edital is not None:
        #         item = {'title': u'Utilizado em: <b>%s</b>' % self.used_edital, 'iconCls': 'icon-crgmpe icon-crgmpe-minus'}
        #     else:
        #         item = {'title': u'Não utilizado', 'iconCls': 'icon-crgmpe icon-crgmpe-add'}
        #     rst.append(item)
        # else:
        #     item = {'title': u'Não homologado para pontuação', 'iconCls': 'icon-crgmpe icon-crgmpe-delete'}
        #     rst.append(item)
        return rst

    def save(self, *args, **kargs):
        super(DetailPunishment, self).save(*args, **kargs)


class AttachmentsDetailPunishment(AuditTimestampModel):
    """ """

    detailpunishment = models.ForeignKey(
        DetailPunishment, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(max_length=2000)
    attached_file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="+",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = ""
