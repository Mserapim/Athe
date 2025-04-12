# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2400(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenefIn.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenefIn/v_S_01_02_00"
    GROUP = 2
    NAME = "Cadastro de Beneficiário - Entes Públicos - Início"
    ACTION_PERM = ACTION
    beneficiario_cpf_benef = models.CharField(max_length=11)
    beneficiario_nm_benefic = models.CharField(max_length=70)
    beneficiario_dt_nascto = models.DateField()
    beneficiario_dt_inicio = models.DateField()
    beneficiario_sexo = models.CharField(max_length=1, null=True, blank=True)
    beneficiario_raca_cor = models.PositiveIntegerField()
    beneficiario_est_civ = models.PositiveIntegerField(null=True, blank=True)
    beneficiario_inc_fis_men = models.CharField(max_length=1)
    beneficiario_dt_inc_fis_men = models.DateField(null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=0, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=0, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2400"
    )
