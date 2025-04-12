from contrib.utils import getLogger
from contrib.middleware import set_current_user

from standard.models import Choice, Item
from rh.models import ControlePagamentoPessoal
from rh.gfp.models import Folha, Evento

from rh.gfp.paycheckdifference_utils import calc_from_period

log = getLogger(__name__)


def buscar_folha(periodo_ano, periodo_mes):
    return Folha.objects.filter(
        periodo__ano=periodo_ano, periodo__mes=periodo_mes, tipo_folha__titulo="NORMAL"
    )


def verificar_conferencia(conferencia_titular, conferencia_substituto):
    return conferencia_titular.exists() or (
        conferencia_substituto is not False and conferencia_substituto.exists()
    )


def verificar_pgto(conferencia_titular, conferencia_substituto):
    if conferencia_titular.exists() is False:
        return False

    if conferencia_substituto is False or conferencia_substituto.exists() is False:
        if (
            conferencia_titular.exists()
            and conferencia_titular.first().status == "pago"
        ):
            return True
        else:
            return False
    else:
        if conferencia_titular.exists() and conferencia_substituto.exists():
            return (
                conferencia_titular.first().status == "pago"
                and conferencia_substituto.first().status == "pago"
            )
        else:
            False


def verificar_folhaevento_servidor(servidor, evento, periodo_ano, periodo_mes):
    return servidor.entries.filter(
        contracheque__folha__periodo__ano=periodo_ano,
        contracheque__folha__periodo__mes=periodo_mes,
        evento=evento,
    )


def verificar_pgto_servidor(servidor, evento, periodo_ano, periodo_mes):
    pgto = False
    conferido = False
    origem = ""
    tipo_insercao = False
    qtd_dias = "-"
    if servidor and evento:
        folhaevento_servidor = verificar_folhaevento_servidor(
            servidor, evento, periodo_ano, periodo_mes
        )

        if folhaevento_servidor.exists():
            pgto = True
            origem = "folhaevento"
            tipo_insercao = folhaevento_servidor.first().insertion_type
            qtd_dias = folhaevento_servidor.first().qnt
        else:
            origem = "conferencia"
            conferencia_servidor = buscar_registro_gcpp(
                servidor, evento, periodo_ano, periodo_mes
            )
            if conferencia_servidor.exists():
                conferido = True
                pgto = True if conferencia_servidor.first().status == "pago" else False
                qtd_dias = conferencia_servidor.first().qtd_dias_confirmado
            else:
                pgto = False

    return {
        "pgto": pgto,
        "conferido": conferido,
        "origem": origem,
        "tipo_insercao": tipo_insercao,
        "qtd_dias": qtd_dias,
    }


def buscar_registro_gcpp(servidor, evento, periodo_ano, periodo_mes):
    return ControlePagamentoPessoal.objects.filter(
        periodo_ano=periodo_ano,
        periodo_mes=periodo_mes,
        conferido=True,
        evento=evento,
        servidor=servidor,
    )


def calcular_dias_servidor(
    servidor,
    tipo,
    payroll,
    evento,
    pgto_servidor,
    todos_meses,
    dias_receber_titular=None,
):
    dias_receber = "-"
    if todos_meses:
        return dias_receber
    else:
        if pgto_servidor["conferido"] is True:
            dias_receber = pgto_servidor["qtd_dias"]
        elif payroll.exists():
            if tipo == "titular" and pgto_servidor["pgto"] is False and evento:
                res = calc_from_period(servidor, payroll.first(), evento)
                dias_receber = int(res["qnt"])
            elif tipo == "subs":
                dias_titular = (
                    0 if dias_receber_titular == "-" else dias_receber_titular
                )
                if (
                    servidor
                    and servidor.ativo
                    and pgto_servidor["pgto"] is False
                    and payroll.first().date_range.days > dias_titular
                    and evento
                ):
                    res = calc_from_period(servidor, payroll.first(), evento)
                    dias_receber = int(res["qnt"])

        return dias_receber


def calcular_dias_membro(servidor, payroll, evento, pgto_servidor):
    dias_receber = "-"
    if pgto_servidor["origem"] == "conferencia" and payroll.exists():
        res = calc_from_period(servidor, payroll.first(), evento)
        dias_receber = int(res["qnt"])

    return dias_receber


def get_icons_servidor(instance, tipo_servidor, pgto_servidor=None):
    icon = ""
    status = ""
    texto_tit_subs = "Titular" if tipo_servidor == "titular" else "Substituto"
    servidor = instance.servidor if tipo_servidor == "titular" else instance.substituto

    if tipo_servidor == "subs" and not instance.substituto:
        icon = "icon-fopag icon-exclamation-black"
        status = "Não há Substituto"
    else:
        icon_ativo = "green" if servidor.ativo else "red"
        icon = f"icon-fopag icon-exclamation-{icon_ativo}"
        status = (
            f"{texto_tit_subs} Ativo" if servidor.ativo else f"{texto_tit_subs} Inativo"
        )

    obj = [
        {
            "iconCls": icon,
            "title": status,
            "alt": status,
        }
    ]

    if pgto_servidor is not None and pgto_servidor["pgto"]:
        title = "Pago"
        obj.append(
            {
                "iconCls": "icon-fopag icon-cash",
                "title": title,
                "alt": title,
            }
        )

    if pgto_servidor is not None and pgto_servidor["origem"] == "folhaevento":
        try:
            txt_tipo_insercao = Choice.objects.get(
                app_label="gfp",
                name="ENTRY_INSERTION_TYPE",
                value=pgto_servidor["tipo_insercao"],
            ).label
        except:
            txt_tipo_insercao = ""
        title = f"Origem pgto: {txt_tipo_insercao}"
        obj.append(
            {
                "iconCls": "icon-fopag icon-money-pencil",
                "title": title,
                "alt": title,
            }
        )

    return obj


def get_icons_registro(instance, evento, periodo_ano, periodo_mes):
    conferencia_titular = buscar_registro_gcpp(
        instance.servidor, evento, periodo_ano, periodo_mes
    )
    if instance.substituto:
        conferencia_substituto = buscar_registro_gcpp(
            instance.substituto, evento, periodo_ano, periodo_mes
        )
    else:
        conferencia_substituto = False

    obj = []

    diligence_conferido = verificar_conferencia(
        conferencia_titular, conferencia_substituto
    )
    if diligence_conferido:
        title = "Conferido"
        obj.append(
            {
                "iconCls": "icon-fopag icon-notebook-plus",
                "title": title,
                "alt": title,
            }
        )

    return obj


def verifiar_comarca(comarca, servidor):
    comarcas_servidor = [
        wp.lotacao.comarca
        for wp in servidor.get_work_assignment().filter(ativo=True, designacao=True)
        if wp.lotacao.comarca
    ]

    return comarca in comarcas_servidor


def verifiar_lotacao(lotacao, servidor):
    lotacoes_servidor = [
        wp.lotacao
        for wp in servidor.get_work_assignment().filter(ativo=True, designacao=True)
        if wp.lotacao
    ]

    return lotacao in lotacoes_servidor


def buscar_verba_calculo_exerc_cumul_consolidado():
    verba_numero = (
        Item.objects.filter(
            configuration__application="gfp", key="exerc_cumulativo_evento_calculo"
        )
        .first()
        .value
    )

    return Evento.objects.get(numero=verba_numero)
