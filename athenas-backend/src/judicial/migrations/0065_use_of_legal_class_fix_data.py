# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from django.db import migrations, models


fix_base = [
    (1, 910002),  # Noticia de Fato
    (2, 910004),  # Inquerito Civil
    (3, 910003),  # Procedimento Preparatório
    (4, 1733),  # Procedimento Investigatório Criminal
    (7, 910005),  # Procedimento Administrativo
    (8, 910015),  # Carta Precatória
]


def _print(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def up_fix_tag(apps, schema):
    Tag = apps.get_model("judicial.Tag")
    LegalClassification = apps.get_model("judicial.LegalClassification")

    _print("\n")
    _print("    fix tags ")

    for tag_id, cnmp_code in fix_base:
        legal_class = LegalClassification.objects.get(cnmp_code=cnmp_code)
        tag, created = Tag.objects.get_or_create(
            pk=tag_id,
            defaults={
                "title": legal_class.title[:40],
                "tag_type": 1,
                "classification_id": legal_class.pk,
            },
        )

        tag.title = legal_class.title[:40]
        tag.classification_id = legal_class.id
        tag.save()

        _print(".")

    Tag.objects.create(pk=6, title="Em Instauração", tag_type=1)
    _print(".")


def down_fix_tag(apps, schema):
    pass


def up_fix_choice_type_lawsuit(apps, schema):
    JudicialChoice = apps.get_model("judicial.JudicialChoice")
    LegalClassification = apps.get_model("judicial.LegalClassification")

    _print("\n")
    _print("    fix type lawsuit ")

    for value, cnmp_code in fix_base:
        legal_class = LegalClassification.objects.get(cnmp_code=cnmp_code)
        choice, created = JudicialChoice.objects.get_or_create(
            value=value,
            app_label="judicial",
            name="TYPE_LAWSUIT",
            defaults={
                "title": legal_class.title[:40],
                "classification_id": legal_class.pk,
            },
        )

        choice.title = legal_class.title[:40]
        choice.classification_id = legal_class.pk
        choice.save()

        _print(".")


def down_fix_choice_type_lawsuit(apps, schema):
    pass


def up_fix_lawsuit(apps, schema):
    Lawsuit = apps.get_model("judicial.OutCourtLawsuit")
    JudicialChoice = apps.get_model("judicial.JudicialChoice")
    Tag = apps.get_model("judicial.Tag")

    _print("\n")
    _print("    fix lawsuits ")

    query = Lawsuit.objects.filter(main_tag=None).exclude(type_lawsuit=6)

    for value, cnmp_code in fix_base:
        try:
            choice = JudicialChoice.objects.get(name="TYPE_LAWSUIT", value=value)
            tag = Tag.objects.get(classification=choice.classification)
            query.filter(type_lawsuit=value).update(main_tag_id=tag.pk)
            _print(".")
        except JudicialChoice.DoesNotExist:
            _print("!(%d)" % value)
        except Exception as e:
            _print("!(%d, %s)" % (value, e))


def down_fix_lawsuit(apps, schema):
    pass


def up_fix_lawsuit_log(apps, schema):
    Log = apps.get_model("judicial.OutCourtLawsuitLog")
    JudicialChoice = apps.get_model("judicial.JudicialChoice")
    Tag = apps.get_model("judicial.Tag")

    _print("\n")
    _print("    fix lawsuit logs ")

    query = Log.objects.filter(main_tag=None).exclude(type_lawsuit=6)
    for value, cnmp_code in fix_base:
        try:
            choice = JudicialChoice.objects.get(name="TYPE_LAWSUIT", value=value)
            tag = Tag.objects.get(classification=choice.classification)
            query.filter(type_lawsuit=value).update(main_tag_id=tag.pk)
            _print(".")
        except JudicialChoice.DoesNotExist:
            _print("!(%d)" % value)
        except Exception as e:
            _print("!(%d, %s)" % (value, e))


def down_fix_lawsuit_log(apps, schema):
    pass


def up_fix_legalclass(apps, schema):
    LegalClass = apps.get_model("judicial.LegalClass")

    fix_base = [
        (1, 910002),  # Noticia de Fato
        (2, 910004),  # Inquerito Civil
        (2, 910003),  # Procedimento Preparatório
        (2, 1733),  # Procedimento Investigatório Criminal
        (2, 910005),  # Procedimento Administrativo
        (1, 910015),  # Carta Precatória
    ]

    _print("\n")
    _print("    fix legal class ")

    for value, cnmp_code in fix_base:
        LegalClass.objects.filter(cnmp_code=cnmp_code).update(instauration=value)
        _print(".")


def down_fix_legalclass(apps, schema):
    pass


def up_fix_judicialchoice(apps, schema):
    JudicialChoice = apps.get_model("judicial.JudicialChoice")

    _print("\n")
    _print("    fix judicial choices ")

    for label, value in (("Documento", 1), ("Portaria", 2)):
        JudicialChoice.objects.create(
            app_label="judicial",
            name="CLASS_INSTAURATION",
            label=label,
            value=value,
            cvalue=str(value),
            cache_path=".".join(["judicial", "CLASS_INSTAURATION"]),
        )

        _print(".")


def down_fix_judicialchoice(apps, schema):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0064_use_of_legal_class"),
    ]

    operations = [
        migrations.RunPython(up_fix_judicialchoice, down_fix_judicialchoice),
        migrations.RunPython(up_fix_legalclass, down_fix_legalclass),
        migrations.RunPython(up_fix_tag, down_fix_tag),
        migrations.RunPython(up_fix_choice_type_lawsuit, down_fix_choice_type_lawsuit),
        migrations.RunPython(up_fix_lawsuit, down_fix_lawsuit),
        migrations.RunPython(up_fix_lawsuit_log, down_fix_lawsuit_log),
    ]
