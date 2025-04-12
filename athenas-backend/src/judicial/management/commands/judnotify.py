# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from judicial.models import NotifyStack
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger


log = getLogger("db")


class Command(BaseCommand):

    def handle(self, *args, **kargs):
        username = "job_judnotify_handle"
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)
        query = NotifyStack.objects.filter(notfied=False)
        total = query.count()
        print("Enviando %d notificações..." % total)
        count = 0
        for entry in query:
            try:
                count += 1
                print("Enviado %d de %d" % (count, total))
                entry.notify()
            except Exception as e:
                print("Erro ao notificar Processo pk: %s" % entry.pk)
        print("Notificações enviadas")
