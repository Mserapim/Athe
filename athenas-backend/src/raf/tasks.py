# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime
from decimal import Decimal

from celery import Celery, group
from common.saci.models import Step
from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.template.defaultfilters import slugify
from engine.mq.models import Task
from judicial.models import LegalClassification, PartLawsuit
from raf.models import (
    Activity,
    ActivityAdjustment,
    AutoReference,
    DataEExt,
    DataEProc,
    FunctionalActivityReport,
    HistoricRAF,
    Item,
    Quiz,
    SubItem,
    TaxonomyClassification,
    WorkerLocation,
)
from rh.models import Lotacao, MovimentacaoPosse, Servidor
from zeep.client import Client
from zeep.transports import Transport


log = getLogger("tasker")
app = Celery("celeryraf")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
# django.setup()


@app.task()
def recalculate_balance_raf(task, hook, month, year, employee, user):
    # state = 'failed'
    message = "<p>Erro ao processar o RAF</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        # initial_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        set_current_user(user)
        servidor = None
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            message = (
                "<p>Recalculando SALDOS...<br /<ul><li>%s</li><li>%s</li></ul></p>"
                % (
                    ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                    ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                )
            )
        else:
            message = "<p>Recalculando SALDOS...<br /<ul><li>%s</li></ul></p>" % (
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>")
            )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        list_of_employees = Servidor.objects.filter(tipo="M", ativo=True)
        if employee:
            list_of_employees = list_of_employees.filter(pk=employee)
        inc_progress = 100.0 / list_of_employees.count()
        rst = False
        fail = False
        result = None
        job = group(
            [
                recalculate_balance_by_employee.s(
                    membro.matricula,
                    month,
                    year,
                    task_father=task.uuid,
                    inc_progress=inc_progress,
                )
                for membro in list_of_employees
            ]
        )
        result = job.apply_async()
        while not (rst):
            rst = result.ready() if result else True
            time.sleep(1)
        fail = result.failed() if result else False
        if not (fail):
            # state = 'ready'
            # final_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            if employee:
                message = (
                    "<p>Processamento concluído com sucesso!<br /<ul><li>%s</li><li>%s</li></ul></p>"
                    % (
                        ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                        ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                    )
                )
            else:
                message = (
                    "<p>Processamento concluído com sucesso!<br /<ul><li>%s</li></ul></p>"
                    % (("RAF: <b>" + str(month) + "/" + str(year) + "</b>"))
                )
        else:
            # state = 'failed'
            message = "<p>Erro ao processar RAF</p>"
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao processar RAF</p>"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def recalculate_balance_by_employee(
    membro, month, year, task_father=None, inc_progress=0
):
    has_exception = None
    try:
        employee = Servidor.objects.filter(matricula=membro).first()
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Iniciado: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome)
            )
        set_current_user(User.objects.get(username="athenas"))
        raf = FunctionalActivityReport.objects.filter(
            employee__matricula=membro, month=month, year=year
        ).first()
        if raf:
            create_raf_worker_on_call(raf=raf)
            calculate_balances(raf)
            # workerlocations = WorkerLocation.objects.filter(raf=raf)
            # for workerlocation in workerlocations:
            #     process_previous_balance(workerlocation=workerlocation)
            #     process_current_balance(workerlocation=workerlocation)

        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Terminado: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome),
                pct_progress=Decimal(inc_progress),
            )
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Erro: MP%s - %s<br/>%s"
                % (str(membro), employee.pessoa_fisica.nome, err),
                pct_progress=Decimal(inc_progress),
            )
    if has_exception:
        raise has_exception


@app.task()
def drop_eproc2atheans(task, hook, month, year, employee, instance, processed, user):
    # state = 'failed'
    message = "<p>Erro ao remover documentos do e-Proc</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        # initial_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        set_current_user(user)
        servidor = None
        msg = "Iniciando..."
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            message = (
                "<p>Removendo documentos do e-Proc...<br /<ul><li>%s</li><li>%s</li></ul></p>"
                % (
                    ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                    ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                )
            )
        else:
            message = (
                "<p>Removendo documentos do e-Proc...<br /<ul><li>%s</li></ul></p>"
                % (("RAF: <b>" + str(month) + "/" + str(year) + "</b>"))
            )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg, pct_progress=0.001)
        if int(instance) == 0:
            inst = ["1", "2"]
        else:
            inst = [instance]
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            docs = DataEProc.objects.filter(
                mes_referencia=str(month),
                ano_referencia=year,
                instancia__in=inst,
                membro=str(servidor.matricula),
            )
        else:
            docs = DataEProc.objects.filter(
                mes_referencia=str(month), ano_referencia=year, instancia__in=inst
            )
        counted = docs.filter(analise=1)
        task.info(msg="Analisando documentos do e-Proc", pct_progress=2)
        if processed == "true" and counted:
            # ret = False
            msg = "Existem documentos do e-Proc já contados no RAF, remoção não realizada."
        else:
            task.info(msg="Removendo documentos do e-Proc", pct_progress=4)
            docs.delete()
            # ret = True
            msg = "Documentos do e-Proc removidos com sucesso"
        if employee:
            message = "<p>%s<br /<ul><li>%s</li><li>%s</li></ul></p>" % (
                msg,
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
            )
        else:
            message = "<p>%s<br /<ul><li>%s</li></ul></p>" % (
                msg,
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
            )
        task.info(msg, pct_progress=94)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao remover documento do e_-Proc</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def drop_eext2atheans(task, hook, month, year, employee, instance, processed, user):

    message = "<p>Erro ao remover documentos do e-Ext</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:

        set_current_user(user)
        servidor = None
        msg = "Iniciando..."
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            message = (
                "<p>Removendo documentos do e-Ext...<br /<ul><li>%s</li><li>%s</li></ul></p>"
                % (
                    ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                    ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                )
            )
        else:
            message = (
                "<p>Removendo documentos do e-Ext...<br /<ul><li>%s</li></ul></p>"
                % (("RAF: <b>" + str(month) + "/" + str(year) + "</b>"))
            )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg, pct_progress=0.001)

        if employee:
            servidor = Servidor.objects.get(pk=employee)
            docs = DataEExt.objects.filter(
                month=str(month),
                year=str(year),
                employee_registration=servidor.matricula,
            )
        else:
            docs = DataEExt.objects.filter(month=str(month), year=str(year))
        counted = docs.filter(analisys=1)
        task.info(msg="Analisando documentos do e-Ext", pct_progress=2)
        if processed == "true" and counted:
            # ret = False
            msg = (
                "Existem documentos do e-Ext já contados no RAF, remoção não realizada."
            )
        else:
            task.info(msg="Removendo documentos do e-Ext", pct_progress=4)
            docs.delete()
            # ret = True
            msg = "Documentos do e-Ext removidos com sucesso"
        if employee:
            message = "<p>%s<br /<ul><li>%s</li><li>%s</li></ul></p>" % (
                msg,
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
            )
        else:
            message = "<p>%s<br /<ul><li>%s</li></ul></p>" % (
                msg,
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
            )
        task.info(msg, pct_progress=94)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao remover documento do e_-Ext</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def drop_raf(task, hook, month, year, employee, activity, adjustment, user):
    # state = 'failed'
    message = "<p>Erro ao remover o RAF</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        # initial_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        set_current_user(user)
        servidor = None
        msg = "Iniciando..."
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            message = "<p>Removendo RAF...<br /<ul><li>%s</li><li>%s</li></ul></p>" % (
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
            )
        else:
            message = "<p>Removendo RAF...<br /<ul><li>%s</li></ul></p>" % (
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>")
            )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg, pct_progress=0.001)
        if employee:
            rafs = FunctionalActivityReport.objects.filter(
                month=month, year=year, employee=employee
            )
        else:
            rafs = FunctionalActivityReport.objects.filter(month=month, year=year)
        workerlocations = WorkerLocation.objects.filter(raf__in=rafs)
        acts = Activity.objects.filter(workerlocation__in=workerlocations)
        actadjs = ActivityAdjustment.objects.filter(activity__in=acts)
        ret = True
        if activity == "true":
            if acts:
                ret = False
                msg = "RAFs com atividades registradas, remoção não realizada."
        if activity == "false" and adjustment == "true":
            if actadjs:
                ret = False
                msg = "RAFs com solicitação de ajuste de atividades, remoção não realizada."
        if ret:
            msg = "Removendo solicitação de ajustes..."
            pct = 1
            task.info(msg=msg, pct_progress=pct)
            actadjs.delete()
            msg = "Removendo referências a documentos..."
            pct = 16
            task.info(msg=msg, pct_progress=pct)
            autos = AutoReference.objects.filter(activity__in=acts)
            autos.delete()
            msg = "Removendo atividades..."
            pct = 36

            rst = False
            fail = False
            result = None
            job = group(
                [
                    process_remove_activity.s(
                        worker.pk, user, task_father=task.uuid, inc_progress=55
                    )
                    for worker in workerlocations
                ]
            )
            result = job.apply_async()
            while not (rst):
                rst = result.ready() if result else True
                time.sleep(1)
            fail = result.failed() if result else False
            if not (fail):
                msg = "Atividades removidas."
            else:
                msg = "Erro ao remover atividades"

            task.info(msg=msg, pct_progress=pct)
            # acts.delete()
            if not (fail):
                msg = "Removendo lotações..."
                pct = 52
                task.info(msg=msg, pct_progress=pct)
                workerlocations.delete()
                msg = "Removendo rafs..."
                pct = 68
                task.info(msg=msg, pct_progress=pct)
                rafs.delete()
                msg = "Redefinindo análise de documentos processados..."
                pct = 84
                task.info(msg=msg, pct_progress=pct)
                if employee:
                    servidor = Servidor.objects.get(pk=employee)
                    docsEProc = DataEProc.objects.filter(
                        mes_referencia=str(month),
                        ano_referencia=str(year),
                        membro=str(servidor.matricula),
                    )
                    docsEExt = DataEExt.objects.filter(
                        month=month, year=year, employee=servidor
                    )
                else:
                    docsEProc = DataEProc.objects.filter(
                        mes_referencia=str(month), ano_referencia=str(year)
                    )
                    docsEExt = DataEExt.objects.filter(month=month, year=year)
                countedEProc = docsEProc.filter(analise=1)
                countedEExt = docsEExt.filter(analisys=1)
                countedEProc.update(analise=0)
                countedEExt.update(analisys=0)
                # state = 'ready'
                # final_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                pct = 100
                task.info(pct_progress=pct)
            if employee:
                message = (
                    "<p>Remoção concluída com sucesso!<br /<ul><li>%s</li><li>%s</li></ul></p>"
                    % (
                        ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                        ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                    )
                )
            else:
                message = (
                    "<p>Remoção concluída com sucesso!<br /<ul><li>%s</li></ul></p>"
                    % (("RAF: <b>" + str(month) + "/" + str(year) + "</b>"))
                )
            task.info(msg="", pct_progress=100)
            task.finish_execution(msg=message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        task.info(
            msg="Erro em %s<br />%s" % (message, err), type_of=3, pct_progress=pct
        )
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def import_eproc(task, hook, initialdate, finaldate, employee, instance, user, success):
    # state = 'failed'
    message = "<p>Erro ao importar dados do e-Proc</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        message = "<p>Importando dados do e-Proc...</p>"
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        WS_EPROC_URL_1 = getattr(settings, "WS_EPROC_PROD_URL_1", None)
        WS_EPROC_URL_2 = getattr(settings, "WS_EPROC_PROD_URL_2", None)
        date_initial = datetime.strptime(initialdate, "%Y-%m-%d").date()
        date_final = datetime.strptime(finaldate, "%Y-%m-%d").date()
        list_of_employees = (
            MovimentacaoPosse.objects.filter(servidor__tipo="M")
            .filter(
                Q(data_desligamento__isnull=True)
                | (
                    Q(data_desligamento__gte=date_initial)
                    & Q(data_desligamento__lte=date_final)
                )
            )
            .order_by("servidor__pessoa_fisica__nome")
            .distinct("servidor__pessoa_fisica__nome")
        )
        if employee:
            list_of_employees = list_of_employees.filter(servidor=employee)
        inc_progress = 0
        if instance == 0:
            inc_progress = 100.0 / (list_of_employees.count() * 2)
        else:
            inc_progress = 100.0 / list_of_employees.count()
        rst1 = False
        fail1 = False
        result1 = None
        if instance == 0 or instance == 1:
            job1 = group(
                [
                    importing_by_employee.s(
                        initialdate,
                        finaldate,
                        membro.servidor.matricula,
                        WS_EPROC_URL_1,
                        1,
                        task_father=task.uuid,
                        inc_progress=inc_progress,
                    )
                    for membro in list_of_employees
                ]
            )
            result1 = job1.apply_async()
        rst2 = False
        fail2 = False
        result2 = None
        if instance == 0 or instance == 2:
            job2 = group(
                [
                    importing_by_employee.s(
                        initialdate,
                        finaldate,
                        membro.servidor.matricula,
                        WS_EPROC_URL_2,
                        2,
                        task_father=task.uuid,
                        inc_progress=inc_progress,
                    )
                    for membro in list_of_employees
                ]
            )
            result2 = job2.apply_async()
        while not (rst1 and rst2):
            rst1 = result1.ready() if result1 else True
            rst2 = result2.ready() if result2 else True
            time.sleep(0.5)
        fail1 = result1.failed() if result1 else False
        fail2 = result2.failed() if result2 else False
        if not (fail1 and fail2):
            # state = 'ready'
            message = success
            task.finish_execution(msg=message)
        else:
            # state = 'failed'
            message = "<p>Erro ao importar dados do e-Proc</p>"
            task.finish_execution(msg=message, status="ERROR")

    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao importar dados do e-Proc</p>"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def importing_by_employee(
    initial_date,
    final_date,
    registration,
    url,
    instance,
    no_insert=None,
    task_father=None,
    inc_progress=0,
):
    try:
        employee = Servidor.objects.filter(matricula=registration).first()
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Iniciado: MP%s - %s para %sª instância"
                % (str(registration), employee.pessoa_fisica.nome, str(instance))
            )
        transport = Transport(timeout=600)
        transport.session.headers["User-Agent"] = getattr(
            settings, "WS_USER_AGENT", None
        )
        client = Client(url, transport=transport)
        user = getattr(settings, "WS_EPROC_USER", None)
        passwd = getattr(settings, "WS_EPROC_PASSWD", None)
        date_initial = datetime.strptime(initial_date, "%Y-%m-%d").date()
        date_final = datetime.strptime(final_date, "%Y-%m-%d").date()
        response = client.service.listarMovimentosMP(
            user, passwd, initial_date, final_date, "MP%s" % (registration)
        )
        if "listarMovimentosMPResposta" in response:
            list_of_movements = response.listarMovimentosMPResposta
            if len(list_of_movements) > 0:
                for moviment in list_of_movements:
                    data = DataEProc()
                    data.mes_referencia = str(int(moviment["dataMovimento"][3:5]))
                    data.ano_referencia = str(int(moviment["dataMovimento"][6:10]))
                    data.membro = str(registration)
                    data.instancia = str(instance)
                    data.promotoria = str(moviment["promotoria"])
                    data.promotoria_slugfy = slugify(str(moviment["promotoria"]))
                    data.processo = str(moviment["processo"])
                    data.codclasse = str(moviment["codClasse"])
                    data.codassuntoprincipal = str(moviment["codAssuntoPrincipal"])
                    data.codmovimento = str(moviment["codMovimento"])
                    data.datamovimento = str(moviment["dataMovimento"])
                    data.semintimacao = str(moviment["semIntimacao"])
                    data.orgao = str(moviment["orgao"])
                    data.analise = 0
                    data.dataintimacao = "None"
                    data.intimacao = "None"
                    data.dataabriuprazo = "None"
                    data.manifestacaoabertura = "None"
                    data.datafechouprazo = "None"
                    data.codmanifestacaofechamento = "None"
                    data.manifestacaofechamento = "None"
                    data.codmanifestacaodecurso = "None"
                    data.manifestacaodecurso = "None"
                    data.datamanifestacaodecurso = "None"
                    data.classe = "None"
                    data.assuntoprincipal = "None"
                    data.codassuntosecundario = "None"
                    data.assuntosecundario = "None"
                    if not no_insert:
                        data.save()
                prepare_returned(
                    registration, instance, date_initial.month, date_initial.year
                )
                prepare_entry(
                    registration, instance, date_initial.month, date_initial.year
                )
                proccess_eproc_none(
                    registration, instance, date_initial.month, date_initial.year
                )
        else:
            pass
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Terminado: MP%s - %s para %sª instância"
                % (str(registration), employee.pessoa_fisica.nome, str(instance)),
                pct_progress=inc_progress,
            )
    except Exception as err:
        task = Task.objects.get(uuid=task_father)
        task.info(
            "ERROR: MP%s - %s para %sª instância<br />%s"
            % (str(registration), employee.pessoa_fisica.nome, str(instance), err),
            pct_progress=inc_progress,
        )


@app.task()
def import_eext(task, hook, initialdate, finaldate, employee, instance, user, success):
    # state = 'failed'
    message = "<p>Erro ao importar dados do e-Ext</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        message = "<p>Importando dados do e-Ext...</p>"
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        date_initial = datetime.strptime(initialdate, "%Y-%m-%d").date()
        date_final = datetime.strptime(finaldate, "%Y-%m-%d").date()
        list_of_employees = (
            MovimentacaoPosse.objects.filter(servidor__tipo="M")
            .filter(
                Q(data_desligamento__isnull=True)
                | (
                    Q(data_desligamento__gte=date_initial)
                    & Q(data_desligamento__lte=date_final)
                )
            )
            .order_by("servidor__pessoa_fisica__nome")
            .distinct("servidor__pessoa_fisica__nome")
        )
        if employee:
            list_of_employees = list_of_employees.filter(servidor=employee)
        inc_progress = 100.0 / list_of_employees.count()
        rst1 = False
        fail1 = False
        result1 = None
        job1 = group(
            [
                importing_by_employee_eext.s(
                    initialdate,
                    finaldate,
                    membro.servidor.matricula,
                    task_father=task.uuid,
                    inc_progress=inc_progress,
                )
                for membro in list_of_employees
            ]
        )
        result1 = job1.apply_async()
        while not (rst1):
            rst1 = result1.ready() if result1 else True
            time.sleep(0.5)
        fail1 = result1.failed() if result1 else False
        if not (fail1):
            # state = 'ready'
            message = success
            task.finish_execution(msg=message)
        else:
            # state = 'failed'
            message = "<p>Erro ao importar dados do e-Ext</p>"
            task.finish_execution(msg=message, status="ERROR")

    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao importar dados do e-Ext</p>"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise has_exception


def prepare_returned(membro, instancia, month, year):
    query = Q(~Q(codmovimento__in=["920246", "920247", "920013", "920014", "920015"]))
    documentos = DataEProc.objects.filter(query).filter(
        datamovimento__icontains=str(month) + "/" + str(year),
        membro=str(membro),
        instancia=str(instancia),
    )
    for d in documentos:
        doc = DataEProc()
        doc.mes_referencia = d.mes_referencia
        doc.ano_referencia = d.ano_referencia
        doc.membro = d.membro
        doc.promotoria = d.promotoria
        doc.promotoria_slugfy = d.promotoria_slugfy
        doc.instancia = d.instancia
        doc.processo = d.processo
        doc.codclasse = d.codclasse
        doc.codassuntoprincipal = d.codassuntoprincipal
        doc.codmovimento = "920247"
        doc.datamovimento = d.datamovimento
        doc.orgao = d.orgao
        doc.semintimacao = "None"
        doc.analise = 0
        doc.dataintimacao = "None"
        doc.intimacao = "None"
        doc.dataabriuprazo = "None"
        doc.manifestacaoabertura = "None"
        doc.datafechouprazo = "None"
        doc.codmanifestacaofechamento = "None"
        doc.manifestacaofechamento = "None"
        doc.codmanifestacaodecurso = "None"
        doc.manifestacaodecurso = "None"
        doc.datamanifestacaodecurso = "None"
        doc.classe = "None"
        doc.assuntoprincipal = "None"
        doc.codassuntosecundario = "None"
        doc.assuntosecundario = "None"
        doc.save()


def prepare_entry(membro, instancia, month, year):
    documentos = DataEProc.objects.filter(
        codmovimento__in=["166", "180"],
        datamovimento__icontains=str(month) + "/" + str(year),
        membro=str(membro),
        instancia=str(instancia),
    )
    for d in documentos:
        doc = DataEProc()
        doc.mes_referencia = d.mes_referencia
        doc.ano_referencia = d.ano_referencia
        doc.membro = d.membro
        doc.promotoria = d.promotoria
        doc.promotoria_slugfy = d.promotoria_slugfy
        doc.instancia = d.instancia
        doc.processo = d.processo
        doc.codclasse = d.codclasse
        doc.codassuntoprincipal = d.codassuntoprincipal
        doc.codmovimento = "920246"
        doc.datamovimento = d.datamovimento
        doc.orgao = d.orgao
        doc.semintimacao = "None"
        doc.analise = 0
        doc.dataintimacao = "None"
        doc.intimacao = "None"
        doc.dataabriuprazo = "None"
        doc.manifestacaoabertura = "None"
        doc.datafechouprazo = "None"
        doc.codmanifestacaofechamento = "None"
        doc.manifestacaofechamento = "None"
        doc.codmanifestacaodecurso = "None"
        doc.manifestacaodecurso = "None"
        doc.datamanifestacaodecurso = "None"
        doc.classe = "None"
        doc.assuntoprincipal = "None"
        doc.codassuntosecundario = "None"
        doc.assuntosecundario = "None"
        doc.save()


def proccess_eproc_none(membro, instancia, month, year):
    documentos = DataEProc.objects.filter(
        datamovimento__icontains=str(month) + "/" + str(year),
        membro=str(membro),
        instancia=str(instancia),
        promotoria="None",
    )
    if documentos:
        for d in documentos:
            d.analise = 2
            d.save()
    else:
        documentos = DataEProc.objects.filter(
            datamovimento__icontains=str(month) + "/" + str(year),
            membro=str(membro),
            instancia=str(instancia),
            codclasse="None",
        )
        if documentos:
            for d in documentos:
                d.analise = 6
                d.save()
        else:
            documentos = DataEProc.objects.filter(
                datamovimento__icontains=str(month) + "/" + str(year),
                membro=str(membro),
                instancia=str(instancia),
                codassuntoprincipal="None",
            )
            if documentos:
                for d in documentos:
                    d.analise = 7
                    d.save()
            else:
                documentos = DataEProc.objects.filter(
                    datamovimento__icontains=str(month) + "/" + str(year),
                    membro=str(membro),
                    instancia=str(instancia),
                    codmovimento="None",
                )
                if documentos:
                    for d in documentos:
                        d.analise = 8
                        d.save()


def getClass(eext_value):
    legalclass = None
    # legalclass = LegalClass.objects.filter(eext_type_lawsuit=eext_value).first()
    return legalclass


@app.task()
def importing_by_employee_eext(
    initial_date,
    final_date,
    registration,
    no_insert=None,
    task_father=None,
    inc_progress=0,
):

    try:
        employee = Servidor.objects.filter(matricula=registration).first()
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Iniciado: MP%s - %s"
                % (employee.matricula, employee.pessoa_fisica.nome)
            )
        date_initial = datetime.strptime(initial_date, "%Y-%m-%d").date()
        date_final = datetime.strptime(final_date, "%Y-%m-%d").date()
        movements = DataEExt.extract_extrajudicial_movements(
            employee=employee, initial_date=date_initial, final_date=date_final
        )

        if not no_insert and movements:
            DataEExt.create_in_bulk(extract=movements)
            proccess_eext_none(employee, date_initial.month, date_initial.year)
        else:
            task.info(
                "MP%s - %s nada foi feito"
                % (employee.matricula, employee.pessoa_fisica.nome)
            )

        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Terminado: MP%s - %s"
                % (employee.matricula, employee.pessoa_fisica.nome),
                pct_progress=inc_progress,
            )
    except Exception as err:
        log.exception(str(err))
        task = Task.objects.get(uuid=task_father)
        task.info(
            "ERROR: MP%s - %s" % (employee.matricula, employee.pessoa_fisica.nome),
            pct_progress=inc_progress,
        )
        raise err


def proccess_eext_none(membro, month, year):
    docs = DataEExt.objects.filter(month=month, year=year, employee=membro)

    if docs.exists():
        docs.filter(location__isnull=True).update(analisys=2)
        docs.filter(legalclass__isnull=True).update(analisys=6)
        docs.filter(legalmatter__isnull=True).update(analisys=7)
        docs.filter(legalmovement__isnull=True).update(analisys=8)


@app.task()
def process_raf(task, hook, month, year, employee, user):
    # state = 'failed'
    message = "<p>Erro ao processar o RAF</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        # initial_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        set_current_user(user)
        servidor = None
        if employee:
            servidor = Servidor.objects.get(pk=employee)
            message = (
                "<p>Processando RAF...<br /<ul><li>%s</li><li>%s</li></ul></p>"
                % (
                    ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                    ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                )
            )
        else:
            message = "<p>Processando RAF...<br /<ul><li>%s</li></ul></p>" % (
                ("RAF: <b>" + str(month) + "/" + str(year) + "</b>")
            )
        task.message = message
        task.state = "ready"
        task.save()
        task.info(msg="Iniciando...", pct_progress=0.001)
        list_of_employees = Servidor.objects.filter(tipo="M", ativo=True)
        if employee:
            list_of_employees = list_of_employees.filter(pk=employee)
        inc_progress = 100.0 / list_of_employees.count()
        rst = False
        fail = False
        result = None
        job = group(
            [
                processing_by_employee.s(
                    membro.matricula,
                    month,
                    year,
                    task_father=task.uuid,
                    inc_progress=inc_progress,
                )
                for membro in list_of_employees
            ]
        )
        result = job.apply_async()
        while not (rst):
            rst = result.ready() if result else True
            time.sleep(0.5)
        fail = result.failed() if result else False
        if not (fail):
            # state = 'ready'
            # final_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            if employee:
                message = (
                    "<p>Processamento concluído com sucesso!<br /<ul><li>%s</li><li>%s</li></ul></p>"
                    % (
                        ("RAF: <b>" + str(month) + "/" + str(year) + "</b>"),
                        ("Membro: <b>" + servidor.pessoa_fisica.nome + "</b>"),
                    )
                )
            else:
                message = (
                    "<p>Processamento concluído com sucesso!<br /<ul><li>%s</li></ul></p>"
                    % (("RAF: <b>" + str(month) + "/" + str(year) + "</b>"))
                )
            task.finish_execution(msg=message)
        else:
            # state = 'failed'
            message = "<p>Erro ao processar RAF</p>"
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        # state = 'failed'
        message = "<p>Erro ao processar RAF</p>"
        task.finish_execution(msg=message, status="ERROR")
    if has_exception:
        raise has_exception


def check_departures(raf=None):
    if raf:
        month_reference = NewDateRange.from_month(month=raf.month, year=raf.year)
        month_reference_days = month_reference
        listAfast = []
        for a in raf.employee.departures(
            start_date=month_reference.first, end_date=month_reference.last
        ):
            afastRange = NewDateRange(a.data_inicio, a.data_fim)
            month_reference_days = month_reference_days - afastRange
            listAfast.append(a)
        if len(month_reference_days.to_list()) == 0:
            set_current_user(raf.employee.user)
            raf.departure = True
            raf.submitted_at = month_reference.last
            raf.submitted_by = raf.employee.user
            for a in listAfast:
                raf.departures.add(a)
            raf.save()
            historic = HistoricRAF()
            historic.raf = raf
            historic.action = 5
            historic.save()


@app.task()
def processing_by_employee(membro, month, year, task_father=None, inc_progress=0):
    has_exception = None
    try:
        employee = Servidor.objects.filter(matricula=membro).first()
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Iniciado: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome)
            )
        set_current_user(User.objects.get(username="athenas"))
        raf = FunctionalActivityReport.objects.filter(
            employee__matricula=membro, month=month, year=year
        ).first()
        if raf and raf.submitted_by is None:
            get_dataeproc(raf=raf)
            process_attendance(raf=raf)
            get_dataeext(raf=raf)
            # processa os saldos
            calculate_balances(raf)
            check_departures(raf=raf)
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Terminado: MP%s - %s" % (str(membro), employee.pessoa_fisica.nome),
                pct_progress=Decimal(inc_progress),
            )
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info(
                "Erro: MP%s - %s<br/>%s"
                % (str(membro), employee.pessoa_fisica.nome, err),
                pct_progress=Decimal(inc_progress),
            )
    if has_exception:
        raise has_exception


def calculate_balances(raf):
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for workerlocation in workerlocations:
        process_previous_balance(workerlocation=workerlocation)
        process_current_balance(workerlocation=workerlocation)


def create_raf_worker_on_call(raf):
    mes_referencia = str(raf.month) + "/" + str(raf.year)
    orgsEproc = (
        DataEProc.objects.exclude(analise__in=[1, 2])
        .filter(datamovimento__icontains=mes_referencia, membro=raf.employee.matricula)
        .distinct("promotoria_slugfy")
        .values("promotoria_slugfy")
        .order_by("promotoria_slugfy")
    )
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for orgEproc in orgsEproc:
        if orgEproc["promotoria_slugfy"] != "none":
            if (
                workerlocations.filter(
                    location__order_nome=orgEproc["promotoria_slugfy"]
                ).count()
                == 0
            ):
                location = Lotacao.objects.filter(
                    order_nome=orgEproc["promotoria_slugfy"]
                ).first()
                if location:
                    worklocation = WorkerLocation()
                    worklocation.raf = raf
                    worklocation.location = location
                    worklocation.save()


def create_path_legalclassification_for_doc(classification_code, taxonomy_type):
    spath = ""
    while classification_code is not None:
        classification = LegalClassification.objects.filter(
            cnmp_code=classification_code, taxonomy_type=taxonomy_type
        ).first()
        if classification is None:
            break
        spath = spath + str(classification.id)
        if classification.father is None:
            break
        classification_code = str(classification.father.cnmp_code)
        if classification_code is not None:
            spath = spath + ","
    retorno = spath.split(",")
    return retorno


def process_quiz_for_doc(raf, classification_code):
    quiz = None
    if classification_code != "None":
        list_classes = create_path_legalclassification_for_doc(
            classification_code=classification_code, taxonomy_type="legalclass"
        )
        for q in Quiz.objects.filter(yearbase=raf.yearbase):
            control = False
            exclude = False
            for e in q.exclude_classes.all():
                if str(e.id) in list_classes:
                    exclude = True
            for c in q.legalclasses.all():
                if str(c.id) in list_classes:
                    control = True
            if not exclude:
                if control:
                    quiz = q
                    break
    return quiz


def process_lines(quiz, class_code, matter_code):
    return_classification = None
    for i in Item.objects.filter(quiz=quiz, activated=True):
        control = False
        exclude = False
        taxonomy_type = (
            TaxonomyClassification.objects.filter(item=i)
            .distinct()
            .values("classification__taxonomy_type")
            .first()
        )
        if taxonomy_type:
            if taxonomy_type["classification__taxonomy_type"] == "legalclass":
                path_classification = create_path_legalclassification_for_doc(
                    classification_code=class_code, taxonomy_type="legalclass"
                )
            if taxonomy_type["classification__taxonomy_type"] == "legalmatter":
                path_classification = create_path_legalclassification_for_doc(
                    classification_code=matter_code, taxonomy_type="legalmatter"
                )
            if taxonomy_type["classification__taxonomy_type"] == "legalprocedure":
                path_classification = create_path_legalclassification_for_doc(
                    classification_code=class_code, taxonomy_type="legalprocedure"
                )
            for e in i.taxonomyclassification_set.all():
                if e.exclude_classification:
                    if str(e.exclude_classification.id) in path_classification:
                        exclude = True
            for c in i.taxonomyclassification_set.all():
                if c.classification:
                    if str(c.classification.id) in path_classification:
                        control = True
            if not exclude:
                if control:
                    return_classification = i
                    break
    return return_classification


def process_columns(quiz, classification_code):
    try:

        path_classification = create_path_legalclassification_for_doc(
            classification_code=classification_code, taxonomy_type="legalmoviment"
        )
        collect = {}

        for subitem in SubItem.objects.filter(quiz=quiz, activated=True):

            def check():
                for clas in subitem.taxonomyclassification_set.all():
                    for level, value in enumerate(path_classification):
                        if clas.exclude_classification:
                            if (
                                level == 0
                                and str(clas.exclude_classification.id) == value
                            ):
                                return
                        elif clas.classification:
                            if str(clas.classification.id) == value:
                                collect.update({subitem: level})
                                if level == 0:
                                    return

            check()

        return min(collect, key=collect.get, default=None)

    except Exception:
        return None


def save_activity(workerlocation, quiz, line, column, doc, date_reference):
    if column:
        activity = Activity.objects.filter(
            workerlocation=workerlocation, item=line, subitem=column
        ).first()
        if activity:
            activity.amount_athenas = (
                activity.amount_athenas if activity.amount_athenas is not None else 0
            ) + 1
            activity.amount_submitted = (
                activity.amount_submitted
                if activity.amount_submitted is not None
                else 0
            ) + 1
            activity.save(recalculate=False)
            save_autoreference(
                activity=activity, doc=doc, date_reference=date_reference
            )
        else:
            activity = Activity()
            activity.workerlocation = workerlocation
            activity.item = line
            activity.subitem = column
            activity.amount_athenas = 1
            activity.amount_submitted = 1
            activity.save(recalculate=False)
            save_autoreference(
                activity=activity, doc=doc, date_reference=date_reference
            )


def save_autoreference(activity, doc, date_reference):
    autoreference = AutoReference()
    autoreference.activity = activity
    autoreference.is_adjustment = False
    autoreference.removed = False
    if doc.__class__.__name__ == "DataEExt":
        autoreference.source = "E-EXT"
        autoreference.source_add = 2
        # autoreference.process_number = doc.proccess_number
        autoreference.process_number = doc.proccess_number.replace(".", "")
        autoreference.obj = ""
    if doc.__class__.__name__ == "DataEProc":
        autoreference.source = "E-PROC"
        autoreference.source_add = 1
        autoreference.process_number = int(
            doc.processo.replace(".", "").replace("-", "").replace("/", "")
        )
        autoreference.obj = ""
        # autoreference.obj = json.dumps(model_to_dict(doc))
    autoreference.date = datetime.strptime(date_reference, "%d/%m/%Y %H:%M:%S")
    autoreference.content_object = doc
    autoreference.save()


def process_previous_balance(workerlocation):
    if workerlocation.raf.previous_raf:
        if workerlocation.raf.yearbase == workerlocation.raf.previous_raf.yearbase:
            location = workerlocation.location
            # month = workerlocation.raf.previous_raf.month
            # year = workerlocation.raf.previous_raf.year
            for q in Quiz.objects.filter(yearbase=workerlocation.raf.yearbase):
                column = SubItem.objects.filter(quiz=q, title="SALDO ANTERIOR").first()
                if column is not None and column.be_calculated.count() > 0:
                    for lin in column.items.all():
                        sum_amount = 0
                        # autos = []
                        for col in column.be_calculated.all():
                            soma = 0
                            acts = Activity.objects.filter(
                                workerlocation__raf=workerlocation.raf.previous_raf,
                                workerlocation__location=location,
                                item=lin,
                                subitem=col.from_the_sum,
                            )
                            if acts.count() > 0:
                                for act in acts:
                                    soma = soma + (
                                        act.amount_submitted
                                        if col.affectation == 1
                                        else -1 * act.amount_submitted
                                    )
                            sum_amount = sum_amount + soma
                        activity = Activity.objects.filter(
                            workerlocation=workerlocation, item=lin, subitem=column
                        ).first()
                        if activity is None:
                            activity = Activity()
                        activity.workerlocation = workerlocation
                        activity.item = lin
                        activity.subitem = column
                        activity.amount_athenas = sum_amount
                        activity.amount_submitted = sum_amount
                        activity.save(recalculate=False)


def process_returned():
    pass


def process_current_balance(workerlocation):
    for q in Quiz.objects.filter(yearbase=workerlocation.raf.yearbase):
        column = SubItem.objects.filter(quiz=q, title="SALDO ATUAL").first()
        if column is not None and column.be_calculated.count() > 0:
            for lin in column.items.all():
                sum_amount = 0
                # autos = []
                for col in column.be_calculated.all():
                    act = Activity.objects.filter(
                        workerlocation=workerlocation,
                        item=lin,
                        subitem=col.from_the_sum,
                    ).first()
                    if act:
                        parcela = (
                            act.amount_submitted if act.amount_submitted else 0
                        ) * (-1 if col.affectation != 1 else 1)
                        sum_amount += parcela
                activity = Activity.objects.filter(
                    workerlocation=workerlocation, item=lin, subitem=column
                ).first()
                if activity is None:
                    activity = Activity()
                activity.workerlocation = workerlocation
                activity.item = lin
                activity.subitem = column
                activity.amount_athenas = sum_amount
                activity.amount_submitted = sum_amount
                activity.save(recalculate=False)


def process_initiation():
    pass


def process_finalized():
    pass


def process_in_progress(workerlocation):
    pass
    # for q in Quiz.objects.filter(yearbase=workerlocation.raf.yearbase):
    #     column = SubItem.objects.filter(quiz=q, title='EM ANDAMENTO').first()
    #     if column is not None and column.be_calculated.count() > 0:
    #         for lin in column.items.all():
    #             sum_amount = 0
    #             autos = []
    #             for col in column.be_calculated.all():
    #                 act = Activity.objects.filter(workerlocation=workerlocation, item=lin, subitem=col.from_the_sum).first()
    #                 if act:
    #                     parcela = (act.amount_submitted if act.amount_submitted else 0) * (-1 if col.affectation != 1 else 1)
    #                     sum_amount += parcela
    #             if sum_amount != 0:
    #                 activity = Activity.objects.filter(workerlocation=workerlocation, item=lin, subitem=column).first()
    #                 if activity is None:
    #                     activity = Activity()
    #                 activity.workerlocation = workerlocation
    #                 activity.item = lin
    #                 activity.subitem = column
    #                 activity.amount_athenas = sum_amount
    #                 activity.amount_submitted = sum_amount
    #                 activity.save(recalculate=False)


def save_attendance(activity, stepattendance):
    autoreference = AutoReference.objects.filter(
        activity=activity,
        process_number=stepattendance.attendance.protocol.codigo,
        date=stepattendance.created_at,
    ).first()
    if autoreference is None:
        autoreference = AutoReference()
        autoreference.activity = activity
        autoreference.is_adjustment = False
        autoreference.removed = False
        autoreference.source = "SIACMP"
        autoreference.source_add = 3
        autoreference.process_number = stepattendance.attendance.protocol.codigo
        autoreference.date = stepattendance.created_at
        autoreference.obj = ""
        # autoreference.obj = json.dumps(model_to_dict(stepattendance))
        autoreference.content_object = stepattendance
        autoreference.save()


def process_attendance(raf):
    month_reference = NewDateRange.from_month(month=raf.month, year=raf.year)
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for workerlocation in workerlocations:
        attendances = Step.objects.filter(
            employee=raf.employee,
            origin=workerlocation.location,
            created_at__range=[month_reference.first, month_reference.last],
        ).count()
        if attendances > 0:
            for q in Quiz.objects.filter(yearbase=workerlocation.raf.yearbase):
                line = Item.objects.filter(
                    quiz=q, title="ATENDIMENTO AO PÚBLICO"
                ).first()
                column = SubItem.objects.filter(quiz=q, title="TOTAL").first()
                if line and column:
                    activity = Activity.objects.filter(
                        workerlocation=workerlocation, item=line, subitem=column
                    ).first()
                    if activity is None:
                        activity = Activity()
                    activity.workerlocation = workerlocation
                    activity.item = line
                    activity.subitem = column
                    activity.amount_athenas = attendances
                    activity.amount_submitted = attendances
                    activity.save(recalculate=False)
                    for stepattendance in Step.objects.filter(
                        employee=workerlocation.raf.employee,
                        origin=workerlocation.location,
                        created_at__range=[month_reference.first, month_reference.last],
                    ):
                        save_attendance(
                            activity=activity, stepattendance=stepattendance
                        )


def create_raf_worker_on_call_eext(raf):
    orgsEExt = (
        DataEExt.objects.exclude(analisys__in=[1, 2])
        .filter(month=str(raf.month), year=str(raf.year), employee=raf.employee)
        .distinct("location_id")
        .values("location_id")
        .order_by("location_id")
    )
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for orgEExt in orgsEExt:
        if orgEExt["location_id"] != "none":
            if workerlocations.filter(location__pk=orgEExt["location_id"]).count() == 0:
                location = Lotacao.objects.filter(pk=orgEExt["location_id"]).first()
                if location:
                    worklocation = WorkerLocation()
                    worklocation.raf = raf
                    worklocation.location = location
                    worklocation.save()


def get_dataeext(raf):
    create_raf_worker_on_call_eext(raf=raf)
    documentos = DataEExt.objects.exclude(analisys__in=[1, 2, 6, 7, 8]).filter(
        month=str(raf.month), year=str(raf.year), employee=raf.employee
    )
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for workerlocation in workerlocations:
        documentos_worklocation = documentos.filter(location=workerlocation.location)
        for doc in documentos_worklocation:
            atuacao = False
            # recebido = False
            analisys = 0
            questionario = None
            linha = None
            coluna = None
            questionario = process_quiz_for_doc(
                raf=raf,
                classification_code=(
                    str(doc.legalclass.cnmp_code) if doc.legalclass else "None"
                ),
            )
            if questionario is not None:
                linha = process_lines(
                    quiz=questionario,
                    class_code=doc.legalclass.cnmp_code,
                    matter_code=doc.legalmatter.cnmp_code,
                )
                if linha is None:
                    linha = Item.objects.filter(
                        quiz=questionario, title="DEMAIS ASSUNTOS"
                    ).first()
                if linha is not None:
                    analisys = 0
                    coluna = process_columns(
                        quiz=questionario,
                        classification_code=(
                            doc.legalmovement.cnmp_code if doc.legalmovement else 0
                        ),
                    )
                    if coluna:
                        analisys = 0
                        # data = '%s/%s/%s %s:%s:%s' % (doc.date_movement.day, doc.date_movement.month, doc.date_movement.year, doc.date_movement.hour, doc.date_movement.minute, doc.date_movement.second)
                        # save_activity(workerlocation=workerlocation, quiz=questionario, line=linha, column=coluna, doc=doc, date_reference=data)
                        save_activity(
                            workerlocation=workerlocation,
                            quiz=questionario,
                            line=linha,
                            column=coluna,
                            doc=doc,
                            date_reference=doc.date_movement.strftime(
                                "%d/%m/%Y %H:%M:%S"
                            ),
                        )
                        atuacao = True
                    else:
                        analisys = 5
                else:
                    analisys = 4
            else:
                analisys = 3
            if atuacao is True:
                doc.analisys = 1
                doc.save()
            else:
                doc.analisys = analisys
                doc.save()
        # process_previous_balance(workerlocation=workerlocation)
        # process_current_balance(workerlocation=workerlocation)


def get_dataeproc(raf):
    month_year = str(raf.month) + "/" + str(raf.year)
    create_raf_worker_on_call(raf=raf)
    documentos = DataEProc.objects.exclude(analise__in=[1, 2, 6, 7, 8]).filter(
        datamovimento__icontains=month_year, membro=raf.employee.matricula
    )
    workerlocations = WorkerLocation.objects.filter(raf=raf)
    for workerlocation in workerlocations:
        documentos_worklocation = documentos.filter(
            promotoria_slugfy=workerlocation.location.order_nome
        )
        for doc in documentos_worklocation:
            atuacao = False
            # recebido = False
            analise = 0
            questionario = None
            linha = None
            coluna = None
            questionario = process_quiz_for_doc(
                raf=raf, classification_code=doc.codclasse
            )
            if questionario is not None:
                linha = process_lines(
                    quiz=questionario,
                    class_code=doc.codclasse,
                    matter_code=doc.codassuntoprincipal,
                )
                if linha is None:
                    linha = Item.objects.filter(
                        quiz=questionario, title="DEMAIS ASSUNTOS"
                    ).first()
                    if linha is None:
                        linha = Item.objects.filter(
                            quiz=questionario, title="DEMAIS CLASSES"
                        ).first()
                if linha is not None:
                    analise = 0
                    coluna = process_columns(
                        quiz=questionario, classification_code=doc.codmovimento
                    )
                    if coluna:
                        analise = 0
                        save_activity(
                            workerlocation=workerlocation,
                            quiz=questionario,
                            line=linha,
                            column=coluna,
                            doc=doc,
                            date_reference=doc.datamovimento,
                        )
                        atuacao = True
                    else:
                        analise = 5
                else:
                    analise = 4
            else:
                analise = 3
            if atuacao is True:
                doc.analise = 1
                doc.save()
            else:
                doc.analise = analise
                doc.save()
        # process_previous_balance(workerlocation=workerlocation)
        # process_current_balance(workerlocation=workerlocation)


@app.task()
def process_remove_activity(worker, user, task_father=None, inc_progress=0):
    has_exception = None
    try:
        set_current_user(user)
        activits = Activity.objects.filter(workerlocation=worker)

        if activits.exists():
            activits.delete()

    except Exception as err:
        log.exception(str(err))
        has_exception = err
        if task_father:
            task = Task.objects.get(uuid=task_father)
            task.info("erro ao remover atividades")
    if has_exception:
        raise has_exception
