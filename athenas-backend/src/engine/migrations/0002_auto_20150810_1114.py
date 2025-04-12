# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0001_initial"),
        ("engine", "0001_initial"),
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskmessages",
            name="file_ged",
            field=models.ForeignKey(
                related_name="tasks_messages",
                verbose_name="Arquivo",
                blank=True,
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),  # Parametro "on_delete" adicionado. (Django 2)
        migrations.AddField(
            model_name="taskmessages",
            name="session",
            field=models.ForeignKey(
                related_name="messages",
                verbose_name="Session",
                to="engine.TaskSession",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ldapserverfault",
            name="server",
            field=models.ForeignKey(
                to="engine.LDAPServer", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controllerpermission",
            name="controllers",
            field=models.ManyToManyField(
                related_name="controller_permissions",
                verbose_name="Funcionalidades",
                to="engine.Controller",
                blank=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controllerpermission",
            name="users",
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, verbose_name="Usu\xe1rios", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controllercontenttype",
            name="content_type",
            field=models.ForeignKey(
                to="contenttypes.ContentType", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="controllercontenttype",
            name="controller",
            field=models.ForeignKey(
                to="engine.Controller", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="controllercontenttype",
            unique_together=set([("controller", "content_type")]),
        ),
        migrations.AddField(
            model_name="controller",
            name="application",
            field=models.ForeignKey(
                verbose_name="Grupo de Funcionalidade",
                to="engine.Application",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="application",
            name="father",
            field=models.ForeignKey(
                verbose_name="Grupo de Funcionalidade",
                blank=True,
                to="engine.Application",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="application",
            unique_together=set([("title", "father")]),
        ),
    ]
