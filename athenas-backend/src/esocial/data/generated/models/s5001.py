# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5001(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtBasesTrab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtBasesTrab/v_S_01_02_00"
    GROUP = 3
    NAME = "Informações das contribuições sociais por trabalhador"
    ACTION_PERM = ACTION
    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_adm = models.DateField(null=True, blank=True)
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    info_compl_cont_cod_cbo = models.CharField(max_length=6, null=True, blank=True)
    info_compl_cont_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_compl_cont_qtd_dias_trab = models.PositiveIntegerField(null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_register_s5001"
    )
    info_cp_calc_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    info_cp_calc_vr_cp_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cp_calc_vr_desc_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cp_class_trib = models.CharField(max_length=2, null=True, blank=True)
    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    info_categ_incid_matricula = models.CharField(max_length=30, null=True, blank=True)
    info_categ_incid_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_categ_incid_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    info_base_cs_ind13 = models.PositiveIntegerField(null=True, blank=True)
    info_base_cs_tp_valor = models.PositiveIntegerField(null=True, blank=True)
    info_base_cs_valor = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    calc_terc_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    calc_terc_vr_cs_seg_terc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    calc_terc_vr_desc_terc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_per_ref_per_ref = models.CharField(max_length=7, null=True, blank=True)
    ide_adc_dt_ac_conv = models.DateField(null=True, blank=True)
    ide_adc_tp_ac_conv = models.CharField(max_length=1, null=True, blank=True)
    ide_adc_dsc = models.CharField(max_length=55, null=True, blank=True)
    ide_adc_remun_suc = models.CharField(max_length=1, null=True, blank=True)
    det_info_per_ref_ind13 = models.PositiveIntegerField(null=True, blank=True)
    det_info_per_ref_tp_vr_per_ref = models.PositiveIntegerField(null=True, blank=True)
    det_info_per_ref_vr_per_ref = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    info_categ_pis_pasep_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    info_categ_pis_pasep_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_base_pis_pasep_ind13 = models.PositiveIntegerField(null=True, blank=True)
    info_base_pis_pasep_tp_valor_pis_pasep = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_base_pis_pasep_valor_pis_pasep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
