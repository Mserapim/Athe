# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0041_remove_replacement"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="judicialdiligence",
            options={
                "ordering": ("diligence_year", "diligence_number", "-delivery_status"),
                "permissions": (
                    ("admin_dilig", "Vis\xe3o Administrador"),
                    ("manager_dilig", "Vis\xe3o Central de Dilig\xeancias"),
                    ("oficial_dilig", "Vis\xe3o Oficial de Diligencias"),
                    ("promotor_dilig", "Vis\xe3o Promotor"),
                ),
            },
        ),
        migrations.AddField(
            model_name="executionorgan",
            name="attribution",
            field=models.CharField(db_index=True, max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="cause",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="attacheddocument",
            name="attached_type",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="dearchivingdispatch",
            name="dearchiving_type",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="delivered",
            field=models.SmallIntegerField(
                null=True,
                verbose_name="a diligencia foi entregue ao destinatario ou nao",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="type_vehicle",
            field=models.SmallIntegerField(
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="dilationperiod",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                null=True, verbose_name="Tipo do Processo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1, null=True, verbose_name="status da entrega", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="glosary",
            name="classification_type",
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="who_type",
            field=models.SmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="manifestation",
            name="who_type",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="officerdiligence",
            name="status",
            field=models.SmallIntegerField(default=1, null=True),
        ),
        migrations.AlterField(
            model_name="ordinace",
            name="type_ordinace",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="ordinacereformulated",
            name="type_ordinace",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="external_locations",
            field=models.ManyToManyField(
                related_name="in_lawsuit_as_external", to="rh.OrgaoGeral"
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="type_lawsuit",
            field=models.SmallIntegerField(default=1, verbose_name="Tipo do Processo"),
        ),
        migrations.AlterField(
            model_name="partlawsuitaccess",
            name="motivation",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="personhasaccess",
            name="state",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="decision_type",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="rejection_fact_type",
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="type_ordinace",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="incident",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="incident_type",
            field=models.SmallIntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name="workerreminder",
            name="priority",
            field=models.SmallIntegerField(),
        ),
    ]
