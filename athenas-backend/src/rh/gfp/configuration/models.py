# -*- coding: utf-8 -*-
from django.db import models
from rh.gfp.models import GFP_TIPO_EVENTO, NatureEvent, Evento
from standard.models import Choice
from rh.models import ServidorLotacao


class ConfigReport(models.Model):
    type_event = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "GFP_TYPE_EVENT"), verbose_name="Tipo"
    )
    section = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "GFP_SECTION"), verbose_name="Seção"
    )
    type_report = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "GFP_TYPE_REPORT"),
        verbose_name="Tipo Relatório",
        default=1,
    )
    nature = models.CharField(
        max_length=12, verbose_name="Natureza", blank=True, null=True
    )
    subelement = models.CharField(
        max_length=12, verbose_name="SubElemento", blank=True, null=True
    )
    creditor = models.CharField(
        max_length=15, verbose_name="Credor", blank=True, null=True
    )
    text = models.TextField(verbose_name="Texo")
    transfer_type = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "TRANSFER_TYPE"),
        verbose_name="Tipo Repasse",
    )
    type_formula = models.IntegerField(
        choices=Choice.get_choices_for("gfp", "TYPE_FORMULA"),
        verbose_name="Tipo Formula",
        blank=True,
        null=True,
    )
    type_by_possession = models.CharField(
        max_length=300, blank=True, verbose_name="Categoria"
    )
    include_funds = models.ManyToManyField(
        Evento,
        related_name="config_include_funds",
        verbose_name="Incluir Verba",
        blank=True,
    )
    exclude_funds = models.ManyToManyField(
        Evento,
        related_name="config_exclude_funds",
        verbose_name="Excluir Verba",
        blank=True,
    )
    include_job_positions = models.ManyToManyField(
        "rh.Cargo",
        verbose_name="Incluir Cargo",
        related_name="config_include_jobs",
        blank=True,
    )
    exclude_job_positions = models.ManyToManyField(
        "rh.Cargo",
        verbose_name="Excluir Cargo",
        related_name="config_exclude_jobs",
        blank=True,
    )
    include_registration = models.ManyToManyField(
        "rh.Servidor",
        blank=True,
        related_name="config_include_registration",
        verbose_name="Incluir Matricula",
    )
    exclude_registration = models.ManyToManyField(
        "rh.Servidor",
        blank=True,
        related_name="config_exclude_registration",
        verbose_name="Excluir Matricula",
    )
    include_workplaces = models.ManyToManyField(
        "rh.Lotacao",
        blank=True,
        related_name="config_include_workplaces",
        verbose_name="Incluir Lotação",
    )
    exclude_workplaces = models.ManyToManyField(
        "rh.Lotacao",
        blank=True,
        related_name="config_exclude_workplaces",
        verbose_name="Excluir Lotação",
    )
    formula = models.TextField(blank=True, null=True, verbose_name="Fórmula")

    class Meta:
        ordering = ("section", "type_event", "nature", "subelement")

    @classmethod
    def include_register(cls, config):
        designations = (
            ServidorLotacao.objects.filter(empenho_gaeco=True)
            .order_by("servidor__matricula")
            .distinct("servidor__matricula")
        )
        config.include_registration.clear()
        for designation in designations:
            config.include_registration.add(designation.servidor)

    @classmethod
    def exclude_register(cls, config):
        designations = (
            ServidorLotacao.objects.filter(empenho_gaeco=True)
            .order_by("servidor__matricula")
            .distinct("servidor__matricula")
        )
        config.exclude_registration.clear()
        for designation in designations:
            config.exclude_registration.add(designation.servidor)

    def __str__(self):
        return self.text
