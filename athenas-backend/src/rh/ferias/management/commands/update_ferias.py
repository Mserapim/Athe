# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.afastamento.models import CANCELED, FeriasAfastamento
from rh.ferias.models import (
    PAS_ALIBERACAO,
    PAS_FRUIDA,
    PAS_INDENIZADA,
    PASU_ALTERADO,
    PASU_AUTORIZADO_CI,
    PASU_EMALTERACAO,
    PASU_FRUIDO,
    PASU_FRUINDO,
    PASU_HOMOLOGADO,
    PASU_INTERROMPIDO,
    PASU_NAOAUTORIZADO,
    PASU_SUBSTITUTO,
    PASU_SUSPENSO,
    PeriodoAquisitivo,
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorUsufruto,
    PAS_EMANDAMENTO,
)
from rh.models import Servidor
from rh.utils import send_mail_and_notify

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá executar todas as rotinas de atualização do sistema de Férias.
    Todos os usufrutos - PASU - serão analisados e terão seu @estado atualizado de acordo com a situação real, ou seja,
    FRUINDO, FRUÍDO, etc. Caso seja atualizado algum usufruto, o PAS correspodente será analisado e atualizado
    seu @estado caso necessite
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--pasus",
            action="store_true",
            dest="pasus",
            help="Atualiza as parcelas!",
        )
        parser.add_argument(
            "-p",
            "--pas",
            action="store_true",
            dest="pas",
            help="Atualiza os Períodos dos Servidores/Membros - PAS",
        )
        parser.add_argument(
            "-l",
            "--liberacao",
            action="store_true",
            dest="liberacao",
            help="Verifica e libera um período para marcação, caso tenha passado do dia para início da marcação",
        )
        parser.add_argument(
            "-n",
            "--notify",
            action="store_true",
            dest="notify",
            help="Notifica os servidoes que irão fruir férias em XX dias.",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            help="Realiza todas as atualizações!",
        )
        parser.add_argument(
            "-c",
            "--create",
            action="store_true",
            dest="create",
            help="Tenta criar afastamentos de férias não criados!",
        )
        parser.add_argument(
            "-b",
            "--atualiza-periodo-aquisitivo",
            action="store_true",
            dest="atualiza-periodo-aquisitivo",
            help="Atualiza os Estados dos Períodos dos Servidores/Membros",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        if options["pasus"] or options["all"]:
            self.atualiza_PASUs()
        if options["pas"] or options["all"]:
            self.atualiza_PASs()
        if options["liberacao"] or options["all"]:
            self.liberar_PAs()
        if options["notify"] or options["all"]:
            self.notify_usufruto([30, 7, 1])
        if options["create"] or options["all"]:
            self.create_vacation_departure()
        if options["atualiza-periodo-aquisitivo"] or options["all"]:
            self.update_acquisition_period()

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def atualiza_PASUs(self):
        self.conf()
        try:
            user = User.objects.get(username="job_update_ferias_atualiza_pasus")
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_atualiza_pass" {e}'
            )
        else:
            set_current_user(user)
        date = datetime.now()
        print(
            (
                ">>> [%s] Iniciando atualizacao automatica dos PASUs >>>>>>>>>>>>>"
                % DateUtils.datetime_to_str(date)
            ).encode("utf-8")
        )
        for pas in PeriodoAquisitivoServidor.objects.exclude(
            estado__in=[
                PAS_ALIBERACAO,
                PAS_FRUIDA,
            ]
        ):
            for pasu in pas.usufrutos.exclude(
                estado__in=[
                    PASU_AUTORIZADO_CI,
                    PASU_EMALTERACAO,
                    PASU_ALTERADO,
                    PASU_INTERROMPIDO,
                    PASU_SUSPENSO,
                    PASU_FRUIDO,
                    PASU_NAOAUTORIZADO,
                    PASU_SUBSTITUTO,
                ]
            ):
                if pasu.data_fim < date.date() and pasu.estado != PASU_FRUIDO:
                    # estado = pasu.estado
                    try:
                        pasu.transicao("finalizar", PASU_FRUIDO)
                        print(
                            (
                                "ALTERADO PARA FRUIDO: %s >> %s"
                                % (pas, DateUtils.date_to_str(pasu.data_fim))
                            ).encode("utf-8")
                        )
                    except Exception as err:
                        print(("ERRO (%s):" % pas).encode("utf-8"))
                        print(("%s" % err).encode("utf-8"))
                elif pasu.data_inicio <= date.date() and pasu.estado != PASU_FRUINDO:
                    try:
                        pasu.transicao("fruir", PASU_FRUINDO)
                        print(
                            (
                                "ALTERADO PARA FRUINDO: %s >> %s"
                                % (pas, DateUtils.date_to_str(pasu.data_inicio))
                            ).encode("utf-8")
                        )
                    except Exception as err:
                        print(("ERRO (%s):" % pas).encode("utf-8"))
                        print(("%s" % err).encode("utf-8"))
            pas.atualiza_estado(False)
        print(
            (
                ">>> [%s] Finalizando atualizacao automatica dos PASUs >>>>>>>>>>>>>"
                % DateUtils.datetime_to_str(date)
            ).encode("utf-8")
        )

    def atualiza_PASs(self):
        self.conf()
        try:
            user = User.objects.get(username="job_update_ferias_atualiza_pass")
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_atualiza_pass" {e}'
            )
        else:
            set_current_user(user)
        date = datetime.now()
        log.debug(
            ">>> [%s] Iniciando atualizacao automatica dos PASs >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        print(
            (
                ">>> [%s] Iniciando atualizacao automatica dos PASs >>>>>>>>>>>>>"
                % DateUtils.datetime_to_str(date)
            ).encode("utf-8")
        )
        for pa in PeriodoAquisitivo.objects.all():
            pa.save()
        log.debug(
            ">>> [%s] Finalizando atualizacao automatica dos PASs >>>>>>>>>>>>>"
            % (DateUtils.datetime_to_str(date))
        )
        print(
            (
                ">>> [%s] Finalizando atualizacao automatica dos PASs >>>>>>>>>>>>>"
                % DateUtils.datetime_to_str(date)
            ).encode("utf-8")
        )

    def update_acquisition_period(self):
        self.conf()
        try:
            user = User.objects.get(
                username="job_update_ferias_update_acquisition_period"
            )
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_atualiza_pass" {e}'
            )
        else:
            set_current_user(user)
        date = datetime.now()
        log.debug(
            ">>> [%s] Iniciando atualização de Estado do PAS >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        print(
            ">>> [%s] Iniciando atualização de Estado do PAS >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
        count = 0
        for pas in PeriodoAquisitivoServidor.objects.all():
            if (
                pas.estado == PAS_EMANDAMENTO
                and (pas.dias_usufruidos + pas.paid_days) == pas.quantidade_dias
            ):
                count += 1
                print(
                    f"dias_usufruidos({pas.dias_usufruidos}) + ({pas.paid_days})paid_days = {pas.dias_usufruidos + pas.paid_days} | quantidade_dias({pas.quantidade_dias})"
                )
                status_display = pas.get_estado_display()
                pas.transicao("finalizar", PAS_FRUIDA)
                print(
                    f">>> [{DateUtils.datetime_to_str(date)}] Atualizando {pas} | {status_display} {pas.get_estado_display()}>>>>>>>>>>>>>"
                )
        print(f"Total modificado de Em andamento para Concluído ({count})")
        log.debug(
            ">>> [%s] Finalizando atualização de Estado do PAS >>>>>>>>>>>>>"
            % (DateUtils.datetime_to_str(date))
        )
        print(
            ">>> [%s] Finalizando atualização de Estado do PAS >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )

    def liberar_PAs(self):
        self.conf()
        try:
            user = User.objects.get(username="job_update_ferias_liberar_pass")
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_liberar_pass" {e}'
            )
        else:
            set_current_user(user)
        date_time = datetime.now()
        for pa in PeriodoAquisitivo.objects.all():
            if not pa.periodo_anterior and (pa.data_inicio_prev <= date_time.date()):
                print(
                    (
                        ">>> [%s] Iniciando liberacao atualizacao automatica do PA (%s) >>>>>>>>>>>>>"
                        % (DateUtils.datetime_to_str(date_time), pa)
                    ).encode("utf-8")
                )
                for pas in pa.paservidores.filter(estado=PAS_ALIBERACAO):
                    pas._liberar()
                print(
                    (
                        ">>> [%s] Finalizando liberacao atualizacao automatica do PA (%s) >>>>>>>>>>>>>"
                        % (DateUtils.datetime_to_str(date_time), pa)
                    ).encode("utf-8")
                )

    def notify_usufruto(self, list_days=[]):
        self.conf()
        try:
            user = User.objects.get(username="job_update_ferias_notify_usufruto")
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_notify_usufruto" {e}'
            )
        else:
            set_current_user(user)
        date = datetime.now()
        dates = [date.date() + relativedelta(days=days) for days in list_days]
        dates_unicode = [
            DateUtils.date_to_str(date.date() + relativedelta(days=days))
            for days in list_days
        ]
        log.info(
            ">>> [%s] Iniciando notificacao de fruicao de ferias >>>>>>>>>>>>> %s"
            % (DateUtils.datetime_to_str(date), dates_unicode)
        )
        print(
            (
                ">>> [%s] Iniciando notificacao de fruicao de ferias >>>>>>>>>>>>> %s"
                % (DateUtils.datetime_to_str(date), dates_unicode)
            ).encode("utf-8")
        )
        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(estado=4).filter(
            data_inicio__in=dates
        ):
            log.info("%s: %s" % ((pasu.data_inicio - date.date()).days, pasu))
            Notification.notify(
                "FRS_FRUICAO",
                pasu.pas.servidor,
                None,
                pa=pasu.pas.periodo_aquisitivo,
                data_inicio=DateUtils.date_to_str(pasu.data_inicio),
                dias=(pasu.data_inicio - date.date()).days,
            )
        log.info(
            ">>> [%s] Finalizando notificacao de fruicao de ferias >>>>>>>>>>>>>"
            % (DateUtils.datetime_to_str(date))
        )
        print(
            (
                ">>> [%s] Finalizando notificacao de fruicao de ferias >>>>>>>>>>>>>"
                % (DateUtils.datetime_to_str(date))
            ).encode("utf-8")
        )

    def create_vacation_departure(self):
        print(">>> Iniciando tentativa de criacao de afastamento de ferias pendentes.")
        log.info(
            ">>> Iniciando tentativa de criacao de afastamento de ferias pendentes."
        )
        self.conf()
        try:
            user = User.objects.get(
                username="job_update_ferias_create_vacation_departure"
            )
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_update_ferias_create_vacation_departure" {e}'
            )
        else:
            set_current_user(user)
        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
            estado__in=[PASU_HOMOLOGADO, PASU_FRUINDO, PASU_FRUIDO],
            periodo_aquisitivo_servidor__servidor__tipo="M",
            data_inicio__gte=datetime.now().date(),
        ).order_by("data_inicio"):
            vacation_departure = FeriasAfastamento.objects.filter(
                servidor=pasu.periodo_aquisitivo_servidor.servidor,
                data_inicio=pasu.data_inicio,
                data_prevista=pasu.data_prevista_fim,
            ).exclude(estado=CANCELED)
            if not vacation_departure.exists():
                log.info(
                    "%s - %s - %s"
                    % (
                        pasu,
                        pasu.get_estado_display(),
                        pasu.periodo_aquisitivo_servidor.servidor,
                    )
                )
                print(
                    (
                        "%s - %s - %s"
                        % (
                            pasu,
                            pasu.get_estado_display(),
                            pasu.periodo_aquisitivo_servidor.servidor,
                        )
                    ).encode("utf-8")
                )
                try:
                    FeriasAfastamento(
                        servidor=pasu.periodo_aquisitivo_servidor.servidor,
                        data_inicio=pasu.data_inicio,
                        data_prevista=pasu.data_prevista_fim,
                        data_fim=pasu.data_prevista_fim,
                        publicacao_movimentacao=None,
                    ).validate()
                    pasu.save()
                except Exception as err:
                    log.exception(err)
                    send_mail_and_notify(
                        source="Erro ao lancar afastamento de férias.",
                        message="Erro ao lancar afastamento de férias. %s" % err,
                        err="%s" % err,
                        employee=Servidor.objects.filter(
                            user__groups__name__icontains="expediente-afastamento"
                        ).distinct(),
                    )
                print("-----------------------------")
