# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0002_auto_20150810_1114"),
        ("cpl", "0001_initial"),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="publicacaolicitacao",
            name="arquivo",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                blank=True, to="ged.Arquivo", null=True, on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="publicacaolicitacao",
            name="licitacao",
            field=models.ForeignKey(
                verbose_name="Licita\xe7\xe3o",
                to="cpl.Licitacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="produtovencedor",
            name="licitacao",
            field=models.ForeignKey(
                related_name="produtovencedor",
                to="cpl.Licitacao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="produtovencedor",
            name="participante",
            field=models.ForeignKey(
                to="cpl.Participante", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="produtovencedor",
            name="produto_processo",
            field=models.ManyToManyField(
                related_name="vencedor_produto", to="compras.ProdutoProcesso"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="produtovencedor",
            unique_together=set([("participante", "licitacao")]),
        ),
        migrations.AddField(
            model_name="participante",
            name="licitacao",
            field=models.ManyToManyField(
                to="cpl.Licitacao", verbose_name="Licita\xe7\xe3o"
            ),
            preserve_default=True,
        ),
    ]
