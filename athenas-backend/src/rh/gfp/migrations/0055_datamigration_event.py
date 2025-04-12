# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import calendar


def migrate_configs(apps, schema_editor):
    Evento = apps.get_model("gfp", "Evento")
    ConfigEvent = apps.get_model("gfp", "ConfigEvent")
    FolhaEvento = apps.get_model("gfp", "FolhaEvento")
    Periodo = apps.get_model("gfp", "Periodo")
    ClassCode = apps.get_model("standard", "ClassCode")
    start_date = datetime.date(2015, 1, 1)
    createds = 0
    ev_ = None
    count_ev = 0
    for ff in (
        FolhaEvento.objects.filter(evento__genre_event__isnull=False, automated=True)
        .order_by("evento__numero", "calculation")
        .values("evento__numero", "calculation")
        .annotate(
            models.Min("folha__periodo"),
            models.Max("folha__periodo"),
            models.Count("calculation"),
        )
        .order_by("evento__numero", "folha__periodo__min")
    ):
        ev = Evento.objects.get(numero=ff["evento__numero"])
        pmax_ = FolhaEvento.objects.filter(
            evento__genre_event__isnull=False, evento=ev
        ).aggregate(fpmax=models.Max("folha__periodo"))["fpmax"]
        if ev_ != ev:
            ev_ = ev
            count_ev = 0
        count_ev += 1
        cc = ClassCode.objects.get(pk=ff["calculation"]) if ff["calculation"] else None
        pmin = Periodo.objects.get(pk=ff["folha__periodo__min"])
        pmax = (
            Periodo.objects.get(pk=ff["folha__periodo__max"])
            if ff["folha__periodo__max"] != pmax_
            else None
        )
        start_date = datetime.date(pmin.ano, min(12, pmin.mes), 1)
        end_date = (
            datetime.date(
                pmax.ano,
                min(12, pmax.mes),
                calendar.monthrange(pmax.ano, min(12, pmax.mes))[1],
            )
            if pmax
            else None
        )

        print(
            "%02d/%04d %02d/%04d %s %s"
            % (
                pmin.mes,
                pmin.ano,
                pmax.mes if pmax else 0,
                pmax.ano if pmax else 0,
                ff["evento__numero"],
                cc.path if cc else "----------------------",
            )
        )

        ce, created = ev.configs.get_or_create(
            start_validity=start_date,
            defaults={
                "max_quantity": ev.quantidade_max,
                "quantity": ev.quantidade,
                "percentage": ev.porcentagem,
                "base_value": ev.valor_base,
                "floor": ev.teto,
                "ceiling": ev.piso,
                "automated": ev.automatico,
                "inverted_calculation": ev.calculo_invertido,
                "calculation": cc,
                "created_at": ev.created_at,
                "modified_at": ev.modified_at,
                "created_by": ev.created_by,
                "modified_by": ev.modified_by,
                "end_validity": end_date,
            },
        )
        createds += 1 if created else 0
        print("(%d) >> " % (ev.incide_sobre.count()))
        if ev.incide_sobre.exists():
            for i in ev.incide_sobre.all():
                ce.focuses_on.add(i.pk)
            print("%d OK" % ce.focuses_on.count())
        print("")

    for ev in (
        Evento.objects.filter(genre_event__isnull=False)
        .annotate(qtd_cfg=models.Count("configs"))
        .filter(qtd_cfg=0)
    ):
        start_date = datetime.date(2015, 5, 1)
        ce, created = ev.configs.get_or_create(
            start_validity=start_date,
            defaults={
                "max_quantity": ev.quantidade_max,
                "quantity": ev.quantidade,
                "percentage": ev.porcentagem,
                "base_value": ev.valor_base,
                "floor": ev.teto,
                "ceiling": ev.piso,
                "automated": ev.automatico,
                "inverted_calculation": ev.calculo_invertido,
                "calculation": ev.calculo,
                "created_at": ev.created_at,
                "modified_at": ev.modified_at,
                "created_by": ev.created_by,
                "modified_by": ev.modified_by,
            },
        )
        createds += 1 if created else 0

    print(">>>>>>>>>>>>>>> CUIDADO! AVALIAR ESSES EVENTOS E CONFIGS <<<<<<<<<<<<<<<<<<")
    for ev in (
        Evento.objects.filter(genre_event__isnull=False)
        .annotate(qtd_cfg=models.Count("configs"))
        .filter(qtd_cfg__gt=1)
    ):
        print("%s > %d" % (ev.numero, ev.qtd_cfg))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0054_auto_20180917_1501"),
    ]

    operations = [
        migrations.RunPython(migrate_configs, _null_function),
    ]
