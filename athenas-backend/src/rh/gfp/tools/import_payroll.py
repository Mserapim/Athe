# -*- coding: utf-8 -*-
"""
    Este módulo contém as funções para importar os dados de pagamentos de diárias.

"""
from django.contrib.auth.models import User
from datetime import date, datetime
from django.db.models import Q, Count, F
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.gfp.models import ContraCheque, Evento, Folha, FolhaTipo
from rh.models import Employee
from rh.sisdias.models import Sdia01OrdemServico
from standard.models import Choice
import requests
from rh.sisdias.utis import montar_sisdias_model

from app.settings import SISDIAS_API_URL, SISDIAS_TOKEN

log = getLogger(__name__)


PAYROLL_TYPES = {
    1: "Diárias",
}


def task_info(task, message, type_of=1):
    if task:
        task.info(msg=message, type_of=type_of)
    else:
        print(message)


def create_daily_paycheck(
    daily_payments, payroll, mes, ano, task=None, inc_progress=None
):
    event_plus = Evento.objects.filter(numero="07200").last()
    event_devolution = Evento.objects.filter(numero="07202").last()
    today = datetime.now().date()

    for mf in daily_payments:
        employee = None
        try:
            if (
                mf.chapa_servidor
                and mf.chapa_servidor != 0
                and not mf.sdia08_cdgpessoa_externa
            ):
                employee = Employee.objects.get(matricula=int(mf.chapa_servidor))
            else:
                raise Exception(" Matrícula do Servidor não foi localizada")
        except Exception as e:
            log.error("Erro ao buscar o servidor: ")
            log.error(e)
            message = f"Evento nº {mf.numero} não possui servidor. {e}"
            task_info(task, message, 3)

        if employee:
            events = {}
            has_event = False
            message = f"Importe de diários de {employee}"
            if (
                mf.data_valor_devolvido
                and mf.data_valor_devolvido.month == mes
                and mf.data_valor_devolvido.year == ano
            ):
                events.update({event_devolution: mf.valor_devolvido})
                has_event = True

            if (
                mf.data_pagamento
                and mf.data_pagamento.month == mes
                and mf.data_pagamento.year == ano
            ):
                events.update({event_plus: mf.valor_total_liquido})
                has_event = True
            if has_event:
                paycheck, created = ContraCheque.objects.get_or_create(
                    servidor=employee, folha=payroll
                )
                log.info(f"{paycheck} adicionou os seguintes eventos: ")
                for event in events:
                    log.info(event)
                    try:
                        fe, created, old_fields = paycheck.update_or_create_entry(
                            False,
                            True,
                            **{
                                "status": "CT",
                                "cid": mf.pk,
                                "evento": event,
                                "info": (
                                    f"{mf.numerounicocnmp} - Data de Pagamento {mf.data_pagamento}"
                                    if event == event_plus
                                    else f"{mf.numerounicocnmp} - Data da Devolução {mf.data_valor_devolvido}"
                                ),
                                "automated": False,
                                "insertion_type": 3,  # Choice id 3 - Tipo de Inserção: Importação
                            },
                        )
                        log.info(f"\n{fe} => {fe.valor}")

                        # Atualizar dados do evento

                        if created:
                            fe.qnt = (
                                mf.num_diaria_estado
                                + mf.num_diaria_pais
                                + mf.num_diaria_exterior
                                + mf.meiadiaria
                            )
                            fe.parcela = 1
                            fe.prazo = 1

                            if event == event_plus:
                                fe.valor_base = mf.valor_total_bruto
                                fe.valor = mf.valor_total_liquido
                                fe.correct_valor = mf.valor_total_liquido

                                fe.save_base()
                            if event == event_devolution:
                                fe.valor_base = mf.valor_devolvido
                                fe.valor = mf.valor_devolvido
                                fe.correct_valor = mf.valor_devolvido
                                fe.save_base()
                            fe.confirma("CI", User.objects.get(pk=1))

                    except Exception as e:
                        log.error(e)
            paycheck.consolidate()
            task_info(task, message, 1)

        if task:
            Task.objects.filter(uuid=task.uuid).update(
                progress=F("progress") + inc_progress
            )


def create_payroll(payrolls, period, payroll_type, data_ordem, task=None):
    complements = payrolls.values_list("complement", flat=True)
    complements_choice = [
        c[0]
        for c in Choice.get_choices_for("gfp", "COMPLEMENT_PAYROLL")
        if c[0] not in complements
    ]

    complements_choice.sort()

    payroll, created = Folha.objects.get_or_create(
        periodo=period,
        tipo_folha=payroll_type,
        complement=complements_choice[0],
        dt_pagamento=data_ordem,
    )
    return payroll


def import_daily_payments(period, task=None):

    # Codigo original da importação do sisdias
    # query = Sdia01OrdemServico.objects.filter(
    #     Q(data_pagamento__month=period.mes,data_pagamento__year=period.ano) |
    #     Q(data_valor_devolvido__month=period.mes,data_valor_devolvido__year=period.ano)
    # ).using('sisdias')

    # total = query.count()

    mes = str(period.mes)
    mes = mes if len(mes) == 2 else f"0{mes}"

    ano = period.ano

    query = []

    # URL da API
    url = f"{SISDIAS_API_URL}v1/diarias/pagamentos?ano={ano}&mes={mes}"

    # Cabeçalhos a serem enviados
    headers = {
        "Authorization": f"Bearer {SISDIAS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Fazer a requisição GET com cabeçalhos
    response = requests.get(url, headers=headers)

    for data in response.json():
        query.append(montar_sisdias_model(data))

    total = len(query)

    inc_progress = 100.0 / total if total else 100.0

    payroll_type = FolhaTipo.objects.filter(numero="51").first()  # TIPO DIÁRIAS
    payrolls = Folha.objects.filter(periodo=period, tipo_folha=payroll_type)
    payroll = payrolls.last()

    if not payroll:
        task.finish_execution(status="ERROR")
        raise Exception("Não foi localizada folha de pagamento de Diárias.")

    if payroll.status in (3, 4):
        task.finish_execution(status="ERROR")
        raise Exception(
            "A folha existente para o mês informado não se encontra disponível para alterações."
        )

    create_daily_paycheck(
        query,
        payroll,
        mes=period.mes,
        ano=period.ano,
        task=task,
        inc_progress=inc_progress,
    )

    payroll.consolidate_payroll(control_by_lock=False)
    payroll.save()


def import_payments(payroll_type, period, task=None):
    task = Task.objects.get(pk=task.pk) if task else None

    if payroll_type == 1:
        import_daily_payments(period, task=task)
    else:
        raise Exception(f"Tipo de folha não suportado {payroll_type}.")
