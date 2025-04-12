# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.dayoff.models import Usufruct
from datetime import datetime


log = getLogger("db")


class Command(BaseCommand):
    help = """Script para popular as parcelas dos usufrutos."""

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("athenas")
        self.popular_parcela()

    def popular_parcela(self):
        log.info(
            f'>>> {datetime.now().strftime("%d/%m/%Y %H:%M")} - Iniciando preenchimento do campo numero_parcela dos Usufrutos <<<'
        )

        usufrutos_ids = list(
            Usufruct.objects.filter(
                activity__acquisition_period__group_period__configuration__sub_type_of_usufruct=9001,
            )
            .exclude(status__in=[4096, 2048, 16, 8])  # USUFRUCT_STATUS_CHOICE
            .order_by("start_date")
            .values_list("pk", flat=True)
        )

        for usufruto_id in usufrutos_ids:
            usufruto = Usufruct.objects.get(pk=usufruto_id)
            query = usufruto.acquisition_period.usufructs.exclude(
                status__in=[4096, 2048, 16, 8]  # USUFRUCT_STATUS_CHOICE
            ).order_by("start_date")

            cont_parcela = 1
            for usu in query.all():
                qnt_parcelas = query.exclude(status__in=[16]).count()
                if usu.activity.modifieds.exists():  # Se existe usufruto retificado
                    for usu_alterado in usu.activity.modifieds.all():
                        Usufruct.objects.filter(pk=usu_alterado.pk).update(
                            numero_parcela=None, payment_installments=0
                        )
                        if usu_alterado in query:
                            query = query.exclude(pk=usu_alterado.pk)
                            usufrutos_ids = [
                                id for id in usufrutos_ids if id != usu_alterado.pk
                            ]

                Usufruct.objects.filter(pk=usu.pk).update(
                    numero_parcela=cont_parcela, payment_installments=qnt_parcelas
                )
                usufrutos_ids = [id for id in usufrutos_ids if id != usu.pk]

                cont_parcela += 1

        log.info(
            f'>>> {datetime.now().strftime("%d/%m/%Y %H:%M")} - Finalizando preenchimento do campo numero_parcela dos Usufrutos <<<'
        )
