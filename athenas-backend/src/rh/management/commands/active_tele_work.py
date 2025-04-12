# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import Configuration, AcquisitionPeriod
from rh.models import MovimentacaoTeletrabalho

log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando verifica diariamente se a data fim do anexo do período aquisitivo é superior a
              data início + dias para prescrição (configuração de usufrutos e folgas), se sim, deve
              alterar o status para Prescrito.
              - Somente executar para anexos vinculados a configuração onde o valor é maior que zero.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def handle(self, *args, **options):
        self.active_tele_work()

    def active_tele_work(self):
        self.conf()
        date = datetime.now()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando alteração do status dos Planos de Teletrabalho >>>>>>>>>>>>>"
        )
        try:
            year = date.year
            month = date.month
            mov_teles = MovimentacaoTeletrabalho.objects.filter(
                Q(
                    Q(data_inicio__month__lte=int(month), data_inicio__year=int(year))
                    | Q(data_inicio__year__lt=int(year))
                )
                & Q(
                    Q(
                        Q(data_fim__month__gt=int(month), data_fim__year=int(year))
                        | Q(data_fim__year__gt=int(year))
                    )
                    | Q(data_fim__isnull=True)
                )
            )
            for tele in mov_teles:
                tele.ativo = True
                tele.save()
                print(
                    f">>> >>> Plano de Teletrabalho: {tele} :: Ativo alterado para True >>>>>>>>>>>>>"
                )

        except Exception as err:
            log.info(err)
            print(err)
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Finalizando alteração do status dos Planos de Teletrabalho >>>>>>>>>>>>>"
        )
