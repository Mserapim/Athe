# -*- coding: utf-8 -*-
import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from optparse import make_option
from datetime import datetime
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from dateutil.relativedelta import relativedelta
from datetime import datetime

from judicial.models import OutCourtLawsuit, PartLawsuit, EventControl

log = getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Execute in simulator mode, only print actions.",
        )

        parser.add_argument(
            "--last-minutes",
            dest="last_minutes",
            default=None,
            help="Especifica que devem ser analizados os procedimentos assinados nos ultimos N minutos.",
        )

        parser.add_argument(
            "--user",
            dest="user",
            required=True,
            help="Usuário que sera utilizado para gerar o cache, deve ter acesso aos procedimentos.",
        )

    def handler_by_part(self, relative_at=None):
        query = PartLawsuit.objects.filter(
            Q(signed_by__isnull=False)
            & Q(Q(access_controls=None) | ~Q(access_controls__suspended_by=None))
        ).order_by("-signed_at")

        if relative_at:
            query = query.filter(signed_at__gt=relative_at)

        count_success = 0
        count_skip = 0
        count_build = 0
        count_error = 0
        count_total = query.count()

        for part in query:
            try:
                if part.can_read and not part.exists_cache_document_in_lawsuit:
                    count_build += 1
                    print(
                        "Criando PDF para %s/%04d assinado %s"
                        % (
                            part.lawsuit.cache_number,
                            EventControl.number_control_of(part.lawsuit, part),
                            part.signed_at,
                        )
                    )
                    part.create_cache_document()
                    count_success += 1
                elif not part.can_read:
                    count_build += 1
                    count_skip += 1
                    print(
                        "Criando PDF para %s/%04d assinado %s {IGNORADO}"
                        % (
                            part.lawsuit.cache_number,
                            EventControl.number_control_of(part.lawsuit, part),
                            part.signed_at,
                        )
                    )
            except Exception as e:
                print("ERROR cache part: %s" % part.pk)
                print(e)
                count_build += 1
                count_error += 1

        print("Processados ....: %d" % count_total)
        print("Compilados .....: %d" % count_build)
        print(" - Com exitos ..: %d" % count_success)
        print(" - Com ignorado : %d" % count_skip)
        print(" - Com erros ...: %d" % count_error)

    def handle(self, dry_run, user, last_minutes=None, *args, **kwargs):

        print("Iniciando cache de procedimento(s).")
        set_current_user(user)

        relative_at = None
        if last_minutes:
            relative_at = datetime.now() + relativedelta(
                minutes=(-1) * int(last_minutes or 0)
            )

        self.handler_by_part(relative_at)
