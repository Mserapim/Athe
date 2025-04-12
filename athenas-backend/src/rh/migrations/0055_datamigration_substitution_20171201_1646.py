# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models.query_utils import Q

import django.db.models.deletion

import sys


def _null_function(apps, schema_editor):
    pass


def migrate_fields(apps, schema_editor):

    revision = "8464"
    message = """Para realizar a migração de 0054 a 0055 é necessário colocar o código na revisão %s.
    Confirme[y] caso tenha certeza que a revisão é %s""" % (
        revision,
        revision,
    )

    if query_yes_no(message, default="no"):

        SubstitutionModel = apps.get_model("rh", "MovimentacaoSubstituicao")
        MembersubstitutionModel = apps.get_model("rh", "MovimentacaoSubstituicaoMembro")

        query = MembersubstitutionModel.objects.filter(
            Q(designation_substitute__isnull=False)
            | Q(designation_substituted__isnull=False)
        )
        print("TOTAL ... %s" % query.count())
        count = 1
        for sub in query:
            print("UPDATING ... %s" % count)
            SubstitutionModel.objects.filter(pk=sub.pk).update(
                designation_substitute_migration=sub.designation_substitute,
                designation_substituted_migration=sub.designation_substituted,
            )
            count += 1
        print("OK")
    else:
        raise Exception("modifique a revisao para %s" % revision)


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0054_auto_20171201_1427"),
    ]

    operations = [
        migrations.AddField(
            model_name="movimentacaosubstituicao",
            name="designation_substitute_migration",
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
            name="designation_substituted_migration",
            field=models.ForeignKey(
                related_name="substituted",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="tipo",
            field=models.IntegerField(
                null=True,
                verbose_name="Tipo",
                choices=[
                    (1, "C\xd4NJUGE"),
                    (2, "COMPANHEIRO(A)"),
                    (3, "FILHO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS"),
                    (4, "FILHO(A) ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR"),
                    (5, "PAI(M\xc3E) COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (
                        6,
                        "IRM\xc3O N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA E GUARDA JUDICIAL",
                    ),
                    (7, "IRMAO(A) ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR"),
                    (8, "ENTEADO N\xc3O EMANCIPADO MENOR DE 21"),
                    (9, "ENTEADO ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR"),
                    (
                        10,
                        "MENOR TUTELADO N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA OU GUARDA JUDICIAL",
                    ),
                    (11, "MENOR ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR"),
                    (12, "AV\xd3S COM DEPENDENCIA ECONOMICA"),
                    (13, "BISAV\xd3S COM DEPENDENCIA ECONOMICA"),
                    (
                        14,
                        "NETO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA E GUARDA JUDICIAL",
                    ),
                    (
                        15,
                        "BISNETO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA E GUARDA JUDICIAL",
                    ),
                    (16, " EX-C\xd4NJUGE"),
                    (
                        17,
                        "FILHO(A) OU ENTEADO(A) UNIVERSIT\xc1RIO(A) OU CURSANDO ESCOLA T\xc9CNICA DE 2\xbaGRAU, AT\xc9 24 ANOS",
                    ),
                    (18, "AGREGADO/OUTROS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaodesligamento",
            name="tipo_desligamento",
            field=models.IntegerField(
                default=1,
                verbose_name="Tipo de Desligamento",
                choices=[
                    (1, "EXONERA\xc7\xc3O EFETIVO"),
                    (2, "EXONERA\xc7\xc3O COMISSIONADO"),
                    (3, "EXONERA\xc7\xc3O ESTABILIZADO"),
                    (4, "APOSENTADORIA POR INVALIDEZ"),
                    (5, "APOSENTADORIA VOLUNT\xc1RIA"),
                    (6, "POSSE EM OUTRO CARGO"),
                    (7, "FALECIMENTO"),
                    (8, "RESCIS\xc3O"),
                    (9, "DEMISS\xc3O"),
                    (10, "RESERVA REFORMA"),
                    (11, "DISPONIBILIDADE"),
                    (12, "PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                    (13, "FIM REQUISI\xc7\xc3O/ACORDO COOPERA\xc7\xc3O"),
                    (14, "APOSENTADORIA COMPULS\xd3RIA"),
                    (15, "APOSENTADORIA ESPECIAL"),
                    (16, "APOSENTADORIA POR TEMPO DE CONTRIBUI\xc7\xc3O"),
                    (17, "APOSENTADORIA POR IDADE"),
                    (18, "REDISTRIBUI\xc7\xc3O"),
                    (19, "REVERS\xc3O DE REINTEGRA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="app",
            field=models.IntegerField(
                default=1, verbose_name="Aplicativo", choices=[(1, "DIARIAS")]
            ),
        ),
        migrations.RunPython(migrate_fields, _null_function),
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
