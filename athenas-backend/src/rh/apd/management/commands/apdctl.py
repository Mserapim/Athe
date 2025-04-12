# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from contrib.utils import getLogger
from rh.apd.models import PeriodicEvaluationPerformance
from contrib.middleware import set_current_user
import datetime

log = getLogger(__name__)


class Command(BaseCommand):

    verbose = "False"
    help = """Este comando irá executar todas as rotinas de notificações do sistema da APD.
    Assim que for liberada uma avaliação, será notificado o chefe imediato do servidor para que este
    possa realiza-la.
    Sera verificado ainda se há alguma licenca/afastamento iniciando-se, caso encontre verifica se esta prorroga a APD,
    fazendo as devidas alterações do periodo da etapa.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            dest="update",
            help="Atualiza as etapas!",
        )
        parser.add_argument(
            "-n",
            "--notify",
            action="store_true",
            dest="notify",
            help="Notifica os chefes!",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            help="Realiza todas as ações!",
        )
        parser.add_argument(
            "-as",
            "--autoscience",
            action="store_true",
            dest="autoscience",
            help="Ciencia automática para APD do mês corrente!",
        )

    def __init__(self, *args, **kargs):
        self.log = getLogger(self.__class__.__name__)
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["update"] or options["all"]:
            self.atualiza_estagio_verificando_afastamentos()
        if options["notify"] or options["all"]:
            self.notify_released()
        if options["autoscience"]:
            self.automatic_science()

    def atualiza_estagio_verificando_afastamentos(self):
        """
        Verifica se há afastamentos com status ATIVO ou ENCERRADO, caso encontre e este esteja dentro da etapa da apd,
        verifica quantos dias pra cada licença e soma os dias e adiciona esses dias prolongando o final da etapa de avaliação.
        """
        pass
        # print " ==== Rodando atualização de Estágio Probatório em: [%s]" % datetime.now()
        # print ">>> [%s] Iniciando atualizacao automatica dos estágios >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(">>> [%s] Iniciando atualizacao automatica dos estágios >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M"))
        # try:

        #     for estagio_servidor in EstagioProbatorioServidor.objects.filter(status=1):
        #         estagio_servidor.calcula_suspensao_afastamentos_cron()

        # except Exception, e:
        #     log.info(e)
        # print ">>>>>>>> [%s] Finalizando atualizacao automatica dos estágios <<<<<<" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(">>>>> [%s] Finalizando atualizacao automatica dos estágios <<<<<<" % datetime.now().strftime("%d/%m/%Y %H:%M"))

    def notify_released(self):
        """
        Verifica se há alguma apd a ser liberada, caso encontre notifica o chefe imediato do servidor que a avaliação está liberada.
        """
        for apd in PeriodicEvaluationPerformance.objects.filter(status=1):

            boss = (
                apd.employee.servidor.chefe_imediato
                if apd.employee.servidor.chefe_imediato
                else apd.employee.servidor._chefe_imediato
            )
            if (
                apd.deadline == 1
                and not apd.evaluation_apd.exists()
                and not apd._released()
            ):
                log.info("Servidor: %s" % apd.employee.servidor)
                apd.notify_released_evaluation(boss)
                log.info(
                    "Notificando %s: sobre avaliação de: %s"
                    % (boss, apd.employee.servidor.pessoa_fisica.nome)
                )

            if apd.deadline == 2 and not apd.evaluation_apd.exists():
                apd.notify_delayed_evaluation(boss)
                # print "Notificando %s: sobre avaliação atrasada de: %s" % (boss, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                log.info(
                    "Notificando %s: sobre avaliação atrasada de: %s"
                    % (boss, apd.employee.servidor.pessoa_fisica.nome)
                )

    def automatic_science(self):
        """
        Realiza manifestação automatica após o dia 15 de cada mês.
        """
        set_current_user("athenas")
        today = datetime.datetime.now()
        if today.day > 15:
            for apd in PeriodicEvaluationPerformance.objects.filter(
                status=1, end_date__year=today.year, end_date__month=today.month
            ):
                apd.automatic_manifestation_science()
