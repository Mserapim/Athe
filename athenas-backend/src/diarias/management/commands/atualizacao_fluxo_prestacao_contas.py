from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from datetime import datetime, timedelta
from diarias.models import Beneficiario, Pagamento
from django.db import transaction
from diarias.utils.fluxo_movimentacao import benef_mover_etapa
from diarias.const import FLUXO_PAGO, FLUXO_AGUARDADO_PRESTACAO_CONTAS

log = getLogger(__name__)


class Command(BaseCommand):
    help = """
        Esse Comando irá atualizar os pagamentos com status 'cnab_criado' 
        para 'pago' e avança para o proximo fluxo.
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
        self.set_user_to_job("job_diarias_atualizacao_fluxo_prestacao_contas")
        self.atualizar_beneficiarios()

    def buscar_beneficiarios(self):
        data_atual = datetime.now().date()
        beneficiarios = Beneficiario.objects.filter(
            fluxo__id=FLUXO_PAGO, viagem__data_fim_viagem=data_atual
        )

        return beneficiarios

    def atualizar_beneficiarios(self):

        beneficiarios = self.buscar_beneficiarios()

        for beneficiario in beneficiarios:
            try:

                log.info(
                    f"movendo o fluxo do beneficiario para o fluxo aguardando prestação de contas: {beneficiario}"
                )
                print(
                    f"movendo o fluxo do beneficiario para o fluxo aguardando prestação de contas: {beneficiario}"
                )

                benef_mover_etapa(beneficiario, FLUXO_AGUARDADO_PRESTACAO_CONTAS)

            except Exception as e:
                print(f"{e}")
                log.error(f"{e}")
