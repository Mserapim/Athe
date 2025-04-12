# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Application",
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
                ("icon", models.CharField(max_length=260, null=True, blank=True)),
                ("title", models.CharField(max_length=50, verbose_name="T\xedtulo")),
                ("active", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "uuid",
                    models.CharField(
                        null=True,
                        max_length=32,
                        blank=True,
                        unique=True,
                        verbose_name="UUID",
                        db_index=True,
                    ),
                ),
            ],
            options={
                "ordering": ["-father__title", "title"],
            },
            bases=(models.Model, standard.models.AuditableMixins),
        ),
        migrations.CreateModel(
            name="Controller",
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
                ("icon", models.CharField(max_length=260, null=True, blank=True)),
                ("title", models.CharField(max_length=50, verbose_name="T\xedtulo")),
                (
                    "controller",
                    models.CharField(max_length=50, verbose_name="Controlador"),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "module",
                    models.CharField(
                        blank=True,
                        max_length=256,
                        null=True,
                        verbose_name="Modulo",
                        choices=[
                            ("django.contrib.auth", "django.contrib.auth"),
                            (
                                "django.contrib.contenttypes",
                                "django.contrib.contenttypes",
                            ),
                            ("django.contrib.sessions", "django.contrib.sessions"),
                            ("django.contrib.sites", "django.contrib.sites"),
                            ("auditoria", "auditoria"),
                            ("engine", "engine"),
                            ("engine.notification", "engine.notification"),
                            ("standard", "standard"),
                            ("edocs.protocolo", "edocs.protocolo"),
                            ("edocs.processo", "edocs.processo"),
                            ("common.mailing", "common.mailing"),
                            ("common.poll", "common.poll"),
                            ("default", "default"),
                            ("rh", "rh"),
                            ("ged", "ged"),
                            ("rh.gfp", "rh.gfp"),
                            ("rh.gfp.dirf", "rh.gfp.dirf"),
                            ("rh.gfp.planoconta", "rh.gfp.planoconta"),
                            ("rh.ferias", "rh.ferias"),
                            ("rh.afastamento", "rh.afastamento"),
                            ("rh.estagio", "rh.estagio"),
                            ("rh.profile", "rh.profile"),
                            ("planejamento.pe", "planejamento.pe"),
                            ("standard.questionario", "standard.questionario"),
                            ("rh.ponto", "rh.ponto"),
                            ("web", "web"),
                            ("web.ouvidoria", "web.ouvidoria"),
                            ("planejamento.contrato", "planejamento.contrato"),
                            ("cesaf.gecap", "cesaf.gecap"),
                            ("cesaf.concurso", "cesaf.concurso"),
                            ("rh.pensao", "rh.pensao"),
                            ("bi", "bi"),
                            ("adm.mto", "adm.mto"),
                            ("adm.eproc", "adm.eproc"),
                            ("adm.compras", "adm.compras"),
                            ("adm.cpl", "adm.cpl"),
                            ("adm.contabilidade", "adm.contabilidade"),
                            ("adm.diarias", "adm.diarias"),
                            ("workflow", "workflow"),
                            ("adm.patrimonio", "adm.patrimonio"),
                            ("common.siatu", "common.siatu"),
                        ],
                    ),
                ),
                (
                    "uuid",
                    models.CharField(
                        null=True,
                        max_length=32,
                        blank=True,
                        unique=True,
                        verbose_name="UUID",
                        db_index=True,
                    ),
                ),
            ],
            options={
                "ordering": ("application", "controller"),
            },
            bases=(models.Model, standard.models.AuditableMixins),
        ),
        migrations.CreateModel(
            name="ControllerContentType",
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
                    "priority",
                    models.SmallIntegerField(
                        default=0, choices=[(0, "Baixa"), (1, "Alta")]
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ControllerPermission",
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
                ("name", models.CharField(max_length=60, verbose_name="Nome")),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Evento",
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
                ("title", models.CharField(max_length=100)),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField(null=True)),
                ("resource", models.CharField(max_length=200)),
                ("interface", models.CharField(max_length=200)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LDAPServer",
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
                ("address", models.IPAddressField(verbose_name="Endere\xe7o")),
                ("port", models.PositiveIntegerField(verbose_name="Porta")),
                ("dn", models.CharField(max_length=60)),
                ("basedn", models.CharField(max_length=60)),
                ("admin_user", models.CharField(max_length=60)),
                ("admin_password", models.CharField(max_length=60)),
                ("user_object", models.CharField(max_length=60)),
                (
                    "priority",
                    models.PositiveIntegerField(
                        verbose_name="Prioridade",
                        choices=[
                            (0, "Muito baixa"),
                            (2, "Baixa"),
                            (5, "Moderada"),
                            (7, "Moderada a alta"),
                            (9, "Alta"),
                        ],
                    ),
                ),
                ("tls", models.BooleanField(default=False, verbose_name="Com TLS")),
                ("falt", models.BooleanField(default=False, verbose_name="Em falta")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LDAPServerFault",
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
                ("moment", models.DateTimeField(auto_now=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TaskMessages",
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
                ("message", models.CharField(max_length=400, verbose_name="Message")),
                (
                    "type_of",
                    models.PositiveSmallIntegerField(
                        default=1,
                        db_index=True,
                        verbose_name="Type",
                        choices=[(1, "INFO"), (2, "WARN"), (3, "ERROR"), (4, "FILE")],
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "db_table": "eng_taskmessages",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TaskSession",
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
                    "sid",
                    models.CharField(max_length=32, verbose_name="SID", db_index=True),
                ),
                (
                    "description",
                    models.CharField(max_length=255, verbose_name="Description"),
                ),
                (
                    "params_cache",
                    models.CharField(
                        default="{}", max_length=400, verbose_name="Params"
                    ),
                ),
                (
                    "started_task",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Started", db_index=True
                    ),
                ),
                (
                    "finished_task",
                    models.DateTimeField(
                        null=True, verbose_name="Finished", db_index=True
                    ),
                ),
                (
                    "visualized",
                    models.BooleanField(default=False, verbose_name="Visualized"),
                ),
                (
                    "status",
                    models.CharField(
                        default="RUNNING",
                        max_length=16,
                        verbose_name="Status",
                        db_index=True,
                        choices=[
                            ("RUNNING", "Executando"),
                            ("STOPED", "Interrompida pelo usu\xe1rio"),
                            ("SUCCESS", "Finalizada com sucesso"),
                            ("ERROR", "Erro na execu\xe7\xe3o"),
                        ],
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        verbose_name="Users",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("started_task",),
                "db_table": "eng_tasksession",
            },
            bases=(models.Model,),
        ),
    ]
