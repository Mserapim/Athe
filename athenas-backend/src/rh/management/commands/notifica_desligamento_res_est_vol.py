from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from rh.models import Servidor
from rh.utils import enviar_email_notificacao_desligamento_res_vol_est


from datetime import date, timedelta


log = getLogger(__name__)


class Command(BaseCommand):
    help = """Esse Comando irá disparar emails para os aprovadores de teletrabalho informando sobre
    o período de envio do relatório de teletrabalho semestral utilizando o modelo de emails.
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
        self.set_user_to_job("job_notifica_desligamento_res_est_vol")
        self.enviar_email_notificacao_desligamento()

    def busca_servidores_desligados(self):

        dia_anterior = date.today() - timedelta(1)

        return Servidor.objects.filter(
            type_by_possession__in=["EST", "VOL", "RES"],
            ativo=False,
            termination_date=dia_anterior,
        )

    def enviar_email_notificacao_desligamento(self):
        try:
            servidores = self.busca_servidores_desligados()

            for servidor in servidores:
                enviar_email_notificacao_desligamento_res_vol_est(servidor)

        except Exception as error:
            log.info(error)
            print(error)
            raise Exception(error)
