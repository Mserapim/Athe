# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0066_auto_20180830_1454"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigCareer",
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
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=10, verbose_name="C\xf3digo")),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(
                        null=True, verbose_name="Fim vig\xeancia", blank=True
                    ),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ConfigJobPosition",
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
                ("name", models.CharField(max_length=100)),
                (
                    "level_instance",
                    models.PositiveSmallIntegerField(
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
                (
                    "instance",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Inst\xe2ncia",
                        choices=[
                            (1, "PRIMEIRA INST\xc2NCIA"),
                            (2, "SEGUNDA INST\xc2NCIA"),
                        ],
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        default="", max_length=12, verbose_name="C\xf3digo"
                    ),
                ),
                (
                    "designates_exercise",
                    models.BooleanField(
                        default=True, verbose_name="Designa Exerc\xedcio"
                    ),
                ),
                ("boss", models.BooleanField(default=False)),
                (
                    "replaceable",
                    models.BooleanField(default=False, verbose_name="Substitu\xedvel"),
                ),
                (
                    "remunerated",
                    models.BooleanField(default=True, verbose_name="Remunerado"),
                ),
                (
                    "cumulative",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Acumul\xe1vel"
                    ),
                ),
                (
                    "quantity",
                    models.IntegerField(
                        default=0, verbose_name="Quantidade de Vagas", blank=True
                    ),
                ),
                (
                    "educational_level",
                    models.IntegerField(
                        default=3,
                        null=True,
                        verbose_name="N\xedvel de Escolaridade",
                        choices=[
                            (1, "FUNDAMENTAL"),
                            (2, "M\xc9DIO"),
                            (3, "SUPERIOR"),
                            (4, "ELEMENTAR"),
                        ],
                    ),
                ),
                (
                    "workload",
                    models.IntegerField(
                        default=40, verbose_name="Carga Hor\xe1ria", blank=True
                    ),
                ),
                (
                    "type_workload",
                    models.IntegerField(
                        default=2,
                        blank=True,
                        verbose_name="Tipo Carga Hor\xe1ria",
                        choices=[(1, "SEMANAL"), (2, "MENSAL")],
                    ),
                ),
                ("health", models.BooleanField(default=False)),
                ("teacher", models.BooleanField(default=False)),
                ("military", models.BooleanField(default=False)),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(
                        null=True, verbose_name="Fim vig\xeancia", blank=True
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "cbo",
                    models.ForeignKey(to="rh.Cbo", on_delete=models.CASCADE),
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
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="HoursWorkContract",
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
                ("title", models.CharField(max_length=100, verbose_name="T\xedtulo")),
                (
                    "code",
                    models.CharField(
                        unique=True, max_length=30, verbose_name="C\xf3digo"
                    ),
                ),
                ("date_start", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "data_end",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
                (
                    "time_start",
                    models.CharField(
                        max_length=4, verbose_name="Hor\xe1rio de In\xedcio"
                    ),
                ),
                (
                    "time_end",
                    models.CharField(max_length=4, verbose_name="Hor\xe1rio de Fim"),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(
                        verbose_name="Dura\xe7\xe3o da Jornada"
                    ),
                ),
                (
                    "flexible",
                    models.BooleanField(default=True, verbose_name="Flex\xedvel"),
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
                "verbose_name": "Contrato de Hor\xe1rio de Trabalho",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="HoursWorkContractWorkload",
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
                    "week_days",
                    django.contrib.postgres.fields.ArrayField(
                        default=[1, 2, 3, 4, 5],
                        size=None,
                        base_field=models.SmallIntegerField(),
                        blank=True,
                    ),
                ),
                (
                    "workhour_contract",
                    models.ForeignKey(
                        to="rh.HoursWorkContract", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "workload",
                    models.ForeignKey(to="rh.CargaHoraria", on_delete=models.CASCADE),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
        ),
        migrations.CreateModel(
            name="LegalProcess",
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
                    "type_process",
                    models.PositiveIntegerField(verbose_name="Tipo de processo"),
                ),
                (
                    "number_process",
                    models.CharField(max_length=21, verbose_name="N\xfamero processo"),
                ),
                (
                    "start_validity",
                    models.DateField(verbose_name="In\xedcio da validade"),
                ),
                (
                    "end_validity",
                    models.DateField(
                        null=True, verbose_name="Fim da validade", blank=True
                    ),
                ),
                (
                    "cod_authorship",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Autoria", blank=True
                    ),
                ),
                (
                    "matter_process",
                    models.PositiveSmallIntegerField(
                        verbose_name="Mat\xe9ria do processo"
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        max_length=255,
                        null=True,
                        verbose_name="Descri\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "judicial_process_id_local",
                    models.PositiveIntegerField(
                        null=True, verbose_name="N\xfamero Vara", blank=True
                    ),
                ),
                (
                    "all_employees",
                    models.BooleanField(
                        default=False, verbose_name="Todos servidores?"
                    ),
                ),
                (
                    "third_party_code",
                    models.CharField(
                        max_length=4,
                        null=True,
                        verbose_name="C\xf3digo de Terceiro",
                        blank=True,
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
                    "employees",
                    models.ManyToManyField(
                        related_name="suspension_process",
                        verbose_name="Servidores",
                        to="rh.Servidor",
                    ),
                ),
                # ('events', models.ManyToManyField(related_name='suspension_process', verbose_name='Eventos', to='gfp.Evento')),
                (
                    "judicial_process_locality",
                    models.ForeignKey(
                        verbose_name="Munic\xedpio",
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                "verbose_name": "Tabela de Processos Administrativos/Judiciais",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcessSuspension",
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
                    "indicative_suspension",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Indicativo suspens\xe3o", blank=True
                    ),
                ),
                ("date_suspension", models.DateField(null=True, blank=True)),
                (
                    "integral_deposit",
                    models.BooleanField(verbose_name="Dep\xf3sito integral?"),
                ),
                (
                    "scope_decision",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Abrang\xeancia"
                    ),
                ),
                (
                    "extension_decision",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="Extens\xe3o"
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
                (
                    "process",
                    models.ForeignKey(
                        related_name="suspensions",
                        verbose_name="Processo",
                        to="rh.LegalProcess",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="WorkHourInterval",
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
                    "code",
                    models.CharField(
                        unique=True, max_length=30, verbose_name="C\xf3digo"
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="T\xedtulo")),
                ("type_interval", models.IntegerField(default=2)),
                (
                    "time_start",
                    models.CharField(
                        max_length=4, verbose_name="Hor\xe1rio de In\xedcio"
                    ),
                ),
                (
                    "time_end",
                    models.CharField(max_length=4, verbose_name="Hor\xe1rio de Fim"),
                ),
                (
                    "duration",
                    models.PositiveIntegerField(
                        verbose_name="Dura\xe7\xe3o da Jornada"
                    ),
                ),
                ("date_start", models.DateField(verbose_name="Data In\xedcio")),
                (
                    "data_end",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
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
                    "hours_work_contract",
                    models.ForeignKey(
                        related_name="intervals",
                        to="rh.HoursWorkContract",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                "verbose_name": "Intervalo de Hor\xe1rio de Trabalho",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="cargo",
            name="cumulative",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Acumul\xe1vel"
            ),
        ),
        migrations.AddField(
            model_name="cargo",
            name="publication",
            field=models.ForeignKey(
                related_name="publication",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="cargo",
            name="publication_extinction",
            field=models.ForeignKey(
                related_name="publication_extinction",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="carreira",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="carreira",
            name="publication",
            field=models.ForeignKey(
                related_name="career_publication",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="carreira",
            name="publication_extinction",
            field=models.ForeignKey(
                related_name="career_publication_extinction",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="pais",
            name="esocial_code",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="pessoafisica",
            name="retired",
            field=models.BooleanField(default=False, verbose_name="Aposentado"),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="federative_body",
            field=models.ForeignKey(
                verbose_name="Ente federativo",
                blank=True,
                to="rh.UnidadeAdministrativa",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="federative_body_owner",
            field=models.BooleanField(
                default=False, verbose_name="Ente federativo respons\xe1vel?"
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="legal_nature",
            field=models.IntegerField(
                default=1058, verbose_name="Natureza jur\xeddica", blank=True
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="main",
            field=models.BooleanField(
                default=False, verbose_name="Principal do \xf3rg\xe3o"
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="rpps",
            field=models.BooleanField(default=False, verbose_name="Possui RPPS?"),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="siafi",
            field=models.CharField(
                default="000001",
                max_length=6,
                verbose_name="N\xfamero SIAFI",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="subtetus_reference",
            field=models.IntegerField(
                default=1, verbose_name="Poder que se refere o subteto", blank=True
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="subtetus_value",
            field=models.DecimalField(
                default=0,
                verbose_name="Valor do subteto",
                max_digits=14,
                decimal_places=2,
            ),
        ),
        migrations.AddField(
            model_name="unidadeadministrativa",
            name="tax_classification",
            field=models.IntegerField(
                default=1, verbose_name="Classifica\xe7\xe3o tribut\xe1ria", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="cargoquadro",
            name="publicacao_extincao",
            field=models.ForeignKey(
                related_name="publicacao_extincao",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="digitaldocument",
            name="document_type",
            field=models.IntegerField(
                verbose_name="Tipo de Documento",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR"),
                    (2, "CNH"),
                    (3, "CTPS"),
                    (5, "NIS"),
                    (6, "PIS/PASEP"),
                    (9, "RESERVISTA"),
                    (10, "CONSELHO PROFISSIONAL"),
                    (11, "RIC"),
                    (12, "RNE"),
                    (13, "CPF"),
                    (14, "RG"),
                    (15, "PASSAPORTE"),
                    (50, "CERTID\xc3O DE NASCIMENTO"),
                    (51, "CERTID\xc3O DE CASAMENTO"),
                    (52, "COMPROVANTE DE ENDERE\xc7O"),
                    (53, "TERMO DE CUSTODIA DE MENOR"),
                    (54, "UNIAO ESTAVEL"),
                    (55, "COMPROVANTE VOTA\xc7\xc3O/QUITA\xc7\xc3O ELEITORAL"),
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
        migrations.AlterField(
            model_name="trainee",
            name="level",
            field=models.IntegerField(
                default=1,
                verbose_name="N\xedvel",
                choices=[
                    (1, "Fundamental"),
                    (2, "M\xe9dio"),
                    (3, "Forma\xe7\xe3o Profissional"),
                    (4, "Superior"),
                    (8, "Especial"),
                    (9, "M\xe3e social"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="trainee",
            name="nature",
            field=models.IntegerField(
                default=1,
                verbose_name="Natureza",
                choices=[(1, "OBRIGAT\xd3RIO"), (2, "N\xc3O OBRIGAT\xd3RIO")],
            ),
        ),
        migrations.AddField(
            model_name="configjobposition",
            name="job_position",
            field=models.ForeignKey(
                related_name="configs", to="rh.Cargo", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="configjobposition",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configjobposition",
            name="publication_restructuring",
            field=models.ForeignKey(
                related_name="publication_restructuring",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="configcareer",
            name="career",
            field=models.ForeignKey(
                related_name="configs", to="rh.Carreira", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="configcareer",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configcareer",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="configcareer",
            name="publication_restructuring",
            field=models.ForeignKey(
                related_name="config_career_publication_restructuring",
                verbose_name="Publica\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="cargahoraria",
            name="workhourcontract",
            field=models.ManyToManyField(
                related_name="workhourcontract",
                through="rh.HoursWorkContractWorkload",
                to="rh.HoursWorkContract",
            ),
        ),
    ]
