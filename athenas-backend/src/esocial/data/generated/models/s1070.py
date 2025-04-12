# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1070(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabProcesso.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabProcesso/v_S_01_02_00"
    GROUP = 1
    NAME = "Tabela de Processos Administrativos/Judiciais"
    ACTION_PERM = ACTION
    ide_processo_tp_proc = models.PositiveIntegerField()
    ide_processo_nr_proc = models.CharField(max_length=21)
    ide_processo_ini_valid = models.CharField(max_length=7)
    ide_processo_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_proc_ind_autoria = models.PositiveIntegerField(null=True, blank=True)
    dados_proc_ind_mat_proc = models.PositiveIntegerField()
    dados_proc_observacao = models.CharField(max_length=55, null=True, blank=True)
    dados_proc_jud_uf_vara = models.CharField(max_length=2, null=True, blank=True)
    dados_proc_jud_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    dados_proc_jud_id_vara = models.PositiveIntegerField(null=True, blank=True)
    info_susp = models.ManyToManyField("InfoSuspensao", related_name="events")
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)
