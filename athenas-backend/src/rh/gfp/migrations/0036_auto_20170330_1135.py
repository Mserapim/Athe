# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from contrib.middleware import set_current_user

set_current_user("athenas")


def updating_structures_references_and_salaries(apps, schema_editor):
    # from rh.gfp.models import EstruturaTabelaSalarial , ReferenciaNiveis2D, ReferenciaSalario
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    ReferenciaNiveis2D = apps.get_model("gfp", "ReferenciaNiveis2D")
    EstruturaTabelaSalarial = apps.get_model("gfp", "EstruturaTabelaSalarial")
    ReferenciaSalario = apps.get_model("gfp", "ReferenciaSalario")
    CargosEstrutura = apps.get_model("gfp", "CargosEstrutura")
    MovimentacaoProgressao = apps.get_model("gfp", "MovimentacaoProgressao")

    print("")
    print("UPDATING estrutura_salarial ON ReferenciaNiveis2D: ")
    cont_rn = ReferenciaNiveis2D.objects.filter(modelo_tabela__isnull=False).update(
        estrutura_salarial=None
    )
    print("%d - OK" % cont_rn)

    for es in EstruturaTabelaSalarial.objects.exclude(modelo_tabela__isnull=True):
        es.horizontal_labels = es.modelo_tabela.labels_horizontal
        es.vertical_labels = es.modelo_tabela.labels_vertical
        es.save()
        # print es.modelo_tabela_id
        q_referencia_niveis = ReferenciaNiveis2D.objects.filter(
            modelo_tabela=es.modelo_tabela_id
        )
        ups = q_referencia_niveis.filter(estrutura_salarial__isnull=True).update(
            estrutura_salarial=es
        )
        q_references = ReferenciaNiveis2D.objects.filter(estrutura_salarial=es)
        total_old = q_referencia_niveis.count()
        total_new = q_references.count()
        print(
            "\033[32;94m%s\033[0m %d/%d (%d)" % (es.codigo, total_new, total_old, ups)
        )
        rn_prev = None

        jobs_ids = [
            ce.cargo.id for ce in CargosEstrutura.objects.filter(estrutura_salarial=es)
        ]

        for rn in q_referencia_niveis.order_by("ordem"):
            rn_new = rn
            rn_old_id = rn.pk
            print(rn.sigla_cache, rn.estrutura_salarial.codigo, ">>")
            try:
                rn_new = q_references.get(
                    horizontal=rn.horizontal, vertical=rn.vertical, ordem=rn.ordem
                )
                print("\033[32;94m U\033[0m")
            except ReferenciaNiveis2D.DoesNotExist as e:
                rn_new.pk = None
                rn_new.modelo_tabela = None
                print("\033[33;94m C\033[0m")
            except Exception as e:
                raise e
            rn_new.estrutura_salarial = es
            rn_new.referencia_anterior = rn_prev
            rn_new.save()
            rn_prev = rn_new
            print(
                rn_new.estrutura_salarial.codigo,
                rn_new.pk,
                rn_new.referencia_anterior.pk if rn_new.referencia_anterior else "-",
            )

            ups_rs = ReferenciaSalario.objects.filter(
                tabela_salarial__estrutura_salarial__pk=es.pk,
                referencia_nivel2d_id=rn_old_id,
            ).update(referencia_nivel2d_id=rn_new.pk)
            print(" RS: %4d" % ups_rs)

            ups_mp = MovimentacaoProgressao.objects.filter(
                referencia_nivel2d_id=rn_old_id,
                movimentacao_posse__quadro__cargo_id__in=jobs_ids,
            ).update(referencia_nivel2d_id=rn_new.pk)
            print(" MP: %4d" % ups_mp)

            ups_ce = 0
            for ce in es.cargos_estrutura.filter():
                if ce.referencias.filter(pk=rn_old_id):
                    ce.referencias.remove(rn_old_id)
                    ce.referencias.add(rn_new.pk)
                    ups_ce += 1
            print(" CE: %4d" % ups_ce)

    error = ReferenciaSalario.objects.exclude(
        tabela_salarial__estrutura_salarial=models.F(
            "referencia_nivel2d__estrutura_salarial"
        )
    ).exists()
    print("Referencia Salarios: %s" % ("INCONSISTENTES" if error else "OK"))

    error = False
    for mp in MovimentacaoProgressao.objects.all():
        jobs = [
            ce.cargo
            for ce in mp.referencia_nivel2d.estrutura_salarial.cargos_estrutura.all()
        ]
        if mp.movimentacao_posse.quadro.cargo not in jobs:
            error = True
            break
    print("Progressoes: %s" % ("INCONSISTENTES" if error else "OK"))

    error = CargosEstrutura.objects.exclude(
        referencias__estrutura_salarial=models.F("estrutura_salarial")
    ).exists()
    print("Referencia in CargosEstrutura: %s" % ("INCONSISTENTES" if error else "OK"))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0035_auto_20170330_1027"),
    ]

    operations = [
        migrations.RunPython(
            updating_structures_references_and_salaries, _null_function
        ),
    ]
