# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2220(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtMonit.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtMonit/v_S_01_02_00"
    GROUP = 2
    NAME = "Monitoramento da Saúde do Trabalhador"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    ex_med_ocup_tp_exame_ocup = models.PositiveIntegerField()
    aso_dt_aso = models.DateField()
    aso_res_aso = models.PositiveIntegerField(null=True, blank=True)
    exame_dt_exm = models.DateField()
    exame_proc_realizado = models.PositiveIntegerField()
    exame_obs_proc = models.CharField(max_length=99, null=True, blank=True)
    exame_ord_exame = models.PositiveIntegerField(null=True, blank=True)
    exame_ind_result = models.PositiveIntegerField(null=True, blank=True)
    medico_nm_med = models.CharField(max_length=70)
    medico_nr_crm = models.CharField(max_length=10, null=True, blank=True)
    medico_uf_crm = models.CharField(max_length=2, null=True, blank=True)
    resp_monit_cpf_resp = models.CharField(max_length=11, null=True, blank=True)
    resp_monit_nm_resp = models.CharField(max_length=70, null=True, blank=True)
    resp_monit_nr_crm = models.CharField(max_length=10, null=True, blank=True)
    resp_monit_uf_crm = models.CharField(max_length=2, null=True, blank=True)
