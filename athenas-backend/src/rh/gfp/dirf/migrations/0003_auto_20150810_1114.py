# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0001_initial"),
        ("rh", "0001_initial"),
        ("dirf", "0002_token_eventos"),
    ]

    operations = [
        migrations.AddField(
            model_name="dirfresumos",
            name="pessoa",
            field=models.ForeignKey(
                related_name="diarias_resumo", to="rh.Pessoa", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="dirfresumos",
            unique_together=set([("pessoa", "ano", "mes", "tipo")]),
        ),
        migrations.AddField(
            model_name="dialect",
            name="copy_from",
            field=models.ForeignKey(
                blank=True, to="dirf.Dialect", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dialect",
            name="dirf",
            field=models.ForeignKey(
                related_name="dialect", to="gfp.IRRF", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="declaracao",
            field=models.ForeignKey(
                related_name="demonstrativos",
                to="dirf.Declaracao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="natureza",
            field=models.ForeignKey(
                related_name="demonstrativos",
                to="dirf.NaturezaRendimento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="pessoa_fisica",
            field=models.ForeignKey(
                related_name="dirfs_pessoa_fisica",
                to="rh.PessoaFisica",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="responsavel",
            field=models.ForeignKey(
                related_name="como_responsavel",
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="servidor",
            field=models.ForeignKey(
                related_name="dirfs",
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="demonstrativo",
            name="tipo_folha",
            field=models.ForeignKey(
                related_name="demonstrativos",
                to="gfp.FolhaTipo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
