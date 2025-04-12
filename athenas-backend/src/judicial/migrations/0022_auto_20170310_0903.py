# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys

from django.db import migrations, models
import standard.models
import judicial.models
import django.db.models.deletion
from django.conf import settings
from django.core.management import call_command
from contrib.middleware import get_current_user, set_current_user


def up_sync_desmemberprocess(apps, schema_editor):
    DismembermentProcess = apps.get_model("judicial.dismembermentprocess")

    print(" ", end="")
    for dp in DismembermentProcess.objects.filter():
        dp.change_title = dp.lawsuit.title
        print("\033[33m+\033[0m", end="")
        for m in dp.lawsuit.matters.filter():
            print("\033[32m+\033[0m", end="")
            dp.matters.add(m)
        dp.save()
        sys.stdout.flush()


def down_sync_desmemberprocess(apps, schema_editor):
    pass


def up_sync_outcourtlawsuit_external_location(apps, schema_editor):
    OutCourtLawsuit = apps.get_model("judicial.OutCourtLawsuit")

    print(" ", end="")
    for lawsuit in OutCourtLawsuit.objects.filter():
        if lawsuit.external_location:
            lawsuit.external_locations.add(lawsuit.external_location)
            print("\033[32m+\033[0m", end="")
        else:
            print("\033[31m.\033[0m", end="")
        sys.stdout.flush()


def down_sync_outcourtlawsuit_external_location(apps, schema_editor):
    pass


def up_sync_remittanceexternal_organ(apps, schema_editor):
    RemittanceExternel = apps.get_model("judicial.RemittanceExternal")

    print(" ", end="")
    for rext in RemittanceExternel.objects.filter():
        if not rext.organs.filter(pk=rext.organ.pk).exists():
            print("\033[32m+\033[0m", end="")
        else:
            print("\033[31m.\033[0m", end="")
        sys.stdout.flush()


def down_sync_remittanceexternal_organ(apps, schema_editor):
    pass


def up_sync_interested(apps, schema_editor):
    from judicial.models import Interested, OutCourtLawsuit

    print(" ", end="")
    for lawsuit in OutCourtLawsuit.objects.filter():
        older_user = get_current_user()
        set_current_user(lawsuit.origin.created_by)
        query = Interested.objects.filter(
            lawsuit=lawsuit, person=lawsuit.origin.interessado
        )

        if not query.exists():
            Interested(
                lawsuit=lawsuit, person=lawsuit.origin.interessado, direct=True
            ).save()
            print("\033[32m+\033[0m", end="")
        else:
            print("\033[31m.\033[0m", end="")

        set_current_user(older_user)


def down_sync_interested(apps, schema_editor):
    pass


def up_city_locations_sync(apps, schema_editor):
    Lawsuit = apps.get_model("judicial.OutCourtlawsuit")
    TriagePartLocation = apps.get_model("judicial.TriagePartLocation")
    AssessmentNoticeOffice = apps.get_model("judicial.AssessmentNoticeOffice")

    print(" ", end="")
    for part in AssessmentNoticeOffice.objects.filter():
        sys.stdout.flush()
        lawsuit = part.lawsuit
        if not lawsuit.city_locations.filter(pk=part.at_where.pk).exists():
            lawsuit.city_locations.add(part.at_where)
            print("\x1b[32m+\x1b[0m", end="")
        else:
            print("\x1b[31m.\x1b[0m", end="")

    print(" ", end="")
    for obj in TriagePartLocation.objects.filter():
        sys.stdout.flush()
        lawsuit = obj.triagepart.triage.lawsuit
        if not lawsuit.city_locations.filter(pk=obj.location.pk).exists():
            lawsuit.city_locations.add(obj.location)
            print("\x1b[32m+\x1b[0m", end="")
        else:
            print("\x1b[31m.\x1b[0m", end="")


def down_city_locations_sync(apps, schema_editor):
    pass


def up_sync(apps, editor_schema):
    from judicial.models import OutCourtLawsuit, Triage, AssessmentNoticeOffice

    print(" ", end="")
    for triage in Triage.objects.filter():
        lawsuit = triage.lawsuit
        for tp in triage.parts.filter():
            if not lawsuit.matters.filter(pk=tp.matter).exists():
                lawsuit.matters.add(tp.matter)
                print("\x1b[32m+\x1b[0m", end="")
            else:
                print("\x1b[31m.\x1b[0m", end="")
            sys.stdout.flush()

    print(" ", end="")
    for notice in AssessmentNoticeOffice.objects.filter():
        lawsuit = notice.lawsuit
        if not lawsuit.matters.filter(pk=notice.matter).exists():
            lawsuit.matters.add(notice.matter)
            print("\x1b[32m+\x1b[0m", end="")
        else:
            print("\x1b[31m.\x1b[0m", end="")
        sys.stdout.flush()


def down_sync(apps, editor_schema):
    from judicial.models import OutCourtLawsuit

    for l in OutCourtLawsuit.objects.filter():
        l.matters.clear()


def up_type(apps, schema_editor):
    AssessmentNoticeOffice = apps.get_model("judicial", "assessmentnoticeoffice")
    AssessmentNoticeOffice.objects.filter(only_notice=True).update(notice_office_type=2)
    AssessmentNoticeOffice.objects.exclude(only_notice=True).update(
        notice_office_type=1
    )


def down_type(apps, schema_editor):
    AssessmentNoticeOffice = apps.get_model("judicial", "assessmentnoticeoffice")
    AssessmentNoticeOffice.objects.filter(notice_office_type=1).update(
        only_notice=False
    )
    AssessmentNoticeOffice.objects.filter(notice_office_type=2).update(only_notice=True)


def up_lf(apps, editor_schema):
    call_command("loaddata", "judicial/fixtures/0022-tipodocumento.json")


def down_lf(apps, editor_schema):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("protocolo", "0014_movimentacao_physical"),
        ("judicial", "0021_auto_20170327_1056"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommonPerson",
            fields=[
                (
                    "bloke_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.Bloke",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "bloke",
                    models.ForeignKey(
                        related_name="has_bloke_common",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.Pessoa",
                    ),
                ),
            ],
            bases=("judicial.bloke",),
        ),
        migrations.CreateModel(
            name="Dispatch",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "dispatch_title",
                    models.CharField(max_length=300, null=True, blank=True),
                ),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="OrdinaceReformulated",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "type_ordinace",
                    models.SmallIntegerField(
                        choices=[
                            (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                            (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
                            (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                            (7, "PROCEDIMENTO ADMINISTRATIVO"),
                        ]
                    ),
                ),
                ("number_part", models.PositiveIntegerField(null=True, blank=True)),
                ("year_number", models.SmallIntegerField(null=True, blank=True)),
                (
                    "formated_code",
                    models.CharField(max_length=15, unique=True, null=True, blank=True),
                ),
                ("change_title", models.TextField(null=True, blank=True)),
                ("content", models.TextField(null=True, blank=True)),
                (
                    "blokers",
                    models.ManyToManyField(related_name="as_blokers", to="rh.Pessoa"),
                ),
                (
                    "location",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Lotacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "major_interested",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="rh.Pessoa",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "matter",
                    models.ManyToManyField(
                        related_name="in_ordinaces_reformulated",
                        to="judicial.LegalMatter",
                    ),
                ),
                (
                    "other_interesteds",
                    models.ManyToManyField(
                        related_name="as_other_interesteds_in_ordinace", to="rh.Pessoa"
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        related_name="as_ordinaces_reformulated",
                        blank=True,
                        to="rh.Publicacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(judicial.models.InitialPartlawsuit, "judicial.partlawsuit"),
        ),
        migrations.CreateModel(
            name="ScientifyWorkplace",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        related_name="in_sciences",
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "movement",
                    models.ForeignKey(
                        related_name="as_science",
                        blank=True,
                        to="protocolo.Movimentacao",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "part",
                    models.ForeignKey(
                        related_name="sciences",
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "protocol",
                    models.ForeignKey(
                        related_name="as_science",
                        blank=True,
                        to="protocolo.Protocolo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="assessmentnoticeoffice",
            name="notice_office_type",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Termo de Declara\xe7\xe3o"),
                    (2, "Noticia de Fato"),
                    (3, "Carta Precat\xf3ria"),
                ],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="diligence",
            name="county",
            field=models.ForeignKey(
                related_name="diligences",
                to="judicial.County",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="city_locations",
            field=models.ManyToManyField(
                related_name="_outcourtlawsuit_city_locations_+", to="rh.Localidade"
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="matters",
            field=models.ManyToManyField(
                related_name="in_lawsuit", to="judicial.LegalMatter"
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="notice_locations",
            field=models.ManyToManyField(
                related_name="_outcourtlawsuit_notice_locations_+", to="rh.Localidade"
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="removed_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="removed_by",
            field=models.ForeignKey(
                related_name="has_remover_of_lawsuit",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attached",
            name="attached_diligence",
            field=models.ForeignKey(
                related_name="attaches",
                blank=True,
                to="judicial.Diligence",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attached",
            name="attached_document",
            field=models.ForeignKey(
                related_name="attaches",
                blank=True,
                to="judicial.PartLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attached",
            name="attached_manifestation",
            field=models.ForeignKey(
                related_name="attaches",
                blank=True,
                to="judicial.Manifestation",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attached",
            name="attached_part_access",
            field=models.ForeignKey(
                related_name="attaches",
                blank=True,
                to="judicial.PartLawsuitAccess",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="interested",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="has_interested",
                to="judicial.OutCourtLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="number_lawsuit",
            field=models.IntegerField(null=True, verbose_name="N\xfamero", blank=True),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="year",
            field=models.SmallIntegerField(null=True, verbose_name="Ano", blank=True),
        ),
        migrations.RunPython(up_lf, down_lf),
        migrations.RunPython(up_sync, down_sync),
        migrations.RunPython(up_type, down_type),
        migrations.RunPython(up_city_locations_sync, down_city_locations_sync),
        migrations.RunPython(up_sync_interested, down_sync_interested),
        migrations.CreateModel(
            name="PartLegalSign",
            fields=[
                (
                    "legalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.LegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "part",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("protocolo.legalsign",),
        ),
        migrations.AlterField(
            model_name="workerreminder",
            name="priority",
            field=models.SmallIntegerField(
                choices=[(1, "Normal"), (2, "Urgente"), (3, "Imediata")]
            ),
        ),
        migrations.CreateModel(
            name="JudicialDiligenceLegalSign",
            fields=[
                (
                    "legalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.LegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "diligence",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="judicial.JudicialDiligence",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=("protocolo.legalsign",),
        ),
        migrations.CreateModel(
            name="ManifestationLegalSign",
            fields=[
                (
                    "legalsign_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="protocolo.LegalSign",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "manifestation",
                    models.ForeignKey(
                        related_name="legal_signs",
                        to="judicial.Manifestation",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(judicial.models.JudicialLegalSign, "protocolo.legalsign"),
        ),
        migrations.CreateModel(
            name="DearchivingDispatch",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("dearchiving_type", models.SmallIntegerField(choices=[])),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AddField(
            model_name="remittanceexternal",
            name="organs",
            field=models.ManyToManyField(
                related_name="in_remittance_external", to="rh.OrgaoGeral"
            ),
        ),
        migrations.RunPython(
            up_sync_remittanceexternal_organ, down_sync_remittanceexternal_organ
        ),
        migrations.RemoveField(
            model_name="remittanceexternal",
            name="organ",
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="external_locations",
            field=models.ManyToManyField(
                related_name="in_lawsuit_as_external",
                null=True,
                to="rh.OrgaoGeral",
                blank=True,
            ),
        ),
        migrations.RunPython(
            up_sync_outcourtlawsuit_external_location,
            down_sync_outcourtlawsuit_external_location,
        ),
        migrations.RemoveField(
            model_name="outcourtlawsuit",
            name="external_location",
        ),
        migrations.CreateModel(
            name="ArchivementNoticeOffice",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("cause", models.SmallIntegerField()),
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.CreateModel(
            name="DilationManifestation",
            fields=[
                (
                    "partlawsuit_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.PartLawsuit",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("older_deadline", models.DateField(null=True, blank=True)),
                ("content", models.TextField()),
                (
                    "manifestation",
                    models.ForeignKey(
                        related_name="dilations",
                        to="judicial.Manifestation",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="with_matter",
            field=models.ForeignKey(
                related_name="as_with_matter",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.LegalMatter",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="dismembermentprocess",
            name="change_title",
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name="dismembermentprocess",
            name="matters",
            field=models.ManyToManyField(
                related_name="in_desmemberment_processes", to="judicial.LegalMatter"
            ),
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="cause",
            field=models.SmallIntegerField(choices=[(1, "Motivo 1")]),
        ),
        migrations.AlterField(
            model_name="dearchivingdispatch",
            name="dearchiving_type",
            field=models.SmallIntegerField(choices=[(1, "Motivo 1")]),
        ),
        migrations.RunPython(up_sync_desmemberprocess, down_sync_desmemberprocess),
        migrations.AlterField(
            model_name="dilationperiod",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="origin",
            field=models.ForeignKey(
                related_name="out_court_lawsuits",
                on_delete=django.db.models.deletion.PROTECT,
                to="protocolo.Protocolo",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="dilationmanifestation",
            name="dilation_days",
            field=models.SmallIntegerField(default=0),
        ),
    ]
