# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2420(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenTerm.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenTerm/v_S_01_02_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Término"
    ACTION_PERM = ACTION
    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_ben_termino_dt_term_beneficio = models.DateField()
    info_ben_termino_mtv_termino = models.CharField(max_length=2)
    info_ben_termino_cnpj_orgao_suc = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_ben_termino_novo_cpf = models.CharField(max_length=11, null=True, blank=True)
