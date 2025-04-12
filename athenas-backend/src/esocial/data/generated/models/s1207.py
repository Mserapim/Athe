# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1207(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtBenPrRP.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtBenPrRP/v_S_01_02_00"
    GROUP = 3
    NAME = "Benefícios - Entes Públicos"
    ACTION_PERM = ACTION
    ide_benef_cpf_benef = models.CharField(max_length=11)
    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    dm_dev_nr_beneficio = models.CharField(max_length=20)
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
    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)
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
    ide_periodo_per_ref = models.CharField(max_length=7, null=True, blank=True)
    ide_periodo_ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_periodo_ide_estab_nr_insc = models.CharField(
        max_length=14, null=True, blank=True
    )
    ide_estab_itens_remun_cod_rubr = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_estab_itens_remun_ide_tab_rubr = models.CharField(
        max_length=8, null=True, blank=True
    )
    ide_estab_itens_remun_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    ide_estab_itens_remun_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ide_estab_itens_remun_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_estab_itens_remun_ind_apur_ir = models.PositiveIntegerField(
        null=True, blank=True
    )
