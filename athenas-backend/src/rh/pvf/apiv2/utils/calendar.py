import datetime as dt
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import unicodedata

from rh.models import Servidor, Lotacao, ServidorLotacao
from rh.afastamento.models import BaseLicencaAfastamento, MovimentacaoSubstituicao
from rh.pvf.models import (
    PortalCancelSchedule,
    PortalRequestAbsence,
    PortalRetificationSchedule,
    ShiftManager,
)
from rh.dayoff.models import Usufruct
from standard.models import Choice
from common.usefulday.models import NonWorkingDay

from contrib.utils import getLogger
from rh.pvf.apiv2.utils.base import get_workers
from rh.pvf.utils.calendar_utils import (
    get_workers_from_workplace,
    get_treatment_pronoun,
    get_status_type_request_absence,
    get_status_type,
)
from rh.dayoff.const import *
from rh.pvf.const import *
from rh.const import CANCELADO, ENCERRADO
from django.db.models.query_utils import Q
import calendar

log = getLogger(__name__)


def get_data_calendar(employee_current, params):
    """
    Este método processa os eventos de calendário de servidores e membros

    Returns:
       list:
    """
    month = params.get("month", None)
    year = params.get("year", None)
    employee_ids = params.getlist("employee_ids[]", None)
    event_types = params.getlist("event_type_ids[]", None)
    keyword = params.get("keyword", None)
    group_ids = params.getlist("group_ids[]", None)
    data = []

    get_event_birthday(data, employee_current, employee_ids, year, month)
    get_event_licenses(data, employee_current, employee_ids, year, month)
    get_non_working_day(data, year, month, employee_current)
    get_event_usufructs(data, employee_current, employee_ids, year, month)
    get_event_substitutions(data, employee_current, employee_ids, year, month)
    get_event_shifts(data, employee_current, employee_ids, year, month)

    if event_types:
        types_int = list(map(int, event_types))
        data = list(filter(lambda ev: ev["event_type"] in types_int, data))

    if group_ids:
        group_int = list(map(int, group_ids))
        data = list(filter(lambda ev: ev["group_id"] in group_int, data))

    if keyword:
        keyword_value_normalized = remove_accents(keyword.lower())
        data = [
            d
            for d in data
            if keyword_value_normalized in remove_accents(d["title"].lower())
        ]

    return data


def get_event_birthday(data, employee_current, employee_ids, year, month):
    try:
        if employee_ids:
            employees = Servidor.objects.filter(pk__in=employee_ids)
            for employee in employees:
                birth_date = employee.pessoa_fisica.data_nascimento
                birthday = dt.date(
                    day=birth_date.day, month=birth_date.month, year=int(year)
                )
                if birthday.month == int(month):
                    if employee.id == employee_current.id:
                        data.append(
                            {
                                "pk": None,
                                "title": "Feliz Aniversário! Parabéns!",
                                "start": birthday,
                                "end": birthday,
                                "event_type": GENERIC_EVENT_BIRTHDAY,
                                "group_id": GROUP_EVENT_BIRTHDAY,
                                "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_BIRTHDAY],
                            }
                        )
                    else:
                        data.append(
                            {
                                "pk": None,
                                "title": "Aniversário de {} ".format(
                                    get_treatment_pronoun(employee)
                                ),
                                "start": birthday,
                                "end": birthday,
                                "event_type": GENERIC_EVENT_BIRTHDAY,
                                "group_id": GROUP_EVENT_BIRTHDAY,
                                "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_BIRTHDAY],
                            }
                        )
        else:
            workers = get_workers(employee_current)
            if employee_current.id not in workers:
                workers.append(employee_current.id)
            workers = Servidor.objects.filter(id__in=workers)
            for worker in workers:
                birth_date = worker.pessoa_fisica.data_nascimento
                birthday = dt.date(
                    day=birth_date.day, month=birth_date.month, year=int(year)
                )
                if birthday.month == int(month):
                    if worker.id == employee_current.id:
                        data.append(
                            {
                                "pk": None,
                                "title": "Feliz Aniversário! Parabéns!",
                                "start": birthday,
                                "end": birthday,
                                "event_type": GENERIC_EVENT_BIRTHDAY,
                                "group_id": GROUP_EVENT_BIRTHDAY,
                                "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_BIRTHDAY],
                            }
                        )
                    else:
                        data.append(
                            {
                                "pk": None,
                                "title": "Aniversário de {} ".format(
                                    get_treatment_pronoun(worker)
                                ),
                                "start": birthday,
                                "end": birthday,
                                "event_type": GENERIC_EVENT_BIRTHDAY,
                                "group_id": GROUP_EVENT_BIRTHDAY,
                                "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_BIRTHDAY],
                            }
                        )

                    if worker.data_desligamento:
                        if month != None:
                            if int(month) < 12:
                                month = int(month) + 1

                            if datetime(
                                month=int(month), year=int(year), day=1
                            ) < datetime(
                                year=worker.data_desligamento.year,
                                month=worker.data_desligamento.month,
                                day=worker.data_desligamento.day,
                            ):
                                data.append(
                                    {
                                        "pk": None,
                                        "title": "Aniversário de {} ".format(
                                            get_treatment_pronoun(worker)
                                        ),
                                        "start": birthday,
                                        "end": birthday,
                                        "event_type": GENERIC_EVENT_BIRTHDAY,
                                        "group_id": GROUP_EVENT_BIRTHDAY,
                                        "group_name": GROUP_EVENT_NAMES[
                                            GROUP_EVENT_BIRTHDAY
                                        ],
                                    }
                                )
                        else:
                            if datetime(year=int(year), month=12, day=31) < datetime(
                                year=worker.data_desligamento.year,
                                month=worker.data_desligamento.month,
                                day=worker.data_desligamento.day,
                            ):
                                data.append(
                                    {
                                        "pk": None,
                                        "title": "Aniversário de {} ".format(
                                            get_treatment_pronoun(worker)
                                        ),
                                        "start": birthday,
                                        "end": birthday,
                                        "event_type": GENERIC_EVENT_BIRTHDAY,
                                        "group_id": GROUP_EVENT_BIRTHDAY,
                                        "group_name": GROUP_EVENT_NAMES[
                                            GROUP_EVENT_BIRTHDAY
                                        ],
                                    }
                                )
    except Exception as e:
        log.error(e)
        return None


def get_event_licenses(data, employee_current, employee_ids, year, month):
    try:
        workers = []
        if not employee_ids:
            workers = get_workers(employee_current)
            if employee_current.id not in workers:
                workers.append(employee_current.id)
        else:
            workers = employee_ids

        absences = (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor__pk__in=workers),
                Q(Q(data_inicio__year=year) | Q(data_fim__year=year)),
            )
            .exclude(estado__in=[CANCELADO])
            .exclude(
                dayoff_usufructs__status__in=[
                    USU_CANCELED,
                    USU_NOT_AUTHORIZED,
                    USU_SOLD,
                    USU_SUSPENDED,
                    USU_SUBSTITUTE,
                    USU_INTERRUPTED,
                    USU_CHANGED,
                    USU_HOMOLOGATED,
                    USU_CHANGING,
                    USU_ENJOYING,
                    USU_ENJOYED,
                ]
            )
        )
        request_absences = PortalRequestAbsence.objects.filter(
            Q(employee__pk__in=workers),
            Q(Q(start_date__year=year) | Q(end_date__year=year)),
        ).exclude(
            status__in=[
                STS_REJECTED,
                STS_CANCELED_APPLICANT,
                STS_CANCELED_DGP,
                STS_EFFECTIVE,
            ]
        )

        if month:
            data_inicio = date(int(year), int(month), 1)
            if month == "12":
                data_fim = date(int(year) + 1, 1, 1)
            else:
                data_fim = date(int(year), int(month), 1) + relativedelta(day=31)

            absences = [
                absence
                for absence in absences
                if not (
                    absence.data_fim < data_inicio or absence.data_inicio >= data_fim
                )
            ]
            request_absences = [
                request_absence
                for request_absence in request_absences
                if not (
                    request_absence.end_date < data_inicio
                    or request_absence.start_date >= data_fim
                )
            ]

        for absence in absences:
            data.append(
                {
                    "pk": absence.pk,
                    "title": "{} solicitou a {}".format(
                        get_treatment_pronoun(absence.servidor),
                        absence.get_texto(),
                    ),
                    "start": absence.data_inicio,
                    "end": absence.data_fim,
                    "event_type": absence.tipo,
                    "group_id": GROUP_EVENT_LICENSES,
                    "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_LICENSES],
                }
            )
        for request_absence in request_absences:
            data.append(
                {
                    "pk": request_absence.pk,
                    "title": "{} solicitou a {}".format(
                        get_treatment_pronoun(request_absence.employee),
                        get_status_type_request_absence(request_absence),
                    ),
                    "start": request_absence.start_date,
                    "end": request_absence.end_date,
                    "event_type": request_absence.type,
                    "group_id": GROUP_EVENT_LICENSES,
                    "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_LICENSES],
                }
            )

    except Exception as e:
        log.error(e)
        return None


def get_event_substitutions(data, employee_current, employee_ids, year, month):
    try:
        workers = []
        if not employee_ids:
            workers = get_workers(employee_current)
            if employee_current.id not in workers:
                workers.append(employee_current.id)
        else:
            workers = employee_ids

        substitutions = MovimentacaoSubstituicao.objects.filter(
            Q(servidor__pk__in=workers),
            Q(Q(data_inicio__year=year) | Q(data_fim__year=year)),
        )
        if month:
            substitutions = substitutions.filter(data_inicio__month=month)

        for substitution in substitutions:
            data.append(
                {
                    "pk": substitution.pk,
                    "title": "{} substituindo {}".format(
                        get_treatment_pronoun(substitution.servidor),
                        get_treatment_pronoun(substitution.servidor_substituido),
                    ),
                    "start": substitution.data_inicio,
                    "end": substitution.data_fim,
                    "event_type": GENERIC_EVENT_SUBSTITUTIONS,
                    "group_id": GROUP_EVENT_SUBSTITUTIONS,
                    "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_SUBSTITUTIONS],
                }
            )
    except Exception as e:
        log.error(e)
        return None


def get_event_usufructs(data, employee_current, employee_ids, year, month):
    try:
        workers = []
        if not employee_ids:
            workers = get_workers(employee_current)
            if employee_current.id not in workers:
                workers.append(employee_current.id)
        else:
            workers = employee_ids

        usufructs = Usufruct.objects.filter(
            Q(activity__acquisition_period__employee__pk__in=workers),
            Q(Q(start_date__year=year) | Q(end_date__year=year)),
        ).exclude(
            status__in=[
                USU_NEW,
                USU_CANCELED,
                USU_NOT_AUTHORIZED,
                USU_SOLD,
                USU_SUSPENDED,
                USU_INTERRUPTED,
                USU_CHANGED,
                USU_SUBSTITUTE,
            ]
        )

        if month:
            usufructs = usufructs.filter(
                Q(start_date__month=month) | Q(end_date__month=month)
            )
        for usufruct in usufructs:
            if PortalCancelSchedule.objects.filter(usufruct=usufruct):
                data.append(
                    {
                        "pk": usufruct.pk,
                        "title": "{} solicitou cancelamento do {}".format(
                            get_treatment_pronoun(usufruct.employee),
                            usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display(),
                        ),
                        "start": usufruct.start_date,
                        "end": usufruct.end_date,
                        "event_type": usufruct.activity.acquisition_period.group_period.configuration.sub_type_of_usufruct,
                        "group_id": GROUP_EVENT_USUFRUCTS,
                        "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_USUFRUCTS],
                    }
                )
            elif PortalRetificationSchedule.objects.filter(
                activity__modifieds=usufruct
            ):
                data.append(
                    {
                        "pk": usufruct.pk,
                        "title": "{} solicitou retificação da {} - {})".format(
                            get_treatment_pronoun(usufruct.employee),
                            usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display(),
                            get_status_type(usufruct),
                        ),
                        "start": usufruct.start_date,
                        "end": usufruct.end_date,
                        "event_type": usufruct.activity.acquisition_period.group_period.configuration.sub_type_of_usufruct,
                        "group_id": GROUP_EVENT_USUFRUCTS,
                        "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_USUFRUCTS],
                    }
                )

            else:
                data.append(
                    {
                        "pk": usufruct.pk,
                        "title": "{} fruindo {}".format(
                            get_treatment_pronoun(usufruct.employee),
                            usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display().lower(),
                        ),
                        "start": usufruct.start_date,
                        "end": usufruct.end_date,
                        "event_type": usufruct.activity.acquisition_period.group_period.configuration.sub_type_of_usufruct,
                        "group_id": GROUP_EVENT_USUFRUCTS,
                        "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_USUFRUCTS],
                    }
                )

    except Exception as e:
        log.error(e)
        return None


def get_non_working_day(data_dict, year, month, employee_current):
    non_working_day = NonWorkingDay.objects.filter(start_date__year=year)
    if month:
        non_working_day = non_working_day.filter(
            Q(start_date__month=month) | Q(end_date__month=month)
        )
    try:
        for data in non_working_day:
            kind = Choice.objects.get(
                app_label="usefulday", name="KIND", value=data.kind
            ).label
            abrangency = Choice.objects.get(
                app_label="usefulday", name="ABRANGENCY", value=data.abrangency
            ).label
            if abrangency in ["Nacional", "Estadual"]:
                if not data.is_partial:
                    data_dict.append(
                        {
                            "pk": data.pk,
                            "title": "{} {} {}".format(
                                kind, abrangency, data.description
                            ),
                            "start": data.start_date.date(),
                            "end": (
                                data.end_date.date() if data.end_date else data.end_date
                            ),
                            "event_type": GENERIC_EVENT_NON_WORKING_DAY,
                            "group_id": GROUP_EVENT_NON_WORKING_DAY,
                            "group_name": GROUP_EVENT_NAMES[
                                GROUP_EVENT_NON_WORKING_DAY
                            ],
                        }
                    )
                else:
                    data_dict.append(
                        {
                            "pk": data.pk,
                            "title": "{} {} {} - Até às {}h".format(
                                kind,
                                abrangency,
                                data.description,
                                (
                                    data.end_date.hour
                                    if data.end_date
                                    else data.start_date.hour
                                ),
                            ),
                            "start": data.start_date.date(),
                            "end": (
                                data.end_date.date() if data.end_date else data.end_date
                            ),
                            "event_type": GENERIC_EVENT_NON_WORKING_DAY,
                            "group_id": GROUP_EVENT_NON_WORKING_DAY,
                            "group_name": GROUP_EVENT_NAMES[
                                GROUP_EVENT_NON_WORKING_DAY
                            ],
                        }
                    )
            else:
                non_work_day_location = is_localidade_feriado(employee_current, data)
                if non_work_day_location:
                    data_dict.append(
                        {
                            "pk": data.pk,
                            "title": "{} {} {}".format(
                                kind, abrangency, data.description
                            ),
                            "start": data.start_date.date(),
                            "end": (
                                data.end_date.date() if data.end_date else data.end_date
                            ),
                            "event_type": GENERIC_EVENT_NON_WORKING_DAY,
                            "group_id": GROUP_EVENT_NON_WORKING_DAY,
                            "group_name": GROUP_EVENT_NAMES[
                                GROUP_EVENT_NON_WORKING_DAY
                            ],
                        }
                    )

    except Exception as e:
        log.error(e)
        return None


def get_event_shifts(data, employee_current, employee_ids, year, month):
    try:
        workers = []
        if not employee_ids:
            workers = get_workers(employee_current)
            if employee_current.id not in workers:
                workers.append(employee_current.id)
        else:
            workers = employee_ids

        shifts = ShiftManager.objects.filter(
            Q(employee__pk__in=workers),
            Q(Q(start_date__year=year) | Q(end_date__year=year)),
        ).exclude(
            server_duty__status__in=[
                STS_REJECTED,
                STS_CANCELED_DGP,
                STS_CANCELED_APPLICANT,
            ]
        )

        if month:
            shifts = shifts.filter(
                Q(start_date__month=month) | Q(end_date__month=month)
            )

        for shift in shifts:
            data.append(
                {
                    "pk": shift.pk,
                    "title": "Plantão de {} em {} ({})".format(
                        get_treatment_pronoun(shift.employee),
                        shift.workplace_name,
                        shift.get_status_nome,
                    ),
                    "start": shift.start_date,
                    "end": shift.end_date,
                    "event_type": shift.type_shift,
                    "group_id": GROUP_EVENT_SHIFTS,
                    "group_name": GROUP_EVENT_NAMES[GROUP_EVENT_SHIFTS],
                }
            )
    except Exception as e:
        log.error(e)
        return None


def remove_accents(input_str):
    """
    Função para remover acentos de uma string.
    Args:
        input_str (str): A string que deseja remover os acentos.
    Returns:
        str: A string sem acentos.
    """
    # Normaliza a string para o formato Unicode compatível com NFKD (Forma de Composição Canônica Compatível com NFKD).
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def is_localidade_feriado(servidor, feriado):
    if servidor.type_by_possession in ["MBR", "MEL", "MEC"]:
        return localidades_mes_membro(servidor, feriado)
    return localidades_mes_servidor(servidor, feriado)


def localidades_mes_servidor(servidor, feriado):
    """
    Função filtra as localidades no feriado para servidores.
    Args:
        servidor (obj): objeto do servidor
        feriado (obj): objeto do feriado
    Returns:
        bool
    """
    localidades = list(set(feriado.places.values_list("pk", flat=True)))
    dt_feriado = feriado.start_date
    lotacaoes = ServidorLotacao.objects.filter(
        Q(servidor=servidor, designacao=False, lotacao__localidade__pk__in=localidades),
        Q(data_vigencia_inicio__lte=dt_feriado)
        & Q(
            Q(data_vigencia_fim__gte=dt_feriado)
            | Q(data_vigencia_fim__isnull=True, data_vigencia_inicio__lte=dt_feriado)
        ),
    )
    return lotacaoes.exists()


def localidades_mes_membro(servidor, feriado):
    """
    Função filtra as localidades no feriado para membros.
    Args:
        servidor (obj): objeto do servidor
        feriado (obj): objeto do feriado
    Returns:
        bool
    """
    localidades = list(set(feriado.places.values_list("pk", flat=True)))
    dt_feriado = feriado.start_date
    lotacaoes = ServidorLotacao.objects.filter(
        Q(servidor=servidor, designacao=True, lotacao__localidade__pk__in=localidades),
        Q(data_vigencia_inicio__lte=dt_feriado)
        & Q(
            Q(data_vigencia_fim__gte=dt_feriado)
            | Q(data_vigencia_fim__isnull=True, data_vigencia_inicio__lte=dt_feriado)
        ),
    )
    return lotacaoes.exists()
