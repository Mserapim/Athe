# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2410(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenIn.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenIn/v_S_01_02_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Início"
    ACTION_PERM = ACTION
    beneficiario_cpf_benef = models.CharField(max_length=11)
    beneficiario_matricula = models.CharField(max_length=30, null=True, blank=True)
    beneficiario_cnpj_origem = models.CharField(max_length=14, null=True, blank=True)
    info_ben_inicio_cad_ini = models.CharField(max_length=1)
    info_ben_inicio_ind_sit_benef = models.PositiveIntegerField(null=True, blank=True)
    info_ben_inicio_nr_beneficio = models.CharField(max_length=20)
    info_ben_inicio_dt_ini_beneficio = models.DateField()
    info_ben_inicio_dt_public = models.DateField(null=True, blank=True)
    dados_beneficio_tp_beneficio = models.CharField(max_length=4)
    dados_beneficio_tp_plan_rp = models.PositiveIntegerField()
    dados_beneficio_dsc = models.CharField(max_length=55, null=True, blank=True)
    dados_beneficio_ind_dec_jud = models.CharField(max_length=1, null=True, blank=True)
    info_pen_morte_tp_pen_morte = models.PositiveIntegerField(null=True, blank=True)
    inst_pen_morte_cpf_inst = models.CharField(max_length=11, null=True, blank=True)
    inst_pen_morte_dt_inst = models.DateField(null=True, blank=True)
    sucessao_benef_cnpj_orgao_ant = models.CharField(
        max_length=14, null=True, blank=True
    )
    sucessao_benef_nr_beneficio_ant = models.CharField(
        max_length=20, null=True, blank=True
    )
    sucessao_benef_dt_transf = models.DateField(null=True, blank=True)
    sucessao_benef_observacao = models.CharField(max_length=55, null=True, blank=True)
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_nr_beneficio_ant = models.CharField(
        max_length=20, null=True, blank=True
    )
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=55, null=True, blank=True)
    info_ben_termino_dt_term_beneficio = models.DateField(null=True, blank=True)
    info_ben_termino_mtv_termino = models.CharField(max_length=2, null=True, blank=True)
