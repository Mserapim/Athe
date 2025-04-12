# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models, transaction


from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import MovimentacaoPosse, PessoaFisica, Quadro
from standard.models import AuditTimestampModel, Choice

log = getLogger(__name__)


class RetirementPrevision(models.Model):
    natural_person = models.OneToOneField(
        PessoaFisica, verbose_name="Pessoa física", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    last_occupation = models.ForeignKey(
        Quadro,
        verbose_name="Última ocupação",
        related_name="retirementprevisions",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    exercise_date = models.DateField(
        verbose_name="Primeiro emprego", null=True, blank=True
    )
    contribution_prevision_date = models.DateField(
        verbose_name="Data da aposentadoria por contribuição", null=True, blank=True
    )
    age_prevision_date = models.DateField(
        verbose_name="Data da aposentadoria por idade"
    )
    integral_prevision_date = models.DateField(
        verbose_name="Data da aposentadoria integral", null=True, blank=True
    )
    before_ec_20_98 = models.BooleanField(
        verbose_name="Vínculo público anterior a EC 20 de 1998", default=False
    )
    active = models.BooleanField(verbose_name="Ativo?", default=False)
    negative_previous_bond = models.BooleanField(
        verbose_name="Negativa de vínculo anterior", default=False
    )

    class Meta:
        verbose_name = "Previsão de Aposentadoria"
        db_table = "ss_retirementprevision"
        ordering = ["integral_prevision_date"]

    @property
    def contributed_accumulated_time(self):
        query_normal = self.employmentbonds.exclude(contribution_double=True).aggregate(
            normal=models.Sum("liquid_days")
        )
        query_doubled = self.employmentbonds.filter(contribution_double=True).aggregate(
            doubled=models.Sum("liquid_days")
        )

        return query_normal.get("normal") or 0 + (query_doubled.get("doubled") or 0) * 2

    @property
    def meets_old_rule_requirement(self):
        if not hasattr(self, "_meets_old_rule_requirement"):
            self._meets_old_rule_requirement = self.employmentbonds.filter(
                begin_date__lt=date(1998, 12, 16), public_employee=True
            ).exists()

        return self._meets_old_rule_requirement

    @property
    def undetermined_removal_time(self):
        if not hasattr(self, "_undetermined_removal_time"):
            self._undetermined_removal_time = False

            try:
                self._undetermined_removal_time = any(
                    [
                        eb.removal.filter(data_fim__isnull=True).exists()
                        for eb in self.employmentbonds.filter(possession__isnull=False)
                    ]
                )
            except Exception:
                log.debug("Não há afastamento com retorno indeterminado neste vínculo.")

        return self._undetermined_removal_time

    @property
    def get_age_prevision_date(self):
        if not hasattr(self, "_age_prevision_date"):
            contributor = self.natural_person
            if contributor.sexo == "M":
                # 60 if self.meets_old_rule_requirement else
                self._age_prevision_date = contributor.data_nascimento + relativedelta(
                    years=+(65)
                )
            elif contributor.sexo == "F":
                # 55 if self.meets_old_rule_requirement else
                self._age_prevision_date = contributor.data_nascimento + relativedelta(
                    years=+(60)
                )

        return self._age_prevision_date

    @property
    def get_contribution_prevision_date(self):
        if not hasattr(self, "_contribution_prevision_date"):
            if self.undetermined_removal_time:
                self._contribution_prevision_date = None
            else:
                if self.natural_person.sexo == "M":
                    self._contribution_prevision_date = date.today() + relativedelta(
                        years=35, days=-self.contributed_accumulated_time
                    )
                elif self.natural_person.sexo == "F":
                    self._contribution_prevision_date = date.today() + relativedelta(
                        years=30, days=-self.contributed_accumulated_time
                    )

        return self._contribution_prevision_date

    @property
    def get_integral_prevision_date(self):
        return (
            max(self.get_age_prevision_date, self.get_contribution_prevision_date)
            if not self.undetermined_removal_time
            else None
        )

    @property
    def get_last_employee(self):
        employee = self.natural_person.servidor_set.filter()

        if employee.filter(ativo=True).exists():
            return employee.filter(ativo=True).latest("pk")
        else:
            return max([e for e in employee], key=lambda x: x.data_exercicio)

    @property
    def get_occupation(self):
        employee = self.get_last_employee

        if employee.posses.filter(quadro__cargo__tipo_lei_cargo="EF"):
            return (
                employee.posses.filter(quadro__cargo__tipo_lei_cargo="EF")
                .latest("data_exercicio")
                .quadro
            )

    @property
    def first_exercise_date(self):
        query = self.employmentbonds.filter(with_pgj=True).aggregate(
            begin=models.Min("begin_date")
        )

        return query.get("begin") or None

    @property
    def rgps_liquid_days(self):
        query = self.employmentbonds.filter(pension_system=1).aggregate(
            sum_rgps_days=models.Sum("liquid_days")
        )

        return query.get("sum_rgps_days") or None

    @property
    def rpps_liquid_days(self):
        query = self.employmentbonds.filter(pension_system=2).aggregate(
            sum_rpps_days=models.Sum("liquid_days")
        )

        return query.get("sum_rpps_days") or None

    @property
    def get_icons(self):
        employee = self.natural_person.servidor_set.last()

        sex_map = {
            "F": "icon-socialsecurity icon-socialsecurity-female",
            "M": "icon-socialsecurity icon-socialsecurity-male",
        }

        type_employee_map = {"S": "Servidor", "M": "Membro"}

        active_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-active",
                "title": "Ativo",
            },
            False: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-inactive",
                "title": "Inativo",
            },
        }

        negative_previous_bond_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-negative",
                "title": "Negativa de vínculo anterior",
            },
            False: {"iconCls": "icon-core icon-core-blank", "title": ""},
        }

        before_ec_20_98_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-old-rule",
                "title": "Anterior a EC 20/98",
            },
            False: {"iconCls": "icon-core icon-core-blank", "title": ""},
        }

        undetermined_removal_time_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-undetermined-removal-time",
                "title": "Afastamento SEM previsão de retorno",
            },
            False: {"iconCls": "icon-core icon-core-blank", "title": ""},
        }

        type_employee = {
            "iconCls": sex_map.get(employee.pessoa_fisica.sexo),
            "title": type_employee_map.get(employee.tipo),
        }
        active = active_map.get(self.active)
        negative_previous_bond = negative_previous_bond_map.get(
            self.negative_previous_bond
        )
        before_ec_20_98 = before_ec_20_98_map.get(self.before_ec_20_98)
        undetermined_removal_time = undetermined_removal_time_map.get(
            self.undetermined_removal_time
        )

        return [
            type_employee,
            active,
            negative_previous_bond,
            before_ec_20_98,
            undetermined_removal_time,
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.age_prevision_date = self.get_age_prevision_date
            self.contribution_prevision_date = self.get_contribution_prevision_date
            self.integral_prevision_date = self.get_integral_prevision_date
            self.last_occupation = self.get_occupation
            self.active = self.natural_person.servidor_set.filter(ativo=True).exists()
            self.before_ec_20_98 = self.meets_old_rule_requirement
            self.exercise_date = self.first_exercise_date
            super(RetirementPrevision, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % (self.natural_person.nome)


class EmploymentBond(AuditTimestampModel):
    # Parametro "on_delete" adicionado. (Django 2)
    retirement_prevision = models.ForeignKey(
        RetirementPrevision,
        verbose_name="Aposentadoria",
        related_name="employmentbonds",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    possession = models.OneToOneField(
        MovimentacaoPosse,
        verbose_name="Movimentação de Posse",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    employer = models.CharField(
        verbose_name="Empregador", max_length=256, null=True, blank=True
    )
    function_name = models.CharField(
        verbose_name="Função", max_length=256, null=True, blank=True
    )
    pension_system = models.PositiveSmallIntegerField(
        verbose_name="Regime previdenciário",
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
        null=True,
        blank=True,
    )
    begin_date = models.DateField(verbose_name="Início", null=True, blank=True)
    end_date = models.DateField(verbose_name="Término", null=True, blank=True)
    deduction = models.PositiveSmallIntegerField(
        verbose_name="Deduções", null=True, blank=True
    )
    liquid_days = models.PositiveSmallIntegerField(
        verbose_name="Tempo líquido", null=True, blank=True
    )
    raw_days = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Tempo Bruto"
    )
    archive = models.CharField(
        verbose_name="Arquivo", max_length=256, blank=True, null=True
    )
    with_pgj = models.BooleanField(verbose_name="Vínculo com a PGJ", default=False)
    contribution_double = models.BooleanField(
        verbose_name="Contribuição em dobro", default=False
    )
    public_employee = models.BooleanField(
        verbose_name="Servidor público", default=False
    )
    purpose = models.PositiveSmallIntegerField(
        verbose_name="Para Fins",
        choices=Choice.get_choices_for("rh", "PURPOSES"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Vínculos empregatícios"
        db_table = "ss_employmentbond"
        unique_together = ("employer", "pension_system", "possession")
        ordering = ["begin_date"]

    @property
    def removal(self):
        if not hasattr(self, "_removal"):
            self._removal = []

            try:
                # estado 4 trata dos afastamentos cancelados
                self._removal = BaseLicencaAfastamento.objects.exclude(estado=4).filter(
                    servidor=self.possession.servidor, remunerado=False
                )
            except Exception:
                log.debug("Não há posses nem afastamentos relacionados a este vínculo.")

        return self._removal

    @property
    def range_of_removal(self):
        removed = NewDateRange()

        if self.possession:
            for r in self.removal:
                removed += NewDateRange(r.data_inicio, r.data_fim)

        return removed

    @property
    def range_of_bond(self):
        return NewDateRange(
            self.begin_date,
            self.end_date if self.end_date else (date.today() - relativedelta(days=1)),
        )

    @property
    def count_removal(self):
        return self.range_of_removal.intersect(self.range_of_bond).days

    @property
    def get_deduction(self):
        if not hasattr(self, "_deduction"):
            self._deduction = (
                self.deduction if self.deduction is not None else self.count_removal
            )

        return self._deduction

    @property
    def get_raw_days(self):
        if not hasattr(self, "_raw_days"):
            self._raw_days = self.range_of_bond.days - self.get_deduction

        return self._raw_days

    @property
    def get_liquid_days(self):
        if not hasattr(self, "_liquid_days"):
            self._liquid_days = self.get_raw_days - self.get_deduction

        return self._liquid_days

    @property
    def get_icons(self):

        doubled_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-doubled",
                "title": "Contribuição dobrada",
            },
            False: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-normal",
                "title": "Normal",
            },
        }

        public_employee_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-public",
                "title": "Serviço Público",
            },
            False: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-private",
                "title": "Serviço Privado",
            },
        }

        with_pgj_map = {
            True: {
                "iconCls": "icon-socialsecurity icon-socialsecurity-pgj",
                "title": "Vínculo com a PGJ",
            },
            False: {"iconCls": "icon-core icon-core-blank", "title": "Vínculo externo"},
        }

        doubled = doubled_map.get(self.contribution_double)
        public_employee = public_employee_map.get(self.public_employee)
        with_pgj = with_pgj_map.get(self.with_pgj)

        return [doubled, public_employee, with_pgj]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.deduction = self.get_deduction
            self.liquid_days = self.get_liquid_days
            self.raw_days = self.get_raw_days
            self.validate()
            super(EmploymentBond, self).save(*args, **kwargs)
            if self.retirement_prevision:
                self.retirement_prevision.save()

    def validate(self):
        self.validate_employer()
        self.validate_pension_system()
        self.validate_begin_date()
        # self.validate_function_name()
        # self.validate_purpose()

    def validate_employer(self):
        if not self.employer:
            raise Exception("Favor preencher o campo: Empregador")

    def validate_pension_system(self):
        if not self.pension_system:
            raise Exception("Favor preencher o campo: Regime")

    def validate_begin_date(self):
        if not self.begin_date:
            raise Exception("Favor preencher o campo: Início")

    def validate_function_name(self):
        if not self.function_name:
            raise Exception("Favor preencher o campo: Cargo/Função")

    def validate_purpose(self):
        if not self.purpose:
            raise Exception("Favor preencher o campo: Para Fins")

    def __str__(self):
        return "%s - %s %s" % (self.employer, str(self.get_liquid_days), "dias")
