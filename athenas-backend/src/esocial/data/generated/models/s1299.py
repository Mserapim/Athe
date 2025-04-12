# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1299(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtFechaEvPer.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtFechaEvPer/v_S_01_02_00"
    GROUP = 3
    NAME = "Fechamento dos Eventos Periódicos"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    info_fech_evt_remun = models.CharField(max_length=1)
    info_fech_evt_pgtos = models.CharField(max_length=1)
    info_fech_evt_com_prod = models.CharField(max_length=1)
    info_fech_evt_contrat_av_np = models.CharField(max_length=1)
    info_fech_evt_info_compl_per = models.CharField(max_length=1)
    info_fech_ind_exc_apur1250 = models.CharField(max_length=1, null=True, blank=True)
    info_fech_trans_dctf_web = models.CharField(max_length=1, null=True, blank=True)
    info_fech_nao_valid = models.CharField(max_length=1, null=True, blank=True)
