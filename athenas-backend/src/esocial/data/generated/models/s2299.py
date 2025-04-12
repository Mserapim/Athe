# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2299(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtDeslig.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtDeslig/v_S_01_02_00"
    GROUP = 2
    NAME = "Desligamento"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    info_deslig_mtv_deslig = models.CharField(max_length=2)
    info_deslig_dt_deslig = models.DateField()
    info_deslig_dt_av_prv = models.DateField(null=True, blank=True)
    info_deslig_ind_pagto_api = models.CharField(max_length=1)
    info_deslig_dt_proj_fim_api = models.DateField(null=True, blank=True)
    info_deslig_pens_alim = models.PositiveIntegerField(null=True, blank=True)
    info_deslig_perc_aliment = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_deslig_vr_alim = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_deslig_nr_proc_trab = models.CharField(max_length=20, null=True, blank=True)
    info_deslig_ind_pdv = models.CharField(max_length=1, null=True, blank=True)
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=55, null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    transf_tit_cpf_substituto = models.CharField(max_length=11, null=True, blank=True)
    transf_tit_dt_nascto = models.DateField(null=True, blank=True)
    mudanca_cpf_novo_cpf = models.CharField(max_length=11, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
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
    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    det_verbas_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    det_verbas_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    det_verbas_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_verbas_ind_apur_ir = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_tp_desc = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    desc_folha_nr_doc = models.CharField(max_length=12, null=True, blank=True)
    desc_folha_observacao = models.CharField(max_length=55, null=True, blank=True)
    info_ag_nocivo_grau_exp = models.PositiveIntegerField(null=True, blank=True)
    info_simples_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    ide_adc_dt_ac_conv = models.DateField(null=True, blank=True)
    ide_adc_tp_ac_conv = models.CharField(max_length=1, null=True, blank=True)
    ide_adc_dsc = models.CharField(max_length=55, null=True, blank=True)
    ide_periodo_per_ref = models.CharField(max_length=7, null=True, blank=True)
    ide_periodo_ide_estab_lot_tp_insc = models.PositiveIntegerField(
        null=True, blank=True
    )
    ide_periodo_ide_estab_lot_nr_insc = models.CharField(
        max_length=14, null=True, blank=True
    )
    ide_periodo_ide_estab_lot_cod_lotacao = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_estab_lot_det_verbas_cod_rubr = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_estab_lot_det_verbas_ide_tab_rubr = models.CharField(
        max_length=8, null=True, blank=True
    )
    ide_estab_lot_det_verbas_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_ind_apur_ir = models.PositiveIntegerField(
        null=True, blank=True
    )
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_register_s2299"
    )
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    proc_cs_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    remun_apos_deslig_ind_remun = models.PositiveIntegerField(null=True, blank=True)
    remun_apos_deslig_dt_fim_remun = models.DateField(null=True, blank=True)
    consig_fgts_ins_consig = models.CharField(max_length=5, null=True, blank=True)
    consig_fgts_nr_contr = models.CharField(max_length=40, null=True, blank=True)
