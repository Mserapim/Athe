# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0059_auto_20171226_1707'),
        ("esocial", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationqualification",
            name="employee",
            field=models.ForeignKey(
                related_name="qualifications",
                verbose_name="Servidor",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="registrationqualification",
            name="type_of_person",
            field=models.PositiveSmallIntegerField(
                default=1,
                choices=[
                    (1, "SERVIDOR ATIVO"),
                    (2, "SERVIDOR INATIVO"),
                    (3, "DEPENDENTE"),
                    (4, "PENSIONISTA"),
                    (5, "ESTAGI\xc1RIO"),
                    (6, "ALIMENTANDO"),
                    (7, "DESCONHECIDO"),
                ],
            ),
        ),
    ]
