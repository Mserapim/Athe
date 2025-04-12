import base64
from datetime import datetime, timedelta
from contrib.utils import getLogger
from rh.models import CargaHoraria
from rh.registerpoint.utils.ponto import folha_ponto_periodo
from django.db.models import Q


log = getLogger(__name__)


def get_dados_relatorio(dt_inicio, dt_fim, servidor, servidor_logado, tipos_dia):
    if isinstance(dt_inicio, str):
        inicio = datetime.strptime(dt_inicio, "%Y-%m-%d").date()
    if isinstance(dt_fim, str):
        fim = datetime.strptime(dt_fim, "%Y-%m-%d").date()

    tipo_normal = 1
    tipo_justificado = 2
    tipo_falta = 3
    tipo_licenca_afas = 5
    tipo_viagem = 7
    tipo_teletrabalho = 8

    dados_ponto = folha_ponto_periodo(
        inicio, fim, servidor, servidor_logado, tipos_dia=tipos_dia, relatorio=True
    )
    dados_pessoa = get_dados_pessoa(servidor, inicio, fim)

    carga_horaria_total = timedelta()
    total_dia_total = timedelta()
    saldo_dia_total = timedelta()

    for dia in dados_ponto:
        # Somar carga_horaria
        if dia["carga_horaria"] and dia["tipo"] in [
            tipo_normal,
            tipo_justificado,
            tipo_falta,
            tipo_licenca_afas,
            tipo_viagem,
            tipo_teletrabalho,
        ]:
            try:
                horas, minutos, segundos = map(int, dia["carga_horaria"].split(":"))
                carga_diaria = timedelta(hours=horas, minutes=minutos, seconds=segundos)
                carga_horaria_total += carga_diaria
            except ValueError as e:
                log.error(f"Erro ao converter carga horária: {e}")

        # Somar total_dia
        if dia["total_dia"]:
            try:
                horas, minutos, segundos = map(int, dia["total_dia"].split(":"))
                total_dia_diario = timedelta(
                    hours=horas, minutes=minutos, seconds=segundos
                )
                total_dia_total += total_dia_diario
            except ValueError as e:
                log.error(f"Erro ao converter total do dia: {e}")

        # Somar saldo_dia
        if dia["saldo_dia"]:
            try:
                negativo = dia["saldo_dia"].startswith("-")
                saldo_str = dia["saldo_dia"].lstrip("-")
                horas, minutos, segundos = map(int, saldo_str.split(":"))
                saldo_diario = timedelta(hours=horas, minutes=minutos, seconds=segundos)

                if negativo:
                    saldo_diario = -saldo_diario

                saldo_dia_total += saldo_diario
            except ValueError as e:
                log.error(f"Erro ao converter saldo do dia: {e}")

        marcacoes_validas = [
            m["marcacao_hora"].strftime("%H:%M:%S")
            for m in dia["marcacoes"]
            if m["marcacao_valida"]
        ]
        dia["marcacoes_formatadas"] = marcacoes_validas + [""] * (
            4 - len(marcacoes_validas)
        )  # Garantir 4 colunas
        dia["total_dia"] = dia["total_dia"] if dia["total_dia"] else ""
        dia["saldo_dia"] = dia["saldo_dia"] if dia["saldo_dia"] else ""

    ch_periodo = format_timedelta(carga_horaria_total)
    total_periodo = format_timedelta(total_dia_total)
    saldo_periodo = format_timedelta(saldo_dia_total)

    resumo_batidas = {
        "DIASUTEIS": sum(
            1
            for dia in dados_ponto
            if dia["tipo"]
            in [
                tipo_normal,
                tipo_justificado,
                tipo_falta,
                tipo_licenca_afas,
                tipo_viagem,
                tipo_teletrabalho,
            ]
        ),
        "DIASTRABALHADOS": sum(
            1
            for dia in dados_ponto
            if dia["tipo"]
            in [tipo_normal, tipo_justificado, tipo_viagem, tipo_teletrabalho]
        ),
        "DIASJUSTIFICADOS": len(
            [dia for dia in dados_ponto if dia["tipo"] == tipo_justificado]
        ),
        "FALTASPERIODO": len([dia for dia in dados_ponto if dia["tipo"] == tipo_falta]),
        "CHPERIODO": ch_periodo,
        "HORASTRABALHADAS": total_periodo,
        "SALDOPERIODO": saldo_periodo,
    }

    with open("static/images/brasao-mpmt.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    values = {
        "title": "Relatório de Folha Ponto",
        "dados": dados_ponto,
        "dados_pessoa": dados_pessoa,
        "resumo_batidas": resumo_batidas if resumo_batidas else {},
        "hora": datetime.now().strftime("%H:%M"),
        "data": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
    }

    return values


# Formatar `carga_horaria_total`, `total_dia_total` e `saldo_dia_total` no formato hh:mm:ss
def format_timedelta(td):
    total_horas = abs(td.total_seconds()) // 3600
    total_minutos = (abs(td.total_seconds()) % 3600) // 60
    total_segundos = abs(td.total_seconds()) % 60
    formatted_time = (
        f"{int(total_horas):02}:{int(total_minutos):02}:{int(total_segundos):02}"
    )
    return f"-{formatted_time}" if td.total_seconds() < 0 else formatted_time


def get_dados_pessoa(servidor, inicio, fim):
    job_position = servidor.job_position(fim) or servidor.job_position(inicio)

    cargo = job_position.cargo.nome if job_position and job_position.cargo else ""

    workplace = servidor.workplace_by_date(fim) or servidor.workplace_by_date(inicio)

    lotacao = workplace.nome if workplace else ""

    if lotacao:
        nome_lotacao = lotacao
    else:
        nome_lotacao = "Sem lotação"

    cargas = (
        CargaHoraria.objects.filter(servidor_id=servidor.id)
        .filter(data_inicio__lte=fim)
        .filter(Q(data_fim__gte=inicio) | Q(data_fim__isnull=True))
        .order_by("-data_inicio")
    )

    carga_horaria = cargas.filter(active=True).first()
    if not carga_horaria:
        carga_horaria = cargas.first()

    if not carga_horaria or not carga_horaria.jornada_trabalho:
        return {
            "success": False,
            "message": "Carga horária ou jornada de trabalho não encontrada.",
        }

    dados_pessoa = {}
    dados_pessoa.update(
        {
            "nome": servidor.pessoa_fisica.social_name,
            "matricula": servidor.matricula,
            "cargo": cargo,
            "lotacao": nome_lotacao,
            "carga_horaria": carga_horaria.jornada_trabalho.duration_hour,
            "dt_inicio": inicio,
            "dt_fim": fim,
        }
    )

    return dados_pessoa


def get_cargo(servidor):
    posses = servidor.posses_ativas
    if not servidor.ativo:
        posses = servidor.posses

    efetivo = posses.filter(quadro__cargo__tipo_lei_cargo="EF")
    if efetivo.exists():
        ef = efetivo.latest("data_exercicio")
        efetivo = ef.quadro
        return efetivo
    if servidor.ativo or (not efetivo):
        comissao = posses.filter(quadro__cargo__tipo_lei_cargo__in=("CM", "FC"))
        if comissao.exists():
            cm = comissao.latest("data_exercicio")
            comissao = cm.quadro
            return comissao
