# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2306(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVAltContr.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVAltContr/v_S_01_02_00"
    GROUP = 2
    NAME = "Alteração contratual (TSV)"
    ACTION_PERM = ACTION
    ide_trab_sem_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_trab_sem_vinculo_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_trab_sem_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_alteracao_dt_alteracao = models.DateField()
    info_tsv_alteracao_nat_atividade = models.PositiveIntegerField(
        null=True, blank=True
    )
    cargo_funcao_nm_cargo = models.CharField(max_length=0, null=True, blank=True)
    cargo_funcao_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    cargo_funcao_nm_funcao = models.CharField(max_length=0, null=True, blank=True)
    cargo_funcao_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=99, null=True, blank=True)
    info_dirigente_sindical_tp_reg_prev = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_trab_cedido_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_mand_elet_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_nat_estagio = models.CharField(max_length=1, null=True, blank=True)
    info_estagiario_niv_estagio = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_area_atuacao = models.CharField(max_length=0, null=True, blank=True)
    info_estagiario_nr_apol = models.CharField(max_length=30, null=True, blank=True)
    info_estagiario_dt_prev_term = models.DateField(null=True, blank=True)
    inst_ensino_cnpj_inst_ensino = models.CharField(
        max_length=14, null=True, blank=True
    )
    inst_ensino_nm_razao = models.CharField(max_length=0, null=True, blank=True)
    inst_ensino_dsc_lograd = models.CharField(max_length=0, null=True, blank=True)
    inst_ensino_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    inst_ensino_bairro = models.CharField(max_length=90, null=True, blank=True)
    inst_ensino_cep = models.CharField(max_length=8, null=True, blank=True)
    inst_ensino_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    inst_ensino_uf = models.CharField(max_length=2, null=True, blank=True)
    age_integracao_cnpj_agnt_integ = models.CharField(
        max_length=14, null=True, blank=True
    )
    supervisor_estagio_cpf_supervisor = models.CharField(
        max_length=11, null=True, blank=True
    )
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
