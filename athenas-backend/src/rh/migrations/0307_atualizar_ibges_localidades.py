from django.db import migrations

from rh.models import Localidade


def forward(*args, **kwargs):
    Localidade.objects.filter(pk=12372).update(ibge="5201603")  # GO - Araçu
    Localidade.objects.filter(pk=12382).update(ibge="5208707")  # GO - Goiania
    Localidade.objects.filter(pk=12371).update(ibge="2108900")  # MA - Poção de Pedras
    Localidade.objects.filter(pk=12373).update(ibge="5105606")  # MT - Matupá
    Localidade.objects.filter(pk=12514).update(
        ibge="5106315"
    )  # MT - Novo Santo Antônio
    Localidade.objects.filter(pk=12490).update(ibge="5107008")  # MT - Poxoréu
    Localidade.objects.filter(pk=12386).update(
        ibge="5107305"
    )  # MT - São José do Rio Claro
    Localidade.objects.filter(pk=12387).update(
        ibge="5107107"
    )  # MT - São José dos Quatro Marcos
    Localidade.objects.filter(pk=12384).update(
        ibge="5107107"
    )  # MT - São José dos Quatro Marcos
    Localidade.objects.filter(pk=12378).update(ibge="1503606")  # PA - Itaituba
    Localidade.objects.filter(pk=12369).update(
        ibge="4318101"
    )  # RS - São Francisco de Assis
    Localidade.objects.filter(pk=12365).update(ibge="4205407")  # SC - Florianópolis
    Localidade.objects.filter(pk=12375).update(ibge="4216008")  # SC - São Carlos
    Localidade.objects.filter(pk=12364).update(ibge="3529005")  # SP - Marília
    Localidade.objects.filter(pk=12377).update(
        ibge="3548708"
    )  # SP - São Bernardo do Campo
    Localidade.objects.filter(pk=12221).update(ibge="1722081")  # TO - Wanderlândia


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0306_auto_20240628_1248"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
