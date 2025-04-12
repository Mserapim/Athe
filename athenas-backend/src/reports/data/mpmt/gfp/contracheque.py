from contrib.utils import getLogger
from rh.gfp.models import ContraCheque, FolhaTipo
from rh.models import Servidor
from datetime import datetime
import base64
from rh.models import Servidor
from django.db.models.query_utils import Q
import calendar
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

log = getLogger(__name__)

DEP_IMPOSTO_RENDA = 1
TODOS_TIPOS = 9999


def get_data_report(params):
    data = []
    servidor = Servidor.objects.get(pk=params["servidor"])
    ano = params.get("ano")
    mes = params.get("mes")
    tipo_folha = params.get("tipo_folha")
    inicio = params.get("inicio")
    fim = params.get("fim")
    inicio_mes = params.get("inicio_mes")
    inicio_ano = params.get("inicio_ano")
    fim_mes = params.get("fim_mes")
    fim_ano = params.get("fim_ano")
    contracheque_id = params.get("contracheque_id")

    def get_contracheques():
        contracheques = []
        if inicio:
            if inicio and fim:
                contracheques = ContraCheque.objects.filter(servidor=servidor).filter(
                    (
                        Q(
                            folha__periodo__mes__gte=inicio_mes,
                            folha__periodo__ano=inicio_ano,
                        )
                        | Q(folha__periodo__ano__gt=inicio_ano)
                    )
                    & (
                        Q(folha__periodo__mes__lte=fim_mes, folha__periodo__ano=fim_ano)
                        | Q(folha__periodo__ano__lt=fim_ano)
                    )
                )
            else:
                contracheques = ContraCheque.objects.filter(
                    servidor=servidor,
                    folha__periodo__mes=inicio_mes,
                    folha__periodo__ano=inicio_ano,
                )
            if tipo_folha:
                type_payroll = FolhaTipo.objects.get(pk=tipo_folha)
                contracheques = contracheques.filter(folha__tipo_folha=type_payroll)

        elif contracheque_id:
            contracheques = ContraCheque.objects.filter(pk=contracheque_id)
        else:
            if tipo_folha == TODOS_TIPOS:
                contracheques = ContraCheque.objects.filter(
                    servidor=servidor, folha__periodo__ano=ano, folha__periodo__mes=mes
                )
            else:
                contracheques = ContraCheque.objects.filter(
                    servidor=servidor,
                    folha__periodo__ano=ano,
                    folha__periodo__mes=mes,
                    folha__tipo_folha=tipo_folha,
                )
        return contracheques

    cargo_efetivo, cargo_comissioando, cargo_eletivo = get_cargos(servidor)
    contracheques = get_contracheques()

    if not contracheques:
        raise Exception("Contracheque não disponível.")

    data_servidor = {
        "matricula": servidor.matricula,
        "nome": servidor.pessoa_fisica.nome,
        "data_vinculo": servidor.data_exercicio,
        "data_exercicio": (
            servidor.last_possession.data_exercicio
            if servidor.last_possession
            else servidor.posses.last().data_exercicio
        ),
        "lotacao": get_lotacao(servidor),
        "situacao_funcional": servidor.get_type_by_possession_display(),
        "situacao_previdenciaria": (
            "ATIVO" if servidor.regime_social_security else "INATIVO"
        ),
        "cargo_comissioando": cargo_comissioando,
        "cargo_efetivo": cargo_efetivo,
        "cargo_eletivo": cargo_eletivo,
        "cpf": servidor.pessoa_fisica.cpf,
        "pasep": (
            servidor.pessoa_fisica.pis_pasep.numero
            if servidor.pessoa_fisica.pis_pasep
            else ""
        ),
        "dep_imp_renda": servidor.dependentes.filter(
            dependencias__tipo=DEP_IMPOSTO_RENDA
        ).count(),
        "total_contracheques": contracheques.count(),
    }

    for index, contracheque in enumerate(list(contracheques)):
        mes_ref, ano_ref = contracheque.folha.periodo.__str__().split("/")
        lancamentos = []
        for lancamento in contracheque.lancamentos.exclude(evento__tipo="I"):
            info = f": {lancamento.info}" if lancamento.info else ""
            lancamentos.append(
                {
                    "verba": f"{lancamento.evento.__str__()} {info}",
                    "ref": f"{lancamento.reference_month}/{lancamento.reference_year}",
                    "qtd": int(lancamento.qnt),
                    "prazo": lancamento.prazo_desc.replace("/", " de "),
                    "percen": (
                        "{:.2f}".format(lancamento.pct) if lancamento.pct else "0.00"
                    ),
                    "base": locale.currency(
                        lancamento.valor_base, grouping=True, symbol=False
                    ),
                    "valor": locale.currency(
                        lancamento.correct_value, grouping=True, symbol=False
                    ),
                }
            )

        if int(mes_ref) == 13:
            ref_mes_str = f"13º/{ano_ref}"
        else:
            ref_mes_str = f"{calendar.month_name[int(mes_ref)].upper()}/{ano_ref}"

        data.append(
            {
                "index": index + 1,
                "ref_mes": ref_mes_str,
                "tipo_folha": contracheque.folha.tipo_folha.titulo,
                "banco": contracheque.dado_bancario_pessoa.banco.nome,
                "agencia": contracheque.dado_bancario_pessoa.agencia,
                "conta": contracheque.dado_bancario_pessoa.conta_corrente_completa,
                "ref_salarial_comissonado": contracheque.referencia_salario_comissao,
                "ref_salarial_efetivo": contracheque.referencia_salario_efetivo,
                "ref_salarial_eletivo": contracheque.referencia_salario_eletivo,
                "pensionista": (
                    contracheque.pensioner.nome if contracheque.pensioner else ""
                ),
                "lancamentos": lancamentos,
                "total_bruto": locale.currency(
                    contracheque.total_bruto, grouping=True, symbol=False
                ),
                "descontos": locale.currency(
                    (contracheque.total_bruto - contracheque.total_liquido),
                    grouping=True,
                    symbol=False,
                ),
                "total_liquido": locale.currency(
                    contracheque.total_liquido, grouping=True, symbol=False
                ),
            }
        )

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "data_servidor": data_servidor,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": [],
    }
    return values


def get_cargos(servidor):
    cargo_comissionado = ""
    cargo_efetivo = ""
    cargo_eletivo = ""
    for posse in servidor.get_posses_ativas():
        if (
            posse.quadro
            and posse.quadro.cargo
            and posse.quadro.cargo.tipo_lei_cargo == "CM"
        ):
            cargo_comissionado = posse.quadro.cargo.nome
        elif (
            posse.quadro
            and posse.quadro.cargo
            and posse.quadro.cargo.tipo_lei_cargo == "EL"
        ):
            cargo_eletivo = posse.quadro.cargo.nome
        elif posse.quadro and posse.quadro.cargo:
            cargo_efetivo = posse.quadro.cargo.nome

    return cargo_efetivo, cargo_comissionado, cargo_eletivo


def get_lotacao(servidor):
    lotacao_atual = servidor.workplace_current
    ultima_lotacao = servidor.lotacoes.last()
    if lotacao_atual:
        return lotacao_atual.nome
    elif ultima_lotacao:
        return ultima_lotacao.nome
    return ""
