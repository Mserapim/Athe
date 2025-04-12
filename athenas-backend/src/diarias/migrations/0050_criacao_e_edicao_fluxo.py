from django.db import migrations


def forward(apps, schema_editor):
    FluxoViagem = apps.get_model("diarias", "FluxoViagem")
    CondicionalFluxoViagem = apps.get_model("diarias", "CondicionalFluxoViagem")
    User = apps.get_model("auth", "User")

    # Adicionando 1 à ordem de todos os fluxos exceto para o fluxo "Rascunho/Solicitante" (id=2)
    fluxos_para_atualizar = FluxoViagem.objects.filter(id__gt=2)
    for fluxo in fluxos_para_atualizar:
        fluxo.ordem += 1
        fluxo.save()

    user = User.objects.filter(is_superuser=True).first()

    # Criando novo fluxo "Chefe imediato/Aguardando ciência" com condicional "Beneficiário seja servidor"
    fluxo_novo = FluxoViagem.objects.create(
        ordem=2,
        situacao=17,
        etapa=14,
        notificar_solicitante=False,
        notificar_emails=None,
        calcular=False,
        deferir_todos_beneficiarios=False,
        created_by=user,
        modified_by=user,
    )

    CondicionalFluxoViagem.objects.create(
        fluxo=fluxo_novo, condicionais=[6], created_by=user, modified_by=user
    )


def backward(apps, schema_editor):
    FluxoViagem = apps.get_model("diarias", "FluxoViagem")
    CondicionalFluxoViagem = apps.get_model("diarias", "CondicionalFluxoViagem")

    # Revertendo criação de fluxo
    fluxo_novo = FluxoViagem.objects.filter(ordem=2, situacao=17, etapa=14).first()
    if fluxo_novo:
        CondicionalFluxoViagem.objects.filter(fluxo=fluxo_novo).delete()
        fluxo_novo.delete()

    # Revertendo update em campo "ordem"
    fluxos_para_reverter = FluxoViagem.objects.filter(id__gt=2, id__lte=20)
    for fluxo in fluxos_para_reverter:
        fluxo.ordem -= 1
        fluxo.save()


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0049_load_fixtures_fluxo_viagem"),
    ]

    operations = [migrations.RunPython(forward, backward)]
