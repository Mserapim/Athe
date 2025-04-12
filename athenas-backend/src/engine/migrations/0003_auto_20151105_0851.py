# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("engine", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="tasksession",
            name="starter_id",
            field=models.CharField(max_length=20, null=True, verbose_name="Starter ID"),
            preserve_default=True,
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
                    ("django.contrib.admin", "django.contrib.admin"),
                    ("django.contrib.auth", "django.contrib.auth"),
                    ("django.contrib.contenttypes", "django.contrib.contenttypes"),
                    ("django.contrib.sessions", "django.contrib.sessions"),
                    ("django.contrib.messages", "django.contrib.messages"),
                    ("django.contrib.staticfiles", "django.contrib.staticfiles"),
                    ("engine", "engine"),
                    ("engine.notification", "engine.notification"),
                    ("auditoria", "auditoria"),
                    ("standard", "standard"),
                    ("default", "default"),
                    ("workflow", "workflow"),
                    ("rh", "rh"),
                    ("rh.afastamento", "rh.afastamento"),
                    ("rh.servidor", "rh.servidor"),
                    ("rh.gfp", "rh.gfp"),
                    ("rh.gfp.dirf", "rh.gfp.dirf"),
                    ("rh.gfp.planoconta", "rh.gfp.planoconta"),
                    ("rh.ponto", "rh.ponto"),
                    ("rh.ferias", "rh.ferias"),
                    ("rh.pensao", "rh.pensao"),
                    ("rh.estagio", "rh.estagio"),
                    ("rh.profile", "rh.profile"),
                    ("cesaf.gecap", "cesaf.gecap"),
                    ("cesaf.concurso", "cesaf.concurso"),
                    ("ged", "ged"),
                    ("planejamento.pe", "planejamento.pe"),
                    ("edocs.protocolo", "edocs.protocolo"),
                    ("edocs.processo", "edocs.processo"),
                    ("planejamento.contrato", "planejamento.contrato"),
                    ("adm.compras", "adm.compras"),
                    ("adm.contabilidade", "adm.contabilidade"),
                    ("adm.eproc", "adm.eproc"),
                    ("adm.mto", "adm.mto"),
                    ("adm.cpl", "adm.cpl"),
                    ("adm.diarias", "adm.diarias"),
                    ("web", "web"),
                    ("common.poll", "common.poll"),
                    ("standard.questionario", "standard.questionario"),
                    ("adm.patrimonio", "adm.patrimonio"),
                    ("common.siatu", "common.siatu"),
                    ("common.mailing", "common.mailing"),
                ],
            ),
            preserve_default=True,
        ),
    ]
