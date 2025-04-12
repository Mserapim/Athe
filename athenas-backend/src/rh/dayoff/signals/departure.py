# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from contrib.utils import DateUtils, getLogger
from rh.afastamento.models import (
    Afastamento,
    AfastamentoComparecimentoJuizo,
    AfastamentoCompeticao,
    AfastamentoCursoConcurso,
    AfastamentoDeslocamento,
    AfastamentoDisponibilidade,
    AfastamentoEleitoral,
    AfastamentoEstudar,
    AfastamentoMandatoEletivo,
    AfastamentoMissao,
    AfastamentoOutroOrgao,
    AfastamentoPrisao,
    AfastamentoServirJuri,
    AfastamentoSuspensao,
    AfastamentoTreinamento,
    AtuacaoGrupoTrabalho,
    Ausencia,
    AusenciaCasamento,
    AusenciaConclusao,
    AusenciaDoacaoSangue,
    AusenciaEleitor,
    AusenciaFalecimento,
    AusenciaNascimento,
    AwardLicense,
    BancoDeHoras,
    DesempenhoFuncao,
    FeriasAfastamento,
    FolgaAniversario,
    FolgaCompensacao,
    FolgaEleitoral,
    HealthPrevent,
    Licenca,
    LicencaAdocao,
    LicencaAfastamentoConjuge,
    LicencaAtividadePolitica,
    LicencaCapacitacao,
    LicencaDoencaPessoaFamilia,
    LicencaInteresseParticular,
    LicencaMandatoClassista,
    LicencaMaternidade,
    LicencaSaude3Dias,
    LicencaSaude30Dias,
    LicencaSaudeJuntaMedica,
    LicencaServicoMilitar,
    Plantao,
    Recesso,
    Viagem,
    AfastamentoCandidatura,
)
from rh.const import CANCELED, INTERRUPTION, SCHEDULED, SUSPENSION
from rh.dayoff.const import (
    ACT_CHANGE,
    ACT_INTERRUPT,
    ACT_SELL,
    ACT_ST_CANCELED,
    ACT_ST_HOMOLOGATED,
    ACT_SUSPEND,
    BLOOD_DONATION_USUFRUCT,
    USU_CANCELED,
    USU_CHANGED,
    USU_ENJOYED,
    USU_ENJOYING,
    USU_HOMOLOGATED,
    USU_INTERRUPTED,
    USU_NOT_AUTHORIZED,
    USU_SUSPENDED,
)
from rh.dayoff.models import (
    AcquisitionPeriod,
    AcquisitionPeriodAttachment,
    ActivityBook,
    ActivityChange,
    ActivityIndemnify,
    ActivityInterrupt,
    ActivitySell,
    ActivitySuspend,
    ActivityBookSell,
    ActivityCancel,
    ActivityRetify,
    ActivityRemaining,
    GroupPeriod,
    Usufruct,
)
from rh.models import (
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoRequisicao,
    RequestMove,
)
from rh.pvf.models import PortalRequestUsufruct
from standard.models import Choice
from datetime import datetime, timedelta
from rh.models import (
    Servidor,
    ServidorLotacao,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
)

log = getLogger(__name__)


@receiver(pre_delete, sender=Usufruct, dispatch_uid="post_delete_dayoff_usufruct")
def usufruct_cancel(sender, instance, **kargs):
    manager_usufruct(instance, None, to_delete=True)


@receiver(post_save, sender=ActivityBook)
@receiver(post_save, sender=ActivityChange)
@receiver(post_save, sender=ActivityInterrupt)
@receiver(post_save, sender=ActivitySuspend)
@receiver(post_save, sender=ActivityIndemnify)
@receiver(post_save, sender=ActivitySell)
@receiver(post_save, sender=ActivityBookSell)
@receiver(post_save, sender=ActivityCancel)
@receiver(post_save, sender=ActivityRetify)
@receiver(post_save, sender=ActivityRemaining)
def activity_save(sender, instance, **kargs):
    manager_departure(activity=instance)


@receiver(pre_delete, sender=ActivityBook)
@receiver(pre_delete, sender=ActivityChange)
@receiver(pre_delete, sender=ActivityInterrupt)
@receiver(pre_delete, sender=ActivitySuspend)
@receiver(pre_delete, sender=ActivityIndemnify)
@receiver(pre_delete, sender=ActivitySell)
@receiver(pre_delete, sender=ActivityBookSell)
@receiver(pre_delete, sender=ActivityCancel)
@receiver(pre_delete, sender=ActivityRetify)
@receiver(pre_delete, sender=ActivityRemaining)
def activity_pre_delete(sender, instance, **kargs):
    manager_departure(activity=instance, to_delete=True)


def manager_departure(activity, to_delete=False):
    """
    USU_STATUS:
    USU_NEW = 1  "Inclusão solicitada"
    USU_AUTORIZED_CI = 2  "Autorizado"
    USU_HOMOLOGATED = 4  "Homologado"  # CRIAR AFASTAMENTO
    USU_CHANGING = 8  "Alteração solicitada"
    USU_CHANGED = 16  "Alterado"  # APAGAR AFASTAMENTO
    USU_INTERRUPTED = 32  "Interrompido"  # ALTERAR AFASTAMENTO
    USU_SUSPENDED = 64  "Suspenso"  # APAGAR AFASTAMENTO
    USU_ENJOYING = 128  "Em fruição"
    USU_ENJOYED = 256  "Usufruído"
    USU_NOT_AUTHORIZED = 512  "Não autorizado"
    USU_SUBSTITUTE = 1024  "Substituto"
    USU_SOLD = 4096  "Vendido"
    USU_CANCELED = 2048 "Cancelado"

    ACT_STATUS:
    ACT_ST_CREATED = 1 "CRIADO"
    ACT_ST_AUTHORIZED = 2 "AUTORIZADO"
    ACT_ST_AUTHORIZED_M = 6 "AUTORIZADO CHEFE MEDIATO"
    ACT_ST_NOT_AUTHORIZED = 3 "NÃO AUTORIZADO"
    ACT_ST_HOMOLOGATED = 4 "HOMOLOGADO"
    ACT_ST_CANCELED = 5 "CANCELADO"
    ACT_ST_SOLD = 7 "VENDIDO"

    ACT_TYPE:
    ACT_BOOK = 1 "MARCAÇÃO"
    ACT_CHANGE = 2 "ALTERAÇÃO"get_status_display
    ACT_SUSPEND = 3 "SUSPENSÃO"
    ACT_INTERRUPT = 4 "INTERRUPÇÃO"
    ACT_INDEMNIFY = 5 "INDENIZAÇÃO"
    ACT_SELL = 7 "VENDA"
    """
    try:
        if (
            activity.status in (ACT_ST_HOMOLOGATED, ACT_ST_CANCELED)
            and activity.type_of_activity != ACT_SELL
        ):

            def _call_manager_usufructs():
                for usufruct in activity.usufructs.filter().order_by("start_date"):
                    manager_usufruct(usufruct, activity)

            def _call_manager_modifieds():
                for usufruct in activity.modifieds.filter().order_by("start_date"):
                    manager_usufruct(usufruct, activity)

            def _call_manager_usufruct_modifieds():
                usufructs = Usufruct.objects.filter(pk__in=activity.usufruct_modifieds)
                for usufruct in usufructs:
                    manager_usufruct(
                        usufruct, usufruct.activity, usufruct_modified=True
                    )

            def _which_call_first():
                match_usufructs = False
                for usu in activity.usufructs.filter():
                    if usu.status in (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED):
                        if (
                            usu.activity.type_of_activity
                            in (ACT_INTERRUPT, ACT_SUSPEND, ACT_CHANGE)
                            and usu.activity.modifieds.filter(
                                start_date=usu.start_date
                            ).exists()
                        ):
                            """se for de interrupção e estiver entrando outro usufruto com a mesma data de início manda atualizar para reutilizar o afastamento"""
                            match_usufructs = True
                            break
                        elif (
                            activity.status == ACT_ST_CANCELED
                            and activity.usufructs.filter(
                                start_date=usu.start_date
                            ).exists()
                        ):
                            match_usufructs = True
                            break
                    elif usu.status in (
                        USU_INTERRUPTED,
                        USU_SUSPENDED,
                        USU_CHANGED,
                        USU_NOT_AUTHORIZED,
                        USU_CANCELED,
                    ):
                        match_usufructs = False
                        if (
                            usu.status != USU_CANCELED
                            and activity.type_of_activity
                            in (ACT_INTERRUPT, ACT_SUSPEND, ACT_CHANGE)
                        ):
                            for usu_in in activity.usufructsin:
                                if usu.start_date == usu_in.get("start_date"):
                                    """se for de interrupção e o usufruto interrompido possuir um que está sendo marcado com a mesma data de início não fará nada"""
                                    match_usufructs = True
                                    break
                        elif usu.status == USU_CANCELED:
                            if usu.activity.modifieds.filter(
                                start_date=usu.start_date
                            ).exists():
                                """caso seja cancelamento de usufruto que possua outro(mesmo start_date) que voltará para homologado, não fará nada"""
                                match_usufructs = True
                                break
                            else:
                                """caso seja cancelamento de usufruto que não possua outro(mesmo start_date) que voltará para homologado, fará update para cancelado"""
                                match_usufructs = True
                                break

                return "usufructs" if match_usufructs else "modifieds"

            which = _which_call_first()
            if which == "usufructs":
                _call_manager_usufructs()
                _call_manager_modifieds()
                _call_manager_usufruct_modifieds()
            else:
                _call_manager_modifieds()
                _call_manager_usufructs()
                _call_manager_usufruct_modifieds()

    except Exception as err:
        log.exception(err)
        # print(err)


def manager_usufruct(usufruct, activity_call, to_delete=False, usufruct_modified=False):
    must_create = False
    must_update = False
    if (
        usufruct.status in (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED)
        and to_delete is False
    ):
        must_create = True
        if usufruct.activity.type_of_activity in (
            ACT_INTERRUPT,
            ACT_SUSPEND,
            ACT_CHANGE,
        ):
            if usufruct.activity.modifieds.filter(
                start_date=usufruct.start_date
            ).exists():
                """se for de interrupção e estiver entrando outro usufruto com a mesma data de início manda atualizar para reutilizar o afastamento"""
                must_create = False
                must_update = True
            else:
                must_create = True
                must_update = False
        elif (
            activity_call.status == ACT_ST_CANCELED
            and activity_call.usufructs.filter(start_date=usufruct.start_date).exists()
        ):
            must_create = False
            must_update = True
    elif (
        usufruct.status
        in (
            USU_INTERRUPTED,
            USU_SUSPENDED,
            USU_CHANGED,
            USU_NOT_AUTHORIZED,
            USU_CANCELED,
        )
        and to_delete is False
    ):
        must_update = True
        if usufruct.status != USU_CANCELED and activity_call.type_of_activity in (
            ACT_INTERRUPT,
            ACT_SUSPEND,
            ACT_CHANGE,
        ):
            for usu_in in activity_call.usufructsin:
                if usufruct.start_date == usu_in.get("start_date"):
                    """se for de interrupção e o usufruto interrompido possuir um que está sendo marcado com a mesma data de início não fará nada"""
                    must_update = False
                    break
        elif usufruct.status == USU_CANCELED:
            if usufruct.activity.modifieds.filter(
                start_date=usufruct.start_date
            ).exists():
                """caso seja cancelamento de usufruto que possua outro(mesmo start_date) que voltará para homologado, não fará nada"""
                must_update = False
            else:
                """caso seja cancelamento de usufruto que não possua outro(mesmo start_date) que voltará para homologado, fará update para cancelado"""
                must_update = True

    if (
        usufruct.status not in (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED)
        and usufruct_modified
    ):
        must_update = True

    if must_create:
        _create(usufruct)
    if must_update or to_delete is True:
        _update(usufruct, to_delete=to_delete)


def _create(usufruct):
    _klass = usufruct.configuration.departure_class
    departures = _klass.objects.filter(
        servidor=usufruct.employee, data_inicio=usufruct.start_date
    ).exclude(estado=CANCELED)

    if not departures.exists():
        if PortalRequestUsufruct.objects.filter(activity=usufruct.activity).exists():
            origin_register = 1  # Vida Funcional
        else:
            origin_register = 4  # Gerenciador Admin
        _kargs = {
            "servidor": usufruct.employee,
            "data_inicio": usufruct.start_date,
            "data_prevista": usufruct.end_date,
            "data_fim": usufruct.end_date,
            "publicacao_movimentacao": None,
            "estado": SCHEDULED,
            "origin_register": origin_register,
        }
        if _klass == FolgaEleitoral:
            _kargs.update(
                {"ano": usufruct.acquisition_period.group_period.year_reference}
            )
            if Choice.objects.filter(
                app_label="rh",
                name="TURNO_ELEITORAL",
                value=usufruct.acquisition_period.group_period.period,
            ).exists():
                _kargs.update(
                    {"turno": usufruct.acquisition_period.group_period.period}
                )
        elif _klass == Recesso:
            _kargs.update(
                {"ano": usufruct.acquisition_period.group_period.year_reference}
            )
        elif _klass == FolgaAniversario:
            _kargs.update(
                {
                    "ano": usufruct.acquisition_period.group_period.year_reference,
                    "data_referencia": usufruct.acquisition_period.start_date_acquisition,
                }
            )

        departure = _klass.objects.create(**_kargs)
        # print(f'Afastamento criado: {departure.pk} | {departure.__str_restful__()}')
        log.debug(f"Afastamento criado: {departure.pk} | {departure.__str_restful__()}")

        Usufruct.objects.filter(pk=usufruct.pk).update(departure=departure)
    else:
        departure = departures.last()
        log.debug(
            f"Já possui afastamento({departures.count()}): {departure.pk} | {departure.__str_restful__()}"
        )
        Usufruct.objects.filter(pk=usufruct.pk).update(departure=departure)


def _update(usufruct, to_delete=False):
    klass_departure = usufruct.configuration.departure_class
    departure = usufruct.departure
    if not departure:
        departure = (
            klass_departure.objects.filter(
                servidor=usufruct.employee, data_inicio=usufruct.start_date
            )
            .exclude(estado=CANCELED)
            .last()
        )
    if departure:
        # print(f'afastamento encontrado: {departure.pk} | {departure.__str_restful__()}')
        log.debug(
            f"afastamento encontrado: {departure.pk} | {departure.__str_restful__()}"
        )
        old_alteration = departure.alteracao
        alteration = departure.alteracao
        old_end_date = departure.data_fim
        if usufruct.status in (USU_HOMOLOGATED, USU_ENJOYING, USU_ENJOYED):
            prevision_date = usufruct.end_date
            alteration = None
        else:
            prevision_date = departure.data_prevista
        end_date = usufruct.end_date

        if usufruct.status == USU_SUSPENDED:
            alteration = SUSPENSION
        elif to_delete is True or usufruct.status in (
            USU_CANCELED,
            USU_NOT_AUTHORIZED,
            USU_CHANGED,
            USU_INTERRUPTED,
        ):
            alteration = CANCELED
        elif usufruct.activity.modifieds.filter(status=USU_INTERRUPTED).exists():
            alteration = INTERRUPTION

        if alteration != old_alteration or end_date != old_end_date:

            if not alteration == INTERRUPTION:
                klass_departure.objects.filter(pk=departure.pk).update(
                    data_prevista=prevision_date, data_fim=end_date
                )
            else:
                klass_departure.objects.filter(pk=departure.pk).update(
                    data_fim=end_date
                )

            departure = klass_departure.objects.get(pk=departure.pk)
            departure.alteracao = alteration
            departure.origin_register = 4  # Gerenciador Admin
            departure.save()

        if not to_delete:
            Usufruct.objects.filter(departure=departure).update(departure=None)
            Usufruct.objects.filter(pk=usufruct.pk).update(departure=departure)
    elif not to_delete and usufruct.status in (
        USU_HOMOLOGATED,
        USU_ENJOYING,
        USU_ENJOYED,
    ):
        log.debug(
            f"Nenhum afastamento encontrado para {usufruct} | {usufruct.employee}."
        )
        _create(usufruct)


def update_acquisition_from_departure(sender, instance, **kargs):
    """Este sinal deve chamar o método AcquisitionPeriod.acquisition_manager"""
    list_dates = set(
        filter(lambda x: x is not None, [instance.data_fim, instance.data_prevista])
    )
    end_date = None
    if list_dates:
        end_date = max(list_dates)
    AcquisitionPeriod.acquisition_manager(
        instance.servidor, start_date=instance.data_inicio, end_date=end_date
    )
    """Código foi comentado pois ainda não foi definido como serão criados os recessos legados"""
    # GroupPeriod.call_run_generate_periods(instance.servidor, date_reference=instance.data_inicio)


@receiver(post_save, sender=Afastamento)
@receiver(post_save, sender=Licenca)
@receiver(post_save, sender=Ausencia)
@receiver(post_save, sender=FeriasAfastamento)
@receiver(post_save, sender=Viagem)
@receiver(post_save, sender=Recesso)
@receiver(post_save, sender=FolgaEleitoral)
@receiver(post_save, sender=FolgaAniversario)
@receiver(post_save, sender=FolgaCompensacao)
@receiver(post_save, sender=BancoDeHoras)
@receiver(post_save, sender=AtuacaoGrupoTrabalho)
@receiver(post_save, sender=DesempenhoFuncao)
@receiver(post_save, sender=Plantao)
@receiver(post_save, sender=LicencaSaude3Dias)
@receiver(post_save, sender=LicencaSaude30Dias)
@receiver(post_save, sender=LicencaSaudeJuntaMedica)
@receiver(post_save, sender=LicencaDoencaPessoaFamilia)
@receiver(post_save, sender=LicencaMaternidade)
@receiver(post_save, sender=LicencaAdocao)
@receiver(post_save, sender=LicencaAfastamentoConjuge)
@receiver(post_save, sender=LicencaServicoMilitar)
@receiver(post_save, sender=LicencaAtividadePolitica)
@receiver(post_save, sender=LicencaCapacitacao)
@receiver(post_save, sender=LicencaInteresseParticular)
@receiver(post_save, sender=LicencaMandatoClassista)
@receiver(post_save, sender=AwardLicense)
@receiver(post_save, sender=AfastamentoDisponibilidade)
@receiver(post_save, sender=HealthPrevent)
@receiver(post_save, sender=AfastamentoOutroOrgao)
@receiver(post_save, sender=AfastamentoMandatoEletivo)
@receiver(post_save, sender=AfastamentoEstudar)
@receiver(post_save, sender=AfastamentoMissao)
@receiver(post_save, sender=AfastamentoEleitoral)
@receiver(post_save, sender=AfastamentoServirJuri)
@receiver(post_save, sender=AfastamentoTreinamento)
@receiver(post_save, sender=AfastamentoDeslocamento)
@receiver(post_save, sender=AfastamentoCompeticao)
@receiver(post_save, sender=AfastamentoCursoConcurso)
@receiver(post_save, sender=AfastamentoPrisao)
@receiver(post_save, sender=AfastamentoSuspensao)
@receiver(post_save, sender=AfastamentoComparecimentoJuizo)
@receiver(post_save, sender=AfastamentoCandidatura)
@receiver(post_save, sender=AusenciaDoacaoSangue)
@receiver(post_save, sender=AusenciaEleitor)
@receiver(post_save, sender=AusenciaCasamento)
@receiver(post_save, sender=AusenciaNascimento)
@receiver(post_save, sender=AusenciaFalecimento)
@receiver(post_save, sender=AusenciaConclusao)
def usufruct_change_suspend(sender, instance, **kargs):
    log.info("AcquisitionPeriod.usufruct_change_suspend não instalado")
    # AcquisitionPeriod.suspend_usufruct_by_departure(instance)
    transaction.on_commit(
        lambda: update_acquisition_from_departure(sender, instance, **kargs)
    )


@receiver(post_save, sender=MovimentacaoDesligamento)
@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoRequisicao)
@receiver(post_save, sender=RequestMove)
def update_periods_dayoff(sender, instance, **kargs):
    if isinstance(instance, MovimentacaoDesligamento):
        date_reference = instance.data_desligamento
    elif isinstance(instance, MovimentacaoPosse):
        date_reference = instance.data_exercicio
    elif isinstance(instance, MovimentacaoRequisicao):
        date_reference = instance.data_inicio
    elif isinstance(instance, RequestMove):
        date_reference = instance.data_inicio
    transaction.on_commit(
        lambda: GroupPeriod.call_run_generate_periods(
            employee=instance.servidor, date_reference=date_reference
        )
    )


@receiver(post_save, sender=AusenciaDoacaoSangue)
def create_usufruct_from_ausenciadoacaosangue(sender, instance, **kargs):
    if instance.servidor.type_by_possession in ["EFE", "ECM", "EFC", "CMS", "EST"]:
        reference_date = instance.data_inicio

        start_date_acquisition = datetime(reference_date.year, 1, 1).date()
        start_date_fruition = start_date_acquisition
        end_date_acquisition = datetime(reference_date.year, 12, 31).date()

        description = (
            start_date_acquisition.strftime("%d/%m/%Y")
            + " - "
            + end_date_acquisition.strftime("%d/%m/%Y")
        )

        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=BLOOD_DONATION_USUFRUCT,
            year_reference=reference_date.year,
        ).first()

        acquisition_period, _ = AcquisitionPeriod.objects.get_or_create(
            start_date_acquisition=start_date_acquisition,
            start_date_fruition=start_date_fruition,
            end_date_acquisition=end_date_acquisition,
            group_period=group_period,
            employee=instance.servidor,
            defaults={
                "automatic_created": True,
                "real_days_cache": 0,
                "days_to_enjoy_cache": 0,
                "days_not_booked_cache": 0,
                "days": 0,
                "suspended_days": 0,
                "paid_days_cache": 0,
                "status": 2,  # Em andamento
                "pendency": False,
                "continuous_period": False,
                "blocked": False,
                "description": description,
            },
        )

        __, ___ = AcquisitionPeriodAttachment.objects.get_or_create(
            date_start=datetime(
                instance.data_inicio.year,
                instance.data_inicio.month,
                instance.data_inicio.day,
            ).date(),
            date_end=datetime(
                instance.data_fim.year, instance.data_fim.month, instance.data_fim.day
            ).date(),
            acquisition_period=acquisition_period,
            defaults={
                "days_law": 1,
                "description": f"{instance}",
            },
        )


@receiver(post_save, sender=AusenciaDoacaoSangue)
def create_birthday_recess_from_ausenciadoacaosangue(sender, instance, **kargs):
    if instance.servidor.type_by_possession in ["EFE", "ECM", "EFC", "CMS"]:
        total_days = 0
        today = datetime.now()
        birthday_date = datetime(
            today.year,
            instance.servidor.pessoa_fisica.data_nascimento.month,
            instance.servidor.pessoa_fisica.data_nascimento.day,
        ).date()

        if birthday_date < today.date():
            birthday_date = datetime(
                today.year + 1,
                instance.servidor.pessoa_fisica.data_nascimento.month,
                instance.servidor.pessoa_fisica.data_nascimento.day,
            ).date()

        if birthday_date.weekday() in (5, 6) or DateUtils.is_holiday(birthday_date):
            birthday_date = DateUtils.next_business_day(birthday_date)
        attachments = AcquisitionPeriodAttachment.objects.filter(
            date_start__gte=datetime(
                birthday_date.year, birthday_date.month, birthday_date.day
            )
            - relativedelta(years=1),
            acquisition_period__group_period__configuration__sub_type_of_usufruct=BLOOD_DONATION_USUFRUCT,
            acquisition_period__employee=instance.servidor,
        )
        for attachment in attachments:
            total_days += attachment.days_law
        if (total_days >= 3 and instance.servidor.pessoa_fisica.sexo == "M") or (
            total_days >= 2 and instance.servidor.pessoa_fisica.sexo == "F"
        ):
            _, __ = FolgaAniversario.objects.get_or_create(
                remunerado=True,
                data_inicio=birthday_date,
                data_fim=birthday_date,
                tipo=43,  # FolgaAniversário
                data_referencia=birthday_date,
                ano=today.year,
                servidor=instance.servidor,
                defaults={
                    "estado": 2,  # Ativo
                },
            )
