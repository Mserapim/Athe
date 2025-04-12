# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1280(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = ""
    XMLNS = ""
    GROUP = 1
    NAME = ""
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    info_subst_patr_ind_subst_patr = models.PositiveIntegerField(null=True, blank=True)
    info_subst_patr_perc_red_contrib = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_subst_patr_op_port_cod_lotacao = models.CharField(
        max_length=30, null=True, blank=True
    )
    info_ativ_concom_fator_mes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_ativ_concom_fator13 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_perc_transf11096_perc_transf = models.PositiveIntegerField(
        null=True, blank=True
    )
