# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2405(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenefAlt.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenefAlt/v_S_01_02_00"
    GROUP = 2
    NAME = "Cadastro de Beneficiário - Entes Públicos - Alteração"
    ACTION_PERM = ACTION
    ide_benef_cpf_benef = models.CharField(max_length=11)
    alteracao_dt_alteracao = models.DateField()
    dados_benef_nm_benefic = models.CharField(max_length=70)
    dados_benef_sexo = models.CharField(max_length=1)
    dados_benef_raca_cor = models.PositiveIntegerField()
    dados_benef_est_civ = models.PositiveIntegerField(null=True, blank=True)
    dados_benef_inc_fis_men = models.CharField(max_length=1)
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
        "Dependent", related_name="dependente_register_s2405"
    )
