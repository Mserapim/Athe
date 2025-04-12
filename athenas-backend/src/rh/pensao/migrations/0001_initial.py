# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pensao",
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
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data do in\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data do fim", blank=True),
                ),
                (
                    "dedutivel_irrf",
                    models.BooleanField(default=True, verbose_name="Dedut\xedvel IRRF"),
                ),
                (
                    "tipo",
                    models.SmallIntegerField(
                        verbose_name="Tipo do Valor",
                        choices=[
                            (1, "VALOR FIXO"),
                            (2, "PERCENTUAL"),
                            (3, "SAL\xc1RIO M\xcdNIMO"),
                        ],
                    ),
                ),
                (
                    "valor",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor",
                        max_digits=16,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "degree_kinship",
                    models.IntegerField(
                        default=10,
                        verbose_name="Grau de parentesco",
                        choices=[
                            (1, "C\xd4NJUGE"),
                            (2, "COMPANHEIRO"),
                            (3, "FILHO(A)"),
                            (4, "PAI/M\xc3E"),
                            (5, "IRM\xc3O"),
                            (6, "ENTEADO"),
                            (7, "MENOR TUTELADO"),
                            (8, "EX-C\xd4NJUGE"),
                            (9, "NETOS"),
                            (10, "OUTROS"),
                        ],
                    ),
                ),
            ],
            options={
                "ordering": [
                    "servidor__pessoa_fisica__nome",
                    "pensionista__nome",
                    "-data_inicio",
                ],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PensaoAlimenticia",
            fields=[
                (
                    "pensao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pensao.Pensao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("pensao.pensao",),
        ),
        migrations.CreateModel(
            name="PensaoEvento",
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
                (
                    "tipo",
                    models.SmallIntegerField(
                        verbose_name="Tipo do Valor",
                        choices=[
                            (1, "VALOR FIXO"),
                            (2, "PERCENTUAL"),
                            (3, "SAL\xc1RIO M\xcdNIMO"),
                        ],
                    ),
                ),
                (
                    "valor",
                    models.DecimalField(
                        default=0,
                        verbose_name="Valor",
                        max_digits=16,
                        decimal_places=6,
                        blank=True,
                    ),
                ),
                (
                    "calculo_oculto",
                    models.BooleanField(default=False, verbose_name="Calculo oculto"),
                ),
                (
                    "evento_principal",
                    models.BooleanField(default=False, verbose_name="Principal"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PensaoAlimenticiaEvento",
            fields=[
                (
                    "pensaoevento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pensao.PensaoEvento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pensao_alimenticia",
                    models.ForeignKey(
                        related_name="eventos",
                        to="pensao.PensaoAlimenticia",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("pensao.pensaoevento",),
        ),
        migrations.CreateModel(
            name="PensaoFolhaEvento",
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
                (
                    "valor",
                    models.DecimalField(default=0, max_digits=16, decimal_places=2),
                ),
                (
                    "valor_base",
                    models.DecimalField(null=True, max_digits=16, decimal_places=2),
                ),
                (
                    "pct",
                    models.DecimalField(null=True, max_digits=16, decimal_places=2),
                ),
                (
                    "contracheque",
                    models.ForeignKey(
                        related_name="lancamentos_pensionitas",
                        blank=True,
                        to="gfp.ContraChequePensionista",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "evento",
                    models.ForeignKey(
                        related_name="em_pensoes",
                        to="gfp.Evento",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "folha",
                    models.ForeignKey(
                        related_name="pensoes",
                        to="gfp.Folha",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "folha_evento",
                    models.ForeignKey(
                        related_name="origem_pensao",
                        to="gfp.FolhaEvento",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PensaoMorte",
            fields=[
                (
                    "pensao_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pensao.Pensao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("pensao.pensao",),
        ),
        migrations.CreateModel(
            name="PensaoMorteEvento",
            fields=[
                (
                    "pensaoevento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="pensao.PensaoEvento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pensao_morte",
                    models.ForeignKey(
                        related_name="eventos",
                        to="pensao.PensaoMorte",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("pensao.pensaoevento",),
        ),
        migrations.AddField(
            model_name="pensaomorte",
            name="evento",
            field=models.ManyToManyField(
                related_name="pensaomorte_eventos",
                through="pensao.PensaoMorteEvento",
                to="gfp.Evento",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensaofolhaevento",
            name="pensao",
            field=models.ForeignKey(
                related_name="lancamentos", to="pensao.Pensao", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="pensaofolhaevento",
            unique_together=set([("pensao", "folha", "evento")]),
        ),
        migrations.AddField(
            model_name="pensaoevento",
            name="evento",
            field=models.ForeignKey(
                related_name="pensaoalimenticiaevento_evento",
                to="gfp.Evento",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensaoevento",
            name="tipo_folhas",
            field=models.ManyToManyField(
                related_name="eventos_pensao", to="gfp.FolhaTipo"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensaoalimenticia",
            name="evento",
            field=models.ManyToManyField(
                related_name="pensaoalimenticia_eventos",
                through="pensao.PensaoAlimenticiaEvento",
                to="gfp.Evento",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pensaoalimenticia",
            name="evento_pensao",
            field=models.ForeignKey(
                related_name="eventos_origem_pensao",
                verbose_name="Evento",
                to="gfp.Evento",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
