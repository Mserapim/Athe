# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import translation

from contrib.middleware import set_current_user
from contrib.nil import nil_datetime
from contrib.utils import getLogger
from rh.socialsecurity.models import EmploymentBond, RetirementPrevision

log = getLogger("db")


class Command(BaseCommand):
    help = """
    Esse comando auxilia no trabalho de atualizacao das previsoes de aposentadoria, bem como dos vinculos empregaticios cadastrados'
    """
    verbose = "False"

    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--employmentbond",
            action="store_true",
            dest="employmentbond",
            default=None,
            help="Atualiza somente vinculos empregaticios.",
        ),
        parser.add_argument(
            "-r",
            "--retirementprevision",
            action="store_true",
            dest="retirementprevision",
            default=None,
            help="Atualiza somente as datas de aposentadoria dos servidores.",
        )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        from django.conf import settings

        translation.activate(settings.LANGUAGE_CODE)

        if options["employmentbond"] is None and options["retirementprevision"] is None:
            print(
                "Nenhum parametro foi passado. Consulte as opcoes passando o parametro -h"
            )
        else:
            if options["employmentbond"]:
                self.set_user_to_job("job_update_socialsecurity_update_employmentbond")
                self.update_employmentbond()
            if options["retirementprevision"]:
                self.set_user_to_job(
                    "job_update_socialsecurity_update_retirementprevision"
                )
                self.update_retirementprevision()

        translation.deactivate()

    def update_employmentbond(self):
        msg = nil_datetime(datetime.now(), None)
        try:
            for eb in EmploymentBond.objects.filter():
                eb.save()
        except Exception:
            msg += " >>> Nao foi possivel realizar a atualizacao dos vinculos."
            log.info(msg)
            print(msg)
        else:
            msg += " >>> Atualizacao dos vinculos empregaticios realizada com sucesso."
            log.info(msg)
            print(msg)

    def update_retirementprevision(self):
        msg = nil_datetime(datetime.now(), None)
        try:
            for rp in RetirementPrevision.objects.filter():
                rp.save()
        except Exception:
            msg += " >>> Nao foi possivel realizar a atualizacao das previsoes."
            log.info(msg)
            print(msg)
        else:
            msg += " >>> Atualizacao dos dados de previsao de aposentadoria realizada com sucesso."
            log.info(msg)
            print(msg)
