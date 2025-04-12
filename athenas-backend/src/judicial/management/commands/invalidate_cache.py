# -*- coding: utf-8 -*-
import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime
from contrib.utils import getLogger

from judicial.models import OutCourtLawsuit, PartLawsuit

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
            "--by-year", dest="year", default=None, help="Specific one year."
        )

        parser.add_argument(
            "--by-access-control", dest="access", default=False, help="All lawsuits."
        )

    def execute_command(self, pkset):
        query = OutCourtLawsuit.objects.filter(pk__in=pkset)

        count_success = 0
        count_build = 0
        count_error = 0
        count_total = query.count()

        for lawsuit in query:
            for part in lawsuit.parts.all():
                try:
                    if part.exists_cache_document_in_lawsuit:
                        count_build += 1
                        print(
                            "invalidando cache part: %s -> %s"
                            % (part.pk, part.signed_at)
                        )
                        part.invalidate_cache()
                        count_success += 1
                except Exception:
                    print("ERROR cache part: %s" % part.pk)
                    count_build += 1
                    count_error += 1

        print("Processados ..: %d" % count_total)
        print("Compilados ...: %d" % count_build)
        print(" - Com exitos : %d" % count_success)
        print(" - Com erros .: %d" % count_error)

    def handler_access_control(self):
        pkset = OutCourtLawsuit.objects.filter(
            access_controls__authorization__state__in=[1, 2]
        ).values("pk")
        self.execute_command(pkset)

    def handler_by_year(self, year):
        pkset = (
            OutCourtLawsuit.objects.filter(year=year)
            .filter(access_controls__authorization__state__in=[1, 2])
            .values("pk")
        )

        self.execute_command(pkset)

    def handle(self, dry_run, year=None, access=None, *args, **kwargs):

        print("Iniciando cache de procedimento(s).")

        if year:
            self.handler_by_year(year)
        elif access:
            self.handler_access_control()
