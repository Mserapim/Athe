# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prontuary", "0007_auto_20181130_1431"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="detailcoursesparticipation",
            options={
                "ordering": ["used_edital", "course_level", "-date_course"],
                "verbose_name": "Cursos registrados para o membro",
            },
        ),
        migrations.RenameField(
            model_name="detailadministrativefunction",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailavailability",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detaildeparture",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detaildesignationcumulation",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailexercise",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailexerciseinrole",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailexoneration",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailjointaction",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailpartieshearings",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailpermutation",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailpromotion",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailpunishment",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailremoval",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailreplacement",
            old_name="act",
            new_name="act_final",
        ),
        migrations.RenameField(
            model_name="detailretirement",
            old_name="act",
            new_name="act_final",
        ),
        migrations.AddField(
            model_name="detailadministrativefunction",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailavailability",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detaildeparture",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detaildesignationcumulation",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailexercise",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailexerciseinrole",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailexoneration",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailjointaction",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailpartieshearings",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailpermutation",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailpromotion",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailpunishment",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailremoval",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailreplacement",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="detailretirement",
            name="act_initial",
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
