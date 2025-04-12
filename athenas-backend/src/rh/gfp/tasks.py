# -*- coding: utf-8 -*-
import codecs
import os
import shutil
import time
from datetime import datetime
from app import settings  # , timedelta

from celery import Celery, group
from dateutil.relativedelta import relativedelta
from django.db.models import F

from contrib.daterange import NewDateRange
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import DateUtils, getLogger, make_zipfile
from default.websocket import RemoteEmmiter
from engine.mq.models import Task
from ged.models import Arquivo as FileGED
from rh.gfp.cedulac.import_cc import create_pdf_cedula_c, search_cpf_and_indentifier
from rh.gfp.const import ESPECIE_EVENTO_RRA
from rh.gfp.generators.consigfacil.protocol import EmployeesFile, EntriesFile

# from rh.gfp.loaders.correctionfactor_loader import LoaderCorrectionFraction
from rh.gfp.models import (
    RRA,
    BankingConvenant,
    ContraCheque as Paycheck,
    DadoBancarioServidorFolha,
    Evento,
    Folha,
    FolhaTipo,
    Periodo,
    RRAEmployee,
)
from rh.gfp.models import Folha as Payroll
from rh.gfp.models import FolhaModelo as ModelPayroll
from rh.gfp.models import Periodo as Period
from rh.models import MovimentacaoPosse as Possession, PessoaFisica, Servidor
from rh.models import Servidor as Employee
from django.template import loader
import pdfkit
from django.conf import settings
from ged.models import Arquivo
from rh.queryregistration.report import get_filename, create_gedfile
from rh.gfp.tools.import_payroll import import_payments, PAYROLL_TYPES
from standard.models import ClassCode
from PyPDF2 import PdfReader, PdfWriter
from rh.gfp.configuration.commitmentlrf import CommitmentLRF

from .signals.remuneration_base import generate_remunerations_by_employee
from rh.gfp.gerar_cnab import gerar_cnab_pensionistas, gerar_cnab_consignados
import pandas as pd

log = getLogger("gfp")
app = Celery("gfp")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)
# django.setup()


@app.task()
def process_evaluation_differences_payroll(
    task, hook, payroll_id, user, number_events=[]
):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    payroll = Payroll.objects.get(pk=payroll_id)
    message = "<p>Erro ao avaliar diferenças da folha %s</p>" % payroll
    task = Task.objects.get(uuid=task)

    # log.debug(('TASK %s' % task.uuid)

    try:
        set_current_user(user)
        feedback(
            "",
            0,
            message="<p>Verificação de diferenças - %s</p>" % payroll,
            state=state,
        )
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )
        # if not (payroll.is_processed or payroll.is_closed):
        #     raise payroll.OpenedPayroll()
        # Procurando por servidores que não entraram na folha
        # log.debug(('TASK %s - Criando contracheques...' % task.uuid)
        if payroll.tipo_folha.modelo:
            for e in payroll.tipo_folha.modelo.get_all_new_employees(payroll):
                paycheck, created = payroll.paychecks.get_or_create(
                    servidor=e, pensioner=None
                )
                # if created:
                #     log.debug(('EVALUTE - CREATING CC: %s' % paycheck)

        list_of_paychecks = (
            payroll.paychecks.all()
        )  # filter(lancamentos__evento__numero='05100')

        total_paychecks = list_of_paychecks.count()
        inc_progress = 100.0 / total_paychecks
        # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

        # rst = False
        # fail = False
        result = None
        job = group(
            [
                evaluate_paycheck.s(
                    task.uuid,
                    paycheck.pk,
                    user,
                    inc_progress=inc_progress,
                    total=total_paychecks,
                    number_events=number_events,
                )
                for paycheck in list_of_paychecks
            ]
        )

        # log.debug(('TASK %s - Iniciando job' % task.uuid)
        result = job.apply_async()
        # log.debug(('TASK %s - Job iniciado' % task.uuid)

        while not result.ready():
            time.sleep(2)

        # log.debug(('TASK %s - Iniciando job 2' % task.uuid)

        state = "ready"
        message = "<p>Verificação de diferenças - <b>%s</b> - concluída</p>" % payroll
        task.info(
            msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

        # log.debug(('TASK %s - Iniciando job 3' % task.uuid)

    except Exception as err:
        log.exception(err)
        state = "failed"
        message = "<p>Erro ao avaliar diferenças</p>"
        task.info(msg="Erro ao avaliar diferenças - %s" % err, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def process_evaluation_differences_periods(task, hook, periods, user, number_events=[]):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    state = "failed"
    # payroll = Payroll.objects.get(pk=perio)
    q_periods = Period.objects.filter(folhas__status__in=[3, 4])[0:periods]
    q_payrolls = Payroll.objects.filter(
        status__in=[3, 4], peiodo__in=[p.pk for p in q_periods]
    )

    if q_payrolls:
        message = (
            "<p>Erro ao avaliar diferenças das folhas!<br /><b>%s</b> a <b>%s</b></p>"
            % (q_periods[periods - 1], q_periods[0])
        )
    else:
        message = "<p>Não há folhas para avaliar!</p>"
    task = Task.objects.get(uuid=task)

    # log.debug(('TASK %s' % task.uuid)

    has_exception = None
    try:
        # Procurando por servidores que não entraram nas folhas e deveriam ter entrado
        # log.debug(('TASK %s - Criando contracheques...' % task.uuid)
        for period in q_periods:
            dr = NewDateRange.from_month(period.ano, min(period.mes, 12))
            for e in Employee.objects.all():
                if (
                    e.data_exercicio
                    and e.data_exercicio <= dr.last
                    and (e.data_desligamento is None or e.data_desligamento > dr.last)
                ):
                    for payroll in q_payrolls.filter(periodo=period):
                        paycheck, created = payroll.paychecks.get_or_create(
                            servidor=e, pensioner=None
                        )
                        # if created:
                        #     log.debug(('EVALUTE - CREATING CC: %s' % paycheck)

        set_current_user(user)
        message = "<p>Avaliando diferenças - <b>%s</b></p>" % payroll
        task.message = message
        task.state = "ready"
        task.save()
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )
        feedback("", 0.001)

        list_of_paychecks = Paycheck.objects.filter(folha__in=[f for f in q_payrolls])

        inc_progress = 100.0 / list_of_paychecks.count()
        # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

        rst = False
        fail = False
        result = None
        job = group(
            [
                evaluate_paycheck.s(
                    task.uuid, paycheck.pk, user, inc_progress=inc_progress
                )
                for paycheck in list_of_paychecks
            ]
        )
        # log.debug(('TASK %s - Iniciando job' % task.uuid)
        result = job.apply_async()
        # log.debug(('TASK %s - Job iniciado' % task.uuid)

        while not (rst):
            rst = result.ready() if result else True
            time.sleep(2)
        # log.debug(('TASK %s - Iniciando job 2' % task.uuid)

        fail = result.failed() if result else False
        if not (fail):
            state = "ready"
            message = "<p>Avaliação de diferenças concluída com sucesso - %s</p>" % (
                "<b>" + str(payroll) + "</b>"
            )
            feedback("", 100)
        else:
            state = "failed"
            message = "<p>Erro ao avaliar diferenças</p>"
            feedback("", 100)
    except Exception as err:
        log.exception(err)
        has_exception = err
        state = "failed"
        message = "<p>Erro ao avaliar diferenças</p>"

    task.info(
        msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
        type_of=1,
    )
    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def evaluate_paycheck(
    task_uuid, paycheck_id, user, number_events=[], inc_progress=0, total=0
):
    set_current_user(user)
    if task_uuid:
        task = Task.objects.get(uuid=task_uuid)
    paycheck = Paycheck.objects.get(pk=paycheck_id)

    try:
        diff = paycheck.evaluate_differences(number_events=number_events)

    except Exception as e:
        if task:
            task.info(
                msg="Erro ao avaliar diferença %s - %s" % (paycheck.servidor, e),
                type_of=3,
            )
    else:
        if diff["changed"] and task:
            task.info(
                msg="DIFERENÇA(S) ENCONTRADA para %s" % (paycheck.servidor), type_of=2
            )
            # log.debug('EVAL DIFF: %s: %s' % (paycheck.servidor.matricula, diff))

    finally:
        if not paycheck.lancamentos.exists():
            paycheck.delete()
        if task_uuid:
            Task.objects.filter(uuid=task_uuid).update(
                progress=F("progress") + inc_progress
            )


@app.task()
def process_recalculate_payroll(
    task, hook, payroll_id, user, model_id=None, possessions_group=None
):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    payroll = Payroll.objects.get(pk=payroll_id)
    model = (
        ModelPayroll.objects.get(pk=model_id) if model_id else payroll.tipo_folha.modelo
    )
    message = "<p>Erro ao recalcular folha %s</p>" % payroll
    task = Task.objects.get(uuid=task)
    # dr = NewDateRange.from_month(payroll.periodo.ano, min(payroll.periodo.mes, 12))

    # log.debug(('TASK %s' % task.uuid)

    set_current_user(user)
    feedback("", 0, message="<p>Recalculo da folha - %s</p>" % payroll, state=state)
    task.info(
        msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
        type_of=1,
    )

    # Procurando por servidores que não entraram na folha
    # log.debug(('TASK %s - Criando contracheques...' % task.uuid)
    query_employees = Servidor.objects.none()
    if model:
        query_employees = query_employees.union(model.get_all_new_employees(payroll))
    if payroll.tipo_folha.modelo:
        query_employees = query_employees.union(
            payroll.tipo_folha.modelo.get_all_new_employees(payroll)
        )

    for e in query_employees:
        paycheck, created = payroll.paychecks.get_or_create(servidor=e, pensioner=None)
        if created:
            task.info(msg=f"Contracheque criado - {paycheck}", type_of=2)

    try:

        list_of_paychecks = payroll.paychecks.all()

        if possessions_group:
            possessions_options = {
                "membros": ["MBR", "MBR2", "MEL", "MCM", "MEC", "MEL2", "MCM2", "MEC2"],
                "servidores": ["EFE", "ECM", "EFC"],
                "comissionados": [
                    "CMS",
                ],
                "aposentados": ["MAP", "SAP", "MAP2", "APO"],
                "pensionistas": [
                    "BFP",
                ],
                "adidos": ["RFC", "REQ", "EXT", "RCM"],
                "estagiarios": ["EST"],
                "residentes": ["RES"],
            }
            list_of_paychecks = list_of_paychecks.filter(
                servidor__type_by_possession__in=possessions_options[possessions_group]
            )

        total_paychecks = list_of_paychecks.count()
        try:
            inc_progress = 100.0 / total_paychecks
        except ZeroDivisionError:
            inc_progress = 1
        # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

        result = None
        job = group(
            [
                recalculate_paycheck.s(
                    task.uuid,
                    paycheck.pk,
                    user,
                    model_id=model_id,
                    inc_progress=inc_progress,
                    total=total_paychecks,
                )
                for paycheck in list_of_paychecks
            ]
        )

        log.debug("TASK %s - Iniciando job" % task.uuid)
        result = job.apply_async()
        log.debug("TASK %s - Job iniciado" % task.uuid)

        while not result.ready():
            time.sleep(2)

        log.debug("TASK %s - Iniciando job 2" % task.uuid)

        state = "ready"
        message = "<p>Recalculo da folha - <b>%s</b> - concluída</p>" % payroll

        log.debug("TASK %s - Iniciando job 3" % task.uuid)

    except Exception as err:
        log.exception(err)
        state = "failed"
        message = "<p>Erro ao recalcular folha</p>"
        task.info(msg="Erro ao recalcular folha - %s" % err, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def recalculate_paycheck(
    task_uuid, paycheck_id, user, model_id=None, inc_progress=0, total=0
):
    set_current_user(user)

    paycheck = Paycheck.objects.get(pk=paycheck_id)
    model = ModelPayroll.objects.get(pk=model_id) if model_id else None

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    try:
        paycheck.recalculate(model=model, task=task)
    except Exception as e:
        if task:
            task.info(
                msg="Erro %s ao recalcular contracheque do servidor %s"
                % (e, paycheck.servidor),
                type_of=3,
            )
    # if diff['changed'] and task:
    #     task.info(msg='CONTRACHEQUE MODIFICADO:  %s' % (paycheck.servidor), type_of=2)
    #     log.debug('EVAL DIFF: %s: %s' % (paycheck.servidor.matricula, diff))

    if not paycheck.lancamentos.exists():
        paycheck.delete()

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def process_consolidate_payroll(task, hook, payroll_id, user):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    payroll = Payroll.objects.get(pk=payroll_id)
    message = "<p>Erro ao consolidar folha %s</p>" % payroll
    task = Task.objects.get(uuid=task)

    set_current_user(user)
    feedback("", 0, message="<p>Consolidando folha - %s</p>" % payroll, state=state)
    task.info(
        msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
        type_of=1,
    )

    list_of_paychecks = payroll.paychecks.all()

    total_paychecks = list_of_paychecks.count()
    inc_progress = 100.0 / total_paychecks
    # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

    result = None
    job = group(
        [
            consolidate_paycheck.s(
                task.uuid,
                paycheck.pk,
                user,
                inc_progress=inc_progress,
                total=total_paychecks,
            )
            for paycheck in list_of_paychecks
        ]
    )

    # log.debug(('TASK %s - Iniciando job' % task.uuid)
    result = job.apply_async()
    # log.debug(('TASK %s - Job iniciado' % task.uuid)

    while not result.ready():

        time.sleep(2)

    # log.debug(('TASK %s - Iniciando job 2' % task.uuid)

    state = "ready"
    message = "<p>Consolidação da folha - <b>%s</b> - concluída</p>" % payroll

    # log.debug(('TASK %s - Iniciando job 3' % task.uuid)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def consolidate_paycheck(task_uuid, paycheck_id, user, inc_progress=0, total=0):
    set_current_user(user)

    paycheck = Paycheck.objects.get(pk=paycheck_id)

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    try:
        diff = paycheck.consolidate(changes=Paycheck.ALL, save=True)
    except Exception as e:
        diff = {}
        task.info(
            msg="ERRO ao consolidar CONTRACHEQUE %s: %s" % (paycheck.servidor, e),
            type_of=3,
        )

    if diff and task:
        task.info(msg="CONTRACHEQUE CONSOLIDADO:  %s" % (paycheck.servidor), type_of=2)
        # log.debug(('CONSOLIDATE DIFF: %s: %s' % (paycheck.servidor.matricula, diff))

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def process_processing_payroll(task, hook, payroll_id, user):

    set_current_user(user)
    task = Task.objects.get(uuid=task)

    state = "progress"
    payroll = Payroll.objects.get(pk=payroll_id)
    message = "<p>Erro ao processar folha %s</p>" % payroll

    # log.debug(('TASK %s' % task.uuid)
    payroll.process_payroll(simulate=False, task=task)

    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def process_load_file(
    task, hook, loader, payroll, path, user, create=False, event=None
):

    set_current_user(user)
    task = Task.objects.get(uuid=task)
    payroll = Payroll.objects.get(pk=payroll)
    classcode = ClassCode.objects.get(pk=loader)
    if event:
        event = Evento.objects.get(pk=event)
    message = f"<p>Carregando arquivo tipo {classcode.name_object} para {payroll}</p>"
    task.message = message
    task.state = "progress"
    task.save()

    msg, status = f"Arquivo carregado com sucesso na folha {payroll}", "SUCCESS"
    Loader = classcode.cls(path, payroll, create=create, evento=event)
    Loader.execute(task=task)

    task.info(pct_progress=100)
    task.finish_execution(msg=msg, status=status)


@app.task()
def process_copy_payroll(
    task,
    hook,
    payroll_source_id,
    payroll_target_id,
    user,
    type_of_copy="CHANGED",
    registrations=[],
):

    def feedback(progress_message, progress, **kwargs):
        # log.debug((kwargs)
        task.progress_message = progress_message % kwargs
        task.progress = progress
        if "message" in kwargs:
            task.message = kwargs["message"]
        if "state" in kwargs:
            task.state = kwargs["state"]
        task.save()

    state = "progress"
    # log.debug(('TASK PAYROLL %s' % payroll_source_id)
    payroll = Payroll.objects.get(pk=payroll_source_id)
    new_payroll = Payroll.objects.get(pk=payroll_target_id)
    message = "<p>Erro ao copiar folha %s</p>" % payroll
    task = Task.objects.get(uuid=task)

    # log.debug(('TASK %s' % task.uuid)

    if new_payroll.pk == payroll.pk:
        task.info("ERRO ao copiar FOLHA: folha de origem e destinos iguais!", 3)
        state = "failed"
        # task.finish_execution('ERROR')

        # raise Folha.CopyAbortedFromAndToEqual()
    else:
        # lock_file = Locker.create_lock('copy_payroll')
        set_current_user(user)
        feedback(
            "",
            0,
            message="<p>Copia da folha %s > %s</p>" % (payroll, new_payroll),
            state=state,
        )
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )

        if type_of_copy == "DELETE":
            task.info("LIMPANDO FOLHA existente: %s!" % new_payroll)
            new_payroll._clear()

        new_payroll.dt_criacao = datetime.now()
        new_payroll.dt_pagamento = payroll.dt_pagamento + relativedelta(months=1)
        new_payroll.folha_anterior = payroll
        new_payroll.save()

        try:

            list_of_paychecks = payroll.paychecks.order_by("pensioner", "servidor")
            # type_of_payroll = payroll.tipo_folha.modelo.para_indicativo if payroll.tipo_folha.modelo else 'I'
            if not list_of_paychecks:
                # log.debug(('A folha %s não possui contracheques a serem copiados!')
                task.info(
                    "A folha %s não possui contracheques para serem copiados!" % payroll
                )
            else:
                # log.debug(('COPIANDO FOLHA: %s >> %s' % (payroll, new_payroll))

                total_paychecks = list_of_paychecks.count()
                inc_progress = 100.0 / total_paychecks
                # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

                result = None
                job = group(
                    [
                        copy_paycheck.s(
                            task.uuid,
                            paycheck.pk,
                            new_payroll.pk,
                            user,
                            type_of_copy=type_of_copy,
                            inc_progress=inc_progress,
                            total=total_paychecks,
                        )
                        for paycheck in list_of_paychecks
                    ]
                )

                # log.debug(('TASK %s - Iniciando job' % task.uuid)
                result = job.apply_async()
                # log.debug(('TASK %s - Job iniciado' % task.uuid)

                while not result.ready():
                    time.sleep(2)

                # log.debug(('TASK %s - Iniciando job 2' % task.uuid)

                # new_payroll.summarize(task=task)

                state = "ready"
                message = "<p>Cópia da folha - <b>%s > %s</b> - concluída</p>" % (
                    payroll,
                    new_payroll,
                )

                # log.debug(('TASK %s - Iniciando job 3' % task.uuid)

        except Exception as err:
            log.exception(err)
            state = "failed"
            message = "<p>Erro ao copiar folha</p>"
            task.info(msg="Erro ao copiar folha - %s" % err, type_of=3)

    feedback("", 100)
    task.message = message
    task.finish_execution(status=state)
    task.state = state
    task.save()


@app.task()
def copy_paycheck(
    task_uuid,
    paycheck_id,
    payroll_target_id,
    user,
    type_of_copy="CHANGED",
    inc_progress=0,
    total=0,
):
    set_current_user(user)

    paycheck = Paycheck.objects.get(pk=paycheck_id)

    payroll = paycheck.folha
    new_payroll = Payroll.objects.get(pk=payroll_target_id)

    task = Task.objects.get(uuid=task_uuid) if task_uuid else None

    paycheck_to, created = Paycheck.objects.get_or_create(
        folha=new_payroll,
        servidor=paycheck.servidor,
        pensioner=paycheck.pensioner,
        defaults={
            "situacao_funcional": paycheck.situacao_funcional,
            "situacao_previdenciaria": paycheck.situacao_previdenciaria,
            "cargo_efetivo": paycheck.cargo_efetivo,
            "referencia_efetivo_cache": paycheck.referencia_efetivo_cache,
            "cargo_comissao": paycheck.cargo_comissao,
            "referencia_comissao_cache": paycheck.referencia_comissao_cache,
            "cargo_eletivo": paycheck.cargo_eletivo,
            "referencia_eletivo_cache": paycheck.referencia_eletivo_cache,
            "data_admissao": paycheck.data_admissao,
            "lotacao": paycheck.lotacao,
            "dependentes_ir": paycheck.dependentes_ir,
            "dependentes_sf": paycheck.dependentes_sf,
            "margem_consignada_total": paycheck.margem_consignada_total,
            "margem_consignada_livre": paycheck.margem_consignada_livre,
            "base_previdenciaria": paycheck.base_previdenciaria,
            "base_ir": paycheck.base_ir,
            "dado_bancario_pessoa": paycheck.dado_bancario_pessoa,
            "total_bruto": paycheck.total_bruto,
            "total_liquido": paycheck.total_liquido,
        },
    )
    # if created: log.info('ContraCheque criado - %s' % paycheck_to)
    # log.debug(('>>> CONTRACHEQUE CRIADO: %s' % paycheck)
    # task['pct'] += 1

    try:
        # Copia eventos sem recalcular.
        # log.debug(('>>> COPIANDO EVENTOS DO CONTRACHEQUE CRIADO: %s' % paycheck.servidor)
        payroll._do_copy_eventos_contracheque(
            paycheck, paycheck_to, type_of_copy=type_of_copy, task=task
        )
        # log.debug(('>>> COPIADO EVENTOS DO CONTRACHEQUE CRIADO: %s' % paycheck.servidor)

        # log.debug(('OK >> RECALCULANDO CONTRACHEQUE (%s): %s' % (
        #     ['%s/%s' % (fe.evento.numero, fe.valor) for fe in paycheck_to.lancamentos.all()], paycheck_to.servidor))
        if (
            not paycheck_to.pensioner
        ):  # Recalculating only for employeers, not for pensioners
            paycheck_to.recalculate(consolidate=Paycheck.ALL, task=task)

        # log.debug(('OK >> CONTRACHEQUE RECALCULADO: %s' % (paycheck_to.servidor))
        if not paycheck_to.lancamentos.exists():
            # NOTIFY Notificar ao usuário que está copiando que o contracheque foi apagado
            # log.info('APAGANDO contracheque por não ter lançamentos: %s' % paycheck_to.servidor)
            task.info(
                "CONTRACHEQUE APAGADO por não ter lançamentos: %s"
                % paycheck_to.servidor,
                2,
            )
            paycheck_to.delete()
        elif paycheck_to.total_liquido <= 0:
            task.info("CONTRACHEQUE ZERADO ou NEGATIVO: %s" % paycheck_to.servidor, 2)

    except Exception as e:
        log.exception(e)
        # log.info('ERRO Copiando contracheque: %s' % paycheck.servidor)
        task.info("ERRO ao copiar CONTRACHEQUE: %s\n%s" % (paycheck.servidor, e), 3)

    # if diff and task:
    #     task.info(msg='CONTRACHEQUE CONSOLIDADO:  %s' % (paycheck.servidor), type_of=2)
    #     # log.debug(('CONSOLIDATE DIFF: %s: %s' % (paycheck.servidor.matricula, diff))

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def management_remuneration_bases(task, hook, period_id, user):

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    state = "failed"

    task = Task.objects.get(uuid=task)

    # log.debug(('TASK %s' % task.uuid)

    period = Period.objects.get(pk=period_id)

    has_exception = None
    try:
        # Procurando por servidores que não entraram nas folhas e deveriam ter entrado
        # log.debug(('TASK %s - Gerenciando remuneration bases...' % task.uuid)

        set_current_user(user)
        message = "<p>Avaliando remuneration bases - <b>%s</b></p>" % period
        task.message = message
        task.state = "ready"
        task.save()
        task.info(
            msg="Iniciando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
            type_of=1,
        )
        feedback("", 0.001)

        possessions_list = (
            Possession.objects.assets_in(range=period.range)
            .distinct("servidor")
            .select_related("servidor")
        )

        inc_progress = 100.0 / possessions_list.count()
        # log.debug(('TASK %s - Increment: %0.1f' % (task.uuid, inc_progress))

        rst = False
        fail = False
        result = None
        job = group(
            [
                evaluate_remuneration_base_by_employee.s(
                    task.uuid,
                    possession.servidor.pk,
                    user,
                    period.pk,
                    inc_progress=inc_progress,
                )
                for possession in possessions_list
            ]
        )
        # log.debug(('TASK %s - Iniciando job' % task.uuid)
        result = job.apply_async(priority=100)
        # log.debug(('TASK %s - Job iniciado' % task.uuid)

        while not (rst):
            rst = result.ready() if result else True
            time.sleep(2)
        # log.debug(('TASK %s - Iniciando job 2' % task.uuid)

        fail = result.failed() if result else False
        if not (fail):
            state = "ready"
            message = (
                "<p>Avaliação de remuneration bases concluída com sucesso - %s</p>"
                % ("<b>" + str(period) + "</b>")
            )
            feedback("", 100)
        else:
            state = "failed"
            message = "<p>Erro ao avaliar remuneration bases</p>"
            feedback("", 100)
    except Exception as err:
        log.exception(err)
        has_exception = err
        state = "failed"
        message = "<p>Erro ao avaliar remuneration bases</p>"

    task.info(
        msg="Finalizando processamento - %s" % time.strftime("%d/%m/%Y %H:%M:%S"),
        type_of=1,
    )
    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def evaluate_remuneration_base_by_employee(
    task_uuid, employee_id, user, period_id, inc_progress=0, total=0
):
    set_current_user(user)

    period = Period.objects.get(pk=period_id)

    employee = Employee.objects.get(pk=employee_id)

    task = Task.objects.get(uuid=task_uuid)

    try:
        generate_remunerations_by_employee(employee, period)
    except Exception as e:
        task.info(
            msg="Erro ao gerar base remuneração para %s - %s! %s"
            % (employee, period, e),
            type_of=3,
        )
        log.exception(e)

    if task:
        Task.objects.filter(pk=task.pk).update(progress=F("progress") + inc_progress)


@app.task()
def import_payroll(task, hook, payroll_type, period, user):
    set_current_user(user)

    period = Period.objects.get(pk=period)

    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        task.message = f"<p>Importador da folha de pagamento {PAYROLL_TYPES.get(payroll_type)} do {period}.</p>"
        task.state = "progress"
        task.progress = 0
        task.save()

        import_payments(payroll_type, period, task=task)
        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"Erro em {err}", type_of=3)
        task.finish_execution(status="ERROR")

    if has_exception:
        raise has_exception


# @app.task
# def load_correction_file(task, hook, startyear, year, month, user, correctionfile, success):
#     state = 'failed'
#     message = "<p>Carregando arquivo de Fatores de Correção"
#     task = Task.objects.get(uuid=task)

#     def feedback(progress_message, progress, **kwargs):
#         task.progress_message = progress_message % kwargs
#         task.progress = progress
#         task.save()

#     has_exception = None
#     try:
#         set_current_user(user)
#         task.state = 'progress'
#         task.save()

#         LoaderCorrectionFraction(
#             startyear=startyear,
#             year=year,
#             month=month,
#             correctionfile=correctionfile).load_from_xls()

#         state = 'ready'
#         message = 'Processo de carregamento concluído.'
#     except Exception as err:
#         log.exception(err)
#         has_exception = err
#         message = '<p>Falha no carregamento do arquivo de fator de correções</p>'

#     task.message = message
#     task.state = state
#     task.save()


@app.task()
def commitment_report(
    task,
    hook,
    success,
    user,
    period=None,
    sheet=None,
    option=None,
    subtitle=None,
    filename=None,
    type=None,
    mimetype=None,
    identifier=None,
):
    """
    Está Task é responsável por renderizar um template html criar arquivo pdf para o
    relatório de empenhos

    Args:
    :period: Periodo da folha EX: 04/2021.
    :type_sheet: Tipo da folha

    """
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        options = {
            "--footer-right": "Página: [page]/[topage]",
            "--footer-font-size": "10",
            "--header-font-size": "10",
            "--footer-spacing": "12",
            "--margin-top": "10mm",
            "--margin-bottom": "25mm",
            "--margin-left": "15mm",
            "--margin-right": "15mm",
            "--footer-line": "",
        }
        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        html = loader.render_to_string(
            f"{type}_template.html",
            eval(f"CommitmentLRF().calc_{type}_report(period,sheet,option,subtitle)"),
        )
        output = pdfkit.from_string(html, output_path=file_path, options=options)
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {"file": file.absolute_path}
        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()


@app.task()
def import_payroll(task, hook, payroll_type, period, user):
    set_current_user(user)

    period = Period.objects.get(pk=period)

    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        task.message = f"<p>Importador da folha de pagamento {PAYROLL_TYPES.get(payroll_type)} do {period}.</p>"
        task.state = "progress"
        task.progress = 0
        task.save()

        import_payments(payroll_type, period, task=task)
        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"Erro em {err}", type_of=3)
        task.finish_execution(status="ERROR")

    if has_exception:
        raise has_exception


@app.task
def gerar_cnab_consignados_task(task, hook, user, periodo, data_pgto):
    set_current_user(user)
    task = Task.objects.get(uuid=task)

    task.message = (
        f"Arquivo CNAB de consignados - período: {periodo} - data pgto: {data_pgto}"
    )
    task.state = "progress"
    task.progress = 0
    task.save()
    set_current_user(user)

    periodo_mes = int(periodo.split("/")[0])
    periodo_ano = int(periodo.split("/")[1])

    data_pgto_ano = int(data_pgto.split("/")[2])
    data_pgto_mes = int(data_pgto.split("/")[1])
    data_pgto_dia = int(data_pgto.split("/")[0])

    arquivo_cnab = gerar_cnab_consignados(
        periodo_ano,
        periodo_mes,
        datetime(data_pgto_ano, data_pgto_mes, data_pgto_dia).date(),
    )

    task.add_file(arquivo_cnab)
    task.finish_execution(msg=task.message + " - FINALIZADO")


@app.task
def process_credit_file(
    task, hook, convenant, payroll, employees, filename, user, somente_pensionistas
):
    # SETTING USER FOR LOCAL

    # log.debug('GENERATE FILE PROCESS: %s: %s: %s' % (user, self.payroll.periodo, self.tmp_dir))
    set_current_user(user)
    task = Task.objects.get(uuid=task)
    task.state = "progress"
    task.progress = 0
    task.save()
    set_current_user(user)
    payroll = Payroll.objects.get(pk=payroll)

    if somente_pensionistas:
        file_cnab = gerar_cnab_pensionistas(payroll, employees)
        task.add_file(file_cnab)

        task.message = "Arquivo cnab pensionista %s %02d/%04d" % (
            payroll.tipo_folha,
            payroll.periodo.mes,
            payroll.periodo.ano,
        )
        task.save()
        task.finish_execution(msg=task.message + " - FINALIZADO")
    else:
        convenant = BankingConvenant.objects.get(pk=convenant)
        employees = Servidor.objects.filter(pk__in=employees)

        task.message = "Arquivo de crédito %s - %s %02d/%04d" % (
            convenant.bank,
            payroll.tipo_folha,
            payroll.periodo.mes,
            payroll.periodo.ano,
        )
        task.save()

        tmp_dir = os.path.join(settings.UPLOAD_STORE_DIR, "gfp", task.uuid)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        file_path = os.path.join(tmp_dir, filename)

        file_buffer = convenant.generator.cls(payroll, convenant, task, log, employees)
        try:
            with codecs.open(file_path, "w", "utf-8") as fd:
                fd.write(str(file_buffer))
        except Exception as e:
            log.debug("ERRO AO GERAR ARQUIVO")
            log.debug(str(e))
            task.finish_execution(status="ERROR", msg="Erro na geração do arquivo")
        else:
            gedfile = FileGED.from_filepath(
                file_path, get_current_user(), "application/txt", 1
            )
            task.add_file(gedfile)

            task.finish_execution(msg=task.message + " - FINALIZADO")

            shutil.rmtree(tmp_dir)

            convenant.counter += 1
            convenant.save()


@app.task
def process_payroll(task, hook, payroll, simulate, user):
    # SETTING USER FOR LOCAL
    set_current_user(user)
    payroll = Payroll.objects.get(pk=payroll)
    # simulate = self.request.POST.get('simulate', True)
    message = f"Processamento da folha {payroll}"
    task = Task.objects.get(uuid=task)
    task.message = message
    task.status = "progress"
    task.progress = 0.0
    task.save()
    # log.debug(('INIT PROCESS SUMMARING PAYROLL...')
    try:
        payroll.proccess_payroll(simulate=simulate, task=task)
        message = f"Folha {payroll} processada com sucesso"
        state = "SUCCESS"
    except Exception as e:
        log.exception(str(e))
        task.info(msg=str(e), type_of=3)
        message = f"Erro ao processar a folha {payroll}"
        state = "ERROR"
    task.finish_execution(msg=message, status=state)


def process_copy_credit_accounts(task, hook, user, from_tipo, to_tipo, vigencia):
    set_current_user(user)
    task = Task.objects.get(uuid=task)
    from_ = FolhaTipo.objects.get(pk=from_tipo)
    to_ = FolhaTipo.objects.get(pk=to_tipo)
    vigencia = DateUtils.str_to_date(vigencia)
    task.state, task.message = (
        "progress",
        f"Copiando contas de crédito de {from_tipo} para {to_tipo}",
    )
    task.progress = 0
    task.save()

    folha = to_.folhas.exclude(dt_pagamento__lt=vigencia).last()
    status = "success"
    if folha:
        try:
            query = PessoaFisica.objects.filter(
                servidor__entries__folha=folha
            ).distinct()
            if query.exists():
                total = query.count() if query.count() > 0 else 0.00000000001
                pos = 0
                count = [0, 0, 0]
                inc = 100.0 / total
                for pessoa in query.order_by("nome"):
                    pos += 1

                    dbsf = (
                        DadoBancarioServidorFolha.objects.filter(
                            tipo_folha=from_, dado_bancario_pessoa__pessoa=pessoa
                        )
                        .order_by("-data_vigencia")
                        .last()
                    )

                    c_dbsf = (
                        DadoBancarioServidorFolha.objects.filter(
                            tipo_folha=to_, dado_bancario_pessoa__pessoa=pessoa
                        )
                        .order_by("-data_vigencia")
                        .last()
                    )

                    if dbsf:
                        if (
                            c_dbsf is None
                            or c_dbsf.dado_bancario_pessoa != dbsf.dado_bancario_pessoa
                        ):
                            dbsf.pk = None
                            dbsf.tipo_folha = to_
                            dbsf.data_inicio_vigencia = vigencia
                            dbsf.save()

                            task.info(
                                msg=f"OK: Copia concluida para {pessoa.nome}", type_of=1
                            )
                            count[0] += 1
                        else:
                            task.info(
                                msg=f"INFO: Não foi necessário copia para {pessoa.nome}",
                                type_of=1,
                            )
                            count[2] += 1
                    else:
                        task.info(
                            msg=f"A pessoa {pessoa.nome} não tem dados bancarios para o tipo de folha {from_tipo}",
                            type_of=2,
                        )
                        count[1] += 1

                    task.increment_progress(inc)

                task.info(msg=f"Sucesso: {count[0]}", type_of=1)
                task.info(msg=f"Info: {count[2]}", type_of=1)
                task.info(msg=f"Falhou: {count[1]}", type_of=1)
        except Exception as e:
            log.exception(str(e))
            task.info(msg=f"Erro copiando contas de crédito", type_of=3)
            status = "ERROR"

    task.finish_execution(msg="Cópia finalizada!", status=status)


@app.task
def process_get_consigfacil(task, hook, tmp_dir, period, filename, user):
    def create_file(filepath, objs):
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        with codecs.open(filepath, "w", "utf-8") as fd:
            fd.writelines(objs)
            fd.write("\n")

    set_current_user(user)

    task = Task.objects.get(uuid=task)
    period = Periodo.objects.get(pk=period)
    task.message = f"Gerando arquivos ConsigFacil - {period.mes}/{period.ano}"
    task.progress = 0
    task.state = "progress"
    task.save()

    ref = "%02d%04d" % (period.mes, period.ano)

    try:
        lines = EmployeesFile(period, task)
        file_employee = os.path.join(tmp_dir, "SERVIDOR_%s.txt" % ref)
        create_file(file_employee, str(lines))
    except Exception as e:
        log.error(e)
        task.info(msg=f"Erro ao gerar {file_employee}: \n {str(e)}", type_of=3)

    try:
        lines = EntriesFile(period, task)
        file_entry = os.path.join(tmp_dir, "FOLHA_%s.txt" % ref)
        create_file(file_entry, str(lines))
    except Exception as e:
        log.error(e)
        task.info(msg=f"Erro ao gerar {file_entry}: \n {str(e)}", type_of=3)

    zipfile = make_zipfile(os.path.join(tmp_dir, "..", filename), tmp_dir, False)
    gedfile = FileGED.from_filepath(zipfile, get_current_user(), "application/zip", 1)
    task.add_file(gedfile)
    task.finish_execution()
    shutil.rmtree(tmp_dir)


@app.task()
def task_import_cedula_c(task, hook, success, user, path, reference) -> None:
    """
    Esta função divide um PDF contendo vários documentos de Cédula C,
    separando por cpf de user e salva cada arquivo por servidor.

    :params: task (Task) Instância da tarefa assíncrona
    :params: hook (str) Identificação da tarefa
    :params: success (str) Mensagem que será retornada em caso de sucesso da tarefa
    :params: user (User) instância de usuário que será vinculado à tarefa
    :params: path (str) Caminho absoluto (path) do arquivo CédulaC
    :params: reference (str) Ano/Tipo de referência do arquivo

    :returns: None

    """
    try:
        task = Task.objects.get(uuid=task)
        if os.path.exists(path):
            reader = PdfReader(path, strict=False)
        output = PdfWriter()
        gedfile = None
        servidor = None
        arquivo = None
        for page in range(len(reader.pages)):
            text = reader.pages[page].extract_text()
            identifier_cpf = search_cpf_and_indentifier(text)
            if not identifier_cpf:
                gedfile, servidor, arquivo = create_pdf_cedula_c(
                    reader,
                    page,
                    output,
                    identifier_cpf,
                    reference,
                    gedfile,
                    servidor,
                    arquivo,
                )
            else:
                output = PdfWriter()
                gedfile, servidor, arquivo = create_pdf_cedula_c(
                    reader, page, output, identifier_cpf, reference, None, None, None
                )
            output = PdfWriter() if not output else output

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
        has_exception = None
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."
        state = "failed"

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def get_cedula_c(
    task,
    hook,
    success,
    user,
    params=None,
    document_pk=None,
    extension=None,
    download=False,
    origem_apiv2=False,
):
    """
    Esta Tarefa localiza uma Cédula-c pelo Pk do Servidor (pk) e ano de referência da Cédula-C
    e retorna valores para download.

    :params: task (Task) Instância da tarefa assíncrona
    :params: hook (str) Identificação da tarefa
    :params: success (str) Mensagem que será retornada em caso de sucesso da tarefa
    :params: user (User) instância de usuário que será vinculado à tarefa
    :params: params (list) lista de parâmetros adicionais
    :params: document_pk (int) Id do Arquivo de referência da Cédula-C
    :params: extension (str) Extenção do arquivo
    :params: download (bool) Se o arquivo terá download autmático ou não

    :returns: None

    """
    try:
        task = Task.objects.get(uuid=task)

        document = Arquivo.objects.filter(pk=document_pk).first()

        if not document:
            has_exception = Exception(
                "O servidor ainda não possui Cédula-C cadastrada para a referência informada."
            )
            message = "O servidor ainda não possui Cédula-C cadastrada para a referência informada."
            state = "failed"
        else:
            task.data = {
                "file": document.absolute_path,
                "filename": document.filename,
                "mimetype": document.mimetype,
                "extension": extension,
                "remove_file": False,
            }
            if download and not origem_apiv2:
                RemoteEmmiter.emmit_for_user(
                    task.owner,
                    "cedula-c",
                    path=f"/athenas/CedulaCIRPF/download_file/?uuid={task.uuid}",
                    filename=document.filename,
                )
            msg_params = locals()
            msg_params.update(uuid=task.uuid)
            message = success % msg_params
            state = "ready"
            has_exception = None
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def vincular_processos_rra(task, hook, folha, rra, user):
    set_current_user(user)

    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        folha_str = Folha.objects.get(pk=folha).__str__()
        task.message = f"<p>Vinculando processo de RRA a folha {folha_str}</p>"
        task.state = "progress"
        task.progress = 0
        task.save()

        rra_servidores = RRAEmployee.objects.filter(rra__pk=rra)

        for rra_servidor in rra_servidores:
            eventos = list(rra_servidor.rra.events.filter())
            contracheques = Paycheck.objects.filter(
                folha__id=folha,
                servidor=rra_servidor.employee,
                lancamentos__evento__in=eventos,
            ).distinct()
            for contracheque in contracheques:
                for lancamento in contracheque.lancamentos.filter(
                    rra_employee__isnull=True
                ):
                    lancamento.rra_employee = rra_servidor
                    lancamento.save()

        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"Erro em {err}", type_of=3)
        task.finish_execution(status="ERROR")

    if has_exception:
        raise has_exception


@app.task()
def importar_processos_rra(task, hook, processo_id, arquivo_id, user):
    set_current_user(user)

    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        processo_rra = RRA.objects.get(pk=processo_id)
        arquivo = Arquivo.objects.get(pk=arquivo_id)
        task.message = f"<p>Importando servidores do processo de rra</p>"
        task.state = "progress"
        task.progress = 0
        task.save()

        df = pd.read_excel(arquivo.absolute_path, engine="openpyxl")
        dados_rra = df.to_dict(orient="records")

        data_object = []

        for rra_servidor in dados_rra:
            servidor = Servidor.objects.get(matricula=rra_servidor["MATRICULA"])
            objeto = RRAEmployee(
                employee=servidor,
                rra=processo_rra,
                months=rra_servidor["MESES"],
                created_by=get_current_user(),
                modified_by=get_current_user(),
            )
            data_object.append(objeto)

        RRAEmployee.objects.bulk_create(data_object)

        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"Erro em {err}", type_of=3)
        task.finish_execution(status="ERROR")

    if has_exception:
        raise has_exception
