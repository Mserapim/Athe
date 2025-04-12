# -*- coding: utf-8 -*-


from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("esocial", "0003_auto_20180918_1300"),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("horario_dia", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "horario_cod_hor_contrat",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RemoveField(
            model_name="configuration",
            name="certificate",
        ),
        migrations.RemoveField(
            model_name="configuration",
            name="certificate_ca",
        ),
        migrations.RemoveField(
            model_name="configuration",
            name="certificate_passwd",
        ),
        migrations.RemoveField(
            model_name="s2200",
            name="horario_cod_hor_contrat",
        ),
        migrations.RemoveField(
            model_name="s2200",
            name="horario_dia",
        ),
        migrations.AddField(
            model_name="configuration",
            name="xml_consult_schema_name",
            field=models.CharField(
                max_length=50,
                null=True,
                verbose_name="Nome do Schema de Consulta",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="configuration",
            name="xml_send_schema_name",
            field=models.CharField(
                max_length=50,
                null=True,
                verbose_name="Nome do Schema de Envio",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="configuration",
            name="xmlns_send",
            field=models.CharField(
                default="", max_length=200, verbose_name="Url de Envio", blank=True
            ),
        ),
        migrations.AddField(
            model_name="configuration",
            name="xmlns_consult",
            field=models.CharField(
                default="", max_length=200, verbose_name="Url de Consulta", blank=True
            ),
        ),
        migrations.AddField(
            model_name="s2200",
            name="horario",
            field=models.ManyToManyField(to="esocial.Schedule", blank=True),
        ),
    ]
