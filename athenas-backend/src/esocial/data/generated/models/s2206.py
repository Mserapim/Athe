# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2206(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAltContratual.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAltContratual/v_S_01_02_00"
    GROUP = 2
    NAME = "Alteração de Contrato de Trabalho"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    alt_contratual_dt_alteracao = models.DateField()
    alt_contratual_dt_ef = models.DateField(null=True, blank=True)
    alt_contratual_dsc_alt = models.CharField(max_length=50, null=True, blank=True)
    vinculo_tp_reg_prev = models.PositiveIntegerField()
    info_celetista_tp_reg_jor = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_dt_base = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_cnpj_sind_categ_prof = models.CharField(
        max_length=14, null=True, blank=True
    )
    trab_temporario_just_prorr = models.CharField(max_length=99, null=True, blank=True)
    aprend_ind_aprend = models.PositiveIntegerField(null=True, blank=True)
    aprend_cnpj_ent_qual = models.CharField(max_length=14, null=True, blank=True)
    aprend_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    aprend_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    aprend_cnpj_prat = models.CharField(max_length=14, null=True, blank=True)
    info_estatutario_tp_plan_rp = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_ind_teto_rgps = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_ind_abono_perm = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_contrato_nm_cargo = models.CharField(max_length=0, null=True, blank=True)
    info_contrato_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_nm_funcao = models.CharField(max_length=0, null=True, blank=True)
    info_contrato_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_acum_cargo = models.CharField(max_length=1, null=True, blank=True)
    info_contrato_cod_categ = models.PositiveIntegerField()
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=99, null=True, blank=True)
    duracao_tp_contr = models.PositiveIntegerField(null=True, blank=True)
    duracao_dt_term = models.DateField(null=True, blank=True)
    duracao_obj_det = models.CharField(max_length=55, null=True, blank=True)
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
    local_temp_dom_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    local_temp_dom_dsc_lograd = models.CharField(max_length=0, null=True, blank=True)
    local_temp_dom_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    local_temp_dom_complemento = models.CharField(max_length=30, null=True, blank=True)
    local_temp_dom_bairro = models.CharField(max_length=90, null=True, blank=True)
    local_temp_dom_cep = models.CharField(max_length=8, null=True, blank=True)
    local_temp_dom_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    local_temp_dom_uf = models.CharField(max_length=2, null=True, blank=True)
    hor_contratual_qtd_hrs_sem = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    hor_contratual_tp_jornada = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_tmp_parc = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_hor_noturno = models.CharField(max_length=1, null=True, blank=True)
    hor_contratual_dsc_jorn = models.CharField(max_length=99, null=True, blank=True)
    alvara_judicial_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=55, null=True, blank=True)
    trei_cap_cod_trei_cap = models.PositiveIntegerField(null=True, blank=True)
