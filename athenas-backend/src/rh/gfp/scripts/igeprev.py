# -*- coding: utf-8 -*-
import datetime

import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db.models import Min, Q, Sum

from contrib.daterange import NewDateRange
from rh.gfp.models import Folha, FolhaEvento, MovimentacaoProgressao, Periodo
from rh.models import CargaHoraria, Servidor, UnidadeAdministrativa
from rh.socialsecurity.models import EmploymentBond
from standard.models import Configuration


def from_month(year, month):
    return NewDateRange.from_month(year, month)


def get_abono(servidor, year, month):
    dr = from_month(year, month)
    return (
        servidor.extrapaymentperiods.filter(
            start_validity__lt=dr.last, extra_payment__slug="ABONO-PERMANENCIA"
        )
        .exclude(end_validity__isnull=False, end_validity__lt=dr.last)
        .first()
    )


def inicio_abono_permanencia(servidor, year, month):
    abono = get_abono(servidor, year, month)
    return abono.start_validity.strftime("%d/%m/%Y") if abono else ""


def tem_abono(servidor, year, month):
    abono = get_abono(servidor, year, month)
    if abono:
        return 1
    else:
        return 2


def situacao_servidor(servidor, year, month):
    dr = from_month(year, month)
    data = dr.last
    if servidor.departures(data, data).filter(tipo=20).exists():
        if servidor.departures(data, data).filter(tipo=20).last().remunerado:
            return 4
        else:
            return 5
    elif servidor.departures(data, data).filter(tipo=21).exists():
        return 9
    elif servidor.departures(data, data).filter(tipo=30).exists():
        return 10
    elif servidor.requested:
        requisicao = servidor.movimentacaopessoal_set.filter(
            Q(movimentacaorequisicao__periodo__data_inicio__lte=data)
            & Q(
                Q(movimentacaorequisicao__periodo__data_fim__gte=data)
                | Q(movimentacaorequisicao__periodo__data_fim=None)
            )
        ).last()
        if (
            requisicao
            and requisicao.movimentacaorequisicao
            and requisicao.movimentacaorequisicao.onus == 2
        ):
            return 6
        else:
            return 7
    elif not servidor.departures(data, data).exclude(
        tipo__in=[7, 8, 9, 10, 11, 12, 13, 34, 35, 37, 43, 42, 45]
    ):
        return 1
    elif servidor.departures(data, data).exclude(
        tipo__in=[7, 8, 9, 10, 11, 12, 13, 34, 35, 37, 43, 42, 45]
    ):
        if (
            servidor.departures(data, data)
            .exclude(tipo__in=[7, 8, 9, 10, 11, 12, 13, 34, 35, 37, 43, 42, 45])
            .last()
            .remunerado
        ):
            return 2
        else:
            return 3

    return 11


def tipo_servidor(servidor):
    if servidor.type_by_possession in ["EFE", "MBR", "MEL", "MBR2", "MEL2"]:
        return 1
    elif servidor.type_by_possession in ["ECM", "MCM", "MEC", "EFC", "MCM2", "MEC2"]:
        return 2
    else:
        return 4


def get_date_entry_into_public_service(servidor):
    return (
        EmploymentBond.objects.filter(
            retirement_prevision__natural_person=servidor.pessoa_fisica,
            public_employee=True,
        )
        .aggregate(date=Min("begin_date"))
        .get("date")
    )


def get_tempo_cont_anterior_rgps(servidor):
    return (
        EmploymentBond.objects.filter(
            retirement_prevision__natural_person=servidor.pessoa_fisica,
            pension_system=1,
            begin_date__lt=servidor.data_exercicio,
        )
        .aggregate(total=Sum("liquid_days"))
        .get("total")
        or 0
    )


def get_regime(servidor):
    ss = servidor.get_socialsecurity_by_validity()
    return ss.mass_segregation_plan
    # if FolhaEvento.objects.filter(contracheque=contracheque, evento__genre_event__genre_number='905').exists():
    #     return 1
    # if FolhaEvento.objects.filter(contracheque=contracheque, evento__genre_event__genre_number='900').exists():
    #     return 2

    # return 1


def get_b_populacao(servidor):

    ssc = servidor.get_socialsecurity_by_validity()
    regime_social_security = ssc.regime if ssc else None
    if regime_social_security == 3:
        return 8
    elif servidor.type_by_possession in [
        "MBR",
        "MEL",
        "MCM",
        "MEC",
        "MBR2",
        "MEL2",
        "MCM2",
        "MEC2",
    ]:
        return 1
    else:
        return 7


def get_c_populacao(servidor):
    ssc = servidor.get_socialsecurity_by_validity()
    regime_social_security = ssc.regime if ssc else None
    if regime_social_security == 3:
        return 8
    elif servidor.pessoa_fisica.necessidade_especial:
        return 2
    else:
        return 1


def get_payroll_base(year, month):
    return Folha.objects.filter(
        tipo_folha__titulo="NORMAL", periodo__mes=month, periodo__ano=year
    ).first()


def get_base_calculo_prev(servidor, year, month):
    dr = from_month(year, month)
    total = (
        FolhaEvento.objects.filter(
            contracheque__servidor=servidor,
            contracheque__folha=get_payroll_base(year, month),
            evento__numero__in=["90000", "90500"],
        )
        .aggregate(Sum("valor_base"))
        .get("valor_base__sum")
    )
    if not total:
        prog = (
            MovimentacaoProgressao.objects.filter(servidor=servidor)
            .filter(data_inicio_vigencia__lt=from_month(year, month).last)
            .order_by("-data_inicio_vigencia")
            .first()
        )
        posse = get_posse_atual(servidor, year, month)
        total = 0
        if prog and posse:
            salarios = posse.quadro.cargo.get_salarios(dr.first, dr.last, prog.salario)
            if salarios:
                total = salarios[-1][1].valor

    return total


def get_contrib_prev(servidor, year, month):
    total = (
        FolhaEvento.objects.filter(
            contracheque__servidor=servidor,
            contracheque__folha=get_payroll_base(year, month),
            evento__numero__in=["90000", "90500"],
        )
        .aggregate(total=Sum("valor"))
        .get("total")
    )

    return total or 0


def get_remuneracao_total(servidor, year, month):
    total = (
        FolhaEvento.objects.filter(
            contracheque__servidor=servidor,
            contracheque__folha=get_payroll_base(year, month),
            evento__carater__in=[1, 9, 13, 15, 21],
            evento__specie_event__specie_number="00",
        )
        .aggregate(total=Sum("value"))
        .get("total")
    )
    return total or get_base_calculo_prev(servidor, year, month)


def get_posse_atual(servidor, year, month):
    dr = from_month(year, month)
    di = dr.first
    df = dr.last
    return (
        servidor.get_posses_ativas(di, df)
        .filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"])
        .last()
    )


def get_conjuge(servidor):
    return servidor.dependentes.filter(tipo=1).first()


def get_workload(employee):
    workload = 35
    workloads = CargaHoraria.objects.filter(servidor=employee, data_fim=None)
    if workloads.exists():
        if workloads.last().quantidade:
            workload = int(workloads.last().quantidade)
    if not employee.ativo:
        workload = 0
    if workload > 35:
        workload = 35
    if workload <= 0:
        workload = 35
    if workload == "":
        workload = 35
    return str(workload)


def get_query_dependents(servidor, year, month=12):
    dr = from_month(year, month)
    return (
        servidor.dependentes.filter(dependencias__tipo=5)
        .filter(Q(data_fim__isnull=True) | Q(data_fim__gt=dr.first))
        .order_by("-pessoa_fisica__data_nascimento")
    )


def get_constitutional_ceiling(servidor, year, month):
    period = Periodo.objects.get(ano=year, mes=month)
    if servidor.type_by_possession in [
        "MBR",
        "MEL",
        "MCM",
        "MEC",
        "MBR2",
        "MEL2",
        "MCM2",
        "MEC2",
    ]:
        return period.salario_teto_membros
    else:
        return period.salario_teto_adm


def get_capacity_dependent(dependent):
    return 2 if dependent.capacidade == 2 or dependent.incapacity else 1


def get_type_of_dependency(dependent):
    from_to = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 8,
        7: 9,
        8: 6,
        9: 7,
        10: 10,
        11: 10,
        14: 11,
        16: 12,
    }
    return from_to.get(dependent.tipo, 99)


def run(year, month, sep=";"):
    with open(f"igeprev_atuarial_{year:04d}_{month:02d}.txt", "w") as fs, open(
        f"igeprev_atuarial_dep_{year:04d}_{month:02d}.txt", "w"
    ) as fd:
        # folha = Folha.objects.get(tipo_folha__titulo='NORMAL', periodo__mes=month, periodo__ano=year)
        q_employeers = Servidor.objects.filter(
            type_by_possession__in=[
                "EFE",
                "ECM",
                "MBR",
                "MEL",
                "MCM",
                "MEC",
                "EFC",
                "MBR2",
                "MEL2",
                "MCM2",
                "MEC2",
            ]
        )
        #  'REQ', 'RCM', 'RFC',
        cfg = Configuration.get_or_create("gfp")
        uadm = UnidadeAdministrativa.objects.get(pk=cfg.get("orgao"))
        for servidor in q_employeers:
            posse_ativa = get_posse_atual(servidor, year, month)
            if not posse_ativa:
                continue
            ssc = servidor.get_socialsecurity_by_validity()
            print(servidor)
            register = [
                year,
                month,
                17,  # CÓDIGO DO ENTE NO IBGE
                f"{uadm.federative_body.pessoa_juridica}",  # NOME DO ENTE
                "TO",  # SIGLA DA UF DO ENTE
                2 if ssc.regime == 3 else 1,  # COMPOSIÇÃO DA MASSA
                get_regime(servidor),  # TIPO DE FUNDO
                uadm.pessoa_juridica.cnpj,  # CNPJ
                uadm.pessoa_juridica.nome,  # NOME DO ÓRGÃO/ENTIDADE
                uadm.poder,  # CÓDIGO DO PODER
                1,  # CÓDIGO DO TIPO  DE PODER
                3 if ssc.regime == 3 else 1,  # CÓDIGO DO TIPO DE POPULAÇÃO COBERTA
                get_b_populacao(servidor),  # CÓDIGO DO TIPO DE CARGO
                get_c_populacao(servidor),  # CÓDIGO DO CRITÉRIO DE ELEGIBILIDADE
                servidor.matricula,  # IDENTIFICAÇÃO DO SERVIDOR (matrícula)
                servidor.pessoa_fisica.cpf,  # IDENTIFICAÇÃO DO SERVIDOR (CPF)
                servidor.pessoa_fisica.pis_pasep.numero,  # IDENTIFICAÇÃO DO SERVIDOR (PIS-PASEP)
                (
                    1 if servidor.pessoa_fisica.sexo == "F" else "2"
                ),  # CÓDIGO DO SEXO DO SERVIDOR
                servidor.pessoa_fisica.estado_civil,  # CÓDIGO DO ESTADO CIVIL  DO SERVIDOR
                servidor.pessoa_fisica.data_nascimento.strftime(
                    "%d/%m/%Y"
                ),  # DATA DE NASCIMENTO DO SERVIDOR
                situacao_servidor(
                    servidor, year, month
                ),  # CÓDIGO DA SITUAÇÃO FUNCIONAL SERVIDOR(na competência da base cadastral da avaliação atuarial)
                tipo_servidor(servidor),  # CÓDIGO DO TIPO DE VÍNCULO
                get_date_entry_into_public_service(servidor).strftime(
                    "%d/%m/%Y"
                ),  # DATA DE INGRESSO NO SERVIÇO PÚBLICO
                servidor.data_exercicio.strftime(
                    "%d/%m/%Y"
                ),  # DATA DE INGRESSO NO ENTE
                (
                    posse_ativa.data_exercicio.strftime("%d/%m/%Y")
                    if posse_ativa
                    else ""
                ),  # DATA DE INGRESSO NA CARREIRA ATUAL
                (
                    posse_ativa.quadro.cargo.carreira.nome
                    if posse_ativa.quadro.cargo.carreira
                    else ""
                ),  # NOME DA CARREIRA ATUAL
                (
                    posse_ativa.data_exercicio.strftime("%d/%m/%Y")
                    if posse_ativa
                    else ""
                ),  # DATA DE INGRESSO NO CARGO ATUAL
                (
                    posse_ativa.quadro.cargo.nome if posse_ativa else ""
                ),  # NOME DO CARGO ATUAL
                get_base_calculo_prev(
                    servidor, year, month
                ),  # BASE DE CÁLCULO MENSAL DO SERVIDOR
                get_remuneracao_total(
                    servidor, year, month
                ),  # REMUNERAÇÃO MENSAL TOTAL DO SERVIDOR
                get_contrib_prev(servidor, year, month),  # CONTRIBUIÇÃO MENSAL
                get_tempo_cont_anterior_rgps(
                    servidor
                ),  # TEMPO DE CONTRIBUIÇÃO DO SERVIDOR PARA O RGPS, ANTERIOR À ADMISSÃO NO ENTE
                "",  # TEMPO DE CONTRIBUIÇÃO DO SERVIDOR PARA OUTROS "RPPS DA ESFERA MUNICIPAL", ANTERIOR À ADMISSÃO NO ENTE
                "",  # TEMPO DE CONTRIBUIÇÃO DO SERVIDOR PARA OUTROS "RPPS DA ESFERA ESTADUAL", ANTERIOR À ADMISSÃO NO ENTE
                "",  # TEMPO DE CONTRIBUIÇÃO DO SERVIDOR PARA OUTROS "RPPS DA ESFERA FEDERAL", ANTERIOR À ADMISSÃO NO ENTE
                get_query_dependents(
                    servidor, year, month
                ).count(),  # NÚMERO DE DEPENDENTES DO SERVIDOR
                tem_abono(
                    servidor, year, month
                ),  # INDICADOR DE RECEBIMENTO DE ABONO DE PERMANÊNCIA
                inicio_abono_permanencia(
                    servidor, year, month
                ),  # DATA DE INÍCIO DE RECEBIMENTO DO ABONO DE PERMANÊNCIA
                2,  # PREVIDÊNCIA COMPLEMENTAR
                get_constitutional_ceiling(
                    servidor, year, month
                ),  # TETO CONSTITUCIONAL REMUNERATÓRIO ESPECÍFICO (DOS SERVIDORES DO RESPECTIVO PODER)
                "",  # DATA PROVAVEL DE APOSENTADORIA
            ]

            for dep in get_query_dependents(servidor, year, month):
                print(f">>> {dep}")
                register_dep = [
                    year,  # ANO DE REFERÊNCIA (20XX)
                    month,  # MÊS (jan =01;  fev = 02...)
                    17,  # CODIGO DO ENTE NO IBGE
                    f"{uadm.federative_body.pessoa_juridica}",  # NOME DO ENTE Nome do Município ou Governo do Estado
                    "TO",  # SIGLA DA UF DO ENTE# SIGLA DA UF DO ENTE Sigla do UF do Município ou do Estado
                    (
                        2 if ssc.regime == 3 else 1
                    ),  # COMPOSIÇÃO DA MASSA 1 - Civil 2 - Militar
                    get_regime(
                        servidor
                    ),  # TIPO DE FUNDO 1 - Plano Previdenciário 2 - Plano Financeiro 3 - Mantidos pelo Tesouro
                    uadm.pessoa_juridica.cnpj,  # CNPJ  do órgão ou entidade ao qual o instituidor está vinculado, conforme informado no DIPR
                    uadm.pessoa_juridica.nome,  # NOME DO ÓRGÃO/ENTIDADE
                    uadm.poder,  # CÓDIGO DO PODER 1 - Executivo 2 - Legislativo 3 - Judiciário 4 - Ministério Público 5 - Tribunal de Contas 6 - Defensoria Pública
                    1,  # CÓDIGO DO TIPO  DE PODER 1 - Administração Direta 2 - Administração Indireta
                    servidor.matricula,  # MATRÍCULA  DO SEGURADO SERVIDOR (POSSÍVEL INSTITUIDOR DE PENSÃO)  (matrícula)
                    servidor.pessoa_fisica.cpf,  # CPF DO SEGURADO SERVIDOR (POSSÍVEL INSTITUIDOR DE PENSÃO) (CPF)
                    servidor.pessoa_fisica.pis_pasep.numero,  # PASEP DO SEGURADO  SERVIDOR (POSSÍVEL INSTITUIDOR DE PENSÃO)  (PIS-PASEP)
                    (
                        1 if servidor.pessoa_fisica.sexo == "F" else "2"
                    ),  # SEXO DO SEGURADO SERVIDOR (POSSÍVEL INSTITUIDOR DE PENSÃO) CÓDIGO DO SEXO DO SERVIDOR 1 - Feminino 2 - Masculino
                    dep.pk,  # IDENTIFICADOR ÚNICO DO DEPENDENTE  Identificador do dependente para ser usado como registro único na base de dados unificada para a avaliação atuarial. Valor único que identifique o registro do dependente e, pode ser utilizado aquele constante do sistema de dados cadastrais já utilizado pelo órgão, desde que elimine possíveis duplicidades de registro.
                    dep.pessoa_fisica.cpf,  # CPF DO DEPENDENTE (CPF)
                    dep.pessoa_fisica.data_nascimento.strftime(
                        "%d/%m/%Y"
                    ),  # DATA DE NASCIMENTO DO DEPENDENTE dd/mm/aaaa
                    (
                        1 if dep.pessoa_fisica.sexo == "F" else "2"
                    ),  # SEXO DO DEPENDENTE 1 - Feminino 2 - Masculino
                    get_capacity_dependent(
                        dep
                    ),  # CONDIÇÃO DO DEPENDENTE 1 - Válido 2 - Inválido
                    get_type_of_dependency(
                        dep
                    ),  # TIPO DE DEPENDÊNCIA DO DEPENDENTE COM O SEGURADO SERVIDOR (POSSÍVEL INSTITUIDOR DE PENSÃO)  1 CÔNJUGUE 2 COMPANHEIRO(A) 3 FILHO(A) MENOR NAO EMANCIPADO(A) 4 FILHO(A) INVÁLIDO(A) 5 PAI(MÃE) COM DEPENDÊNCIA ECONÔMICA 6 ENTEADO(A) MENOR NAO EMANCIPADO(A) COM DEPENDÊNCIA ECONÔMICA 7 ENTEADO(A) INVÁLIDO(A) COM DEPENDÊNCIA ECONÔMICA 8 IRMÃO(A) MENOR NAO EMANCIPADO(A) COM DEPENDÊNCIA ECONÔMICA 9 IRMÃO(A) INVÁLIDO(A) COM DEPENDÊNCIA ECONÔMICA 10 MENOR TUTELADO 11 NETO 12 EX-CÔNJUGE QUE RECEBA PENSÃO DE ALIMENTOS 99 OUTROS
                ]
                line_str_dep = [str(v1) for v1 in register_dep]
                fd.write(f"{sep.join(line_str_dep)}\n")

            line_str = [str(v) for v in register]
            fs.write(f"{sep.join(line_str)}\n")


if __name__ == "__main__":
    sep = input(
        "Script de Geração de Atualização Atuarial. Informe o separador(default=;): "
    ).lower()
    month_year = input(
        "Script de Geração de Atualização Atuarial. Informe o mês(default=datetetime.now()): Ex=month/year "
    ).lower()
    month_year = month_year.split("/")
    print(month_year)
    if len(month_year) == 2:
        month = int(month_year[0])
        year = int(month_year[1])
    else:
        month_year = datetime.datetime.now().date()
        month = month_year.month
        year = month_year.year
    run(year, month)
