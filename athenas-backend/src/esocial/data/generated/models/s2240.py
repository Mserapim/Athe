# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2240(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtExpRisco.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtExpRisco/v_S_01_02_00"
    GROUP = 2
    NAME = "Condições Ambientais do Trabalho - Agentes Nocivos"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_exp_risco_dt_ini_condicao = models.DateField()
    info_exp_risco_dt_fim_condicao = models.DateField(null=True, blank=True)
    info_amb_local_amb = models.PositiveIntegerField()
    info_amb_dsc_setor = models.CharField(max_length=0)
    info_amb_tp_insc = models.PositiveIntegerField()
    info_amb_nr_insc = models.CharField(max_length=14)
    info_ativ_dsc_ativ_des = models.CharField(max_length=99)
    ag_noc_cod_ag_noc = models.CharField(max_length=9)
    ag_noc_dsc_ag_noc = models.CharField(max_length=0, null=True, blank=True)
    ag_noc_tp_aval = models.PositiveIntegerField(null=True, blank=True)
    ag_noc_int_conc = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    ag_noc_lim_tol = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    ag_noc_un_med = models.PositiveIntegerField(null=True, blank=True)
    ag_noc_tec_medicao = models.CharField(max_length=40, null=True, blank=True)
    ag_noc_nr_proc_jud = models.CharField(max_length=21, null=True, blank=True)
    epc_epi_utiliz_epc = models.PositiveIntegerField(null=True, blank=True)
    epc_epi_efic_epc = models.CharField(max_length=1, null=True, blank=True)
    epc_epi_utiliz_epi = models.PositiveIntegerField(null=True, blank=True)
    epc_epi_efic_epi = models.CharField(max_length=1, null=True, blank=True)
    epi_doc_aval = models.CharField(max_length=55, null=True, blank=True)
    epi_compl_med_protecao = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_cond_functo = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_uso_inint = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_prz_valid = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_periodic_troca = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_higienizacao = models.CharField(max_length=1, null=True, blank=True)
    resp_reg_cpf_resp = models.CharField(max_length=11)
    resp_reg_ide_oc = models.PositiveIntegerField(null=True, blank=True)
    resp_reg_dsc_oc = models.CharField(max_length=20, null=True, blank=True)
    resp_reg_nr_oc = models.CharField(max_length=14, null=True, blank=True)
    resp_reg_uf_oc = models.CharField(max_length=2, null=True, blank=True)
    obs_obs_compl = models.CharField(max_length=99, null=True, blank=True)
