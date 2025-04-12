# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0016_auto_20160425_1556"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargo",
            name="health",
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="declaracaoatividade",
            name="activity_as",
            field=models.CharField(
                default="I",
                max_length=1,
                blank=True,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servidor",
            name="categoria_cache",
            field=models.CharField(
                default="SERVIDOR_QUADRO",
                max_length=40,
                choices=[
                    (
                        "MEMBRO_1ENT",
                        "Membro - Promotor de Justi\xe7a 1\xaa Entr\xe2ncia",
                    ),
                    (
                        "MEMBRO_3ENT",
                        "Membro - Promotor de Justi\xe7a 3\xaa Entr\xe2ncia",
                    ),
                    ("SERVIDOR_EXTRAQUADRO", "Servidor - Extraquadro"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_AC_ONUS",
                        "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica com \xf4nus",
                    ),
                    ("VOLUNTARIO", "Volunt\xe1rio"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_ONUS",
                        "Servidor - Extraquadro requisitado com \xf4nus",
                    ),
                    (
                        "MEMBRO_2ENT",
                        "Membro - Promotor de Justi\xe7a 2\xaa Entr\xe2ncia",
                    ),
                    ("MEMBRO", "Membro"),
                    ("MEMBRO_PROCURADOR", "Membro - Procurador de Justi\xe7a"),
                    ("MEMBRO_SUBS", "Membro - Promotor de Justi\xe7a Substituto"),
                    ("TERCEIRIZADO", "Terceirizado"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO_AC",
                        "Servidor - Extraquadro - Acordo Coopera\xe7\xe3o T\xe9cnica sem \xf4nus",
                    ),
                    ("SERVIDOR_QUADRO", "Servidor - Quadro"),
                    ("ESTAGIARIO", "Estagi\xe1rio"),
                    (
                        "SERVIDOR_EXTRA_REQUISITADO",
                        "Servidor - Extraquadro requisitado",
                    ),
                ],
            ),
            preserve_default=True,
        ),
    ]
