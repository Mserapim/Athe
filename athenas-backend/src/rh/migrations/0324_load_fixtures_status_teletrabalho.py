from django.conf import settings
from django.db import migrations, models
from django.core.management import call_command
import os

FIXTURES = ("fixtures/status_teletrabalho_choices.json",)


def forward(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running forward...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "rh", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0323_auto_20241122_1411"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
        migrations.RunSQL(
            sql="""
                COMMENT ON COLUMN rh_movimentacaoteletrabalho.situacao IS
                'Status Teletrabalho:
                 1 - Regular
                 2 - Desbloqueado
                 3 - Bloqueado
                 4 - Revogado
                 5 - Ignorado
                 6 - Concluído
                 7 - Pendente';
            """,
            reverse_sql="COMMENT ON COLUMN rh_movimentacaoteletrabalho.situacao IS NULL;",
        ),
    ]
