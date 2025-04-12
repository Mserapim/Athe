# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from contrib.utils import getLogger
from rh.ponto.models import Falta

from contrib.middleware import set_current_user
from django.contrib.auth.models import User

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá executar todas as rotinas de notificações do estágio probatório.
    Assim que for liberada uma avaliação, será notificado o chefe imediato do servidor para que este
    possa realiza-la.
    Sera verificado ainda se há alguma licenca/afastamento iniciando-se, caso encontre verifica se esta interrompe o estagio,
    fazendo as devidas alterações do periodo da etapa.
    """

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        if options["all"]:
            self.remove_faltas_zeradas()

    def remove_faltas_zeradas(self):
        """ """
        try:
            user = User.objects.get(username="job_pontoctl_remove_faltas_zeradas")
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_pontoctl_remove_faltas_zeradas" - {e}'
            )
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)
        # print u">>> [%s] Iniciando remoção de faltas zeradas >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(u">>> [%s] Iniciando remoção de faltas zeradas >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M"))
        try:

            if Falta.objects.filter(
                injustificada=0,
                justificada=0,
                excedente=0,
                horas_positivas=0,
                horas_negativas=0,
            ).exists():
                for f in Falta.objects.filter(
                    injustificada=0,
                    justificada=0,
                    excedente=0,
                    horas_positivas=0,
                    horas_negativas=0,
                ):
                    f.delete()
                # Falta.objects.filter(injustificada=0, justificada=0, excedente=0).delete()

        except Exception as e:
            log.info(e)
        # print u">>> [%s] Iniciando remoção de faltas zeradas >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(u">>> [%s] Iniciando remoção de faltas zeradas >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M"))
