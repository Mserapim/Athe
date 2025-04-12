# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1270(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = ""
    XMLNS = ""
    GROUP = 1
    NAME = ""
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    remun_av_np_tp_insc = models.PositiveIntegerField()
    remun_av_np_nr_insc = models.CharField(max_length=14)
    remun_av_np_cod_lotacao = models.CharField(max_length=30)
    remun_av_np_vr_bc_cp00 = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_bc_cp15 = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_bc_cp20 = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_bc_cp25 = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_bc_cp13 = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_bc_fgts = models.DecimalField(max_digits=14, decimal_places=2)
    remun_av_np_vr_desc_cp = models.DecimalField(max_digits=14, decimal_places=2)
