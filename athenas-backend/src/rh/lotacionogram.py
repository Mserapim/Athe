import base64
from datetime import datetime
from django.db.models import Q
from rh.afastamento.models import LicencaInteresseParticular

from rh.models import (
    Lotacao,
    Localidade,
    MovimentacaoAuxiliarCoordenacao,
    MovimentacaoDiligencia,
    MovimentacaoSubstituicao,
    MovimentacaoTeletrabalho,
    Servidor,
    MovimentacaoPosse,
    ServidorLotacao,
)
from standard.models import Choice

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


def filter_data(params, electoral=None):
    """
    Lotações serão ordenadas pela prioridade
    Ordenar as sub-lotações (que possui a lotação de prioridade como lotação superior) por ordem alfabética
    """

    # Extract params
    _cargo = params.get("cargo", None)
    _lotacao = params.get("lotacao", None)
    _nucleo = params.get("nucleo", None)
    _municipio = params.get("municipio", None)
    _types_by_possession = params.get("types_by_possession", None)
    _servidor = params.get("servidor", None)
    _competencia = params.get("competencia", None)
    _comarca_id = params.get("comarca_id", None)
    _comarca = params.get("comarca", "false")
    _keyword = params.get("keyword", None)

    # Apply filters
    _filter = []

    if _competencia:
        month, year = validate_period_format(_competencia)
        _filter.append(
            Q(
                Q(
                    Q(
                        servidores_lotacao__data_vigencia_inicio__month__lte=int(month),
                        servidores_lotacao__data_vigencia_inicio__year=int(year),
                    )
                    | Q(servidores_lotacao__data_vigencia_inicio__year__lt=int(year))
                )
                & Q(
                    Q(
                        Q(
                            servidores_lotacao__data_vigencia_fim__month__gte=int(
                                month
                            ),
                            servidores_lotacao__data_vigencia_fim__year=int(year),
                        )
                        | Q(servidores_lotacao__data_vigencia_fim__year__gt=int(year))
                    )
                    | Q(servidores_lotacao__data_vigencia_fim__isnull=True)
                ),
            )
        )
    else:
        _filter.append(Q(servidores_lotacao__ativo=True))

    if _servidor:
        _filter.append(
            Q(
                servidores_lotacao__servidor__pk=int(_servidor),
                # servidores_lotacao__ativo=True,
            )
        )
    if _keyword:
        _filter.append(
            Q(
                servidores_lotacao__servidor__pessoa_fisica__nome__icontains=_keyword,
                # servidores_lotacao__ativo=True,
            )
        )
    if _cargo:
        _filter.append(
            Q(
                # servidores_lotacao__ativo=True,
                servidores_lotacao__movimentacao_posse__quadro__cargo=int(_cargo),
                servidores_lotacao__movimentacao_posse__ativo=True,
                servidores_lotacao__servidor__ativo=True,
            )
        )

    if _lotacao:
        _filter.append(Q(pk=int(_lotacao)))

    if electoral is False:
        _filter.append(Q(electoral_zone=False))

    if _comarca_id:
        _filter.append(Q(comarca=int(_comarca_id)))

    if _nucleo:
        _filter.append(Q(nucleo=int(_nucleo)))

    if _municipio:
        if _comarca == "true":
            municipio = Localidade.objects.filter(id=int(_municipio)).first()
            if municipio and municipio.comarca:
                _filter.append(Q(comarca__id=int(municipio.comarca.id)))
            else:
                _filter.append(Q(localidade=int(_municipio)))
        else:
            _filter.append(Q(localidade=int(_municipio)))

    if _types_by_possession:
        types_by_possession = _types_by_possession.split(",")
        _filter.append(
            Q(
                servidores_lotacao__servidor__type_by_possession__in=types_by_possession,
                servidores_lotacao__servidor__ativo=True,
            )
        )

    q_filter = None
    for qf in _filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf

    lotacoes_com_prioridade = (
        Lotacao.objects.filter(ativo=True, lotacionograma=True)
        .exclude(Q(prioridade=0) | Q(prioridade__isnull=True))
        .order_by("prioridade")
    )
    lotacoes_sem_prioridade = Lotacao.objects.filter(
        Q(ativo=True, lotacionograma=True)
        & (Q(prioridade=0) | Q(prioridade__isnull=True))
    ).order_by("prioridade")

    if q_filter:
        lotacoes_com_prioridade = lotacoes_com_prioridade.filter(q_filter).distinct()
        lotacoes_sem_prioridade = lotacoes_sem_prioridade.filter(q_filter).distinct()

    lotacoes = [lotacoes_com_prioridade, lotacoes_sem_prioridade]
    return lotacoes


def get_data(params):
    """
    Dados completos do lotacionograma
    """
    _cargo = params.get("cargo", None)
    _types_by_possession = params.get("types_by_possession", None)
    _servidor = params.get("servidor", None)
    _competencia = params.get("competencia", None)

    if _competencia:
        month, year = validate_period_format(_competencia)

    lotacoes = filter_data(params)
    data = []
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
                    designacao=True,
                ).values_list("servidor__pk", flat=True)
                servidores = (
                    Servidor.objects.filter(lotacoes=lotacao, pk__in=servs_lots)
                    .distinct()
                    .order_by("type_by_possession")
                )
            else:
                servs_lots = ServidorLotacao.objects.filter(
                    lotacao=lotacao, ativo=True, designacao=True
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

            titulo = f"{localidade} - LOTAÇÃO: {lotacao.nome}"
            subtitulo = f"{responsavel} - {titular}"
            # nucleo = lotacao.get_nucleo_display() if lotacao.nucleo else None
            nucleo = (
                Choice.objects.get(
                    app_label="rh", name="NUCLEO_CHOICES", value=lotacao.nucleo
                ).label
                if lotacao.nucleo
                else None
            )

            endereco = lotacao.address.last()
            endereco_completo = ""
            if endereco:
                endereco_completo = f"""
                    {endereco.get_tipo_logradouro_display()} 
                    {endereco.logradouro} , 
                    {endereco.numero} - 
                    {endereco.bairro} - 
                    Cep {endereco.cep} - 
                    {endereco.complemento}
                """

            phones = []
            for phone in lotacao.phone.filter():
                phones.append(f"{phone.numero} - {phone.description}")

            localidade = lotacao.localidade
            local = ""
            if localidade:
                local = localidade.nome

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
                            ),
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
                            ),
                        )
                    for mv in mov_dili.filter(servidor=servidor):
                        observations.append(
                            {
                                "observacao": "TITULAR DE VERBA DE DILIGÊNCIA",
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
                                "observacao": "SUBSTITUTO DE VERBA DE DILIGÊNCIA",
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
                        ),
                    )
                for ma in mov_aux.filter(servidor=servidor):
                    observations.append(
                        {
                            "observacao": "AUXILIAR DE COORDENAÇÃO",
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
                            "observacao": "SUBSTITUTO DE AUXILIAR DE COORDENAÇÃO",
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
                if not _competencia:
                    date = datetime.now()
                    year = date.year
                    month = date.month

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
                            Q(data_fim__month__gte=int(month), data_fim__year=int(year))
                            | Q(data_fim__year__gt=int(year))
                        )
                        | Q(data_fim__isnull=True)
                    )
                    & Q(ativo=True)
                )

                for tele in mov_teles:
                    observations.append(
                        {
                            "observacao": f"TELETRABALHO - {tele.get_tipo_ato_display()}",
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
                            "observacao": "LICENCA INTERESSE PARTICULAR",
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
                mov_substistuicoes = MovimentacaoSubstituicao.objects.filter(
                    servidor=servidor,
                    place=lotacao,
                    afastamento__tipo__in=[
                        12,
                    ],
                )
                if _competencia:
                    mov_substistuicoes = mov_substistuicoes.filter(
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
                for mov_subs in mov_substistuicoes:
                    observations.append(
                        {
                            "observacao": f"SUBSTITUTO DE LICENÇA MATERNIDADE: {mov_subs.servidor_substituido.matricula} - {mov_subs.servidor_substituido.pessoa_fisica.nome}",
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
                    Q(
                        ativo=True,
                        servidor=servidor,
                        lotacao=lotacao,
                    )
                )

                servs_lots_membros = servs_lots.filter(
                    Q(
                        servidor__type_by_possession__in=tipos_membro,
                    ),
                    designacao=True,
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
                            "observacao": f"DESIGNAÇÕES DE EXERCÍCIO: {texto_info_serv_lot}",
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
                            "observacao": f"ATRIBUIÇÃO: {texto_atribuicao}",
                        }
                    )

                #  clear data
                c += 1
                if old_type == "" or old_type != type_by_possession:
                    subdata.append(
                        {
                            "tipo_servidor": old_type,
                            "info_servidor": contents,
                        }
                    )
                    old_type = type_by_possession
                    contents = []
                contents.append(
                    {
                        "nome": texto_servidor,
                        "cargo": cargo,
                        "email": servidor.pessoa_fisica.email,
                        "dt_admissao": dt_admissao,
                        "dt_ini_lotacao": dt_ini_lotacao,
                        "observacoes": observations,
                    }
                )
                if c == total_por_lotacao:
                    subdata.append(
                        {
                            "tipo_servidor": old_type,
                            "info_servidor": contents,
                        }
                    )
            data.append(
                {
                    "localidade": local,
                    "endereco": endereco_completo,
                    "phones": phones,
                    "lotacao": titulo,
                    "responsavel": subtitulo,
                    "total": total,
                    "dados": subdata,
                    "nucleo": nucleo,
                }
            )

    return data


def get_data_resume(params):
    """
    dados resumido do lotacionograma
    """
    _cargo = params.get("cargo", None)
    _types_by_possession = params.get("types_by_possession", None)
    _servidor = params.get("servidor", None)
    _keyword = params.get("keyword", None)
    _competencia = params.get("competencia", None)

    if _competencia:
        month, year = validate_period_format(_competencia)

    lotacoes = filter_data(params, electoral=False)
    data = []
    for lots in lotacoes:
        for lotacao in lots:
            if _competencia:
                servs_lots = (
                    ServidorLotacao.objects.filter(
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
                    )
                    .exclude(
                        Q(
                            servidor__type_by_possession__in=[
                                "MBR",
                                "MEL",
                                "MCM",
                                "MEC",
                                "MBR2",
                                "MEL2",
                                "MCM2",
                                "MEC2",
                                "MAP",
                            ],
                            designacao=False,
                        )
                    )
                    .values_list("servidor__pk", flat=True)
                )
                servidores = (
                    Servidor.objects.filter(lotacoes=lotacao, pk__in=servs_lots)
                    .distinct()
                    .order_by("type_by_possession")
                )
            else:
                servs_lots = (
                    ServidorLotacao.objects.filter(lotacao=lotacao, ativo=True)
                    .exclude(
                        Q(
                            servidor__type_by_possession__in=[
                                "MBR",
                                "MEL",
                                "MCM",
                                "MEC",
                                "MBR2",
                                "MEL2",
                                "MCM2",
                                "MEC2",
                                "MAP",
                            ],
                            designacao=False,
                        )
                    )
                    .values_list("servidor__pk", flat=True)
                )
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
            if _keyword:
                servidores = servidores.filter(
                    servidor_lotacao__servidor__pessoa_fisica__nome__icontains=_keyword
                )
            total_por_lotacao = servidores.count()
            if lotacao.responsavel:
                responsavel_nome = lotacao.responsavel.pessoa_fisica.nome
                responsavel = responsavel_nome
            else:
                responsavel_nome = ""
                responsavel = ""

            nucleo = (
                Choice.objects.get(
                    app_label="rh", name="NUCLEO_CHOICES", value=lotacao.nucleo
                )
                if lotacao.nucleo
                else None
            )
            nucleo_label = None
            nucleo_id = None
            if nucleo:
                nucleo_label = nucleo.label
                nucleo_id = nucleo.value

            endereco = lotacao.address.last()
            endereco_completo = ""
            if endereco:
                endereco_completo = f"""
                    {endereco.get_tipo_logradouro_display()} 
                    {endereco.logradouro} , 
                    {endereco.numero} - 
                    {endereco.bairro} - 
                    Cep {endereco.cep} - 
                    {endereco.complemento}
                """

            phones = []
            for phone in lotacao.phone.filter():
                phones.append(f"{phone.numero} - {phone.description}")

            localidade = lotacao.localidade
            # Localidade
            local = ""
            localidade_id = None
            # Comarca
            comarca = ""
            comarca_id = None
            if localidade:
                local = localidade.nome
                localidade_id = localidade.pk
                if localidade.comarca:
                    comarca = localidade.comarca.nome
                    comarca_id = localidade.comarca.pk

            subdata = []
            contents = []
            old_type = ""
            c = 0
            for servidor in servidores:
                observations = []
                type_by_possession = Choice.objects.get(
                    app_label="rh",
                    name="CLASSIF_EMPLOYEE_BY_POSSESSION",
                    cvalue=servidor.type_by_possession,
                ).label
                if old_type == "":
                    old_type = type_by_possession

                nm_servidor = servidor.pessoa_fisica.nome
                texto_servidor = f"{nm_servidor}"

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
                    ).last()
                else:
                    movposse = MovimentacaoPosse.objects.filter(
                        servidor=servidor, ativo=True
                    ).last()

                cargo = ""
                cargo_id = None
                if movposse:
                    if movposse.quadro:
                        cargo = movposse.quadro.cargo.nome
                        cargo_id = movposse.quadro.cargo.pk

                #  clear data
                c += 1

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
                            "afastamento": f"AFASTADO {start_date_absence} - {end_date_absence}"
                        }
                    )
                if old_type == "" or old_type != type_by_possession:
                    subdata.append(
                        {
                            "tipo_servidor": old_type,
                            "info_servidor": contents,
                        }
                    )
                    old_type = type_by_possession
                    contents = []
                contents.append(
                    {
                        "nome": texto_servidor,
                        "cargo": cargo,
                        "cargo_id": cargo_id,
                        "email": servidor.pessoa_fisica.email_institucional,
                        "observacoes": observations,
                    }
                )
                if c == total_por_lotacao:
                    subdata.append(
                        {
                            "tipo_servidor": old_type,
                            "info_servidor": contents,
                        }
                    )
            data.append(
                {
                    "localidade": local,
                    "localidade_id": localidade_id,
                    "comarca": comarca,
                    "comarca_id": comarca_id,
                    "nucleo": nucleo_label,
                    "nucleo_id": nucleo_id,
                    "endereco": endereco_completo,
                    "phones": phones,
                    "lotacao": lotacao.nome,
                    "responsavel": responsavel,
                    "dados": subdata,
                }
            )

    return data
