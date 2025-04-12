# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2230(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAfastTemp.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAfastTemp/v_S_01_02_00"
    GROUP = 2
    NAME = "Afastamento Temporário"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    ini_afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    ini_afastamento_cod_mot_afast = models.CharField(
        max_length=2, null=True, blank=True
    )
    ini_afastamento_info_mesmo_mtv = models.CharField(
        max_length=1, null=True, blank=True
    )
    ini_afastamento_tp_acid_transito = models.PositiveIntegerField(
        null=True, blank=True
    )
    ini_afastamento_observacao = models.CharField(max_length=55, null=True, blank=True)
    per_aquis_dt_inicio = models.DateField(null=True, blank=True)
    per_aquis_dt_fim = models.DateField(null=True, blank=True)
    info_cessao_cnpj_cess = models.CharField(max_length=14, null=True, blank=True)
    info_cessao_inf_onus = models.PositiveIntegerField(null=True, blank=True)
    info_mand_sind_cnpj_sind = models.CharField(max_length=14, null=True, blank=True)
    info_mand_sind_inf_onus_remun = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_cnpj_mand_elet = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_retif_orig_retif = models.PositiveIntegerField(null=True, blank=True)
    info_retif_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    info_retif_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    fim_afastamento_dt_term_afast = models.DateField(null=True, blank=True)
