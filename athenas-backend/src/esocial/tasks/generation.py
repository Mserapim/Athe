# -*- coding: utf-8 -*-
import os

import django
from celery import Celery
from django.db.models import F, Q

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from esocial.const import RECTIFICATION
from esocial.extractors.base import Factory
from esocial.managers.cleaning import (
    _change_environment_on_clone_base,
    _clear_local_database,
    _clear_restricted_production,
)
from esocial.models import S1210, PayrollPeriod, BatchEvent, DemonstrativeItem, Event
from esocial.utils import get_acronyms_from_kind
from rh.gfp.models import Periodo

log = getLogger("esocial")
app = Celery("esocial")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)
django.setup()


@app.task()
def create_events_task(task, hook, event_kind, user, **kwargs):
    map_title = {
        "EEMP": "do Empregador",
        "TI": "de tabelas iniciais",
        "CF": "de cadastros funcionais",
        "FP": "periódicos (de folha)",
        "TOT": "totalizadores",
        "SST": "de SST",
        "STPC": "de totalização de pagamentos em contingência",
        "REP": "de reabertura de eventos periódicos",
        "FEP": "de fechamento de eventos periódicos",
        "EBS": "de exclusão",
    }
    message = "<p>Gerando eventos " + map_title.get(event_kind[0]) + " (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.create_events(event_kind=event_kind, task=task.uuid, period=None)
        task.finish_execution(msg=message, set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_ti_task(task, hook, user):
    message = "<p>Geração de eventos de TI (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_events_ti(task=task)
        task.finish_execution(set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_ti_registration_task(task, hook, user):
    message = "<p>Geração de eventos de TI e Cadastro (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_events_ti_registration(task=task)
        task.finish_execution(set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_registration_task(
    task, hook, user, group_event="CF", categories=[]
):
    message = "<p>Geração de eventos de Cadastro (e-Social)</p>"

    if group_event == "SST":
        message = "<p>Geração de eventos de SST (e-Social)</p>"

    task = Task.objects.get(uuid=task)
    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_events_registration(
            group_event=group_event, task=task, categories=categories
        )
        task.finish_execution(set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = f"<p>Erro em {message}</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_payroll_task_list(task, hook, user, period=[]):
    msg = ""
    for p in Periodo.objects.filter(pk__in=period).order_by("ano", "mes"):
        msg += f"{p} "

    message = f"<p>Geração de eventos de Folha (e-Social) {msg}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        for p in Periodo.objects.filter(pk__in=period).order_by("ano", "mes"):
            task.message = f"{message} - {p}"
            task.state = "progress"
            task.progress_message = ""
            task.progress = 0
            task.save()
            BatchEvent.generate_events_payroll(task=task, period=p.pk)
            task.refresh_from_db()

        task.refresh_from_db()
        task.finish_execution(msg=f"{message} - finalizado.", set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_payroll_process_task_list(task, hook, user, period=[], events=[]):
    msg = ""
    for p in Periodo.objects.filter(pk__in=period).order_by("ano", "mes"):
        msg += f"{p} "

    message = f"<p>Geração de eventos de Folha (e-Social) {msg}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        for p in Periodo.objects.filter(pk__in=period).order_by("ano", "mes"):
            task.message = f"{message} - {p}"
            task.state = "progress"
            task.progress_message = ""
            task.progress = 0
            task.save()
            BatchEvent.generate_events_payroll_process(
                task=task, period=p.pk, events=events
            )
            task.refresh_from_db()

        task.refresh_from_db()
        task.finish_execution(msg=f"{message} - finalizado.", set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_payroll_task(task, hook, user, period):
    period = Periodo.objects.get(pk=period)
    message = f"<p>Geração de eventos de Folha (e-Social) {period}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_events_payroll(task=task, period=period.pk)
        task.finish_execution(set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_events_payroll_process_task(task, hook, user, period, events=[]):
    period = Periodo.objects.get(pk=period)
    message = f"<p>Geração de eventos de Folha (e-Social) {period}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_events_payroll_process(
            task=task, period=period.pk, events=events
        )
        task.finish_execution(set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao gerar tabelas</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_delete_events_payroll_task(task, hook, user, period, events=[]):
    period = Periodo.objects.get(pk=period)
    message = f"<p>Geração de eventos de exclusão (S-3000) da Folha de Pagamentos {period}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_delete_events_payroll(
            task=task, period=period.pk, events=events
        )
        task.finish_execution(message, set_process=False)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao excluir evento</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task
def delete_event_payroll(task_uuid, user, event, inc_progress=0):
    set_current_user(user)
    task = Task.objects.filter(uuid=task_uuid).last()

    try:
        Event.objects.get(pk=event).delete_esocial(task=task)
    except Exception as err:
        log.exception(err)
        msg = f"Erro gerando Exclusão de {event}: {err}"
        print(msg)
        if task:
            task.info(msg=msg, type_of=3)

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_close_events_payroll_task(task, hook, user, period):
    period = Periodo.objects.get(pk=period)
    message = f"<p>Geração de evento de fechamento (S-1299) da Folha de Pagamentos {period}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_close_events_payroll(task=task, period=period.pk)
        task.finish_execution(message)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao excluir evento</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_reopen_events_payroll_task(task, hook, user, period):
    period = Periodo.objects.get(pk=period)
    message = f"<p>Geração de evento de reabertura (S-1298) da Folha de Pagamentos {period}</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_reopen_events_payroll(task=task, period=period.pk)
        task.finish_execution(message)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro ao excluir evento</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def generate_event_registration(
    task_uuid, user, period, registry, registry_person, map_event=None, inc_progress=0
):
    map_events = {
        "s2200": Q(matricula=registry),  #  servidor
        "s2300": Q(matricula=registry),  #  servidor
        "s2205": Q(matricula=registry),  #  servidor
        "s2206": Q(matricula=registry),  #  servidor
        "s2306": Q(matricula=registry),  #  servidor
        "s2400": Q(matricula=registry),  #  servidor
        "s2405": Q(matricula=registry),  #  servidor
        "s2410": Q(servidor__matricula=registry),  #  benefitmov
        "s2416": Q(servidor__matricula=registry),  #  benefitmov
        "s2418": Q(servidor__matricula=registry),  #  benefitmov
        "s2420": Q(servidor__matricula=registry),  #  movimentacaodesligamento
        "s2230": Q(servidor__matricula=registry),  #  baselicencaafastamento
        "s2231": Q(servidor__matricula=registry),  #  afastamentooutroorgao
        "s2299": Q(servidor__matricula=registry),  #  desligamento
        "s2399": Q(servidor__matricula=registry),  #  requisicao
        "s2298": Q(servidor__matricula=registry),  #  servidor
    }

    set_current_user(user)
    task = Task.objects.filter(uuid=task_uuid).last()

    def _create():
        acronyms = get_acronyms_from_kind(["CF"])

        """Criação"""

        try:
            Factory.get_factory(map_event).manage_in_bulk(
                task=task,
                period=period,
                filter_query_instance=map_events.get(map_event),
                registry=registry,
            )
        except Exception as err:
            log.exception(err)
            msg = f"Erro gerando {map_event}: {err}"
            print(msg)
            if task:
                task.info(msg=msg, type_of=3)
        Event.call_evaluate_dependency(
            acronyms=acronyms, registry_employee=registry, task=task
        )

    _create()

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_event_sst(
    task_uuid, user, period, registry, registry_person, inc_progress=0
):
    map_events = {
        "s2210": Q(employee__pessoa_fisica__cpf=registry_person),  #  servidor
        "s2220": Q(employee__pessoa_fisica__cpf=registry_person),  #  servidor
        "s2240": Q(employee__pessoa_fisica__cpf=registry_person),  #  servidor
    }

    set_current_user(user)
    task = Task.objects.filter(uuid=task_uuid).last()

    def _create():
        acronyms = get_acronyms_from_kind(["SST"])

        """Criação"""
        for acronym in acronyms:
            try:
                Factory.get_factory(acronym).manage_in_bulk(
                    task=task,
                    period=period,
                    filter_query_instance=map_events.get(acronym),
                    registry=None,
                    registry_person=registry_person,
                )
            except Exception as err:
                log.exception(err)
                msg = f"Erro gerando {acronym}: {err}"
                print(msg)
                if task:
                    task.info(msg=msg, type_of=3)
        Event.call_evaluate_dependency(
            acronyms=acronyms, registry_person=registry_person, task=task
        )

    _create()

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_event_s1010(task_uuid, user, period, number, inc_progress=0):
    acronym = "s1010"
    set_current_user(user)
    task = Task.objects.filter(uuid=task_uuid).last()

    if acronym in get_acronyms_from_kind(["TI"]):

        """Criação"""
        try:
            Factory.get_factory(acronym).manage_in_bulk(
                task=task, period=period, filter_query_instance=Q(numero=number)
            )
        except Exception as err:
            log.exception(err)
            if task:
                task.info(msg=f"Erro gerando {acronym}: {err}", type_of=3)

        Event.call_evaluate_dependency(acronyms=[acronym], oid=number, task=task)

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_event_payroll(
    task_uuid, user_pk, period_pk, registry_person, inc_progress=0
):
    map_events = {
        "s1200": Q(cpf=registry_person),
        "s1202": Q(cpf=registry_person),
        "s1207": Q(cpf=registry_person),
        "s1210": Q(cpf=registry_person),
    }

    set_current_user(user_pk)
    task = Task.objects.filter(uuid=task_uuid).last()
    period = Periodo.objects.get(pk=period_pk)

    dr = NewDateRange.from_month(period.ano, 12 if period.mes == 13 else period.mes)
    start_competence = dr.first
    end_competence = dr.last

    acronyms = get_acronyms_from_kind(["FP"])

    """Criação"""
    for acronym in acronyms:
        try:
            Factory.get_factory(acronym).manage_in_bulk(
                task=task,
                period=period,
                start_competence=start_competence,
                end_competence=end_competence,
                filter_query_instance=map_events.get(acronym),
                registry_person=registry_person,
            )
        except Exception as err:
            log.exception(err)
            if task:
                task.info(msg=f"Erro gerando {acronym}: {err}", type_of=3)

    Event.call_evaluate_dependency(
        acronyms=acronyms, registry_person=registry_person, task=task
    )

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_event_payroll_process(
    task_uuid, user_pk, period_pk, registry_person, events=[], inc_progress=0
):
    map_events = {
        "s1200": Q(cpf=registry_person),
        "s1202": Q(cpf=registry_person),
        "s1207": Q(cpf=registry_person),
        "s1210": Q(cpf=registry_person),
    }

    acronyms = list(set(get_acronyms_from_kind(["FP"])).intersection(events))
    acronyms.sort()

    set_current_user(user_pk)
    task = Task.objects.filter(uuid=task_uuid).last()
    period = Periodo.objects.get(pk=period_pk)

    dr = NewDateRange.from_month(period.ano, 12 if period.mes == 13 else period.mes)
    start_competence = dr.first
    end_competence = dr.last

    def _create(acronyms):
        """Este método executa a criação de eventos contidos em acronyms.

        Args:
            acronyms (list): lista de acrônimos.
        """
        for acronym in acronyms:
            try:
                Factory.get_factory(acronym).manage_in_bulk(
                    task=task,
                    period=period,
                    start_competence=start_competence,
                    end_competence=end_competence,
                    filter_query_instance=map_events.get(acronym),
                    registry_person=registry_person,
                )
            except Exception as err:
                log.exception(err)
                if task:
                    task.info(msg=f"Erro gerando {acronym}: {err}", type_of=3)

        Event.call_evaluate_dependency(
            acronyms=acronyms, registry_person=registry_person, task=task
        )

    def _evaluate_exclusion():
        """Este método analisa se é necessário criar exclusões(s1210) no esocial a partir de retificações nos demonstrativos."""
        demonstratives = (
            Event.objects.filter(
                acronym__in=("s1200", "s1202", "s1207"),
                action=RECTIFICATION,
                registry_person=registry_person,
            )
            .validity_in(start_competence, end_competence)
            .valids_not_sent()
        )
        payments = S1210.objects.filter(registry_person=registry_person).validity_in(
            start_competence, end_competence
        )

        remove_payment = False
        if demonstratives.exists():
            remove_payment = True
        elif payments.filter(action=RECTIFICATION).valids_not_sent().exists():
            remove_payment = True

        if remove_payment:
            """Apagando s1210 não enviados."""
            for payment in payments.valids_not_sent():
                payment.delete()
            """Apagando s1210 não enviados."""
            for payment in payments.valids_sent():
                payment.delete_esocial(task=task)
        return remove_payment

    """Criando todos eventos de pagamento."""
    _create(acronyms)

    """Analisando se é necessário criar exclusões(s1210) no esocial."""
    if _evaluate_exclusion():
        """Criando pagamentos após exclusões no esocial."""
        _create(("s1210",))

    Event.call_evaluate_dependency(
        acronyms=acronyms, registry_person=registry_person, task=task
    )

    if task:
        Task.objects.filter(uuid=task_uuid).update(
            progress=F("progress") + inc_progress
        )


@app.task()
def generate_delete_events_task(task, hook, user, events):
    message = "<p>Geração de eventos de exclusão (S-3000)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.generate_delete_events(task=task, events=events)
        task.finish_execution(message)
    except Exception as err:
        log.exception(err)
        has_exception = err
        task.info(msg=f"<p>Erro ao excluir evento</p><br />{err}", type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def delete_events_task(task, hook, user):
    message = "<p>Apagando eventos da base local (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        _clear_local_database()
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao gerar eventos"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def delete_events_not_sent_task(task, hook, user):
    message = "<p>Apagando eventos não enviados da base local (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        _clear_local_database(only_not_sent=True)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao apagar eventos"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def clone_production_base_task(task, hook, user):
    message = "<p>Importando base de produção para ambiente de desenvolvimento</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        ups_event, ups_batch, ups_rr, ups_o, ups_ed, ups_conf = (
            _change_environment_on_clone_base()
        )
        msg = f"Ambiente do banco modificado para desenvolvimento. Eventos: {ups_event} Lotes: {ups_batch}"
        msg += f"Retorno: {ups_rr} Ocorrência: {ups_o} Dependência: {ups_ed} Configuração: {ups_conf}."
        task.info(msg=msg)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao alterar ambiente de eventos!"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def create_batches_task(task, hook, user):
    message = "<p>Criando lotes (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        msg = "Iniciando..."
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        BatchEvent.create_batches(generate_xml=True, task=task)
        task.info(msg, pct_progress=100)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        task.state = "failed"
        message = "Erro ao criar lotes"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def clear_restricted_production_task(task, hook, user):
    message = "<p>Apagando produção restrita (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()
        _clear_restricted_production(task=task, feedback=feedback)
        task.finish_execution()
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao limpar produção restrita"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def consult_batches_task(task, hook, batch, user):
    message = "<p>Consultando lotes enviados (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        msg = "Iniciando..."
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        task.info(msg, pct_progress=0)

        if batch:
            batches = BatchEvent.objects.filter(pk=batch)
        else:
            batches = BatchEvent.objects.filter(process_status=101)
        for batch in batches:
            try:
                batch.consult_process(task=task)
                task.info(f"{batch} consultado.", type_of=1)
            except Exception as err:
                log.exception(err)
                task.info(f"Erro consultando {batch}: {err}", type_of=3)
            task.increment_progress(100.0 / batches.count())
        task.info("Consulta finalizada.", pct_progress=100)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao consultar lotes"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def send_batches_task(task, hook, batch, user):
    message = "<p>Enviando lotes (e-Social)</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        if batch:
            batches = BatchEvent.objects.filter(pk=batch)
        else:
            batches = BatchEvent.objects.filter(process_status=101)
        for batch in batches:
            try:
                batch.send_to_esocial()
                task.info(f"{batch} enviado.", type_of=1)
            except Exception as err:
                log.exception(err)
                task.info(f"Erro enviando {batch}: {err}", type_of=3)
            task.increment_progress(100.0 / batches.count())
        task.info("Envio finalizado.", pct_progress=100)
        task.finish_execution(msg=message)
    except Exception as err:
        log.exception("{}".format(err))
        has_exception = err
        message = "Erro ao consultar lotes"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def analysis_task(task, hook, user, period):
    period = Periodo.objects.get(pk=period)

    message = f"<p>Análise de Fechamento de Folha do período {period} (e-Social).</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        PayrollPeriod.analysis(task=task, period=period.pk)

        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro em Análise de Fechamento de Folha</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task()
def analysis_all_period_task(task, hook, user, periods=[]):
    message = "<p>Análise de Períodos de Folha (e-Social).</p>"
    task = Task.objects.get(uuid=task)

    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.progress = 0
        task.save()

        PayrollPeriod.analysis_all_period(task=task, periods=periods)

        task.finish_execution()
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>Erro em Análise de Fechamento de Folha</p>"
        task.info(msg="Erro em %s<br />%s" % (message, err), type_of=3)
        task.finish_execution(status="ERROR")
    if has_exception:
        raise has_exception


@app.task
def analysis_period(task_uuid, user, period):
    set_current_user(user)
    PayrollPeriod.analysis(
        task=Task.objects.filter(uuid=task_uuid).last(), period=period
    )


@app.task()
def update_demonstrative_item(user, demonstrative_item, task=None):
    set_current_user(user)

    try:
        DemonstrativeItem.objects.get(pk=demonstrative_item).update_entry()
    except Exception as err:
        log.exception(err)
        if task:
            task = Task.objects.get(uuid=task)
            task.info(
                msg=f"Erro atualizando {DemonstrativeItem.objects.get(pk=demonstrative_item)}: {err}",
                type_of=3,
            )
