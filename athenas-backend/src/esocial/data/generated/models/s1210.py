# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1210(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtPgtos.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtPgtos/v_S_01_02_00"
    GROUP = 3
    NAME = "Pagamentos de Rendimentos do Trabalho"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    ide_benef_cpf_benef = models.CharField(max_length=11)
    info_pgto_dt_pgto = models.DateField(null=True, blank=True)
    info_pgto_tp_pgto = models.PositiveIntegerField(null=True, blank=True)
    info_pgto_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_pgto_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    info_pgto_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_pgto_pais_resid_ext = models.CharField(max_length=3, null=True, blank=True)
    info_pgto_ext_ind_nif = models.PositiveIntegerField(null=True, blank=True)
    info_pgto_ext_nif_benef = models.CharField(max_length=30, null=True, blank=True)
    info_pgto_ext_frm_tribut = models.CharField(max_length=2, null=True, blank=True)
    end_ext_end_dsc_lograd = models.CharField(max_length=80, null=True, blank=True)
    end_ext_end_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    end_ext_end_complem = models.CharField(max_length=30, null=True, blank=True)
    end_ext_end_bairro = models.CharField(max_length=60, null=True, blank=True)
    end_ext_end_cidade = models.CharField(max_length=40, null=True, blank=True)
    end_ext_end_estado = models.CharField(max_length=40, null=True, blank=True)
    end_ext_end_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    end_ext_telef = models.CharField(max_length=15, null=True, blank=True)
    info_ir_complem_dt_laudo = models.DateField(null=True, blank=True)
    per_ant_per_ref_ajuste = models.CharField(max_length=7, null=True, blank=True)
    per_ant_nr_rec1210_orig = models.CharField(max_length=23, null=True, blank=True)
    info_dep_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    info_dep_dt_nascto = models.DateField(null=True, blank=True)
    info_dep_nome = models.CharField(max_length=70, null=True, blank=True)
    info_dep_dep_irrf = models.CharField(max_length=1, null=True, blank=True)
    info_dep_tp_dep = models.CharField(max_length=2, null=True, blank=True)
    info_dep_descr_dep = models.CharField(max_length=0, null=True, blank=True)
    info_ircr_tp_cr = models.CharField(max_length=6, null=True, blank=True)
    ded_depen_tp_rend = models.PositiveIntegerField(null=True, blank=True)
    ded_depen_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    ded_depen_vlr_ded_dep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    pen_alim_tp_rend = models.PositiveIntegerField(null=True, blank=True)
    pen_alim_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    pen_alim_vlr_ded_pen_alim = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_tp_prev = models.PositiveIntegerField(null=True, blank=True)
    previd_compl_cnpj_entid_pc = models.CharField(max_length=14, null=True, blank=True)
    previd_compl_vlr_ded_pc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_ded_pc13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_patroc_funp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_patroc_funp13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_proc_ret_tp_proc_ret = models.PositiveIntegerField(null=True, blank=True)
    info_proc_ret_nr_proc_ret = models.CharField(max_length=21, null=True, blank=True)
    info_proc_ret_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    info_valores_vlr_n_retido = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_dep_jud = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_cmp_ano_cal = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_cmp_ano_ant = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_rend_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ded_susp_ind_tp_deducao = models.PositiveIntegerField(null=True, blank=True)
    ded_susp_vlr_ded_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ded_susp_cnpj_entid_pc = models.CharField(max_length=14, null=True, blank=True)
    ded_susp_vlr_patroc_funp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    benef_pen_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    benef_pen_vlr_depen_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    plan_saude_cnpj_oper = models.CharField(max_length=14, null=True, blank=True)
    plan_saude_reg_ans = models.CharField(max_length=6, null=True, blank=True)
    plan_saude_vlr_saude_tit = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_dep_sau_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    info_dep_sau_vlr_saude_dep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_reemb_med_ind_org_reemb = models.PositiveIntegerField(null=True, blank=True)
    info_reemb_med_cnpj_oper = models.CharField(max_length=14, null=True, blank=True)
    info_reemb_med_reg_ans = models.CharField(max_length=6, null=True, blank=True)
    det_reemb_tit_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    det_reemb_tit_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    det_reemb_tit_vlr_reemb = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_reemb_tit_vlr_reemb_ant = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_reemb_dep_cpf_benef = models.CharField(max_length=11, null=True, blank=True)
