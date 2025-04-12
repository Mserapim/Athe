# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S3000(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtExclusao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtExclusao/v_S_01_02_00"
    GROUP = 2
    NAME = "Exclusão de Eventos"
    ACTION_PERM = ACTION
    info_exclusao_tp_evento = models.CharField(max_length=6)
    info_exclusao_nr_rec_evt = models.CharField(max_length=23)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11, null=True, blank=True)
