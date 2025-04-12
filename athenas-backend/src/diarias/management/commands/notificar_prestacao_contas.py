from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from datetime import date, timedelta
from diarias.models import Beneficiario
from diarias.utils.notificacao_prestacao_contas import (
    envio_email_prestacao_contas_aviso,
    envio_email_prestacao_contas_colaboradores_externos,
)


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Esse Comando irá disparar emails para os benficiarios que possuem prestaçãop de contas para serem enviadas
      utilizando o modelo de emails.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_notificar_prestacao_contas_colaborador_externo")
        self.enviar_email_notificacao_prestacao_contas()

    def busca_beneficiarios(self):

        data_limite = date.today() - timedelta(5)

        FLUXO = 17  # Aguardando Prestação de Contas/DEFIN- Gerencia de Tomada de conta

        return Beneficiario.objects.filter(
            historico_fluxos__fluxo__id=FLUXO,
            prestacoes_contas__status="aguardando",
            viagem__data_fim_viagem__gte=data_limite,
        ).exclude(servidor__type_by_possession__in=["COE", "TCR"])

    def enviar_email_notificacao_prestacao_contas(self):

        beneficiarios = self.busca_beneficiarios()

        for beneficiario in beneficiarios:

            try:
                print(
                    f"Envio do email de notificação sobre a prestação de contas, para: {beneficiario} "
                )

                prestacao = beneficiario.prestacoes_contas.filter(
                    status="aguardando"
                ).first()
                envio_email_prestacao_contas_aviso(prestacao)

            except Exception as error:
                log.info(error)
                print(error)
