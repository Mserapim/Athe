# -*- coding:utf-8 -*-

from celery import Celery
from django.db import transaction
from django.contrib.auth.models import User
from contrib.utils import getLogger
from engine.mq.models import Task
from common.poll.models import Poll, AllowedList, BlackList

log = getLogger(__name__)

app = Celery("poll")
app.config_from_object("app.celeryconf")


@app.task
def fill_allowed_list(task, hook, poll_id):
    poll = Poll.objects.get(pk=poll_id)

    if poll.is_locked():
        Exception(
            "Não é possivel atualizar a lista de aptos. A eleição está em andamento ou encerrada."
        )

    task = Task.objects.get(uuid=task)
    task.message = "<p>Gerando lista de aptos para a eleição %s</p>" % poll
    task.state = "progress"
    try:
        with transaction.atomic():
            task.save()
            a_list = AllowedList.objects.get(poll=poll)
            b_list = BlackList.objects.get(poll=poll)
            a_list.allowed_users.clear()  # Necessário para não ficar usuários indevidos caso o publico alvo seja alterado

            users = User.objects.filter(servidor__isnull=False)
            for user in users:
                a_users_qs = a_list.allowed_users.filter(pk=user.pk)
                b_users_qs = b_list.blocked_users.filter(pk=user.pk)
                if (
                    poll.test_user_conditions(user)
                    and not a_users_qs.exists()
                    and not b_users_qs.exists()
                ):
                    a_list.allowed_users.add(user)
    except Exception as e:
        task.message = (
            "<p>Não foi possível gerar lista de aptos para a eleição %s</p>" % poll
        )
        task.state = "failed"
        task.save()
        log.exception(e)
    else:
        task.message = "<p>Lista de aptos para a eleição %s foi gerada.</p>" % poll
        task.state = "ready"
        task.save()
        poll.updating_allowed_list = False
        poll.save()
        log.info("Allowed list filled.")
