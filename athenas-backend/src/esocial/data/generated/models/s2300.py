# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2300(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVInicio.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVInicio/v_S_01_02_00"
    GROUP = 2
    NAME = "Trabalhador Sem Vínculo – Início"
    ACTION_PERM = ACTION
    trabalhador_cpf_trab = models.CharField(max_length=11)
    trabalhador_nm_trab = models.CharField(max_length=70)
    trabalhador_sexo = models.CharField(max_length=1)
    trabalhador_raca_cor = models.PositiveIntegerField()
    trabalhador_est_civ = models.PositiveIntegerField(null=True, blank=True)
    trabalhador_grau_instr = models.CharField(max_length=2)
    trabalhador_nm_soc = models.CharField(max_length=70, null=True, blank=True)
    nascimento_dt_nascto = models.DateField()
    nascimento_pais_nascto = models.CharField(max_length=3)
    nascimento_pais_nac = models.CharField(max_length=3)
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
    info_deficiencia_observacao = models.CharField(max_length=55, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2300"
    )
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)
    info_tsv_inicio_cad_ini = models.CharField(max_length=1)
    info_tsv_inicio_matricula = models.CharField(max_length=30, null=True, blank=True)
    info_tsv_inicio_cod_categ = models.PositiveIntegerField()
    info_tsv_inicio_dt_inicio = models.DateField()
    info_tsv_inicio_nr_proc_trab = models.CharField(
        max_length=20, null=True, blank=True
    )
    info_tsv_inicio_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    cargo_funcao_nm_cargo = models.CharField(max_length=0, null=True, blank=True)
    cargo_funcao_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    cargo_funcao_nm_funcao = models.CharField(max_length=0, null=True, blank=True)
    cargo_funcao_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=99, null=True, blank=True)
    fgts_dt_opc_fgts = models.DateField(null=True, blank=True)
    info_dirigente_sindical_categ_orig = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_dirigente_sindical_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    info_dirigente_sindical_nr_insc = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_dirigente_sindical_dt_adm_orig = models.DateField(null=True, blank=True)
    info_dirigente_sindical_matric_orig = models.CharField(
        max_length=30, null=True, blank=True
    )
    info_dirigente_sindical_tp_reg_trab = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_dirigente_sindical_tp_reg_prev = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_trab_cedido_categ_orig = models.PositiveIntegerField(null=True, blank=True)
    info_trab_cedido_cnpj_cednt = models.CharField(max_length=14, null=True, blank=True)
    info_trab_cedido_matric_ced = models.CharField(max_length=30, null=True, blank=True)
    info_trab_cedido_dt_adm_ced = models.DateField(null=True, blank=True)
    info_trab_cedido_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
    info_trab_cedido_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_categ_orig = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_cnpj_orig = models.CharField(max_length=14, null=True, blank=True)
    info_mand_elet_matric_orig = models.CharField(max_length=30, null=True, blank=True)
    info_mand_elet_dt_exerc_orig = models.DateField(null=True, blank=True)
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_mand_elet_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
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
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=55, null=True, blank=True)
    afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    afastamento_cod_mot_afast = models.CharField(max_length=2, null=True, blank=True)
    termino_dt_term = models.DateField(null=True, blank=True)
