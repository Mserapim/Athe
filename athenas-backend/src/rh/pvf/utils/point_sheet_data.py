import datetime
from contrib.utils import getLogger, DateUtils
from contrib.middleware import get_current_user, set_current_user
from rh.registerpoint.const import DSR, FALTA, JUSTIFICADO, NORMAL


log = getLogger(__name__)

EXCLUIDO = 3


def create_data_point_sheet(portal_request):
    """Esse Comando irá gerar as pendêncais do folha ponto como saldo negativo e faltas sem justificativas para ser
    utilizada em relatórios."""
    from rh.pvf.models import SendingTimeSheet, PointJustification
    from rh.ponto.models import Falta
    from standard.models import JustificationItem

    from rh.pvf.utils.folha_ponto import data_inicio_fim_referencia
    from rh.pvf.utils.folha_ponto_data import folha_ponto_periodo
    from rh.teletrabalho.utils import dias_teletrabalho_mes

    def criar_pendencias_falta():

        if not Falta.objects.filter(
            servidor=employee, data__lte=day, data_fim__gte=day, request_sts=sheet
        ):
            Falta.objects.create(
                servidor=employee,
                data=day,
                data_fim=day,
                request_sts=sheet,
                origem=1,
                situacao=1,
                justificado=False,
                observacao="",
                payroll=True,
                vertical_progression=True,
                premium_license=True,
            )

    def cria_pendencias_justificativas():
        query = PointJustification.objects.filter(
            employee=employee, start_date__lte=day, end_date__gte=day, cancelado=False
        )

        if query.exists():
            qtd_justificativas = query.count()
            qtd_justificada = 0
            for just_vdf in query:
                if not Falta.objects.filter(
                    servidor=employee,
                    data__gte=just_vdf.start_date,
                    data_fim__lte=just_vdf.end_date,
                    request_sts=sheet,
                ).exclude(situacao=EXCLUIDO):
                    obj_falta = None
                    if (
                        qtd_justificativas != qtd_justificada
                        and just_vdf.fault is None
                        and just_vdf.origem != FERIADO_MUNICIPAL
                    ):
                        justificado = True
                        if JustificationItem.objects.filter(
                            value=just_vdf.reason_type
                        ).exists():
                            query_motivo = JustificationItem.objects.get(
                                value=just_vdf.reason_type
                            )
                            payroll = query_motivo.payroll
                            vertical_progression = query_motivo.vertical_progression
                            premium_license = query_motivo.premium_license

                            if query_motivo.gera_falta == GERA_FALTA:
                                obj_falta = Falta.objects.create(
                                    servidor=employee,
                                    data=just_vdf.start_date,
                                    data_fim=just_vdf.end_date,
                                    request_sts=sheet,
                                    origem=1,
                                    situacao=1,
                                    justificado=justificado,
                                    observacao=just_vdf.observation,
                                    payroll=payroll,
                                    vertical_progression=vertical_progression,
                                    premium_license=premium_license,
                                )
                                obj_falta.point_justification.set([just_vdf])
                                obj_falta.save()
                                qtd_justificada += 1

                        else:
                            payroll = False
                            vertical_progression = False
                            premium_license = False

                            obj_falta = Falta.objects.create(
                                servidor=employee,
                                data=just_vdf.start_date,
                                data_fim=just_vdf.end_date,
                                request_sts=sheet,
                                origem=1,
                                situacao=1,
                                justificado=justificado,
                                observacao=just_vdf.observation,
                                payroll=payroll,
                                vertical_progression=vertical_progression,
                                premium_license=premium_license,
                            )
                            obj_falta.point_justification.set([just_vdf])
                            obj_falta.save()
                            qtd_justificada += 1

    def cria_pendencias():
        marcacoes = len(record["marcacoes"]) if record["marcacoes"] else 0
        if record["tipo"] == JUSTIFICADO:
            cria_pendencias_justificativas()
        elif record["tipo"] == FALTA:
            criar_pendencias_falta()

    GERA_FALTA = 1  # contante para testar se a justificativa vai criar uma falta
    FERIADO_MUNICIPAL = 3

    log.info(
        f">>> [{DateUtils.datetime_to_str(datetime.datetime.now())}] Iniciando a criação das pendências folha ponto >>>>>>>>>>>>>"
    )
    month = portal_request.get_reference_month
    year = portal_request.get_reference_year
    set_current_user(get_current_user())
    sheet = SendingTimeSheet.objects.get(pk=portal_request.pk)
    employee = sheet.employee
    try:

        inicio, fim = data_inicio_fim_referencia(month, year)
        point_records = folha_ponto_periodo(inicio, fim, employee)

        days_teleworks = dias_teletrabalho_mes(month, year, employee)

        for record in point_records:
            day = datetime.datetime.strptime(record["data"], "%d/%m/%Y").date()
            if day not in days_teleworks:
                cria_pendencias()

    except Exception as err:
        log.error(err)

    log.info(
        ">>> [{}] Finalizando a criação das pendências folha ponto".format(
            DateUtils.datetime_to_str(datetime.datetime.now())
        )
    )
