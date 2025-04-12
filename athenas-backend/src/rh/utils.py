# -.- coding: utf-8 -.-
"""
    Utils from rh package.
"""
import random

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import mail_managers
from django.db import transaction
from django.template.loader import render_to_string
from app.settings import HERMES_TOKEN
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger

from engine.models import ControllerPermission, GroupPermission
from engine.mq.const import (
    SISTEMA_HERMES,
    TIPO_TASK_PROCESSAMENTO_EMAIL_PESSOAL,
    TIPO_TOKEN_HERMES,
)
from engine.notification.models import Notification
from standard.models import Item, EmailTemplate
from common.util.send_email import EmailNotification

from rh.const import CATEGORIA_SERVIDOR, SERVIDOR_LOTACAO_ESTADO
from rh.constants_functional_situations import SITUACAO_FUNCIONAL


log = getLogger(__name__)


def notify_employee(
    msg_or_mid="NOTIFICACAO_ATHENAS", employee=[], sender=None, types=["SYS"], **kargs
):
    """
    :py:function:: notify_employee(msg_or_mid, target, sender=None, types=['SYS'], **kargs)

    Notify employee with a message

    :param str msg_or_mid: Message id or Message name. Default 'NOTIFICACAO_ATHENAS'
    :param list employee: Servidor list
    :param object sender: Object
    :param str list types: Types of message
    :param dict kargs: Parameters to format message
    """
    for empl in employee:
        notify(msg_or_mid, empl, sender, **kargs)

    user_employee = employee_from_user(get_current_user())

    if (
        user_employee
        and not isinstance(employee, list)
        and not employee.filter(pk=user_employee.pk).exists()
    ):
        notify(msg_or_mid, user_employee, sender, **kargs)
    elif user_employee and user_employee in employee:
        notify(msg_or_mid, user_employee, sender, **kargs)


def notify(msg_or_mid, employee, sender=None, types=["SYS"], **kargs):
    """
    :py:function:: notify(msg_or_mid, employee, sender=None, types=['SYS'], **kargs)

    This method is a wrapper to Notification.notify. Its implements transaction to isolate Exception.

    :param str msg_or_mid: Message id or Message name.
    :param Servidor employee: Servidor
    :param object sender: Object
    :param str list types: Types of message
    :param dict kargs: Parameters to format message

    """
    try:
        with transaction.atomic():
            Notification.notify(
                msg_or_mid,
                employee,
                sender if sender is not None else User.objects.get(username="athenas"),
                types=types,
                **kargs,
            )
    except Exception as err:
        log.exception(err)


def send_mail_and_notify(
    source="",
    message="",
    err=None,
    sender=None,
    employee=[],
    msg_or_mid="NOTIFICACAO_ATHENAS",
    fail_silently=True,
):
    """
    :py:function:: send_mail_and_notify(
        source='', message='', err=None, sender=None, employee=[], msg_or_mid='NOTIFICACAO_ATHENAS',
        fail_silently=True)

    Este método é responsável por enviar email e notificações.
    Emails são enviados para os administradores do sistema.
    Notificações são enviadas para o usuário.

    :param str source: Str representation of the source of this message
    :param str message: The body of the message
    :param Exception err: Exception
    :param object sender: Object sender
    :param queryset employee: Servidor queryset

    :return void
    """
    mail_managers(
        source,
        "%s :  -> %s" % (message, err if err is not None else ""),
        fail_silently=fail_silently,
    )
    notify_employee(
        msg_or_mid=msg_or_mid, employee=employee, sender=sender, mensagem=message
    )


def servidor_lotacao_estado_unicode(key):
    """
    Este método formata a situação funcional removendo o prefixo. Deixando apenas o valor descricional.
    """
    return SERVIDOR_LOTACAO_ESTADO.get(key)


def situation_unicode(date_start, date_end):
    situation = "ATIVO"
    try:
        if datetime.now().date() < date_start:
            situation = "AGENDADO"
        elif date_end and datetime.now().date() > date_end:
            situation = "ENCERRADO"
    except Exception as err:
        log.exception(err)
    return situation


def departure_reason_unicode(departure):
    departure_unicode = "Não encontrada"
    if departure:
        departure_unicode = format_situacao_funcional(departure.situacao_funcional)
        if departure.situacao_funcional == "ATIVO_LIC_SAUDE":
            departure_unicode = departure.instancia_modelo._meta.verbose_name
    return departure_unicode


def verifica_situacao_funcional(key):
    """
    Este método verifica e retorna o estado base da situação funcional.
    ATIVO..., INATIVO..., NOT_FOUND
    """
    status = "ATIVO"
    if key.startswith("INATIVO"):
        status = "INATIVO"
    elif key.startswith("NOT_FOUND"):
        status = "NOT_FOUND"
    return status


def format_situacao_funcional(key):
    """
    Este método formata a situação funcional removendo o prefixo. Deixando apenas o valor descricional.
    """
    return SITUACAO_FUNCIONAL.get(key)


def verifica_categoria(key):
    """
    Este método verifica a qual categoria foi informada.
    """
    status = "SERVIDOR"
    if key.startswith("MEMBRO"):
        status = "MEMBRO"
    elif key.startswith("ESTAGIARIO"):
        status = "ESTAGIARIO"
    return status


def format_categoria(key, pre_fixo=True):
    """
    Este método formata a categoria informada.
    """
    if pre_fixo:
        return CATEGORIA_SERVIDOR.get(key)
    tamanho = 9
    if verifica_categoria(key) == "MEMBRO":
        tamanho = 7
    elif verifica_categoria(key) == "ESTAGIARIO":
        tamanho = 11
    fim = tamanho
    try:
        fim = len(CATEGORIA_SERVIDOR.get(key))
    except Exception:
        pass
    return CATEGORIA_SERVIDOR.get(key)[tamanho:fim]


def boolean_unicode(value):
    return "SIM" if value else "NÃO"


def is_active(today=None, date_start=None, date_end=None):
    """
     :py:function:: is_active(date=None, date_start=None, date_end=None):

     This method verify compare today with date_end to answer if is active.
     The today parameter assume datetime.now().date() as default value.

     :param date date_start: Can be datetime.now().date() or datetime.now(), but date_start should be the same type
     to avoid raises
     :param date date_end: Can be datetime.now().date() or datetime.now(), but date_end should be the same type to
     avoid raises
     :param date today: Can be datetime.now().date() or datetime.now(), but date should be the same type to avoid
     raises
    :return: True of False
    :rtype: boolean
    :raises TypeError: can't compare datetime.datetime to datetime.date
    """
    active = True
    today = datetime.now().date() if not today else today
    date_start = today if not date_start else date_start
    if date_start > today:
        active = False
    if date_end and date_end < today:
        active = False
    return active


def dump_instance_fields_dict(instance):
    """
     :py:function:: dump_instance_fields_dict(instance)

     This method dumps instance fields to a dict.

     :param models.Model instance: models.Model instance of
    :return: dict of models.Model instance
    :rtype: dict
    """
    return dict(
        [
            (fld.name, getattr(instance, fld.name))
            for fld in instance._meta.fields
            if fld.name != instance._meta.pk
        ]
    )


def show_trace(stack, indent_size=0, indent_char="."):
    """
    stack = traceback.extract_stack()
    """
    indent = 0
    for filename, lineno, module, unused in stack:
        log.info(
            "%(indent)s%(filename)s in line %(lineno)d"
            % {
                "indent": indent_char * (indent * indent_size),
                "filename": filename,
                "lineno": lineno,
            }
        )
        indent += 1


def _concat_dict(errors={}, err=None):
    count = 1
    error_dict = {}
    if type(err) == dict:
        error_dict.update(err)
    elif not isinstance(err, ValidationError):
        while ("err%s" % count) in list(errors.keys()):
            count += 1
        error_dict = {"err%s" % count: err}
    elif hasattr(err, "error_dict"):
        error_dict.update(err.message_dict)
    elif hasattr(err, "error_list"):
        for msg in err.error_list:
            error_dict.update({"err%s" % count: str(msg)})
            count += 1
    else:
        error_dict = {"err%s" % count: str(err)}

    for key in list(error_dict.keys()):
        errors.update({key: error_dict.get(key)})
    return errors


class FeatureFlagDisabledError(Exception):
    def __init__(self, message=None):
        if not message:
            "Could not run code. Feature flag is disabled."
        super().__init__(message)


def is_arquimedes_enabled():
    """Tells if Athenas has integration with Arquimedes

    Use this function to decide between running or not Arquimedes related code.
    """
    from django.conf import settings

    return getattr(settings, "ENABLE_ARQUIMEDES", False)


def feature_flag_arquimedes(func):
    """A feature flag decorator for functions executing Arquimedes related code

    Use this decorator to decide between running or not Arquimedes related functions.
    """

    def wrapper(*args, **kwargs):
        if is_arquimedes_enabled():
            return func(*args, **kwargs)
        raise FeatureFlagDisabledError(
            f"Could not run `{func.__name__}` function. "
            "Feature flag `ENABLE_ARQUIMEDES` is disabled."
        )

    return wrapper


def create_username(name, username_type=""):
    """Este método retonar o usuário baseado na configuração

    Args:
        name (str): Nome do servidor
        username_type (str, optional): Configuração do tipo do nome usuário. Defaults to ''.

    Returns:
        str: nome do usuário
    """

    if username_type == "initials_last":
        username = initials_last(name)
    else:
        username = first_dot_last(name)

    return username


def initials_last(name):
    """Este método retorna uma string com as iniciais do nome e último nome do servidor

    Args:
        name (str): Nome do Servidor

    Returns:
        str: Iniciais e Último nome do servidor concatenado
    """

    invalid_names = [
        "da",
        "de",
        "di",
        "do",
        "du",
        "das",
        "des",
        "dis",
        "dos",
        "dus",
        "e",
    ]

    name_initials = "".join(
        [n[0] for n in normalize_name(name)[:-1] if n not in invalid_names]
    )
    # name_initials = name_lower_splitted[0][0] if not exist else name_lower_splitted[0][0:2]
    last_name = normalize_name(name)[-1]

    return f"{name_initials}{last_name}"


def first_dot_last(name):
    """Este método retorna uma string com o primeiro e último nome do servidor separados por ponto

    Args:
        name (str): Nome do Servidor

    Returns:
        str: Primeiro e Último nome do servidor separado por ponto e concatenado
    """
    first_name = normalize_name(name)[0]
    last_name = normalize_name(name)[-1]

    return f"{first_name}.{last_name}"


def normalize_name(name):
    """Este método realiza a normalização do nome do servidor

    Args:
        name (str): Nome do servidor

    Returns:
        list: Lista com os nomes do servidor
    """

    return name.lower().split()


def assign_group_permission(user):
    """Este método realiza a atribuição de permissão de grupo ao Usuário

    Args:
        employee (str): Usuário
    """
    group_permissions = GroupPermission.objects.filter(is_default=True)
    for group_permission in group_permissions:
        group_permission.user_set.add(user)


def vincular_grupo_permissao_padrao(servidor):
    """Este método realiza a atribuição de permissão de grupo padrão ao servidor

    Args:
        servidor
    """
    from menu_permissoes.models import UsuarioGrupo

    grupos_permissoes = UsuarioGrupo.objects.filter(grupo_padrao=True)
    for groupo_permissao in grupos_permissoes:
        groupo_permissao.servidores.add(servidor)


def assign_func_permission(user):
    """Este método realiza a atribuição de permissão de funcionalidade ao Usuário

    Args:
        employee (str): Usuário
    """
    config = Item.objects.filter(key="servers_permissions").first()
    controller_permissions = ControllerPermission.objects.filter(is_default=True)
    for controller_permission in controller_permissions:
        if config and controller_permission.name in config.value.split(","):
            if user.servidor.type_by_possession not in ["MBR", "MEL", "MCM"]:
                user.controllerpermission_set.add(controller_permission)
        else:
            user.controllerpermission_set.add(controller_permission)


def set_employee_user(employee):
    """Este método verificar se tem usuário para um cpf e atrubui esse usuário a nova matricula
    Args:
        employee (str): Servidor
    """
    record = User.objects.filter(
        servidor__pessoa_fisica__cpf=employee.pessoa_fisica.cpf
    ).order_by("-servidor__termination_date")
    if record:
        user = record[0]
        old_record = record[0].servidor
        if not old_record.ativo:
            old_record.user = None
            employee.user = user
            old_record.save()
            employee.save()


def envia_cod_validacao(pessoa):
    """
    Envia código por e-mail para validação do e-mail pessoal fornecido
    """

    lista_destinatarios = [
        {
            "email": pessoa.email_pessoal,
            "nome": pessoa.nome,
        },
    ]

    email_template = EmailTemplate.objects.get(code="VALIDACAO_EMAIL_PESSOAL")
    conteudo = email_template.contents.replace("%NOME%", pessoa.nome).replace(
        "%CODIGO%", str(pessoa.codigo_email)
    )
    assunto = email_template.subject
    html_content = render_to_string("util/template_email.html", {"message": conteudo})
    token = TIPO_TOKEN_HERMES.get(TIPO_TASK_PROCESSAMENTO_EMAIL_PESSOAL, HERMES_TOKEN)
    sistema = SISTEMA_HERMES.get(TIPO_TASK_PROCESSAMENTO_EMAIL_PESSOAL, "ATHENAS")
    EmailNotification().send_email_default(
        lista_destinatarios, assunto, html_content, hermes_token=token, sistema=sistema
    )


def criar_gcpp_aux_creche(dependencia):
    from rh.models import Servidor
    from rh.gfp.models import Evento, Folha
    from rh.gfp.gcpp_utils import criar_gcpp
    from rh.gfp.calcs.mpmt.aid import AidRetroactiveDaycare

    dt_inicio_dep = f"{dependencia.data_inicio.year}{dependencia.data_inicio.month:02}"
    dt_cadastro_dep = f"{dependencia.created_at.year}{dependencia.created_at.month:02}"

    if dt_inicio_dep < dt_cadastro_dep:
        servidor = dependencia.dependente.servidor
        servidor_conf_por = Servidor.objects.get(user__id=get_current_user().id)
        folha = (
            Folha.objects.filter(tipo_folha__titulo="NORMAL")
            .order_by("periodo")
            .first()
        )
        evento = Evento.objects.get(numero="06606")
        qnt = AidRetroactiveDaycare(servidor, folha, evento).qtd_por_dependencia(
            dependencia
        )

        gcpp = criar_gcpp(
            servidor=servidor,
            evento=evento,
            qtd_dias=qnt,
            periodo_ano=folha.periodo.ano,
            periodo_mes=folha.periodo.mes,
            servidor_conferido_por=servidor_conf_por,
            modulo_origem="Cadastro de Dependentes",
            info="",
        )

        gcpp.dependencia = dependencia
        gcpp.save()


def get_substituicoes(date=None, lapse=None, yesterday=None, today=None):
    from rh.models import MovimentacaoSubstituicao

    date = datetime.now().date() if not date else date
    lapse = 1 if not lapse else lapse
    lapse_day = date - relativedelta(days=lapse)
    if yesterday and today:
        return MovimentacaoSubstituicao.objects.filter(
            (Q(data_fim__gte=yesterday) & Q(data_fim__lt=today))
            | (Q(data_inicio__gte=yesterday) & Q(data_inicio__lte=today))
            | Q(modified_at=today)
        )
    else:
        return MovimentacaoSubstituicao.objects.filter(
            (Q(data_fim__gte=lapse_day) & Q(data_fim__lte=date))
            | (Q(data_inicio__gte=lapse_day) & Q(data_inicio__lte=date))
        )


def notificar_nao_criacao_lotacao(mov_sub):
    from django.template.loader import render_to_string
    from common.util.send_email import EmailNotification
    from standard.models import EmailTemplate, Item

    """
    Esta função é usada para notificar sobre a não criação de designação, pois o membro
    não está lotado no local em que a substituição foi programada
    
    :param mov_sub: instância do modelo MovimentacaoSubstituicao
    """

    lista_emails = Item.objects.get(
        configuration__application="rh", key="detinatarios_nao_criacao_lotacao"
    ).value
    lista_destinatarios = get_emails_destinatarios(lista_emails)
    email_template = EmailTemplate.objects.get(code="NOTIFICA_NAO_CRIACAO_LOTACAO")

    conteudo = (
        email_template.contents.replace(
            "%solicitante%", f"{mov_sub.servidor_substituido}"
        )
        .replace("%lotacao%", f"{mov_sub.designation_substituted}")
        .replace("%substituto%", f"{mov_sub.servidor}")
        .replace("%periodo%", f"{mov_sub.data_inicio} - {mov_sub.data_fim}")
    )
    html_content = render_to_string("util/template_email.html", {"message": conteudo})
    EmailNotification().send_email_default(
        lista_destinatarios, email_template.subject, html_content
    )


def get_emails_destinatarios(lista_emails):
    from rh.models import PessoaFisica

    emails_destinatarios = []
    emails = lista_emails.split(",")
    for email in emails:
        person = PessoaFisica.objects.filter(email_institucional=email.upper()).first()
        emails_destinatarios.append(
            {
                "email": email,
                "nome": person.nome if person else email.upper(),
                "idUsuario": (
                    person.servidor_set.last().id_usuario_mastiff if person else None
                ),
            }
        )
    return emails_destinatarios


def get_email_template(template_code):
    try:
        log.info(f"Buscando o Modelo de Email: {template_code}!")

        return EmailTemplate.objects.get(code=template_code)
    except EmailTemplate.DoesNotExist:
        log.error(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
        print(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
        raise Exception(
            f"Não foi possível encontrar o Modelo de Email: {template_code}!"
        )


def enviar_email_notificacao_desligamento_res_vol_est(servidor):
    try:
        email_template_code = (
            "NOTIFICACAO_DESLIGAMENTO_RESIDENTES_ESTAGIARIOS_VOLUNTARIOS"
        )

        email_template = get_email_template(email_template_code)

        lotacao = servidor.get_workplace_only().first().lotacao.nome

        message = (
            email_template.contents.replace(
                "%nome%", servidor.pessoa_fisica.social_name
            )
            .replace("%matricula%", str(servidor.matricula))
            .replace("%tipo%", servidor.get_type_by_possession_display())
            .replace("%CPF%", servidor.pessoa_fisica.cpf)
            .replace("%lotacao%", lotacao)
            .replace("%supervisor%", servidor.chefe_imediato.pessoa_fisica.social_name)
            .replace("%data_inicio%", servidor.exercise_date.strftime("%d/%m/%Y"))
            .replace("%data_fim%", servidor.termination_date.strftime("%d/%m/%Y"))
        )

        destinatarios = [
            {
                "email": "suporte@mpmt.mp.br",
                "nome": "Suporte",
            },
        ]

        if servidor.type_by_possession == "EST":
            config_destinatarios = Item.objects.get(
                key="EMAIL_DESLIGAMENTO_ESTAGIARIOS"
            )

            for destinatario in config_destinatarios.value.split(";"):
                destinatarios.append(
                    {
                        "email": destinatario,
                        "nome": "",
                    }
                )
        elif servidor.type_by_possession == "RES":
            config_destinatarios = Item.objects.get(key="EMAIL_DESLIGAMENTO_RESIDENTES")

            for destinatario in config_destinatarios.value.split(";"):
                destinatarios.append(
                    {
                        "email": destinatario,
                        "nome": "",
                    }
                )
        elif servidor.type_by_possession == "VOL":
            config_destinatarios = Item.objects.get(
                key="EMAIL_DESLIGAMENTO_VOLUNTARIOS"
            )

            for destinatario in config_destinatarios.value.split(";"):
                destinatarios.append(
                    {
                        "email": destinatario,
                        "nome": "",
                    }
                )

        data_fim_teletrabalho = servidor.data_desligamento - timedelta(1)

        if servidor.teletrabalho_ativo(data_fim_teletrabalho):
            config_destinatarios = Item.objects.get(
                key="EMAIL_DESLIGAMENTO_TELETRABALHO"
            )

            for destinatario in config_destinatarios.value.split(";"):
                destinatarios.append(
                    {
                        "email": destinatario,
                        "nome": "",
                    }
                )

        log.info(
            f"Envio de notificação de desligamento do servidor {servidor.pessoa_fisica.social_name} - {servidor.matricula}"
        )
        print(
            f"Envio de notificação de desligamento do servidor {servidor.pessoa_fisica.social_name} - {servidor.matricula}"
        )

        html_content = render_to_string(
            "util/template_email.html", {"message": message}
        )
        EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

    except Exception as error:
        log.info(error)
        print(error)
        raise Exception(error)


def atualizar_data_fim_carga_horaria(servidor, nova_data_fim):
    """
    Atualiza o campo data_fim da carga horária ativa do servidor, se necessário.
    """

    from rh.models import CargaHoraria

    try:
        carga = CargaHoraria.objects.get(servidor=servidor, active=True)
    except CargaHoraria.DoesNotExist:
        return

    if carga.data_fim != nova_data_fim:
        try:
            carga.data_fim = nova_data_fim
            carga.save()
        except Exception as ex:
            raise Exception("Erro ao atualizar CargaHoraria: %s" % ex)


def remover_data_fim_carga_horaria(servidor):
    """
    Remove (limpa) a data_fim da carga horária ativa do servidor,
    definindo o campo como None.
    """
    from rh.models import CargaHoraria

    try:
        carga = CargaHoraria.objects.get(servidor=servidor, active=True)
        if carga.data_fim is not None:
            carga.data_fim = None
            carga.save()
    except CargaHoraria.DoesNotExist:
        return
    except Exception as ex:
        raise Exception("Erro ao remover data_fim da CargaHoraria: %s" % ex)
