# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class S2200(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAdmissao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_02_00"
    GROUP = 2
    NAME = "Admissão de Trabalhador"
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
    info_deficiencia_info_cota = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_observacao = models.CharField(max_length=55, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2200"
    )
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)
    vinculo_matricula = models.CharField(max_length=30)
    vinculo_tp_reg_trab = models.PositiveIntegerField()
    vinculo_tp_reg_prev = models.PositiveIntegerField()
    vinculo_cad_ini = models.CharField(max_length=1)
    info_celetista_dt_adm = models.DateField(null=True, blank=True)
    info_celetista_tp_admissao = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_ind_admissao = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nr_proc_trab = models.CharField(max_length=20, null=True, blank=True)
    info_celetista_tp_reg_jor = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_dt_base = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_cnpj_sind_categ_prof = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_celetista_mat_anot_jud = models.CharField(max_length=30, null=True, blank=True)
    fgts_dt_opc_fgts = models.DateField(null=True, blank=True)
    trab_temporario_hip_leg = models.PositiveIntegerField(null=True, blank=True)
    trab_temporario_just_contr = models.CharField(max_length=99, null=True, blank=True)
    ide_estab_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_trab_substituido_cpf_trab_subst = models.CharField(
        max_length=11, null=True, blank=True
    )
    aprend_ind_aprend = models.PositiveIntegerField(null=True, blank=True)
    aprend_cnpj_ent_qual = models.CharField(max_length=14, null=True, blank=True)
    aprend_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    aprend_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    aprend_cnpj_prat = models.CharField(max_length=14, null=True, blank=True)
    info_estatutario_tp_prov = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_dt_exercicio = models.DateField(null=True, blank=True)
    info_estatutario_tp_plan_rp = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_ind_teto_rgps = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_ind_abono_perm = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_dt_ini_abono = models.DateField(null=True, blank=True)
    info_contrato_nm_cargo = models.CharField(max_length=0, null=True, blank=True)
    info_contrato_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_dt_ingr_cargo = models.DateField(null=True, blank=True)
    info_contrato_nm_funcao = models.CharField(max_length=0, null=True, blank=True)
    info_contrato_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_acum_cargo = models.CharField(max_length=1, null=True, blank=True)
    info_contrato_cod_categ = models.PositiveIntegerField()
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=99, null=True, blank=True)
    duracao_tp_contr = models.PositiveIntegerField(null=True, blank=True)
    duracao_dt_term = models.DateField(null=True, blank=True)
    duracao_clau_assec = models.CharField(max_length=1, null=True, blank=True)
    duracao_obj_det = models.CharField(max_length=55, null=True, blank=True)
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
    hor_contratual_qtd_hrs_sem = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    hor_contratual_tp_jornada = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_tmp_parc = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_hor_noturno = models.CharField(max_length=1, null=True, blank=True)
    hor_contratual_dsc_jorn = models.CharField(max_length=99, null=True, blank=True)
    alvara_judicial_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=55, null=True, blank=True)
    trei_cap_cod_trei_cap = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_transf = models.DateField(null=True, blank=True)
    sucessao_vinc_observacao = models.CharField(max_length=55, null=True, blank=True)
    transf_dom_cpf_substituido = models.CharField(max_length=11, null=True, blank=True)
    transf_dom_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    transf_dom_dt_transf = models.DateField(null=True, blank=True)
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=55, null=True, blank=True)
    afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    afastamento_cod_mot_afast = models.CharField(max_length=2, null=True, blank=True)
    desligamento_dt_deslig = models.DateField(null=True, blank=True)
    cessao_dt_ini_cessao = models.DateField(null=True, blank=True)
