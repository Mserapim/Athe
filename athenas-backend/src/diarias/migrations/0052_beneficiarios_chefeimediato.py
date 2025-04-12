from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("diarias", "0051_load_fixtures_template_email_prestacao_contas"),
    ]

    operations = [
        migrations.AddField(
            model_name="beneficiario",
            name="chefe_imediato",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="chefe_imediato_diarias",
                to="rh.Servidor",
                null=True,
                blank=True,
                verbose_name="Chefe Imediato",
            ),
        ),
    ]
