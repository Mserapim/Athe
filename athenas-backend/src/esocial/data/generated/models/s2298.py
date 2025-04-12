# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2298(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReintegr.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReintegr/v_S_01_02_00"
    GROUP = 2
    NAME = "Reintegração"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    info_reintegr_tp_reint = models.PositiveIntegerField()
    info_reintegr_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    info_reintegr_nr_lei_anistia = models.CharField(
        max_length=13, null=True, blank=True
    )
    info_reintegr_dt_efet_retorno = models.DateField()
    info_reintegr_dt_efeito = models.DateField()
