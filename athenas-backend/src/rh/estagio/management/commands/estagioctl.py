# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from contrib.utils import getLogger
from rh.estagio.models import EstagioProbatorioServidor

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
            self.set_user_to_job(
                "job_estagioctl_atualiza_estagio_verificando_afastamentos"
            )
            self.atualiza_estagio_verificando_afastamentos()
        if options["notify"] or options["all"]:
            self.set_user_to_job("job_estagioctl_notify_liberacao")
            self.notify_liberacao()

    def atualiza_estagio_verificando_afastamentos(self):
        """
        Verifica se há afastamentos com status ATIVO ou ENCERRADO, caso encontre e este esteja dentro
        da etapa de avaliação de um estagio, verifica quantos dias pra cada licença e soma os dias e adiciona
        esses dias prolongando o final da etapa de avaliação.
        """

        # print " ==== Rodando atualização de Estágio Probatório em: [%s]" % datetime.now()
        # print ">>> [%s] Iniciando atualizacao automatica dos estágios >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(">>> [%s] Iniciando atualizacao automatica dos estágios >>>>>>>>>>>>>" % datetime.now().strftime("%d/%m/%Y %H:%M"))
        try:

            for estagio_servidor in EstagioProbatorioServidor.objects.filter(status=1):
                estagio_servidor.calcula_suspensao_afastamentos_cron()

        except Exception as e:
            log.info(e)
        # print ">>>>>>>> [%s] Finalizando atualizacao automatica dos estágios <<<<<<" % datetime.now().strftime("%d/%m/%Y %H:%M")
        # log.info(">>>>> [%s] Finalizando atualizacao automatica dos estágios <<<<<<" % datetime.now().strftime("%d/%m/%Y %H:%M"))

    def notify_liberacao(self):
        """
        Verifica se há alguma avaliação a ser liberada, caso encontre notifica o chefe imediato
        do servidor que a avaliação está liberada.
        """
        # log.info(">>> [%s] Iniciando notificação de avaliação de estágio liberada <<<" % (datetime.now().strftime("%d/%m/%Y %H:%M")))
        # print ">>>>>>>>>>>> [%s] Iniciando notificação de avaliação de estágio liberada <<<" % (datetime.now().strftime("%d/%m/%Y %H:%M"))
        for avaliacao in EstagioProbatorioServidor.objects.filter(
            status=1, bloqueada=False
        ):
            chefe = (
                avaliacao.posse_servidor.servidor.chefe_imediato
                if avaliacao.posse_servidor.servidor.chefe_imediato
                else avaliacao.posse_servidor.servidor._chefe_imediato
            )
            if avaliacao._liberada():
                avaliacao.notifica_avaliacao_liberada(chefe)
                # print "Notificando %s: sobre avaliação de: %s" % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                log.info(
                    "Notificando %s: sobre avaliação de: %s"
                    % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                )

            if avaliacao._liberada_dia():
                avaliacao.notifica_avaliacao_liberada(chefe)
                # print "Notificando %s: sobre avaliação de: %s" % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                log.info(
                    "Notificando %s: sobre avaliação de: %s"
                    % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                )

            if avaliacao._atrasada():
                avaliacao.notifica_avaliacao_atrasada(chefe)
                # print "Notificando %s: sobre avaliação atrasada de: %s" % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                log.info(
                    "Notificando %s: sobre avaliação atrasada de: %s"
                    % (chefe, avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                )

            if avaliacao._manifestacao_atrasada():
                avaliacao.notifica_manifestacao_atrasada()
                # print "Notificando %s: sobre manifestação atrasada." % (avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                log.info(
                    "Notificando %s: sobre manifestação atrasada."
                    % (avaliacao.posse_servidor.servidor.pessoa_fisica.nome)
                )

        # log.info(">>>>>>>>> [%s] Finalizando notificação de avaliação de estágio liberada <<<<<<<<<" % (
        #   datetime.now().strftime("%d/%m/%Y %H:%M")))
        # print ">>>>>>>> [%s] Finalizando notificação de avaliação de estágio liberada <<<<<<<<" % (
        #   datetime.now().strftime("%d/%m/%Y %H:%M"))
