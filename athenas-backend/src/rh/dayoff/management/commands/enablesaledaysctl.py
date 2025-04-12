# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.models import Configuration
import datetime
from django.db.models import Q


log = getLogger(__name__)


class Command(BaseCommand):
    verbose = "False"
    help = """Este comando irá habilitar e desabilitar a venda de dias de acordo com a configuração vigente
     - Executado diariamente
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def activate_athenas_user(self):
        try:
            user = User.objects.get(
                username="job_enablesaledaysctl_enable_or_disable_sale_days"
            )
        except User.DoesNotExist as e:
            log.error(
                f'Não foi localizado o usuário "job_enablesaledaysctl_enable_or_disable_sale_days" {e}'
            )
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.enable_or_disable_sale_days()

    def enable_or_disable_sale_days(self):
        self.activate_athenas_user()
        date = datetime.date.today()
        print(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando verificação de venda de dias >>>>>>>>>>>>>"
        )
        try:
            for config in Configuration.objects.all():
                for config_sale in config.configuration_sale.all():
                    if (
                        config_sale.end_date_sale
                        and date >= config_sale.start_date_sale
                        and date <= config_sale.end_date_sale
                    ) or (
                        not config_sale.end_date_sale
                        and date >= config_sale.start_date_sale
                    ):
                        config.sell_booked_days = True
                    else:
                        config.sell_booked_days = False
                    config.save()

        except Exception as err:
            log.info(err)
            print(err)

        print(
            ">>> [%s] Finalizando verificação de venda de dias >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
