# -*- coding: utf-8 -*-

# from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta

from django.db import models
from django.db.models import Max, Q


from contrib.middleware import get_current_user
from contrib.utils import DateUtils, getLogger
from engine.models import ControllerPermission, Group
from engine.notification.models import Notification
from ged.models import Arquivo
from rh.const import CANCELED, SCHEDULED
from rh.models import Endereco, Pais, PessoaJuridica
from standard.models import AuditTimestampModel
from standard.models import Configuration as Conf

log = getLogger(__name__)

DAY_WEEK = (
    (0, "Não informado"),
    (1, "SEGUNDA-FEIRA"),
    (2, "TERÇA-FEIRA"),
    (3, "QUARTA-FEIRA"),
    (4, "QUINTA-FEIRA"),
    (5, "SEXTA-FEIRA"),
    (6, "SÁBADO"),
    (7, "DOMINGO"),
)

STATUS_INFORMATION = (
    (1, "ATIVO"),
    (2, "FINALIZADO"),
)

STATUS_MODIFICATION = (
    (1, "NÃO ALTERADO"),
    (2, "ALTERADO"),
)

STATUS_PENDENCY = (
    (1, "SEM PENDÊNCIA"),
    (2, "COM PENDÊNCIA"),
)

TYPE_RESIDENCE = (
    (1, "CASA"),
    (2, "APARTAMENTO"),
    (3, "HOTEL"),
)

KIND = (
    (1, "INDIVIDUAL"),
    (2, "CÔNJUGE"),
    (3, "DEPENDENTE"),
)

STATUS_PERIOD = (
    (1, "ATIVO"),
    (2, "INATIVO"),
)

MODALITY = (
    (1, "PRESENCIAL"),
    (2, "EAD"),
)


class EducationalInstitution(PessoaJuridica):
    """INSTITUIÇÃO DE ENSINO"""

    class Meta:
        pass

    county = models.ForeignKey(
        "rh.Localidade", null=True, blank=False, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s - %s - %s " % (
            self.nome,
            self.razao_social,
            self.county,
        )


class Discipline(AuditTimestampModel):
    """DISCIPLINA"""

    class Meta:
        pass

    name = models.CharField(max_length=350, unique=True, verbose_name="Nome")

    def __str__(self):
        return "%s" % self.name


class Schedule(AuditTimestampModel):
    """HORÁRIO DE AULAS"""

    class Meta:
        ordering = ("day_week",)

    day_week = models.SmallIntegerField(
        null=True, blank=True, default=0, choices=DAY_WEEK, verbose_name="Dia da Semana"
    )
    start_time = models.TimeField(auto_now_add=False, verbose_name="Hora Início")
    end_time = models.TimeField(auto_now_add=False, verbose_name="Hora Fim")

    def __str__(self):
        return "%s - %s às %s " % (
            self.get_day_week_display(),
            self.start_time,
            self.end_time,
        )


class ReferencePeriod(AuditTimestampModel):
    """PERÍODO DE EXERCÍCIO"""

    class Meta:
        ordering = ("-id",)

    previous_referenceperiod = models.ForeignKey(
        "ReferencePeriod",
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Período Anterior",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    exercise = models.CharField(
        max_length=50,
        default="0",
        null=True,
        blank=True,
        verbose_name="Período de Exercício",
    )
    exercise_year = models.IntegerField(
        default=0, null=True, blank=True, verbose_name="Período de Exercício"
    )
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Data Início Exercício"
    )
    end_date = models.DateField(
        null=True, blank=True, verbose_name="Data Fim Exercício"
    )
    main_period = models.BooleanField(
        default=False, verbose_name="Período de referência principal"
    )
    status_period = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_PERIOD,
        verbose_name="Status do período",
    )
    # STATUS_PERIOD

    def __str__(self):
        return "%s - %s à %s " % (
            self.exercise,
            DateUtils.date_to_str(self.start_date),
            DateUtils.date_to_str(self.end_date) if self.end_date else "Não informada",
        )

    def save(self, *args, **kwargs):
        if self.previous_referenceperiod and not self.previous_referenceperiod.end_date:
            ReferencePeriod.objects.filter(pk=self.previous_referenceperiod.pk).update(
                end_date=self.start_date - timedelta(1)
            )
        if self.exercise:
            if "/" in self.exercise:
                self.exercise_year = self.exercise.split("/")[0]
            else:
                self.exercise_year = self.exercise
        super(ReferencePeriod, self).save(*args, **kwargs)


class ControlInformationMember(AuditTimestampModel):
    """GESTOR DE CONTROLE DAS INFORMAÇÕES DOS MEMBROS"""

    class Meta:
        ordering = ("employee__servidor",)
        permissions = (
            ("cif_admin", "Administrador de Informações Membros"),
            ("cif_membro", "Membro usuário"),
            ("cif_auditoria", "Auditoria do Sistema"),
        )

    previous_controlinformation = models.ForeignKey(
        "ControlInformationMember",
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Controle Anterior",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        "rh.MovimentacaoPosse",
        verbose_name="Membro",
        related_name="controlinformation",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    referenceperiod = models.ForeignKey(
        ReferencePeriod,
        related_name="controlinformation",
        verbose_name="Período de Referência",
        on_delete=models.PROTECT,
    )
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_INFORMATION,
        verbose_name="Status",
    )
    flag_not_exercise_teaching = models.BooleanField(
        default=False, verbose_name="Não exerce atividade de docência"
    )
    lock_teaching = models.BooleanField(
        default=False, verbose_name="Bloqueio para Docência"
    )
    lock_address = models.BooleanField(
        default=False, verbose_name="Bloqueio para Endereço"
    )
    lock_property = models.BooleanField(
        default=False, verbose_name="Bloqueio para Bens"
    )
    lock_debts = models.BooleanField(
        default=False, verbose_name="Bloqueio para Dívidas"
    )

    pendency_teaching = models.BooleanField(
        default=False, verbose_name="Pendência em docência"
    )
    pendency_address = models.BooleanField(
        default=False, verbose_name="Pendência em endereço"
    )
    pendency_property = models.BooleanField(
        default=False, verbose_name="Pendência em bens"
    )
    pendency_debts = models.BooleanField(
        default=False, verbose_name="Pendência em debitos"
    )

    def __str__(self):
        return "%s - %s" % (
            self.referenceperiod,
            self.employee.servidor,
        )

    class ControlInformationInactive(Exception):
        def __init__(self):
            Exception.__init__(self, "Essas informações não podem mais ser alteradas!")

    @property
    def deadline_teaching(self):
        conf = Conf.objects.get(application="cif")
        deadline = conf.itens.get(key="deadline_teaching").value
        return DateUtils.str_to_date(deadline) if deadline else None

    @property
    def deadline_address(self):
        conf = Conf.objects.get(application="cif")
        deadline = conf.itens.get(key="deadline_address").value
        return DateUtils.str_to_date(deadline) if deadline else None

    @property
    def deadline_property(self):
        conf = Conf.objects.get(application="cif")
        deadline = conf.itens.get(key="deadline_property").value
        return DateUtils.str_to_date(deadline) if deadline else None

    @property
    def deadline_debtsencumbrances(self):
        conf = Conf.objects.get(application="cif")
        deadline = conf.itens.get(key="deadline_debtsencumbrances").value
        return DateUtils.str_to_date(deadline) if deadline else None

    @property
    def is_active(self):
        return True if int(self.status) == 1 else False

    def validate(self):
        """Valida se o periodo de referencia está ativo e permite alterações"""
        if not self.is_active:
            raise Exception(self.ControlInformationInactive())

    @property
    def get_state_icons(self):
        icons = []
        if int(self.status) == 1:
            icons.append(
                {"iconCls": "icon-cif icon-cif-active", "title": "Período Ativo"}
            )
        elif int(self.status) == 2:
            icons.append(
                {"iconCls": "icon-cif icon-cif-inactive", "title": "Período Inativo"}
            )

        return icons

    def exists_license(self):
        data = datetime.now().date()
        return (
            self.employee.servidor.get_afastamentos(data)
            .filter(baselicencaafastamento__desempenhofuncao=None)
            .exclude(baselicencaafastamento__estado__in=[SCHEDULED, CANCELED])
            .exists()
        )

    @property
    def is_license(self):
        icons = self.get_state_icons

        (
            icons.append(
                {
                    "iconCls": "icon-cif icon-cif-medal-bronze",
                    "title": "Possui afastamento ativo.",
                }
            )
            if self.exists_license()
            else icons.append({"iconCls": "icon-cif icon-cif-blank", "title": ""})
        )

        return icons

    @property
    def get_icons_teaching(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-book-minus",
                "title": "Nenhuma atividade de Docência cadastrada!",
            }
            if not self.flag_not_exercise_teaching and not self.teaching.exists()
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def get_icons_address(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-home-minus",
                "title": "Nenhum Endereço cadastrado!",
            }
            if not self.address.exists()
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def get_icons_property(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-cash-minus",
                "title": "Nenhum Bem/Valor cadastrado!",
            }
            if not self.property.exists()
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def general_pendencies(self):
        icons = self.is_license
        icons.append(self.get_icons_teaching)
        icons.append(self.get_icons_address)
        icons.append(self.get_icons_property)

        return icons

    def get_pendendy_teaching(self):
        state_teaching = False
        if self.teaching.exists():
            for t in self.teaching.all():
                if t.exists_pendencies():
                    state_teaching = True

        if not self.teaching.filter(
            refperiod_teaching=ReferencePeriod.objects.filter(
                main_period=False, status_period=1
            )
        ).exists():
            state_teaching = True

        return state_teaching

    def get_pendency_address(self):
        state_address = False
        if self.address.exists():
            for a in self.address.all():
                if a.exists_pendencies():
                    state_address = True
        return state_address

    def get_pendency_property(self):
        state_property = False
        if self.property.exists():
            for p in self.property.all():
                if p.exists_pendencies():
                    state_property = True
        return state_property

    def get_pendency_debts(self):
        state_debts = False
        if self.debtsencumbrances.exists():
            for d in self.debtsencumbrances.all():
                if d.exists_pendencies():
                    state_debts = True
        return state_debts

    @property
    def get_pendency_(self):
        text_title = ""

        if self.get_pendendy_teaching():
            text_title += "*Há pendência em Docência <br>"
        if self.get_pendency_address():
            text_title += "*Há pendência em Endereço <br>"
        if self.get_pendency_property():
            text_title += "*Há pendência em Bens/Valores <br>"

        return (
            {"iconCls": "icon-cif icon-cif-warning", "title": "%s" % text_title}
            if len(text_title) > 0
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def get_icons_locks(self):
        text_title = ""
        if self.lock_teaching:
            text_title += "*Cadastro de Docência bloqueada <br>"
        if self.lock_address:
            text_title += "*Cadastro de Endereço bloqueado <br>"
        if self.lock_property:
            text_title += "*Cadastro de Bens e Valores bloqueado <br>"
        if self.lock_debts:
            text_title += "*Cadastro de Débitos e Ônus reais bloqueado <br>"

        return (
            {"iconCls": "icon-cif icon-cif-lock", "title": "%s" % text_title}
            if len(text_title) > 0
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def icons(self):
        lista = []
        lista = self.general_pendencies
        lista.append(self.get_pendency_)
        lista.append(self.get_icons_locks)
        return lista

    def notification_member(self, message=""):
        try:
            Notification.notify(
                "cif-notification-member",
                self.employee.servidor,
                sender=self,
                types=("SYS",),
                **{
                    "msg": message,
                }
            )
            # log.info('Notificando %s' % self.employee.servidor)
        except Exception as e:
            log.info(e)

    def notification_all_member(self, message=""):
        try:
            Notification.notify(
                "cif-notification-all-member",
                self.employee.servidor,
                sender=self,
                types=("SYS",),
                **{
                    "msg": message,
                }
            )
            # log.info('Notificando %s' % self.employee.servidor)
        except Exception as e:
            log.info(e)

    def notification_create_control(self, message=""):
        try:
            Notification.notify(
                "cif-create-control",
                self.employee.servidor,
                sender=self,
                types=("SYS",),
                **{
                    "period": self.referenceperiod,
                }
            )
            # log.info('Notificando %s' % self.employee.servidor)
        except Exception as e:
            log.info(e)

    def copy_controlinformation(self, old_information=None):
        # Cria um novo controle de informacoes referentes a um novo periodo para cada membro
        # Copia atividades de docencia de um controle anteiror para o novo controle
        if old_information:
            if old_information.teaching.exists():
                for old_teaching in old_information.teaching.all():
                    new_teaching = Teaching(
                        member=self,
                        educational_institution=old_teaching.educational_institution,
                        discipline=old_teaching.discipline,
                        work_hours=old_teaching.work_hours,
                        start_date=old_teaching.start_date,
                        end_date=old_teaching.end_date,
                        status_pendency=old_teaching.status_pendency,
                        refperiod_teaching=old_teaching.refperiod_teaching,
                    )
                    new_teaching.save()
                    if old_teaching.schedule.exists():
                        for sc in old_teaching.schedule.all():
                            new_teaching.schedule.add(sc)
                    new_teaching.save()

            # Copia endereços de um controle anteiror para o novo controle
            if old_information.address.exists():
                for old_address in old_information.address.all():
                    log.info(self.pk)
                    new_address = AddressCif(
                        previus_addres=old_address,
                        member=self,
                        start_date=old_address.start_date,
                        end_date=old_address.end_date,
                        type_residence=old_address.type_residence,
                        # municipio=old_address.municipio,
                        # logradouro=old_address.logradouro,
                        # tipo_logradouro=old_address.tipo_logradouro,
                        # numero=old_address.numero,
                        # complemento=old_address.complemento,
                        # bairro=old_address.bairro,
                        # cep=old_address.cep,
                        # tipo_endereco=old_address.tipo_endereco,
                        status_pendency=old_address.status_pendency,
                        refperiod_address=old_address.refperiod_address,
                        ref_address=old_address.ref_address,
                    )
                    new_address.save()

            # # Copia bens e valores para o novo controle
            if old_information.property.exists():
                for old_property in old_information.property.all():
                    new_property = Property(
                        member=self,
                        code=old_property.code,
                        country=old_property.country,
                        description=old_property.description,
                        current_value=old_property.current_value,
                        last_value=old_property.current_value,
                        refperiod_property=old_property.refperiod_property,
                        status_pendency=old_property.status_pendency,
                    )
                    new_property.save()

            # # Copia dividas e onus reais para o novo controle
            if old_information.debtsencumbrances.exists():
                for old_debts in old_information.debtsencumbrances.all():
                    new_debts = DebtsEncumbrances(
                        member=self,
                        code=old_debts.code,
                        description=old_debts.description,
                        current_value=old_debts.current_value,
                        last_value=old_debts.current_value,
                        refperiod_debts=old_debts.refperiod_debts,
                        status_pendency=old_debts.status_pendency,
                    )
                    new_debts.save()

    def save(self, *args, **kwargs):
        if self.pk is None:
            # self.notification_create_control()

            comissao_permission, created = ControllerPermission.objects.get_or_create(
                name="cif-membro"
            )
            comissao_permission.users.add(self.employee.servidor.user)
            group = Group.objects.get(name="cif-membro")
            self.employee.servidor.user.groups.add(group)

            if self.get_pendendy_teaching():
                self.pendency_property = True
            else:
                self.pendency_property = False
            if self.get_pendency_address():
                self.pendency_address = True
            else:
                self.pendency_address = False
            if self.get_pendency_property():
                self.pendency_property = True
            else:
                self.pendency_property = False
            if self.get_pendency_debts():
                self.pendency_debts = True
            else:
                self.pendency_debts = False

        super(ControlInformationMember, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if (
            self.teaching.exists()
            or self.property.exists()
            or self.address.exists()
            or self.debtsencumbrances.exists()
        ):
            raise Exception("Não é possível remover este membro!")
        super(ControlInformationMember, self).delete(*args, **kwargs)


class Teaching(AuditTimestampModel):
    """DOCÊNCIA"""

    class Meta:
        ordering = ("-id",)

    member = models.ForeignKey(
        ControlInformationMember,
        verbose_name="Membro",
        related_name="teaching",
        on_delete=models.PROTECT,
    )
    educational_institution = models.ForeignKey(
        EducationalInstitution,
        related_name="teaching",
        verbose_name="Instituição de Ensino",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    discipline = models.ForeignKey(
        Discipline,
        related_name="teaching",
        verbose_name="Disciplina",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    work_hours = models.SmallIntegerField(
        default="0", verbose_name="Carga Horária", null=True, blank=True
    )
    schedule = models.ManyToManyField(
        Schedule, related_name="teaching", verbose_name="Horários"
    )
    start_date = models.DateField(
        verbose_name="Data Início Docência", null=True, blank=True
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Data Fim Docência")
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_MODIFICATION,
        verbose_name="Status",
    )
    status_pendency = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_PENDENCY,
        verbose_name="Status Pendência",
    )
    file_document = models.ForeignKey(
        Arquivo,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Anexo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    authorization = models.BooleanField(
        default=True, verbose_name="Autorização para dar aula fora da comarca"
    )
    refperiod_teaching = models.ForeignKey(
        ReferencePeriod,
        null=True,
        blank=True,
        related_name="ref_teaching",
        verbose_name="Período de Referência",
        on_delete=models.PROTECT,
    )
    modality = models.SmallIntegerField(
        null=True, blank=True, default=0, choices=MODALITY, verbose_name="Modalidade"
    )

    MAX_WORKHOURS = 20
    WORK_INIT_AM = time(8, 0)
    WORK_FINISH_AM = time(12, 0)
    WORK_INIT_PM = time(14, 0)
    WORK_FINISH_PM = time(18, 0)

    def __str__(self):
        return "%s - %s - %s" % (
            self.member,
            self.educational_institution,
            self.discipline,
        )

    def get_schedules(self):
        sc = ""
        if self.schedule.exists():
            for s in self.schedule.all():
                t = "[%s ]" % s
                sc = sc + t
        return sc

    def exists_pendencies(self):
        return (
            True
            if self.is_schedules_conflict
            or self.is_between_workhours
            or self.is_out_referenceperiod
            or self.get_conflict_address_teaching
            or int(self.status) == 1
            else False
        )

    @property
    def is_out_referenceperiod(self):
        if (
            self.start_date
            and self.end_date
            and self.refperiod_teaching.status_period == 1
        ):
            return (
                False
                if self.start_date >= self.refperiod_teaching.start_date
                and self.end_date <= self.refperiod_teaching.end_date
                else True
            )
        else:
            return False

    @property
    def is_between_workhours(self):
        return (
            True
            if int(self.work_hours) > self.MAX_WORKHOURS
            and self.refperiod_teaching.status_period == 1
            else False
        )

    @property
    def get_conflict_address_teaching(self):
        if self.educational_institution and self.refperiod_teaching.status_period == 1:
            return (
                not self.member.employee.servidor.work_locations.filter(
                    localidade__pk__in=[self.educational_institution.county.pk],
                    ativo=True,
                ).exists()
                and not self.authorization
            )

    @property
    def icon_status(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-item-unchecked",
                "title": "Informação não confirmada.",
            }
            if int(self.status) == 1
            else {
                "iconCls": "icon-cif icon-cif-item-checked",
                "title": "Informação confirmada.",
            }
        )

    @property
    def icon_out_referenceperiod(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-date-go",
                "title": "Período de Docência informado fora do Período de Referência das informações",
            }
            if self.is_out_referenceperiod
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def icon_hours(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-clock-plus",
                "title": "Carga Horária superior a permitida em lei!",
            }
            if self.is_between_workhours
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def icon_conflict_address_teaching(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-home-exclamation",
                "title": "Endereço da Lotação no Sistema Athenas diverge da Instituição de Ensino!",
            }
            if self.get_conflict_address_teaching and not self.authorization
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def is_schedules_conflict(self):
        if not self.authorization:
            return (
                Schedule.objects.filter(teaching=self, day_week__in=[1, 2, 3, 4, 5])
                .exclude(
                    Q(start_time__gte=self.WORK_FINISH_PM)
                    | Q(end_time__isnull=False, end_time__lte=self.WORK_INIT_AM)
                )
                .exists()
            )
        else:
            return False

    @property
    def icon_workhours(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-clock-exclamation",
                "title": "Há horário de aula conflitante com as atividades no Ministério Público!",
            }
            if self.is_schedules_conflict
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def icon_not_teaching(self):
        if (
            not self.discipline
            and not self.educational_institution
            and not self.work_hours
        ):
            return {
                "iconCls": "icon-cif icon-cif-accept",
                "title": "Não Exerce Docência.",
            }
        else:
            return {"iconCls": "icon-cif icon-cif-blank", "title": ""}

    def validate_deadline(self):
        now = date.today()
        if self.member.deadline_teaching:
            if now > self.member.deadline_teaching and self.member.lock_teaching:
                raise Exception(
                    "Não é possível cadastrar/alterar essa informação pois ela está bloqueada e o prazo para preenchimento foi encerrado em: %s"
                    % DateUtils.date_to_str(self.member.deadline_teaching)
                )

    def validade_excercises_teaching(self):
        """Verifica se o membro exerce docência ou não."""
        if (
            self.status == 2
            and not self.educational_institution
            and not self.discipline
            and not self.schedule.exists()
        ):
            return False
        else:
            return True

    @property
    def text_not_teaching(self):
        return "O membro informou não exercer docência"

    @property
    def icons(self):
        lista = []
        lista.append(self.icon_status)
        lista.append(self.icon_not_teaching)
        lista.append(self.icon_conflict_address_teaching)
        lista.append(self.icon_hours)
        lista.append(self.icon_workhours)
        lista.append(self.icon_out_referenceperiod)

        return lista

    def save(self, *args, **kwargs):
        if self.refperiod_teaching.status_period != 1:
            raise Exception(
                "Não é possível alterar informações de um período que não esteja vigente!"
            )
        self.member.validate()
        self.validate_deadline()

        if self.exists_pendencies():
            self.status_pendency = 2
            self.member.pendency_teaching = True
            self.member.save()
        else:
            self.status_pendency = 1
            self.member.pendency_teaching = False
            self.member.save()

        super(Teaching, self).save(*args, **kwargs)


class AddressCif(AuditTimestampModel):
    """ENDEREÇO"""

    class Meta:
        ordering = ("-id",)

    previus_addres = models.ForeignKey(
        "AddressCif",
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Endereço Anterior",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    member = models.ForeignKey(
        ControlInformationMember,
        verbose_name="Membro",
        related_name="address",
        on_delete=models.PROTECT,
    )
    ref_address = models.ForeignKey(
        Endereco,
        related_name="cif_address",
        null=True,
        blank=True,
        verbose_name="Endereço",
        on_delete=models.PROTECT,
    )
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Data Início Residência"
    )
    end_date = models.DateField(
        null=True, blank=True, verbose_name="Data Fim Residência"
    )
    type_residence = models.SmallIntegerField(
        null=True,
        blank=True,
        default=0,
        choices=TYPE_RESIDENCE,
        verbose_name="Tipo de Residência",
    )
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_MODIFICATION,
        verbose_name="Status",
    )
    status_pendency = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_PENDENCY,
        verbose_name="Status Pendência",
    )
    file_document = models.ForeignKey(
        Arquivo,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Anexo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    refperiod_address = models.ForeignKey(
        ReferencePeriod,
        null=True,
        blank=True,
        related_name="ref_address",
        verbose_name="Período de Referência",
        on_delete=models.PROTECT,
    )
    block_change = models.BooleanField(
        default=False, verbose_name="Bloqueia a alteração da informação"
    )
    authorization_reside_outside = models.BooleanField(
        default=False, verbose_name="Autorização para residir fora da comarca"
    )

    def __str__(self):
        return "%s - %s - %s" % (
            self.member,
            DateUtils.date_to_str(self.start_date) if self.start_date else "",
            DateUtils.date_to_str(self.end_date) if self.end_date else "",
        )

    def exists_pendencies(self):
        return True if self.get_conflict_address or int(self.status) == 1 else False

    @property
    def posse_ativa(self):
        workplace_active = self.member.employee.servidor.workplace_only_active
        return workplace_active[0] if workplace_active.exists() else False

    @property
    def get_conflict_address(self):
        if not self.authorization_reside_outside:
            last_date = (
                AddressCif.objects.filter(member=self.member)
                .aggregate(Max("start_date"))
                .get("start_date__max")
            )
            if (
                not self.member.employee.servidor.work_locations.filter(
                    localidade__pk__in=[self.ref_address.municipio_id], ativo=True
                ).exists()
                and self.posse_ativa
            ):
                return (
                    False
                    if self.ref_address.municipio == self.posse_ativa.lotacao.localidade
                    else True
                )
            elif self.start_date and self.start_date == last_date:
                return not self.member.employee.servidor.work_locations.filter(
                    localidade__pk__in=[self.ref_address.municipio_id], ativo=True
                ).exists()
            else:
                return False
        else:
            return False

    def get_status_outside(self):
        if self.get_conflict_address:
            if self.authorization_reside_outside:
                return "SIM"
            else:
                return "NÃO"
        else:
            return ""

    @property
    def icon_conflict_address(self):
        _return = {}
        if self.get_conflict_address:
            _return = {
                "iconCls": "icon-cif icon-cif-home-exclamation",
                "title": "Endereço da Lotação no Sistema Athenas diverge do endereço informado!",
            }
        elif self.authorization_reside_outside:
            _return = {
                "iconCls": "icon-cif icon-cif-accept",
                "title": "Membro com permissão para residir fora da lotação.",
            }
        else:
            _return = {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        return _return

    @property
    def icon_block_unblock(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-lock",
                "title": "Informação bloqueada para alteração.",
            }
            if self.block_change
            else {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        )

    @property
    def icon_status(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-item-unchecked",
                "title": "Informação não confirmada.",
            }
            if int(self.status) == 1
            else {
                "iconCls": "icon-cif icon-cif-item-checked",
                "title": "Informação confirmada.",
            }
        )

    @property
    def icons(self):
        lista = [self.icon_block_unblock, self.icon_status, self.icon_conflict_address]
        return lista

    def validate_deadline(self):
        now = date.today()
        if self.member.deadline_address:
            if now > self.member.deadline_address and self.member.lock_address:
                raise Exception(
                    "Não é possível cadastrar/alterar essa informação pois ela está bloqueada e o prazo para preenchimento foi encerrado em: %s"
                    % DateUtils.date_to_str(self.member.deadline_address)
                )

    def address_already_registered(self):
        return (
            True if AddressCif.objects.filter(member=self.member).count() > 0 else False
        )

    def save(self, *args, **kwargs):
        self.member.validate()
        self.validate_deadline()

        if self.address_already_registered() and not self.pk:
            raise Exception("Já existe endereço cadastrado para este membro.")

        if self.block_change and not get_current_user().has_perm("cif.cif_admin"):
            raise Exception("Essa informação encontra-se bloqueada para alteração!")

        if self.pk:
            self.status = 2

        # self.status_pendency = 2 if self.exists_pendencies() else 1
        if self.exists_pendencies():
            self.status_pendency = 2
            self.member.pendency_address = True
            self.member.save()
        else:
            self.status_pendency = 1
            self.member.pendency_address = False
            self.member.save()

        if self.previus_addres and self.start_date:
            AddressCif.objects.filter(pk=self.previus_addres.pk).update(
                end_date=self.start_date - timedelta(1)
            )

        self.person = self.member.employee.servidor.pessoa_fisica.pessoa_ptr

        super(AddressCif, self).save(*args, **kwargs)


class CodeProperty(AuditTimestampModel):
    """CÓDIGO DE CLASSIFICAÇÃO CONFORME RECEITA"""

    class Meta:
        ordering = ("code",)

    code = models.SmallIntegerField(
        default="0", verbose_name="Código", null=True, blank=True
    )
    title = models.CharField(
        max_length=300, default="", verbose_name="Título", null=True, blank=True
    )

    def __str__(self):
        return "%s - %s" % (
            self.code,
            self.title,
        )


class Property(AuditTimestampModel):
    """BENS, RENDAS E VALORES"""

    class Meta:
        ordering = ("-id",)

    member = models.ForeignKey(
        ControlInformationMember,
        verbose_name="Membro",
        related_name="property",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    code = models.ForeignKey(
        CodeProperty,
        related_name="property",
        verbose_name="Código",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    country = models.ForeignKey(
        Pais, verbose_name="País", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField(
        default="", null=True, blank=True, verbose_name="Descrição"
    )
    kind = models.SmallIntegerField(
        null=True, blank=True, default=1, choices=KIND, verbose_name="TIPO DE BEM"
    )
    last_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="Última Situação (R$)",
    )
    current_value = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="Situação Atual (R$)"
    )
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_MODIFICATION,
        verbose_name="Status",
    )
    status_pendency = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_PENDENCY,
        verbose_name="Status Pendência",
    )
    file_document = models.ForeignKey(
        Arquivo,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Anexo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    refperiod_property = models.ForeignKey(
        ReferencePeriod,
        null=True,
        blank=True,
        related_name="ref_property",
        verbose_name="Período de Referência",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return "%s - %s" % (
            self.member,
            self.code,
        )

    def exists_pendencies(self):
        return True if int(self.status) == 1 else False

    @property
    def icon_status(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-item-unchecked",
                "title": "Informação não confirmada.",
            }
            if int(self.status) == 1
            else {
                "iconCls": "icon-cif icon-cif-item-checked",
                "title": "Informação confirmada.",
            }
        )

    @property
    def icon_kind(self):
        if self.code:
            if int(self.kind) == 1:
                return {"iconCls": "icon-cif icon-cif-member", "title": "Individual"}
            elif int(self.kind) == 2:
                return {"iconCls": "icon-cif icon-cif-users", "title": "Cônjuge"}
            elif int(self.kind) == 3:
                return {
                    "iconCls": "icon-cif icon-cif-user-group",
                    "title": "Dependente",
                }
            else:
                return {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        else:
            return {"iconCls": "icon-cif icon-cif-blank", "title": ""}

    @property
    def icons(self):
        lista = []
        lista.append(self.icon_status)
        lista.append(self.icon_kind)

        return lista

    def validate_deadline(self):
        now = date.today()
        if self.member.deadline_property:
            if now > self.member.deadline_property and self.member.lock_property:
                raise Exception(
                    "Não é possível cadastrar/alterar essa informação pois ela está bloqueada e o prazo para preenchimento foi encerrado em: %s"
                    % DateUtils.date_to_str(self.member.deadline_property)
                )

    def validade_exists_property(self):
        """Verifica se o membro possui bens ou não."""
        if self.status == 2 and not self.country and not self.code:
            return False
        else:
            return True

    @property
    def text_not_property(self):
        return "O membro informou não possuir bens e valores"

    def save(self, *args, **kwargs):
        self.member.validate()
        self.validate_deadline()

        if self.pk:
            self.status = 2

        # self.status_pendency = 2 if self.exists_pendencies() else 1
        if self.exists_pendencies():
            self.status_pendency = 2
            self.member.pendency_property = True
            self.member.save()
        else:
            self.status_pendency = 1
            self.member.pendency_property = False
            self.member.save()

        super(Property, self).save(*args, **kwargs)


class CodeDebtsEncumbrances(AuditTimestampModel):
    """CÓDIGO DE CLASSIFICAÇÃO CONFORME RECEITA"""

    class Meta:
        ordering = ("code",)

    code = models.SmallIntegerField(
        default="0", null=True, blank=True, verbose_name="Código"
    )
    title = models.CharField(
        max_length=300, default="", null=True, blank=True, verbose_name="Título"
    )

    def __str__(self):
        return "%s - %s" % (
            self.code,
            self.title,
        )


class DebtsEncumbrances(AuditTimestampModel):
    """DIVIDAS E ONUS REAIS"""

    class Meta:
        ordering = ("-id",)

    member = models.ForeignKey(
        ControlInformationMember,
        verbose_name="Membro",
        related_name="debtsencumbrances",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    code = models.ForeignKey(
        CodeDebtsEncumbrances,
        related_name="debtsencumbrances",
        verbose_name="Código",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField(
        default="", null=True, blank=True, verbose_name="Descrição"
    )
    kind = models.SmallIntegerField(
        null=True, blank=True, default=1, choices=KIND, verbose_name="TIPO DE BEM"
    )
    last_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="Última Situação (R$)",
    )
    current_value = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="Situação Atual (R$)"
    )
    status = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_MODIFICATION,
        verbose_name="Status",
    )
    status_pendency = models.SmallIntegerField(
        null=True,
        blank=True,
        default=1,
        choices=STATUS_PENDENCY,
        verbose_name="Status Pendência",
    )
    file_document = models.ForeignKey(
        Arquivo,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Anexo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    refperiod_debts = models.ForeignKey(
        ReferencePeriod,
        null=True,
        blank=True,
        related_name="ref_debts",
        verbose_name="Período de Referência",
        on_delete=models.PROTECT,
    )

    def exists_pendencies(self):
        return True if int(self.status) == 1 else False

    @property
    def icon_status(self):
        return (
            {
                "iconCls": "icon-cif icon-cif-item-unchecked",
                "title": "Informação não confirmada.",
            }
            if int(self.status) == 1
            else {
                "iconCls": "icon-cif icon-cif-item-checked",
                "title": "Informação confirmada.",
            }
        )

    @property
    def icon_kind(self):
        if self.code:
            if int(self.kind) == 1:
                return {"iconCls": "icon-cif icon-cif-member", "title": "Individual"}
            elif int(self.kind) == 2:
                return {"iconCls": "icon-cif icon-cif-users", "title": "Cônjuge"}
            elif int(self.kind) == 3:
                return {
                    "iconCls": "icon-cif icon-cif-user-group",
                    "title": "Dependente",
                }
            else:
                return {"iconCls": "icon-cif icon-cif-blank", "title": ""}
        else:
            return {"iconCls": "icon-cif icon-cif-blank", "title": ""}

    @property
    def icons(self):
        lista = []
        lista.append(self.icon_status)
        lista.append(self.icon_kind)

        return lista

    def validate_deadline(self):
        now = date.today()
        if self.member.deadline_debtsencumbrances:
            if now > self.member.deadline_debtsencumbrances and self.member.lock_debts:
                raise Exception(
                    "Não é possível cadastrar/alterar essa informação pois ela está bloqueada e o prazo para preenchimento foi encerrado em: %s"
                    % DateUtils.date_to_str(self.member.deadline_debtsencumbrances)
                )

    def validade_exists_debts(self):
        """Verifica se o membro possui debitos ou não."""
        if self.status == 2 and not self.code:
            return False
        else:
            return True

    @property
    def text_not_debts(self):
        return "O membro informou não possuir dívidas e ônus reais"

    def save(self, *args, **kwargs):
        self.member.validate()
        self.validate_deadline()

        if self.pk:
            self.status = 2

        # self.status_pendency = 2 if self.exists_pendencies() else 1
        if self.exists_pendencies():
            self.status_pendency = 2
            self.member.pendency_debts = True
            self.member.save()
        else:
            self.status_pendency = 1
            self.member.pendency_debts = False
            self.member.save()

        super(DebtsEncumbrances, self).save(*args, **kwargs)


class Attachment(AuditTimestampModel):
    member = models.ForeignKey(
        ControlInformationMember,
        verbose_name="Membro",
        related_name="attachment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=100, blank=False)
    attach = models.ForeignKey(
        "ged.arquivo", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s - %s" % (
            self.attach,
            self.title,
        )
