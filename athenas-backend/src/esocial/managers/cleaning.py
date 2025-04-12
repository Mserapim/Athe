# -*- coding: utf-8 -*-
import shutil
import time

from django.conf import settings

from contrib.utils import getLogger
from esocial.managers.file_support import directory_data_generate_xml
from esocial.models import (
    BatchEvent,
    Configuration,
    Event,
    EventDependency,
    Occurrence,
    Reference,
    ReturnResult,
)
from esocial.utils import esocial_environment

TIME_TO_WAIT = 5  # second
NUMBER_OF_TRY = 10  # second
TOTAL_PCT = 100


log = getLogger(__name__)


def _clear_restricted_production(clear_environment=True, task=None, feedback=None):
    _clear_local_database()
    BatchEvent.create_events(
        clear_environment=clear_environment, events=["s1000"], task=task.uuid
    )

    BatchEvent.create_batches(generate_xml=True, task=task)
    batch = BatchEvent.objects.filter(delivery_status=2).last()
    try:
        batch.send_to_esocial()
        task.info(f"{batch} enviado.", type_of=1)
    except Exception as err:
        log.exception(err)
        task.info(f"Erro enviando {batch}: {err}", type_of=3)

    task.info(pct_progress=50)
    batch.refresh_from_db()
    count = 0
    while count < 30 and batch.process_status == 101:
        try:
            batch.consult_process(task=task)
            if batch.process_status != 101:
                task.info(f"{batch} consultado.", type_of=1)
                task.info(pct_progress=50)
                break
            else:
                task.info(f"{batch} consultando...", type_of=1)
                time.sleep(10)
            count += 1
        except Exception as err:
            log.exception(err)
            task.info(f"Erro consultando {batch}: {err}", type_of=3)


def _clear_local_database(only_not_sent=False):

    def _clear_event():
        query = Event.objects_deleted.exclude(ide_evento_tp_amb=1)
        total = query.count()
        print(f"Apagando Event {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_event_not_sent():
        query = Event.objects_deleted.filter(process_status__in=(1, 2, 3, 5)).exclude(
            internal=True
        )
        total = query.count()
        print(f"Apagando Event not sent {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_bacthevent():
        query = BatchEvent.objects.exclude(environment=1)
        total = query.count()
        print(f"Apagando BatchEvent: {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_returnresult():
        query = ReturnResult.objects.exclude(environment=1)
        total = query.count()
        print(f"Apagando ReturnResult: {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_occurrence():
        query = Occurrence.objects.exclude(environment=1)
        total = query.count()
        print(f"Apagando Occurrence: {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_reference():
        query = Reference.objects.exclude(environment=1)
        total = query.count()
        print(f"Apagando Reference: {total}...")
        rs = query.delete()
        print(f"...{rs}")

    def _clear_eventdependency():
        query = EventDependency.objects.exclude(environment=1)
        total = query.count()
        print(f"Apagando EventDependency: {total}...")
        rs = query.delete()
        print(f"...{rs}")

    if only_not_sent:
        _clear_event_not_sent()
    else:
        environment = esocial_environment()
        if environment != 1:

            print(f"eSocial environment({environment})")

            _clear_eventdependency()
            _clear_reference()
            _clear_event()
            _clear_bacthevent()
            _clear_returnresult()
            _clear_occurrence()

            try:
                shutil.rmtree(directory_data_generate_xml(), ignore_errors=True)
            except Exception as err:
                log.exception(err)

        else:
            raise Exception("Não é permitido apagar base local em produção!")


def _change_environment_on_clone_base():
    """Clonar a base de dados do ambiente de produção para que possa ser usado no ambiente de teste ou homologação.
    Antes da clonagem a base de ambiente 2 (produção restrita) será apagada localmente e depois todos os eventos
    de produção - ambiente 1 (enviados ou não) serão atualizados para ambiente 2.
    Esta rotina não deve ser utilizada em maquina de produção, mesmo que esteja em ambiente 2.

    Raises:
        Exception: _description_
    """
    env_var = settings.ESOCIAL_ENVIRONMENT
    environment = esocial_environment()

    ups_event = ups_batch = 0

    if env_var == 2 and environment == 2:

        print(f"eSocial environment({environment})")

        _clear_local_database()

        ups_event = Event.objects_all.filter(ide_evento_tp_amb=1).update(
            ide_evento_tp_amb=2
        )
        ups_batch = BatchEvent.objects_all.filter(environment=1).update(environment=2)
        ups_rr = ReturnResult.objects_all.filter(environment=1).update(environment=2)
        ups_o = Occurrence.objects_all.filter(environment=1).update(environment=2)
        ups_ed = EventDependency.objects_all.filter(environment=1).update(environment=2)
        conf_restricted = Configuration.objects.filter(environment=2).last()
        ws_batch_submission = conf_restricted.ws_batch_submission
        ws_batch_consult_process = conf_restricted.ws_batch_consult_process
        xml_send_schema_name = conf_restricted.xml_send_schema_name
        xmlns_send = conf_restricted.xmlns_send
        xml_consult_schema_name = conf_restricted.xml_consult_schema_name
        xmlns_consult = conf_restricted.xmlns_consult
        ups_conf = Configuration.objects.filter(environment=1).update(
            environment=2,
            ws_batch_submission=ws_batch_submission,
            ws_batch_consult_process=ws_batch_consult_process,
            xml_send_schema_name=xml_send_schema_name,
            xmlns_send=xmlns_send,
            xml_consult_schema_name=xml_consult_schema_name,
            xmlns_consult=xmlns_consult,
        )
        conf_restricted.delete()
        return ups_event, ups_batch, ups_rr, ups_o, ups_ed, ups_conf
    else:
        raise Exception("Não é permitido modificar base de produção!")
