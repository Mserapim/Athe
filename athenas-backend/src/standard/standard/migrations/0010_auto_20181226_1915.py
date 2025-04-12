# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_configuration(apps, schema_editor):
    Item = apps.get_model("standard", "Item")
    for i in Item.objects.all():
        config = i.configs.first()
        i.configuration = config
        if i.type_of == 0:
            i.type_of = 3
        i.save()
    # upsp = FolhaEvento.objects.exclude(base_previdencia=0).filter(evento__tipo='P').update(correct_contribution_base=models.F('base_previdencia'), correct_base_previdencia=models.F('base_previdencia'))
    # upsd = FolhaEvento.objects.exclude(base_previdencia=0).filter(evento__tipo='D').update(correct_contribution_base=models.F('base_previdencia')*-1, correct_base_previdencia=models.F('base_previdencia'))

    # print 'BASE_PREVIDENCIAS UPDATEDS: P(%s) D(%s)' % (upsp, upsd),


def migrate_cvalue_choices(apps, schema_editor):
    Choice = apps.get_model("standard", "Choice")
    Choice.objects.filter(cvalue="").update(cvalue=models.F("value"))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0009_auto_20181207_1543"),
    ]

    operations = [
        migrations.RunPython(migrate_cvalue_choices, _null_function),
        migrations.RenameField(
            model_name="item",
            old_name="type",
            new_name="type_of",
        ),
        migrations.AlterModelOptions(
            name="item",
            options={"ordering": ("configuration", "key")},
        ),
        migrations.AddField(
            model_name="item",
            name="configuration",
            field=models.ForeignKey(
                related_name="items",
                default=1,
                verbose_name="Configura\xe7\xe3o",
                to="standard.Configuration",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="configuration",
            name="itens",
            field=models.ManyToManyField(related_name="configs", to="standard.Item"),
        ),
        migrations.AlterUniqueTogether(
            name="choice",
            unique_together=set(
                [
                    ("app_label", "name", "value"),
                    ("app_label", "name", "label"),
                    ("app_label", "name", "cvalue"),
                ]
            ),
        ),
        migrations.RunPython(migrate_configuration, _null_function),
        migrations.AlterUniqueTogether(
            name="item",
            unique_together=set([("configuration", "key")]),
        ),
    ]
