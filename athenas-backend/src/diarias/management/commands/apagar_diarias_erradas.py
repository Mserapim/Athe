from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from diarias.models import Viagem, CalculoConsolidado, DadosBancariosImportacao
from diarias.utils.fluxo_movimentacao import benef_mover_etapa

from standard.models import Item

log = getLogger(__name__)


class Command(BaseCommand):
    help = """

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
        self.set_user_to_job("job_athenas_diarias")
        self.apagar_diarias()

    def buscar_diarias(self):
        item_config = Item.objects.get(key="LISTA_DIARIAS_APAGAR")

        lista_ids = item_config.value.split(";") if item_config.value else []

        diarias = Viagem.objects.filter(id__in=lista_ids)

        return diarias

    def apagar_diarias(self):

        log.info(f"iniciando o job atualizacao_status_pagamento")

        diarias = self.buscar_diarias()

        for diaria in diarias:
            try:
                log.info(f"Apagando a diaria: {diaria}")
                print(f"Apagando a diaria: {diaria}")

                beneficiarios = diaria.beneficiarios.all()

                for beneficiario in beneficiarios:
                    beneficiario.pagamentos.all().delete()
                    beneficiario.eventos.all().delete()
                    beneficiario.destinos.all().delete()

                    for prestacao in beneficiario.prestacoes_contas.all():
                        prestacao.anexos.all().delete()
                        prestacao.delete()

                    for historico in beneficiario.historico_fluxos.all():
                        historico.anexos.all().delete()
                        historico.delete()

                    CalculoConsolidado.objects.filter(
                        beneficiario=beneficiario
                    ).delete()

                    DadosBancariosImportacao.objects.filter(
                        beneficiario=beneficiario
                    ).delete()

                    beneficiario.delete(validate=False)

                for historico in diaria.historico_fluxos.all():
                    historico.anexos.all().delete()
                    historico.delete()

                diaria.anexos_viagem.all().delete()
                diaria.delete()

            except Exception as e:
                print(f"{e}")
                log.error(f"{e}")
