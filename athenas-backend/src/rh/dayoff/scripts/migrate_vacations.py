# -.- coding: utf-8 -.-
import os
import re
import sys
import traceback

import django
from django.db.models.aggregates import Count
from django.db.models import F, Sum, signals, Q
from django.dispatch import Signal

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()
from datetime import date, datetime
from contrib.middleware import get_current_user, set_current_user
from rh.dayoff.const import (
    ACQP_INDEMNIFIED,
    ACQP_PROGRESS,
    ACT_SELL,
    CONF_VACATION,
    USU_CHANGED,
    USU_NOT_AUTHORIZED,
)
from rh.dayoff.models import (
    AcquisitionPeriod,
    Activity,
    ActivityBook,
    ActivityChange,
    ActivityInterrupt,
    ActivitySell,
    ActivitySuspend,
    Configuration,
    GroupPeriod,
    Usufruct,
    Payment,
)
from rh.dayoff.signals import departure as s_departure
from rh.dayoff.signals import usufruct as s_usufruct
from rh.dayoff.utils import action_check

# from rh.dayoff.signals.departure import usufruct_cancel, usufruct_create
from rh.ferias.models import (
    AlteracaoPASU,
    Configuracao,
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorUsufruto,
)
from rh.models import AnotacaoFerias
from rh.gfp.models import FolhaEvento

set_current_user("athenas")
# set_current_user('iradianmorais')


RED = "\033[0;31m"
GREEN = "\033[0;32m"
ORANGE = "\033[0;33m"
WHITE = "\033[1;37m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

SELL_EVENTS = [
    "05700",
]
RECISION_EVENTS = [
    "05300",
    "05500",
]


def pass_through_func(*args, **kwargs):
    return True


def pass_through(self, *args, **kwargs):
    return True


def pass_through_cls(*args, **kwargs):
    return True


def _define_authorize_context_admin(self, authorize=None, context=None):
    """Esté método atribui 'admin' ao .context e authorize=True caso seja o admin fazendo e ele possua permissão. Ou seja o system."""
    # if authorize is None and ((self.admin_can_authorize() and context == 'admin') or self.system_can_authorize()):
    #     authorize = True
    #     context = 'admin'
    return authorize, context


s_departure.manager_departure = pass_through
s_departure.manager_usufruct = pass_through
update_acquisition_period_old = s_usufruct.update_acquisition_period
s_usufruct.update_acquisition_period = pass_through
s_departure.manager_departure = pass_through_cls
# action_check = pass_through_func

# Activity.notify_release = pass_through
Activity.notify = pass_through
Activity.notify_authorize = pass_through
Activity.notify_homologated = pass_through
Activity.notify_fruition = pass_through
Activity.notify = pass_through
# Activity.notify_call_authorization = pass_through
Activity.notify = pass_through
Activity.notify_authorize = pass_through
Activity.validate = pass_through
Activity.validate_immediate_authorization = pass_through

ActivityBook.validate_booked_days = pass_through
ActivityBook.notify = pass_through
ActivityBook.notify_authorize = pass_through
ActivityBook.notify_homologated = pass_through
ActivityBook.notify_fruition = pass_through
ActivityBook.notify = pass_through
ActivityBook.notify_call_authorization = pass_through
ActivityBook.notify = pass_through
ActivityBook.notify_authorize = pass_through

ActivityChange.validate_modifieds = pass_through
ActivityChange.notify = pass_through
ActivityChange.notify_authorize = pass_through
ActivityChange._define_authorize_context_admin = _define_authorize_context_admin

ActivitySell.validate_allow_sell = pass_through
ActivitySell.validate_days_on_sale = pass_through
ActivitySell._change_usufructs_before_sell = pass_through

Usufruct.validate_range_fruition = pass_through
Usufruct.validate_conflicts_between_usufructs = pass_through
Usufruct.validate_min_days_division = pass_through

AcquisitionPeriod.notify_release = pass_through
AcquisitionPeriod.validate_days_per_period = pass_through


class temp_disconnect_signal:
    """Temporarily disconnect a model from a signal"""

    # def __init__(self, signal, receiver, sender, dispatch_uid=None):
    #     self.signal = signal
    #     self.receiver = receiver
    #     self.sender = sender
    #     self.dispatch_uid = dispatch_uid

    def __enter__(self):
        # self.signal.disconnect(
        #     receiver=self.receiver,
        #     sender=self.sender,
        #     dispatch_uid=self.dispatch_uid,
        #     # weak=False
        # )
        # signals.post_save.disconnect(receiver=d_signals.usufruct_change_suspend, sender=Usufruct, dispatch_uid='post_save_dayoff_usufruct')
        # signals.post_save.disconnect(receiver=d_signals.activity_save, sender=Usufruct, dispatch_uid='post_save_dayoff_usufruct')
        # signals.pre_delete.disconnect(receiver=d_signals.usufruct_cancel, sender=Usufruct, dispatch_uid='pre_delete_dayoff_usufruct')
        pass

    def __exit__(self, type, value, traceback):
        # self.signal.connect(
        #     receiver=self.receiver,
        #     sender=self.sender,
        #     dispatch_uid=self.dispatch_uid,
        #     # weak=False
        # )
        # signals.post_save.connect(receiver=d_signals.usufruct_create, sender=Usufruct, dispatch_uid='post_save_dayoff_usufruct')
        # signals.post_delete.connect(receiver=d_signals.usufruct_cancel, sender=Usufruct, dispatch_uid='post_delete_dayoff_usufruct')
        pass


# TODO
# 1. CORRER TODOS OS USUFRUTOS EM ORDEM DE CRIAÇÃO, SENDO OS PRIMERIOS OS PROVENIENTE DE MARCAÇÃO E SO DEPOIS ALTERAÇÃO
# 2. PARA CADA USUFRUTO
# 2.1 VERIFICAR SE O USUFRUTO POSSUI UMA ALTERACAO QUE DEU ORIGEM
# 2.2 CASO NEGATIVO (ORIGEM NUMA MARCAÇÃO): DEVE-SE CRIAR o ActivityBook
# 2.2.1 SE EXISTIR OUTROS USUFRUTOS CRIADOS NO MESMO TIMESTAMP, ONDE A QUANTIDADE DE DIAS JUNTOS SEJA MENOR DO QUE 30 e A QUANTIDADE DE USUFRUTOS MENOR QUE A CONFIGRAÇÃO DE PARCELAMENTO DEVE-SE CRIAR APENAS UM ActivityBoook PARA TODOS OS USUFRUTOS
# 2.2.2 SE NÃO, DEVE-SE CRIAR UMA ActivityBook PARA CADA USUFRUTO

FINISHED_PATH_FILE = "registers_finished.list"
LOG_PATH_FILE = "migration_dayoff.log"


def load_finisheds():
    registers_finished = []
    if os.path.isfile(FINISHED_PATH_FILE):
        with open(FINISHED_PATH_FILE, "r") as fp:
            registers_finished = [reg.strip("\n") for reg in fp.readlines()]

    return registers_finished


def dump_finished_employee(register):
    with open(FINISHED_PATH_FILE, "a") as fp:
        fp.write(f"{register}\n")


def dump_finisheds(registers=[]):
    with open(FINISHED_PATH_FILE, "w") as fp:
        fp.writelines(registers)


def log_migration(lines=[], clear=False):
    with open(LOG_PATH_FILE, "a" if not clear else "w") as fp:
        fp.writelines(f"{s}\n" for s in lines)


def migrate_confs_groups():
    configs = groups = periods = 0
    for fconf in Configuracao.objects.all():
        if fconf.periodoaquisitivo_set.count():
            # print(f'>> {fconf}')
            dconf, created = Configuration.objects.update_or_create(
                title=fconf.nome.upper(),
                type_of_usufruct=CONF_VACATION,
                defaults={
                    "continuous_period": fconf.modo == "CONTINUO",
                    "block_on_conflict": fconf.bloquear_conflitos,
                    "mediate_authorization": fconf.exigir_autorizacao_chefia_mediata,
                    "months_prescription": fconf.meses_prescricao,
                    "max_division": fconf.max_divisoes,
                    "min_days_division": fconf.min_dias_por_divisao,
                    "months_max_usufruct": fconf.meses_max_fruicao,
                    "days_precede_fruition": fconf.dias_antecedencia_fruicao,
                    "months_exercise_first_acquitition": fconf.meses_exercicio,
                    "months_exercise_next_acquitition": fconf.meses_exercicio,
                    "days_per_period": fconf.dias_por_periodo,
                    "periods_per_year": fconf.quantidade_periodos,
                    "chronological_fruition": False,
                    "created_by": get_current_user(),
                    "modified_by": get_current_user(),
                },
            )
            if created:
                configs += 1
            for fpa in fconf.periodoaquisitivo_set.order_by("ano_aquisicao", "periodo"):
                # print(f'>>> {fpa}')
                title = f'Férias {"Membros" if fconf.tipo_servidor == "M" else "Servidores"} - {fpa}'
                gp, gp_created = dconf.groupperiods.update_or_create(
                    title=title.upper(),
                    period=fpa.periodo,
                    year_reference=fpa.ano_aquisicao,
                    defaults={
                        "start_date_book": fpa.data_inicio_prev,
                        "end_date_book": fpa.data_fim_prev,
                        "homologation_date": fpa.data_homologacao_prev,
                        "publication_date": fpa.data_publicacao,
                        "blocked": fpa.bloqueado,
                        # TOHELP Não entendi o campo year_collective_fruition
                        # 'year_collective_fruition': ,
                        # TOHELP Existe start_date_fruition para férias
                        "start_date_fruition": date(fpa.ano_aquisicao, 1, 1),
                        # 'end_date_fruition': ,
                        # 'start_date_automatic_usufruct': ,
                        # 'end_date_automatic_usufruct': ,
                        # 'attachment': ,
                    },
                )
                if gp_created:
                    groups += 1


def validate_migration(pas, dpa, usufructs, usufructs_migrated):
    errors = []
    all_usufructs = len(usufructs) == 0
    for u in usufructs:
        errors.append(f">{dpa} {u} {RED}não migrado{NC}")
    equals_days = (
        pas.dias_usufruidos == dpa.days_enjoyed
        and pas.paid_days == dpa.paid_days
        and pas.dias_ausufruir == dpa.days_to_enjoy
        and pas.dias_marcados == dpa.booked_days
    )
    if not equals_days:
        errors.append(
            f"{dpa} ED:{pas.dias_usufruidos}/{dpa.days_enjoyed} PD:{pas.paid_days}/{dpa.paid_days} TED:{pas.dias_ausufruir}/{dpa.days_to_enjoy} BD:{pas.dias_agendados}/{dpa.booked_days}"
        )
    result = all_usufructs and equals_days

    return result, errors


def migrate_vacations(
    registers=[], clear=False, only_finished=False, stop_on_error=True
):
    registers_finished = load_finisheds()

    if only_finished:
        registers = registers_finished
        registers_finished = []

    with temp_disconnect_signal():
        print(f">>>>>> {RED}DELETING EMPTY GROUPS{NC} <<<<<<", end="")
        if clear:
            clear_groups()
        print(f"{GREEN}OK{NC}")

        migrate_confs_groups()
        previous_period = {}
        pas_query = PeriodoAquisitivoServidor.objects.order_by(
            "servidor",
            "periodo_aquisitivo__ano_aquisicao",
            "periodo_aquisitivo__periodo",
        ).exclude(servidor__matricula__in=registers_finished)
        if registers:
            pas_query = pas_query.filter(servidor__matricula__in=registers)

        update_data_before_migrate()

        employee = None
        employee_pass = True
        messages_employee_migration = []
        log_migration([], True)

        for pas in pas_query:
            pas.atualiza_estado()
            if employee != pas.servidor:
                clear_vacations(registers=[pas.servidor.matricula])
                if employee:
                    messages_employee_migration.insert(
                        0, f">>>>>>>> {employee} <<<<<<<<<"
                    )
                    if employee_pass:
                        registers_finished.append(employee.matricula)
                        dump_finished_employee(employee.matricula)
                        validate_ap_payments(
                            registers=[employee.matricula], only_registers=True
                        )
                    else:
                        log_migration(messages_employee_migration)
                    messages_employee_migration = []
                    employee_pass = True

                employee = pas.servidor
                print("")
                print(f"{WHITE}{employee}{NC} ", end="", flush=True)

            title = f'Férias {"Membros" if pas.servidor.tipo == "M" else "Servidores"} - {pas.periodo_aquisitivo}'
            dgp = GroupPeriod.objects.get(
                title=title.upper(),
                period=pas.periodo_aquisitivo.periodo,
                year_reference=pas.periodo_aquisitivo.ano_aquisicao,
            )
            # print(f'>>>>| GROUP: {"OK" if dgp else "NO"} FOR {pas}')
            dpa, dpa_created = dgp.acquisitionperiods.update_or_create(
                employee=pas.servidor,
                defaults={
                    "status": ACQP_PROGRESS,
                    "start_date_acquisition": pas.data_inicio_aquisicao,
                    "end_date_acquisition": pas.data_fim_aquisicao,
                    "start_date_fruition": pas.data_inicio_usufruto,
                    "end_date_fruition": pas.data_fim_usufruto,
                    "blocked": pas.bloqueado,
                    "days": pas.quantidade_dias,
                    "paid_days_cache": pas.paid_days,
                    "paid_without_payroll": pas.pago_sem_folha,
                    "paycheck_event": pas.folha_evento_terco_constitucional,
                    "automatic_created": False,
                    "continuous_period": True,
                    "note": False,
                    "indemnified": pas.estado == ACQP_INDEMNIFIED,
                    "previous_period": previous_period.get(
                        pas.servidor.matricula, None
                    ),
                },
            )
            previous_period[pas.servidor.matricula] = dpa

            try:
                result, messages = migrate_usufructs(pas, dpa)
                error_e = False
            except Exception as e:
                result = False
                messages = [
                    f"{dpa}\n>>{e}",
                ]
                traceback.print_exc(file=sys.stdout)
                error_e = True

            if not result:
                employee_pass = False
                messages_employee_migration += messages

            print(
                f'{GREEN if result else RED}{"#" if error_e else "*"}{NC}',
                end="",
                flush=True,
            )

            if stop_on_error and not result:
                print("-------------- ERROR -------------------------")
                print(messages_employee_migration)
                return result


def clear_vacations(registers=[]):

    q_activities = Activity.objects.filter(
        acquisition_period__group_period__configuration__type_of_usufruct=1,
    )
    q_periods = AcquisitionPeriod.objects.filter(
        group_period__configuration__type_of_usufruct=1,
    )
    q_payments = Payment.objects.filter(
        acquisition_period__group_period__configuration__type_of_usufruct=1,
    )

    if registers:
        q_activities = q_activities.filter(
            acquisition_period__employee__matricula__in=registers
        )
        q_periods = q_periods.filter(employee__matricula__in=registers)
        q_payments = q_payments.filter(
            acquisition_period__employee__matricula__in=registers
        )

    q_activities.delete()
    q_payments.delete()
    q_periods.delete()


def clear_groups():

    for gp in GroupPeriod.objects.all():
        # print(gp.acquisitionperiods.count(), gp)
        if gp.acquisitionperiods.count() == 0:
            gp.delete()


def migrate_usufructs(pas, dpa):
    pas.atualiza_estado(True)
    usufructs = [usu for usu in pas.usufrutos.order_by("created_at")]
    usufructs_migrateds = {}
    # print(usufructs)

    migrate_first_book_from_scale_annotations(pas, dpa, usufructs, usufructs_migrateds)
    migrate_others_book(pas, dpa, usufructs, usufructs_migrateds)
    # print(usufructs)
    migrate_changed_usufructs(pas, dpa, usufructs, usufructs_migrateds)
    migrate_changed_usufructs_with_inconsistence(
        pas, dpa, usufructs, usufructs_migrateds
    )
    migrate_suspensed_usufruct(pas, dpa, usufructs, usufructs_migrateds)
    migrate_sell_days(pas, dpa, usufructs, usufructs_migrateds)
    migrate_payments(pas, dpa, usufructs, usufructs_migrateds)

    dpa.update_status(update_usufructs=True, validate_prevent=True)

    result, errors = validate_migration(pas, dpa, usufructs, usufructs_migrateds)
    # print(f' {GREEN if result else RED}{"OK" if result else "ERRO"}{NC}')

    # for msg in errors:
    #     print(msg)
    return result, errors


def migrate_first_book_from_scale_annotations(
    pas, dpa, usufructs, usufructs_migrateds, print_=False
):
    """
    HOMOLOGAR, a(s) parcela(s) de férias abaixo relacionada(s), referente à ESCALA DE FÉRIAS do período aquisitivo 2016 / 2017, conforme  ATO 00033/2016-CHGAB/DG (DIÁRIO ELETRÔNICO DO MPE nº 169) de 22/11/2016:

    parcela: 19/11/2018 a 18/12/2018 (30 dias).
    """
    usufructs_ = [u for u in usufructs if not u.alteracao_in.exists()]
    anots = AnotacaoFerias.objects.filter(
        servidor=pas.servidor, identificador=str(pas.pk), texto__icontains="ESCALA"
    ).order_by("-created_at")
    anot = anots.first()
    first_book = []
    days = 0
    if anot:
        print_ and print(anot.texto)
        test_str = anot.texto.replace("\n", "")
        regex = (
            "parcela: (?P<data>[0-9]{2}/[0-9]{2}/[0-9]{4} a [0-9]{2}/[0-9]{2}/[0-9]{4})"
        )
        matches = re.findall(regex, test_str)
        # print(matches)

        authorises = set()
        for match in matches:
            # print('MATCH: ', match)
            anot_start_date = datetime.strptime(match.split()[0], "%d/%m/%Y").date()
            anot_end_date = datetime.strptime(match.split()[2], "%d/%m/%Y").date()
            usufruct = None
            for pasu in usufructs_:
                if (
                    pasu.data_inicio == anot_start_date
                    and pasu.data_prevista_fim == anot_end_date
                ):
                    usufruct = pasu
                    break
            if not usufruct:
                first_book = []
                break
            else:
                first_book.append(usufruct)
                days += (anot_end_date - anot_start_date).days + 1
                if usufruct.estado == 512:
                    authorises.add(False)
                elif usufruct.estado == 1:
                    authorises.add(None)
                else:
                    authorises.add(True)
        # print(days, ' FB: ', first_book)
        # TODO Verificar se pode haver algum efeito colateral, pois escalas que foram
        # parcialmente autorizadas estão sendo migradas como autorizadas e apenas
        # o status da parcela não autorizada foi modificado após criação da atividade de marcação
        if (
            first_book and len(first_book) <= 2 and days <= 30
        ):  # and len(authorises) == 1:
            # print(authorises)
            # if len(first_book) > 2 or days > 30:
            #     print(f'{BLUE}{len(first_book)} {days} {pas}{NC}')
            # elif days < 30:
            #     print(f'{ORANGE}{len(first_book)} {days} {pas}{NC}')
            # else:
            #     print(f'{GREEN}{len(first_book)} {days} {pas}{NC} {first_book}')

            usus = [
                {
                    "start_date": u.data_inicio,
                    "end_date": (u.data_prevista_fim or u.data_fim_cache),
                }
                for u in first_book
            ]
            # TODO Atualizar dados da autorização e homologação

            dpa.status = ACQP_PROGRESS
            res = ActivityBook.do(
                acquisition_period=dpa,
                usufructs_in=usus,
                modifieds=[],
                authorize=True if True in authorises else authorises.pop(),
                # attachment=attachment,
                # justification=justification,
                note=False,
                immediate_authorization=first_book[0].autorizado_por,
                # immediate_authorization_at=first_book[0].autorizado_em,
                # homologation_by=first_book[0].autorizado_por,
                # homologation_at=first_book[0].autorizado_por,
                # mediate_authorization=mediate_authorization,
                context="admin",
                # scale_homologation=True,
            )
            for u in first_book:
                usufructs.remove(u)
                end_date = u.data_prevista_fim or u.data_fim_cache
                usufructs_migrateds[u] = res.usufructs.get(
                    start_date=u.data_inicio, end_date=end_date
                )
                if u.estado == USU_NOT_AUTHORIZED:
                    Usufruct.objects.filter(pk=usufructs_migrateds[u].pk).update(
                        status=USU_NOT_AUTHORIZED
                    )
    return first_book


def migrate_others_book(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    # Filtrando todos os usufrutos que não foram provenientes de uma alteração
    usufructs_to_migrate = [u for u in usufructs if not u.alteracao_in.exists()]

    # Filtrando todos os usufrutos provenientes de uma alteração inconsistente,
    # ou seja, que não possue antigos_pasus
    for c in pas.alteracoes.order_by("criado_em"):
        if not c.antigos_pasus.exists():
            for u in c.novos_pasus.all():
                usufructs_to_migrate.append(u)
    # print(usufructs_to_migrate)
    for usufruct in usufructs_to_migrate:
        # Caso em que o usufruto não é proveniente de uma alteração
        usus = [
            {
                "start_date": usufruct.data_inicio,
                "end_date": usufruct.data_prevista_fim or usufruct.data_fim_cache,
            }
        ]
        # TODO Atualizar dados da autorização e homologação
        if usufruct.estado == 512:
            authorise = False
        elif usufruct.estado == 1:
            authorise = None
        else:
            authorise = True
        dpa.status = ACQP_PROGRESS
        res = ActivityBook.do(
            acquisition_period=dpa,
            usufructs_in=usus,
            modifieds=[],
            authorize=authorise,
            # attachment=attachment,
            # justification=justification,
            note=False,
            immediate_authorization=usufruct.autorizado_por,
            # mediate_authorization=mediate_authorization,
            context="admin",
            # scale_homologation=True,
        )
        ActivityBook.objects.filter(pk=res.pk).update(
            immediate_authorization_at=usufruct.autorizado_em,
            homologation_by=get_current_user(),
            homologation_at=usufruct.autorizado_em,
        )
        usufructs.remove(usufruct)
        usufructs_migrateds[usufruct] = res.usufructs.get()
        # print('MO2:', usufruct)


def migrate_suspensed_usufruct(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    for usufruct in usufructs_migrateds:
        if usufruct.estado in [64, 32]:
            usus = [usufructs_migrateds[usufruct]]
            usus_new = []
            if usufruct.estado == 64:
                # print(f'{RED}SUSPENSO?{NC} {usufruct}')
                KlassActivity = ActivitySuspend
                # TODO Atualizar dados da autorização e homologação
                # immediate_auth_by = usufruct.autorizado_por if usufruct.autorizado_por != dpa.employee else None
            else:
                # print(f'{RED}INTERROMPIDO{NC} {usufruct}')
                KlassActivity = ActivityInterrupt
                end_date = usufruct.data_fim_cache
                if usufruct.data_prevista_fim == usufruct.data_fim_cache:
                    end_date = usufruct.data_fim_cache
                usus_new = [{"start_date": usufruct.data_inicio, "end_date": end_date}]

            dpa.status = ACQP_PROGRESS
            res = KlassActivity.do(
                acquisition_period=dpa,
                usufructs_in=usus_new,
                modifieds=usus,
                authorize=True,
                # attachment=attachment,
                # justification=justification,
                note=False,
                immediate_authorization=usufruct.suspenso_por,
                # immediate_authorization_at=usufruct.autorizado_em,
                # homologation_by=usufruct.autorizado_por,
                # homologation_at=usufruct.autorizado_por,
                # mediate_authorization=mediate_authorization,
                # scale_homologation=True,
            )
            KlassActivity.objects.filter(pk=res.pk).update(
                immediate_authorization_at=usufruct.suspenso_em,
                homologation_by=get_current_user(),
                homologation_at=usufruct.autorizado_em,
            )


def migrate_sell_days(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    if pas.paid_days:
        # print(pas.paid_days)
        dpa.status = ACQP_PROGRESS
        ActivitySell.do(
            days=pas.paid_days,
            acquisition_period=dpa,
            authorize=True,
            note=False,
            context="migrate",
        )


def _migrate_payments_sell(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    entries = [
        p.entry_payment.pk
        for p in Payment.objects.filter(acquisition_period__employee=pas.servidor)
    ]
    # print(pas, pas.paid_days, end=' ')
    ps1 = (
        f"{pas.periodo_aquisitivo}".upper()
        .replace("SEMESTRE", "")
        .replace(" ", "")
        .replace("/", "-")
    )
    ps2 = ps1.split("-")
    q_entries = (
        FolhaEvento.objects.filter(
            evento__numero__in=SELL_EVENTS, servidor=pas.servidor
        )
        .filter(Q(info__icontains=ps2[0]) & Q(info__icontains=ps2[1]))
        .exclude(pk__in=entries)
    )
    q_sum = q_entries.aggregate(tpd=Sum("correct_qnt"), cs=Count("pk"))
    pdays = q_sum["tpd"] or 0
    # if not q_entries:
    #     print(pas, ps2)
    if pdays > pas.paid_days:
        print(f"{pdays}/{pas.paid_days}", end="")
        return []
    else:
        for fe in q_entries:
            usufruct = (
                dpa.usufructs.filter(payments__isnull=True)
                .filter(activity__type_of_activity=ACT_SELL, days=pdays)
                .first()
            )
            dpa.payments.get_or_create(
                entry_payment=fe,
                defaults={
                    "type_of": 2,
                    "info": f"{fe.folha.unicode_cache}",
                    "description": "",
                    "usufruct": usufruct,
                    "payment_oid": fe.pk,
                },
            )
        return q_entries


def _migrate_payments_recision(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    entries = [
        p.entry_payment.pk
        for p in Payment.objects.filter(acquisition_period__employee=pas.servidor)
    ]
    # print(pas, pas.paid_days, end=' ')
    ps1 = (
        f"{pas.periodo_aquisitivo}".upper()
        .replace("SEMESTRE", "")
        .replace(" ", "")
        .replace("/", "-")
    )
    ps2 = ps1.split("-")
    q_entries = (
        FolhaEvento.objects.filter(
            evento__numero__in=RECISION_EVENTS, servidor=pas.servidor
        )
        .filter(Q(info__icontains=ps2[0]) & Q(info__icontains=ps2[1]))
        .exclude(pk__in=entries)
    )
    # if not q_entries:
    #     print(pas, ps2)
    for fe in q_entries:
        dpa.payments.get_or_create(
            entry_payment=fe,
            defaults={
                "type_of": 3,
                "info": f"{fe.folha.unicode_cache}",
                "description": "",
                # 'usufruct': '',
                "payment_oid": fe.pk,
            },
        )
    return q_entries


def _migrate_payments_aid(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    if pas.folha_evento_terco_constitucional:
        dpa.payments.get_or_create(
            entry_payment=pas.folha_evento_terco_constitucional,
            defaults={
                "type_of": 1,
                "info": f"{pas.folha_evento_terco_constitucional.folha.unicode_cache}",
                "description": "",
                # 'usufruct': '',
                "entry_payment": pas.folha_evento_terco_constitucional,
                "payment_oid": pas.folha_evento_terco_constitucional.pk,
            },
        )


def _validate_payments_not_migrated():
    pass


def migrate_payments(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    _migrate_payments_aid(pas, dpa, usufructs, usufructs_migrateds, print_)
    _migrate_payments_sell(pas, dpa, usufructs, usufructs_migrateds, print_)
    _migrate_payments_recision(pas, dpa, usufructs, usufructs_migrateds, print_)
    # acquisition_period
    # type_of
    # info
    # description
    # usufruct
    # entry_payment
    # payment_oid


def migrate_changed_usufructs(pas, dpa, usufructs, usufructs_migrateds, print_=False):
    # TODO Verificar se os dias restantes para época oportuna deve ser informado
    changes = [
        c for c in pas.alteracoes.order_by("criado_em") if c.antigos_pasus.exists()
    ]
    change = changes[0] if changes else None
    idx = 0
    while change:
        ready = True
        usus_new = []
        usus_old = []
        for usufruct in change.antigos_pasus.all():
            if usufruct not in usufructs_migrateds:
                ready = False
            else:
                usus_old.append(usufructs_migrateds[usufruct])
        for usufruct in change.novos_pasus.all():
            if usufruct not in usufructs:
                ready = False
            else:
                usus_new.append(
                    {
                        "usufruct": usufruct,
                        "start_date": usufruct.data_inicio,
                        "end_date": usufruct.data_prevista_fim
                        or usufruct.data_fim_cache,
                    }
                )

        authorise = None
        if change.autorizado_em:
            authorise = True if change.autorizado else False
        # print(change, ready, change.autorizado, authorise, change.pas)
        if ready:
            # print(f'{ORANGE}ALTERADO{NC} {change} {usus_new} {usus_old}')
            dpa.status = ACQP_PROGRESS
            res = ActivityChange.do(
                acquisition_period=dpa,
                usufructs_in=usus_new,
                modifieds=usus_old,
                authorize=authorise,
                # attachment=attachment,
                # justification=justification,
                note=False,
                immediate_authorization=change.autorizado_por,
                # mediate_authorization=mediate_authorization,
                context="admin",
                # scale_homologation=True,
            )
            ActivityChange.objects.filter(pk=res.pk).update(
                immediate_authorization_at=change.autorizado_em,
                homologation_by=get_current_user(),
                homologation_at=change.autorizado_em,
            )
            for u in usus_new:
                usufructs.remove(u["usufruct"])
                end_date = (
                    u["usufruct"].data_prevista_fim or u["usufruct"].data_fim_cache
                )
                u_new = res.usufructs.get(
                    start_date=u["usufruct"].data_inicio, end_date=end_date
                )
                # u_new.atualiza_estado(validate_prevent=True)
                usufructs_migrateds[u["usufruct"]] = u_new
            # for u in usus_old:
            #     u.update_status()
            # res.update_status()

            changes.remove(change)
            idx = 0
        else:
            idx += 1
        change = changes[idx] if idx < len(changes) else None


def migrate_changed_usufructs_with_inconsistence(
    pas, dpa, usufructs, usufructs_migrateds, print_=False
):
    # TODO Verificar se os dias restantes para época oportuna deve ser informado
    usu_changes = [
        u
        for u in usufructs_migrateds
        if (u.estado == USU_CHANGED and not u.alteracao_out.exists())
    ]
    for u in usu_changes:
        # print(u, u.alteracao_out.exists(), u.get_estado_display())
        dpa.status = ACQP_PROGRESS
        res = ActivityChange.do(
            acquisition_period=dpa,
            usufructs_in=[],
            modifieds=[usufructs_migrateds[u].pk],
            authorize=True,
            # attachment=attachment,
            # justification=justification,
            note=False,
            immediate_authorization=u.autorizado_por,
            # mediate_authorization=mediate_authorization,
            context="admin",
            # scale_homologation=True,
        )
        ActivityChange.objects.filter(pk=res.pk).update(
            immediate_authorization_at=u.modified_at,
            homologation_by=get_current_user(),
            homologation_at=u.modified_at,
        )


def clear_actions_before_migrate(registers=[]):
    query = Activity.objects.filter()
    if registers:
        query = query.filter(acquisition_period__employee__matricula__in=registers)
    return query.delete()


def update_data_before_migrate():
    # Corrigindo inconsistencia de alterações onde as parcelas foram autorizadas, mas a alteração consta como não alterada
    AlteracaoPASU.objects.filter(pk__in=[1, 26, 27, 41, 61, 82, 5567]).update(
        autorizado=True
    )

    # Corrigindo inconsistencia de alterações onde as parcelas foram autorizadas, mas a alteração consta como não alterada
    pks = [5198, 19102, 17496]
    for pasu in (
        PeriodoAquisitivoServidorUsufruto.objects.annotate(alts=Count("alteracao_out"))
        .filter(alteracao_out__autorizado=True, estado=256)
        .filter(alts=1)
    ):
        pks.append(pasu.alteracao_out.get().pk)
    AlteracaoPASU.objects.filter(pk__in=pks).update(autorizado=False)

    # Corrigindo usufrutos que está com data_prevista_fim inconsistente.
    PeriodoAquisitivoServidorUsufruto.objects.filter(pk=2376).update(
        data_prevista_fim=date(2013, 7, 28)
    )
    PeriodoAquisitivoServidorUsufruto.objects.filter(pk=6908).update(
        data_prevista_fim=date(2009, 8, 4)
    )


def validate_sell_payments(registers=[], type_of=None, only_registers=False):

    if not only_registers:
        registers += load_finisheds()
    q_payments_entries = FolhaEvento.objects.filter(
        evento__numero__in=SELL_EVENTS, dayoff_payments__isnull=True
    )
    if type_of:
        q_payments_entries = q_payments_entries.exclude(servidor__tipo=type_of)
    if registers:
        q_payments_entries = q_payments_entries.filter(
            servidor__matricula__in=registers
        )
    if q_payments_entries:
        print(f" {ORANGE}LANCAMENTOS NÃO CONTABILIZADOS NOS PERIODOS AQUISITIVOS{NC}")
    for fe in q_payments_entries:
        print(" > ", fe.pk, fe, fe.qnt, fe.contracheque)


def validate_ap_payments(registers=[], type_of=None, only_registers=False):

    if not only_registers:
        registers += load_finisheds()
    print(registers)
    q_acquisition_periods = AcquisitionPeriod.objects.filter()

    if type_of:
        q_acquisition_periods = q_acquisition_periods.exclude(employee__tipo=type_of)
    if registers:
        q_acquisition_periods = q_acquisition_periods.filter(
            employee__matricula__in=registers
        )
    employee = None

    for ap in q_acquisition_periods.order_by("employee"):
        if employee and ap.employee != employee:
            print(f" {ORANGE}PERIODOS COM INCONSISTENCIAS DE PAGAMENTOS{NC}")
            validate_sell_payments(
                registers=[ap.employee.matricula], only_registers=only_registers
            )
        p1 = ap.paid_days
        p2 = sum(p.entry_payment.qnt for p in ap.payments.filter(type_of__in=[2, 3]))
        if p1 != p2:
            print(f" > {p1}/{p2:0.1f} - {ap.pk} {ap}")
        employee = ap.employee

    if employee:
        validate_sell_payments(
            registers=[employee.matricula], only_registers=only_registers
        )


if __name__ == "__main__":
    print("")
    migrate_vacations(clear=True, stop_on_error=False)
    # migrate_vacations(registers=[14093], clear=True, stop_on_error=False)
    # validate_sell_payments()
    # validate_ap_payments(registers=[14093], only_registers=True)
    # migrate_vacations(registers=[], clear=True, only_finished=False, stop_on_error=False)
