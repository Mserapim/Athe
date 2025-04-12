# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from optparse import make_option
from datetime import datetime
from common.usefulday.models import ParseNonWorkingDay
from rh.models import Localidade
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger("db")


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
            "--date", dest="to_date", default=None, help="Set specific date."
        )

        parser.add_argument(
            "--lawsuit",
            dest="lawsuit",
            default=None,
            help="Specific one lawsuit for analize.",
        )

        parser.add_argument(
            "--diligence",
            dest="diligence",
            default=None,
            help="Specific one diligence for analize.",
        )

    def handle(self, dry_run, to_date, lawsuit, diligence, *args, **kwargs):
        from judicial.tasks import decrement_remaining_days as executor

        username = "job_juddeadline_handle"
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

        print("Iniciando contador de Prazo.")

        to_date = (
            datetime.strptime(to_date, "%d/%m/%Y") if to_date else datetime.today()
        )

        mydate = to_date.date()

        print("Data: %s " % mydate)

        occurrence = ParseNonWorkingDay.occurrences_not_processed_on_the_date(
            date=mydate
        )

        ignore_locations = []

        if occurrence.exists():
            exit = False
            oc = occurrence.filter(is_partial=False)

            if oc.exists():
                if not oc.filter(nonworkingday__abrangency__in=[1, 2]).exists():
                    ignore_locations = [l.place.pk for l in oc.filter()]

                else:
                    print(
                        "Prazo não será contado. Ha ocorrência de abrangência Nacional/Estadual na data %s "
                        % to_date
                    )
                    exit = True

            ParseNonWorkingDay.process_occurrences(occurrences=occurrence.filter())

            if exit:
                return

        query = Localidade.objects.filter(estado__sigla="TO").exclude(
            pk__in=ignore_locations
        )

        print("Quantidade de cidades a serem analizadas: %s " % query.count())

        for location in query.order_by("nome"):
            executor.delay(dry_run, location.pk, mydate)
