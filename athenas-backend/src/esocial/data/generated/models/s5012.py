# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5012(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtIrrf.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrf/v_S_01_02_00"
    GROUP = 3
    NAME = "S-5012 - Imposto de Renda Retido na Fonte Consolidado por Contribuinte"
    ACTION_PERM = ACTION
    info_irrf_nr_rec_arq_base = models.CharField(max_length=23)
    info_irrf_ind_exist_info = models.PositiveIntegerField()
    info_cr_men_cr_men = models.CharField(max_length=6, null=True, blank=True)
    info_cr_men_vr_cr_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cr_dia_per_apur_dia = models.PositiveIntegerField(null=True, blank=True)
    info_cr_dia_cr_dia = models.CharField(max_length=6, null=True, blank=True)
    info_cr_dia_vr_cr_dia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
