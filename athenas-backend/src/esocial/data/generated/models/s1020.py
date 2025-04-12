# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1020(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabLotacao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabLotacao/v_S_01_02_00"
    GROUP = 1
    NAME = "Tabela de Lotações Tributárias"
    ACTION_PERM = ACTION
    ide_lotacao_cod_lotacao = models.CharField(max_length=30)
    ide_lotacao_ini_valid = models.CharField(max_length=7)
    ide_lotacao_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_lotacao_tp_lotacao = models.CharField(max_length=2)
    dados_lotacao_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    dados_lotacao_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    fpas_lotacao_fpas = models.PositiveIntegerField()
    fpas_lotacao_cod_tercs = models.CharField(max_length=4)
    fpas_lotacao_cod_tercs_susp = models.CharField(max_length=4, null=True, blank=True)
    proc_jud_terceiro = models.ManyToManyField(
        "ProcJudTerceiro", related_name="proc_jud_terceiro_register_s1020"
    )
    info_empr_parcial_tp_insc_contrat = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_empr_parcial_nr_insc_contrat = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_empr_parcial_tp_insc_prop = models.PositiveIntegerField(null=True, blank=True)
    info_empr_parcial_nr_insc_prop = models.CharField(
        max_length=14, null=True, blank=True
    )
    dados_op_port_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    dados_op_port_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)
