# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5501(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTribProcTrab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrf/v_S_01_02_00"
    GROUP = 3
    NAME = "S-5501 - Informações Consolidadas de Tributos Decorrentes de Processo Trabalhista"
    ACTION_PERM = ACTION
    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_proc_nr_proc_trab = models.CharField(max_length=20)
    info_tributos_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_cr_contrib = models.ManyToManyField(
        "InfoCRContrib", related_name="info_cr_contrib_register_s5501"
    )
    info_crirrf_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    info_crirrf_vr_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
