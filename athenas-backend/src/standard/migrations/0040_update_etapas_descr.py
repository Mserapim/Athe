from django.db import migrations

from standard.models import Choice


def forward(*args, **kwargs):
    print("Running forward...")

    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=16).update(
        description="ASS_SUB_JUR"
    )
    Choice.objects.filter(name="ETAPA_SOLICITACAO_VIAGEM", value=8).update(
        description="ASS_SUB_ADM"
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0039_load_fixture_template_email_criacao_novo_usuario"),
    ]

    operations = [migrations.RunPython(forward, backward)]
