# -*- coding: utf-8 -*-


from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("ged", "0004_auto_20180201_1933"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("standard", "0008_auto_20180426_1520"),
        ("rh", "0068_datamigration_config"),
        ("esocial", "0002_auto_20180105_1403"),
    ]

    operations = [
        migrations.CreateModel(
            name="BatchEvent",
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
                ("group", models.PositiveIntegerField(default=1, verbose_name="Grupo")),
                (
                    "description",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "application",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ESOCIAL"), (2, "EFD-REINF")]
                    ),
                ),
                (
                    "delivery_receipt",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("delivery_date", models.DateTimeField(null=True, blank=True)),
                ("delivery_version_app", models.CharField(max_length=20)),
                (
                    "delivery_status",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[
                            (1, "Aguardando envio"),
                            (201, "Lote recebido com Sucesso"),
                            (202, "Lote recebido com advert\xeancias"),
                            (301, "Erro servidor eSocial"),
                            (401, "Lote incorreto - Erro preenchimento"),
                            (402, "Lote incorreto - Schema inv\xe1lido"),
                            (
                                403,
                                "Lote incorreto - Vers\xe3o do schema n\xe3o permitida",
                            ),
                            (404, "Lote incorreto - Erro certificado"),
                            (405, "Lote incorreto - Lote nulo ou vazio"),
                        ],
                    ),
                ),
                ("process_date", models.DateTimeField(null=True, blank=True)),
                ("process_version_app", models.CharField(max_length=20)),
                (
                    "process_status",
                    models.PositiveIntegerField(
                        default=101,
                        choices=[
                            (101, "Lote aguardando processamento"),
                            (201, "Lote processado com Sucesso"),
                            (202, "Lote processado com advert\xeancias"),
                            (301, "Erro servidor eSocial"),
                            (401, "Lote incorreto - Erro preenchimento"),
                            (402, "Lote incorreto - Schema inv\xe1lido"),
                            (
                                403,
                                "Lote incorreto - Vers\xe3o do schema n\xe3o permitida",
                            ),
                            (404, "Lote incorreto - Erro certificado"),
                            (405, "Lote incorreto - Lote nulo ou vazio"),
                            (501, "Solicita\xe7\xe3o de consulta incorreta"),
                        ],
                    ),
                ),
                (
                    "xsd_schema_validated",
                    models.BooleanField(default=False, verbose_name="Validado"),
                ),
                ("xmlns", models.CharField(max_length=256)),
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
                    "delivery_user",
                    models.ForeignKey(
                        related_name="event_batch_user",
                        verbose_name="Usu\xe1rio",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
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
                "ordering": ("-delivery_date", "group", "created_at"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Configuration",
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
                    "environment",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Ambiente",
                        choices=[(1, "Produ\xe7\xe3o"), (2, "Produ\xe7\xe3o Restrita")],
                    ),
                ),
                (
                    "layout_version",
                    models.CharField(max_length=20, verbose_name="Vers\xe3o do layout"),
                ),
                (
                    "ws_batch_submission",
                    models.CharField(
                        default="",
                        max_length=200,
                        verbose_name="Web Service - Envio",
                        blank=True,
                    ),
                ),
                (
                    "ws_batch_consult_process",
                    models.CharField(
                        default="",
                        max_length=200,
                        verbose_name="Web Service - Consulta",
                        blank=True,
                    ),
                ),
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
                (
                    "certificate_passwd",
                    models.CharField(
                        max_length=32,
                        null=True,
                        verbose_name="Senha do certificado",
                        blank=True,
                    ),
                ),
                (
                    "certificate",
                    models.ForeignKey(
                        related_name="configuration_certificate",
                        verbose_name="Certificado Digital A1(pfx, p12)",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "certificate_ca",
                    models.ForeignKey(
                        related_name="configuration_certificate_ca",
                        verbose_name="Certificado Digital CAs",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
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
                    "employer",
                    models.ForeignKey(
                        related_name="configuration_employer",
                        verbose_name="\xd3rg\xe3o empregador",
                        to="rh.UnidadeAdministrativa",
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
                (
                    "responsible",
                    models.ForeignKey(
                        related_name="configuration_responsible",
                        verbose_name="Respons\xe1vel para ESOCIAL",
                        to="rh.PessoaFisica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "responsible_software_house",
                    models.ForeignKey(
                        related_name="configuration_responsible_software_house",
                        verbose_name="Respons\xe1vel software house",
                        to="rh.PessoaFisica",
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
            name="Dependent",
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
                    "dependente_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "dependente_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("dependente_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "dependente_cpf_dep",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "dependente_dep_irrf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_dep_sf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_inc_trab",
                    models.CharField(max_length=1, null=True, blank=True),
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
        migrations.CreateModel(
            name="Event",
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
                    "oid",
                    models.PositiveIntegerField(
                        null=True, verbose_name="ID objeto origem", blank=True
                    ),
                ),
                (
                    "application",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ESOCIAL"), (2, "EFD-REINF")]
                    ),
                ),
                ("sequential", models.PositiveIntegerField()),
                ("identifier", models.CharField(unique=True, max_length=36)),
                ("name", models.CharField(max_length=255)),
                ("event_version", models.CharField(max_length=20)),
                ("acronym", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=255, null=True)),
                ("competence_month", models.PositiveIntegerField()),
                ("competence_year", models.PositiveIntegerField()),
                (
                    "periodicity",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "MENSAL"),
                            (2, "QUALQUER MOMENTO"),
                            (3, "UMA VEZ"),
                        ],
                    ),
                ),
                (
                    "obligation",
                    models.PositiveIntegerField(
                        default=3,
                        choices=[
                            (1, "OBRIGAT\xd3RIO"),
                            (2, "N\xc3O OBRIGAT\xd3RIO"),
                            (3, "OBRIGAT\xd3RIO SE EXISTIR INFORMA\xc7\xd5ES"),
                            (4, "N\xc3O APLIC\xc1VEL"),
                        ],
                    ),
                ),
                (
                    "action",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[
                            (1, "INCLUS\xc3O"),
                            (2, "ALTERA\xc7\xc3O"),
                            (3, "EXCLUS\xc3O"),
                        ],
                    ),
                ),
                (
                    "xsd_schema_validated",
                    models.BooleanField(default=False, verbose_name="Validado"),
                ),
                ("process_date", models.DateTimeField(null=True, blank=True)),
                (
                    "process_receipt",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "process_status",
                    models.PositiveIntegerField(
                        default=1,
                        choices=[
                            (1, "Aguardando empacotamento"),
                            (2, "Aguardando finaliza\xe7\xe3o de depend\xeancia"),
                            (3, "Empacotado e aguardando envio"),
                            (4, "Enviado e aguardando processamento"),
                            (201, "Sucesso"),
                            (202, "Sucesso com advert\xeancia"),
                            (301, "Erro Servidor"),
                            (401, "Erro no conte\xfado do evento"),
                            (402, "Schema inv\xe1lido"),
                            (403, "Leiaute inv\xe1lido"),
                            (404, "Erro do certificado digital"),
                            (405, "Erro na assinatura evento"),
                            (406, "Evento n\xe3o pertence ao grupo"),
                            (407, "Regra de preced\xeancia de eventos n\xe3o seguida"),
                            (408, "Erro na integra\xe7\xe3o com o sistema CNPJ / CPF"),
                            (
                                409,
                                "Erro na integra\xe7\xe3o - Procura\xe7\xe3o Eletr\xf4nica RFB",
                            ),
                            (
                                410,
                                "Erro na integra\xe7\xe3o - Procura\xe7\xe3o Eletr\xf4nica Caixa",
                            ),
                            (411, "Assinante inv\xe1lido"),
                        ],
                    ),
                ),
                ("process_version_app", models.CharField(max_length=20)),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="IdeEmployer",
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
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
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
            name="IdeProcesso",
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
                    "ide_processo_tp_proc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_processo_nr_proc",
                    models.CharField(max_length=21, null=True, blank=True),
                ),
                (
                    "ide_processo_ext_decisao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_processo_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="IdeTransmitter",
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
                ("ide_transmissor_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_transmissor_nr_insc", models.CharField(max_length=15)),
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
            name="InfoSuspensao",
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
                    "info_susp_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_susp_ind_susp",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("info_susp_dt_decisao", models.DateField(null=True, blank=True)),
                (
                    "info_susp_ind_deposito",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Occurrence",
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
                    "code",
                    models.PositiveIntegerField(
                        default=0, verbose_name="C\xc3\xb3digo", blank=True
                    ),
                ),
                (
                    "type_occurrence",
                    models.PositiveIntegerField(
                        default=1, verbose_name="Tipo", blank=True
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default="",
                        max_length=400,
                        verbose_name="Descri\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        max_length=400,
                        null=True,
                        verbose_name="Localiza\xe7\xe3o",
                        blank=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Process",
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
                    "ide_processo_tp_proc",
                    models.PositiveIntegerField(default=1, blank=True),
                ),
                (
                    "ide_processo_nr_proc",
                    models.CharField(default="", max_length=20, blank=True),
                ),
                (
                    "ide_processo_ext_decisao",
                    models.PositiveIntegerField(default=1, blank=True),
                ),
                (
                    "ide_processo_cod_susp",
                    models.PositiveIntegerField(default=1, blank=True),
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
        migrations.CreateModel(
            name="ProcJudTerceiro",
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
                    "proc_jud_terceiro_cod_terc",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "proc_jud_terceiro_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_terceiro_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReturnResult",
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
                ("delivery_date", models.DateTimeField(null=True, blank=True)),
                ("delivery_version_app", models.CharField(max_length=20)),
                (
                    "delivery_status",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Aguardando envio"),
                            (201, "Lote recebido com Sucesso"),
                            (202, "Lote recebido com advert\xeancias"),
                            (301, "Erro servidor eSocial"),
                            (401, "Lote incorreto - Erro preenchimento"),
                            (402, "Lote incorreto - Schema inv\xe1lido"),
                            (
                                403,
                                "Lote incorreto - Vers\xe3o do schema n\xe3o permitida",
                            ),
                            (404, "Lote incorreto - Erro certificado"),
                            (405, "Lote incorreto - Lote nulo ou vazio"),
                        ],
                    ),
                ),
                ("process_date", models.DateTimeField(null=True, blank=True)),
                (
                    "process_status",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (101, "Lote aguardando processamento"),
                            (201, "Lote processado com Sucesso"),
                            (202, "Lote processado com advert\xeancias"),
                            (301, "Erro servidor eSocial"),
                            (401, "Lote incorreto - Erro preenchimento"),
                            (402, "Lote incorreto - Schema inv\xe1lido"),
                            (
                                403,
                                "Lote incorreto - Vers\xe3o do schema n\xe3o permitida",
                            ),
                            (404, "Lote incorreto - Erro certificado"),
                            (405, "Lote incorreto - Lote nulo ou vazio"),
                            (501, "Solicita\xe7\xe3o de consulta incorreta"),
                        ],
                    ),
                ),
                ("process_version_app", models.CharField(max_length=20)),
                (
                    "batch",
                    models.ForeignKey(
                        related_name="results",
                        verbose_name="Lote",
                        to="esocial.BatchEvent",
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
                    "horario_intervalo_tp_interv",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "horario_intervalo_dur_interv",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "horario_intervalo_ini_interv",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "horario_intervalo_term_interv",
                    models.CharField(max_length=4, null=True, blank=True),
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
        migrations.CreateModel(
            name="S1000",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_periodo_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_periodo_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("info_cadastro_nm_razao", models.CharField(max_length=100)),
                ("info_cadastro_class_trib", models.CharField(max_length=2)),
                (
                    "info_cadastro_nat_jurid",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_cadastro_ind_coop",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cadastro_ind_constr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_cadastro_ind_des_folha", models.PositiveIntegerField()),
                ("info_cadastro_ind_opt_reg_eletron", models.PositiveIntegerField()),
                (
                    "info_cadastro_ind_ent_ed",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                ("info_cadastro_ind_ett", models.CharField(max_length=1)),
                (
                    "info_cadastro_nr_reg_ett",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "dados_isencao_ide_min_lei",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "dados_isencao_nr_certif",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                (
                    "dados_isencao_dt_emis_certif",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "dados_isencao_dt_venc_certif",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "dados_isencao_nr_prot_renov",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                (
                    "dados_isencao_dt_prot_renov",
                    models.DateField(null=True, blank=True),
                ),
                ("dados_isencao_dt_dou", models.DateField(null=True, blank=True)),
                (
                    "dados_isencao_pag_dou",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("contato_nm_ctt", models.CharField(max_length=70)),
                ("contato_cpf_ctt", models.CharField(max_length=11)),
                (
                    "contato_fone_fixo",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_fone_cel",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_email",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "info_op_nr_siafi",
                    models.CharField(max_length=6, null=True, blank=True),
                ),
                (
                    "info_efr_ide_efr",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_efr_cnpj_efr",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_ente_nm_ente",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                ("info_ente_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "info_ente_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_ente_ind_rpps",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_ente_subteto",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_ente_vr_subteto",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_org_internacional_ind_acordo_isen_multa",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "software_house_cnpj_soft_house",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "software_house_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "software_house_nm_cont",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "software_house_telefone",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "software_house_email",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "situacao_pj_ind_sit_pj",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "situacao_pf_ind_sit_pf",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1005",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_estab_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_estab_cnae_prep", models.PositiveIntegerField()),
                ("aliq_gilrat_aliq_rat", models.PositiveIntegerField()),
                (
                    "aliq_gilrat_fap",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "aliq_gilrat_aliq_rat_ajust",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "proc_adm_jud_rat_tp_proc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_adm_jud_rat_nr_proc",
                    models.CharField(max_length=21, null=True, blank=True),
                ),
                (
                    "proc_adm_jud_rat_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_adm_jud_fap_tp_proc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_adm_jud_fap_nr_proc",
                    models.CharField(max_length=21, null=True, blank=True),
                ),
                (
                    "proc_adm_jud_fap_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_caepf_tp_caepf",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_obra_ind_subst_patr_obra",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_trab_reg_pt", models.PositiveIntegerField()),
                ("info_apr_cont_apr", models.PositiveIntegerField()),
                (
                    "info_apr_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "info_apr_cont_ent_ed",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_ent_educ_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "info_pcd_cont_pcd",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_pcd_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1010",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_rubrica_cod_rubr", models.CharField(max_length=30)),
                ("ide_rubrica_ide_tab_rubr", models.CharField(max_length=8)),
                ("ide_rubrica_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_rubrica_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_rubrica_dsc_rubr", models.CharField(max_length=100)),
                ("dados_rubrica_nat_rubr", models.PositiveIntegerField()),
                ("dados_rubrica_tp_rubr", models.PositiveIntegerField()),
                ("dados_rubrica_cod_inc_cp", models.CharField(max_length=2)),
                ("dados_rubrica_cod_inc_irrf", models.CharField(max_length=2)),
                ("dados_rubrica_cod_inc_fgts", models.CharField(max_length=2)),
                ("dados_rubrica_cod_inc_sind", models.CharField(max_length=2)),
                (
                    "dados_rubrica_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "ide_processo_cp",
                    models.ManyToManyField(
                        related_name="event_process_cp", to="esocial.IdeProcesso"
                    ),
                ),
                (
                    "ide_processo_fgts",
                    models.ManyToManyField(
                        related_name="event_process_fgts", to="esocial.IdeProcesso"
                    ),
                ),
                (
                    "ide_processo_irrf",
                    models.ManyToManyField(
                        related_name="event_process_irrf", to="esocial.IdeProcesso"
                    ),
                ),
                (
                    "ide_processo_sind",
                    models.ManyToManyField(
                        related_name="event_process_sind", to="esocial.IdeProcesso"
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1020",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_lotacao_cod_lotacao", models.CharField(max_length=30)),
                ("ide_lotacao_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_lotacao_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_lotacao_tp_lotacao", models.CharField(max_length=2)),
                (
                    "dados_lotacao_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "dados_lotacao_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                ("fpas_lotacao_fpas", models.PositiveIntegerField()),
                ("fpas_lotacao_cod_tercs", models.CharField(max_length=4)),
                (
                    "fpas_lotacao_cod_tercs_susp",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_empr_parcial_tp_insc_contrat",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_empr_parcial_nr_insc_contrat",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_empr_parcial_tp_insc_prop",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_empr_parcial_nr_insc_prop",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "proc_jud_terceiro",
                    models.ManyToManyField(
                        related_name="event_proc_jud_terceiro",
                        to="esocial.ProcJudTerceiro",
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1030",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_cargo_cod_cargo", models.CharField(max_length=30)),
                ("ide_cargo_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_cargo_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_cargo_nm_cargo", models.CharField(max_length=100)),
                ("dados_cargo_cod_cbo", models.CharField(max_length=6)),
                (
                    "cargo_publico_acum_cargo",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "cargo_publico_contagem_esp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "cargo_publico_dedic_excl",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                ("lei_cargo_nr_lei", models.CharField(max_length=12)),
                ("lei_cargo_dt_lei", models.DateField()),
                ("lei_cargo_sit_cargo", models.PositiveIntegerField()),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1035",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_carreira_cod_carreira", models.CharField(max_length=30)),
                ("ide_carreira_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_carreira_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_carreira_dsc_carreira", models.CharField(max_length=100)),
                (
                    "dados_carreira_lei_carr",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("dados_carreira_dt_lei_carr", models.DateField()),
                ("dados_carreira_sit_carr", models.PositiveIntegerField()),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1040",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_funcao_cod_funcao", models.CharField(max_length=30)),
                ("ide_funcao_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_funcao_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_funcao_dsc_funcao", models.CharField(max_length=100)),
                ("dados_funcao_cod_cbo", models.CharField(max_length=6)),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1050",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_hor_contratual_cod_hor_contrat", models.CharField(max_length=30)),
                ("ide_hor_contratual_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_hor_contratual_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_hor_contratual_hr_entr", models.CharField(max_length=4)),
                ("dados_hor_contratual_hr_saida", models.CharField(max_length=4)),
                ("dados_hor_contratual_dur_jornada", models.PositiveIntegerField()),
                (
                    "dados_hor_contratual_per_hor_flexivel",
                    models.CharField(max_length=1),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "horario_intervalo",
                    models.ManyToManyField(
                        related_name="register_S1050", to="esocial.WorkHourInterval"
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1060",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_ambiente_cod_amb", models.CharField(max_length=30)),
                ("ide_ambiente_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_ambiente_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("dados_ambiente_dsc_amb", models.CharField(max_length=999)),
                ("dados_ambiente_local_amb", models.PositiveIntegerField()),
                ("dados_ambiente_tp_insc", models.PositiveIntegerField()),
                ("dados_ambiente_nr_insc", models.CharField(max_length=15)),
                ("fator_risco_cod_fat_ris", models.CharField(max_length=10)),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1070",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_processo_tp_proc", models.PositiveIntegerField()),
                ("ide_processo_nr_proc", models.CharField(max_length=21)),
                ("ide_processo_ini_valid", models.CharField(max_length=7)),
                (
                    "ide_processo_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "dados_proc_ind_autoria",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("dados_proc_ind_mat_proc", models.PositiveIntegerField()),
                (
                    "dados_proc_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "dados_proc_jud_uf_vara",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "dados_proc_jud_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "dados_proc_jud_id_vara",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "nova_validade_ini_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "nova_validade_fim_valid",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "info_susp",
                    models.ManyToManyField(
                        related_name="events", to="esocial.InfoSuspensao"
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1200",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("info_mv_ind_mv", models.PositiveIntegerField(null=True, blank=True)),
                ("remun_outr_empr_tp_insc", models.PositiveIntegerField()),
                ("remun_outr_empr_nr_insc", models.CharField(max_length=15)),
                ("remun_outr_empr_cod_categ", models.PositiveIntegerField()),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "info_complem_nm_trab",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("info_complem_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "info_complem_cod_cbo",
                    models.CharField(max_length=6, null=True, blank=True),
                ),
                (
                    "info_complem_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_complem_qtd_dias_trab",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_empreg_ant",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("sucessao_vinc_dt_adm", models.DateField(null=True, blank=True)),
                (
                    "sucessao_vinc_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_tp_trib",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("dm_dev_cod_categ", models.PositiveIntegerField()),
                (
                    "ide_estab_lot_qtd_dias_av",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_per_apur_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "remun_per_apur_ind_simples",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("det_oper_cnpj_oper", models.CharField(max_length=14)),
                ("det_oper_reg_ans", models.CharField(max_length=6)),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "det_plano_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "det_plano_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "det_plano_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("det_plano_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "det_plano_vlr_pg_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("ide_adc_dt_ac_conv", models.DateField(null=True, blank=True)),
                ("ide_adc_tp_ac_conv", models.CharField(max_length=1)),
                (
                    "ide_adc_comp_ac_conv",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("ide_adc_dt_ef_ac_conv", models.DateField(null=True, blank=True)),
                ("ide_adc_dsc", models.CharField(max_length=255)),
                ("ide_adc_remun_suc", models.CharField(max_length=1)),
                ("ide_periodo_per_ref", models.CharField(max_length=7)),
                ("ide_estab_lot_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_lot_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_lot_cod_lotacao", models.CharField(max_length=30)),
                (
                    "remun_per_ant_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "remun_per_ant_ind_simples",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("itens_remun_cod_rubr", models.CharField(max_length=30)),
                ("itens_remun_ide_tab_rubr", models.CharField(max_length=8)),
                (
                    "itens_remun_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_vr_rubr",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "info_ag_nocivo_grau_exp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_trab_interm_cod_conv",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1200",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1202",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_trabalhador_qtd_dep_fp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_tp_trib",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                (
                    "remun_per_apur_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("remun_per_apur_cod_categ", models.PositiveIntegerField()),
                ("det_oper_cnpj_oper", models.CharField(max_length=14)),
                ("det_oper_reg_ans", models.CharField(max_length=6)),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "det_plano_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "det_plano_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "det_plano_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("det_plano_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "det_plano_vlr_pg_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("ide_adc_dt_lei", models.DateField()),
                ("ide_adc_nr_lei", models.CharField(max_length=12)),
                ("ide_adc_dt_ef", models.DateField(null=True, blank=True)),
                ("ide_periodo_per_ref", models.CharField(max_length=7)),
                ("ide_estab_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_nr_insc", models.CharField(max_length=15)),
                (
                    "remun_per_ant_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("remun_per_ant_cod_categ", models.PositiveIntegerField()),
                ("itens_remun_cod_rubr", models.CharField(max_length=30)),
                ("itens_remun_ide_tab_rubr", models.CharField(max_length=8)),
                (
                    "itens_remun_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "itens_remun_vr_rubr",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1202",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1207",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_benef_cpf_benef", models.CharField(max_length=11)),
                ("dm_dev_tp_benef", models.PositiveIntegerField()),
                ("dm_dev_nr_benefic", models.CharField(max_length=20)),
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("itens_cod_rubr", models.CharField(max_length=30)),
                ("itens_ide_tab_rubr", models.CharField(max_length=8)),
                ("itens_vr_rubr", models.DecimalField(max_digits=14, decimal_places=2)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1207",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1210",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_benef_cpf_benef", models.CharField(max_length=11)),
                (
                    "deps_vr_ded_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("info_pgto_dt_pgto", models.DateField()),
                ("info_pgto_tp_pgto", models.PositiveIntegerField()),
                ("info_pgto_ind_res_br", models.CharField(max_length=1)),
                (
                    "det_pgto_fl_per_ref",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "det_pgto_fl_ide_dm_dev",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "det_pgto_fl_ind_pgto_tt",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "det_pgto_fl_vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_pgto_fl_nr_rec_arq",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_per_ref",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_ide_dm_dev",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_ind_pgto_tt",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ret_pgto_tot_cod_rubr",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ret_pgto_tot_ide_tab_rubr",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "ret_pgto_tot_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ret_pgto_tot_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ret_pgto_tot_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ret_pgto_tot_vr_rubr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_pgto_parc_cod_rubr",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_pgto_parc_ide_tab_rubr",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "info_pgto_parc_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_pgto_parc_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_pgto_parc_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_pgto_parc_vr_rubr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_pgto_fer_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("det_pgto_fer_dt_ini_goz", models.DateField(null=True, blank=True)),
                (
                    "det_pgto_fer_qt_dias",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "det_pgto_fer_vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("det_rubr_fer_cod_rubr", models.CharField(max_length=30)),
                ("det_rubr_fer_ide_tab_rubr", models.CharField(max_length=8)),
                (
                    "det_rubr_fer_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_rubr_fer_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_rubr_fer_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_rubr_fer_vr_rubr",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "pen_alim_cpf_benef",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("pen_alim_dt_nascto_benef", models.DateField(null=True, blank=True)),
                (
                    "pen_alim_nm_benefic",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "pen_alim_vlr_pensao",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_pgto_ant_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_pgto_ant_tp_bc_irrf", models.CharField(max_length=2)),
                (
                    "info_pgto_ant_vr_bc_irrf",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("ide_pais_cod_pais", models.CharField(max_length=3)),
                ("ide_pais_ind_nif", models.PositiveIntegerField()),
                (
                    "ide_pais_nif_benef",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("end_ext_dsc_lograd", models.CharField(max_length=80)),
                (
                    "end_ext_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "end_ext_complem",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "end_ext_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("end_ext_nm_cid", models.CharField(max_length=50)),
                (
                    "end_ext_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1210",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1280",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "info_subst_patr_ind_subst_patr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_subst_patr_perc_red_contrib",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_subst_patr_op_port_cnpj_op_portuario",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1280",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1298",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1298",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1299",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_resp_inf_nm_resp",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_cpf_resp",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_telefone",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_email",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("info_fech_evt_remun", models.CharField(max_length=1)),
                ("info_fech_evt_pgtos", models.CharField(max_length=1)),
                ("info_fech_evt_aq_prod", models.CharField(max_length=1)),
                ("info_fech_evt_com_prod", models.CharField(max_length=1)),
                ("info_fech_evt_contrat_av_np", models.CharField(max_length=1)),
                ("info_fech_evt_info_compl_per", models.CharField(max_length=1)),
                (
                    "info_fech_comp_sem_movto",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1299",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1300",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("contrib_sind_cnpj_sindic", models.CharField(max_length=14)),
                ("contrib_sind_tp_contrib_sind", models.PositiveIntegerField()),
                (
                    "contrib_sind_vlr_contrib_sind",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S1300",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2100",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("trabalhador_cpf_trab", models.CharField(max_length=11)),
                ("trabalhador_nis_trab", models.CharField(max_length=11)),
                ("trabalhador_nm_trab", models.CharField(max_length=70)),
                ("trabalhador_sexo", models.CharField(max_length=1)),
                ("trabalhador_raca_cor", models.PositiveIntegerField()),
                (
                    "trabalhador_est_civ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("trabalhador_grau_instr", models.CharField(max_length=2)),
                (
                    "trabalhador_nm_soc",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("nascimento_dt_nascto", models.DateField()),
                (
                    "nascimento_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "nascimento_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("nascimento_pais_nascto", models.CharField(max_length=3)),
                ("nascimento_pais_nac", models.CharField(max_length=3)),
                (
                    "nascimento_nm_mae",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "nascimento_nm_pai",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ctps_nr_ctps",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ctps_serie_ctps",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                ("ctps_uf_ctps", models.CharField(max_length=2, null=True, blank=True)),
                ("ric_nr_ric", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "ric_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("ric_dt_exped", models.DateField(null=True, blank=True)),
                ("rg_nr_rg", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rg_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rg_dt_exped", models.DateField(null=True, blank=True)),
                ("rne_nr_rne", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rne_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rne_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_nr_oc", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "oc_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("oc_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_dt_valid", models.DateField(null=True, blank=True)),
                (
                    "cnh_nr_reg_cnh",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("cnh_dt_exped", models.DateField(null=True, blank=True)),
                ("cnh_uf_cnh", models.CharField(max_length=2, null=True, blank=True)),
                ("cnh_dt_valid", models.DateField(null=True, blank=True)),
                ("cnh_dt_pri_hab", models.DateField(null=True, blank=True)),
                (
                    "cnh_categoria_cnh",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "brasil_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "brasil_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "brasil_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "brasil_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "brasil_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("brasil_cep", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "brasil_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("brasil_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "exterior_pais_resid",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "exterior_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "exterior_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "exterior_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "exterior_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "exterior_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "exterior_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_dt_chegada",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_class_trab_estrang",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_casado_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_filhos_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_fisica",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_visual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_auditiva",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_mental",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_intelectual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_reab_readap",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_info_cota",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "dependente_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "dependente_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("dependente_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "dependente_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "dependente_dep_irrf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_dep_sf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_dep_plan",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_inc_trab",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "aposentadoria_trab_aposent",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "contato_fone_princ",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_fone_alternat",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_email_princ",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "contato_email_alternat",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("vinculo_matricula", models.CharField(max_length=30)),
                ("vinculo_tp_reg_trab", models.PositiveIntegerField()),
                ("vinculo_tp_reg_prev", models.PositiveIntegerField()),
                ("info_celetista_dt_adm", models.DateField(null=True, blank=True)),
                (
                    "info_celetista_tp_admissao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_ind_admissao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_tp_reg_jor",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_dt_base",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_cnpj_sind_categ_prof",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                ("fgts_opc_fgts", models.PositiveIntegerField()),
                ("fgts_dt_opc_fgts", models.DateField(null=True, blank=True)),
                (
                    "trab_temporario_hip_leg",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_temporario_just_contr",
                    models.CharField(max_length=999, null=True, blank=True),
                ),
                (
                    "trab_temporario_tp_incl_contr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("ide_tomador_serv_tp_insc", models.PositiveIntegerField()),
                ("ide_tomador_serv_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_estab_vinc_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_estab_vinc_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "ide_trab_substituido_cpf_trab_subst",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("aprend_tp_insc", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "aprend_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "info_estatutario_ind_provim",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estatutario_tp_prov",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estatutario_dt_nomeacao",
                    models.DateField(null=True, blank=True),
                ),
                ("info_estatutario_dt_posse", models.DateField(null=True, blank=True)),
                (
                    "info_estatutario_dt_exercicio",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "info_estatutario_tp_plan_rp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_dec_jud_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "info_contrato_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_contrato_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_cod_categ", models.PositiveIntegerField()),
                (
                    "info_contrato_cod_carreira",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_dt_ingr_carr", models.DateField(null=True, blank=True)),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("remuneracao_und_sal_fixo", models.PositiveIntegerField()),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=90, null=True, blank=True),
                ),
                ("duracao_tp_contr", models.PositiveIntegerField()),
                ("duracao_dt_term", models.DateField(null=True, blank=True)),
                (
                    "local_trab_geral_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_geral_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "local_trab_geral_desc_comp",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "local_trab_dom_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "local_trab_dom_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "local_trab_dom_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_dom_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "hor_contratual_qtd_hrs_sem",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                (
                    "hor_contratual_tp_jornada",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "hor_contratual_dsc_tp_jorn",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "hor_contratual_tmp_parc",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                ("horario_dia", models.PositiveIntegerField()),
                ("horario_cod_hor_contrat", models.CharField(max_length=30)),
                (
                    "filiacao_sindical_cnpj_sind_trab",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "alvara_judicial_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_empreg_ant",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_dt_ini_vinculo",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "sucessao_vinc_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("afastamento_dt_ini_afast", models.DateField(null=True, blank=True)),
                (
                    "afastamento_cod_mot_afast",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("desligamento_dt_deslig", models.DateField(null=True, blank=True)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2100",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2190",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("info_reg_prelim_cpf_trab", models.CharField(max_length=11)),
                ("info_reg_prelim_dt_nascto", models.DateField()),
                ("info_reg_prelim_dt_adm", models.DateField()),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2190",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2200",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("trabalhador_cpf_trab", models.CharField(max_length=11)),
                ("trabalhador_nis_trab", models.CharField(max_length=11)),
                ("trabalhador_nm_trab", models.CharField(max_length=70)),
                ("trabalhador_sexo", models.CharField(max_length=1)),
                ("trabalhador_raca_cor", models.PositiveIntegerField()),
                (
                    "trabalhador_est_civ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("trabalhador_grau_instr", models.CharField(max_length=2)),
                (
                    "trabalhador_ind_pri_empr",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "trabalhador_nm_soc",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("nascimento_dt_nascto", models.DateField()),
                (
                    "nascimento_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "nascimento_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("nascimento_pais_nascto", models.CharField(max_length=3)),
                ("nascimento_pais_nac", models.CharField(max_length=3)),
                (
                    "nascimento_nm_mae",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "nascimento_nm_pai",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ctps_nr_ctps",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ctps_serie_ctps",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                ("ctps_uf_ctps", models.CharField(max_length=2, null=True, blank=True)),
                ("ric_nr_ric", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "ric_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("ric_dt_exped", models.DateField(null=True, blank=True)),
                ("rg_nr_rg", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rg_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rg_dt_exped", models.DateField(null=True, blank=True)),
                ("rne_nr_rne", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rne_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rne_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_nr_oc", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "oc_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("oc_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_dt_valid", models.DateField(null=True, blank=True)),
                (
                    "cnh_nr_reg_cnh",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("cnh_dt_exped", models.DateField(null=True, blank=True)),
                ("cnh_uf_cnh", models.CharField(max_length=2, null=True, blank=True)),
                ("cnh_dt_valid", models.DateField(null=True, blank=True)),
                ("cnh_dt_pri_hab", models.DateField(null=True, blank=True)),
                (
                    "cnh_categoria_cnh",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "brasil_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "brasil_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "brasil_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "brasil_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "brasil_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("brasil_cep", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "brasil_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("brasil_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "exterior_pais_resid",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "exterior_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "exterior_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "exterior_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "exterior_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "exterior_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "exterior_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_dt_chegada",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_class_trab_estrang",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_casado_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_filhos_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_fisica",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_visual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_auditiva",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_mental",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_intelectual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_reab_readap",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_info_cota",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "aposentadoria_trab_aposent",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "contato_fone_princ",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_fone_alternat",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_email_princ",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "contato_email_alternat",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("vinculo_matricula", models.CharField(max_length=30)),
                ("vinculo_tp_reg_trab", models.PositiveIntegerField()),
                ("vinculo_tp_reg_prev", models.PositiveIntegerField()),
                (
                    "vinculo_nr_rec_inf_prelim",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("vinculo_cad_ini", models.CharField(max_length=1)),
                ("info_celetista_dt_adm", models.DateField(null=True, blank=True)),
                (
                    "info_celetista_tp_admissao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_ind_admissao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_tp_reg_jor",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_dt_base",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_cnpj_sind_categ_prof",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                ("fgts_opc_fgts", models.PositiveIntegerField(null=True, blank=True)),
                ("fgts_dt_opc_fgts", models.DateField(null=True, blank=True)),
                (
                    "trab_temporario_hip_leg",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_temporario_just_contr",
                    models.CharField(max_length=999, null=True, blank=True),
                ),
                (
                    "trab_temporario_tp_incl_contr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_tomador_serv_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_tomador_serv_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "ide_estab_vinc_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_estab_vinc_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "ide_trab_substituido_cpf_trab_subst",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("aprend_tp_insc", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "aprend_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "info_estatutario_ind_provim",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estatutario_tp_prov",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estatutario_dt_nomeacao",
                    models.DateField(null=True, blank=True),
                ),
                ("info_estatutario_dt_posse", models.DateField(null=True, blank=True)),
                (
                    "info_estatutario_dt_exercicio",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "info_estatutario_tp_plan_rp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_dec_jud_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "info_contrato_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_contrato_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_cod_categ", models.PositiveIntegerField()),
                (
                    "info_contrato_cod_carreira",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_dt_ingr_carr", models.DateField(null=True, blank=True)),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("remuneracao_und_sal_fixo", models.PositiveIntegerField()),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("duracao_tp_contr", models.PositiveIntegerField()),
                ("duracao_dt_term", models.DateField(null=True, blank=True)),
                (
                    "duracao_clau_asseg",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "local_trab_geral_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_geral_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "local_trab_geral_desc_comp",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "local_trab_dom_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "local_trab_dom_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "local_trab_dom_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_dom_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "hor_contratual_qtd_hrs_sem",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                (
                    "hor_contratual_tp_jornada",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "hor_contratual_dsc_tp_jorn",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "hor_contratual_tmp_parc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("horario_dia", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "horario_cod_hor_contrat",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "filiacao_sindical_cnpj_sind_trab",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "alvara_judicial_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "observacoes_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_empreg_ant",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("sucessao_vinc_dt_transf", models.DateField(null=True, blank=True)),
                (
                    "sucessao_vinc_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "transf_dom_cpf_substituido",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "transf_dom_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("transf_dom_dt_transf", models.DateField(null=True, blank=True)),
                ("afastamento_dt_ini_afast", models.DateField(null=True, blank=True)),
                (
                    "afastamento_cod_mot_afast",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("desligamento_dt_deslig", models.DateField(null=True, blank=True)),
                (
                    "dependente",
                    models.ManyToManyField(
                        related_name="register_S2200", to="esocial.Dependent"
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2205",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                ("alteracao_dt_alteracao", models.DateField()),
                (
                    "dados_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("dados_trabalhador_nm_trab", models.CharField(max_length=70)),
                ("dados_trabalhador_sexo", models.CharField(max_length=1)),
                ("dados_trabalhador_raca_cor", models.PositiveIntegerField()),
                (
                    "dados_trabalhador_est_civ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("dados_trabalhador_grau_instr", models.CharField(max_length=2)),
                (
                    "dados_trabalhador_nm_soc",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ctps_nr_ctps",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ctps_serie_ctps",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                ("ctps_uf_ctps", models.CharField(max_length=2, null=True, blank=True)),
                ("ric_nr_ric", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "ric_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("ric_dt_exped", models.DateField(null=True, blank=True)),
                ("rg_nr_rg", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rg_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rg_dt_exped", models.DateField(null=True, blank=True)),
                ("rne_nr_rne", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rne_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rne_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_nr_oc", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "oc_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("oc_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_dt_valid", models.DateField(null=True, blank=True)),
                (
                    "cnh_nr_reg_cnh",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("cnh_dt_exped", models.DateField(null=True, blank=True)),
                ("cnh_uf_cnh", models.CharField(max_length=2, null=True, blank=True)),
                ("cnh_dt_valid", models.DateField(null=True, blank=True)),
                ("cnh_dt_pri_hab", models.DateField(null=True, blank=True)),
                (
                    "cnh_categoria_cnh",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "brasil_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "brasil_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "brasil_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "brasil_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "brasil_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("brasil_cep", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "brasil_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("brasil_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "exterior_pais_resid",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "exterior_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "exterior_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "exterior_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "exterior_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "exterior_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "exterior_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_dt_chegada",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_class_trab_estrang",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_casado_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_filhos_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_fisica",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_visual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_auditiva",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_mental",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_intelectual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_reab_readap",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_info_cota",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "dependente_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "dependente_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("dependente_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "dependente_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "dependente_dep_irrf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_dep_sf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_inc_trab",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "aposentadoria_trab_aposent",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "contato_fone_princ",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_fone_alternat",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_email_princ",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "contato_email_alternat",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2205",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2206",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                ("ide_vinculo_nis_trab", models.CharField(max_length=11)),
                ("ide_vinculo_matricula", models.CharField(max_length=30)),
                ("alt_contratual_dt_alteracao", models.DateField()),
                ("alt_contratual_dt_ef", models.DateField(null=True, blank=True)),
                (
                    "alt_contratual_dsc_alt",
                    models.CharField(max_length=150, null=True, blank=True),
                ),
                ("vinculo_tp_reg_prev", models.PositiveIntegerField()),
                (
                    "info_celetista_tp_reg_jor",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_dt_base",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_celetista_cnpj_sind_categ_prof",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "trab_temp_just_prorr",
                    models.CharField(max_length=999, null=True, blank=True),
                ),
                ("aprend_tp_insc", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "aprend_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "info_estatutario_tp_plan_rp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_contrato_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_contrato_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_cod_categ", models.PositiveIntegerField()),
                (
                    "info_contrato_cod_carreira",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_contrato_dt_ingr_carr", models.DateField(null=True, blank=True)),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("remuneracao_und_sal_fixo", models.PositiveIntegerField()),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("duracao_tp_contr", models.PositiveIntegerField()),
                ("duracao_dt_term", models.DateField(null=True, blank=True)),
                (
                    "local_trab_geral_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_geral_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "local_trab_geral_desc_comp",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "local_trab_dom_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_trab_dom_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "local_trab_dom_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "local_trab_dom_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "local_trab_dom_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_trab_dom_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "hor_contratual_qtd_hrs_sem",
                    models.DecimalField(
                        null=True, max_digits=4, decimal_places=2, blank=True
                    ),
                ),
                (
                    "hor_contratual_tp_jornada",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "hor_contratual_dsc_tp_jorn",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "hor_contratual_tmp_parc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("horario_dia", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "horario_cod_hor_contrat",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "filiacao_sindical_cnpj_sind_trab",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "alvara_judicial_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "observacoes_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "serv_publ_mtv_alter",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2206",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2210",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_registrador_tp_registrador", models.PositiveIntegerField()),
                (
                    "ide_registrador_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_registrador_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("cat_dt_acid", models.DateField()),
                ("cat_tp_acid", models.CharField(max_length=6)),
                ("cat_hr_acid", models.CharField(max_length=4)),
                ("cat_hrs_trab_antes_acid", models.CharField(max_length=4)),
                ("cat_tp_cat", models.PositiveIntegerField()),
                ("cat_ind_cat_obito", models.CharField(max_length=1)),
                ("cat_dt_obito", models.DateField(null=True, blank=True)),
                ("cat_ind_comun_policia", models.CharField(max_length=1)),
                (
                    "cat_cod_sit_geradora",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("cat_iniciat_cat", models.PositiveIntegerField()),
                (
                    "cat_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("local_acidente_tp_local", models.PositiveIntegerField()),
                (
                    "local_acidente_dsc_local",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_acidente_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "local_acidente_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "local_acidente_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "local_acidente_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "local_acidente_cnpj_local_acid",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "local_acidente_pais",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "local_acidente_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("parte_atingida_cod_parte_ating", models.PositiveIntegerField()),
                ("parte_atingida_lateralidade", models.PositiveIntegerField()),
                ("agente_causador_cod_agnt_causador", models.PositiveIntegerField()),
                (
                    "atestado_cod_cnes",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("atestado_dt_atendimento", models.DateField(null=True, blank=True)),
                (
                    "atestado_hr_atendimento",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "atestado_ind_internacao",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "atestado_dur_trat",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "atestado_ind_afast",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "atestado_dsc_lesao",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "atestado_dsc_comp_lesao",
                    models.CharField(max_length=200, null=True, blank=True),
                ),
                (
                    "atestado_diag_provavel",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "atestado_cod_cid",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "atestado_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("emitente_nm_emit", models.CharField(max_length=70)),
                ("emitente_ide_oc", models.PositiveIntegerField()),
                ("emitente_nr_oc", models.CharField(max_length=14)),
                (
                    "emitente_uf_oc",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("cat_origem_dt_cat_orig", models.DateField(null=True, blank=True)),
                (
                    "cat_origem_nr_cat_orig",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2210",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2220",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_vinculo_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("aso_dt_aso", models.DateField()),
                ("aso_tp_aso", models.PositiveIntegerField()),
                ("aso_res_aso", models.PositiveIntegerField()),
                ("exame_dt_exm", models.DateField(null=True, blank=True)),
                (
                    "exame_proc_realizado",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "exame_obs_proc",
                    models.CharField(max_length=200, null=True, blank=True),
                ),
                (
                    "exame_interpr_exm",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("exame_ord_exame", models.PositiveIntegerField(null=True, blank=True)),
                ("exame_dt_ini_monit", models.DateField(null=True, blank=True)),
                ("exame_dt_fim_monit", models.DateField(null=True, blank=True)),
                (
                    "exame_ind_result",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("resp_monit_nis_resp", models.CharField(max_length=11)),
                ("resp_monit_nr_cons_classe", models.CharField(max_length=8)),
                (
                    "resp_monit_uf_cons_classe",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "ide_serv_saude_cod_cnes",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("ide_serv_saude_frm_ctt", models.CharField(max_length=100)),
                (
                    "ide_serv_saude_email",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("medico_nm_med", models.CharField(max_length=70)),
                ("crm_nr_crm", models.CharField(max_length=8)),
                ("crm_uf_crm", models.CharField(max_length=2)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2220",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2230",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_vinculo_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_vinculo_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ini_afastamento_dt_ini_afast",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "ini_afastamento_cod_mot_afast",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "ini_afastamento_info_mesmo_mtv",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "ini_afastamento_tp_acid_transito",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ini_afastamento_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "info_atestado_cod_cid",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_atestado_qtd_dias_afast",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("emitente_nm_emit", models.CharField(max_length=70)),
                ("emitente_ide_oc", models.PositiveIntegerField()),
                ("emitente_nr_oc", models.CharField(max_length=14)),
                (
                    "emitente_uf_oc",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "info_cessao_cnpj_cess",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_cessao_inf_onus",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_mand_sind_cnpj_sind",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_mand_sind_inf_onus_remun",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_retif_orig_retif",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_retif_tp_proc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_retif_nr_proc",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "fim_afastamento_dt_term_afast",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2230",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2240",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_vinculo_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ini_exp_risco_dt_ini_condicao",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "alt_exp_risco_dt_alt_condicao",
                    models.DateField(null=True, blank=True),
                ),
                ("info_ativ_dsc_ativ_des", models.CharField(max_length=999)),
                ("fat_risco_cod_fat_ris", models.CharField(max_length=10)),
                (
                    "fat_risco_int_conc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "fat_risco_tec_medicao",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("epc_epi_utiliz_epc", models.PositiveIntegerField()),
                ("epc_epi_utiliz_epi", models.PositiveIntegerField()),
                ("epc_dsc_epc", models.CharField(max_length=70, null=True, blank=True)),
                ("epc_efic_epc", models.CharField(max_length=1, null=True, blank=True)),
                ("epi_ca_epi", models.CharField(max_length=20, null=True, blank=True)),
                ("epi_efic_epi", models.CharField(max_length=1, null=True, blank=True)),
                (
                    "epi_med_protecao",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "epi_cond_functo",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "epi_prz_valid",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "epi_periodic_troca",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "epi_higienizacao",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                ("fim_exp_risco_dt_fim_condicao", models.DateField()),
                ("info_amb_cod_amb", models.CharField(max_length=30)),
                ("resp_reg_dt_ini", models.DateField()),
                ("resp_reg_dt_fim", models.DateField(null=True, blank=True)),
                ("resp_reg_nis_resp", models.CharField(max_length=11)),
                ("resp_reg_nr_oc", models.CharField(max_length=14)),
                (
                    "resp_reg_uf_oc",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2240",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2241",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_vinculo_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ini_insal_peric_dt_ini_condicao",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "alt_insal_peric_dt_alt_condicao",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "fim_insal_peric_dt_fim_condicao",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "ini_aposent_esp_dt_ini_condicao",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "alt_aposent_esp_dt_alt_condicao",
                    models.DateField(null=True, blank=True),
                ),
                ("infoamb_cod_amb", models.CharField(max_length=30)),
                ("fat_risco_cod_fat_ris", models.CharField(max_length=10)),
                (
                    "fim_aposent_esp_dt_fim_condicao",
                    models.DateField(null=True, blank=True),
                ),
                ("info_amb_cod_amb", models.CharField(max_length=30)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2241",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2298",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                ("ide_vinculo_nis_trab", models.CharField(max_length=11)),
                ("ide_vinculo_matricula", models.CharField(max_length=30)),
                ("info_reintegr_tp_reint", models.PositiveIntegerField()),
                (
                    "info_reintegr_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "info_reintegr_nr_lei_anistia",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                ("info_reintegr_dt_efet_retorno", models.DateField()),
                ("info_reintegr_dt_efeito", models.DateField()),
                ("info_reintegr_ind_pagto_juizo", models.CharField(max_length=1)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2298",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2299",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                ("ide_vinculo_nis_trab", models.CharField(max_length=11)),
                ("ide_vinculo_matricula", models.CharField(max_length=30)),
                ("info_deslig_mtv_deslig", models.CharField(max_length=2)),
                ("info_deslig_dt_deslig", models.DateField()),
                ("info_deslig_ind_pagto_api", models.CharField(max_length=1)),
                (
                    "info_deslig_dt_proj_fim_api",
                    models.DateField(null=True, blank=True),
                ),
                ("info_deslig_pens_alim", models.PositiveIntegerField()),
                (
                    "info_deslig_perc_aliment",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_deslig_vr_alim",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_deslig_nr_cert_obito",
                    models.CharField(max_length=32, null=True, blank=True),
                ),
                (
                    "info_deslig_nr_proc_trab",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("info_deslig_ind_cumpr_parc", models.PositiveIntegerField()),
                (
                    "info_deslig_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_sucessora",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "transf_tit_cpf_substituto",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("transf_tit_dt_nascto", models.DateField(null=True, blank=True)),
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("det_oper_cnpj_oper", models.CharField(max_length=14)),
                ("det_oper_reg_ans", models.CharField(max_length=6)),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "det_plano_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "det_plano_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "det_plano_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("det_plano_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "det_plano_vlr_pg_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("ide_adc_dt_ac_conv", models.DateField()),
                ("ide_adc_tp_ac_conv", models.CharField(max_length=1)),
                (
                    "ide_adc_comp_ac_conv",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("ide_adc_dt_ef_ac_conv", models.DateField()),
                ("ide_adc_dsc", models.CharField(max_length=255)),
                ("ide_periodo_per_ref", models.CharField(max_length=7)),
                ("ide_estab_lot_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_lot_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_lot_cod_lotacao", models.CharField(max_length=30)),
                ("det_verbas_cod_rubr", models.CharField(max_length=30)),
                ("det_verbas_ide_tab_rubr", models.CharField(max_length=8)),
                (
                    "det_verbas_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_vr_rubr",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "info_ag_nocivo_grau_exp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_simples_ind_simples",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_trab_interm_cod_conv",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_tp_trib",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_mv_ind_mv", models.PositiveIntegerField(null=True, blank=True)),
                ("remun_outr_empr_tp_insc", models.PositiveIntegerField()),
                ("remun_outr_empr_nr_insc", models.CharField(max_length=15)),
                ("remun_outr_empr_cod_categ", models.PositiveIntegerField()),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("quarentena_dt_fim_quar", models.DateField(null=True, blank=True)),
                ("consig_fgts_id_consig", models.CharField(max_length=1)),
                (
                    "consig_fgts_ins_consig",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "consig_fgts_nr_contr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2299",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2300",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("trabalhador_nm_trab", models.CharField(max_length=70)),
                ("trabalhador_sexo", models.CharField(max_length=1)),
                ("trabalhador_raca_cor", models.PositiveIntegerField()),
                (
                    "trabalhador_est_civ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("trabalhador_grau_instr", models.CharField(max_length=2)),
                (
                    "trabalhador_nm_soc",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("nascimento_dt_nascto", models.DateField()),
                (
                    "nascimento_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "nascimento_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("nascimento_pais_nascto", models.CharField(max_length=3)),
                ("nascimento_pais_nac", models.CharField(max_length=3)),
                (
                    "nascimento_nm_mae",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "nascimento_nm_pai",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ctps_nr_ctps",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ctps_serie_ctps",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                ("ctps_uf_ctps", models.CharField(max_length=2, null=True, blank=True)),
                ("ric_nr_ric", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "ric_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("ric_dt_exped", models.DateField(null=True, blank=True)),
                ("rg_nr_rg", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rg_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rg_dt_exped", models.DateField(null=True, blank=True)),
                ("rne_nr_rne", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "rne_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("rne_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_nr_oc", models.CharField(max_length=14, null=True, blank=True)),
                (
                    "oc_orgao_emissor",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("oc_dt_exped", models.DateField(null=True, blank=True)),
                ("oc_dt_valid", models.DateField(null=True, blank=True)),
                (
                    "cnh_nr_reg_cnh",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("cnh_dt_exped", models.DateField(null=True, blank=True)),
                ("cnh_uf_cnh", models.CharField(max_length=2, null=True, blank=True)),
                ("cnh_dt_valid", models.DateField(null=True, blank=True)),
                ("cnh_dt_pri_hab", models.DateField(null=True, blank=True)),
                (
                    "cnh_categoria_cnh",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "brasil_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "brasil_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "brasil_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "brasil_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "brasil_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("brasil_cep", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "brasil_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("brasil_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "exterior_pais_resid",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "exterior_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "exterior_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "exterior_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "exterior_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "exterior_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "exterior_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_dt_chegada",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_class_trab_estrang",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_casado_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "trab_estrangeiro_filhos_br",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_fisica",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_visual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_auditiva",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_mental",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_def_intelectual",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_reab_readap",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_deficiencia_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "dependente_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "dependente_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("dependente_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "dependente_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "dependente_dep_irrf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_dep_sf",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "dependente_inc_trab",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "contato_fone_princ",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_fone_alternat",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "contato_email_princ",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "contato_email_alternat",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("info_tsv_inicio_cod_categ", models.PositiveIntegerField()),
                ("info_tsv_inicio_dt_inicio", models.DateField()),
                (
                    "info_tsv_inicio_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "remuneracao_und_sal_fixo",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("fgts_opc_fgts", models.PositiveIntegerField(null=True, blank=True)),
                ("fgts_dt_opc_fgts", models.DateField(null=True, blank=True)),
                (
                    "info_dirigente_sindical_categ_orig",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_dirigente_sindical_cnpj_origem",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_dirigente_sindical_dt_adm_orig",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "info_dirigente_sindical_matric_orig",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_trab_cedido_categ_orig",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_trab_cedido_cnpj_cednt",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_trab_cedido_matric_ced",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_trab_cedido_dt_adm_ced",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "info_trab_cedido_tp_reg_trab",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_trab_cedido_tp_reg_prev",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_trab_cedido_inf_onus",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estagiario_nat_estagio",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_estagiario_niv_estagio",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estagiario_area_atuacao",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "info_estagiario_nr_apol",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_estagiario_vlr_bolsa",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_estagiario_dt_prev_term",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "inst_ensino_cnpj_inst_ensino",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                ("inst_ensino_nm_razao", models.CharField(max_length=100)),
                (
                    "inst_ensino_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "inst_ensino_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "inst_ensino_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "inst_ensino_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "inst_ensino_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "inst_ensino_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "age_integracao_cnpj_agnt_integ",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "age_integracao_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "age_integracao_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "age_integracao_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "age_integracao_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "age_integracao_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "age_integracao_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "age_integracao_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_cpf_supervisor",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_nm_superv",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2300",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2306",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trab_sem_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trab_sem_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("ide_trab_sem_vinculo_cod_categ", models.PositiveIntegerField()),
                ("info_tsv_alteracao_dt_alteracao", models.DateField()),
                (
                    "info_tsv_alteracao_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "remuneracao_und_sal_fixo",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "info_estagiario_nat_estagio",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_estagiario_niv_estagio",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estagiario_area_atuacao",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "info_estagiario_nr_apol",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_estagiario_vlr_bolsa",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_estagiario_dt_prev_term",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "inst_ensino_cnpj_inst_ensino",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                ("inst_ensino_nm_razao", models.CharField(max_length=100)),
                (
                    "inst_ensino_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "inst_ensino_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "inst_ensino_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "inst_ensino_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "inst_ensino_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "inst_ensino_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "age_integracao_cnpj_agnt_integ",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "age_integracao_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "age_integracao_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "age_integracao_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "age_integracao_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "age_integracao_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "age_integracao_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "age_integracao_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_cpf_supervisor",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_nm_superv",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2306",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2399",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trab_sem_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trab_sem_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("ide_trab_sem_vinculo_cod_categ", models.PositiveIntegerField()),
                ("info_tsv_termino_dt_term", models.DateField()),
                (
                    "info_tsv_termino_mtv_deslig_tsv",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("ide_estab_lot_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_lot_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_lot_cod_lotacao", models.CharField(max_length=30)),
                ("det_verbas_cod_rubr", models.CharField(max_length=30)),
                ("det_verbas_ide_tab_rubr", models.CharField(max_length=8)),
                (
                    "det_verbas_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_verbas_vr_rubr",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("det_oper_cnpj_oper", models.CharField(max_length=14)),
                ("det_oper_reg_ans", models.CharField(max_length=6)),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "det_plano_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "det_plano_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "det_plano_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("det_plano_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "det_plano_vlr_pg_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_ag_nocivo_grau_exp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_simples_ind_simples",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_tp_trib",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "proc_jud_trab_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_mv_ind_mv", models.PositiveIntegerField(null=True, blank=True)),
                ("remun_outr_empr_tp_insc", models.PositiveIntegerField()),
                ("remun_outr_empr_nr_insc", models.CharField(max_length=15)),
                ("remun_outr_empr_cod_categ", models.PositiveIntegerField()),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("quarentena_dt_fim_quar", models.DateField(null=True, blank=True)),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2399",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2400",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_benef_cpf_benef", models.CharField(max_length=11)),
                ("ide_benef_nm_benefic", models.CharField(max_length=70)),
                ("dados_nasc_dt_nascto", models.DateField()),
                (
                    "dados_nasc_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "dados_nasc_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("dados_nasc_pais_nascto", models.CharField(max_length=3)),
                ("dados_nasc_pais_nac", models.CharField(max_length=3)),
                (
                    "dados_nasc_nm_mae",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "dados_nasc_nm_pai",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "brasil_tp_lograd",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "brasil_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "brasil_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "brasil_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "brasil_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("brasil_cep", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "brasil_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("brasil_uf", models.CharField(max_length=2, null=True, blank=True)),
                (
                    "exterior_pais_resid",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "exterior_dsc_lograd",
                    models.CharField(max_length=80, null=True, blank=True),
                ),
                (
                    "exterior_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "exterior_complemento",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "exterior_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                (
                    "exterior_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "exterior_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("info_beneficio_tp_plan_rp", models.PositiveIntegerField()),
                (
                    "ini_beneficio_tp_benef",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ini_beneficio_nr_benefic",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("ini_beneficio_dt_ini_benef", models.DateField(null=True, blank=True)),
                (
                    "ini_beneficio_vr_benef",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "alt_beneficio_tp_benef",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "alt_beneficio_nr_benefic",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("alt_beneficio_dt_ini_benef", models.DateField(null=True, blank=True)),
                (
                    "alt_beneficio_vr_benef",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_pen_morte_id_quota",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_pen_morte_cpf_inst",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "fim_beneficio_tp_benef",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "fim_beneficio_nr_benefic",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("fim_beneficio_dt_fim_benef", models.DateField(null=True, blank=True)),
                (
                    "fim_beneficio_mtv_fim",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S2400",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S3000",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("info_exclusao_tp_evento", models.CharField(max_length=6)),
                ("info_exclusao_nr_rec_evt", models.CharField(max_length=40)),
                (
                    "ide_trabalhador_cpf_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S3000",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S5001",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_evento_nr_rec_arq_base",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "proc_jud_trab_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "proc_jud_trab_cod_susp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cp_calc_tp_cr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cp_calc_vr_cp_seg",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cp_calc_vr_desc_seg",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("ide_estab_lot_tp_insc", models.PositiveIntegerField()),
                ("ide_estab_lot_nr_insc", models.CharField(max_length=15)),
                ("ide_estab_lot_cod_lotacao", models.CharField(max_length=30)),
                (
                    "info_categ_incid_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_categ_incid_cod_categ", models.PositiveIntegerField()),
                (
                    "info_categ_incid_ind_simples",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_base_cs_ind13",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_base_cs_tp_valor",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_base_cs_valor",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("calc_terc_tp_cr", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "calc_terc_vr_cs_seg_terc",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "calc_terc_vr_desc_terc",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S5001",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S5002",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_evento_nr_rec_arq_base",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "info_dep_vr_ded_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_irrf_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                ("info_irrf_ind_res_br", models.CharField(max_length=1)),
                ("bases_irrf_tp_valor", models.PositiveIntegerField()),
                (
                    "bases_irrf_valor",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                ("irrf_tp_cr", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "irrf_vr_irrf_desc",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("ide_pais_cod_pais", models.CharField(max_length=3)),
                ("ide_pais_ind_nif", models.PositiveIntegerField()),
                (
                    "ide_pais_nif_benef",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("end_ext_dsc_lograd", models.CharField(max_length=80)),
                (
                    "end_ext_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "end_ext_complem",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "end_ext_bairro",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("end_ext_nm_cid", models.CharField(max_length=50)),
                (
                    "end_ext_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S5002",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S5011",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "info_cs_nr_rec_arq_base",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("info_cs_ind_exist_info", models.PositiveIntegerField()),
                (
                    "info_cp_seg_vr_desc_cp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cp_seg_vr_cp_seg",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("info_contrib_class_trib", models.CharField(max_length=2)),
                (
                    "info_pj_ind_coop",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_pj_ind_constr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_pj_ind_subst_patr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_pj_perc_red_contrib",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_at_conc_fator_mes",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "info_at_conc_fator13",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_estab_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_estab_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "info_estab_cnae_prep",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estab_aliq_rat",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estab_fap",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "info_estab_aliq_rat_ajust",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "info_compl_obra_ind_subst_patr_obra",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_lotacao_cod_lotacao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_lotacao_fpas",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_lotacao_cod_tercs",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "ide_lotacao_cod_tercs_susp",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_terc_susp_cod_terc",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_empr_parcial_tp_insc_contrat",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_empr_parcial_nr_insc_contrat",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "info_empr_parcial_tp_insc_prop",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_empr_parcial_nr_insc_prop",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "dados_op_port_cnpj_op_portuario",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "dados_op_port_aliq_rat",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "dados_op_port_fap",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "dados_op_port_aliq_rat_ajust",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=4, blank=True
                    ),
                ),
                (
                    "bases_remun_ind_incid",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "bases_remun_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "bases_cp_vr_bc_cp00",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_bc_cp15",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_bc_cp20",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_bc_cp25",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_susp_bc_cp00",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_susp_bc_cp15",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_susp_bc_cp20",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_susp_bc_cp25",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_desc_sest",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_calc_sest",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_desc_senat",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_calc_senat",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_sal_fam",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_cp_vr_sal_mat",
                    models.DecimalField(max_digits=14, decimal_places=2),
                ),
                (
                    "bases_av_n_port_vr_bc_cp00",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_bc_cp15",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_bc_cp20",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_bc_cp25",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_bc_cp13",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_bc_fgts",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_av_n_port_vr_desc_cp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_subst_patr_op_port_cnpj_op_portuario",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "bases_aquis_ind_aquis",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "bases_aquis_vlr_aquis",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_cp_desc_pr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_cpn_ret",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_rat_n_ret",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_senar_n_ret",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_cp_calc_pr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_rat_desc_pr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_rat_calc_pr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_senar_desc",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_aquis_vr_senar_calc",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_comerc_ind_comerc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "bases_comerc_vr_bc_com_pr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_comerc_vr_cp_susp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_comerc_vr_rat_susp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "bases_comerc_vr_senar_susp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cr_estab_tp_cr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cr_estab_vr_cr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cr_estab_vr_susp_cr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cr_contrib_tp_cr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cr_contrib_vr_cr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_cr_contrib_vr_cr_susp",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S5011",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S5012",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "info_irrf_nr_rec_arq_base",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("info_irrf_ind_exist_info", models.PositiveIntegerField()),
                (
                    "info_cr_contrib_tp_cr",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_cr_contrib_vr_cr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_empregador",
                    models.ForeignKey(
                        related_name="register_S5012",
                        to="esocial.IdeEmployer",
                        max_length=1,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("esocial.event",),
        ),
        migrations.AddField(
            model_name="returnresult",
            name="event",
            field=models.ForeignKey(
                related_name="results",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="esocial.Event",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="returnresult",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="occurrence",
            name="result",
            field=models.ForeignKey(
                related_name="ocurrences",
                to="esocial.ReturnResult",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="event",
            name="batches",
            field=models.ManyToManyField(
                related_name="events", verbose_name="Lotes", to="esocial.BatchEvent"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="dependencies",
            field=models.ManyToManyField(related_name="dependents", to="esocial.Event"),
        ),
        migrations.AddField(
            model_name="event",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="previous_event",
            field=models.OneToOneField(
                related_name="next_event",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="esocial.Event",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="rectified_register",
            field=models.ForeignKey(
                blank=True, to="esocial.Event", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="event",
            name="validator",
            field=models.ForeignKey(
                related_name="validator",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="standard.ClassCode",
                null=True,
            ),
        ),
    ]
