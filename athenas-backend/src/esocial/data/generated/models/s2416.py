# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2416(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenAlt.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenAlt/v_S_01_02_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Alteração"
    ACTION_PERM = ACTION
    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_ben_alteracao_dt_alt_beneficio = models.DateField()
    dados_beneficio_tp_beneficio = models.CharField(max_length=4)
    dados_beneficio_tp_plan_rp = models.PositiveIntegerField()
    dados_beneficio_dsc = models.CharField(max_length=55, null=True, blank=True)
    dados_beneficio_ind_suspensao = models.CharField(max_length=1)
    info_pen_morte_tp_pen_morte = models.PositiveIntegerField(null=True, blank=True)
    suspensao_mtv_suspensao = models.CharField(max_length=2, null=True, blank=True)
    suspensao_dsc_suspensao = models.CharField(max_length=55, null=True, blank=True)
