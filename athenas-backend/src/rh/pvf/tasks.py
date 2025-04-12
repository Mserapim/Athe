# -*- coding: utf-8 -*-
import os
from logging import getLogger

from celery import Celery, group
from django.db.models import F, Sum

from datetime import datetime
import time

from contrib.middleware import set_current_user, get_current_user
from contrib.utils import getLogger, employee_from_user
from engine.mq.models import Task
from common.util.send_email import EmailNotification
from django.template import loader
from default.websocket import RemoteEmmiter
import pdfkit, base64
from rh.pvf.const import (
    PORTAL_COMP_CLEARANCE_MEMBERS_TYPE,
    PORTAL_COMP_VACATION_MEMBERS_TYPE,
    PORTAL_FORENSIC_RECESS_TYPE,
    PORTAL_SERVER_SHIFT_TYPE,
    REQUEST_ACT_EFETIVACAO_AUTOMATICO,
    REQUEST_ACT_INDEFERIMENTO_AUTOMATICO,
    STS_CANCELED_APPLICANT,
    STS_EFETIVACAO_AUTOMATICA,
)
from rh.pvf.utils.folha_ponto import (
    agrupar_aprovador_folha_ponto,
    enviar_email_gestor_folha_ponto_aprovador,
    filtro_gestor_folha_ponto,
    enviar_email_gestor_folha_ponto,
)
from rh.pvf.utils.folha_ponto_data import get_dados_relatorio
from django.template.loader import render_to_string
from rh.models import MovimentacaoTeletrabalho, Servidor
from rh.registerpoint.models import FolhaPontoHistoricoNotificacoes
from standard.models import EmailTemplate, Item
from rh.pvf.const import (
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_REJECTED,
    STS_STAND_BY,
)
from rh.pvf.models import PortalRequest, SendingTimeSheet
from django.db import transaction
from rh.utils import User, get_emails_destinatarios


log = getLogger(__name__)

app = Celery("pvf")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def send_mail_pvf(
    task,
    hook,
    subject,
    messages,
    solicitation,
    code,
    date,
    requester,
    observation,
    receivers,
    receivers_rh_person_ids,
    success,
    user,
):
    """
    Está Task é responsável por realizar os envios de emails do Portal Vida Funcional

    Args:
    :subject: (str) Campo assunto do email.
    :message: (str) Mensagem preambular do email.
    :solicitation: (str) Campo contendo o tipo da solicitação.
    :code: (str) Campo contendo o código da solicitação.
    :date: (str) Campo contendo a data da solicitação.
    :requester: (str) Nome do solicitante.

    :receivers: (list) Lista contendo dicionários cujas chaves são o email e nome do destinatário da mensagem.
    :receivers_rh_person_ids: (list) lista de ids do model Pessoa

    """

    state = "failed"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()
        EmailNotification().send_email_pvf(
            subject=subject,
            message=messages,
            solicitation=solicitation,
            code=code,
            date=date,
            requester=requester,
            receivers=receivers,
            receivers_rh_person_ids=receivers_rh_person_ids,
            observation=observation if observation else "",
        )
        message = success

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar enviar o email!" % (err)

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def point_sheet_report(
    task, hook, success, user, month=None, year=None, html_path=None, origem_apiv2=False
):
    """
    Está Task é responsável por renderizar um template html e criar arquivo pdf do Folha Ponto
    """

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Folha Ponto...</p>'"

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        options = {
            "--footer-font-size": "10",
            "--header-font-size": "10",
            "--footer-spacing": "5",
            "--margin-top": "0mm",
            "--margin-bottom": "15mm",
            "--margin-left": "0mm",
            "--margin-right": "0mm",
            "--footer-line": "",
        }

        values = {}
        html = loader.render_to_string(html_path, values)
        output = pdfkit.from_string(html, output_path=False, options=options)
        task.data = {
            "file": base64.b64encode(output),
            "mimetype": "application/pdf",
            "extension": "pdf",
            "filename": "Folha Ponto",
        }
        task.params = {"filename": "Folha Ponto"}
        if not origem_apiv2:
            RemoteEmmiter.emmit_for_user(
                task.owner,
                "point-sheet",
                path=f"/athenas/PointSheetReport/viewer/?uuid={task.uuid}",
                filename="Relatório Folha Ponto",
            )
        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        RemoteEmmiter.emmit_for_user(
            task.owner,
            "point-sheet-error",
            path="",
            message="Não há dados para o período pesquisado.",
            filename="Relatório Folha Ponto",
        )
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        log.error(has_exception)
        raise has_exception


@app.task()
def folha_ponto_relatorio(
    task,
    hook,
    success,
    servidor_id,
    inicio,
    fim,
    tipos_dia,
    html_path=None,
    user_id=None,
):
    """
    Está Task é responsável por renderizar um template html e criar arquivo pdf do Folha Ponto segundo dados do Athenas
    """

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Folha Ponto...</p>'"

    try:
        task.message = message
        task.state = "progress"
        options = {
            "--footer-font-size": "10",
            "--header-font-size": "10",
            "--footer-spacing": "5",
            "--margin-top": "0mm",
            "--margin-bottom": "15mm",
            "--margin-left": "0mm",
            "--margin-right": "0mm",
            "--footer-line": "",
        }

        if user_id:
            user = User.objects.get(pk=user_id)
            set_current_user(user)
        else:
            raise ValueError("Usuário não especificado para a task.")

        servidor = Servidor.objects.get(pk=servidor_id)
        values = get_dados_relatorio(inicio, fim, servidor, user, tipos_dia=tipos_dia)
        html = loader.render_to_string(html_path, values)
        output = pdfkit.from_string(html, output_path=False, options=options)
        task.data = {
            "file": base64.b64encode(output),
            "mimetype": "application/pdf",
            "extension": "pdf",
            "filename": "Folha Ponto",
        }
        task.params = {"filename": "Folha Ponto"}

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        RemoteEmmiter.emmit_for_user(
            task.owner,
            "point-sheet-error",
            path="",
            message="Não há dados para o período pesquisado.",
            filename="Relatório Folha Ponto",
        )
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        log.error(has_exception)
        raise has_exception


@app.task()
def send_mail_teletrabalho(task, hook, tele_pk, nm_template, user):
    """
    Está Task é responsável por realizar os envios de emails para os servidores pendentes de envio do teletrabalho

    Args:
    :tele_pk: (str) ID da MovimentacaoTeletrabalho.
    :nm_template: (str) Nome do template do e-mail.
    :user: (str) ID do usuário logado.

    """

    state = "failed"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()

        tele = MovimentacaoTeletrabalho.objects.get(pk=tele_pk)
        data_atual = datetime.today().date()
        data_prazo = datetime(data_atual.year, data_atual.month, 10).date()
        lista_destinatarios = ""
        if tele.servidor.pessoa_fisica.email:
            lista_destinatarios = get_emails_destinatarios(
                tele.servidor.pessoa_fisica.email
            )
            email_template = EmailTemplate.objects.get(code=nm_template)

            conteudo = (
                email_template.contents.replace(
                    "%nome%", f"{tele.servidor.pessoa_fisica.nome}"
                )
                .replace("%matricula%", f"{tele.servidor.matricula}")
                .replace(
                    "%cargo%",
                    f'{tele.servidor.job_position().cargo.nome if tele.servidor.job_position() else ""}',
                )
                .replace("%data_inicio%", f"{tele.data_inicio}")
                .replace("%data_fim%", f"{tele.data_fim}")
                .replace("%dias%", f"{(data_prazo - data_atual).days}")
            )
            html_content = render_to_string(
                "util/template_email.html", {"message": conteudo}
            )
            EmailNotification().send_email_default(
                lista_destinatarios, email_template.subject, html_content
            )
            log.info(f"E-mail enviado com sucesso: {tele}")
        else:
            log.error(f"Não possui e-mail cadastrado: {tele}")

        message = f"E-mail enviado com sucesso: {tele}"

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar enviar o email!" % (err)

    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def envia_email_aprovador_teletrabalho(
    task, hook, teles_pk, aprovador_pk, nm_template, user
):
    """
    Está Task é responsável por realizar os envios de emails para os aprovadores sobre os servidores pendentes de envio do teletrabalho

    Args:
    :teles_pk: (list) ID da MovimentacaoTeletrabalho.
    :aprovador_pk: (str) ID do aprovador do teletrabalho.
    :nm_template: (str) Nome do template do e-mail.
    :user: (str) ID do usuário logado.

    """
    state = "failed"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()

        aprovador = Servidor.objects.get(pk=aprovador_pk)
        txt_servidores = ""
        lista_destinatarios = ""
        if aprovador.pessoa_fisica.email:
            for tele_pk in teles_pk:
                tele = MovimentacaoTeletrabalho.objects.get(pk=tele_pk)

                if txt_servidores == "":
                    txt_servidores = f'{tele.servidor.matricula} - {tele.servidor.pessoa_fisica.nome} - {tele.servidor.job_position().cargo.nome if tele.servidor.job_position() else ""}, Teletrabalho: {tele.data_inicio} - {tele.data_fim}<br />'
                else:
                    txt_servidores = f'{txt_servidores}{tele.servidor.matricula} - {tele.servidor.pessoa_fisica.nome} - {tele.servidor.job_position().cargo.nome if tele.servidor.job_position() else ""}, Teletrabalho: {tele.data_inicio} - {tele.data_fim}<br />'

            lista_destinatarios = get_emails_destinatarios(
                aprovador.pessoa_fisica.email
            )
            email_template = EmailTemplate.objects.get(code=nm_template)

            conteudo = email_template.contents.replace(
                "%nome%", f"{aprovador.pessoa_fisica.nome}"
            ).replace("%conteudo%", f"{txt_servidores}")
            html_content = render_to_string(
                "util/template_email.html", {"message": conteudo}
            )
            EmailNotification().send_email_default(
                lista_destinatarios, email_template.subject, html_content
            )
            log.info(f"E-mail enviado com sucesso: {aprovador} -> {txt_servidores}")
        else:
            log.error(f"Não possui e-mail cadastrado: {aprovador} -> {txt_servidores}")

        message = f"E-mail enviado com sucesso: {aprovador}"

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar enviar o email!" % (err)

    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def send_mail_gestor_folha_ponto(
    task,
    mes_competencia=None,
    ano_competencia=None,
    servidor_id=None,
    user=None,
    inc_progress=0,
):
    """
    Está Task é responsável por realizar os envios de emails para os servidores pendentes de envio do folha ponto
    Args:
    :mes_competencia: (str).
    :ano_competencia: (str).
    :servidor_id (str)
    :user: (str) ID do usuário logado.
    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()

        servidor = Servidor.objects.get(pk=servidor_id)
        status_excluidos = [
            STS_CANCELED_APPLICANT,
            STS_STAND_BY,
            STS_CANCELED_DGP,
            STS_REJECTED,
        ]
        ultimo_envio = (
            SendingTimeSheet.objects.filter(employee=servidor)
            .exclude(status__in=status_excluidos)
            .last()
        )

        params_envio = {
            "mes_competencia": mes_competencia,
            "ano_competencia": ano_competencia,
            "servidor": servidor,
            "ultimo_envio": ultimo_envio,
        }

        periodo_ano = int(ano_competencia) if ano_competencia else datetime.today().year
        periodo_mes = (
            int(mes_competencia) if mes_competencia else datetime.today().month
        )

        with transaction.atomic():
            enviar_email_gestor_folha_ponto(params_envio)
            if servidor.pessoa_fisica.email_institucional:
                FolhaPontoHistoricoNotificacoes.objects.create(
                    servidor=servidor,
                    referencia_ano=periodo_ano,
                    referencia_mes=periodo_mes,
                )
                message = f"E-mail enviado com sucesso. {servidor.__str__()}"
            else:
                message = f"E-mail não encontrado para: {servidor.__str__()}"
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar enviar o email!" % (err)

    task.message = message
    task.info(message)
    task.finish_execution(status=state)
    task.state = state
    Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def send_mail_gestor_folha_ponto_aprovador(
    task,
    mes_competencia=None,
    ano_competencia=None,
    aprovador_id=None,
    conteudo=[],
    user=None,
    inc_progress=0,
):
    """
    Está Task é responsável por realizar os envios de emails para os servidores pendentes de envio do folha ponto
    Args:
    :mes_competencia: (str).
    :ano_competencia: (str).
    :aprovador_id (int)
    :conteudo (list)
    :user: (str) ID do usuário logado.
    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()

        servidor = Servidor.objects.get(pk=aprovador_id)

        params_envio = {
            "mes_competencia": mes_competencia,
            "ano_competencia": ano_competencia,
            "aprovador": servidor,
            "conteudo": conteudo,
        }

        enviar_email_gestor_folha_ponto_aprovador(params_envio)
        if servidor.pessoa_fisica.email_institucional:
            message = f"E-mail enviado com sucesso.{servidor.__str__()}"
        else:
            message = f"E-mail não encontrado para: {servidor.__str__()}"
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar enviar o email!" % (err)

    task.message = message
    task.info(message)
    task.finish_execution(status=state)
    task.state = state
    Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def start_send_mail_gestor_folha_ponto(
    task,
    hook,
    mes_competencia=None,
    ano_competencia=None,
    status=None,
    posses=None,
    notificado=None,
    user=None,
):
    task = Task.objects.get(uuid=task)
    task.message = "<p>Enviando Email em Massa...</p>"
    task.state = "progress"
    task.save()

    params = {
        "mes_competencia": mes_competencia,
        "ano_competencia": ano_competencia,
        "status": status,
        "posses": posses,
        "notificado": notificado,
        "filtro_email": True,
    }

    query_servidores = filtro_gestor_folha_ponto(params)

    total = query_servidores.count()
    inc_progress = 100.0 / total if total else 0
    result = None

    jobs = []
    dict_aprovadores = {}
    for servidor in query_servidores:
        agrupar_aprovador_folha_ponto(servidor, dict_aprovadores)
        jobs.append(
            send_mail_gestor_folha_ponto.s(
                task.uuid,
                mes_competencia=mes_competencia,
                ano_competencia=ano_competencia,
                user=user,
                servidor_id=servidor.pk,
                inc_progress=inc_progress,
            )
        )

    for aprovador in dict_aprovadores:
        jobs.append(
            send_mail_gestor_folha_ponto_aprovador.s(
                task.uuid,
                mes_competencia=mes_competencia,
                ano_competencia=ano_competencia,
                user=user,
                aprovador_id=aprovador,
                conteudo=dict_aprovadores[aprovador],
                inc_progress=inc_progress,
            )
        )

    job = group(jobs)

    result = job.apply_async()

    while not result.ready():
        time.sleep(2)

    task.info(pct_progress=100)
    task.finish_execution()


@app.task()
def efetivar_indeferir_solicitacao_venda_plantao(
    task, solicitacao_id=None, user=None, inc_progress=0
):
    """
    Task é responsável por realizar a efetivação da venda de plantões
    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None

    try:
        set_current_user(user)

        task.message = "<p>Enviando Email...</p>"
        task.state = "progress"
        task.save()

        solicitacao = PortalRequest.objects.get(pk=solicitacao_id)

        if solicitacao.employee.ativo:
            infos = {
                "acao_efetivar": REQUEST_ACT_EFETIVACAO_AUTOMATICO,
                "usuario_job": User.objects.get(
                    username="job_efetivar_solicitacoes_automatico"
                ),
            }
            solicitacao.defered(infos)
            message = f">>>>>>>>>>>>>> Solicitação Nº {solicitacao.pk} Efetivada Automaticamente. >>>>>>>>>>>>>>>>>>"
        else:
            infos = {
                "acao_indeferir": REQUEST_ACT_INDEFERIMENTO_AUTOMATICO,
                "usuario_job": User.objects.get(
                    username="job_efetivar_solicitacoes_automatico"
                ),
            }
            solicitacao.denyed(infos)
            message = f">>>>>>>>>>>>>> Solicitação Nº {solicitacao.pk} Indeferida Automaticamente. >>>>>>>>>>>>>>>>>>"

        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar efetivar a solicitação!" % (err)

    task.message = message
    task.info(message)
    task.finish_execution(status=state)
    task.state = state
    Task.objects.filter(uuid=task).update(progress=F("progress") + inc_progress)
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def efetivar_indeferir_venda_plantoes(task, hook, user):
    """
    Task responsável por realizar a efetivação da venda de plantões

    """

    task = Task.objects.get(uuid=task)
    task.message = "<p>Efetivando solicitações de venda de plantões</p>"
    task.state = "progress"
    task.save()

    query_solicitacoes = PortalRequest.objects.filter(
        status=STS_EFETIVACAO_AUTOMATICA,
        portal_request_type__in=[
            PORTAL_FORENSIC_RECESS_TYPE,
            PORTAL_SERVER_SHIFT_TYPE,
            PORTAL_COMP_CLEARANCE_MEMBERS_TYPE,
            PORTAL_COMP_VACATION_MEMBERS_TYPE,
        ],
    )

    total = query_solicitacoes.count()
    inc_progress = 100.0 / total if total else 0
    result = None

    jobs = []
    for solicitacao in query_solicitacoes:
        jobs.append(
            efetivar_indeferir_solicitacao_venda_plantao.s(
                task.uuid,
                solicitacao_id=solicitacao.pk,
                user=user,
                inc_progress=inc_progress,
            )
        )

    job = group(jobs)

    result = job.apply_async()

    while not result.ready():
        time.sleep(2)

    task.info(pct_progress=100)
    task.finish_execution()
