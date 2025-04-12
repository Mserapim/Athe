# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='PasswordChangeRequest',
        #     fields=[
        #         ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
        #         ('key', models.CharField(max_length=64, db_index=True)),
        #         ('valid', models.BooleanField(default=True, db_index=True)),
        #         ('user', models.ForeignKey(related_name='password_change_requests', to='web.RegularWebUser', null=True, on_delete=models.CASCADE)), # Parametro "on_delete" adicionado. (Django 2)
        #     ],
        #     options={
        #     },
        #     bases=(models.Model,),
        # ),
        migrations.AddField(
            model_name="regularwebuser",
            name="email",
            field=models.EmailField(max_length=75, null=True),
            preserve_default=True,
        ),
    ]
