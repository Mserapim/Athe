# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def migrate_fields(apps, schema_editor):
    from rh.gfp.models import PaycheckDifference

    FolhaEvento = apps.get_model("gfp", "FolhaEvento")
    PaycheckDifferenceItem = apps.get_model("gfp", "PaycheckDifferenceItem")
    # PaycheckDifference = apps.get_model("gfp", "PaycheckDifference")

    FolhaEvento.objects.update(
        correct_valor=models.F("correct_value"),
        correct_patronal=models.F("correct_employer_contribution"),
        diff_valor_aprovisionado=models.F("diff_value_provisioned"),
        diff_patronal_aprovisionado=models.F("diff_employer_contribution_provisioned"),
    )

    FolhaEvento.objects.filter(evento__tipo="D").update(
        correct_value=models.F("correct_value") * -1,
        diff_value_provisioned=models.F("diff_value_provisioned") * -1,
    )
    PaycheckDifferenceItem.objects.filter(entry_difference__evento__tipo="D").update(
        value=models.F("value") * -1, fixed_value=models.F("fixed_value") * -1
    )
    PaycheckDifferenceItem.objects.filter(
        ~models.Q(employer_contribution=0) & models.Q(fixed_employer_contribution=0)
    ).update(fixed_employer_contribution=models.F("employer_contribution"))

    if settings.ORGAN_IDENTIFIER == "mpto":
        PaycheckDifference.objects.filter(
            identifier__in=[
                "885cc52c60c24286997fae5b8ea40dfc",
                "c45e6c5287414ccf8d3ac313eb672ecf",
            ]
        ).update(diff_type="DEV", status=2)

    print("UPDATING DIFFERENCES...")
    for pd in PaycheckDifference.objects.exclude(status__in=[6]):
        if pd.difference_items.exists():
            #  totals_di = pd.difference_items.aggregate(value=models.Sum('fixed_value'), employer_contribution=models.Sum('fixed_employer_contribution'))
            pd.total_value = 0
            pd.total_employer_contribution = 0
        pd.save()
        if not pd.entries_payment.exists():
            pd.delete()
        elif pd.status not in [4, 5]:
            print(pd.payable, pd.get_status_display(), pd)
    print("OK")

    if settings.ORGAN_IDENTIFIER == "mpto":
        print("UPDATING DIFFERENCES FOR EVENT 51500...")
        for fe in FolhaEvento.objects.filter(evento__numero="51500").exclude(
            paycheck_difference__isnull=True
        ):
            pd = fe.paycheck_difference
            pd.difference_items.update(
                employer_contribution=0, fixed_employer_contribution=0
            )
            pd.save()
        print("OK")


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0041_auto_20170721_1204"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="cid",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="correct_patronal",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="correct_valor",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="diff_patronal_aprovisionado",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhaevento",
            name="diff_valor_aprovisionado",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="calculo",
            field=models.ForeignKey(
                related_name="eventos",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="C\xe1lculo",
                blank=True,
                to="standard.ClassCode",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="correct_value",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.RunPython(migrate_fields, _null_function),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
