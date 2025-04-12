# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5003(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = ""
    XMLNS = ""
    GROUP = 1
    NAME = ""
    ACTION_PERM = ACTION
    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    info_fgts_dt_venc = models.DateField(null=True, blank=True)
    info_fgts_class_trib = models.CharField(max_length=2, null=True, blank=True)
    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_lotacao_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    ide_lotacao_tp_lotacao = models.CharField(max_length=2, null=True, blank=True)
    ide_lotacao_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_lotacao_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    info_trab_fgts_matricula = models.CharField(max_length=30, null=True, blank=True)
    info_trab_fgts_cod_categ = models.PositiveIntegerField()
    info_trab_fgts_categ_orig = models.PositiveIntegerField(null=True, blank=True)
    info_trab_fgts_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
    info_trab_fgts_remun_suc = models.CharField(max_length=1, null=True, blank=True)
    info_trab_fgts_dt_deslig = models.DateField(null=True, blank=True)
    info_trab_fgts_mtv_deslig = models.CharField(max_length=2, null=True, blank=True)
    info_trab_fgts_dt_term = models.DateField(null=True, blank=True)
    info_trab_fgts_mtv_deslig_tsv = models.CharField(
        max_length=2, null=True, blank=True
    )
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_adm = models.DateField(null=True, blank=True)
    base_per_apur_tp_valor = models.PositiveIntegerField(null=True, blank=True)
    base_per_apur_ind_incid = models.PositiveIntegerField(null=True, blank=True)
    base_per_apur_rem_fgts = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    base_per_apur_dps_fgts = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_rubr_susp_cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    det_rubr_susp_ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    det_rubr_susp_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_processo_fgts = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_fgts_register_s5003"
    )
    info_base_per_ant_e_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_base_per_ant_e_tp_ac_conv = models.CharField(
        max_length=1, null=True, blank=True
    )
    base_per_ant_e_tp_valor_e = models.PositiveIntegerField(null=True, blank=True)
    base_per_ant_e_ind_incid_e = models.PositiveIntegerField(null=True, blank=True)
    base_per_ant_e_rem_fgtse = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    base_per_ant_e_dps_fgtse = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    proc_cs_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    e_consignado_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    e_consignado_nr_contrato = models.CharField(max_length=8, null=True, blank=True)
    e_consignado_vre_consignado = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
