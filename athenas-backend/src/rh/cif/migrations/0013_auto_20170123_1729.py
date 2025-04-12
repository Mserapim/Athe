# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0012_attachment_member"),
    ]

    operations = [
        migrations.AddField(
            model_name="controlinformationmember",
            name="pendency_address",
            field=models.BooleanField(
                default=False, verbose_name="Pend\xeancia em endere\xe7o"
            ),
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="pendency_debts",
            field=models.BooleanField(
                default=False, verbose_name="Pend\xeancia em debitos"
            ),
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="pendency_property",
            field=models.BooleanField(
                default=False, verbose_name="Pend\xeancia em bens"
            ),
        ),
        migrations.AddField(
            model_name="controlinformationmember",
            name="pendency_teaching",
            field=models.BooleanField(
                default=False, verbose_name="Pend\xeancia em doc\xeancia"
            ),
        ),
    ]
