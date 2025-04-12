# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.db.models.query_utils import Q

import sys


def migrate_fields(apps, schema_editor):

    revision = "8466"
    message = """Para realizar a migração de 0055 a 0056 é necessário colocar o código na revisão %s.
    Confirme[y] caso tenha certeza que a revisão é %s.
    Esta migração também apagará os campos designation_substitute e designation_substituted
        do modelo MovimentacaoSubstituicaoMembro. E o campos de transição designation_substitute_migration e designation_substituted_migration
        do modelo MovimentacaoSubstituicao""" % (
        revision,
        revision,
    )

    if query_yes_no(message, default="no"):

        SubstitutionModel = apps.get_model("rh", "MovimentacaoSubstituicao")

        query = SubstitutionModel.objects.filter(
            Q(designation_substitute_migration__isnull=False)
            | Q(designation_substituted_migration__isnull=False)
        )
        print("TOTAL ... %s" % query.count())
        count = 1
        for sub in query:
            print("UPDATING ... %s" % count)
            SubstitutionModel.objects.filter(pk=sub.pk).update(
                designation_substitute=sub.designation_substitute_migration,
                designation_substituted=sub.designation_substituted_migration,
            )
            count += 1
        print("OK")
    else:
        raise Exception("modifique a revisao para %s" % revision)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        # ('rh', '0056_datamigration_substitution'),
        ("rh", "0055_datamigration_substitution_20171201_1646"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="movimentacaosubstituicaomembro",
            name="designation_substitute",
        ),
        migrations.RemoveField(
            model_name="movimentacaosubstituicaomembro",
            name="designation_substituted",
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicao",
            name="designation_substitute",
            field=models.ForeignKey(
                related_name="substitution_substitute",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicao",
            name="designation_substituted",
            field=models.ForeignKey(
                related_name="substituted",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.RunPython(migrate_fields, _null_function),
        migrations.RemoveField(
            model_name="movimentacaosubstituicao",
            name="designation_substitute_migration",
        ),
        migrations.RemoveField(
            model_name="movimentacaosubstituicao",
            name="designation_substituted_migration",
        ),
    ]


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
