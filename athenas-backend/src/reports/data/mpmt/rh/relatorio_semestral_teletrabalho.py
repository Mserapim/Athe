from contrib.utils import QuerySetChain, getLogger
from datetime import datetime
import base64
from rh.pvf.models import RelatorioSemestralTeletrabalho
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
import calendar
from rh.models import Servidor
from datetime import datetime, date
from django.db.models.query_utils import Q


log = getLogger(__name__)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """

    data = {}
    periodo = get_periodo(params)
    relatorios_semestrais = RelatorioSemestralTeletrabalho.objects.filter(
        periodo_envio=periodo
    ).order_by("employee__pessoa_fisica__nome")

    data["relatorios"] = relatorios_semestrais

    mes_inicio_analisado, ano_inicio_analisado = map(
        int, periodo.data_inicio_periodo_analisado.split("/")
    )
    mes_fim_analisado, ano_fim_analisado = map(
        int, periodo.data_fim_periodo_analisado.split("/")
    )

    inicio_mes, fim_mes = get_inicio_fim_mes(mes_inicio_analisado, mes_fim_analisado)
    data_inicio, data_fim = get_data_inicio_fim(
        mes_inicio_analisado, mes_fim_analisado, ano_inicio_analisado, ano_fim_analisado
    )

    query_servidor = Servidor.objects.filter(
        Q(aprovador_teletrabalho__data_inicio__lte=data_fim)
        & Q(aprovador_teletrabalho__data_fim__gte=data_inicio)
    ).distinct()

    q_gestores = Servidor.objects.filter(
        pk__in=relatorios_semestrais.values_list("employee")
    ).exclude(pk__in=query_servidor)

    query_servidor = QuerySetChain(q_gestores, query_servidor)

    total_servidor = query_servidor.count()

    total_relatorios = relatorios_semestrais.count()

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "inicio_mes": inicio_mes.capitalize(),
        "fim_mes": fim_mes.capitalize(),
        "ano_referencia": ano_inicio_analisado,
        "total_enviado": total_relatorios,
        "total_nao_eviado": abs(total_servidor - total_relatorios),
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }
    return values


def get_periodo(params):
    periodo_id = params["periodo"]
    if periodo_id:
        periodo_id = int(periodo_id.split("_")[1])

    if periodo_id:
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.filter(
            id=periodo_id
        ).first()
    else:
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.last()
    return periodo


def get_inicio_fim_mes(inicio_analisado, fim_analisado):
    inicio_mes = calendar.month_name[inicio_analisado]
    fim_mes = calendar.month_name[fim_analisado]
    return [inicio_mes, fim_mes]


def get_data_inicio_fim(mes_inicio, mes_fim, ano_inicio, ano_fim):
    data_inicio = date(ano_inicio, mes_inicio, 1)
    ultimo_dia_mes_fim_analisado = calendar.monthrange(ano_fim, mes_fim)[1]
    data_fim = date(ano_fim, mes_fim, ultimo_dia_mes_fim_analisado)
    return [data_inicio, data_fim]
