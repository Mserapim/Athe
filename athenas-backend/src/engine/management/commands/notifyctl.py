# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from engine.notification.models import Notification
from dateutil.relativedelta import relativedelta
from datetime import datetime
from contrib.middleware import set_current_user
from django.contrib.auth.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--mark-read",
            dest="mark_read",
            help="Marca as mensagens selecionadas como lidas.",
            action="store_true",
        )

        parser.add_argument(
            "--older",
            dest="older",
            help="Seleciona as mensagens que chegaram a mais de X dias e estão como não lidas.",
            type=int,
            default=None,
        )

    def handle(self, mark_read=False, older=None, **kwargs):
        try:
            user = User.objects.get(username="job_notifyctl_handle")
        except User.DoesNotExist as e:
            self.error('Não econtrei o usuário "job_notifyctl_handle"')
            raise e
        else:
            set_current_user(user)

        limit = (
            datetime.now() - relativedelta(days=older)
            if older
            else datetime(1900, 1, 1, 0, 0, 0)
        )

        query = Notification.objects.filter(created_at__lte=limit, status=2)
        print("Selecionado as mensagens não lidas enviadas até %s" % limit)
        print("Total de mensagens não lidas: %d" % query.count())

        if mark_read:
            count = query.update(status=16)
            print("Total de mensagens marcadas como abandonadas: %d" % count)
