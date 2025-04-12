from datetime import datetime

from django.db.models import Count

from contrib.middleware import set_current_user
from contrib.utils import getLogger

from rh.models import ControlePagamentoPessoal, Dependencia
from rh.gfp.models import Folha, Evento
from standard.models import Choice

from rh.gfp.paycheckdifference_utils import calc_from_period
from rh.gfp.gfp_utils import get_paycheck, create_entry

log = getLogger(__name__)


def calcular_e_salvar_gcpp(gcpp, titulo_folha="NORMAL"):
    evento = Evento.objects.get(numero=gcpp.evento.numero)

    try:
        folha = Folha.objects.get(
            tipo_folha__titulo=titulo_folha,
            periodo__ano=gcpp.periodo_ano,
            periodo__mes=gcpp.periodo_mes,
        )
    except:
        folha = (
            Folha.objects.filter(tipo_folha__titulo=titulo_folha)
            .order_by("-periodo__ano", "-periodo__mes")
            .first()
        )

    """
    Cálculo para o segundo dependente do aux. creche
    """
    segundo_dependente = False
    if gcpp.dependencia:
        query = Dependencia.objects.filter(
            dependente__servidor__matricula=gcpp.servidor.matricula,
            tipo=4,
            data_inicio__lte=gcpp.dependencia.data_inicio,
        ).exclude(pk=gcpp.dependencia.pk)

        if query.exists():
            segundo_dependente = True
            from rh.gfp.calcs.mpmt.aid import AidRetroactiveDaycare

            class_aid = AidRetroactiveDaycare(gcpp.servidor, folha, evento)
            valor = class_aid._value_for_dep2(gcpp.dependencia)
            qnt_dias = class_aid.qtd_por_dependencia(gcpp.dependencia)

    params = {"qnt": gcpp.qtd_dias_confirmado}

    if gcpp.pct:
        params["pct"] = gcpp.pct

    valores_calc = calc_from_period(gcpp.servidor, folha, evento, params=params)

    gcpp.qtd_dias_calculado = (
        valores_calc["qnt"] if not segundo_dependente else qnt_dias
    )
    gcpp.valor_calculado = valores_calc["valor"] if not segundo_dependente else valor
    gcpp.qtd_max_dias = valores_calc["qnt_max"]
    gcpp.parcela = valores_calc["parcela"]
    gcpp.prazo = valores_calc["prazo"]
    gcpp.pct = valores_calc["pct"]
    gcpp.valor_base = valores_calc["valor_base"]
    gcpp.valor_base_prev = valores_calc["base_previdencia"]
    gcpp.valor_patronal = valores_calc["patronal"]
    gcpp.status = "calculado"
    gcpp.save()


def confirmar_e_salvar_gcpp(gcpp):
    if gcpp.qtd_dias_pgto is None and gcpp.valor_pgto is None:
        gcpp.qtd_dias_pgto = gcpp.qtd_dias_calculado
        gcpp.valor_pgto = gcpp.valor_calculado

    gcpp.status = "apto"
    gcpp.save()


def declinar_e_salvar_gcpp(gcpp):
    gcpp.status = "inapto"
    gcpp.save()


def aplicar_e_salvar_gcpp(gcpp_id, folha_id):
    gcpp = ControlePagamentoPessoal.objects.get(pk=gcpp_id)
    folha = Folha.objects.get(pk=folha_id)
    evento = Evento.objects.get(numero=gcpp.evento.numero)
    contracheque = get_paycheck(gcpp.servidor, folha)

    info_duplicada = (
        contracheque.lancamentos.values("info")
        .annotate(count=Count("info"))
        .filter(
            count__gte=1,
            info=gcpp.info,
            evento=evento,
        )
        .exists()
    )

    success = True
    message = ""
    # Caso tenha duplicidade do campo INFO para os lançamentos
    # e caso a Folha escolhida já possua uma rúbrica com este evento e caso seja o evento 04600
    # não permitir a aplicação
    if (
        info_duplicada
        and contracheque.lancamentos.filter(evento=evento).exists()
        and evento.numero != "04600"
    ):  # FALTA AUXÍLIO ALIMENTAÇÃO
        success = False
        message = f"""
        <p>A Folha escolhida, {contracheque}, já possui uma rúbrica com este evento.
        Por favor escolha outra Folha para aplicar o registro de Pagamento de Pessoal.</p>
        """
    else:
        try:
            create_entry(
                contracheque,
                evento,
                qtd=gcpp.qtd_dias_pgto,
                qtd_max=gcpp.qtd_max_dias,
                installments_paid=gcpp.parcela,
                installments=gcpp.prazo,
                pct=gcpp.pct,
                value=gcpp.valor_pgto,
                base_value=gcpp.valor_base,
                employer_value=gcpp.valor_patronal,
                contribution_base=gcpp.valor_base_prev,
                info=gcpp.info,
                ref_year=gcpp.periodo_ano,
                ref_month=gcpp.periodo_mes,
                insertion_type=5,  # Choice id 5 - Tipo de Inserção: GCPP
            )

            gcpp.status = "pago"
            gcpp.contracheque_aplicado = contracheque
            gcpp.save()
        except:
            success = False
            message = (
                "ERRO ao aplicar em folha o(s) registro(s) de Pagamento de Pessoal."
            )

    return {"success": success, "message": message}


def criar_gcpp(**kwargs):
    servidor_conferido_por = kwargs.get("servidor_conferido_por")
    set_current_user(servidor_conferido_por.user)

    gcpp = ControlePagamentoPessoal.objects.create(
        servidor=kwargs.get("servidor"),
        evento=kwargs.get("evento"),
        qtd_dias_confirmado=kwargs.get("qtd_dias"),
        pct=kwargs.get("pct", None),
        periodo_ano=kwargs.get("periodo_ano"),
        periodo_mes=kwargs.get("periodo_mes"),
        conferido=True,
        conferido_por=servidor_conferido_por,
        modulo_origem=kwargs.get("modulo_origem", None),
        info=kwargs.get("info", None),
    )

    return gcpp


def get_tipo_folha(nome_variavel):
    return Choice.objects.filter(app_label="gfp", name=nome_variavel).values_list(
        "cvalue", flat=True
    )


def valida_tipo_folha(registro, folha):
    """
    Valida se o type_by_possession do Servidor é diferente da Folha selecionada
    """
    tipos_folha_est = get_tipo_folha("TIPO_FOLHA_EST")
    tipos_folha_res = get_tipo_folha("TIPO_FOLHA_RES")
    if (
        registro.servidor.type_by_possession == "EST"
        and folha.tipo_folha.numero not in tipos_folha_est
    ) or (
        registro.servidor.type_by_possession == "RES"
        and folha.tipo_folha.numero not in tipos_folha_res
    ):
        return True
    return False


def remove_gcpp_gcf(falta):
    query = falta.pag_pessoal_faltas.exclude(status="pago")
    if query.exists():
        for gcf in query:
            if gcf.qtd_dias_confirmado > falta.get_days:
                gcf.qtd_dias_confirmado -= falta.get_days
                gcf.save()
            else:
                query.delete()
                break


def remove_dependencia_gcpp(dependencia):
    query = dependencia.pag_pessoal_dependencia.exclude(status="pago")
    if query.exists():
        query.delete()


def remove_gcpp_contracheque(contracheque):
    query = contracheque.pag_pessoal_aplicado.all()
    if query.exists():
        for gcpp in query:
            gcpp.contracheque_removido_texto = gcpp.contracheque_aplicado.__str__()
            gcpp.contracheque_removido = True
            gcpp.contracheque_aplicado = None
            gcpp.status = "inapto"
            gcpp.save()
