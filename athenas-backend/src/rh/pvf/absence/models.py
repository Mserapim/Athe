from pyexpat import model
from cesaf.concurso.models import SelecaoEstagio
from contrib.decorator import validate
from django.db import models
from ged.models import Arquivo as File
from rh.dayoff.const import BLOOD_DONATION_USUFRUCT
from rh.dayoff.models import (
    AcquisitionPeriod,
    AcquisitionPeriodAttachment,
    ActivityBookSell,
    ActivityCancel,
    GroupPeriod,
    Usufruct,
    ActivitySuspend,
)
from rh.models import Curso as Curse, Localidade, PessoaFisica, Publicacao
from rh.models import PessoaFisica as Person
from rh.models import UnidadeAdministrativa as AdministrativeUnit
from rh.models import Dependente as Dependent, Dependencia
from standard.models import AuditTimestampModel, Choice
from rh.pvf.models import (
    PortalRequestAbsence,
    PortalRequestSubstitute,
    PortalRequestHistory,
)
from rh.models import MovimentacaoSubstituicao
from rh.afastamento.models import (
    CID,
    BaseLicencaAfastamento,
    LicencaSaudeJuntaMedica,
    LicencaSaude30Dias,
    LicencaSaude3Dias,
    LicencaDoencaPessoaFamilia,
    LicencaCapacitacao,
    LicencaInteresseParticular,
    LicencaAtividadePolitica,
    LicencaMaternidade,
    AusenciaNascimento,
    AusenciaCasamento,
    AusenciaFalecimento,
    AusenciaDoacaoSangue,
    LicencaSaudeHoras,
)
from datetime import datetime, timedelta
from contrib.middleware import get_current_user
from django.db import transaction
from contrib.daterange import NewDateRange
from rh.const import (
    CANCELADO,
    INTERRUPCAO,
    TYPE_ABSENCE_BIRTH,
    TYPE_ABSENCE_BLOOD_DONATION,
    TYPE_HEALTH3DAYS,
    TYPE_HEALTH30DAYS,
    TYPE_HEALTH_MEDICAL_BOARD,
    TYPE_HEALTH_FAMILY_DESEASE,
    DEFERIDA,
    TYPE_HEALTHHOURS,
    TYPE_LICENSE_TRAINING,
    TYPE_LICENSE_SPECIAL_INTEREST,
    TYPE_LICENSE_POLITICAL_ACTIVITIES,
    TYPE_MATERNITY_LICENSE,
    TYPE_ABSENCE_DEATH,
    TYPE_ABSENCE_MARRIAGE,
)
from rh.pvf.const import *
from contrib.utils import DateUtils, getLogger
from auditlog.registry import auditlog

from contrib.daterange import NewDateRange


log = getLogger(__name__)


class HealthTreatmentAbsence(PortalRequestAbsence):
    medical_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_healthtreatmentabsences",
    )
    cid = models.ForeignKey(
        CID,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_requests",
    )
    hours = models.IntegerField(verbose_name="Afastamento em horas", null=True)

    class Meta:
        verbose_name = "Licença Saúde"
        db_table = "pvf_absence_healthtreatment"

    def validate_medical_certificate(self, file):
        if not file:
            raise Exception("É obrigatório anexar o atestado médico.")
        return True

    def validate_days(self, days, hours):
        if not days and not hours:
            raise Exception("Informe a quantidade de dias ou de horas.")
        return True

    def validate_fields(self, start_date, end_date, file, days, hours):
        """Valida se o campos foram passados"""
        self.validate_start_date(start_date)
        self.validate_days(days, hours)
        self.validate_end_date(end_date)
        self.validate_medical_certificate(file)

    def set_type_lincense(self):
        if self.hours:
            self.type = TYPE_HEALTHHOURS
        elif (
            self.employee.type_by_possession in ["MBR", "MCM", "MEL"]
            and self.days <= 15
        ):
            self.type = TYPE_HEALTH30DAYS
        elif self.days <= 15:
            self.type = TYPE_HEALTH3DAYS
        else:
            self.type = TYPE_HEALTH_MEDICAL_BOARD

    @classmethod
    def set_portal_request_type(cls, employee, days, hours):
        if hours:
            return PORTAL_HEALTH_TYPE_HEALTHHOURS
        if (
            days
            and employee.type_by_possession not in ["MBR", "MCM", "MEL"]
            and int(days) <= 15
        ):
            return PORTAL_HEALTH_TREATMENT_SERVER_ABSENCE_TYPE
        elif days and int(days) <= 15:
            return PORTAL_HEALTH_TREATMENT_MEMBER_ABSENCE_TYPE
        else:
            return PORTAL_HEALTH_MEDICAL_BOARD_ABSENCE_TYPE

    @classmethod
    def set_certificate_lincese(cls, certificate_lincese):
        if certificate_lincese:
            return File.objects.get(pk=certificate_lincese)
        return None

    def validate(self, start_date, end_date, employee, file, days, hours):
        self.validate_fields(start_date, end_date, file, days, hours)
        self.validate_start_date_greater_end_date(start_date, end_date)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        days = kwargs.get("days")
        if validate_prevent:
            self.validate(
                self.start_date,
                self.end_date,
                self.employee,
                self.medical_certificate,
                days,
                self.hours,
            )
            self.set_days()
            self.set_type_lincense()
        kwargs = self._pop_before_save()
        super(HealthTreatmentAbsence, self).save(**kwargs)

    @classmethod
    def create_leave_health(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            with transaction.atomic():
                start_date = (
                    datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                    if params["start_date"]
                    else None
                )
                end_date = (
                    datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                    if params["end_date"]
                    else None
                )
                hours = int(params["hours"])
                days = params["days"]
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    start_date=start_date,
                    end_date=end_date,
                    portal_request_type=cls.set_portal_request_type(
                        employee, days, hours
                    ),
                    medical_certificate=cls.set_certificate_lincese(
                        params["medical_certificate"]
                    ),
                    cid=cls.set_cid(params["cid"]),
                    hours=hours,
                )

                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True, days=days)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            atestado_medico=self.medical_certificate,
            tipo=self.type,
            prazo_solicitado=self.days,
            prazo_concedido=self.days,
            aprovacao=DEFERIDA,
            cid=self.cid,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        if self.type == TYPE_HEALTHHOURS:
            instance.hours = self.hours
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save(validate_prevent=False)
        self.effectived_substitute()


class FamilyHealthTreatmentAbsence(PortalRequestAbsence):
    medical_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_familyhealthtreatmentabsences",
    )
    person = models.ForeignKey(
        Person,
        related_name="pvf_familyhealthtreatmentabsences",
        on_delete=models.CASCADE,
    )
    degree_kinship = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Tipo de Vínculo",
        default=10,
    )
    cid = models.ForeignKey(
        CID,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_familyhealthtreatmentabsences",
    )

    class Meta:
        verbose_name = "Licença Saúde (Pessoa da Família)"
        db_table = "pvf_absence_familyhealthtreatment"

    @property
    def person_name(self):
        return self.person.nome

    @property
    def degree_kinship_label(self):
        return self.get_degree_kinship_display()

    def validate_medical_certificate(self, file):
        if not file:
            raise Exception("É obrigatório anexar o atestado médico.")
        return True

    def validate_person(self, person):
        if not person:
            raise Exception("Informe o familiar")
        return True

    @property
    def tipo_label_lincenca(self):
        if self.days >= 6:
            return TYPE_DOENCA_PESSOA_FAMILIA_JUNTA_MEDICA
        return TYPE_HEALTH_FAMILY_DESEASE

    @classmethod
    def tipo_lincenca_pessoa_familia(cla, days):
        if days >= 6:
            return PORTAL_DOENCA_PESSOA_FAMILIA_JUNTA_MEDICA_TYPE
        return PORTAL_HEALTH_FAMILY_DESEASE_TYPE

    def validate_fields(self, start_date, end_date, file, person, days):
        self.validate_medical_certificate(file)
        self.validate_person(person)
        self.validate_start_date(start_date)
        self.validate_days(days)
        self.validate_end_date(end_date)

    @classmethod
    def set_certificate_lincese(cls, certificate_lincese):
        if certificate_lincese:
            return File.objects.get(pk=certificate_lincese)
        return None

    def validate(self, start_date, end_date, employee, file, person, days):
        self.validate_fields(start_date, end_date, file, person, days)
        self.validate_start_date_greater_end_date(start_date, end_date)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        days = kwargs.get("days")
        if validate_prevent:
            person = self.person if self.person_id else None
            self.validate(
                self.start_date,
                self.end_date,
                self.employee,
                self.medical_certificate,
                person,
                days,
            )
            self.set_days()
        kwargs = self._pop_before_save()
        super(FamilyHealthTreatmentAbsence, self).save(**kwargs)

    @classmethod
    def create_family_health(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            with transaction.atomic():
                start_date = (
                    datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                    if params["start_date"]
                    else None
                )
                end_date = (
                    datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                    if params["end_date"]
                    else None
                )
                days = params["days"]
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_HEALTH_FAMILY_DESEASE,
                    start_date=start_date,
                    end_date=end_date,
                    portal_request_type=cls.tipo_lincenca_pessoa_familia(days),
                    person=(
                        Person.objects.get(pk=params["person"])
                        if params["person"]
                        else None
                    ),
                    degree_kinship=(
                        params["degree_kinship"] if params["degree_kinship"] else 10
                    ),
                    medical_certificate=cls.set_certificate_lincese(
                        params["medical_certificate"]
                    ),
                    cid=cls.set_cid(params["cid"]),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True, days=days)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            atestado_medico=self.medical_certificate,
            tipo=self.type,
            aprovacao=DEFERIDA,
            grau_parentesco=self.degree_kinship,
            acompanhado=self.person,
            prazo_solicitado=self.days,
            prazo_concedido=self.days,
            remunerado=False,
            publicacao_movimentacao=published,
            cid=self.cid,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class TrainingAbsence(PortalRequestAbsence):
    curse = models.ForeignKey(
        Curse,
        on_delete=models.PROTECT,
        related_name="pvf_trainingabsences",
        null=True,
        blank=True,
    )
    institution = models.ForeignKey(
        AdministrativeUnit,
        on_delete=models.PROTECT,
        related_name="pvf_trainingabsences",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Licença Capacitação"
        db_table = "pvf_absence_training"

    def validate_curse(self, curse):
        if not curse:
            raise Exception("Informe o Curso.")
        return True

    def validate_institution(self, institution):
        if not institution:
            raise Exception("Informe a Instituição.")
        return True

    def validate_publication(self, publication):
        if not publication:
            raise Exception("Informe a Publicação.")
        return True

    def validate_fields(self, start_date, end_date, curse, institution):
        self.validate_curse(curse)
        self.validate_institution(institution)
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)

    def validate(self, start_date, end_date, employee, curse, institution):
        self.validate_fields(start_date, end_date, curse, institution)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            self.validate(
                self.start_date,
                self.end_date,
                self.employee,
                self.curse,
                self.institution,
            )
            self.set_days()
        kwargs = self._pop_before_save()
        super(TrainingAbsence, self).save(**kwargs)

    @classmethod
    def create_training(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_LICENSE_TRAINING,
                    start_date=start_date,
                    end_date=end_date,
                    curse=(
                        Curse.objects.get(pk=params["curse"])
                        if params["curse"]
                        else None
                    ),
                    institution=(
                        AdministrativeUnit.objects.get(pk=params["institution"])
                        if params["institution"]
                        else None
                    ),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        self.validate_publication(publication)
        published = self.published(publication)
        instance = eval(self.get_type_display())
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            tipo=self.type,
            curso=self.curse,
            publicacao_movimentacao=published,
            instituicao=self.institution,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class MaternityAbsence(PortalRequestAbsence):
    birth_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_maternityabsences",
    )
    dependent = models.ForeignKey(
        Person,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_maternityabsences",
    )
    is_childcare_assistence = models.BooleanField(
        "Dependente do Auxílio Creche", default=False
    )
    is_incoming_tax = models.BooleanField("Dependente do IR", default=False)
    capacity = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CAPACITY"), null=True, default=1
    )
    incapacity = models.BooleanField(
        default=False, blank=True, verbose_name="Incapacidade física/mental"
    )
    dependent_type = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        verbose_name="Tipo",
        null=True,
        blank=True,
    )
    classificacao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CLASSIFICACAO_LICENCA_MATERNIDADE"),
        null=True,
        default=1,
    )

    class Meta:
        verbose_name = "Licença Maternidade"
        db_table = "pvf_absence_maternity"

    @property
    def dependent_name(self):
        if self.dependent:
            return self.dependent.nome
        return None

    @property
    def capacity_label(self):
        return self.get_capacity_display()

    @property
    def dependent_type_label(self):
        return self.get_dependent_type_display()

    def validate_birth_certificate(self):
        if not self.birth_certificate:
            raise Exception("Informe a certidão de nascimento ou atestado.")
        return True

    def validate_dependent(self):
        if (
            not self.dependent
            and self.classificacao == CLASSIF_LICENCA_MATERNIDADE_NORMAL
        ):
            raise Exception("Informe o Dependente.")
        return True

    def validate_dependent_year(self):
        if self.dependent:
            if self.dependent.idade > CHILD_AGE_LIMIT:
                raise Exception("O dependente(filho) não pode ter mais que 6 anos.")
        else:
            raise Exception("Dependente sem data de nascimento cadastrada.")

    def validate_fields(self):
        self.validate_dependent()
        self.validate_birth_certificate()
        self.validate_start_date(self.start_date)
        self.validate_end_date(self.end_date)
        self.validate_conflict_employee_dependent(self.dependent)

    def validate(self):
        self.validate_fields()
        self.validate_substitute_conflict_period(
            self.start_date, self.end_date, self.employee
        )
        self.validate_conflict_dependent(self.dependent)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            self.validate()
            self.set_days()
        kwargs = self._pop_before_save()
        super(MaternityAbsence, self).save(**kwargs)

    @classmethod
    def create_maternity(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            dependent_id = params["dependent"] if params["dependent"] != None else None
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_MATERNITY_LICENSE,
                    start_date=start_date,
                    end_date=end_date,
                    classificacao=params["classificacao"],
                    portal_request_type=PORTAL_MATERNITY_LICENSE_TYPE,
                    birth_certificate=(
                        File.objects.get(pk=params["birth_certificate"])
                        if params["birth_certificate"]
                        else None
                    ),
                    dependent=(
                        Person.objects.get(pk=dependent_id) if dependent_id else None
                    ),
                    capacity=params["capacity"] if params["capacity"] else 1,
                    incapacity=True if params["incapacity"] else False,
                    dependent_type=(
                        params["dependent_type"] if params["dependent_type"] else None
                    ),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def get_usufrutos_conflitantes(self):
        usufrutos_conflitantes = (
            Usufruct.objects.filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                activity__acquisition_period__employee=self.employee,
            )
            .exclude(
                status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                ]
            )
            .order_by("start_date")
        )
        return usufrutos_conflitantes

    def get_afastamentos_conflitantes(self):
        afastamentos_conflitantes = BaseLicencaAfastamento.objects.filter(
            data_inicio__lte=self.end_date,
            data_fim__gte=self.start_date,
            servidor=self.employee,
        ).exclude(estado=CANCELADO)
        return afastamentos_conflitantes

    def suspender_usufruto(self, usufruto):
        dt_fim = self.start_date - timedelta(days=1)
        usu_suspensao = [
            {
                "start_date": DateUtils.date_to_str(usufruto.start_date),
                "end_date": DateUtils.date_to_str(dt_fim),
            }
        ]
        usu_modificado = [usufruto.pk]
        ActivitySuspend.do(
            acquisition_period=usufruto.acquisition_period,
            usufructs_in=usu_suspensao,
            modifieds=usu_modificado,
        )

    def remarcar_usufruto(self, usufruto, dt_referencia_fim, suspensao=False):
        inicio_usufruto = self.start_date if suspensao else usufruto.start_date
        dias = NewDateRange(inicio_usufruto, usufruto.end_date).days

        dt_inicio = (
            dt_referencia_fim + timedelta(days=1)
            if dt_referencia_fim
            else self.end_date + timedelta(days=1)
        )
        dt_fim = dt_inicio + timedelta(days=(dias - 1))

        usu_marcacao = [
            {
                "start_date": DateUtils.date_to_str(dt_inicio),
                "end_date": DateUtils.date_to_str(dt_fim),
            }
        ]

        atividade = ActivityBookSell.do(
            acquisition_period=usufruto.acquisition_period,
            usufructs_in=usu_marcacao,
            modifieds=[],
            authorize=True,
        )

        return atividade.usufructs.first()

    def cancelar_usufruto(self, usufruto):
        ActivityCancel.do(
            acquisition_period=usufruto.acquisition_period, modified=usufruto.pk
        )

    def acoes_usufrutos(self):
        usufrutos = self.get_usufrutos_conflitantes()
        dt_referencia_fim = None
        for usu in usufrutos:
            tp_usufruto = (
                usu.acquisition_period.group_period.configuration.sub_type_of_usufruct
            )
            tp_usufruto_ferias = tp_usufruto in [REGULAR_VACATIONS, INDIVIDUAL_VACATION]
            if usu.start_date < self.start_date:
                self.suspender_usufruto(usu)
                if tp_usufruto_ferias:
                    usu_marcado = self.remarcar_usufruto(
                        usu, dt_referencia_fim, suspensao=True
                    )
                    dt_referencia_fim = usu_marcado.end_date
            else:
                self.cancelar_usufruto(usu)
                if tp_usufruto_ferias:
                    usu_marcado = self.remarcar_usufruto(
                        usu, dt_referencia_fim, suspensao=False
                    )
                    dt_referencia_fim = usu_marcado.end_date

    def acoes_afastamentos(self):
        afastamentos = self.get_afastamentos_conflitantes()
        for afastamento in afastamentos:
            if afastamento.data_inicio < self.start_date:
                afastamento.data_fim = self.start_date - timedelta(days=1)
                afastamento.alteracao = INTERRUPCAO
                afastamento.save()
            else:
                afastamento.alteracao = CANCELADO
                afastamento.save()

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        self.validate_date_of_birth()
        self.acoes_usufrutos()
        self.acoes_afastamentos()
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            aprovacao=DEFERIDA,
            prazo_concedido=self.days,
            crianca=self.dependent,
            publicacao_movimentacao=published,
            classification=self.classificacao,
            documento_solicitacao=self.birth_certificate,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()
        if self.dependent:
            self.create_dependent()


class PaternityAbsence(PortalRequestAbsence):
    birth_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_paternityabsences",
    )
    dependent = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="pvf_paternityabsences",
    )
    is_childcare_assistence = models.BooleanField(
        "Dependente do Auxílio Creche", default=False
    )
    is_incoming_tax = models.BooleanField("Dependente do IR", default=False)
    capacity = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CAPACITY"), null=True, default=1
    )
    incapacity = models.BooleanField(
        default=False, blank=True, verbose_name="Incapacidade física/mental"
    )
    dependent_type = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        verbose_name="Tipo",
        null=True,
        blank=True,
    )

    deadline = {"days": 20}

    class Meta:
        verbose_name = "Licença Paternidade"
        db_table = "pvf_absence_paternity"

    @property
    def dependent_name(self):
        return self.dependent.nome

    @property
    def capacity_label(self):
        return self.get_capacity_display()

    @property
    def dependent_type_label(self):
        return self.get_dependent_type_display()

    def validate_birth_certificate(self, birth_certificate):
        if not birth_certificate:
            raise Exception("Informe a certidão de Nascimento.")
        return True

    def validate_dependent(self, dependent):
        if not dependent:
            raise Exception("Informe o Dependente.")
        return True

    def validate_dependent_year(self, dependent):
        person = PessoaFisica.objects.get(pk=dependent)
        if person.data_nascimento:
            if person.idade > CHILD_AGE_LIMIT:
                raise Exception("O dependente(filho) não pode ter mais que 6 anos.")
        else:
            raise Exception("Dependente sem data de nascimento cadastrada.")

    def validate_fields(self, start_date, end_date, birth_certificate, dependent):
        self.validate_dependent(dependent)
        self.validate_birth_certificate(birth_certificate)
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)
        self.validate_conflict_employee_dependent(dependent)

    def validate(self, start_date, end_date, employee, birth_certificate, dependent):
        self.validate_fields(start_date, end_date, birth_certificate, dependent)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)
        self.validate_conflict_dependent(dependent)
        self.validate_max_days()

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            dependent = self.dependent if self.dependent_id else None
            self.validate(
                self.start_date,
                self.end_date,
                self.employee,
                self.birth_certificate,
                dependent,
            )
            self.set_days()
        kwargs = self._pop_before_save()
        super(PaternityAbsence, self).save(**kwargs)

    @classmethod
    def create_paternity(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_ABSENCE_BIRTH,
                    start_date=start_date,
                    end_date=end_date,
                    portal_request_type=PORTAL_ABSENCE_BIRTH_TYPE,
                    birth_certificate=(
                        File.objects.get(pk=params["birth_certificate"])
                        if params["birth_certificate"]
                        else None
                    ),
                    dependent=(
                        Person.objects.get(pk=params["dependent"])
                        if params["dependent"]
                        else None
                    ),
                    capacity=params["capacity"] if params["capacity"] else 1,
                    incapacity=True if params["incapacity"] else False,
                    dependent_type=(
                        params["dependent_type"] if params["dependent_type"] else None
                    ),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        self.validate_date_of_birth()
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            crianca=self.dependent,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()
        self.create_dependent()


class MourningAbsence(PortalRequestAbsence):
    death_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_deathmourningabsences",
    )
    family_bond = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Tipo de Vínculo",
        default=10,
    )
    person = models.ForeignKey(
        Person, related_name="pvf_mourningabsences", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Licença Luto"
        db_table = "pvf_absence_mourning"

    deadline = {"days": 8}

    @property
    def family_bond_label(self):
        return self.get_family_bond_display()

    @property
    def person_name(self):
        return self.person.nome

    def validate_family_bond(self, family_bond):
        if not family_bond:
            raise Exception("Informe o grau de parentesco.")
        return True

    def validate_person(self, person):
        if not person:
            raise Exception("Informe o familiar.")
        return True

    def validate_fields(self, start_date, end_date, family_bond, person):
        self.validate_family_bond(family_bond)
        self.validate_person(person)
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)

    def validate(self, start_date, end_date, employee, family_bond, person):
        self.validate_fields(start_date, end_date, family_bond, person)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)
        self.validate_max_days()

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            person = self.person if self.person_id else None
            self.validate(
                self.start_date, self.end_date, self.employee, self.family_bond, person
            )
            self.set_days()
        kwargs = self._pop_before_save()
        super(MourningAbsence, self).save(**kwargs)

    @classmethod
    def create_mourning(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_ABSENCE_DEATH,
                    start_date=start_date,
                    end_date=end_date,
                    portal_request_type=PORTAL_ABSENCE_DEATH_TYPE,
                    death_certificate=(
                        File.objects.get(pk=params["death_certificate"])
                        if params["death_certificate"]
                        else None
                    ),
                    family_bond=params["family_bond"] if params["family_bond"] else 10,
                    person=(
                        Person.objects.get(pk=params["person"])
                        if params["person"]
                        else None
                    ),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            pessoa=self.person,
            vinculo=self.family_bond,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        person = instance.pessoa
        person.data_obito = self.start_date
        person.save()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class MarriageAbsence(PortalRequestAbsence):

    marriage_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_marriageabsences",
    )
    person = models.ForeignKey(
        Person, related_name="pvf_marriageabsences", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Licença para Casamento"
        db_table = "pvf_absence_marriage"

    deadline = {"days": 8}

    @property
    def person_name(self):
        return self.person.nome

    def validate_person(self, person):
        if not person:
            raise Exception("Informe o parceiro.")
        return True

    def validate_fields(self, start_date, end_date, person):
        self.validate_person(person)
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)

    def validate(self, start_date, end_date, employee, person):
        self.validate_fields(start_date, end_date, person)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)
        self.validate_max_days()

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            person = self.person if self.person_id else None
            self.validate(self.start_date, self.end_date, self.employee, person)
            self.set_days()
        kwargs = self._pop_before_save()
        super(MarriageAbsence, self).save(**kwargs)

    @classmethod
    def create_marriage(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_ABSENCE_MARRIAGE,
                    start_date=start_date,
                    end_date=end_date,
                    portal_request_type=PORTAL_ABSENCE_MARRIAGE_TYPE,
                    marriage_certificate=(
                        File.objects.get(pk=params["marriage_certificate"])
                        if params["marriage_certificate"]
                        else None
                    ),
                    person=(
                        Person.objects.get(pk=params["person"])
                        if params["person"]
                        else None
                    ),
                )
                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
                return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            conjuge=self.person,
            data_casamento=self.start_date,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class PrivateInterestAbsence(PortalRequestAbsence):

    class Meta:
        verbose_name = "Licença Interesse Particular"
        db_table = "pvf_afastamento_private"

    def validate_publication(self, publication):
        if not publication:
            raise Exception("Informe a Publicação.")
        return True

    def validate_fields(self, start_date, end_date):
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)

    def validate(self, start_date, end_date, employee):
        self.validate_fields(start_date, end_date)
        self.validate_start_date_greater_end_date(start_date, end_date)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            self.validate(self.start_date, self.end_date, self.employee)
            self.set_days()
        kwargs = self._pop_before_save()
        super(PrivateInterestAbsence, self).save(**kwargs)

    @classmethod
    def create_private_interest(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_LICENSE_SPECIAL_INTEREST,
                    start_date=start_date,
                    end_date=end_date,
                )

                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        self.validate_publication(publication)
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class PoliticalActivityAbsence(PortalRequestAbsence):
    elective_office = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CARGO_ELETIVO_CHOICES"),
        verbose_name="Cargo Eletivo",
        default=1,
    )
    political_party = models.CharField(
        verbose_name="Partido Político", max_length=100, default=""
    )
    location = models.ForeignKey(
        Localidade,
        related_name="pvf_politicalactivityabsences",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Licença Atividade Política"
        db_table = "pvf_absence_politicalactivity"

    def validate_elective_office(self, elective_office):
        if not elective_office:
            raise Exception("Informe o Cargo Eletivo.")
        return True

    def validate_political_party(self, political_party):
        if not political_party:
            raise Exception("Informe o Partido Político.")
        return True

    def validate_publication(self, publication):
        if not publication:
            raise Exception("Informe a Publicação.")
        return True

    def validate_fields(self, start_date, end_date, elective_office, political_party):
        self.validate_elective_office(elective_office)
        self.validate_political_party(political_party)
        self.validate_start_date(start_date)
        self.validate_end_date(end_date)

    def validate(
        self, start_date, end_date, employee, elective_office, political_party
    ):
        self.validate_fields(start_date, end_date, elective_office, political_party)
        self.validate_start_date_greater_end_date(start_date, end_date)
        self.validate_substitute_conflict_period(start_date, end_date, employee)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)

    def save(self, *args, **kwargs):
        validate_prevent = kwargs.get("validate_prevent", False)
        if validate_prevent:
            self.validate(
                self.start_date,
                self.end_date,
                self.employee,
                self.elective_office,
                self.political_party,
            )
            self.set_days()
        kwargs = self._pop_before_save()
        super(PoliticalActivityAbsence, self).save(**kwargs)

    @classmethod
    def create_political_activity(cls, params):
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:
            start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            end_date = (
                datetime.strptime(params["end_date"], "%d/%m/%Y").date()
                if params["end_date"]
                else None
            )
            with transaction.atomic():
                instance = cls(
                    employee=employee,
                    request_type=REQUEST_TYPE_ABSENCE,
                    date=date_request,
                    request=user,
                    type=TYPE_LICENSE_POLITICAL_ACTIVITIES,
                    start_date=start_date,
                    end_date=end_date,
                    elective_office=(
                        params["elective_office"] if params["elective_office"] else 1
                    ),
                    political_party=(
                        params["political_party"] if params["political_party"] else ""
                    ),
                    location=(
                        Localidade.objects.get(pk=params["location"])
                        if params["location"]
                        else None
                    ),
                )

                instance.approval_flow(params["substitutes"])
                instance.save(validate_prevent=True)
                PortalRequestSubstitute.create_substitute(
                    substitutes=params["substitutes"],
                    request=instance,
                    interval_dates={
                        "date_absence": [
                            {"start_date": start_date, "end_date": end_date}
                        ]
                    },
                    total_days=NewDateRange(start_date, end_date).days,
                )
                PortalRequestHistory.create_history(
                    observation=params["observation"],
                    action=REQUEST_ACT_SOLICITATION,
                    request=instance,
                    date=datetime.now(),
                    group=None,
                    user=user,
                )
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """Efetiva a Solicitação de Licença"""
        self.validate_publication(publication)
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            data_prevista=self.end_date,
            tipo=self.type,
            cargo_eletivo=self.elective_office,
            partido=self.political_party,
            localidade=self.location,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()


class BloodDonationAbsence(PortalRequestAbsence):
    blood_donation_certificate = models.ForeignKey(
        File,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="pvf_blood_donation_certificate",
    )

    class Meta:
        verbose_name = "Licença de Doação de Sangue"
        db_table = "pvf_absence_blood_donation"

    @classmethod
    def set_comprobation_document(cls, comprobation_doc):
        """
        Criação de isntância de documento de comprovação de doação de sangue
        """
        if comprobation_doc:
            return File.objects.get(pk=comprobation_doc)
        return None

    def validate(self, start_date, end_date, employee):
        self.validate_start_date_greater_end_date(start_date, end_date)
        self.validate_usufruct_conflict(start_date, end_date, employee)
        self.validate_absence_conflict(start_date, end_date, employee)
        self.validate_substitute_conflict_period(start_date, end_date, employee)

    @classmethod
    def create_absence(cls, params):
        """
        Metodo para criação de Afastamento de Doação de Sangue
        """
        employee = get_current_user().servidor
        user = get_current_user()
        date_request = datetime.today().date()
        try:

            end_date = start_date = (
                datetime.strptime(params["start_date"], "%d/%m/%Y").date()
                if params["start_date"]
                else None
            )
            days = params["days"]
            instance = cls(
                employee=employee,
                request_type=REQUEST_TYPE_ABSENCE,
                type=TYPE_ABSENCE_BLOOD_DONATION,
                portal_request_type=PORTAL_BLOOD_DONATION_ABSENCE_TYPE,
                date=date_request,
                request=user,
                start_date=start_date,
                end_date=end_date,
                days=days,
                blood_donation_certificate=cls.set_comprobation_document(
                    params["blood_donation_certificate"]
                ),
            )
            instance.validate(instance.start_date, instance.end_date, employee)

            instance.approval_flow(instance, params["substitutes"])
            instance.save()
            PortalRequestSubstitute.create_substitute(
                substitutes=params["substitutes"],
                request=instance,
                interval_dates={
                    "date_absence": [{"start_date": start_date, "end_date": end_date}]
                },
                total_days=NewDateRange(start_date, end_date).days,
            )
            PortalRequestHistory.create_history(
                observation=params["observation"],
                action=REQUEST_ACT_SOLICITATION,
                request=instance,
                date=datetime.now(),
                group=None,
                user=user,
            )
            return instance
        except Exception as ex:
            raise Exception(ex)

    def effectived(self, publication):
        """
        Efetiva a Solicitação de Licença
        """
        instance = eval(self.get_type_display())
        published = self.published(publication)
        instance = instance(
            servidor=self.employee,
            data_inicio=self.start_date,
            data_fim=self.end_date,
            tipo=self.type,
            publicacao_movimentacao=published,
            origin_register=1,  # Origem = VDF
        )
        instance.texto = instance.get_texto()
        instance.save()
        self.absence = instance
        self.save()
        self.effectived_substitute()
        self.create_blood_donation_usufruct()

    def create_blood_donation_usufruct(self):
        """
        Cria um novo período de usufruto de doação de sangue para o ano corrente.

        Este método calcula as datas de início e fim para o novo período de aquisição,
        recupera o período de grupo correspondente e cria um novo período de aquisição
        e anexo no banco de dados. O novo período de aquisição está associado ao
        funcionário atual e tem um status de 'Em andamento'. A descrição do período de
        aquisição é gerada com base nas datas de início e fim. O anexo é associado ao
        novo período de aquisição e tem um valor padrão de 1 para o campo 'days_law'.

        """
        if self.employee.type_by_possession in ["EFE", "ECM", "EFC", "CMS", "EST"]:
            reference_date = self.start_date
            start_date_acquisition = datetime(reference_date.year, 1, 1).date()

            start_date_fruition = start_date_acquisition
            end_date_acquisition = datetime(reference_date.year, 12, 31).date()

            description = (
                start_date_acquisition.strftime("%d/%m/%Y")
                + " - "
                + end_date_acquisition.strftime("%d/%m/%Y")
            )

            group_period = GroupPeriod.objects.filter(
                configuration_id=ID_CONFIG_DOACAO_SANGUE_SERVIDOR,
                year_reference=reference_date.year,
            ).first()

            acquisition_period, _ = AcquisitionPeriod.objects.get_or_create(
                start_date_acquisition=start_date_acquisition,
                start_date_fruition=start_date_fruition,
                end_date_acquisition=end_date_acquisition,
                group_period=group_period,
                employee=self.employee,
                defaults={
                    "automatic_created": True,
                    "real_days_cache": 0,
                    "days_to_enjoy_cache": 0,
                    "days_not_booked_cache": 0,
                    "days": 0,
                    "suspended_days": 0,
                    "paid_days_cache": 0,
                    "status": 2,  # Em andamento
                    "pendency": False,
                    "continuous_period": False,
                    "blocked": False,
                    "description": description,
                },
            )
            __, ___ = AcquisitionPeriodAttachment.objects.get_or_create(
                date_start=datetime(
                    self.start_date.year, self.start_date.month, self.start_date.day
                ).date(),
                date_end=datetime(
                    self.end_date.year, self.end_date.month, self.end_date.day
                ).date(),
                acquisition_period=acquisition_period,
                defaults={
                    "days_law": 1,
                    "description": f"{self}",
                },
            )


auditlog.register(HealthTreatmentAbsence)
auditlog.register(FamilyHealthTreatmentAbsence)
auditlog.register(TrainingAbsence)
auditlog.register(MaternityAbsence)
auditlog.register(PaternityAbsence)
auditlog.register(MarriageAbsence)
auditlog.register(MourningAbsence)
auditlog.register(BloodDonationAbsence)
