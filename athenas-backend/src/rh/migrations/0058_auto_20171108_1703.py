# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import migrations, models
from django.conf import settings


def up(apps, schema_editor):
    pass


def down(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0057_auto_20171108_1703"),
    ]

    operations = [
        migrations.AddField(
            model_name="lotacao",
            name="replacements",
            field=models.ManyToManyField(
                related_name="_lotacao_replacements_+",
                through="rh.Replacement",
                to="rh.Lotacao",
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="app",
            field=models.IntegerField(
                default=1, verbose_name="Aplicativo", choices=[(1, "diarias")]
            ),
        ),
    ]
