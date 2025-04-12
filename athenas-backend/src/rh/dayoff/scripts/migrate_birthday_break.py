# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Q, Count

from contrib.middleware import set_current_user, get_current_user
from contrib.daterange import NewDateRange
from rh.models import Servidor
from rh.const import CANCELED
from rh.dayoff.models import (
    AcquisitionPeriod,
    Usufruct,
    Activity,
    Configuration,
    GroupPeriod,
    ActivityBook,
    ActivityInterrupt,
    Attachment,
)
from rh.dayoff.const import (
    ACQP_PROGRESS,
    USU_HOMOLOGATED,
    USU_AUTORIZED_CI,
    ACQP_WAIT,
    CONFIGURATION_CHOICE,
    CONF_BIRTHDAY_BREAK,
    AUTO_HOMOLOGATION,
    AUTO_HOMOLOGATION_NOT,
    USU_NEW,
    ACT_ST_AUTHORIZED_M,
    ACT_ST_AUTHORIZED,
    USU_CANCELED,
    AUTO_HOMOLOGATION_AFTER_SCALE,
)
from rh.dayoff.signals import departure as departure_signals
from rh.dayoff.signals import usufruct as usufruct_signals
from rh.afastamento.models import FolgaAniversario
from standard.models import ClassCode

from contrib.utils import getLogger


import datetime
import time


log = getLogger(__name__)

YEARS_TO_IMPORT = [2020, 2021]
VERBOSE = True


def show_message(message):
    if VERBOSE:
        print(message)


def manager_departure(activity, to_delete=False):
    return True


def manager_usufruct(usufruct, activity_call, to_delete=False):
    return True


def update_acquisition_period(sender, instance, **kargs):
    return True


departure_signals.manager_departure = manager_departure
departure_signals.manager_usufruct = manager_usufruct
update_acquisition_period_old = usufruct_signals.update_acquisition_period
usufruct_signals.update_acquisition_period = update_acquisition_period


def notify_release(self, notify_prevent=False):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_authorize(self, notify_prevent=False):
    return True


def notify_homologated(self, notify_prevent=False):
    return True


def notify_fruition(cls, list_days=[]):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_call_authorization(self, notify_prevent=False):
    return True


def notify(self, notify_prevent=False):
    return True


def notify_authorize(self, notify_prevent=False):
    return True


def validate_range_fruition(self):
    return True


def validate_days_per_period(self):
    return True


def validate_departure(self):
    return True


Activity.notify_release = notify_release
Activity.notify = notify
Activity.notify_authorize = notify_authorize
Activity.notify_homologated = notify_homologated
Activity.notify_fruition = notify_fruition
Activity.notify = notify
Activity.notify_call_authorization = notify_call_authorization
Activity.notify = notify
Activity.notify_authorize = notify_authorize

ActivityBook.notify_release = notify_release
ActivityBook.notify = notify
ActivityBook.notify_authorize = notify_authorize
ActivityBook.notify_homologated = notify_homologated
ActivityBook.notify_fruition = notify_fruition
ActivityBook.notify = notify
ActivityBook.notify_call_authorization = notify_call_authorization
ActivityBook.notify = notify
ActivityBook.notify_authorize = notify_authorize

Usufruct.validate_range_fruition = validate_range_fruition
Usufruct.validate_departure = validate_departure

AcquisitionPeriod.validate_days_per_period = validate_days_per_period

GROUPS = {}


def create_group_period_birthday_break(year):
    from datetime import datetime

    global GROUPS
    group = GROUPS.get("FOLGA ANIVERSÁRIO-{year}", None)
    if not group:
        defaults = {
            "block_on_conflict": False,
            "block_after_pay": False,
            "mediate_authorization": False,
            "auto_authorization": 0,
            "auto_create_on_scale": False,
            "months_prescription": None,
            "auto_create_prescription": False,
            "auto_homologation": AUTO_HOMOLOGATION_AFTER_SCALE,
            "max_division": 20,
            "max_division_admin": 20,
            "min_days_division": 1,
            "min_days_division_admin": 1,
            "chronological_fruition": False,
            "months_max_usufruct": None,
            "max_alteration_usufruct": None,
            "start_month_next_period": None,
            "days_precede_fruition": None,
            "work_days_precede_fruition": False,
            "months_exercise_sale": None,
            "min_days_sale": False,
            "max_days_sale": False,
            "months_exercise_first_acquitition": 0,
            "months_exercise_next_acquitition": None,
            "days_per_period": 1,
            "periods_per_year": 1,
            "division_after_suspension": 0,
        }
        configuration, created = Configuration.objects.get_or_create(
            title="FOLGA ANIVERSÁRIO",
            type_of_usufruct=CONF_BIRTHDAY_BREAK,
            defaults=defaults,
        )
        start_date = datetime(int(year), 1, 1).date()
        defaults = {
            "configuration": configuration,
            "end_date_book": None,
            "start_date_book": start_date,
            "start_date_fruition": start_date,
            "homologation_date": start_date,
            "publication_date": start_date,
            "blocked": True,
        }
        group, created = GroupPeriod.objects.get_or_create(
            title="FOLGA ANIVERSÁRIO", year_reference=year, defaults=defaults
        )
        GROUPS.update({"FOLGA ANIVERSÁRIO-{group.year_reference}": group})
    return group


def run_create_acquisition_period_birthday_break(departure, success):
    group_period = create_group_period_birthday_break(departure.ano)
    _classcode = None
    if group_period.classcode:
        _classcode = group_period.classcode.cls(group_period, departure.servidor)
    defaults = {
        "note": True,
        "status": ACQP_PROGRESS,
        "start_date_acquisition": (
            _classcode.get_start_date_acquisition()
            if _classcode
            else group_period.start_date_fruition
        ),
        "end_date_acquisition": (
            _classcode.get_end_date_acquisition()
            if _classcode
            else group_period.end_date_fruition
        ),
        "start_date_fruition": (
            _classcode.get_start_date_fruition()
            if _classcode
            else group_period.start_date_fruition
        ),
        "end_date_fruition": (
            _classcode.get_end_date_fruition()
            if _classcode
            else group_period.end_date_fruition
        ),
        "continuous_period": True,
        "blocked": True,
        "days": group_period.configuration.days_per_period,
        "paid_days_cache": 0,
        "paid_without_payroll": False,
        "indemnified": False,
        "suspended_days": 0,
        "annotation": departure.anotacao_aquisicao,
    }
    acquisition_period, created = AcquisitionPeriod.objects.get_or_create(
        group_period=group_period, employee=departure.servidor, defaults=defaults
    )
    if not created:
        defaults = {
            "start_date_acquisition": (
                _classcode.get_start_date_acquisition()
                if _classcode
                else group_period.start_date_acquisition
            ),
            "end_date_acquisition": (
                _classcode.get_end_date_acquisition()
                if _classcode
                else group_period.end_date_acquisition
            ),
            "start_date_fruition": (
                _classcode.get_start_date_fruition()
                if _classcode
                else group_period.start_date_fruition
            ),
            "end_date_fruition": (
                _classcode.get_end_date_fruition()
                if _classcode
                else group_period.end_date_fruition
            ),
            "annotation": departure.anotacao_aquisicao,
        }
        acquisition_period, created = AcquisitionPeriod.objects.update_or_create(
            group_period=group_period, employee=departure.servidor, defaults=defaults
        )
    log.info(f"{created}, {acquisition_period}")
    usufructs = [
        {"start_date": departure.data_inicio, "end_date": departure.data_fim},
    ]
    try:
        acquisition_period.book(usufructs_in=usufructs, context="admin")
        for usu in acquisition_period.usufructs.filter():
            usu.transit_status(None, USU_HOMOLOGATED, validate_prevent=True)
            usu.refresh_from_db()
            usu.update_status()
        acquisition_period.update_status(validate_prevent=True)
    except Exception as err:
        print(
            f"group: {group_period}\nemployee: {departure.servidor}\ndeparture: {departure.__str_restful__()}\nerr: {err}\n"
        )
        raise Exception(
            f"group: {group_period}\nemployee: {departure.servidor}\ndeparture: {departure.__str_restful__()}\nerr: {err}\n"
        )
    return acquisition_period, created


def query_birthday_break():
    return FolgaAniversario.objects.filter(
        servidor__tipo__in=["S", "M"], ano__in=YEARS_TO_IMPORT
    ).exclude(estado=CANCELED)


def call_create_acquisition_period_birthday_break():
    report_result = ""
    report_err = ""
    pks_createds = []
    query = query_birthday_break()
    total = query.count()
    count = 0
    show_message(
        f"Realizando a importação de períodos a partir de FolgaAniversario: {count} of {total}.."
    )
    log.info(
        f"Realizando a importação de períodos a partir de FolgaAniversario: {count} of {total}.."
    )
    for departure in query.order_by(
        "servidor__pessoa_fisica__nome", "-ano", "data_inicio"
    ):
        count += 1
        try:
            acquisition_period, created = run_create_acquisition_period_birthday_break(
                departure, ""
            )
            message = f"{departure.servidor} | {departure.__str_restful__()}"
            report_result += f"{message}\n"
            message = f"Realizando a importação de períodos a partir de {message} | {count} of {total}.."
            show_message(message)
            log.info(message)
            pks_createds.append(acquisition_period.pk)
        except Exception as err:
            log.exception(err)
            report_err += f"{err}\n"
    return report_result, report_err


def migrate_all():
    global VERBOSE

    print(
        """Script para importação de períodos aquisitivos de Folga de Aniversário a partir do Gestor de Afastamentos.
    Script para criação/atualização de períodos aquisitivos de Folga de Aniversário.
    """
    )

    todo_option = input(
        f"\nEscolha as tarefas:\n(1) Importação\n(2) Criação/atualização\n 1 e 2 como default, ou escolha qual:"
    )

    verbose = input(f"\nModo VERBOSE(True default) (True/False)?")
    if verbose is False:
        VERBOSE = False

    user = input(
        f"\nInforme um usuário (athenas será default) para criar os dados?"
    ).lower()
    if not user:
        user = "athenas"
    while not User.objects.filter(username=user).exists():
        user = input(f"\nInforme um usuário para criar os dados?").lower()
    set_current_user(user)

    def delete_acquisition_periods(rs):
        if rs == "y":
            user = get_current_user()
            set_current_user("athenas")
            query = AcquisitionPeriod.objects.filter(
                group_period__year_reference__in=YEARS_TO_IMPORT,
                group_period__configuration__type_of_usufruct=CONF_BIRTHDAY_BREAK,
            )
            total = query.count()
            count = 0
            for ap in query.order_by("employee"):
                count += 1
                log.info(f"deleting {count} of {total}...")
                print(f"deleting {count} of {total}...")
                ap.delete()
            set_current_user(user)

    rs = input(f"\nApagar informações antes de criar? (y/N):").lower()
    delete_acquisition_periods(rs)
    usufruct_signals.update_acquisition_period = update_acquisition_period_old

    report_result = "Períodos aquisitivos importados de Folga Aniversário:\n"
    report_err = ""
    if not todo_option or todo_option == "1":
        report_result, report_err = call_create_acquisition_period_birthday_break()

    def generate_all_acquisition_periods():
        report_err = ""
        query_group = GroupPeriod.objects.filter(
            configuration__type_of_usufruct=CONF_BIRTHDAY_BREAK,
            year_reference__in=YEARS_TO_IMPORT,
        )
        total_group = query_group.count()
        count_group = 0
        types = []
        for group in query_group:
            for v in group.configuration.type_employees.values("cvalue"):
                types.append(v["cvalue"])

        query_employee = Servidor.objects.filter(
            ativo=True, type_by_possession__in=types
        )
        total_employee = query_employee.count()
        count_employee = 0
        log.info(
            f"Criando períodos aquisitivos pendentes para {total_employee} servidores."
        )
        show_message(
            f"Criando períodos aquisitivos pendentes para {total_employee} servidores."
        )
        for employee in query_employee:
            count_employee += 1
            count_group = 0
            for group in query_group:
                count_group += 1

                _klass = group.classcode.cls
                class_code_acqp = _klass(group, employee)
                err = None
                obj = None
                try:
                    prescribed = (
                        class_code_acqp.get_end_date_fruition()
                        < datetime.datetime.now().date()
                    )
                    calculate_acquired_days, info = (
                        class_code_acqp.calculate_acquired_days()
                    )
                    if (
                        not prescribed
                        and calculate_acquired_days > 0
                        or class_code_acqp.acq_period
                    ):
                        obj, mode = (
                            class_code_acqp.update_or_create_acquisition_period()
                        )
                        show_message(
                            f"{obj} => servidor({count_employee} of {total_employee}), Grupo({count_group} of {total_group})."
                        )
                    # else:
                    #     message = f'{group} - {employee}'
                    #     message += f'\nNão criado!'
                    #     if prescribed:
                    #         message += f'Prescreveu!'
                    #     else:
                    #         message += info
                    #     print(message)
                    #     print('---------------------------------')
                except Exception as err:
                    print(
                        f"group: {group}\nemployee: {employee}\nerr: {err} {type(err)}"
                    )
                    report_err += f"{obj} => ERRO: {err}\n"
                    print("---------------------------------")
        return report_err

    if not todo_option or todo_option == "2":
        report_err += generate_all_acquisition_periods()

    print(f"Resultado:\n {report_result}")
    print(f"Erros:\n {report_err}")


migrate_all()
