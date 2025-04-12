# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("engine", "0004_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="application",
            options={"ordering": ["layer", "title"]},
        ),
        migrations.AddField(
            model_name="application",
            name="layer",
            field=models.PositiveSmallIntegerField(default=1, blank=True),
        ),
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
                    ("django.contrib.admin", "django.contrib.admin"),
                    ("django.contrib.humanize", "django.contrib.humanize"),
                    ("auth.ws", "auth.ws"),
                    ("auditoria", "auditoria"),
                    ("engine", "engine"),
                    ("engine.notification", "engine.notification"),
                    ("engine.mq", "engine.mq"),
                    ("standard", "standard"),
                    ("edocs.protocolo", "edocs.protocolo"),
                    ("edocs.processo", "edocs.processo"),
                    ("common.mailing", "common.mailing"),
                    ("common.poll", "common.poll"),
                    ("common.official_journal", "common.official_journal"),
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
                    ("rh.socialsecurity", "rh.socialsecurity"),
                    ("web", "web"),
                    ("web.ouvidoria", "web.ouvidoria"),
                    ("planejamento.contrato", "planejamento.contrato"),
                    ("cesaf.gecap", "cesaf.gecap"),
                    ("cesaf.concurso", "cesaf.concurso"),
                    ("rh.pensao", "rh.pensao"),
                    ("bi", "bi"),
                    ("rh.cif", "rh.cif"),
                    ("rh.scmmp", "rh.scmmp"),
                    ("rh.apd", "rh.apd"),
                    ("adm.cpl", "adm.cpl"),
                    ("adm.contabilidade", "adm.contabilidade"),
                    ("adm.diarias", "adm.diarias"),
                    ("workflow", "workflow"),
                    ("adm.compras", "adm.compras"),
                    ("adm.mto", "adm.mto"),
                    ("adm.eproc", "adm.eproc"),
                    ("adm.patrimonio", "adm.patrimonio"),
                    ("common.siatu", "common.siatu"),
                    ("common.saci", "common.saci"),
                    ("common.util", "common.util"),
                    ("judicial", "judicial"),
                    ("judicial.tac", "judicial.tac"),
                    ("judicial.council", "judicial.council"),
                ],
            ),
        ),
    ]
