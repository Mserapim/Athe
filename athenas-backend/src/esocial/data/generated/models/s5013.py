# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S5013(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = ""
    XMLNS = ""
    GROUP = 1
    NAME = ""
    ACTION_PERM = ACTION
    info_fgts_nr_rec_arq_base = models.CharField(max_length=23)
    info_fgts_ind_exist_info = models.PositiveIntegerField()
    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_lotacao_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    ide_lotacao_tp_lotacao = models.CharField(max_length=2, null=True, blank=True)
    ide_lotacao_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_lotacao_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    base_per_apur_tp_valor = models.PositiveIntegerField(null=True, blank=True)
    base_per_apur_ind_incid = models.PositiveIntegerField(null=True, blank=True)
    base_per_apur_base_fgts = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    base_per_apur_vr_fgts = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_base_per_ant_e_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_base_per_ant_e_tp_ac_conv = models.CharField(
        max_length=1, null=True, blank=True
    )
    base_per_ant_e_tp_valor_e = models.PositiveIntegerField(null=True, blank=True)
    base_per_ant_e_ind_incid_e = models.PositiveIntegerField(null=True, blank=True)
    base_per_ant_e_base_fgtse = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    base_per_ant_e_vr_fgtse = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
