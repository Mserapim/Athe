# -*- coding: utf-8 -*-

import os
from logging import getLogger

from celery import Celery
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models.query_utils import Q

from contrib.middleware import set_current_user
from edocs.protocolo.task.rh_reference import generalorgan_update_reference
from engine.mq.models import Task
from rh.models import Cargo, Lotacao, Publicacao, ServidorLotacao

log = getLogger("tasker")

app = Celery("generalorgan")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def create_new_employeeworkplace(
    task, hook, new, old, old_reference, publication, user
):
    state = "failed"
    message = "<p>RH - Criando nova lotação de servidor para: %s...</p>" % new
    task = Task.objects.get(uuid=task)
    has_exception = None
    try:
        set_current_user(user)
        new = Lotacao.objects.get(pk=new)
        if not publication:
            raise Exception("Publicação de criação da Lotação não foi informada.")
        message = "<p>RH - Criando nova lotação de servidor para: %s...</p>" % new
        old = Lotacao.objects.get(pk=old)
        old_reference = Lotacao.objects.get(pk=old_reference) if old_reference else None
        publication = Publicacao.objects.get(pk=publication)

        task.message = "<p>RH - Criando nova lotação de servidor para: %s...</p>" % new
        task.state = "progress"
        task.save()
        with transaction.atomic():
            if old_reference and publication and publication.data_vigencia:
                date_start = publication.data_vigencia
                date_end = publication.data_vigencia - relativedelta(days=1)
                for employee_workplace in ServidorLotacao.objects.filter(
                    lotacao=old, ativo=True
                ):
                    ServidorLotacao.validate_posse = lambda x: True
                    if not ServidorLotacao.objects.filter(
                        lotacao=new.lotacao, servidor=employee_workplace.servidor
                    ).exists():
                        new_kwargs = dict(
                            [
                                (fld.name, getattr(employee_workplace, fld.name))
                                for fld in employee_workplace._meta.fields
                                if fld.name != employee_workplace._meta.pk
                            ]
                        )
                        new_kwargs.pop("id")
                        new_kwargs.pop("ativo")
                        new_kwargs.update({"lotacao": new.lotacao})
                        new_kwargs.update({"data_vigencia_inicio": date_start})
                        new_kwargs.update({"data_vigencia_fim": None})
                        new_kwargs.update({"publicacao": publication})
                        employee_workplace.data_vigencia_fim = date_end
                        try:
                            employee_workplace.save()
                        except Exception as err:
                            log.exception(err)
                        try:
                            ServidorLotacao.objects.create(**new_kwargs)
                        except Exception as err:
                            log.exception(err)
                        log.info("Lotação criada: %s" % new)
                state = "ready"
                message = (
                    "<p>RH - Criando nova lotação de servidor para: %s.</p><p>Finalizada com sucesso.</p>"
                    % new
                )
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = (
            "<p>RH - Falha na criação de nova lotação de servidor para: %s.</p><p>%s</p>"
            % (new, err)
        )
    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task
def manager_taks_updater(task, hook, new, user):
    message = "<p>EDOCS - Gerenciador de tarefas. </p>"
    log.info(message)
    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.save()
        for workplace in Lotacao.objects.filter(pk=new).exclude(old=None):
            log.info(
                "Migrando referências de %s =======> %s" % (workplace.old, workplace)
            )
            task_generalorgan_update_reference = Task.start(
                generalorgan_update_reference,
                new=workplace.pk,
                old=workplace.old.pk,
                sender=workplace.pk,
                sender_klass=workplace._meta.model.__name__,
            )
            while Task.objects.get(
                uuid=task_generalorgan_update_reference.uuid
            ).state in ("initialized", "progress"):
                # log.info('Running Task: %s -> %s' % (unicode(task_generalorgan_update_reference.uuid), unicode(
                #   Task.objects.get(uuid=task_generalorgan_update_reference.uuid).state)))
                pass
            task_update_workplace = Task.start(
                update_workplace, new=workplace.pk, old=workplace.old.pk
            )
            while Task.objects.get(uuid=task_update_workplace.uuid).state in (
                "initialized",
                "progress",
            ):
                # log.info('Running Task: %s -> %s' % (unicode(task_update_workplace.uuid), unicode(
                #   Task.objects.get(uuid=task_update_workplace.uuid).state)))
                pass
        state = "ready"
        message = "<p>EDOCS - Gerenciador de tarefas. </p>"
    except Exception as err:
        log.exception(err)
        has_exception = err
    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task
def update_workplace(task, hook, new, old):
    state = "failed"
    message = "<p>RH - Atualizando referências de %s para %s...</p>" % (old, new)
    task = Task.objects.get(uuid=task)
    has_exception = None
    try:
        new = Lotacao.objects.get(pk=new)
        old = Lotacao.objects.get(pk=old)
        message = "<p>RH - Atualizando referências de %s para %s...</p>" % (old, new)
        log.info(message)
        task.message = message
        task.state = "progress"
        task.save()
        with transaction.atomic():
            # MODELOS DE PARAMENTRO, ATUALIZAR PARA AS NOVAS REFERÊNCIAS
            log.info(
                "Lotacao.objects.filter(pai=old).exclude(~Q(new=None)) %s"
                % Lotacao.objects.filter(pai=old).exclude(~Q(new=None)).count()
            )
            Lotacao.objects.filter(pai=old).exclude(~Q(new=None)).update(pai=new)
            Cargo.objects.filter(lotacao_responsavel=old).update(
                lotacao_responsavel=new
            )

            Lotacao.objects.filter(pk=new.pk).update(habilita_protocolo=True)
            Lotacao.objects.filter(pk=new.pk).update(ativo=True)

            Lotacao.objects.filter(pk=old.pk).update(habilita_protocolo=False)
            Lotacao.objects.filter(pk=old.pk).update(ativo=False)

            # OS MODELOS ABAIXAO, PERMENACERÃO COM AS REFERÊNCIAS ANTIGAS
            # ServidorLocalizacao.objects.filter(localizacao=old).update(localizacao=new)
            # MovimentacaoRemocao.objects.filter(lotacao_destino=old).update(lotacao_destino=new)
            # MovimentacaoRemocaoMembro.objects.filter(lotacao_destino=old).update(lotacao_destino=new)
            # Publicacao.objects.filter(origem=old).update(origem=new)
            state = "ready"
            message = (
                "<p>RH - Atualizando referências de %s para %s.</p><p>Finalizada com sucesso.</p>"
                % (old, new)
            )
            log.info(message)
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>RH - Falha na atualização das referências de %s para: %s.</p>" % (
            old,
            new,
        )

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
