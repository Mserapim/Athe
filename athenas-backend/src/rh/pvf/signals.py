from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from contrib.utils import getLogger

from .tasks import send_mail_pvf
from engine.mq.models import Task
from rh.models import Employee, Pessoa, PessoaFisica, Servidor
from rh.pvf.models import (
    PortalRequestHistory,
    PortalRequest,
    PortalRequestUsufruct,
    PortalRequestWorkload,
    PortalRetificationSchedule,
    PortalRequestDoc,
    PortalCancelSchedule,
    SendingTimeSheet,
    SendingTelework,
    ApproveServerDuty,
    PortalRequestProgression,
    PortalRequestProgressionH,
)
from rh.pvf.absence.models import (
    HealthTreatmentAbsence,
    FamilyHealthTreatmentAbsence,
    MaternityAbsence,
    PaternityAbsence,
    MourningAbsence,
    MarriageAbsence,
)
from rh.pvf.const import *
from standard.models import Choice, Item, EmailTemplate

import re


log = getLogger(__name__)


@receiver(post_save, sender=PortalRequestHistory)
def handler_pvf_send_email(sender, instance, **kwargs):
    """
    O presente signal trata do envio de E-mails pelo portal Vida Funcional, nos seguintes casos

    1 - Ao solicitante, ao criar uma nova solicitação
    2 - Ao aprovador (Exceto quando o aprovador for um grupo de aprovação)
    3 - Ao solicitante quando a solicitação for efetivada
    4 - Ao solicitante quando a solicitação for indeferida.
    5 - O substituto que há solicitação para dar ciência.
    6 - Devolver ao solicitante.
    7 - Reenvio da solicitação.

    Verifica-se há alterações no model PortalRequestHistory e a depender da ação ocorrida no histórico, efetiva-se o envio do email.

    """

    try:
        instance_request = instance.portal_request
        request_type = instance.portal_request.type_of_request
        request_date = instance.portal_request.date.strftime("%d/%m/%Y")
        approver = instance.portal_request.approver
        employee = instance.portal_request.employee
        id_request = instance.portal_request.id
        subject = "Portal Vida Funcional - Protocolo ID: {} [{}]".format(
            id_request, request_type
        )

        person = PessoaFisica.objects.get(
            id=instance.portal_request.employee.pessoa_fisica.id
        )

        requester_email = [
            {
                "email": person.email_institucional,
                "nome": employee.pessoa_fisica.social_name,
                "idUsuario": employee.id_usuario_mastiff,
            },
        ]
        pattern = re.compile(r"<[^>]*>")

        task = Task()
        task.owner = instance.portal_request.request
        task.save()

        if instance.action in [
            REQUEST_ACT_SOLICITATION,
            REQUEST_ACT_OPEN_SOLICITANTION,
        ]:
            """
            Verifica o status 1 - Solicitação
            """

            if (
                instance_request.portal_request_type
                != PORTAL_REQUEST_TYPE_PROGRESSION_V
            ):
                message = (
                    "A solicitação {} foi recepcionada pelo sistema Athenas.".format(
                        id_request
                    )
                )

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=requester_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )

        # if instance.action == REQUEST_ACT_DEFER:
        #     """
        #     Verifica o status 2 - Deferimento
        #     """
        #     message = 'A solicitação {} foi deferida'.format(id_request)

        #     send_mail_pvf(
        #         task        = task.uuid,
        #         hook        = None,
        #         subject     = subject,
        #         messages    = message,
        #         solicitation= request_type,
        #         code        = str(id_request),
        #         date        = str(request_date),
        #         requester   = employee.pessoa_fisica.social_name,
        #         receivers   = requester_email,
        #         receivers_rh_person_ids= None,
        #         success     ="Email enviado com sucesso.",
        #         user        =instance.portal_request.request,
        #     )

        if instance.action == REQUEST_ACT_INDEFER:
            """
            Verifica o status 3 - Indeferimento
            """
            message = "A solicitação {} foi indeferida.".format(id_request)

            send_mail_pvf(
                task=task.uuid,
                hook=None,
                subject=subject,
                messages=message,
                solicitation=request_type,
                code=str(id_request),
                date=str(request_date),
                requester=employee.pessoa_fisica.social_name,
                observation=instance.observation,
                receivers=requester_email,
                receivers_rh_person_ids=None,
                success="Email enviado com sucesso.",
                user=instance.portal_request.request,
            )

        if instance.action == REQUEST_ACT_DEFER:
            """
            Verifica o status 2 - Deferimento
            """

            if (
                instance_request.portal_request_type
                == PORTAL_CANCELAMENTO_TELETRABALHO_TYPE
            ):
                log.info(f"PORTAL_CANCELAMENTO_TELETRABALHO_TYPE")
                email_approvers = Item.objects.get(
                    configuration__application="vdf",
                    key="notificao-gerencia-desenvolvimento",
                ).value
                approver_email = get_emails_approvers(email_approvers)
                html_message = EmailTemplate.objects.get(
                    code="NOTIFICACAO_CANCELAMENTO_TELETRABALHO"
                ).contents
                message = (
                    re.sub(pattern, "", html_message)
                    .replace("%action%", instance.get_action_display())
                    .replace("%status%", instance_request.get_status_display())
                )

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=approver_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )
            elif (
                instance_request.portal_request_type
                == PORTAL_SOLICITACAO_DESBLOQUEIO_TELETRABALHO
            ):
                message = "A solicitação {} foi deferida".format(id_request)

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=requester_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )

        if instance.action == REQUEST_ACT_EFFECTIVENESS:
            """
            Verifica o status 6 - Efetivação
            """
            if (
                instance_request.portal_request_type
                != PORTAL_REQUEST_TYPE_PROGRESSION_V
            ):
                message = "A solicitação {} foi finalizada.".format(id_request)

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=requester_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )

        if instance.action == REQUEST_ACT_CANCEL:
            """
            Verifica o status 7 - Cancelada
            """
            message = "A solicitação {} foi cancelada.".format(id_request)

            send_mail_pvf(
                task=task.uuid,
                hook=None,
                subject=subject,
                messages=message,
                solicitation=request_type,
                code=str(id_request),
                date=str(request_date),
                requester=employee.pessoa_fisica.social_name,
                observation=instance.observation,
                receivers=requester_email,
                receivers_rh_person_ids=None,
                success="Email enviado com sucesso.",
                user=instance.portal_request.request,
            )

        if instance.action == REQUEST_ACT_RETURN_APPLICANT:
            """
            Verifica o status 9 - Devolver ao solicitante
            """
            if (
                instance_request.portal_request_type
                != PORTAL_REQUEST_TYPE_PROGRESSION_V
            ):
                message = "A solicitação {} foi devolvida para alterações.".format(
                    id_request
                )

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=requester_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )

    except Exception as e:
        log.error(e)

    try:
        if approver:
            if instance.action in [
                REQUEST_ACT_SOLICITATION,
                REQUEST_ACT_DEFER,
                REQUEST_ACT_SCIENCE,
                REQUEST_ACT_ANNOTATION,
            ]:
                """
                Verifica se há aprovador/substituto
                """

                approver_email = [
                    {
                        "email": (
                            approver.pessoa_fisica.email_institucional
                            if approver.pessoa_fisica.email_institucional
                            else approver.pessoa_fisica.email_pessoal
                        ),
                        "nome": approver.pessoa_fisica.social_name,
                        "idUsuario": approver.id_usuario_mastiff,
                    },
                ]

                message = "O pedido abaixo necessita da sua manifestação/ciência."
                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=approver_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )
    except Exception as e:
        log.error(e)

    try:
        if not approver and instance_request.portal_request_type in [
            PORTAL_REQUEST_TYPE_PROGRESSION_H,
            PORTAL_REQUEST_TYPE_PROGRESSION_V,
        ]:
            if instance.action in [
                REQUEST_ACT_SOLICITATION,
                REQUEST_ACT_DEFER,
                REQUEST_ACT_EFFECTIVENESS,
                REQUEST_ACT_OPEN_SOLICITANTION,
            ]:
                """
                Verifica se email do aprovador progressões
                """
                message = ""

                if (
                    instance_request.portal_request_type
                    == PORTAL_REQUEST_TYPE_PROGRESSION_H
                ):
                    email_approvers = Item.objects.get(
                        configuration__application="vdf",
                        key="notificao-gerencia-desenvolvimento",
                    ).value
                    approver_email = get_emails_approvers(email_approvers)
                    html_message = EmailTemplate.objects.get(
                        code="NOTIFICACAO_PROGRESSAO_HORIZONTAL"
                    ).contents
                    message = (
                        re.sub(pattern, "", html_message)
                        .replace("%action%", instance.get_action_display())
                        .replace("%status%", instance_request.get_status_display())
                    )
                else:
                    html_message = EmailTemplate.objects.get(
                        code="NOTIFICACAO_PROGRESSAO_VERTICAL"
                    ).contents
                    message = (
                        re.sub(pattern, "", html_message)
                        .replace("%action%", instance.get_action_display())
                        .replace("%status%", instance_request.get_status_display())
                    )
                    if instance_request.status == STS_EFFECTIVE:
                        email_approvers = Item.objects.get(
                            configuration__application="vdf",
                            key="notificao-gerencia-desenvolvimento",
                        ).value
                        approver_email = get_emails_approvers(email_approvers)

                    elif (
                        instance_request.step_current
                        == REQUEST_STEP_JURIDICAL_ADVISORY_1
                    ):
                        email_approvers = Item.objects.get(
                            configuration__application="vdf",
                            key="notificao-assessoria-jur-1",
                        ).value
                        approver_email = get_emails_approvers(email_approvers)

                    elif (
                        instance_request.step_current
                        == REQUEST_STEP_JURIDICAL_ADVISORY_2
                    ):
                        email_approvers = Item.objects.get(
                            configuration__application="vdf",
                            key="notificao-assessoria-jur-2",
                        ).value
                        approver_email = get_emails_approvers(email_approvers)

                    elif instance_request.step_current == REQUEST_STEP_PROG_DG:
                        email_approvers = Item.objects.get(
                            configuration__application="vdf", key="notificacao-prog-dg"
                        ).value
                        approver_email = get_emails_approvers(email_approvers)

                send_mail_pvf(
                    task=task.uuid,
                    hook=None,
                    subject=subject,
                    messages=message,
                    solicitation=request_type,
                    code=str(id_request),
                    date=str(request_date),
                    requester=employee.pessoa_fisica.social_name,
                    observation=instance.observation,
                    receivers=approver_email,
                    receivers_rh_person_ids=None,
                    success="Email enviado com sucesso.",
                    user=instance.portal_request.request,
                )
    except Exception as e:
        log.error(e)

    try:
        if (
            instance_request.portal_request_type
            == PORTAL_SOLICITACAO_DESBLOQUEIO_TELETRABALHO
            and instance.action in [REQUEST_ACT_SOLICITATION, REQUEST_ACT_SEND_SUB]
        ):
            if instance_request.step_current == REQUEST_STEP_GER_DEV:
                email_approvers = Item.objects.get(
                    configuration__application="vdf",
                    key="notificao-gerencia-desenvolvimento",
                ).value
                approver_email = get_emails_approvers(email_approvers)
            elif instance_request.step_current == REQUEST_STEP_SUB_ADM:
                email_approvers = Item.objects.get(
                    configuration__application="vdf", key="notificacao-sub-adm"
                ).value
                approver_email = get_emails_approvers(email_approvers)

            message = "Solicita-se análise do pedido abaixo."
            send_mail_pvf(
                task=task.uuid,
                hook=None,
                subject=subject,
                messages=message,
                solicitation=request_type,
                code=str(id_request),
                date=str(request_date),
                requester=employee.pessoa_fisica.social_name,
                observation=instance.observation,
                receivers=approver_email,
                receivers_rh_person_ids=None,
                success="Email enviado com sucesso.",
                user=instance.portal_request.request,
            )

    except Exception as e:
        log.error(e)


def get_emails_approvers(email_approvers):
    approver_email = []
    emails = email_approvers.split(",")
    for email in emails:
        person = PessoaFisica.objects.filter(email_institucional=email.upper()).first()
        approver_email.append(
            {
                "email": email,
                "nome": person.nome if person else "",
                "idUsuario": (
                    person.servidor_set.last().id_usuario_mastiff if person else None
                ),
            }
        )
    return approver_email
