# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1010(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabRubrica.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabRubrica/v_S_01_02_00"
    GROUP = 1
    NAME = "Tabela de Rubricas"
    ACTION_PERM = ACTION
    ide_rubrica_cod_rubr = models.CharField(max_length=30)
    ide_rubrica_ide_tab_rubr = models.CharField(max_length=8)
    ide_rubrica_ini_valid = models.CharField(max_length=7)
    ide_rubrica_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_rubrica_dsc_rubr = models.CharField(max_length=0)
    dados_rubrica_nat_rubr = models.PositiveIntegerField()
    dados_rubrica_tp_rubr = models.PositiveIntegerField()
    dados_rubrica_cod_inc_cp = models.CharField(max_length=2)
    dados_rubrica_cod_inc_irrf = models.PositiveIntegerField()
    dados_rubrica_cod_inc_fgts = models.CharField(max_length=2)
    dados_rubrica_cod_inc_cprp = models.CharField(max_length=2, null=True, blank=True)
    dados_rubrica_cod_inc_pis_pasep = models.CharField(
        max_length=2, null=True, blank=True
    )
    dados_rubrica_teto_remun = models.CharField(max_length=1, null=True, blank=True)
    dados_rubrica_observacao = models.CharField(max_length=55, null=True, blank=True)
    ide_processo_cp = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_cp_register_s1010"
    )
    ide_processo_irrf = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_irrf_register_s1010"
    )
    ide_processo_fgts = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_fgts_register_s1010"
    )
    ide_processo_pis_pasep_nr_proc = models.CharField(
        max_length=20, null=True, blank=True
    )
    ide_processo_pis_pasep_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)
