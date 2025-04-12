from django.db import models
from standard.models import AuditTimestampModel, Choice
from contrib.utils import getLogger

from rh.gfp.models import Folha, ContraCheque, FolhaEvento, Evento
from rh.models import Cbo, PessoaFisica, Lotacao

log = getLogger(__name__)


class PFProviderEntry(AuditTimestampModel):
    natural_person = models.ForeignKey(
        PessoaFisica,
        verbose_name="Pessoa Física",
        related_name="pf_providers",
        on_delete=models.CASCADE,
    )
    payroll = models.ForeignKey(
        Folha,
        verbose_name="Folha",
        related_name="pf_providers",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    paycheck = models.ForeignKey(
        ContraCheque,
        verbose_name="ContraCheque",
        related_name="pf_providers",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    cbo = models.ForeignKey(
        Cbo,
        verbose_name="CBO",
        related_name="pf_providers",
        null=True,
        on_delete=models.CASCADE,
    )
    workplace = models.ForeignKey(
        Lotacao,
        verbose_name="Lotação",
        related_name="pf_providers",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
    )
    pay_day = models.DateField(verbose_name="Data do Pagamento", null=True, blank=True)
    gross_value = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        verbose_name="Valor Bruto",
        null=True,
        blank=True,
    )
    inss_value = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        verbose_name="Valor INSS",
        null=True,
        blank=True,
    )
    inss_exempt = models.BooleanField(verbose_name="Isento INSS", default=False)
    nature_activity = models.SmallIntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name="Natureza da Atividade",
        choices=Choice.get_choices_for("defin", "NATURE_ACTIVITY"),
    )
    partial_contribution = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0,
        verbose_name="Contribuição parcial em outro local",
        null=True,
        blank=True,
    )
    contributed = models.BooleanField(
        verbose_name="Existe contribuição parcial em outro local?", default=False
    )
    ir_value = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Valor IR"
    )
    liquid_value = models.DecimalField(
        max_digits=16, decimal_places=2, default=0, verbose_name="Valor líquido"
    )
    applied_payroll = models.BooleanField(
        verbose_name="Aplicado em Folha", default=False
    )

    class Meta:
        verbose_name = "Entradas do Provedor PF"

    def __str__(self):
        if self.natural_person.social_name:
            nome = self.natural_person.social_name
        else:
            nome = self.natural_person.nome
        return f"{nome} - {self.pay_day}"

    def save(self, *args, **kargs):
        self.validate()
        super(PFProviderEntry, self).save(*args, **kargs)

    def validate(self):
        self.validades_gross_value()
        self.validates_exemption_inss()
        self.validates_pay_day()
        self.validates_contributed()
        self.validates_contribution_value()
        self.validates_have_entry()

    def validates_pay_day(self):
        if not self.pay_day:
            raise Exception("Favor preencher o Dia do Pagamento.")

    def validades_gross_value(self):
        if not self.gross_value or self.gross_value == 0:
            raise Exception("Favor preencher o Valor Bruto.")

    def validates_exemption_inss(self):
        if self.inss_exempt:
            self.inss_value = 0  # Se for isento INSS, valor deve ser igual a 0

    def validates_contributed(self):
        if not self.contributed:
            self.partial_contribution = (
                0  # Se não houver Contribuição Parcial, valor deve ser igual a 0
            )
        elif not self.partial_contribution:
            raise Exception("Favor preencher o Valor da Contribuição Parcial.")

    def validates_contribution_value(self):
        if self.contributed:
            if self.partial_contribution > self.inss_value:
                raise Exception(
                    "O Valor de Contribuição Parcial não deve ser maior que o Valor de INSS."
                )

    def validates_have_entry(self):
        evento = Evento.objects.get(numero="60000")
        employee = self.natural_person.servidor_set.filter(
            type_by_possession="COE"
        ).first()
        entries = FolhaEvento.objects.filter(
            evento=evento,
            servidor=employee,
            reference_year=self.pay_day.year,
            reference_month=self.pay_day.month,
        )
        if not entries:
            self.applied_payroll = False
