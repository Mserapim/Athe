import base64
from datetime import datetime
from django.db.models import Q, Sum

from contrib.utils import getLogger
from rh.models import Servidor, MovimentacaoPosse
from rh.gfp.models import FolhaEvento, Evento

from decimal import Decimal

log = getLogger(__name__)


def validate_period_format(value):

    try:
        month, year = value.split("/")
        return month, year
    except Exception as e:
        log.error(e)
        raise Exception(
            "A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        )


def get_data_report(params):

    data = {}

    # Extract params
    matricula = params["matricula"]
    ano_inicial = params["ano_inicial"]
    ano_final = params["ano_final"]
    output_format = params["output_format"]

    periodos = list(range(int(ano_inicial), int(ano_final) + 1))

    try:
        servidor = Servidor.objects.get(matricula=matricula)

        primeira_posse = (
            MovimentacaoPosse.objects.filter(servidor=servidor)
            .order_by("data_exercicio")
            .first()
        )

        if servidor.ativo:
            mov_posses = servidor.posses_ativas.filter(ativo=True)
        else:
            mov_posses = servidor.posses.filter()

        lista_cargos = []

        for mov in mov_posses:
            lista_cargos.append(mov.quadro.cargo.nome)

        data["matricula"] = servidor.matricula
        data["nome"] = servidor.pessoa_fisica.social_name
        data["exercicio"] = servidor.exercise_date.strftime("%d/%m/%Y")
        data["posse"] = mov_posses.last().data_posse.strftime("%d/%m/%Y")

        data["cargo"] = " / ".join(lista_cargos)

        if primeira_posse:
            if (
                primeira_posse.publicacao_movimentacao
                and primeira_posse.publicacao_movimentacao.data_expedicao
            ):
                data["nomeacao"] = (
                    primeira_posse.publicacao_movimentacao.data_expedicao.strftime(
                        "%d/%m/%Y"
                    )
                )
            else:
                data["nomeacao"] = primeira_posse.data_exercicio.strftime("%d/%m/%Y")
        else:
            data["nomeacao"] = ""

    except:
        raise "Erro ao Buscar dados do Servidor"

    periodos_list = []

    try:
        for periodo in periodos:

            proventos = []
            descontos = []

            eventos_proventos = Evento.objects.filter(
                tipo="P",
                lancamentos__servidor=servidor,
                lancamentos__status="CT",
                lancamentos__folha__status=3,
                lancamentos__folha__available_pvf=True,
                lancamentos__folha__periodo__ano=periodo,
            ).distinct()

            eventos_descontos = Evento.objects.filter(
                tipo="D",
                lancamentos__servidor=servidor,
                lancamentos__status="CT",
                lancamentos__folha__status=3,
                lancamentos__folha__available_pvf=True,
                lancamentos__folha__periodo__ano=periodo,
            ).distinct()

            for evento in eventos_proventos:
                dados_provento = []
                dados_provento.append(f"{evento.numero} - {evento.titulo}")
                total = 0

                for mes in range(1, 14):
                    valor = FolhaEvento.objects.filter(
                        evento=evento,
                        servidor=servidor,
                        status="CT",
                        folha__status=3,
                        folha__available_pvf=True,
                        folha__periodo__ano=periodo,
                        folha__periodo__mes=mes,
                    ).aggregate(soma=Sum("valor"))["soma"]

                    dados_provento.append(Decimal(valor) if valor else Decimal("0.00"))
                    if valor is not None:
                        total += Decimal(valor)

                dados_provento.append(total)

                proventos.append(dados_provento)

            total = ["TOTAL PROVENTOS"] + [0] * 13
            for item in proventos:
                for y in range(1, 14):
                    total[y] = total[y] + item[y]

            proventos.append(total)

            for evento in eventos_descontos:
                dados_desconto = []
                dados_desconto.append(f"{evento.numero} - {evento.titulo}")
                total = 0

                for mes in range(1, 14):
                    valor = FolhaEvento.objects.filter(
                        evento=evento,
                        servidor=servidor,
                        status="CT",
                        folha__status=3,
                        folha__available_pvf=True,
                        folha__periodo__ano=periodo,
                        folha__periodo__mes=mes,
                    ).aggregate(soma=Sum("valor"))["soma"]
                    dados_desconto.append(valor if valor else 0.00)
                    if valor is not None:
                        total += valor

                dados_desconto.append(total)

                descontos.append(dados_desconto)

            total = ["TOTAL DESCONTOS"] + [0] * 13
            for item in descontos:
                for y in range(1, 14):
                    total[y] += Decimal(str(item[y]))

            descontos.append(total)

            total_liquido = ["TOTAL LIQUIDO"] + [0] * 13

            for y in range(1, 14):
                total_liquido[y] = proventos[-1][y] - descontos[-1][y]

            periodos_list.append(
                {
                    "ano": periodo,
                    "proventos": proventos,
                    "descontos": descontos,
                    "total_liquido": total_liquido,
                }
            )

        data["periodos"] = periodos_list
    except:
        raise "Erro a Definir"

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": [],
    }
    return values
