from django.db import migrations

from diarias.models import CondicionalFluxoViagem, FluxoViagem


def forward(apps, schema_editor):
    fluxo_daa = 8
    fluxo = FluxoViagem.objects.filter(id=fluxo_daa).first()
    print(fluxo)
    if fluxo:
        # Excluir todas as condicionais associadas ao fluxo
        condicionais = CondicionalFluxoViagem.objects.filter(fluxo=fluxo).all()
        condicionais.delete()

        print("Condicional para fluxo DAA atualizada com sucesso.")


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0089_auto_20241122_1146"),
    ]

    operations = [migrations.RunPython(forward, backward)]
