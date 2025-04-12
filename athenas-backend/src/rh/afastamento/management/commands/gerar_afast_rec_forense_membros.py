# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import Servidor
from rh.dayoff.const import COMP_VACATION_MEMBERS
from rh.dayoff.models import AcquisitionPeriod, GroupPeriod
from rh.afastamento.models import BaseLicencaAfastamento


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá gerar os afastamentos automaticamente baseado no Grupo de Periodo
    criado pela API do comando planotesctl a partir do ano referencia de 2024
    """

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_criar_afastamentos_de_recesso_forense")
        self.gerar_afastamentos()

    def gerar_afastamentos(self):
        grupos = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=COMP_VACATION_MEMBERS,
            year_reference__gte=2024,
        ).values("id", "year_reference")
        log.info(">>> Iniciando criação de Afastamentos >>>>>>>>>>>>>")
        for grupo in grupos:
            servidores = []
            for periodo in AcquisitionPeriod.objects.filter(
                group_period=grupo.get("id")
            ):
                servidor = periodo.employee
                date_start = periodo.attachment_acquisitionperiod.last().date_start
                date_end = periodo.attachment_acquisitionperiod.first().date_start
                antes, depois = self.separar_datas_por_range(
                    date_start, date_end, grupo.get("year_reference")
                )
                if antes:
                    try:
                        afastamento_antes, created_antes = (
                            BaseLicencaAfastamento.objects.get_or_create(
                                situation_unicode="Recesso Forense - Membros",
                                servidor=servidor,
                                data_inicio=antes[0],
                                data_fim=antes[1],
                                data_prevista=antes[1],
                            )
                        )
                        if created_antes:
                            afastamento_antes.tipo = 7
                            afastamento_antes.save()
                            log.info(
                                f">>> Afastamento para servidor: {servidor.matricula} criado >>>>>>>>>>>>>"
                            )
                        else:
                            log.info(
                                f">>> Servidor: {servidor.matricula} ja possuia afastamento criado para este periodo >>>>>>>>>>>>>"
                            )
                        servidores.append(afastamento_antes.servidor.id)
                    except Exception as e:
                        log.info(
                            f">>> Falha ao realizar criação de afastamentos do criterio ANTES: {e} >>>>>>>>>>>>>"
                        )

                try:
                    afastamento_depois, created_depois = (
                        BaseLicencaAfastamento.objects.get_or_create(
                            situation_unicode="Recesso Forense - Membros",
                            servidor=servidor,
                            data_inicio=depois[0],
                            data_fim=depois[1],
                            data_prevista=depois[1],
                        )
                    )
                    if created_depois:
                        afastamento_depois.tipo = 7
                        afastamento_depois.save()
                        log.info(
                            f">>> Afastamento para servidor: {servidor.matricula} criado >>>>>>>>>>>>>"
                        )
                    else:
                        log.info(
                            f">>> Servidor: {servidor.matricula} ja possuia afastamento criado para este periodo >>>>>>>>>>>>>"
                        )
                    servidores.append(afastamento_depois.servidor.id)
                except Exception as e:
                    log.info(
                        f">>> SERVIDOR: {servidor.id} - Falha ao realizar criação de afastamentos do criterio DEPOIS: {e} >>>>>>>>>>>>>"
                    )
            self.gerar_afastamentos_para_servidores_sem_plantao(
                servidores, grupo.get("year_reference")
            )
        log.info(">>> Criação de Afastamentos finalizado >>>>>>>>>>>>>")

    @staticmethod
    def gerar_afastamentos_para_servidores_sem_plantao(
        servidores_com_plantão, ano_referencia
    ):
        log.info(
            ">>> Criação de Afastamentos para servidores sem plantão >>>>>>>>>>>>>"
        )
        servidores = (
            Servidor.objects.filter(ativo=True, type_by_possession="MBR")
            .exclude(id__in=servidores_com_plantão)
            .values_list("id", flat=True)
        )
        log.info(f"servidores - {servidores}")
        dados = {
            "data_inicio": datetime(ano_referencia, 12, 20).date(),
            "data_fim": datetime(ano_referencia + 1, 1, 6).date(),
            "data_prevista": datetime(ano_referencia + 1, 1, 6).date(),
            "tipo": 7,
            "situation_unicode": "Recesso Forense - Membros",
        }
        for servidor in servidores:
            try:
                afastamento, criado = BaseLicencaAfastamento.objects.get_or_create(
                    servidor_id=servidor, **dados
                )
                if criado:
                    afastamento.tipo = 7
                    afastamento.save()
                    log.info(
                        f">>> Afastamento para servidor de id: {servidor} criado >>>>>>>>>>>>>"
                    )
                else:
                    log.info(
                        f">>> Servidor de id: {servidor} ja possuia afastamento criado para este periodo >>>>>>>>>>>>>"
                    )
            except Exception as e:
                log.info(
                    f">>> SERVIDOR de id: {servidor} - Falha ao realizar criação de afastamentos do criterio DEPOIS: {e} >>>>>>>>>>>>>"
                )

    @staticmethod
    def separar_datas_por_range(data_inicio, data_fim, ano_base):

        datas = [
            "20-12",
            "21-12",
            "22-12",
            "23-12",
            "24-12",
            "25-12",
            "26-12",
            "27-12",
            "28-12",
            "29-12",
            "30-12",
            "31-12",
            "01-01",
            "02-01",
            "03-01",
            "04-01",
            "05-01",
            "06-01",
        ]

        datas_datetime = []
        for dia_mes in datas:
            mes = int(dia_mes.split("-")[1])
            if mes == 1:
                data = datetime.strptime(f"{dia_mes}-{ano_base + 1}", "%d-%m-%Y")
            else:
                data = datetime.strptime(f"{dia_mes}-{ano_base}", "%d-%m-%Y")
            datas_datetime.append(data.date())

        if data_fim < data_inicio:
            data_fim = data_fim.replace(year=data_inicio.year + 1)

        antes = [data for data in datas_datetime if data < data_inicio]
        depois = [data for data in datas_datetime if data > data_fim]

        if len(antes) > 1:
            antes = [antes[0], antes[-1]]
        elif len(antes) == 1:
            antes = [antes[0], antes[0]]

        depois = [depois[0], depois[-1]]
        return antes, depois
