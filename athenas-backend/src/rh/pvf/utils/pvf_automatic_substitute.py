import datetime
from common.util.send_email import EmailNotification
from contrib.middleware import set_current_user

from rh.pvf.models import PortalRequestSubstitute, PortalRequest, PortalRequestHistory
from rh.models import Servidor
from rh.pvf.const import REQUEST_ACT_SCIENCE, STS_WAI_SUBS_SCIENCE
from standard.models import Choice
from contrib.utils import getLogger

log = getLogger("db")


def _return_deadline_for_substituition_acknowledgment():
    """
    Função para retornar a data máxima para que um mebro dê ciência à uma substituição.
    :returns (int): Valor maximo para ciência, em dias.
    """

    try:
        if Choice.objects.get(name="PVF_AUTOMATIC_ACKNOWLEDGMENT_DAYS"):
            return Choice.objects.get(name="PVF_AUTOMATIC_ACKNOWLEDGMENT_DAYS").value
    except Exception as err:
        log.error(f"Não foi possível localizar o limite de dias para ciência{err}")
        choice = Choice(
            app_label="PVF",
            name="PVF_AUTOMATIC_ACKNOWLEDGMENT_DAYS",
            label="Prazo em dias para dar ciência automática por substituto",
            description="Prazo em dias para o substituto dar cinência a um afastamento/usufruto, antes que seja feita a ciência automática pelo sistema",
            value=5,
        ).save()
        return choice.value


def email_substitute(request, substitute_fisical_person, deadline_date):
    subject = "Portal Vida Funcional - Protocolo ID: {}".format(request.id)
    message = "Ocorreu a ciência automática da substituição do pedido abaixo, em virtude do decurso de prazo de {} dias sem manifestação do substituto.".format(
        deadline_date
    )
    type_of_request = request.type_of_request
    code = request.id
    date_request = request.date.strftime("%d/%m/%Y")
    requester = request.employee.pessoa_fisica.social_name
    receivers_rh_person_ids = [
        {
            "email": (
                substitute_fisical_person.email_institucional
                if substitute_fisical_person.email_institucional
                else substitute_fisical_person.email
            ),
            "nome": substitute_fisical_person.social_name,
            "idUsuario": substitute_fisical_person.servidor_set.last().id_usuario_mastiff,
        },
        {
            "email": (
                request.employee.pessoa_fisica.email_institucional
                if request.employee.pessoa_fisica.email_institucional
                else request.approver.pessoa_fisica.email
            ),
            "nome": request.employee.pessoa_fisica.social_name,
            "idUsuario": request.employee.id_usuario_mastiff,
        },
    ]
    EmailNotification().send_email_pvf(
        subject=subject,
        message=message,
        solicitation=type_of_request,
        code=str(code),
        date=str(date_request),
        requester=requester,
        receivers=receivers_rh_person_ids,
        receivers_rh_person_ids=None,
    )


def automatic_substitute_acknowledgment():
    """
    Função para dar ciência automática para os substitutos depois do prazo estabelecido através de PVF_AUTOMATIC_ACKNOWLEDGMENT_DAYS.
    """
    log.info("Iniciando verificação do prazo para ciência dos substitutos")
    pvf_requests = PortalRequest.objects.filter(status=STS_WAI_SUBS_SCIENCE)
    for request in pvf_requests:
        log.info(
            f"Verificando prazo para ciência do substituto da solicitação: {request}"
        )
        try:
            substitute_history = PortalRequestHistory.objects.filter(
                portal_request=request, action=REQUEST_ACT_SCIENCE
            ).last()
            deadline_date = _return_deadline_for_substituition_acknowledgment()
            if substitute_history is None:
                last_movimentation_substitute = request.date
            else:
                last_movimentation_substitute = substitute_history.date.date()
            if last_movimentation_substitute + datetime.timedelta(
                days=deadline_date
            ) <= datetime.date.today() - datetime.timedelta(days=1):
                if request.have_substitute:
                    if request.status == STS_WAI_SUBS_SCIENCE:
                        substitutes = (
                            PortalRequestSubstitute.objects.filter(
                                portal_request=request
                            )
                            .exclude(
                                substitute__user__in=PortalRequestHistory.objects.filter(
                                    portal_request=request, action=REQUEST_ACT_SCIENCE
                                ).values_list(
                                    "user", flat=True
                                )
                            )
                            .distinct()
                        )

                        for ps in substitutes:
                            substitute = ps.substitute
                            substitute_user = substitute.user
                            substitute_fisical_person = substitute.pessoa_fisica
                            set_current_user(substitute_user)
                            log.info(
                                f"Ciência automática pelo decurso do prazo de {deadline_date} dias, do substituto: {substitute_fisical_person.nome}"
                            )
                            request.science(
                                observation=f"Ciência automática pelo decurso do prazo de {deadline_date} dias",
                                user=substitute_user,
                            )
                            email_substitute(
                                request=request,
                                substitute_fisical_person=substitute_fisical_person,
                                deadline_date=deadline_date,
                            )

        except Exception as err:
            log.error(err.with_traceback())
            import traceback

            log.info(f"Erro ao processar substituição automática: {err}")
            log.info(traceback.format_exc())
