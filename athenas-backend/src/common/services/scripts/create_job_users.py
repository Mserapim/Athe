import django
import os
import secrets

from django.contrib.auth.models import User, Group
from standard.models import Choice
from contrib.utils import getLogger

log = getLogger(__name__)

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

JOB_USERS = [
    "job_notifyctl_handle",
    "job_diariasctl_handle",
    "job_update_ferias_atualiza_pasus",
    "job_update_ferias_atualiza_pass",
    "job_update_ferias_update_acquisition_period",
    "job_update_ferias_liberar_pass",
    "job_update_ferias_notify_usufruto",
    "job_update_ferias_create_vacation_departure",
    "job_estagioctl_atualiza_estagio_verificando_afastamentos",
    "job_estagioctl_notify_liberacao",
    "job_pontoctl_remove_faltas_zeradas",
    "job_update_servidor_procedimento_movimentacao_requisicao",
    "job_update_servidor_servidor_exercicio",
    "job_update_servidor_atualizar_servidor_lotacao",
    "job_update_servidor_situacao_funcional",
    "job_update_servidor_afastamento",
    "job_update_servidor_atualizar_movimentacao_substituicao",
    "job_update_servidor_declaration",
    "job_update_servidor_workplacehistory",
    "job_rh_update_atualizar_movimentacao_posse",
    "job_rh_update_cmd_terminate_trainee",
    "job_rh_update_cmd_terminate_resident",
    "job_rh_update_cmd_termination_process",
    "job_rh_update_cmd_activate_workload_by_date",
    "job_rh_update_cmd_inactivate_workload_by_date",
    "job_registration_load_employeers",
    "job_registration_load_dependents",
    "job_user_permission_remove_handle",
    "job_update_socialsecurity_update_employmentbond",
    "job_update_socialsecurity_update_retirementprevision",
    "job_dayoffctl_update_usufruct",
    "job_dayoffctl_update_acquisition_period",
    "job_dayoffctl_release",
    "job_dayoffctl_notify_usufruct",
    "job_dayoffctl_create_departure",
    "job_dayoffctl_auto_authorization",
    "job_siatuctl_verify_pendency",
    "job_judnotify_handle",
    "job_juddeadline_handle",
    "job_cirdir__exec_actions",
    "job_cifctl_verify_pendency",
    "job_cifctl_notify",
    "job_raf_admin_handle",
    "job_protocolctl_handle",
    "job_clinicalctl__build_all_pendent",
    "job_clinicalctl__dispatch_all_pendent",
    "job_vacationgeneratorctl_server_generator",
    "job_vacationgeneratorctl_member_generator",
    "job_vacationgeneratorctl_trainee_generator",
    "job_vacationgeneratorctl_resident_generator",
    "job_updateapproverctl_pvf_update_approver",
    "job_automaticsubstitutectl_acknowledgment_automatic",
    "job_enablesaledaysctl_enable_or_disable_sale_days",
    "job_sinc_form_nomeacao_residentes",
    "job_automacao_status_trabalho_remoto",
    "job_gera_faltas_retroativo",
    "job_popular_justificativas",
    "job_atualizar_lista_antiguidades_membros",
    "job_atualizar_todos_servidores",
    "job_automatizacao_eventos_cadastro_esocial",
    "sdc",  # sistema de custos
    "job_folhaponto_atualizar_campo_marcacao",
    "job_folhaponto_import_justif",
    "job_folhaponto_import_batidas",
    "job_notifica_desligamento_res_est_vol",
    "job_inativa_carga_horaria",
    "mpmt_ad_service",
    "athenas_diarias",
    "job_athenas_diarias",
    "job_abertura_prazo_teletrabalho",
    "job_encerramento_prazo_teletrabalho",
    "job_nao_envio_teletrabalho",
    "job_notifica_aprovadores_teletrabalho",
    "job_limpar_grupo_usuarios_servidores_inativos",
    "job_notificar_prestacao_contas_colaborador_externo",
    "job_atualiza_status_teletrabalho",
    "diarias_mpmt_prestacao_externa",
    "job_diarias_atualizacao_status_pagamento",
    "job_notificar_prestacao_contas",
    "job_bloquear_mov_teletrabalho",
    "job_homologar_usufrutos_autorizado",
    "job_athenas_gerar_afastamento_usufruto_ferramenta",
    "job_efetivar_solicitacoes_automatico",
]

API_USERS = [
    "user_api",  # portal transparência
    "api_residente",  # Residentes
    "api_econtrol",  # E-control
    "api_dify",  # Dify
    "api_smc",  # Sistema de movimentacação de carreira
    "api_painel360",  # Painel 360
    "api_sisplan",  # Sisplan
]


def cria_usuarios():
    for user in JOB_USERS:
        password = secrets.token_urlsafe(32)
        if not User.objects.filter(username=user).exists():
            obj = User.objects.create_superuser(user, f"{user}@mpmt.mp.br", password)
        else:
            obj = User.objects.get(username=user)

        group_name = Choice.objects.filter(
            name="PERMISSION_SERVICES", app_label="common"
        ).first()
        group = Group.objects.get(name=group_name)
        obj.groups.add(group)
        obj.save()


def cria_usuarios_api():
    for user in API_USERS:
        password = secrets.token_urlsafe(32)
        if not User.objects.filter(username=user).exists():
            User.objects.create_user(user, f"{user}@mpmt.mp.br", password)
