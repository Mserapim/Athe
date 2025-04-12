# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2190(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = ""
    XMLNS = ""
    GROUP = 1
    NAME = ""
    ACTION_PERM = ACTION
    info_reg_prelim_cpf_trab = models.CharField(max_length=11)
    info_reg_prelim_dt_nascto = models.DateField()
    info_reg_prelim_dt_adm = models.DateField()
    info_reg_prelim_matricula = models.CharField(max_length=30)
    info_reg_prelim_cod_categ = models.PositiveIntegerField()
    info_reg_prelim_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_reg_ctps_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    info_reg_ctps_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_reg_ctps_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    info_reg_ctps_tp_contr = models.PositiveIntegerField(null=True, blank=True)
    info_reg_ctps_dt_term = models.DateField(null=True, blank=True)
