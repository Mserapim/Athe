# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5011(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCS.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCS/v_S_01_02_00"
    GROUP = 3
    NAME = "Informações das contribuições sociais consolidadas por contribuinte"
    ACTION_PERM = ACTION
    info_cs_nr_rec_arq_base = models.CharField(max_length=23)
    info_cs_ind_exist_info = models.PositiveIntegerField()
    info_cp_seg_vr_desc_cp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cp_seg_vr_cp_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_contrib_class_trib = models.CharField(max_length=2)
    info_pj_ind_coop = models.PositiveIntegerField(null=True, blank=True)
    info_pj_ind_constr = models.PositiveIntegerField(null=True, blank=True)
    info_pj_ind_subst_patr = models.PositiveIntegerField(null=True, blank=True)
    info_pj_perc_red_contrib = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_pj_perc_transf = models.PositiveIntegerField(null=True, blank=True)
    info_pj_ind_trib_folha_pis_pasep = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_at_conc_fator_mes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_at_conc_fator13 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    info_estab_cnae_prep = models.PositiveIntegerField(null=True, blank=True)
    info_estab_cnpj_resp = models.CharField(max_length=14, null=True, blank=True)
    info_estab_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    info_estab_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_estab_aliq_rat_ajust = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_estab_ref_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    info_estab_ref_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_estab_ref_aliq_rat_ajust = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_compl_obra_ind_subst_patr_obra = models.PositiveIntegerField(
        null=True, blank=True
    )
    ide_lotacao_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    ide_lotacao_fpas = models.PositiveIntegerField(null=True, blank=True)
    ide_lotacao_cod_tercs = models.CharField(max_length=4, null=True, blank=True)
    ide_lotacao_cod_tercs_susp = models.CharField(max_length=4, null=True, blank=True)
    info_terc_susp_cod_terc = models.CharField(max_length=4, null=True, blank=True)
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
    info_empr_parcial_cno_obra = models.CharField(max_length=12, null=True, blank=True)
    dados_op_port_cnpj_op_portuario = models.CharField(
        max_length=14, null=True, blank=True
    )
    dados_op_port_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    dados_op_port_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    dados_op_port_aliq_rat_ajust = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    bases_remun_ind_incid = models.PositiveIntegerField(null=True, blank=True)
    bases_remun_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    bases_cp_vr_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp00_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp15_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp20_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp25_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp00_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp15_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp20_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp25_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_desc_sest = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_calc_sest = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_desc_senat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_calc_senat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_sal_fam = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_sal_mat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_susp_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_susp_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_susp_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp13_vr_susp_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_bc_cp13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_av_n_port_vr_desc_cp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_subst_patr_op_port_cnpj_op_portuario = models.CharField(
        max_length=14, null=True, blank=True
    )
    bases_aquis_ind_aquis = models.PositiveIntegerField(null=True, blank=True)
    bases_aquis_vlr_aquis = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_cp_desc_pr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_cpn_ret = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_rat_n_ret = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_senar_n_ret = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_cp_calc_pr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_rat_desc_pr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_rat_calc_pr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_senar_desc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_aquis_vr_senar_calc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_comerc_ind_comerc = models.PositiveIntegerField(null=True, blank=True)
    bases_comerc_vr_bc_com_pr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_comerc_vr_cp_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_comerc_vr_rat_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_comerc_vr_senar_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cr_estab_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    info_cr_estab_vr_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cr_estab_vr_susp_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_pis_pasep_vr_bc_pis_pasep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_pis_pasep_vr_bc_pis_pasep_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cr_contrib = models.ManyToManyField(
        "InfoCRContrib", related_name="info_cr_contrib_register_s5011"
    )
