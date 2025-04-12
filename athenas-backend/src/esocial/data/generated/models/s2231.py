# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2231(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCessao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCessao/v_S_01_02_00"
    GROUP = 2
    NAME = "Cessão/Exercício em Outro Órgão"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    ini_cessao_dt_ini_cessao = models.DateField(null=True, blank=True)
    ini_cessao_cnpj_cess = models.CharField(max_length=14, null=True, blank=True)
    ini_cessao_resp_remun = models.CharField(max_length=1, null=True, blank=True)
    fim_cessao_dt_term_cessao = models.DateField(null=True, blank=True)
