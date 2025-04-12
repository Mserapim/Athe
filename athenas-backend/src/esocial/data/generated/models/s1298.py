# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1298(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReabreEvPer.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReabreEvPer/v_S_01_02_00"
    GROUP = 3
    NAME = "Reabertura dos Eventos Periódicos"
    ACTION_PERM = ACTION
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
