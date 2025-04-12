# -*- coding: utf-8 -*-
import inspect

from datetime import datetime, timedelta, date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.dayoff.const import COMP_CLEARANCE_MEMBERS, COMP_VACATION_MEMBERS
from rh.dayoff.models import (
    AcquisitionPeriod,
    AcquisitionPeriodAttachment,
    Configuration,
    GroupPeriod,
)
from rh.models import Servidor
from rh.plantoes.management.utils import dias_plantoes, get_api_plantoes_membros
from rh.pvf.const import MAX_SALDO_FOLGA_PLANTAO, TIPO_PLANTAO_JUIZADO_TORCEDOR
from standard.models import Choice


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá buscar os plantões na base de dados do Protheus,
    importando o saldo de plantões para o anexo do Período Aquisitivo correspondente
    """

    def handle(self, *args, **options):
        self.conf()
        self.create_attachment_on_duty()

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def create_attachment_on_duty(self):
        """
        Função responsável por importar os dados de Plantões de Membros e criar anexos de Períodos Aquisitivos
        relativo a quantidade de dias adquiridos.
        """
        max_days_for_year = Choice.objects.get(
            app_label="plantoes", name="PLANTOES_MAX_DAYS_GET_COMP_CLEARANCE_MEMBERS"
        )
        deadline_choice = Choice.objects.get(
            app_label="plantoes", name="PLANTOES_DEADLINE_DAYS_FOR_IMPORT"
        )
        configuration_days_limit = [
            x.value
            for x in Choice.objects.filter(
                app_label="plantoes",
                name="PLANTOES_CONFIGURATION_DAYS_LIMIT",
                active=True,
            )
        ]
        multiplier_number_member_plantao = 1.5

        now = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(now)}] Iniciando criação de Anexo de Períodos Aquisitivos de Plantões de Membros >>>>>>>>>>>>>"
        )

        date_deadline_initial = now - timedelta(days=deadline_choice.value + 7)
        date_deadline_final = now - timedelta(days=deadline_choice.value)

        plantoes = get_api_plantoes_membros(
            date_deadline_initial.date(), date_deadline_final.date()
        )

        log.info(f"Plantões a serem importados em {now} - total de {len(plantoes)}")
        for plantao in plantoes:
            log.info(plantao)

            non_days = dias_plantoes(plantao.get("de"), plantao.get("ate"))
            employee = Servidor.objects.filter(
                matricula=plantao.get("servidor_id")
            ).first()

            for day in range(non_days[0]):
                days_total = 0
                repr_day = non_days[1][day]
                str_day = repr_day.strftime("%d/%m/%Y")
                date_day = (
                    repr_day.date() if isinstance(repr_day, datetime) else repr_day
                )

                acq_periods = AcquisitionPeriod.objects.filter(
                    group_period__year_reference=date_day.year,
                    group_period__configuration__sub_type_of_usufruct=get_sub_tipo_de_usufruto(
                        repr_day
                    ),
                    group_period__configuration__pk__in=configuration_days_limit,
                    employee=employee,
                )

                if acq_periods.exists():
                    acquisition_period = acq_periods.last()
                    for acq_period in acq_periods:
                        days_total += acq_period.days

                else:
                    try:
                        start_date = date(date_day.year, 1, 1)
                        group_period, created = GroupPeriod.objects.get_or_create(
                            period=1,
                            year_reference=date_day.year,
                            configuration=Configuration.objects.filter(
                                sub_type_of_usufruct=get_sub_tipo_de_usufruto(repr_day)
                            ).first(),
                            defaults={
                                "title": (
                                    "PLANTÃO DE RECESSO FORENSE - MEMBROS"
                                    if get_sub_tipo_de_usufruto(repr_day)
                                    == COMP_VACATION_MEMBERS
                                    else "FOLGA COMPENSATORIA DE MEMBROS"
                                ),
                                "end_date_book": None,
                                "start_date_book": start_date,
                                "start_date_fruition": start_date,
                                "homologation_date": start_date,
                                "publication_date": start_date,
                                "blocked": True,
                            },
                        )
                        acquisition_period, created = (
                            AcquisitionPeriod.objects.get_or_create(
                                status=2,
                                group_period=group_period,
                                employee=employee,
                                paid_without_payroll=False,
                                indemnified=False,
                                note=False,
                                pendency=False,
                                continuous_period=False,
                                blocked=False,
                                automatic_created=False,
                                start_date_acquisition=start_date,
                                end_date_acquisition=(
                                    (start_date + timedelta(days=365))
                                    if isinstance(
                                        (start_date + timedelta(days=365)), date
                                    )
                                    else (start_date + timedelta(days=365)).date()
                                ),
                                defaults={
                                    "real_days_cache": 0,
                                    # 'start_date_acquisition': start_date,
                                    # 'end_date_acquisition': (start_date + timedelta(days=365)).date(),
                                    "days_to_enjoy_cache": 0,
                                    "days_not_booked_cache": 0,
                                    "days": 0,
                                    "suspended_days": 0,
                                    "paid_days_cache": 0,
                                },
                            )
                        )
                    except Exception as e:
                        log.error(f"Erro ao gerar o Grupo/Período Aquisitivo: {e}")

                days_law = 0
                if days_total < int(max_days_for_year.value + 0.5):
                    days_law = 1
                    if plantao.get("grupo_id") in [10013, 10014]:
                        days_law = 1 * multiplier_number_member_plantao

                days_law = get_dias_saldo_anexo(acquisition_period, days_law, date_day)

                try:
                    describe = f'Referente periodo de plantão ({plantao.get("de")} - {plantao.get("ate")})'

                    if days_law != 0:
                        attachment, created_attachment = (
                            AcquisitionPeriodAttachment.objects.update_or_create(
                                acquisition_period=acquisition_period,
                                date_start=date_day,
                                date_end=date_day,
                                defaults={
                                    "description": describe,
                                    "days_law": days_law,
                                    "information": f"Gerado a partir do sistema de plantões em {now}",
                                    "status": 1,
                                },
                            )
                        )
                        attachment.days_law = days_law
                        attachment.save()

                    else:
                        attachment, created_attachment = (
                            AcquisitionPeriodAttachment.objects.get_or_create(
                                acquisition_period=acquisition_period,
                                date_start=date_day,
                                date_end=date_day,
                                defaults={
                                    "description": describe,
                                    "information": f"Gerado a partir do sistema de plantões em {now}",
                                    "status": 1,
                                    "days_law": days_law,
                                },
                            )
                        )

                    if created_attachment:
                        if days_law:
                            log.info(
                                f"--> Criado o anexo {attachment} para o servidor: {employee} referente ao dia {str_day} "
                            )
                            days_total += 1
                        else:

                            log.info(
                                f"""
                                O servidor: {employee} atingiu o número máximo de {days_total} dias de Folga Compensatória por ano,
                                portanto, não foi gerado anexo para o dia {str_day}.
                            """
                            )

                    else:
                        log.info(
                            f"--> Não foi criado o anexo {attachment} para o servidor: {employee} referente ao dia {str_day} "
                        )

                except Exception as e:
                    log.error(
                        f"Erro ao gerar o anexo para o servidor: {employee}, referente ao dia {str_day} -{e}"
                    )

        dt_hr_fim = datetime.now()
        log.info(
            ">>> [%s] Finalizando a criação de Anexo de Períodos Aquisitivos de Plantões de Membros >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(dt_hr_fim)
        )


def get_dias_saldo_anexo(acquisition_period, dias_saldo, data_plantao):
    """
    Função que retorna o total de dias que será adicionado ao anexo
    Args:
        acquisition_period:(objeto)
        dias_saldo:(int)
        data_plantao:(date)
    Returns:
        dias_saldo:int
    """
    servidor = acquisition_period.employee
    total_periodo = (
        get_total_folga_juizado_torcedor(data_plantao, servidor)
        + acquisition_period.days
    )
    if total_periodo >= MAX_SALDO_FOLGA_PLANTAO:
        return 0
    elif (total_periodo + dias_saldo) > MAX_SALDO_FOLGA_PLANTAO:
        return MAX_SALDO_FOLGA_PLANTAO - total_periodo
    else:
        return dias_saldo


def get_total_folga_juizado_torcedor(data_plantao, servidor):
    """
    Função que retorna o total de dias do período aquisitivo de folga juizado de torcedor
    Args:
        data_plantao:(date)
        servidor:(objeto)
    Returns:
       saldo:int
    """
    ano_referencia = data_plantao.year
    peridodo_aquisitivo = AcquisitionPeriod.objects.filter(
        group_period__configuration__sub_type_of_usufruct=get_sub_tipo_de_usufruto(
            data_plantao
        ),
        group_period__year_reference=ano_referencia,
        employee=servidor,
        group_period__configuration__type_of_duty=TIPO_PLANTAO_JUIZADO_TORCEDOR,
    ).first()
    if peridodo_aquisitivo:
        return peridodo_aquisitivo.days
    return 0


def get_sub_tipo_de_usufruto(data):
    data_formatada = data.strftime("%d-%m")
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
    if data_formatada in datas:
        return COMP_VACATION_MEMBERS
    return COMP_CLEARANCE_MEMBERS
