# -*- coding: utf-8 -*-
import os
from logging import getLogger

from django.db import transaction
from celery import Celery

from engine.mq.models import Task
from contrib.middleware import StartupLoader, set_current_user
from edocs.protocolo.models import Protocolo, Movimentacao, Impressora
from rh.models import OrgaoGeral, User

log = getLogger("tasker")

# django.setup()

app = Celery("rh_reference")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def generalorgan_update_reference(task, hook, new, old, sender, sender_klass):
    StartupLoader().doLoad()

    set_current_user("athenas")

    message = (
        "<p>EDOCS - Atualizando referências de %s: %s -> mudou para-> %s...</p>"
        % (sender, old, new)
    )
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    try:
        new = OrgaoGeral.objects.get(pk=new)
        old = OrgaoGeral.objects.get(pk=old)
        sender = eval(sender_klass).objects.get(pk=sender)

        message = (
            "<p>EDOCS - Atualizando referências de %s: %s -> mudou para-> %s...</p>"
            % (sender._meta.verbose_name, old, new)
        )
        log.info(message)
        task.message = message
        task.state = "progress"
        task.save()

        with transaction.atomic():
            log.info(
                "Protocolo orgao_geral_origem: %s"
                % (Protocolo.objects.filter(orgao_geral_origem=old).count())
            )
            Protocolo.objects.filter(orgao_geral_origem=old).update(
                orgao_geral_origem=new
            )
            log.info(
                "Protocolo orgao_geral_destino: %s"
                % (Protocolo.objects.filter(orgao_geral_destino=old).count())
            )
            Protocolo.objects.filter(orgao_geral_destino=old).update(
                orgao_geral_destino=new
            )
            log.info(
                "Protocolo lotacao_criacao: %s"
                % (Protocolo.objects.filter(lotacao_criacao=old).count())
            )
            Protocolo.objects.filter(lotacao_criacao=old).update(lotacao_criacao=new)
            log.info(
                "Movimentacao lotacao_origem: %s"
                % (Movimentacao.objects.filter(lotacao_origem=old).count())
            )
            Movimentacao.objects.filter(lotacao_origem=old).update(lotacao_origem=new)
            log.info(
                "Movimentacao lotacao_destino: %s"
                % (Movimentacao.objects.filter(lotacao_destino=old).count())
            )
            Movimentacao.objects.filter(lotacao_destino=old).update(lotacao_destino=new)
            log.info(
                "Movimentacao lotacao_criacao: %s"
                % (Movimentacao.objects.filter(lotacao_criacao=old).count())
            )
            Movimentacao.objects.filter(lotacao_criacao=old).update(lotacao_criacao=new)
            if old.lotacao and new.lotacao:
                Impressora.objects.filter(lotacao=old.lotacao).update(
                    lotacao=new.lotacao
                )
            message = (
                "<p>EDOCS - Atualização de referências de %s: %s -> mudou para -> %s.</p><p>Finalizada com sucesso.</p>"
                % (sender._meta.verbose_name, old, new)
            )
            state = "ready"
            log.info(message)
    except Exception as err:
        log.exception(str(err))
        has_exception = err
        message = (
            "<p>EDOCS - Falha na atualização de referências de %s: %s -> mudou para -> %s.</p>"
            % (
                sender._meta.verbose_name if not isinstance(sender, int) else sender,
                old,
                new,
            )
        )
    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def receive_send(
    user_to_receive,
    user_to_send,
    move,
    physical,
    opinion,
    urgency,
    close,
    advice,
    references,
    location_destination,
):
    StartupLoader().doLoad()

    set_current_user(User.objects.get(pk=user_to_receive))

    move = Movimentacao.objects.get(pk=move)
    message = "Enviando %s" % move
    log.info(message)
    print(message)
    try:
        params = {
            "physical": physical,
            "opinion": opinion,
            "urgency": urgency,
            "close": close,
            "advice": advice,
            "references": references,
            "location_destination": [location_destination],
        }
        try:
            move.sign_received()
        except Exception as err:
            log.info(str(err))
            print(str(err))

        set_current_user(User.objects.get(pk=user_to_send))
        validate_possession_for_do_send = Movimentacao.validate_possession_for_do_send
        Movimentacao.validate_possession_for_do_send = lambda self: True
        move.do_send(**params)
        Movimentacao.validate_possession_for_do_send = validate_possession_for_do_send
    except Exception as err:
        log.exception(str(err))
        print(str(err))
