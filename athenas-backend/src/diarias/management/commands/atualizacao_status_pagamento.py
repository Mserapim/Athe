from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from datetime import datetime, timedelta
from diarias.models import Beneficiario, Pagamento
from django.db import transaction
from diarias.utils.fluxo_movimentacao import benef_mover_etapa


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
        self.set_user_to_job("job_diarias_atualizacao_status_pagamento")
        self.atualizar_pagamentos()

    def buscar_pagamentos(self):
        data_atual = datetime.now().date()
        pagamentos = Pagamento.objects.filter(
            status="cnab_criado", data_pgto__lte=data_atual
        )

        return pagamentos

    def atualizar_pagamentos(self):

        log.info(f"iniciando o job atualizacao_status_pagamento")

        pagamentos = self.buscar_pagamentos()

        for pagamento in pagamentos:
            try:
                log.info(f"atualizando os status do pagamento: {pagamento}")
                print(f"atualizando os status do pagamento: {pagamento}")

                pagamento.status = "pago"
                pagamento.save()
                benef_mover_etapa(pagamento.beneficiario)

            except Exception as e:
                print(f"{e}")
                log.error(f"{e}")
