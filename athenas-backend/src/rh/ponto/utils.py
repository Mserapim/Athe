import calendar

from django.db.models import Q
from engine.mq.models import Task
from rh.models import Servidor, ControlePagamentoPessoal
from rh.gfp.models import Evento, FolhaEvento
from rh.ponto.models import Falta
from standard.models import Choice, Item

from rh.gfp.gcpp_utils import criar_gcpp

from datetime import date, datetime
from contrib.utils import getLogger


log = getLogger(__name__)


def get_start_end_date(reference):
    month, year = mes_ano(reference)
    last_day = calendar.monthrange(int(year), int(month))
    start_date = date(int(year), int(month), 1)
    end_date = date(int(year), int(month), last_day[1])
    return start_date, end_date


def mes_ano(referencia):
    return referencia.split("/")


def query_faltas(employee_id, start_date, end_date, situacao):
    return Falta.objects.filter(
        Q(servidor__id__in=employee_id)
        & Q(situacao=situacao)
        & Q(
            Q(
                Q(data__isnull=False, data_fim__isnull=False)
                & Q(
                    Q(data__lte=start_date, data_fim__gte=start_date)
                    | Q(data__gte=start_date, data__lte=end_date)
                )
            )
            | Q(Q(data__isnull=False, data_fim__isnull=True) & Q(data__lte=start_date))
        )
    ).exclude(Q(competencia_desconto__isnull=True, payroll=True))


def registrar_faltas_no_gcpp(query, servidor_id, user_id):
    """
    Eventos:
        Estagiários:
            15600: Falta Bolsa
            *15602: Falta Bolsa - Devolução
            15700: Falta Transporte
            *15702: Falta Transporte - Devolução
        Residentes:
            15800: Falta Bolsa
            *15802: Falta Bolsa - Devolução
            15900: Falta Transporte
            *15902: Falta Transporte - Devolução
        Subsídio:
            04900: Falta
            *04902: Falta - Devolução
        Gratificações:
            10200: Falta
            *10202: Falta - Devolução
        Auxílio Alimentação:
            04600: Falta
            *04602: Falta - Devolução
    """

    modulo = "Gestor de Faltas"
    servidor = Servidor.objects.get(id__in=servidor_id)
    servidor_conf_por = Servidor.objects.get(user__id=user_id)
    faltas = query.filter(competencia_desconto__isnull=False)

    comps_desc = (
        faltas.order_by("competencia_desconto")
        .values_list("competencia_desconto")
        .distinct("competencia_desconto")
    )  # Separação das Comp. de Desconto

    for comp_desc in comps_desc:
        mes_desc, ano_desc = mes_ano(comp_desc[0])
        faltas_comp_desc = faltas.filter(
            competencia_desconto=comp_desc[0]
        )  # Faltas agrupadas pela Comp. de Desconto

        comps_falta = []
        for falta in faltas_comp_desc.order_by("data"):
            comp_falta = f"{falta.data.month}/{falta.data.year}"
            if comp_falta not in comps_falta:
                comps_falta.append(
                    comp_falta
                )  # Comp. de Faltas dentro dessa Comp. de Desconto

        for comp_falta in comps_falta:
            faltas_gcpp = []
            faltas_gcpp_just = []
            faltas_gcpp_injust = []
            qtd_dias = 0  # Faltas injustificadas e justificadas
            qtd_dias_just = 0  # Faltas justificadas e marcadas para Folha
            qtd_dias_injust = 0  # Faltas injustificadas e marcadas para Folha
            mes_falta, ano_falta = mes_ano(comp_falta)

            mes = (
                Choice.objects.filter(name="MONTHS", app_label="rh", value=mes_falta)
                .first()
                .label
            )
            info = f"{ano_falta} - {mes.title()}"

            faltas_comp_desc_falta = faltas_comp_desc.filter(
                data__month=mes_falta, data__year=ano_falta
            )  # Faltas agrupadas pela Comp. de Desconto e Comp. da Falta

            for falta in faltas_comp_desc_falta:
                if falta.justificado and falta.payroll:
                    qtd_dias_just += falta.get_days
                    faltas_gcpp_just.append(falta)
                elif (not falta.justificado) and falta.payroll:
                    qtd_dias_injust += falta.get_days
                    faltas_gcpp_injust.append(falta)
                qtd_dias += falta.get_days
                faltas_gcpp.append(falta)

            if servidor.type_by_possession in ["EST"]:
                evento_15700 = Evento.objects.get(numero="15700")
                evento_15600 = Evento.objects.get(numero="15600")

                if (
                    qtd_dias > 0
                ):  # Faltas justificadas/injustificadas e marcadas para Folha
                    # 15700: Falta Transporte
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_15700,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp[0].data.month,
                        faltas_gcpp[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(gcpp_encontrado, qtd_dias, faltas_gcpp)
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_15700,
                            qtd_dias=qtd_dias,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp)
                if qtd_dias_injust > 0:  # Faltas injustificadas
                    # 15600: Falta Bolsa
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_15600,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp_injust[0].data.month,
                        faltas_gcpp_injust[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(
                            gcpp_encontrado, qtd_dias_injust, faltas_gcpp_injust
                        )
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_15600,
                            qtd_dias=qtd_dias_injust,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp_injust)

            elif servidor.type_by_possession in ["RES"]:
                evento_15900 = Evento.objects.get(numero="15900")
                evento_15800 = Evento.objects.get(numero="15800")

                if (
                    qtd_dias > 0
                ):  # Faltas justificadas/injustificadas e marcadas para Folha
                    # 15900: Falta Transporte
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_15900,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp[0].data.month,
                        faltas_gcpp[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(gcpp_encontrado, qtd_dias, faltas_gcpp)
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_15900,
                            qtd_dias=qtd_dias,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp)
                if qtd_dias_injust > 0:  # Faltas injustificadas
                    # 15800: Falta Bolsa
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_15800,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp_injust[0].data.month,
                        faltas_gcpp_injust[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(
                            gcpp_encontrado, qtd_dias_injust, faltas_gcpp_injust
                        )
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_15800,
                            qtd_dias=qtd_dias_injust,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp_injust)

            elif servidor.type_by_possession in ["EFE", "CMS"]:
                evento_04900 = Evento.objects.get(numero="04900")
                evento_10200 = Evento.objects.get(numero="10200")
                evento_04600 = Evento.objects.get(numero="04600")

                # Só Faltas injustificadas e marcadas para Folha
                if qtd_dias_injust > 0:
                    # 04900: Falta - Subsídio
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_04900,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp_injust[0].data.month,
                        faltas_gcpp_injust[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(
                            gcpp_encontrado, qtd_dias_injust, faltas_gcpp_injust
                        )
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_04900,
                            qtd_dias=qtd_dias_injust,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp_injust)

                    # 10200: Falta - Gratificações
                    ev_dili = Item.objects.get(key="evento_grat_diligencia").value
                    ev_coord = Item.objects.get(key="evento_grat_aux_coord").value
                    query = FolhaEvento.objects.filter(
                        servidor=servidor,
                        folha__periodo__mes=mes_desc,
                        folha__periodo__ano=ano_desc,
                        evento__numero__in=[ev_dili, ev_coord],
                    )
                    if query.exists():
                        gcpp_encontrado = retornar_gcpp(
                            servidor,
                            evento_10200,
                            mes_desc,
                            ano_desc,
                            faltas_gcpp_injust[0].data.month,
                            faltas_gcpp_injust[0].data.year,
                        )
                        if (
                            gcpp_encontrado
                        ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                            unificar_faltas_gcpp(
                                gcpp_encontrado, qtd_dias_injust, faltas_gcpp_injust
                            )
                        else:
                            gcpp = criar_gcpp(
                                servidor=servidor,
                                evento=evento_10200,
                                qtd_dias=qtd_dias_injust,
                                periodo_ano=ano_desc,
                                periodo_mes=mes_desc,
                                servidor_conferido_por=servidor_conf_por,
                                modulo_origem=modulo,
                                info=info,
                            )
                            gcpp.faltas.add(
                                *faltas_gcpp_injust
                            )  # Evento 10200 em observação

                    # 04600: Falta - Auxílio Alimentação
                    gcpp_encontrado = retornar_gcpp(
                        servidor,
                        evento_04600,
                        mes_desc,
                        ano_desc,
                        faltas_gcpp_injust[0].data.month,
                        faltas_gcpp_injust[0].data.year,
                    )
                    if (
                        gcpp_encontrado
                    ):  # Se já existir gcpp com mesmo evento na mesma competência de desconto e da falta
                        unificar_faltas_gcpp(
                            gcpp_encontrado, qtd_dias_injust, faltas_gcpp_injust
                        )
                    else:
                        gcpp = criar_gcpp(
                            servidor=servidor,
                            evento=evento_04600,
                            qtd_dias=qtd_dias_injust,
                            periodo_ano=ano_desc,
                            periodo_mes=mes_desc,
                            servidor_conferido_por=servidor_conf_por,
                            modulo_origem=modulo,
                            info=info,
                        )
                        gcpp.faltas.add(*faltas_gcpp_injust)


def evento_por_tipo_posse(servidor):
    if servidor.type_by_possession in ["EST"]:
        return Evento.objects.get(numero="15600"), Evento.objects.get(numero="15700")
    elif servidor.type_by_possession in ["RES"]:
        return Evento.objects.get(numero="15800"), Evento.objects.get(numero="15900")


def retornar_gcpp(servidor, evento, mes_desc, ano_desc, mes_falta, ano_falta):
    return (
        ControlePagamentoPessoal.objects.filter(
            servidor=servidor,
            evento=evento,
            periodo_ano=ano_desc,
            periodo_mes=mes_desc,
            faltas__data__year=ano_falta,
            faltas__data__month=mes_falta,
        )
        .exclude(status__in=["pago", "inapto"])
        .first()
    )


def unificar_faltas_gcpp(gcpp_encontrado, qtd_dias, faltas_gcpp):
    if gcpp_encontrado.status not in ["pago", "inapto"]:
        gcpp_encontrado.qtd_dias_confirmado += qtd_dias
        gcpp_encontrado.save()
        gcpp_encontrado.faltas.add(*faltas_gcpp)


def dados_sem_justificativa(current_user, day, sheet):
    dados = {
        "created_by_id": current_user.id,
        "modified_by_id": current_user.id,
        "created_at": datetime.now(),
        "modified_at": datetime.now(),
        "data_fim": day,
        "request_sts": sheet,
        "origem": 1,
        "situacao": 1,
        "justificado": False,
        "observacao": "",
        "payroll": True,  # financeiro
        "vertical_progression": True,
        "premium_license": True,
    }
    return dados


def dados_com_justificativa(
    current_user,
    just_vdf,
    sheet,
    justificado,
    payroll,
    vertical_progression,
    premium_license,
):
    dados = {
        "created_by_id": current_user.id,
        "modified_by_id": current_user.id,
        "created_at": datetime.now(),
        "modified_at": datetime.now(),
        "data_fim": just_vdf.end_date,
        "request_sts": sheet,
        "origem": 1,
        "situacao": 1,
        "justificado": justificado,
        "observacao": just_vdf.observation,
        "payroll": payroll,
        "vertical_progression": vertical_progression,
        "premium_license": premium_license,
    }
    return dados


def atribuir_por_falta(falta_ids, user_id, competencia_desconto):
    from rh.ponto.tasks_falta import atribuir_comp_desc_por_falta_task

    try:
        if falta_ids:
            Task.start(
                atribuir_comp_desc_por_falta_task,
                description=f"Atribuir Competência de Desconto.",
                user=user_id,
                falta_ids=list(falta_ids),
                competencia_desconto=competencia_desconto,
            )

            success = True
            message = "Iniciando Atribuição de Competência de Desconto!"
        else:
            success = False
            message = "Não há Faltas para atribuir ou as Faltas não possuem Competência de Desconto!"
    except:
        success = False
        message = "ERRO ao Atribuir Competência de Desconto!"

    return success, message


def processar_por_falta(falta_ids, user_id):
    from rh.ponto.tasks_falta import processar_faltas_task

    try:
        if falta_ids:
            Task.start(
                processar_faltas_task,
                description=f"Processar Faltas",
                user=user_id,
                falta_ids=list(falta_ids),
            )

            success = True
            message = "Iniciando Processamento de Faltas!"
        else:
            success = False
            message = "Não há Faltas para processar ou as Faltas não possuem Competência de Desconto!"
    except:
        success = False
        message = "ERRO ao Processar Faltas!"

    return success, message
