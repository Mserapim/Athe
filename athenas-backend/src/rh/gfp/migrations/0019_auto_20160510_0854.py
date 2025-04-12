# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0018_auto_20160320_1439"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cargosestrutura",
            name="referencias",
            field=models.ManyToManyField(
                related_name="cargos_estrutura", to="gfp.ReferenciaNiveis2D"
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="config_value",
            field=models.CharField(
                default="",
                max_length=400,
                verbose_name="Cofigura\xc3\xa7\xc3\xa3o - valor",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="description",
            field=models.CharField(
                default="",
                max_length=400,
                verbose_name="Decri\xc3\xa7\xc3\xa3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="incide_sobre",
            field=models.ManyToManyField(
                related_name="aplica_em", verbose_name="Incide sobre", to="gfp.Evento"
            ),
        ),
        migrations.AlterField(
            model_name="extrapaymentperiod",
            name="end_validity",
            field=models.DateField(
                null=True, verbose_name="Fim vig\xeancia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="folha",
            name="ci_por",
            field=models.ForeignKey(
                related_name="folhas_validadas",
                verbose_name="Respons\xe1vel pelo valida\xe7\xe3o",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folha",
            name="fechado_por",
            field=models.ForeignKey(
                related_name="folhas_fechadas",
                verbose_name="Respons\xe1vel pelo fechamento",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folha",
            name="processado_por",
            field=models.ForeignKey(
                related_name="folhas_executadas",
                verbose_name="Respons\xe1vel pela execu\xe7\xe3o",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="acessorios",
            field=models.ManyToManyField(
                related_name="come_acessorio",
                verbose_name="Verbas acess\xf3rio",
                to="gfp.Evento",
            ),
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="para_indicativo",
            field=models.CharField(
                default=None,
                max_length=1,
                null=True,
                verbose_name="Para os",
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
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="servidores",
            field=models.ManyToManyField(related_name="nos_modelos", to="rh.Servidor"),
        ),
        migrations.AlterField(
            model_name="gestorprogressoes",
            name="posse_servidor",
            field=models.OneToOneField(
                related_name="+", to="rh.MovimentacaoPosse", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="perfilprevidencia",
            name="lei_cargo",
            field=models.CharField(
                max_length=10,
                verbose_name="Tipo de Lei",
                choices=[
                    ("EF", "EFETIVO"),
                    ("CM", "COMISS\xc3O"),
                    ("FC", "FUN\xc7\xc3O DE CONFIAN\xc7A"),
                    ("AC", "ACORDO DE COOPERA\xc7\xc3O T\xc9CNICA"),
                    ("ES", "ESTAGI\xc1RIO"),
                    ("EL", "ELETIVO"),
                    ("TE", "TERCEIRIZADO"),
                    ("VL", "VOLUNT\xc1RIO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="cargos",
            field=models.ManyToManyField(
                related_name="referencias_salariais", to="rh.Cargo"
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="estrutura_salarial",
            field=models.ForeignKey(
                related_name="+",
                verbose_name="N\xedvel Salarial",
                blank=True,
                to="gfp.EstruturaTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
