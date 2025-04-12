# -*- coding: utf-8 -*-
from django.db import models
from standard.models import AuditTimestampModel, Choice
from contrib.utils import getLogger
from raf.models import Item, SubItem

log = getLogger(__name__)


class ConfigProductivity(AuditTimestampModel):
    """
    Tabela de configuracao da Produtividade/Score Table
    """

    productivity = models.IntegerField(
        choices=Choice.get_choices_for("raf", "PRODUCTIVITY"),
        verbose_name="Fator Produtividade",
    )

    score_table = models.IntegerField(
        choices=Choice.get_choices_for("corregedoria", "SCORE_TABLE"),
        verbose_name="Tabela de Cálculo",
    )

    class Meta:
        ordering = ["productivity"]
        verbose_name = "Tabela de configuração  Produtividade / Score Table"


class ConfigScoreTable(AuditTimestampModel):
    """
    Tabela de configuracao dos calculos de pontuacao
    """

    ordination = models.CharField(max_length=250)
    score_table = models.IntegerField(
        choices=Choice.get_choices_for("corregedoria", "SCORE_TABLE"),
        verbose_name="Tabela de Cálculo",
    )
    active = models.BooleanField(default=True)
    initial_validity = models.DateField(null=True, blank=True)
    final_validity = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["active"]
        verbose_name = "Tabela de configuração dos cálculos de pontuação"


class BandScoreTable(AuditTimestampModel):
    """
    Faixas para tabela de pontuacao
    """

    configscoretable = models.ForeignKey(
        ConfigScoreTable, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    label = models.CharField(max_length=250)
    initial_value = models.DecimalField(
        null=True, blank=True, max_digits=16, decimal_places=2
    )
    end_value = models.DecimalField(
        null=True, blank=True, max_digits=16, decimal_places=2
    )
    score = models.SmallIntegerField()
    active = models.BooleanField(default=True)
    observation = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Faixas para tabela de pontuação"


class ConfigLinkInspectionRAF(AuditTimestampModel):
    """
    Vinculo para afericao de dados do RAF em Inspection
    """

    inspection_table = models.IntegerField(
        choices=Choice.get_choices_for("corregedoria", "INSPECTION_TABLE"),
        verbose_name="Tabela de Inspection",
    )
    raf_item = models.ForeignKey(
        Item, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    raf_subitem = models.ForeignKey(
        SubItem, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["inspection_table"]
        verbose_name = "Vínculo para aferição de dados do RAF em Inspection"
