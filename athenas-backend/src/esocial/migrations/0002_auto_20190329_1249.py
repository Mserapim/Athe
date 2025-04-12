# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import migrations, models

import datetime
import standard.models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("esocial", "0001_squashed_0004_auto_20190107_1810"),
        ("standard", "0011_auto_20190130_1128"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BatchEvent",
        ),
        migrations.DeleteModel(
            name="Dependent",
        ),
        migrations.DeleteModel(
            name="Event",
        ),
        migrations.DeleteModel(
            name="IdeEmployer",
        ),
        migrations.DeleteModel(
            name="IdeProcesso",
        ),
        migrations.DeleteModel(
            name="IdeTransmitter",
        ),
        migrations.DeleteModel(
            name="InfoSuspensao",
        ),
        migrations.DeleteModel(
            name="Occurrence",
        ),
        migrations.DeleteModel(
            name="Process",
        ),
        migrations.DeleteModel(
            name="ProcJudTerceiro",
        ),
        migrations.DeleteModel(
            name="ReturnResult",
        ),
        migrations.DeleteModel(
            name="S1000",
        ),
        migrations.DeleteModel(
            name="S1005",
        ),
        migrations.DeleteModel(
            name="S1010",
        ),
        migrations.DeleteModel(
            name="S1020",
        ),
        migrations.DeleteModel(
            name="S1030",
        ),
        migrations.DeleteModel(
            name="S1035",
        ),
        migrations.DeleteModel(
            name="S1040",
        ),
        migrations.DeleteModel(
            name="S1050",
        ),
        migrations.DeleteModel(
            name="S1060",
        ),
        migrations.DeleteModel(
            name="S1070",
        ),
        migrations.DeleteModel(
            name="S1200",
        ),
        migrations.DeleteModel(
            name="S1202",
        ),
        migrations.DeleteModel(
            name="S1207",
        ),
        migrations.DeleteModel(
            name="S1210",
        ),
        migrations.DeleteModel(
            name="S1280",
        ),
        migrations.DeleteModel(
            name="S1298",
        ),
        migrations.DeleteModel(
            name="S1299",
        ),
        migrations.DeleteModel(
            name="S1300",
        ),
        migrations.DeleteModel(
            name="S2100",
        ),
        migrations.DeleteModel(
            name="S2190",
        ),
        migrations.DeleteModel(
            name="S2200",
        ),
        migrations.DeleteModel(
            name="S2205",
        ),
        migrations.DeleteModel(
            name="S2206",
        ),
        migrations.DeleteModel(
            name="S2210",
        ),
        migrations.DeleteModel(
            name="S2220",
        ),
        migrations.DeleteModel(
            name="S2230",
        ),
        migrations.DeleteModel(
            name="S2240",
        ),
        migrations.DeleteModel(
            name="S2241",
        ),
        migrations.DeleteModel(
            name="S2298",
        ),
        migrations.DeleteModel(
            name="S2299",
        ),
        migrations.DeleteModel(
            name="S2300",
        ),
        migrations.DeleteModel(
            name="S2306",
        ),
        migrations.DeleteModel(
            name="S2399",
        ),
        migrations.DeleteModel(
            name="S2400",
        ),
        migrations.DeleteModel(
            name="S3000",
        ),
        migrations.DeleteModel(
            name="S5001",
        ),
        migrations.DeleteModel(
            name="S5002",
        ),
        migrations.DeleteModel(
            name="S5011",
        ),
        migrations.DeleteModel(
            name="S5012",
        ),
        migrations.DeleteModel(
            name="Schedule",
        ),
        migrations.DeleteModel(
            name="WorkHourInterval",
        ),
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
                (
                    "search_cache",
                    models.CharField(default="", max_length=255, blank=True),
                ),
                (
                    "internal",
                    models.BooleanField(default=False, verbose_name="Indireto"),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=(standard.models.AuditableMixins, models.Model),
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
                    models.TextField(
                        default="", verbose_name="Descri\xe7\xe3o", blank=True
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
            name="Dependent",
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
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="HealthCertificate",
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
                (
                    "info_atestado_cod_cid",
                    models.CharField(max_length=4, null=True, blank=True),
                ),
                (
                    "info_atestado_qtd_dias_afast",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "emitente_nm_emit",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("emitente_ide_oc", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "emitente_nr_oc",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "emitente_uf_oc",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="IdeProcesso",
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
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="InfoSuspensao",
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
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="Process",
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
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="ProcJudTerceiro",
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
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
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
                (
                    "info_cadastro_ind_opc_cp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
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
                        related_name="ide_processo_cp_register_S1010",
                        to="esocial.IdeProcesso",
                    ),
                ),
                (
                    "ide_processo_fgts",
                    models.ManyToManyField(
                        related_name="ide_processo_fgts_register_S1010",
                        to="esocial.IdeProcesso",
                    ),
                ),
                (
                    "ide_processo_irrf",
                    models.ManyToManyField(
                        related_name="ide_processo_irrf_register_S1010",
                        to="esocial.IdeProcesso",
                    ),
                ),
                (
                    "ide_processo_sind",
                    models.ManyToManyField(
                        related_name="ide_processo_sind_register_S1010",
                        to="esocial.IdeProcesso",
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
                        related_name="proc_jud_terceiro_register_S1020",
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
                (
                    "lei_cargo_nr_lei",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                ("lei_cargo_dt_lei", models.DateField(null=True, blank=True)),
                (
                    "lei_cargo_sit_cargo",
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    "duracao_clau_assec",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "duracao_obj_det",
                    models.CharField(max_length=255, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    "sucessao_vinc_tp_insc_ant",
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
                (
                    "mudanca_cpf_cpf_ant",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "mudanca_cpf_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("mudanca_cpf_dt_alt_cpf", models.DateField(null=True, blank=True)),
                (
                    "mudanca_cpf_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("afastamento_dt_ini_afast", models.DateField(null=True, blank=True)),
                (
                    "afastamento_cod_mot_afast",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("desligamento_dt_deslig", models.DateField(null=True, blank=True)),
                (
                    "dependente",
                    models.ManyToManyField(
                        related_name="dependente_register_S2200", to="esocial.Dependent"
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                (
                    "dependente",
                    models.ManyToManyField(
                        related_name="dependente_register_s2205", to="esocial.Dependent"
                    ),
                ),
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
                    "duracao_obj_det",
                    models.CharField(max_length=255, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    models.CharField(max_length=21, null=True, blank=True),
                ),
                (
                    "fim_afastamento_dt_term_afast",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "info_atestado",
                    models.ManyToManyField(
                        related_name="S2230", to="esocial.HealthCertificate"
                    ),
                ),
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
                    "info_deslig_qtd_dias_interm",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "observacoes_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_tp_insc_suc",
                    models.PositiveIntegerField(null=True, blank=True),
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
                (
                    "mudanca_cpf_novo_cpf",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "dm_dev_ide_dm_dev",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_estab_lot_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_estab_lot_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "ide_estab_lot_cod_lotacao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "det_verbas_cod_rubr",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "det_verbas_ide_tab_rubr",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
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
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_oper_cnpj_oper",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "det_oper_reg_ans",
                    models.CharField(max_length=6, null=True, blank=True),
                ),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
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
                ("ide_adc_dt_ac_conv", models.DateField(null=True, blank=True)),
                (
                    "ide_adc_tp_ac_conv",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "ide_adc_comp_ac_conv",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("ide_adc_dt_ef_ac_conv", models.DateField(null=True, blank=True)),
                (
                    "ide_adc_dsc",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "ide_periodo_per_ref",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "ide_periodo_ide_estab_lot_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_periodo_ide_estab_lot_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "ide_periodo_ide_estab_lot_cod_lotacao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_estab_lot_det_verbas_cod_rubr",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "ide_estab_lot_det_verbas_ide_tab_rubr",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "ide_estab_lot_det_verbas_qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_estab_lot_det_verbas_fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_estab_lot_det_verbas_vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_estab_lot_det_verbas_vr_rubr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_estab_lot_info_ag_nocivo_grau_exp",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_estab_lot_info_simples_ind_simples",
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
                (
                    "remun_outr_empr_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "remun_outr_empr_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "proc_cs_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("quarentena_dt_fim_quar", models.DateField(null=True, blank=True)),
                (
                    "consig_fgts_ins_consig",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "consig_fgts_nr_contr",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
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
                    models.CharField(max_length=90, null=True, blank=True),
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
                    "info_tsv_inicio_cad_ini",
                    models.CharField(default="S", max_length=1),
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
                (
                    "inst_ensino_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "inst_ensino_dsc_lograd",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "inst_ensino_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "inst_ensino_bairro",
                    models.CharField(max_length=90, null=True, blank=True),
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
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "age_integracao_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "age_integracao_bairro",
                    models.CharField(max_length=90, null=True, blank=True),
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
                    "mudanca_cpf_cpf_ant",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("mudanca_cpf_dt_alt_cpf", models.DateField(null=True, blank=True)),
                (
                    "mudanca_cpf_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("afastamento_dt_ini_afast", models.DateField(null=True, blank=True)),
                (
                    "afastamento_cod_mot_afast",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                ("termino_dt_term", models.DateField(null=True, blank=True)),
                (
                    "dependente",
                    models.ManyToManyField(
                        related_name="register_S2300", to="esocial.Dependent"
                    ),
                ),
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
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="Schedule",
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
                ("horario_dia", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "horario_cod_hor_contrat",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="WorkHourInterval",
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
            ],
            options={
                "abstract": False,
            },
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
        migrations.AddField(
            model_name="s2206",
            name="horario",
            field=models.ManyToManyField(
                related_name="horario_register_s2206", to="esocial.Schedule"
            ),
        ),
        migrations.AddField(
            model_name="s2200",
            name="horario",
            field=models.ManyToManyField(
                related_name="horario_register_S2200", to="esocial.Schedule"
            ),
        ),
        migrations.AddField(
            model_name="s1050",
            name="horario_intervalo",
            field=models.ManyToManyField(
                related_name="horario_intervalo_register_S1050",
                to="esocial.WorkHourInterval",
            ),
        ),
        migrations.AddField(
            model_name="configuration",
            name="initial_date_non_periodic_events",
            field=models.DateField(
                default=datetime.datetime(2017, 3, 1, 13, 15, 51, 848363),
                verbose_name="In\xedcio - N\xe3o peri\xf3dicos",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="configuration",
            name="initial_date_periodic_events",
            field=models.DateField(
                default=datetime.datetime(2017, 5, 1, 13, 15, 55, 557495),
                verbose_name="In\xedcio - Peri\xf3dicos",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="configuration",
            name="initial_date_start_tables",
            field=models.DateField(
                default=datetime.datetime(2017, 1, 1, 13, 16, 0, 676830),
                verbose_name="In\xedcio - Tabelas iniciais",
            ),
            preserve_default=False,
        ),
    ]
