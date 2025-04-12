from datetime import datetime
from rh.const import TIPO_DEPENDENTE_IR, TIPO_DEPENDENTE_AUX_CRECHE
from rh.models import Lotacao
from rh.pvf.const import *
from rh.pvf.utils.calendar_utils import get_workers_from_workplace
from standard.models import Choice
from contrib.utils import getLogger
from rh.dayoff.models import Usufruct
from django.db.models import Q

log = getLogger(__name__)


def formart_date_str(date_str, formart="%d/%m/%Y"):
    """
    Converte uma data str do formato '2023-05-21T04:00:00.000Z' para o formato '%d/%m/%Y'.
    Args:
        data: A data no formato '2023-05-21T04:00:00.000Z' a ser convertida.
    Returns:
        A data convertida no formato '%d/%m/%Y'.
    """
    if date_str:
        date_str_z = date_str.replace("Z", "")
        format = "%Y-%m-%dT%H:%M:%S.%f"
        data = datetime.strptime(date_str_z, format)
        new_date_str = data.strftime(formart)
        return new_date_str
    return None


def convert_data(data):
    """
    Converte os dados recebidos no objeto 'data' para o formato esperado.
    Realiza as transformações necessárias nos dados fornecidos, garantindo que estejam
    corretamente formatados de acordo com as especificações definidas pela aplicação.
    Args:
        request (Request): O objeto 'data' contendo os dados a serem convertidos.
    Returns:
        dict: Os dados convertidos para o formato esperado.
    """
    try:
        datetime.strptime(data["start_date"], "%Y-%m-%d")
        is_valid_format = True
    except ValueError:
        is_valid_format = False
    if not is_valid_format:
        data["start_date"] = formart_date_str(data["start_date"], formart="%Y-%m-%d")

    try:
        datetime.strptime(data["end_date"], "%Y-%m-%d")
        is_valid_format = True
    except ValueError:
        is_valid_format = False
    if not is_valid_format:
        data["end_date"] = formart_date_str(data["end_date"], formart="%Y-%m-%d")
    return data


def get_workers(employee):
    """
    Lista de servidores das lotações filhas
    Args:
        employee: servidor responsável pela lotação.
    :returns: (list)
    """
    responsible_workplaces = Lotacao.objects.filter(responsavel=employee.id)
    workplaces = Lotacao.objects.filter(pai__in=responsible_workplaces)
    all_workplaces = workplaces.union(responsible_workplaces)
    return get_workers_from_workplace(workplaces=all_workplaces, employee=employee)


def get_permissions(employee):
    """
    Lista de permissões plantão servidores
    :returns: (list)
    """
    permissons = []
    workplaces = Lotacao.objects.filter(responsavel=employee)
    for workplace in workplaces:
        if workplace.gestor_plantao_dti:
            permissons.append(TYPE_SHIFT_DTI)
        if workplace.gestor_plantao_final_semana:
            permissons.append(
                TYPE_SHIFT_WEEKEND,
            )
        if workplace.gestor_plantao_recesso:
            permissons.append(TYPE_SHIFT_RECESS)
        if workplace.gestor_plantao_eleitoral:
            permissons.append(TYPE_SHIFT_ELECTORAL)
        if workplace.gestor_plantao_pgj:
            permissons.append(TIPO_PLANTAO_PGJ)
    return permissons


def cancel_usufructs():
    """
    Retorna os tipos de usufrutos poderão ser cancelados.
    Returns:
        list: type de usufrutos que podem ser cancelados
    """
    try:
        list_exclude_usufruct = Choice.objects.filter(
            name="PVF_SUB_CONFIGURATION_EXCLUDE_CANCEL_USUFRUCT", active=True
        ).values_list("value")
        list_of_cancelable_usufructs = (
            Choice.objects.filter(name="SUB_CONFIGURATION_CHOICE", active=True)
            .exclude(value__in=[x[0] for x in list_exclude_usufruct])
            .values_list("value")
        )
        return [x[0] for x in list_of_cancelable_usufructs]
    except Exception as e:
        log.error(e)


def expressao_query(filtro):
    q_filtro = None
    for qf in filtro:
        if not q_filtro:
            q_filtro = qf
        else:
            q_filtro = q_filtro | qf
    return q_filtro


def get_lista_params(params):
    lista_dados = []
    for chave, valor in params:
        if chave.startswith("dates["):
            try:
                # Extrair o índice e o nome do campo (start_date ou end_date)
                partes = chave.split("[")
                indice = int(partes[1].replace("]", ""))
                nome = partes[2].replace("]", "")

                if len(lista_dados) <= indice:
                    lista_dados.append({})

                lista_dados[indice][nome] = valor.strip(
                    '"'
                )  # Remova as aspas dos valores

            except (ValueError, IndexError) as e:
                log.error(e)

    return lista_dados


def cria_solicitacao_aux_creche_ir(instancia):
    from rh.pvf.models import PVFSolicitacaoAuxilioCrecheDepenIR

    antecipacao = False
    if instancia.portal_request_type == PORTAL_MATERNITY_LICENSE_TYPE:
        antecipacao = instancia.classificacao == CLASSIF_LICENCA_MATERNIDADE_ANTECIPACAO

    if instancia.portal_request_type in [
        PORTAL_MATERNITY_LICENSE_TYPE,
        PORTAL_ABSENCE_BIRTH_TYPE,
    ]:
        if not antecipacao:
            query_solicitacao = PVFSolicitacaoAuxilioCrecheDepenIR.objects.filter(
                pessoa_familia=instancia.dependent
            ).exclude(
                status__in=[STS_CANCELED_DGP, STS_CANCELED_APPLICANT, STS_REJECTED]
            )

            return not query_solicitacao.exists()
    return False
