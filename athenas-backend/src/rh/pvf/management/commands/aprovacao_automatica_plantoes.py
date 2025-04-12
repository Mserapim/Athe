# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from engine.mq.models import Task
from rh.dayoff.models import ConfigurationSale
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import DateUtils, getLogger
from rh.pvf.models import USUFRUTO_PLANTAO_COMPENSATORIAS
from rh.pvf.tasks import efetivar_indeferir_venda_plantoes

log = getLogger("db")


class Command(BaseCommand):
    help = """Esse Comando vai  rodar após a data de fechamento da janela da venda de plantões, 
    será executado um JOB para efetivar ou indeferir as solicitações. """

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_efetivar_solicitacoes_automatico")
        self.efetivar_indeferir_automatico()

    def efetivar_indeferir_automatico(self):
        date = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando efetivação automática >>>>>>>>>>>>>"
        )

        data_atual = datetime.today().date()

        if not ConfigurationSale.objects.filter(
            end_date_sale__gte=data_atual,
            configuration__sub_type_of_usufruct__in=USUFRUTO_PLANTAO_COMPENSATORIAS,
        ).exists():
            Task.start(
                efetivar_indeferir_venda_plantoes,
                user=get_current_user().pk,
            )

        log.info(
            ">>> [%s] Finalizando efetivação automática >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
