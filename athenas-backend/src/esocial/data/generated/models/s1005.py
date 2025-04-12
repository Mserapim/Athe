# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1005(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabEstab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabEstab/v_S_01_02_00"
    GROUP = 1
    NAME = "Tabela de Estabelecimentos e Obras de Construção Civil"
    ACTION_PERM = ACTION
    ide_estab_tp_insc = models.PositiveIntegerField()
    ide_estab_nr_insc = models.CharField(max_length=14)
    ide_estab_ini_valid = models.CharField(max_length=7)
    ide_estab_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_estab_cnae_prep = models.PositiveIntegerField()
    dados_estab_cnpj_resp = models.CharField(max_length=14, null=True, blank=True)
    aliq_gilrat_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    aliq_gilrat_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    proc_adm_jud_rat_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_rat_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    proc_adm_jud_rat_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_fap_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_fap_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    proc_adm_jud_fap_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    info_caepf_tp_caepf = models.PositiveIntegerField(null=True, blank=True)
    info_obra_ind_subst_patr_obra = models.PositiveIntegerField(null=True, blank=True)
    info_apr_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    info_ent_educ_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    info_pcd_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)
