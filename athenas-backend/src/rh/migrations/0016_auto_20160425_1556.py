# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0015_auto_20160218_1016"),
    ]

    operations = [
        migrations.CreateModel(
            name="SeriousDiseases",
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
                ("name", models.CharField(max_length=200, verbose_name="Nome")),
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
                "ordering": ("name",),
                "permissions": (("serious_diseases", "Administrar Doen\xe7as Graves"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SocialProgram",
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
                ("name", models.CharField(max_length=200, verbose_name="Nome")),
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
                "ordering": ("name",),
                "permissions": (("social_program", "Administrar Programa Social"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="orgaogeral",
            options={
                "ordering": ["nome"],
                "verbose_name": "\xd3rg\xe3o Geral",
                "permissions": (
                    ("can_manage_general_organ", "Pode Gerenciar \xd3rg\xe3o Geral"),
                ),
            },
        ),
        migrations.AlterModelOptions(
            name="pessoafisica",
            options={
                "ordering": ("nome", "cpf"),
                "verbose_name": "Pessoa F\xedsica",
                "permissions": (
                    (
                        "can_manage_person_employee",
                        "Permiss\xe3o para gerenciar Servidor",
                    ),
                ),
            },
        ),
        migrations.AlterModelOptions(
            name="pessoajuridica",
            options={
                "ordering": ("nome", "cnpj"),
                "verbose_name": "Pessoa Jur\xeddica",
                "permissions": (
                    (
                        "can_manage_legal_person",
                        "Permiss\xe3o para gerenciar Pessoa Jur\xeddica",
                    ),
                ),
            },
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="has_serious_diseases",
            field=models.BooleanField(default=False, verbose_name="Doen\xe7a Grave"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="renda_familiar",
            field=models.CharField(
                max_length=10, null=True, verbose_name="Renda Familiar", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="serious_diseases",
            field=models.ManyToManyField(
                related_name="in_pessoafisica",
                verbose_name="Doen\xe7as Graves",
                to="rh.SeriousDiseases",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="social_program",
            field=models.ManyToManyField(
                related_name="in_pesssoafisica",
                verbose_name="Programas Sociais",
                to="rh.SocialProgram",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="cargo",
            name="indicativo",
            field=models.CharField(
                default="S",
                max_length=1,
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
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Inst\xe2ncia",
                choices=[(1, "PRIMEIRA INST\xc2NCIA"), (2, "SEGUNDA INST\xc2NCIA")],
            ),
            preserve_default=True,
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
            preserve_default=True,
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
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="cargo",
            name="tipo_lei_cargo",
            field=models.CharField(
                default="EF",
                max_length=2,
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
            preserve_default=True,
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
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="raca_cor",
            field=models.IntegerField(
                default=5,
                verbose_name="Ra\xe7a/Cor",
                choices=[
                    (6, "BRANCA"),
                    (1, "PARDA"),
                    (2, "AMARELA"),
                    (3, "NEGRA"),
                    (4, "IND\xcdGENA"),
                    (5, "N\xc3O INFORMADO"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="pessoajuridica",
            name="cnpj",
            field=models.CharField(max_length=14, null=True, blank=True),
            preserve_default=True,
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
            preserve_default=True,
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
            preserve_default=True,
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
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servidor",
            name="tipo",
            field=models.CharField(
                default="S",
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
            model_name="tiposervidor",
            name="indicativo",
            field=models.CharField(
                max_length=1,
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
    ]
