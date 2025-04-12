from datetime import datetime

from django.db.models import Q

from contrib.utils import getLogger
from rh.models import MovimentacaoTeletrabalho, Servidor, ServidorLotacao
from rh.pvf.const import REQUEST_STEP_STAND
from rh.pvf.models import SendingTimeSheet

log = getLogger(__name__)


def validate_period_format(value: str) -> tuple:
    """
    Função responsável por converter uma parâmetro de forma " dd/yyyy "
    em uma tupla com dois elementos, mês e ano
    :returns: (tuple) mês, ano
    """
    try:
        month, year = value.split("/")
        return int(month), int(year)

    except Exception as e:
        log.error(e)
        raise Exception(
            " A Formatação das competências deve seguir o seguinte padrão: MM/AAAA (Ex.: 08/2023)"
        )


def upper_capacity(employee):
    """
    Busca a lotação atual do servidor ou lotação superior se for responsável pela lotação atual
    """
    employee_capacity = ServidorLotacao.objects.filter(
        servidor__matricula=employee.matricula, designacao=False, ativo=True
    )
    if employee_capacity:
        upper_capacity = employee_capacity.first().lotacao
        if upper_capacity.responsavel == employee:
            return upper_capacity.pai
        return upper_capacity
    else:
        return None


def get_current_capacity(employee):
    """Retorna a lotação do atual servidor"""
    employee_capacity = ServidorLotacao.objects.filter(
        servidor__matricula=employee.matricula, designacao=False, ativo=True
    )
    if employee_capacity:
        capacity = employee_capacity.first().lotacao
        return capacity
    else:
        return None


def get_immediate_boss(employee):
    """
    Buscar o chefe imediato ou o responsável pela lotação recursivamente
    """
    current_capacity = get_current_capacity(employee)
    _upper_capacity = upper_capacity(employee)
    if not current_capacity:
        return employee.chefe_imediato
    if (
        employee.chefe_imediato
        and current_capacity.responsavel != employee.chefe_imediato
    ):
        if employee.chefe_imediato.afastamento_ativo():
            if employee.chefe_imediato.substitutions():
                return employee.chefe_imediato.substitutions().first().servidor
            else:
                return employee.chefe_imediato
        else:
            return employee.chefe_imediato
    else:
        responsible_stocking = None
        if not _upper_capacity:
            return employee.chefe_imediato
        while not responsible_stocking:
            if (
                _upper_capacity.responsavel
                and _upper_capacity.portal_approver
                and _upper_capacity.responsavel != employee
            ):
                responsible_stocking = _upper_capacity.responsavel
            else:
                if _upper_capacity.pai:
                    stocking_dad = _upper_capacity.pai
                    _upper_capacity = stocking_dad
                else:
                    break

        if not responsible_stocking:
            return employee.chefe_imediato

        if responsible_stocking.afastamento_ativo():
            if responsible_stocking.substitutions():
                return responsible_stocking.substitutions().first().servidor
            else:
                return responsible_stocking
        else:
            return responsible_stocking


def buscar_cargo(employee, possses):
    posses_efetivo = possses.filter(quadro__cargo__tipo_lei_cargo="EF")
    posse_comissionado = possses.filter(quadro__cargo__tipo_lei_cargo__in=("CM", "FC"))
    posse_estagiario = possses.filter(quadro__cargo__tipo_lei_cargo__in=("ES", "RS"))
    cargo = None
    if employee.ativo and posses_efetivo.exists():
        ef = posses_efetivo.latest("data_exercicio")
        cargo = ef.quadro
    elif employee.ativo and posse_comissionado.exists():
        cm = posse_comissionado.latest("data_exercicio")
        cargo = cm.quadro
    elif employee.ativo and posse_estagiario.exists():
        es = posse_estagiario.latest("data_exercicio")
        cargo = es.quadro
    else:
        cargo = "Não encontrado"
    return cargo


def get_data_report(params: dict) -> dict:
    """
    Function: Função responsável pela geração de dados do relatório,
    aplica-se os filtros e organiza os dados a serem retornados
    :returns: (dict)
    """

    data = []

    query = Servidor.objects.filter()

    # Extract params
    employee_pk = params["employee"]
    competence = params["competence"]
    output_format = params["output_format"]
    employee = Servidor.objects.filter(pk=employee_pk).first()
    # Apply filters
    _filter = []
    if employee_pk:
        # query = Servidor.objects.filter(pk=employee_pk).first().subordinados.filter(ativo=True)
        possessions = [
            "EFE",
            "ECM",
            "EFC",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "CMS",
            "REQ",
            "RCM",
            "RFC",
            "REX",
            "CTR",
            "EST",
            "RES",
            "VOL",
            "JCA",
            "EXT",
        ]
        query = Servidor.objects.filter(ativo=True, type_by_possession__in=possessions)

    q_filter = None
    for qf in _filter:
        if not q_filter:
            q_filter = qf
        else:
            q_filter = q_filter & qf
    if q_filter:
        query = query.filter(q_filter)

    if output_format == "PDF":
        pass

    if output_format == "XLS":
        for q in query:
            if employee == get_immediate_boss(q):
                capacity = None
                possessions = q.posses_ativas
                if not q.ativo:
                    possessions = q.posses
                cargo = buscar_cargo(q, possessions)

                employee_capacity = ServidorLotacao.objects.filter(
                    servidor__matricula=q.matricula, designacao=False, ativo=True
                )
                if employee_capacity:
                    capacity = employee_capacity.first().lotacao

                if competence:
                    month, year = validate_period_format(competence)
                    today = datetime.now().date()
                    data_reference = datetime(year, month, 1)
                    sendingtimesheet = SendingTimeSheet.objects.filter(
                        reference_month=month, reference_year=year, employee=q
                    ).exclude(step_current=REQUEST_STEP_STAND)
                    teletrabalho = MovimentacaoTeletrabalho.objects.filter(
                        Q(data_inicio__lte=data_reference)
                        & Q(Q(data_fim__gte=data_reference) | Q(data_fim=None)),
                        servidor=q,
                    )
                    lotacao_teletrabalho = ServidorLotacao.objects.filter(
                        servidor=q, lotacao__pk__in=[52923, 53013], ativo=True
                    )
                    data.append(
                        {
                            "Matrícula": q.matricula,
                            "Nome": q.pessoa_fisica.nome,
                            "Tipo Servidor": q.get_type_by_possession_display(),
                            "Cargo": str(cargo),
                            "Lotação": str(capacity) if capacity else "",
                            "Teletrabalho": (
                                "Sim"
                                if teletrabalho.exists()
                                or lotacao_teletrabalho.exists()
                                else "Não"
                            ),
                            "Enviado?": "Sim" if sendingtimesheet.exists() else "Não",
                            "Data do Envio": (
                                datetime.strftime(
                                    sendingtimesheet.first().date, "%d/%m/%Y"
                                )
                                if sendingtimesheet.exists()
                                else ""
                            ),
                        }
                    )

    order_list = [
        "Matrícula",
        "Nome",
        "Tipo Servidor",
        "Cargo",
        "Lotação",
        "Teletrabalho",
        "Enviado?",
        "Data do Envio",
    ]

    if output_format == "CSV":
        pass

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "keys": order_list,
    }
    return values
