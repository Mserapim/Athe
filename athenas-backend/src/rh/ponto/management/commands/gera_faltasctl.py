# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from datetime import datetime
from contrib.middleware import set_current_user
from django.contrib.auth.models import User
from contrib.utils import getLogger
from engine.mq.models import Task

from rh.ponto.models import Falta
from rh.pvf.models import SendingTimeSheet

from rh.pvf.const import STS_EFFECTIVE

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """
    Este comando irá gerar as faltas para os Folhas Ponto efetivados entre 01/2023 e 08/2023.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["all"]:
            self.gera_faltas_retroativo()

    def activate_athenas_user(self):
        try:
            user = User.objects.get(username="job_gera_faltas_retroativo")
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "job_gera_faltas_retroativo" {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

        return user

    def gera_faltas_retroativo(self):
        user = self.activate_athenas_user()
        dt_hr_inicio = datetime.now().strftime("%d/%m/%Y %H:%M")
        print(
            f">>> {dt_hr_inicio} Iniciando geração de Faltas retroativo. >>>>>>>>>>>>>"
        )
        log.info(
            f">>> {dt_hr_inicio} Iniciando geração de Faltas retroativo. >>>>>>>>>>>>>"
        )

        meses_referencia = [1, 2, 3, 4, 5, 6, 7, 8]
        for mes in meses_referencia:
            try:
                servidor_ids = (
                    SendingTimeSheet.objects.filter(
                        status__in=[STS_EFFECTIVE],
                        reference_month=mes,
                        reference_year=2023,
                    )
                    .values_list("employee__pk", flat=True)
                    .distinct()
                )

                for servidor_id in servidor_ids:
                    pass

            except Exception as e:
                log.error(e)

        dt_hr_fim = datetime.now().strftime("%d/%m/%Y %H:%M")
        print(
            f">>> {dt_hr_inicio} - {dt_hr_fim} <<< Finalizando geração de Faltas retroativo. >>>>>>>>>>>>>"
        )
        log.info(
            f">>> {dt_hr_inicio} - {dt_hr_fim} <<< Finalizando geração de Faltas retroativo. >>>>>>>>>>>>>"
        )
