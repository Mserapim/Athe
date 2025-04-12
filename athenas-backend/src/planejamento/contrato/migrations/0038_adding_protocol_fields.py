from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0037_auto_20210903_1331"),
    ]

    operations = [
        migrations.AddField(
            model_name="agreementannotation",
            name="protocol",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="annotation",
                to="protocolo.Protocolo",
                verbose_name="Protocolo de notificação",
            ),
        ),
        migrations.AddField(
            model_name="agreementannotation",
            name="protocol_movement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="annotation",
                to="protocolo.Movimentacao",
            ),
        ),
    ]
