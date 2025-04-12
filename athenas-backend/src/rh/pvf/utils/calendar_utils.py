import datetime as dt
from datetime import datetime

from django.db.models.query_utils import Q

from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELADO, ENCERRADO
from rh.dayoff.const import *
from rh.dayoff.models import Usufruct
from rh.models import MovimentacaoSubstituicao, Servidor, ServidorLotacao
from rh.pvf.const import *
from rh.pvf.models import (
    PortalCancelSchedule,
    PortalRequestAbsence,
    PortalRetificationSchedule,
    ShiftManager,
)
from standard.models import Choice

log = getLogger(__name__)


def get_status_type_request_absence(request_absence):
    for abs_type in TYPE_OF_LICENSE:
        if request_absence.type == abs_type:
            return TYPE_OF_LICENSE.get(abs_type)


def get_status_type(usufruct):
    for usu in USUFRUCT_STATUS_CHOICE:
        if usufruct.status == usu:
            if usufruct.status == USU_SUBSTITUTE:
                return "Aguardando Substituto"
            return USUFRUCT_STATUS_CHOICE.get(usu)


def get_workers_from_workplace(workplaces, employee):
    if workplaces and len(workplaces) > 0:
        employees = Servidor.objects.filter(
            Q(tipo="S"),
            pk__in=ServidorLotacao.objects.filter(
                ativo=True, lotacao__in=[x[0] for x in workplaces.values_list("pk")]
            ).values_list("servidor__pk", flat=True),
        ).values_list("pk")
        return [x[0] for x in employees] + [employee.pk]
    return []


def get_treatment_pronoun(employee):
    if employee.type_by_possession in [
        "MBR",
        "MEL",
        "MCM",
        "MEC",
        "MBR2",
        "MEL2",
        "MCM2",
        "MEC2",
    ]:
        if employee.pessoa_fisica.sexo == "M":
            return f"Dr. {employee.pessoa_fisica.social_name.title()}"
        else:
            return f"Dra. {employee.pessoa_fisica.social_name.title()}"
    else:
        return employee.pessoa_fisica.social_name.title()


def get_event_days(events, days):
    dates = {}
    for event, value in events.items():
        for day, date in days.items():
            if date >= value["event_start_date"] and date <= value["event_end_date"]:
                dates[int(day)] = date
    return dict(sorted(dates.items(), key=lambda x: x[0]))


def get_event_birthday(employee, year, month, workers=None):
    try:
        birthdate_event = {}

        if not workers:
            birth_date = employee.pessoa_fisica.data_nascimento
            birthday = dt.date(
                day=birth_date.day, month=birth_date.month, year=int(year)
            )
            birthdate_event[birthday] = {
                "event_name": "Feliz Aniversário! Parabéns!",
                "event_start_date": birthday,
                "event_end_date": birthday,
                "event_type": 1,
                "employee": employee,
            }
        else:
            workers = Servidor.objects.filter(id__in=workers)
            for worker in workers:
                birth_date = worker.pessoa_fisica.data_nascimento
                birthday = dt.date(
                    day=birth_date.day, month=birth_date.month, year=int(year)
                )
                if worker.id == employee.id:
                    birthdate_event[worker] = {
                        "event_name": "Feliz Aniversário! Parabéns!",
                        "event_start_date": birthday,
                        "event_end_date": birthday,
                        "event_type": 1,
                        "employee": worker,
                    }

                else:
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
                                birthdate_event[worker] = {
                                    "event_name": "Aniversário de {} ".format(
                                        get_treatment_pronoun(worker)
                                    ),
                                    "event_start_date": birthday,
                                    "event_end_date": birthday,
                                    "event_type": 1,
                                    "employee": worker,
                                }
                        else:
                            if datetime(year=int(year), month=12, day=31) < datetime(
                                year=worker.data_desligamento.year,
                                month=worker.data_desligamento.month,
                                day=worker.data_desligamento.day,
                            ):
                                birthdate_event[worker] = {
                                    "event_name": "Aniversário de {} ".format(
                                        get_treatment_pronoun(worker)
                                    ),
                                    "event_start_date": birthday,
                                    "event_end_date": birthday,
                                    "event_type": 1,
                                    "employee": worker,
                                }

                    else:
                        birthdate_event[worker] = {
                            "event_name": "Aniversário de {} ".format(
                                get_treatment_pronoun(worker)
                            ),
                            "event_start_date": birthday,
                            "event_end_date": birthday,
                            "event_type": 1,
                            "employee": worker,
                        }

        return birthdate_event
    except Exception as e:
        log.error(e)
        return None


def get_event_licenses(employee, month, year, workers=None):
    try:
        if not workers:
            workers = [employee.id]
        request_absence_event = {}
        absence_event = {}
        absences = (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor__pk__in=workers),
                Q(Q(data_inicio__year=year) | Q(data_fim__year=year)),
            )
            .exclude(estado__in=[CANCELADO, ENCERRADO])
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
        ).exclude(status__in=[STS_REJECTED, STS_CANCELED_APPLICANT, STS_CANCELED_DGP])
        if month:
            absences = absences.filter(
                Q(data_inicio__month=month) | Q(data_fim__month=month)
            )
            request_absence = request_absences.filter(
                Q(start_date__month=month) | Q(end_date__month=month)
            )
        for absence in absences:
            absence_event[absence] = {
                "event_name": "{} solicitou o {}".format(
                    get_treatment_pronoun(absence.servidor),
                    absence.get_texto(),
                ),
                "event_start_date": absence.data_inicio,
                "event_end_date": absence.data_fim,
                "event_type": 2,
                "employee": employee,
            }
        for request_absence in request_absences:
            request_absence_event[request_absence] = {
                "event_name": "{} solicitou o {}".format(
                    get_treatment_pronoun(request_absence.employee),
                    get_status_type_request_absence(request_absence),
                ),
                "event_start_date": request_absence.start_date,
                "event_end_date": request_absence.end_date,
                "event_type": 3,
                "employee": employee,
            }
        return absence_event, request_absence_event
    except Exception as e:
        log.error(e)
        return None, None


def get_event_substitutions(employee, month, year, workers=None):
    try:
        if not workers:
            workers = [employee.id]
        substitution_event = {}
        substitutions = MovimentacaoSubstituicao.objects.filter(
            Q(servidor__pk__in=workers),
            Q(Q(data_inicio__year=year) | Q(data_fim__year=year)),
        )
        if month:
            substitutions = substitutions.filter(
                Q(data_inicio__month=month) | Q(data_fim__month=month)
            )

        for substitution in substitutions:
            substitution_event[substitution] = {
                "event_name": "{} substituindo {}".format(
                    get_treatment_pronoun(employee),
                    get_treatment_pronoun(substitution.servidor_substituido),
                ),
                "event_start_date": substitution.data_inicio,
                "event_end_date": substitution.data_fim,
                "event_type": 5,
                "employee": employee,
            }
        return substitution_event
    except Exception as e:
        log.error(e)
        return None


def get_eventos_plantao(employee, month, year, workers=None):
    try:
        if not workers:
            workers = [employee.id]
        plantao_eventos = {}
        plantoes = ShiftManager.objects.filter(
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
            plantoes = plantoes.filter(
                Q(start_date__month=month) | Q(end_date__month=month)
            )

        for plantao in plantoes:
            plantao_eventos[plantao] = {
                "event_name": "Plantão de {} em {} ({})".format(
                    get_treatment_pronoun(plantao.employee),
                    plantao.workplace_name,
                    plantao.get_status_nome,
                ),
                "event_start_date": plantao.start_date,
                "event_end_date": plantao.end_date,
                "event_type": 6,
                "employee": employee,
            }
        return plantao_eventos
    except Exception as e:
        log.error(e)
        return None


def get_event_usufructs(employee, month, year, workers=None):
    try:
        if not workers:
            workers = [employee.id]
        usufructs_event = {}
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
                usufructs_event[usufruct] = {
                    "event_name": "{} solicitou cancelamento do {}".format(
                        get_treatment_pronoun(usufruct.employee),
                        usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display(),
                    ),
                    "event_start_date": usufruct.start_date,
                    "event_end_date": usufruct.end_date,
                    "event_type": 4,
                    "employee": employee,
                }
            elif PortalRetificationSchedule.objects.filter(
                activity__modifieds=usufruct
            ):
                usufructs_event[usufruct] = {
                    "event_name": "{} solicitou retificação da {} - {})".format(
                        get_treatment_pronoun(usufruct.employee),
                        usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display().lower(),
                        get_status_type(usufruct),
                    ),
                    "event_start_date": usufruct.start_date,
                    "event_end_date": usufruct.end_date,
                    "event_type": 4,
                    "employee": employee,
                }

            else:
                usufructs_event[usufruct] = {
                    "event_name": "{} fruindo {}".format(
                        get_treatment_pronoun(usufruct.employee),
                        usufruct.activity.acquisition_period.group_period.configuration.get_sub_type_of_usufruct_display().lower(),
                    ),
                    "event_start_date": usufruct.start_date,
                    "event_end_date": usufruct.end_date,
                    "event_type": 4,
                    "employee": employee,
                }
        return usufructs_event
    except Exception as e:
        log.error(e)
        return None


def get_non_working_day(non_working_day):
    context_non_working_day = {}
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
                    context_non_working_day[data] = {
                        "event_name": "{} {} {}".format(
                            kind, abrangency, data.description
                        ),
                        "event_start_date": data.start_date,
                        "event_end_date": data.end_date,
                    }
                else:
                    context_non_working_day[data] = {
                        "event_name": "{} {} {} - Até às {}h".format(
                            kind,
                            abrangency,
                            data.description,
                            (
                                data.end_date.hour
                                if data.end_date
                                else data.start_date.hour
                            ),
                        ),
                        "event_start_date": data.start_date,
                        "event_end_date": data.end_date,
                    }

        return context_non_working_day
    except Exception as e:
        log.error(e)
        return None
