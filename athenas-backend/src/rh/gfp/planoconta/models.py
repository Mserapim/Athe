# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models

from contrib.decorator import cache_return
from contrib.middleware import get_current_user
from contrib.utils import get_json_engine, getLogger
from rh.gfp.models import GFP_STATUS_WORKFLOW
from rh.gfp.models import Evento as Event
from rh.gfp.models import FolhaTipo
from rh.models import PessoaJuridica
from rh.models import Servidor as Employee
from standard.models import AuditTimestampModel, Choice, ClassCode

log = getLogger(__name__)
json = get_json_engine()


class PlanoConta(models.Model):
    plano = models.ForeignKey(
        "planoconta.Plano", null=True, related_name="contas", on_delete=models.CASCADE
    )
    finalidade = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "FINALIDADE_PLANOCONTA"), default=1
    )
    regime_previdenciario = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
        verbose_name="Regime previdenciário",
        default=1,
    )
    # TODO Tipo não utilizado - Deprecated
    tipo = models.SmallIntegerField(
        choices=(
            (1, "ATIVO"),
            (2, "INATIVO"),
            (3, "PENSIONISTA"),
        ),
        default=1,
        blank=True,
        null=False,
    )
    inscricao_ne = models.CharField(max_length=12)
    evento_nld = models.CharField(max_length=12, null=True, blank=True)
    evento_nld_two = models.CharField(max_length=12, null=True, blank=True)
    evento_nlc = models.CharField(max_length=12, null=True, blank=True)
    classificacao_nld = models.CharField(max_length=12)
    vpd = models.CharField(max_length=12, null=True, blank=True)
    classificacao_nlc = models.CharField(max_length=12, null=True, blank=True)
    equity_note_item = models.CharField(max_length=12, null=True, blank=True)
    equity_note_operation = models.CharField(max_length=12, null=True, blank=True)
    equity_note_classification = models.CharField(max_length=12, null=True, blank=True)

    class Meta:
        unique_together = (
            "inscricao_ne",
            "evento_nld",
            "evento_nlc",
            "classificacao_nld",
            "classificacao_nlc",
            "plano",
            "tipo",
            "finalidade",
            "regime_previdenciario",
        )
        ordering = ("finalidade", "plano", "regime_previdenciario")

    def __str__(self):
        return "%(evento)s - %(inscricao)s - %(classificacao)s" % {
            "inscricao": self.inscricao_ne,
            "evento": self.evento_nld,
            "classificacao": self.classificacao_nld,
        }


class Plano(models.Model):
    titulo = models.CharField(max_length=60, null=True)
    folha_tipo = models.ForeignKey(
        FolhaTipo, related_name="planos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    ano_calendario = models.IntegerField()
    tipo = models.SmallIntegerField(choices=Choice.get_choices_for("gfp", "TIPO_PLANO"))
    pessoa_juridica = models.ForeignKey(
        PessoaJuridica, related_name="planos", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    banco = models.ForeignKey(
        "rh.Banco",
        related_name="em_plano",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    agencia = models.CharField(max_length=15, null=True, blank=True)
    conta = models.CharField(max_length=15, null=True, blank=True)
    fonte = models.CharField(max_length=10, null=True, blank=True)
    eventos = models.ManyToManyField("gfp.Evento", related_name="em_plano")
    genre_events = models.ManyToManyField("gfp.GenreEvent", related_name="em_plano")
    invert_negative = models.BooleanField(
        verbose_name="Inverter caso negativo", null=False, default=False
    )
    composes_total_net = models.BooleanField(
        verbose_name="Compõe líquido?", null=False, default=False
    )

    class Meta:
        ordering = ("ano_calendario", "folha_tipo", "pessoa_juridica", "tipo")
        unique_together = ("folha_tipo", "ano_calendario", "tipo", "titulo")

    def save(self, *args, **kargs):
        if self.titulo is None or self.titulo == "":
            self.titulo = str(self.pessoa_juridica)

        models.Model.save(self, *args, **kargs)

    @classmethod
    def copy_ano_calendario(
        cls,
        plans=[],
        year_from=None,
        year_to=None,
        type_payroll_from=None,
        type_payroll_to=None,
    ):
        if not plans:
            if not year_from:
                year_from = Plano.objects.aggregate(year=models.Max("ano_calendario"))[
                    "year"
                ]
            if year_from:
                plans = Plano.objects.filter(ano_calendario=year_from)

                if type_payroll_from:
                    plans = plans.filter(folha_tipo=type_payroll_from)
        if not year_to:
            year_from = year_from

        for plan in plans:

            new_plan, created = Plano.objects.update_or_create(
                ano_calendario=int(year_to) if year_to else plan.ano_calendario,
                folha_tipo=type_payroll_to if type_payroll_to else plan.folha_tipo,
                tipo=plan.tipo,
                titulo=plan.titulo,
                defaults={
                    "pessoa_juridica": plan.pessoa_juridica,
                    "banco": plan.banco,
                    "agencia": plan.agencia,
                    "conta": plan.conta,
                },
            )

            for genre in plan.genre_events.all():
                if genre not in new_plan.genre_events.all():
                    new_plan.genre_events.add(genre)

            for account in plan.contas.all():
                if not new_plan.contas.filter(
                    inscricao_ne=account.inscricao_ne.replace(
                        f"{year_from}NE", f"{year_to}NE"
                    ),
                    evento_nld=account.evento_nld,
                    evento_nlc=account.evento_nlc,
                    classificacao_nld=account.classificacao_nld,
                    classificacao_nlc=account.classificacao_nlc,
                    plano=new_plan,
                    tipo=account.tipo,
                    finalidade=account.finalidade,
                    regime_previdenciario=account.regime_previdenciario,
                ).exists():
                    account.pk = None
                    account.plano = new_plan
                    account.inscricao_ne = account.inscricao_ne.replace(
                        f"{year_from}NE", f"{year_to}NE"
                    )
                    account.save()

        return Plano.objects.filter(ano_calendario=year_to).exists()

    def __str__(self):
        return "%s-%s" % (self.titulo, self.ano_calendario)


class ProvisionPlan(models.Model):
    class Meta:
        ordering = ("type_provision", "start_validity")

    title = models.CharField(max_length=120, blank=True)
    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True)
    type_provision = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_PROVISION")
    )
    provision_calc = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        verbose_name="Cálculo",
        related_name="plans_provisions",
        on_delete=models.SET_NULL,
    )
    paid_events_value = models.ManyToManyField(
        Event, related_name="plans_provisions_value"
    )
    paid_events_employer = models.ManyToManyField(
        Event, related_name="plans_provisions_employer"
    )
    update_previous_balance = models.BooleanField(
        default=False, verbose_name="Atualiza saldo?"
    )
    auto_balance_at_end_period = models.BooleanField(
        default=False, verbose_name="Zerar balanço?"
    )

    def __str__(self):
        return "%s" % self.title

    def save(self, *args, **kwargs):
        log.debug(self.__dict__)
        if not self.title:
            self.title = "PROVISÃO DE %s" % (self.get_type_provision_display())
        super(ProvisionPlan, self).save(*args, **kwargs)

    # def create_initial


class ProvisionEmployee(models.Model):
    class Meta:
        ordering = ("employee", "start_acquisition")

    provision_plan = models.ForeignKey(
        ProvisionPlan,
        on_delete=models.CASCADE,
        related_name="provisions_employee",
        verbose_name="Plano de Provisão",
    )  # Parametro "on_delete" adicionado. (Django 2)
    employee = models.ForeignKey(
        Employee,
        related_name="provisions",
        verbose_name="Servidor",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    info = models.CharField(
        max_length=50, verbose_name="Info", default="", db_index=True
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name="Quantidade max.", default=12
    )
    start_acquisition = models.DateField(verbose_name="Início Aquisição")
    end_acquisition = models.DateField(verbose_name="Fim Aquisição")

    def __str__(self):
        return "%s - %s" % (self.employee, self.info)


class ProvisionManager(AuditTimestampModel):
    class Meta:
        ordering = (
            "-reference_year",
            "-reference_month",
            "provision_plan",
            "pension_system",
        )

    class PreviousNotProcessed(Exception):
        def __init__(self, previous):
            Exception.__init__(
                self,
                "Existe período anterior (%s) ainda não processado. Processo-o para que pssa criar o próximo!"
                % previous,
            )

    class PreviousNotImmediate(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "O período solicitado não possui periodo igual ou imediatamente superior, \
                    tente periodos com no máximo 1 mês de diferênça!",
            )

    DEFAULT_USER = "athenas"

    provision_plan = models.ForeignKey(
        ProvisionPlan,
        related_name="summaries",
        verbose_name="Plano de Provisão",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    reference_year = models.PositiveSmallIntegerField(verbose_name="Ano de referência")
    reference_month = models.PositiveSmallIntegerField(verbose_name="Mês de referência")
    total_provisioned_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Valor aprovisionado"
    )
    total_paid_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Valor liquidado"
    )
    total_provisioned_employer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Patronal provisionado",
    )
    total_paid_employer = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Patronal pago"
    )
    total_previous_balance_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Saldo anterior valor",
    )
    total_previous_balance_employer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Saldo anterior patronal",
    )
    total_manual_balance_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Balanço valor"
    )
    total_manual_balance_employer = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Balanço patronal"
    )
    status = models.SmallIntegerField(
        choices=Choice.get_choices_for("gfp", "STATUS_PAYROLL"),
        verbose_name="Status",
        default=1,
        blank=True,
    )
    pension_system = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Regime previdenciário",
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
    )

    class ChangeStatusNotPermited(Exception):
        def __init__(self):
            Exception.__init__(
                self,
                "Por motivos de segurança essa alteração de status da provisão não pode ser efetuada!",
            )

    class UserHasNotPermission(Exception):
        def __init__(self):
            Exception.__init__(
                self, "Vocẽ não tem permissão para alterar o status da provisão!"
            )

    def create_or_update_provisions(self):
        pass

    def change_status(self, status, save=True):
        if status != self.status:
            if status not in list(GFP_STATUS_WORKFLOW[self.status].keys()):
                raise self.ChangeStatusNotPermited()

            if not get_current_user().has_perm(
                GFP_STATUS_WORKFLOW[self.status][status]
            ):
                raise self.UserHasNotPermission()

            self.status = status

            if save:
                self.save()

    @property
    def balance_value(self):
        return self.previous_balance_value + self.provisioned_value + self.paid_value

    @property
    def balance_employer(self):
        return (
            self.previous_balance_employer
            + self.provisioned_employer
            + self.paid_employer
        )

    @property
    @cache_return
    def previous(self):
        previous_reference_date = date(
            self.reference_year, self.reference_month, 1
        ) - relativedelta(days=1)
        manager = None
        try:
            manager = self.provision_plan.summaries.get(
                reference_year=previous_reference_date.year,
                reference_month=previous_reference_date.month,
                pension_system=self.pension_system,
            )
        except ProvisionManager.DoesNotExist:
            pass
        except Exception as e:
            raise e
        return manager

    def last_provision(self):
        manager = None
        try:
            manager = (
                ProvisionManager.objects.filter(
                    provision_plan__type_provision=self.provision_plan.type_provision,
                    pension_system=self.pension_system,
                )
                .order_by("-reference_year", "-reference_month")
                .first()
            )
        except ProvisionManager.DoesNotExist:
            return False
        except Exception as e:
            raise e

        if manager:
            reference_date = (
                date(self.reference_year, self.reference_month, 1)
                - date(manager.reference_year, manager.reference_month, 1)
            ).days
            if 0 > reference_date or reference_date > 31:
                return True
        else:
            return False

    def __str__(self):
        return "%s - %02d/%04d" % (
            self.provision_plan,
            self.reference_month,
            self.reference_year,
        )

    def save(self, *args, **kwargs):
        # log.debug(unicode(self.last_provision))
        if self.last_provision():
            raise self.PreviousNotImmediate()
        if self.previous and self.previous.status in [1, 2]:
            raise self.PreviousNotProcessed(self.previous)
        # reference_date = date(self.reference_year, self.reference_month, 1)
        super(ProvisionManager, self).save(*args, **kwargs)


class Provision(AuditTimestampModel):

    class Meta:
        ordering = (
            "provision_manager__reference_year",
            "provision_manager__reference_month",
            "provision_employee__employee",
        )

    DEFAULT_USER = "athenas"

    provision_manager = models.ForeignKey(
        ProvisionManager,
        on_delete=models.CASCADE,
        related_name="provisions",
        verbose_name="Gertor de Provisão",
    )  # Parametro "on_delete" adicionado. (Django 2)
    provision_employee = models.ForeignKey(
        ProvisionEmployee,
        on_delete=models.CASCADE,
        related_name="provisions",
        verbose_name="Provisão do Servidor",
    )  # Parametro "on_delete" adicionado. (Django 2)
    acquired = models.PositiveSmallIntegerField(
        verbose_name="Quantidade max.", default=1
    )
    base_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Base salarial"
    )
    provisioned_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Valor aprovisionado"
    )
    paid_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Valor liquidado"
    )
    provisioned_employer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Patronal provisionado",
    )
    paid_employer = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Patronal pago"
    )
    previous_balance_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Saldo anterior valor",
    )
    previous_balance_employer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        verbose_name="Saldo anterior patronal",
    )
    manual_balance_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Balanço valor"
    )
    manual_balance_employer = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Balanço patronal"
    )

    @property
    def balance_value(self):
        return (
            float(self.previous_balance_value)
            + float(self.provisioned_value)
            + float(self.paid_value)
            + float(self.manual_balance_value)
        )

    @property
    def balance_employer(self):
        return (
            float(self.previous_balance_employer)
            + float(self.provisioned_employer)
            + float(self.paid_employer)
            + float(self.manual_balance_employer)
        )

    @property
    @cache_return
    def previous(self):
        return (
            Provision.objects.filter(
                provision_manager__provision_plan=self.provision_manager.provision_plan,
                provision_employee__employee=self.provision_employee.employee,
            )
            .filter(
                models.Q(
                    provision_manager__reference_year__lt=self.provision_manager.reference_year
                )
                | (
                    models.Q(
                        provision_manager__reference_year=self.provision_manager.reference_year
                    )
                    & models.Q(
                        provision_manager__reference_month__lt=self.provision_manager.reference_month
                    )
                )
            )
            .order_by(
                "-provision_manager__reference_year",
                "-provision_manager__reference_month",
            )
            .first()
        )
        # return provisions[0] if provisions else None

    @property
    def is_first_provision(self):
        if not hasattr(self, "_is_first_provision"):
            self._is_first_provision = (
                not Provision.objects.filter(
                    provision_employee__employee=self.provision_employee.employee
                )
                .exclude(
                    provision_manager__reference_year__gt=self.provision_manager.reference_year
                )
                .exclude(
                    provision_manager__reference_year=self.provision_manager.reference_year,
                    provision_manager__reference_month__gte=self.provision_manager.reference_month,
                )
                .exists()
            )
        return self._is_first_provision

    @property
    def is_last_provision_of_manager(self):
        if not hasattr(self, "_is_last_provision_of_manager"):
            qnt = (
                self.provision_employee.provisions.exclude(
                    provision_manager__reference_year__gt=self.provision_manager.reference_year
                )
                .exclude(
                    provision_manager__reference_year=self.provision_manager.reference_year,
                    provision_manager__reference_month__gt=self.provision_manager.reference_month,
                )
                .aggregate(total=models.Sum("acquired"))
                .get("total", 0)
            )

            self._is_last_provision_of_manager = qnt == self.provision_employee.quantity
        return self._is_last_provision_of_manager

    @property
    def is_first_provision_of_manager(self):
        if not hasattr(self, "_is_last_provision_of_manager"):
            qnt = (
                self.provision_employee.provisions.exclude(
                    provision_manager__reference_year__gt=self.provision_manager.reference_year
                )
                .exclude(
                    provision_manager__reference_year=self.provision_manager.reference_year,
                    provision_manager__reference_month__gt=self.provision_manager.reference_month,
                )
                .aggregate(total=models.Sum("acquired"))
                .get("total", 0)
            )

            self._is_last_provision_of_manager = qnt == 1
        return self._is_last_provision_of_manager
