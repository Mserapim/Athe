from django.db import models
from contrib.decorator import to_search
from contrib.utils import getLogger

from rh.models import Servidor
from standard.models import AuditTimestampModel, Choice

log = getLogger(__name__)


@to_search(
    [
        {"name": "name", "type": "text"},
        {"name": "description", "type": "text"},
        {"name": "local", "type": "text"},
        {"name": "period", "type": "text"},
    ]
)
class Capacitation(AuditTimestampModel):
    name = models.CharField(
        verbose_name="Nome",
        max_length=400,
    )
    description = models.TextField(verbose_name="Descrição", blank=True, null=True)
    month = models.PositiveIntegerField(
        choices=Choice.get_choices_for("rh", "MONTHS"),
        verbose_name="Mês de Competência",
    )
    year = models.PositiveIntegerField(
        verbose_name="Ano de Competência",
    )
    local = models.CharField(
        verbose_name="Local", max_length=400, blank=True, null=True
    )
    time_total = models.DecimalField(
        verbose_name="Total de Horas",
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
    )
    capacitation_cost = models.DecimalField(
        verbose_name="Total de Horas",
        max_digits=20,
        decimal_places=2,
        blank=True,
        null=True,
    )
    period = models.CharField(
        verbose_name="Período", max_length=400, blank=True, null=True
    )

    @property
    def reference_period(self):
        return f"{self.month}/{self.year}"

    def __str__(self) -> str:
        return f"{self.name}"

    def validate_year(self):
        if len(str(self.year)) != 4:
            raise Exception(
                "O ano de competência deve conter 4 algarismos (Ex.: 2022)."
            )

    def validate(self):
        self.validate_year()

    def save(self, *args, **kargs):
        self.validate()
        return super().save(*args, **kargs)


class Participant(AuditTimestampModel):
    name = models.CharField(
        verbose_name="Nome",
        max_length=400,
    )
    employee = models.ForeignKey(
        Servidor,
        verbose_name="Servidor",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    type_participant = models.SmallIntegerField(
        verbose_name="Tipo de Participação",
        choices=Choice.get_choices_for("ceaf", "TYPE_CEAF_PARTICIPANT"),
        default=1,
        blank=True,
        null=True,
    )
    capacitation = models.ForeignKey(
        Capacitation,
        on_delete=models.CASCADE,
        verbose_name="Participantes",
        related_name="participants",
    )

    def __str__(self) -> str:
        return f"{self.name}"

    def validate_unique_employee(self):
        if (
            not self.pk
            and Participant.objects.filter(
                employee=self.employee, capacitation=self.capacitation
            )
            .exclude(employee__isnull=True)
            .exists()
        ):
            raise Exception(
                "O servidor informado já se encontra cadastrado nesta capacitação."
            )

    def validate(self):
        self.validate_unique_employee()

    def save(self, *args, **kargs):
        self.validate()
        return super().save(*args, **kargs)
