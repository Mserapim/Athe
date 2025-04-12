# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5002(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtIrrfBenef.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrfBenef/v_S_01_02_00"
    GROUP = 3
    NAME = "Imposto de Renda Retido na Fonte por Trabalhador"
    ACTION_PERM = ACTION
    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_trabalhador_cpf_benef = models.CharField(max_length=11)
    dm_dev_per_ref = models.CharField(max_length=7, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    dm_dev_tp_pgto = models.PositiveIntegerField(null=True, blank=True)
    dm_dev_dt_pgto = models.DateField(null=True, blank=True)
    dm_dev_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_ir_tp_info_ir = models.PositiveIntegerField(null=True, blank=True)
    info_ir_valor = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_ir_desc_rendimento = models.CharField(max_length=0, null=True, blank=True)
    info_proc_jud_rub_nr_proc = models.CharField(max_length=20, null=True, blank=True)
    info_proc_jud_rub_uf_vara = models.CharField(max_length=2, null=True, blank=True)
    info_proc_jud_rub_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    info_proc_jud_rub_id_vara = models.PositiveIntegerField(null=True, blank=True)
    tot_apur_men_cr_men = models.CharField(max_length=6, null=True, blank=True)
    tot_apur_men_vlr_rend_trib = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_rend_trib13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_prev_oficial = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_prev_oficial13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_cr_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_cr13_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_parc_isenta65 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_parc_isenta65_dec = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_diarias = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_ajuda_custo = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_ind_res_contrato = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_abono_pec = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_rend_mole_grave = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_rend_mole_grave13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_aux_moradia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_bolsa_medico = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_bolsa_medico13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_juros_mora = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_vlr_isen_outros = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_men_desc_rendimento = models.CharField(
        max_length=55, null=True, blank=True
    )
    tot_apur_dia_per_apur_dia = models.PositiveIntegerField(null=True, blank=True)
    tot_apur_dia_cr_dia = models.CharField(max_length=6, null=True, blank=True)
    tot_apur_dia_frm_tribut = models.CharField(max_length=2, null=True, blank=True)
    tot_apur_dia_pais_resid_ext = models.CharField(max_length=3, null=True, blank=True)
    tot_apur_dia_vlr_pago_dia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    tot_apur_dia_vlr_cr_dia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_pgto_ext_pais_resid_ext = models.CharField(max_length=3, null=True, blank=True)
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
    consolid_apur_men_cr_men = models.CharField(max_length=6, null=True, blank=True)
    consolid_apur_men_vlr_rend_trib = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_rend_trib13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_prev_oficial = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_prev_oficial13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_cr_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_cr13_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_parc_isenta65 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_parc_isenta65_dec = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_diarias = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_ajuda_custo = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_ind_res_contrato = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_abono_pec = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_rend_mole_grave = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_rend_mole_grave13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_aux_moradia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_bolsa_medico = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_bolsa_medico13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_juros_mora = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_vlr_isen_outros = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    consolid_apur_men_desc_rendimento = models.CharField(
        max_length=99, null=True, blank=True
    )
    info_ir_complem_dt_laudo = models.DateField(null=True, blank=True)
    per_ant_per_ref_ajuste = models.CharField(max_length=7, null=True, blank=True)
    per_ant_nr_rec1210_orig = models.CharField(max_length=23, null=True, blank=True)
    ide_dep_cpf_dep = models.CharField(max_length=11, null=True, blank=True)
    ide_dep_dep_irrf = models.CharField(max_length=1, null=True, blank=True)
    ide_dep_dt_nascto = models.DateField(null=True, blank=True)
    ide_dep_nome = models.CharField(max_length=70, null=True, blank=True)
    ide_dep_tp_dep = models.CharField(max_length=2, null=True, blank=True)
    ide_dep_descr_dep = models.CharField(max_length=0, null=True, blank=True)
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
