# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from dateutil.relativedelta import relativedelta
from optparse import make_option
from datetime import datetime
from common.siatu.models import Chamado, Status
from standard.models import Configuration
from contrib.middleware import StartupLoader
from contrib.utils import DateUtils
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger


log = getLogger("db")

StartupLoader().doLoad()


class Command(BaseCommand):
    verbose = "False"
    help = """
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-u", "--update", action="store_true", dest="update", help="Atualiza!"
        ),
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            help="Realiza todas as ações!",
        ),

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        if options["update"] or options["all"]:
            self.set_user_to_job("job_siatuctl_verify_pendency")
            self.verify_pendency()

    def verify_pendency(self):
        """ """
        # print u">>> [%s] INICIANDO VERIFICAÇÃO DE PENDENCIAS EM SIATU >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M")
        try:
            conf = Configuration.objects.get(application="siatu")
            dias_avaliacao = int(conf.itens.get(key="max_dias_avaliacao").value)
            for c in Chamado.objects.filter(status_atual__status__in=[4]):
                if (
                    c.status_atual.status == 4
                    and c.status_atual.data_inicio + relativedelta(days=dias_avaliacao)
                    < datetime.now()
                    and not c.cancelado
                ):
                    print(
                        ">> Alterando Chamado: %s criado em: %s"
                        % (
                            c.cache_numero,
                            DateUtils.date_to_str(c.status_atual.data_inicio),
                        )
                    )
                    # CRIA O STATUS
                    s = Status(
                        status=Status.NAOAVALIADO, data_inicio=datetime.now(), chamado=c
                    )
                    s.save()
        except Exception as e:
            log.info(str(e))
        # print u">>>>>>>> [%s] FINALIZANDO VERIFICAÇÃO DE PENDENCIAS EM SIATU <<<<<<" % datetime.now().strftime("%d/%m/%Y %H:%M")
