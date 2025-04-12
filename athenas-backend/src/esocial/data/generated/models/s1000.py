# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S1000(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtInfoEmpregador.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtInfoEmpregador/v_S_01_02_00"
    GROUP = 1
    NAME = "Informações do Empregador/Contribuinte"
    ACTION_PERM = ACTION
    ide_periodo_ini_valid = models.CharField(max_length=7)
    ide_periodo_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    info_cadastro_class_trib = models.CharField(max_length=2, null=True, blank=True)
    info_cadastro_ind_coop = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_constr = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_des_folha = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_opc_cp = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_porte = models.CharField(max_length=1, null=True, blank=True)
    info_cadastro_ind_opt_reg_eletron = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_cadastro_cnpj_efr = models.CharField(max_length=14, null=True, blank=True)
    info_cadastro_dt_trans11096 = models.DateField(null=True, blank=True)
    info_cadastro_ind_trib_folha_pis_pasep = models.CharField(
        max_length=1, null=True, blank=True
    )
    dados_isencao_ide_min_lei = models.CharField(max_length=70, null=True, blank=True)
    dados_isencao_nr_certif = models.CharField(max_length=40, null=True, blank=True)
    dados_isencao_dt_emis_certif = models.DateField(null=True, blank=True)
    dados_isencao_dt_venc_certif = models.DateField(null=True, blank=True)
    dados_isencao_nr_prot_renov = models.CharField(max_length=40, null=True, blank=True)
    dados_isencao_dt_prot_renov = models.DateField(null=True, blank=True)
    dados_isencao_dt_dou = models.DateField(null=True, blank=True)
    dados_isencao_pag_dou = models.PositiveIntegerField(null=True, blank=True)
    info_org_internacional_ind_acordo_isen_multa = models.PositiveIntegerField(
        null=True, blank=True
    )
