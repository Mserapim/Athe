# -*- coding: utf-8 -*-
from django.db import models
from ged.models import Arquivo as File


class ModelPDF(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    template = models.ForeignKey(
        File,
        verbose_name="Modelo PDF",
        on_delete=models.PROTECT,
        related_name="modelpdf",
    )


class ModelODT(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome")
    template = models.ForeignKey(
        File,
        verbose_name="Modelo ODT",
        on_delete=models.PROTECT,
        related_name="modelodt",
    )
