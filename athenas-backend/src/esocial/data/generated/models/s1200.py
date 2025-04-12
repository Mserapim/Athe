# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1200(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtRemun.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtRemun/v_S_01_02_00"
    GROUP = 3
    NAME = "Remuneração do Trabalhador - RGPS"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_complem_nm_trab = models.CharField(max_length=70, null=True, blank=True)
    info_complem_dt_nascto = models.DateField(null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_adm = models.DateField(null=True, blank=True)
    sucessao_vinc_observacao = models.CharField(max_length=55, null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_register_s1200"
    )
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    dm_dev_cod_categ = models.PositiveIntegerField()
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
    ide_estab_lot_qtd_dias_av = models.PositiveIntegerField(null=True, blank=True)
    remun_per_apur_matricula = models.CharField(max_length=30, null=True, blank=True)
    remun_per_apur_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    itens_remun_cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    itens_remun_ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    itens_remun_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    itens_remun_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    itens_remun_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    itens_remun_ind_apur_ir = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_tp_desc = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    desc_folha_nr_doc = models.CharField(max_length=12, null=True, blank=True)
    desc_folha_observacao = models.CharField(max_length=55, null=True, blank=True)
    info_ag_nocivo_grau_exp = models.PositiveIntegerField(null=True, blank=True)
    ide_adc_dt_ac_conv = models.DateField(null=True, blank=True)
    ide_adc_tp_ac_conv = models.CharField(max_length=1, null=True, blank=True)
    ide_adc_dsc = models.CharField(max_length=55, null=True, blank=True)
    ide_adc_remun_suc = models.CharField(max_length=1, null=True, blank=True)
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
    remun_per_ant_matricula = models.CharField(max_length=30, null=True, blank=True)
    remun_per_ant_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    remun_per_ant_itens_remun_cod_rubr = models.CharField(
        max_length=30, null=True, blank=True
    )
    remun_per_ant_itens_remun_ide_tab_rubr = models.CharField(
        max_length=8, null=True, blank=True
    )
    remun_per_ant_itens_remun_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    remun_per_ant_itens_remun_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    remun_per_ant_itens_remun_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remun_per_ant_itens_remun_ind_apur_ir = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_compl_cont_cod_cbo = models.CharField(max_length=6, null=True, blank=True)
    info_compl_cont_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_compl_cont_qtd_dias_trab = models.PositiveIntegerField(null=True, blank=True)
