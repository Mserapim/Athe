# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.models import MovimentacaoPosse
from rh.socialsecurity.models import RetirementPrevision, EmploymentBond

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando alinha as posses aos vínculos empregatícios"""

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.align_possession_on_employmentbond()

    def align_possession_on_employmentbond(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando alinhamento das posses aos vínculos empregatícios >>>>>>>>>>>>>"
        )

        movs_posses = MovimentacaoPosse.objects.filter(
            servidor__type_by_possession__in=["EFE", "ECM", "EFC"]
        )
        for mov_posse in movs_posses:
            if mov_posse.data_exercicio:
                rp, created = RetirementPrevision.objects.get_or_create(
                    natural_person=mov_posse.servidor.pessoa_fisica
                )
                end_date = (
                    (mov_posse.data_desligamento + relativedelta(days=-1))
                    if mov_posse.data_desligamento
                    else None
                )
                if mov_posse.servidor.posses.filter(quadro__cargo__tipo_lei_cargo="EF"):
                    if rp.employmentbonds.all().count() > 0:
                        eb, created = rp.employmentbonds.update_or_create(
                            possession=mov_posse,
                            defaults={
                                "begin_date": mov_posse.data_exercicio,
                                "end_date": end_date,
                                "deduction": 0,
                                "public_employee": True,
                                "with_pgj": True,
                                "pension_system": mov_posse.servidor.regime_previdenciario,
                                "employer": "%s"
                                % mov_posse.quadro.cargo.unidade_administrativa,
                            },
                        )
                    else:
                        EmploymentBond.objects.create(
                            possession=mov_posse,
                            retirement_prevision=rp,
                            begin_date=mov_posse.data_exercicio,
                            end_date=end_date,
                            deduction=0,
                            public_employee=True,
                            with_pgj=True,
                            pension_system=mov_posse.servidor.regime_previdenciario,
                            employer="%s"
                            % mov_posse.quadro.cargo.unidade_administrativa,
                        )
                    log.info(
                        "Update SocialSecurity %s" % mov_posse.servidor.pessoa_fisica
                    )

        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando alinhamento das posses aos vínculos empregatícios >>>>>>>>>>>>>"
        )
