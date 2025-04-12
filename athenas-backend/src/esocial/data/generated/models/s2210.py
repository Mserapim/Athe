# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2210(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCAT.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCAT/v_S_01_02_00"
    GROUP = 2
    NAME = "Comunicação de Acidente de Trabalho"
    ACTION_PERM = ACTION
    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    cat_dt_acid = models.DateField()
    cat_tp_acid = models.PositiveIntegerField()
    cat_hr_acid = models.CharField(max_length=4, null=True, blank=True)
    cat_hrs_trab_antes_acid = models.CharField(max_length=4, null=True, blank=True)
    cat_tp_cat = models.PositiveIntegerField()
    cat_ind_cat_obito = models.CharField(max_length=1)
    cat_dt_obito = models.DateField(null=True, blank=True)
    cat_ind_comun_policia = models.CharField(max_length=1)
    cat_cod_sit_geradora = models.PositiveIntegerField()
    cat_iniciat_cat = models.PositiveIntegerField()
    cat_obs_cat = models.CharField(max_length=99, null=True, blank=True)
    cat_ult_dia_trab = models.DateField(null=True, blank=True)
    cat_houve_afast = models.CharField(max_length=1, null=True, blank=True)
    local_acidente_tp_local = models.PositiveIntegerField()
    local_acidente_dsc_local = models.CharField(max_length=55, null=True, blank=True)
    local_acidente_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    local_acidente_dsc_lograd = models.CharField(max_length=0)
    local_acidente_nr_lograd = models.CharField(max_length=10)
    local_acidente_complemento = models.CharField(max_length=30, null=True, blank=True)
    local_acidente_bairro = models.CharField(max_length=90, null=True, blank=True)
    local_acidente_cep = models.CharField(max_length=8, null=True, blank=True)
    local_acidente_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    local_acidente_uf = models.CharField(max_length=2, null=True, blank=True)
    local_acidente_pais = models.CharField(max_length=3, null=True, blank=True)
    local_acidente_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    ide_local_acid_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_local_acid_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    parte_atingida_cod_parte_ating = models.PositiveIntegerField()
    parte_atingida_lateralidade = models.PositiveIntegerField()
    agente_causador_cod_agnt_causador = models.PositiveIntegerField()
    atestado_dt_atendimento = models.DateField()
    atestado_hr_atendimento = models.CharField(max_length=4)
    atestado_ind_internacao = models.CharField(max_length=1)
    atestado_dur_trat = models.PositiveIntegerField()
    atestado_ind_afast = models.CharField(max_length=1)
    atestado_dsc_lesao = models.PositiveIntegerField()
    atestado_dsc_comp_lesao = models.CharField(max_length=0, null=True, blank=True)
    atestado_diag_provavel = models.CharField(max_length=0, null=True, blank=True)
    atestado_cod_cid = models.CharField(max_length=4)
    atestado_observacao = models.CharField(max_length=55, null=True, blank=True)
    emitente_nm_emit = models.CharField(max_length=70)
    emitente_ide_oc = models.PositiveIntegerField()
    emitente_nr_oc = models.CharField(max_length=14)
    emitente_uf_oc = models.CharField(max_length=2, null=True, blank=True)
    cat_origem_nr_rec_cat_orig = models.CharField(max_length=23, null=True, blank=True)
