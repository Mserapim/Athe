import base64
from datetime import datetime
from django.db.models import Q
from rh.afastamento.models import LicencaInteresseParticular

from rh.models import (
    Localidade,
    Lotacao,
    MovimentacaoAuxiliarCoordenacao,
    MovimentacaoDiligencia,
    MovimentacaoSubstituicao,
    MovimentacaoTeletrabalho,
    Servidor,
    MovimentacaoPosse,
    ServidorLotacao,
)
from standard.models import Choice
from rh.lotacionogram import filter_data

from contrib.utils import getLogger

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
    """
    Estrutura do relatório:
    ________________________________________________________________________
    |titulo                                                                 |
    |subtitulo                                                              |
    |type_by_possession                                                     |
    |    texto_servidor  |   cargo   |   dt_admissao    |   dt_ini_lotacao  |
    |total_por_lotacao                                                      |
    |_______________________________________________________________________|
    """

    """
    Lotações serão ordenadas pela prioridade
        Ordenar as sub-lotações (que possui a lotação de prioridade como lotação superior) por ordem alfabética
    """

    data = []
    _cargo = params.get("cargo", None)
    _types_by_possession = params.get("types_by_possession", None)
    _servidor = params.get("servidor", None)
    _competencia = params.get("competencia", None)

    if _competencia:
        month, year = validate_period_format(_competencia)

    output_format = params["output_format"]
    order_list = []

    lotacoes = filter_data(params)
    for lots in lotacoes:
        for lotacao in lots:
            localidade = lotacao.localidade.nome
            if _competencia:
                servs_lots = ServidorLotacao.objects.filter(
                    Q(
                        Q(
                            data_vigencia_inicio__month__lte=int(month),
                            data_vigencia_inicio__year=int(year),
                        )
                        | Q(data_vigencia_inicio__year__lt=int(year))
                    )
                    & Q(
                        Q(
                            Q(
                                data_vigencia_fim__month__gte=int(month),
                                data_vigencia_fim__year=int(year),
                            )
                            | Q(data_vigencia_fim__year__gt=int(year))
                        )
                        | Q(data_vigencia_fim__isnull=True)
                    ),
                    lotacao=lotacao,
                ).values_list("servidor__pk", flat=True)
                servidores = (
                    Servidor.objects.filter(lotacoes=lotacao, pk__in=servs_lots)
                    .distinct()
                    .order_by("type_by_possession")
                )
            else:
                servs_lots = ServidorLotacao.objects.filter(
                    lotacao=lotacao, ativo=True
                ).values_list("servidor__pk", flat=True)
                servidores = (
                    Servidor.objects.filter(
                        ativo=True, lotacoes=lotacao, pk__in=servs_lots
                    )
                    .distinct()
                    .order_by("type_by_possession")
                )
            if _cargo:
                servidores = servidores.filter(
                    Q(
                        servidor_lotacao__movimentacao_posse__quadro__cargo=int(_cargo),
                        servidor_lotacao__movimentacao_posse__ativo=True,
                    )
                )
            if _types_by_possession:
                types_by_possession = _types_by_possession.split(",")
                servidores = servidores.filter(
                    type_by_possession__in=types_by_possession
                )
            if _servidor:
                servidores = servidores.filter(
                    servidor_lotacao__servidor__pk=int(_servidor)
                )
            total_por_lotacao = servidores.count()
            total = f"Total: {total_por_lotacao}"
            if lotacao.responsavel:
                responsavel_nome = (
                    lotacao.responsavel.pessoa_fisica.nome
                    if lotacao.responsavel
                    else ""
                )
                responsavel = f"RESPONSÁVEL: {responsavel_nome}"
            else:
                responsavel_nome = ""
                responsavel = ""
            if lotacao.owner:
                titular_nome = lotacao.owner.last().pessoa_fisica.nome
                titular = f"TITULAR: {titular_nome}"
            else:
                titular_nome = ""
                titular = ""

            titulo = f"Comarca {lotacao.comarca} | LOTAÇÃO: {lotacao.nome} | CIDADE: {localidade}"
            subtitulo = f"{responsavel} - {titular}"
            # nucleo = lotacao.get_nucleo_display() if lotacao.nucleo else None
            nucleo = (
                Choice.objects.get(
                    app_label="rh", name="NUCLEO_CHOICES", value=lotacao.nucleo
                ).label
                if lotacao.nucleo
                else None
            )

            subdata = []
            contents = []
            old_type = ""
            c = 0
            for servidor in servidores:
                type_by_possession = Choice.objects.get(
                    app_label="rh",
                    name="CLASSIF_EMPLOYEE_BY_POSSESSION",
                    cvalue=servidor.type_by_possession,
                ).label
                if old_type == "":
                    old_type = type_by_possession

                matricula = servidor.matricula
                nm_servidor = servidor.pessoa_fisica.nome
                texto_servidor = f"{matricula} - {nm_servidor}"
                if _competencia:
                    dt_ini_lotacao = (
                        servidor.servidor_lotacao.filter(
                            Q(
                                Q(
                                    data_vigencia_inicio__month__lte=int(month),
                                    data_vigencia_inicio__year=int(year),
                                )
                                | Q(data_vigencia_inicio__year__lt=int(year))
                            )
                            & Q(
                                Q(
                                    Q(
                                        data_vigencia_fim__month__gte=int(month),
                                        data_vigencia_fim__year=int(year),
                                    )
                                    | Q(data_vigencia_fim__year__gt=int(year))
                                )
                                | Q(data_vigencia_fim__isnull=True)
                            )
                        )
                        .filter(lotacao=lotacao)
                        .order_by("data_vigencia_inicio")
                        .last()
                        .data_vigencia_inicio.strftime("%d/%m/%Y")
                    )
                else:
                    dt_ini_lotacao = (
                        servidor.servidor_lotacao.filter(ativo=True, lotacao=lotacao)
                        .order_by("data_vigencia_inicio")
                        .last()
                        .data_vigencia_inicio.strftime("%d/%m/%Y")
                    )

                if _competencia:
                    movposse = MovimentacaoPosse.objects.filter(
                        Q(
                            Q(
                                data_exercicio__month__lte=int(month),
                                data_exercicio__year=int(year),
                            )
                            | Q(data_exercicio__year__lt=int(year))
                        )
                        & Q(
                            Q(
                                Q(
                                    data_desligamento__month__gte=int(month),
                                    data_desligamento__year=int(year),
                                )
                                | Q(data_desligamento__year__gt=int(year))
                            )
                            | Q(data_desligamento__isnull=True)
                        ),
                        servidor=servidor,
                    )
                else:
                    movposse = MovimentacaoPosse.objects.filter(
                        servidor=servidor, ativo=True
                    )

                tipos_membro = [
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                ]
                cargo = ""
                dt_admissao = ""
                if movposse.last():
                    if servidor.type_by_possession in tipos_membro:
                        dt_admissao = (
                            MovimentacaoPosse.objects.filter(servidor=servidor)
                            .first()
                            .data_posse.strftime("%d/%m/%Y")
                        )
                    else:
                        dt_admissao = movposse.last().data_posse.strftime("%d/%m/%Y")
                    if movposse.last().quadro:
                        cargo = movposse.last().quadro.cargo.nome

                # observations
                observations = []
                if not _competencia:
                    data_hoje = datetime.now().date()

                if lotacao.comarca:
                    mov_dili = MovimentacaoDiligencia.objects.filter(
                        comarca=lotacao.comarca
                    )
                    if _competencia:
                        mov_dili = mov_dili.filter(
                            Q(
                                Q(
                                    data_inicio__month__lte=int(month),
                                    data_inicio__year=int(year),
                                )
                                | Q(data_inicio__year__lt=int(year))
                            )
                            & Q(
                                Q(
                                    Q(
                                        data_fim__month__gte=int(month),
                                        data_fim__year=int(year),
                                    )
                                    | Q(data_fim__year__gt=int(year))
                                )
                                | Q(data_fim__isnull=True)
                            )
                        )
                    else:
                        mov_dili = mov_dili.filter(
                            Q(data_inicio__lte=data_hoje)
                            & Q(Q(data_fim__gte=data_hoje) | Q(data_fim__isnull=True)),
                        )
                    for mv in mov_dili.filter(servidor=servidor):
                        observations.append(
                            {
                                "observation": "TITULAR DE VERBA DE DILIGÊNCIA",
                                "dt_inicio": (
                                    mv.data_inicio.strftime("%d/%m/%Y")
                                    if mv.data_inicio
                                    else ""
                                ),
                                "dt_fim": (
                                    mv.data_fim.strftime("%d/%m/%Y")
                                    if mv.data_fim
                                    else ""
                                ),
                            }
                        )
                    for mv in mov_dili.filter(substituto=servidor):
                        observations.append(
                            {
                                "observation": "SUBSTITUTO DE VERBA DE DILIGÊNCIA",
                                "dt_inicio": (
                                    mv.data_inicio.strftime("%d/%m/%Y")
                                    if mv.data_inicio
                                    else ""
                                ),
                                "dt_fim": (
                                    mv.data_fim.strftime("%d/%m/%Y")
                                    if mv.data_fim
                                    else ""
                                ),
                            }
                        )

                    if servidor.get_afastamentos().exists():
                        start_date_absence = (
                            servidor.get_afastamentos()
                            .first()
                            .baselicencaafastamento.data_inicio.strftime("%d/%m/%Y")
                            if servidor.get_afastamentos()
                            .first()
                            .baselicencaafastamento.data_inicio
                            else ""
                        )
                        end_date_absence = (
                            servidor.get_afastamentos()
                            .first()
                            .baselicencaafastamento.data_fim.strftime("%d/%m/%Y")
                            if servidor.get_afastamentos()
                            .first()
                            .baselicencaafastamento.data_fim
                            else ""
                        )
                        observations.append(
                            {
                                "observation": "AFASTAMENTO",
                                "dt_inicio": start_date_absence,
                                "dt_fim": end_date_absence,
                            }
                        )

                mov_aux = MovimentacaoAuxiliarCoordenacao.objects.filter(
                    servidor_designacao__lotacao=lotacao
                )
                if _competencia:
                    mov_aux = mov_aux.filter(
                        Q(
                            Q(
                                data_inicio__month__lte=int(month),
                                data_inicio__year=int(year),
                            )
                            | Q(data_inicio__year__lt=int(year))
                        )
                        & Q(
                            Q(
                                Q(
                                    data_fim__month__gte=int(month),
                                    data_fim__year=int(year),
                                )
                                | Q(data_fim__year__gt=int(year))
                            )
                            | Q(data_fim__isnull=True)
                        )
                    )
                else:
                    mov_aux = mov_aux.filter(
                        Q(data_inicio__lte=data_hoje)
                        & Q(Q(data_fim__gte=data_hoje) | Q(data_fim__isnull=True)),
                    )
                for ma in mov_aux.filter(servidor=servidor):
                    observations.append(
                        {
                            "observation": "AUXILIAR DE COORDENAÇÃO",
                            "dt_inicio": (
                                ma.data_inicio.strftime("%d/%m/%Y")
                                if ma.data_inicio
                                else ""
                            ),
                            "dt_fim": (
                                ma.data_fim.strftime("%d/%m/%Y") if ma.data_fim else ""
                            ),
                        }
                    )
                for ma in mov_aux.filter(substituto=servidor):
                    observations.append(
                        {
                            "observation": "SUBSTITUTO DE AUXILIAR DE COORDENAÇÃO",
                            "dt_inicio": (
                                ma.data_inicio.strftime("%d/%m/%Y")
                                if ma.data_inicio
                                else ""
                            ),
                            "dt_fim": (
                                ma.data_fim.strftime("%d/%m/%Y") if ma.data_fim else ""
                            ),
                        }
                    )

                mov_teles = MovimentacaoTeletrabalho.objects.filter(servidor=servidor)

                if _competencia:
                    mov_teles = mov_teles.filter(
                        Q(
                            Q(
                                data_inicio__month__lte=int(month),
                                data_inicio__year=int(year),
                            )
                            | Q(data_inicio__year__lt=int(year))
                        )
                        & Q(
                            Q(
                                Q(
                                    data_fim__month__gte=int(month),
                                    data_fim__year=int(year),
                                )
                                | Q(data_fim__year__gt=int(year))
                            )
                            | Q(data_fim__isnull=True)
                        )
                    )
                else:
                    mov_teles = mov_teles.filter(
                        Q(data_inicio__lte=data_hoje),
                        Q(data_fim__gte=data_hoje) | Q(data_fim__isnull=True),
                    )
                for tele in mov_teles:
                    observations.append(
                        {
                            "observation": f"TELETRABALHO - {tele.get_tipo_ato_display()}",
                            "dt_inicio": (
                                tele.data_inicio.strftime("%d/%m/%Y")
                                if tele.data_inicio
                                else ""
                            ),
                            "dt_fim": (
                                tele.data_fim.strftime("%d/%m/%Y")
                                if tele.data_fim
                                else ""
                            ),
                        }
                    )

                for lic_particular in LicencaInteresseParticular.objects.filter(
                    servidor=servidor,
                    designation_exercise__movimentacao_posse=movposse.last(),
                ):
                    observations.append(
                        {
                            "observation": "LICENCA INTERESSE PARTICULAR",
                            "dt_inicio": (
                                lic_particular.data_inicio.strftime("%d/%m/%Y")
                                if lic_particular.data_inicio
                                else ""
                            ),
                            "dt_fim": (
                                lic_particular.data_fim.strftime("%d/%m/%Y")
                                if lic_particular.data_fim
                                else ""
                            ),
                        }
                    )
                mov_substituicoes = MovimentacaoSubstituicao.objects.filter(
                    servidor=servidor,
                    place=lotacao,
                    afastamento__tipo__in=[
                        12,
                    ],
                )
                if _competencia:
                    mov_substituicoes = mov_substituicoes.filter(
                        Q(
                            Q(
                                data_inicio__month__lte=int(month),
                                data_inicio__year=int(year),
                            )
                            | Q(data_inicio__year__lt=int(year))
                        )
                        & Q(
                            Q(
                                Q(
                                    data_fim__month__gte=int(month),
                                    data_fim__year=int(year),
                                )
                                | Q(data_fim__year__gt=int(year))
                            )
                            | Q(data_fim__isnull=True)
                        ),
                    )
                else:
                    mov_substituicoes = mov_substituicoes.filter(
                        Q(data_inicio__lte=data_hoje)
                        & Q(Q(data_fim__gte=data_hoje) | Q(data_fim__isnull=True)),
                    )
                for mov_subs in mov_substituicoes:
                    observations.append(
                        {
                            "observation": f"SUBSTITUTO DE LICENÇA MATERNIDADE: {mov_subs.servidor_substituido.matricula} - {mov_subs.servidor_substituido.pessoa_fisica.nome}",
                            "dt_inicio": (
                                mov_subs.data_inicio.strftime("%d/%m/%Y")
                                if mov_subs.data_inicio
                                else ""
                            ),
                            "dt_fim": (
                                mov_subs.data_fim.strftime("%d/%m/%Y")
                                if mov_subs.data_fim
                                else ""
                            ),
                        }
                    )

                info_serv_lot = {
                    "Provisória": False,
                    "Responsável": False,
                    "Por portaria": False,
                    "Afastável": False,
                    "Comissão": False,
                    "Coordenador": False,
                    "Com Prejuízo": False,
                    "Sem Prejuízo": False,
                    "Coadjuvando": False,
                    "Colaborando": False,
                    "Adjunto": False,
                }

                servs_lots = ServidorLotacao.objects.filter(
                    Q(ativo=True, servidor=servidor, lotacao=lotacao, designacao=True)
                )

                servs_lots_membros = servs_lots.filter(
                    Q(
                        servidor__type_by_possession__in=tipos_membro,
                    )
                )

                for serv_lot in servs_lots_membros:
                    if serv_lot.provisorio:
                        info_serv_lot["Provisória"] = True
                    if serv_lot.responsible:
                        info_serv_lot["Responsável"] = True
                    if serv_lot.ordinance:
                        info_serv_lot["Por portaria"] = True
                    if serv_lot.owner:
                        info_serv_lot["Afastável"] = True
                    if serv_lot.commission:
                        info_serv_lot["Comissão"] = True
                    if serv_lot.coordinator:
                        info_serv_lot["Coordenador"] = True

                    if serv_lot.prejudice == 1:
                        info_serv_lot["Com Prejuízo"] = True
                    elif serv_lot.prejudice == 2:
                        info_serv_lot["Sem Prejuízo"] = True

                    if serv_lot.action == 1:
                        info_serv_lot["Coadjuvando"] = True
                    elif serv_lot.action == 2:
                        info_serv_lot["Colaborando"] = True
                    elif serv_lot.action == 3:
                        info_serv_lot["Adjunto"] = True

                texto_info_serv_lot = ""
                for info in info_serv_lot:
                    if info_serv_lot[info]:
                        if texto_info_serv_lot == "":
                            texto_info_serv_lot = info
                        else:
                            texto_info_serv_lot = f"{texto_info_serv_lot} - {info}"

                if texto_info_serv_lot != "":
                    observations.append(
                        {
                            "observation": f"DESIGNAÇÕES DE EXERCÍCIO: {texto_info_serv_lot}",
                            "dt_inicio": (
                                servs_lots.first().data_vigencia_inicio.strftime(
                                    "%d/%m/%Y"
                                )
                                if servs_lots.first().data_vigencia_inicio
                                else ""
                            ),
                            "dt_fim": (
                                servs_lots.first().data_vigencia_fim.strftime(
                                    "%d/%m/%Y"
                                )
                                if servs_lots.first().data_vigencia_fim
                                else ""
                            ),
                        }
                    )

                texto_atribuicao = ""
                for serv_lot in servs_lots:
                    if serv_lot.atribuicao:
                        texto_atribuicao = serv_lot.atribuicao.descricao

                if texto_atribuicao != "":
                    observations.append(
                        {
                            "observation": f"ATRIBUIÇÃO: {texto_atribuicao}",
                            "dt_inicio": "",
                            "dt_fim": "",
                        }
                    )

                #  clear data
                c += 1
                if old_type == "" or old_type != type_by_possession:
                    subdata.append(
                        {
                            "type_by_possession": old_type,
                            "contents": contents,
                        }
                    )
                    old_type = type_by_possession
                    contents = []
                contents.append(
                    {
                        "texto_servidor": texto_servidor,
                        "cargo": cargo,
                        "dt_admissao": dt_admissao,
                        "dt_ini_lotacao": dt_ini_lotacao,
                        "observations": observations,
                    }
                )
                if c == total_por_lotacao:
                    subdata.append(
                        {
                            "type_by_possession": old_type,
                            "contents": contents,
                        }
                    )
            if output_format == "PDF":
                data.append(
                    {
                        "titulo": titulo,
                        "subtitulo": subtitulo,
                        "total": total,
                        "subdata": subdata,
                        "nucleo": nucleo,
                    }
                )
            if output_format == "CSV":
                for sub in subdata:
                    for content in sub["contents"]:
                        observations = content.pop("observations")
                        observation_str = ""
                        dt_inicio_str = ""
                        dt_fim_str = ""

                        for observation in observations:
                            observation_str = (
                                observation_str + observation["observation"] + "\n"
                            )
                            dt_inicio_str = (
                                dt_inicio_str + observation["dt_inicio"] + "\n"
                            )
                            dt_fim_str = dt_fim_str + observation["dt_fim"] + "\n"

                        data.append(
                            {
                                "Localidade": localidade,
                                "Lotação": lotacao.nome,
                                "Titular": titular_nome,
                                "Responsável": responsavel_nome,
                                "Núcleo": nucleo,
                                "Observação": observation_str,
                                "Data Início": dt_inicio_str,
                                "Data Fim": dt_fim_str,
                                "Servidor/Membro": content["texto_servidor"],
                                "Cargo": content["cargo"],
                                "Data de admissão": content["dt_admissao"],
                                "Data Início na Lotação": content["dt_ini_lotacao"],
                            }
                        )

                order_list = [
                    "Localidade",
                    "Lotação",
                    "Responsável",
                    "Titular",
                    "Núcleo",
                    "Servidor/Membro",
                    "Cargo",
                    "Data de admissão",
                    "Data Início na Lotação",
                    "Observação",
                    "Data Início",
                    "Data Fim",
                ]

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": order_list,
    }
    return values
