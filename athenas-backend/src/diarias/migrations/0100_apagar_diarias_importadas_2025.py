from django.db import migrations
from django.conf import settings
from django.core.management import call_command
import os
from contrib.utils import getLogger


from diarias.models import Viagem, CalculoConsolidado, DadosBancariosImportacao


log = getLogger(__name__)


def forward(*args, **kwargs):
    print("Running forward...")

    log.info(f"iniciando script para apagar diarias importadas do ano 2025")

    diarias = Viagem.objects.filter(importada=True, data_inicio_viagem__year=2025)

    for diaria in diarias:
        try:
            log.info(f"Apagando a diaria: {diaria}")

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

                CalculoConsolidado.objects.filter(beneficiario=beneficiario).delete()

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


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0099_load_fixtures_email_fluxo_cancelamento_diarias_dg"),
    ]

    operations = [migrations.RunPython(forward, backward)]
