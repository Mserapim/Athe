# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2418(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReativBen.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReativBen/v_S_01_02_00"
    GROUP = 2
    NAME = "Reativação de Benefício - Entes Públicos"
    ACTION_PERM = ACTION
    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_reativ_dt_efet_reativ = models.DateField()
    info_reativ_dt_efeito = models.DateField()
