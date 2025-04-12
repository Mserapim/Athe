# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2205(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAltCadastral.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAltCadastral/v_S_01_02_00"
    GROUP = 2
    NAME = "Alteração de Dados Cadastrais do Trabalhador"
    ACTION_PERM = ACTION
    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    alteracao_dt_alteracao = models.DateField()
    dados_trabalhador_nm_trab = models.CharField(max_length=70)
    dados_trabalhador_sexo = models.CharField(max_length=1)
    dados_trabalhador_raca_cor = models.PositiveIntegerField()
    dados_trabalhador_est_civ = models.PositiveIntegerField(null=True, blank=True)
    dados_trabalhador_grau_instr = models.CharField(max_length=2)
    dados_trabalhador_nm_soc = models.CharField(max_length=70, null=True, blank=True)
    dados_trabalhador_pais_nac = models.CharField(max_length=3)
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
    trab_imig_tmp_resid = models.PositiveIntegerField(null=True, blank=True)
    trab_imig_cond_ing = models.PositiveIntegerField(null=True, blank=True)
    info_deficiencia_def_fisica = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_visual = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_auditiva = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_def_mental = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_intelectual = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_reab_readap = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_info_cota = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_observacao = models.CharField(max_length=55, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2205"
    )
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)
