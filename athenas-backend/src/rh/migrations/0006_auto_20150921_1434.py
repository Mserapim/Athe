# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0005_pessoa_enable_protocol"),
    ]

    operations = [
        migrations.AddField(
            model_name="servidorlotacao",
            name="from_substitution",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="full_exercise",
            field=models.BooleanField(default=False, verbose_name="Exerc\xedcio pleno"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="situation",
            field=models.IntegerField(
                default=2,
                blank=True,
                choices=[(2, "ATIVO"), (3, "ENCERRADO"), (5, "AFASTADO")],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="enable_protocol",
            field=models.BooleanField(default=True, verbose_name="Habilitar protocolo"),
            preserve_default=True,
        ),
    ]
