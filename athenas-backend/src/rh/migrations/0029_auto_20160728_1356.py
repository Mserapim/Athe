# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0028_pessoafisica_renda_familiar"),
    ]

    operations = [
        migrations.CreateModel(
            name="CourseAreaCNMP",
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
                (
                    "area",
                    models.CharField(max_length=200, verbose_name="\xc1rea do Curso"),
                ),
                ("value", models.SmallIntegerField(default=0)),
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
        migrations.CreateModel(
            name="GraduationCNMP",
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
                ("course", models.CharField(max_length=200, verbose_name="Curso")),
                (
                    "institution",
                    models.CharField(max_length=200, verbose_name="Instituicao"),
                ),
                (
                    "conclusion_year",
                    models.SmallIntegerField(
                        default=0, verbose_name="Ano de conclus\xe3o"
                    ),
                ),
                (
                    "course_area",
                    models.ForeignKey(
                        verbose_name="Area do Curso",
                        to="rh.CourseAreaCNMP",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
        migrations.CreateModel(
            name="ImprovementAndGraduateCNMP",
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
                ("course", models.CharField(max_length=200, verbose_name="Curso")),
                (
                    "institution",
                    models.CharField(max_length=200, verbose_name="Institui\xe7\xe3o"),
                ),
                (
                    "conclusion_year",
                    models.SmallIntegerField(
                        default=0, verbose_name="Ano de conclus\xe3o"
                    ),
                ),
                (
                    "nivel",
                    models.IntegerField(
                        verbose_name="N\xedvel",
                        choices=[
                            (1, "Lato-Sensu"),
                            (2, "Mestrado"),
                            (3, "Doutorado"),
                            (4, "P\xf3s-Doutorado"),
                            (5, "Livre Doc\xeancia"),
                            (6, "Especializa\xe7\xe3o"),
                            (7, "Aperfei\xe7oamento Funcional"),
                        ],
                    ),
                ),
                (
                    "course_area",
                    models.ForeignKey(
                        verbose_name="\xc1rea do Curso",
                        to="rh.CourseAreaCNMP",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
        migrations.CreateModel(
            name="PublishedWorksCNMP",
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
                ("title", models.CharField(max_length=200, verbose_name="T\xedtulo")),
                ("area", models.CharField(max_length=200, verbose_name="\xc1rea")),
                (
                    "institution",
                    models.CharField(max_length=200, verbose_name="Institui\xe7\xe3o"),
                ),
                (
                    "work_type",
                    models.IntegerField(
                        verbose_name="Tipo",
                        choices=[
                            (1, "Artigo"),
                            (2, "Disserta\xe7\xe3o"),
                            (3, "Livro"),
                            (4, "Monografia"),
                            (5, "Peri\xf3dico"),
                            (6, "Relat\xf3rio"),
                            (7, "Registro em Anal"),
                            (8, "Tese"),
                        ],
                    ),
                ),
                ("year", models.SmallIntegerField(default=0, verbose_name="Ano")),
                (
                    "publication_place",
                    models.CharField(
                        max_length=50,
                        verbose_name="Meio de Publica\xe7\xe3o",
                        choices=[
                            ("IMPRESSO", "IMPRESSO"),
                            ("INTERNET", "INTERNET"),
                            ("MAGNETICO", "MAGNETICO"),
                        ],
                    ),
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
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo Documento",
                choices=[
                    (1, "ATO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (12, "APOSTILA"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Inst\xe2ncia",
                choices=[(1, "PRIMEIRA INST\xc2NCIA"), (2, "SEGUNDA INST\xc2NCIA")],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Entr\xe2ncia",
                choices=[
                    (1, "PRIMEIRA ENTR\xc2NCIA"),
                    (2, "SEGUNDA ENTR\xc2NCIA"),
                    (3, "TERCEIRA ENTR\xc2NCIA"),
                    (4, "PROCURADORIA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="poder",
            field=models.IntegerField(
                default=5,
                choices=[
                    (1, "EXECUTIVO"),
                    (2, "LEGISLATIVO"),
                    (3, "JUDICI\xc1RIO"),
                    (4, "MINIST\xc9RIO P\xdaBLICO"),
                    (5, "DESCONHECIDO"),
                    (6, "TRIBUNAL DE CONTAS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="turno",
            field=models.IntegerField(
                default=4,
                choices=[
                    (1, "Matutino"),
                    (2, "Vespertino"),
                    (3, "Noturno"),
                    (4, "Dia inteiro"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="serious_diseases",
            field=models.ManyToManyField(
                related_name="in_pessoafisica",
                verbose_name="Doen\xe7as Graves",
                to="rh.SeriousDiseases",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="social_program",
            field=models.ManyToManyField(
                related_name="in_pesssoafisica",
                verbose_name="Programas Sociais",
                to="rh.SocialProgram",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="publication_state",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Em Aberto"),
                    (2, "P\xfablica\xe7\xe3o Solicitada"),
                    (3, "P\xfablica\xe7\xe3o Realizada"),
                    (4, "P\xfablica\xe7\xe3o Cancelada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(
                verbose_name="Tipo de Publica\xe7\xe3o",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="veiculo_publicacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Ve\xedculo Publica\xe7\xe3o",
                choices=[
                    (1, "DOE ACRE"),
                    (2, "DOE AMAPA"),
                    (3, "DOE AMAZONAS"),
                    (4, "DOE RORAIMA"),
                    (5, "DOE RONDONIA"),
                    (6, "DOE PARA"),
                    (7, "DOE TOCANTINS"),
                    (8, "DOE CEARA"),
                    (9, "DOE RIO GRANDE DO NORTE"),
                    (10, "DOE PERNAMBUCO"),
                    (11, "DOE PARAIBA"),
                    (12, "DOE SERGIPE"),
                    (13, "DOE BAHIA"),
                    (14, "DOE MARANHAO"),
                    (15, "DOE PIAUI"),
                    (16, "DOE MINAS GERAIS"),
                    (17, "DOE SAO PAULO"),
                    (18, "DOE ESPIRITO SANTO"),
                    (19, "DOE RIO DE JANEIRO"),
                    (21, "DOE PARANA"),
                    (22, "DOE SANTA CATARINA"),
                    (23, "DOE RIO GRANDE DO SUL"),
                    (24, "DOE MATO GROSSO DO SUL"),
                    (25, "DOE GOIAS"),
                    (26, "DOE DISTRITO FEDERAL"),
                    (27, "DOE MATO GROSSO"),
                    (28, "DIARIO JUSTICA"),
                    (29, "DIARIO JUSTICA ELEITORAL"),
                    (30, "DIARIO OFICIAL DA UNIAO"),
                    (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                    (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                    (33, "PLACAR"),
                    (34, "DI\xc1RIO ELETR\xd4NICO DO MPE"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="graduation",
            field=models.ManyToManyField(
                related_name="employee",
                verbose_name="Gradua\xe7\xe3o",
                to="rh.GraduationCNMP",
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="improvement_and_graduate",
            field=models.ManyToManyField(
                related_name="employee",
                verbose_name="Aperfei\xe7oamento e P\xf3s-gradua\xe7\xe3o",
                to="rh.ImprovementAndGraduateCNMP",
            ),
        ),
        migrations.AddField(
            model_name="servidor",
            name="published_works",
            field=models.ManyToManyField(
                related_name="employee",
                verbose_name="Trabalhos publicados",
                to="rh.PublishedWorksCNMP",
            ),
        ),
    ]
