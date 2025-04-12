# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2399(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVTermino.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVTermino/v_S_01_02_00"
    GROUP = 2
    NAME = "Trabalhador Sem Vínculo – Término"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    ide_trab_sem_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_trab_sem_vinculo_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_trab_sem_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_termino_dt_term = models.DateField()
    info_tsv_termino_mtv_deslig_tsv = models.CharField(
        max_length=2, null=True, blank=True
    )
    info_tsv_termino_pens_alim = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_termino_perc_aliment = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_tsv_termino_vr_alim = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_tsv_termino_nr_proc_trab = models.CharField(
        max_length=20, null=True, blank=True
    )
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
    info_simples_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_register_s2399"
    )
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remun_apos_term_ind_remun = models.PositiveIntegerField(null=True, blank=True)
    remun_apos_term_dt_fim_remun = models.DateField(null=True, blank=True)
