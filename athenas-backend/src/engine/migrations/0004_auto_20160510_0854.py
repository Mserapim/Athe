# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engine", "0003_auto_20151105_0851"),
    ]

    operations = [
        migrations.AlterField(
            model_name="controller",
            name="module",
            field=models.CharField(
                blank=True,
                max_length=256,
                null=True,
                verbose_name="Modulo",
                choices=[
                    ("django.contrib.auth", "django.contrib.auth"),
                    ("django.contrib.contenttypes", "django.contrib.contenttypes"),
                    ("django.contrib.sessions", "django.contrib.sessions"),
                    ("django.contrib.sites", "django.contrib.sites"),
                    ("auth.ws", "auth.ws"),
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
                    ("rh.socialsecurity", "rh.socialsecurity"),
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
                    ("common.saci", "common.saci"),
                    ("common.official_journal", "common.official_journal"),
                    ("engine.mq", "engine.mq"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="ldapserver",
            name="address",
            field=models.CharField(max_length=15, verbose_name="Endere\xe7o"),
        ),
        migrations.AlterField(
            model_name="tasksession",
            name="status",
            field=models.CharField(
                default="RUNNING",
                max_length=16,
                verbose_name="Status",
                db_index=True,
                choices=[
                    ("ABORTED", "Abortado"),
                    ("RUNNING", "Executando"),
                    ("STOPED", "Interrompida pelo usu\xe1rio"),
                    ("SUCCESS", "Finalizada com sucesso"),
                    ("ERROR", "Erro na execu\xe7\xe3o"),
                ],
            ),
        ),
    ]
