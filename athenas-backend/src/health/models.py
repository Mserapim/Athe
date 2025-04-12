# -*- coding: utf-8 -*-

from django.db import models

from contrib.utils import DateUtils
from standard.models import AuditTimestampModel, Choice


# Create your models here.
class DiagnosisProcedureQuerySet(models.QuerySet):
    def get_by_natural_key(self, code, *args):
        return self.get(code=code)


class DiagnosisProcedure(AuditTimestampModel):

    code = models.CharField(max_length=10, verbose_name="Código")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )

    objects = DiagnosisProcedureQuerySet.as_manager()

    class Meta:
        verbose_name = "Procedimento Diagnóstico"

    def __str__(self):
        return f"{self.code}: {self.title}"

    def natural_key(self):
        return self.code


class Exam(AuditTimestampModel):
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="exam",
        on_delete=models.CASCADE,
    )
    exam_date = models.DateTimeField("Data do exame")
    diagnosis_procedure = models.ForeignKey(
        DiagnosisProcedure,
        verbose_name="Procedimento diagnóstico",
        related_name="exam",
        on_delete=models.PROTECT,
    )
    note = models.CharField("Observação", max_length=999, null=True, blank=True)
    order = models.PositiveSmallIntegerField(
        "Ordem", default=99, choices=Choice.get_choices_for("health", "ORDER")
    )
    result = models.PositiveSmallIntegerField(
        "Resultado", default=99, choices=Choice.get_choices_for("health", "RESULT")
    )

    class Meta:
        verbose_name = "Exame"
        ordering = ("exam_date",)

    def __str__(self):
        return f"{DateUtils.datetime_to_str(self.exam_date)}: ({self.diagnosis_procedure.code}) - {self.employee}"

    def save(self, *args, **kargs):
        super(Exam, self).save(*args, **kargs)
