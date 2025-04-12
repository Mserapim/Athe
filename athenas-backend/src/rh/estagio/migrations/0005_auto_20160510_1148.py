# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estagio", "0004_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conceito",
            name="descricao",
            field=models.CharField(default="", max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="avaliador_externo",
            field=models.TextField(
                null=True, verbose_name="Avaliador de \xd3rg\xe3o Externo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="cargo_avaliado",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Cargo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="cargo_avaliador",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Cargo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="cargo_externo",
            field=models.TextField(
                null=True,
                verbose_name="Cargo do Avaliador de \xd3rg\xe3o Externo",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="data_avaliacao_externa",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="finalizado_por",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="lotacao_avaliado",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="lotacao_avaliador",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Lotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="lotacao_externo",
            field=models.TextField(
                null=True,
                verbose_name="Lota\xe7\xe3o do Avaliador de \xd3rg\xe3o Externo",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="matricula_externo",
            field=models.TextField(
                null=True,
                verbose_name="Matricula do Avaliador de \xd3rg\xe3o Externo",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="estagioavaliacao",
            name="media_comissao",
            field=models.DecimalField(
                null=True, max_digits=5, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="ciencia_decisao_estagio",
            field=models.DateField(
                null=True,
                verbose_name="Data da Ci\xeancia da Decis\xe3o do est\xe1gio",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="dias_falta",
            field=models.DecimalField(
                default=0, null=True, max_digits=5, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="fim_estagio",
            field=models.DateField(
                null=True, verbose_name="Data Fim Est\xe1gio", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="proxima_avaliacao",
            field=models.DateField(
                null=True, verbose_name="Data Proxima Avaliacao", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="publicacao_homologacao",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="estagioprobatorioservidor",
            name="ultima_avaliacao",
            field=models.DateField(
                null=True, verbose_name="Data Ultima Avaliacao", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="integrantescomissao",
            name="ordem",
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
