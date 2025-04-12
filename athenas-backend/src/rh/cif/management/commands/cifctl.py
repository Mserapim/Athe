# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from django.core.management.base import BaseCommand

from contrib.utils import getLogger
from rh.cif.models import ControlInformationMember

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-u", "--update", action="store_true", dest="update", help="Atualiza!"
        )
        parser.add_argument(
            "-n", "--notify", action="store_true", dest="notify", help="Notifica!"
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            help="Realiza todas as ações!",
        )

    def __init__(self, *args, **kargs):
        self.log = getLogger(self.__class__.__name__)
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
            self.set_user_to_job("job_cifctl_verify_pendency")
            self.verify_pendency()
        if options["notify"] or options["all"]:
            self.set_user_to_job("job_cifctl_notify")
            self.notify()

    def verify_pendency(self):
        """ """
        # print ">>> [%s] INICIANDO VERIFICAÇÃO DE PENDENCIAS EM CONTROLE DE INFORMAÇÕES MEMBROS >>>>>>>>>>>>>" % datetime.now()
        try:
            for con in ControlInformationMember.objects.filter(status=1):
                # print con
                con.pendency_teaching = False
                if con.get_pendendy_teaching():
                    con.pendency_teaching = True

                if not con.teaching.exists():
                    con.pendency_teaching = True

                con.pendency_address = False
                if con.get_pendency_address():
                    con.pendency_address = True

                if not con.address.exists():
                    con.pendency_address = True

                con.pendency_property = False
                if con.get_pendency_property():
                    con.pendency_property = True

                if not con.property.exists():
                    con.pendency_property = True

                con.pendency_debts = False
                if con.get_pendency_debts():
                    con.pendency_debts = True

                if not con.debtsencumbrances.exists():
                    con.pendency_debts = True

                con.save()
        except Exception as err:
            log.error(err)
            print(err)
        # print ">>>>>>>> [%s] FINALIZANDO VERIFICAÇÃO DE PENDENCIAS EM CONTROLE DE INFORMAÇÕES MEMBROS <<<<<<" % datetime.now()

    def notify(self):
        """
        NOTIFICAR VENCIMENTO DE UM PERÍODO DE INFORMAÇÃO SEM A PRESTAÇÃO DA DEVIDA INFORMAÇÃO
        """
        pass
