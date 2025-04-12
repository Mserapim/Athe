# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import rh.gfp.dirf.models
import django.db.models.deletion
from django.conf import settings


def update_dialects(apps, schema_editor):

    Dialect = apps.get_model("dirf", "Dialect")
    Choice = apps.get_model("standard", "Choice")
    print("")
    for d in Dialect.objects.all():
        d.reference_year = d.dirf.ano_calendario + 1
        d.calendar_year = d.dirf.ano_calendario
        d.save()
        for t in d.tokens.exclude(id_receita=""):
            try:
                id_ = "%s-%s" % (
                    "BPFRRA" if t.slug.startswith("rra") else "BPFDEC",
                    t.id_receita,
                )
                if t.slug.startswith("outros"):
                    id_ = "BPFDEC-RIO"
                elif t.slug.startswith("decimo-terceiro"):
                    id_ = "%s-13" % id_
                choice = Choice.objects.get(
                    app_label="dirf", name="IDENTIFIERS_DIRF", label=id_
                )
            except Exception:
                pass
            else:
                t.extra_info = t.id_receita
                t.identifier = choice.value
            t.save()
        print("%s %d/%d" % (d, d.reference_year, d.calendar_year))

    DirfResumos = apps.get_model("dirf", "DirfResumos")

    try:
        choice = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label="BPFDEC-RIDAC"
        )
    except Exception:
        pass
    else:
        DirfResumos.objects.filter(
            tipo__in=[
                "DIARIA",
                "IDENIZA-TRANSPORTE",
                "AJUDA-TRANSPORTE",
                "BOLSA-ESTUDOS",
            ]
        ).update(identifier=choice.value)

    try:
        choice = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label="BPFDEC-RIO"
        )
    except Exception:
        pass
    else:
        DirfResumos.objects.filter(tipo__in=["AUX-NATALIDADE", "AUX-FUNERAL"]).update(
            identifier=choice.value
        )


def migre_dirfsummaries(apps, schema_editor):

    DirfResumos = apps.get_model("dirf", "DirfResumos")
    DirfSummary = apps.get_model("dirf", "DirfSummary")
    NaturezaRendimento = apps.get_model("dirf", "NaturezaRendimento")

    from contrib.middleware import set_current_user

    set_current_user("athenas")

    for dr in DirfResumos.objects.filter(
        ano=2016, tipo__in=["AUX-NATALIDADE", "AUX-FUNERAL", "BOLSA-ESTUDOS"]
    ).exclude(tipo="DIRF"):
        ds, created = DirfSummary.objects.get_or_create(
            person=dr.pessoa,
            calendar_year=dr.ano,
            info=dr.tipo,
            identifier=dr.identifier,
            code=NaturezaRendimento.objects.get(codigo="0561"),
        )
        value = getattr(ds, "value_%02d" % dr.mes)
        if value > 0:
            print(
                "ERRO ao migrar DirfResumos: %s/%s %s %s"
                % (dr.mes, dr.ano, dr.tipo, dr.pessoa)
            )
        setattr(ds, "value_%02d" % dr.mes, dr.valor)
        ds.save()


def null_method(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0034_auto_20170127_1553"),
        ("rh", "0038_auto_20170127_1553"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dirf", "0009_auto_20160219_0743"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.CreateModel(
            name="DirfSummary",
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
                ("identifier", models.PositiveSmallIntegerField()),
                ("info", models.CharField(default=b"", max_length=50, db_index=True)),
                ("calendar_year", models.SmallIntegerField()),
                (
                    "value_01",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_02",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_03",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_04",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_05",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_06",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_07",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_08",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_09",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_10",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_11",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_12",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                (
                    "value_13",
                    models.DecimalField(default=0, max_digits=11, decimal_places=2),
                ),
                ("dirf_created", models.BooleanField(default=False)),
                (
                    "code",
                    models.ForeignKey(
                        related_name="summaries",
                        to="dirf.NaturezaRendimento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "pensioner",
                    models.ForeignKey(
                        related_name="dirf_summaries_pensioner",
                        blank=True,
                        to="rh.PessoaFisica",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "person",
                    models.ForeignKey(
                        related_name="dirf_summaries",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "rra",
                    models.ForeignKey(
                        related_name="dirf_summaries",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="RRA",
                        blank=True,
                        to="gfp.RRA",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-calendar_year", "code", "person", "identifier", "info"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterModelOptions(
            name="dialect",
            options={"ordering": ("-reference_year", "-calendar_year")},
        ),
        migrations.AlterModelOptions(
            name="dirfresumos",
            options={"ordering": ("-ano", "pessoa", "mes", "identifier")},
        ),
        migrations.AddField(
            model_name="dialect",
            name="calendar_year",
            field=models.PositiveSmallIntegerField(
                default=rh.gfp.dirf.models.current_year, blank=True
            ),
        ),
        migrations.AddField(
            model_name="dialect",
            name="reference_year",
            field=models.PositiveSmallIntegerField(
                default=rh.gfp.dirf.models.current_year, blank=True
            ),
        ),
        migrations.AddField(
            model_name="dirfresumos",
            name="identifier",
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="token",
            name="extra_info",
            field=models.CharField(
                max_length=30, null=True, verbose_name="Info", blank=True
            ),
        ),
        migrations.AddField(
            model_name="token",
            name="identifier",
            field=models.PositiveSmallIntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name="dirfresumos",
            name="pessoa",
            field=models.ForeignKey(
                related_name="dirf_resumos", to="rh.Pessoa", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="token",
            name="id_receita",
            field=models.CharField(
                default=b"",
                max_length=30,
                null=True,
                verbose_name="Identificador do Registro",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="token",
            name="tipo",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name="dirfresumos",
            unique_together=set([("pessoa", "ano", "mes", "tipo", "identifier")]),
        ),
        migrations.AlterUniqueTogether(
            name="dirfsummary",
            unique_together=set(
                [("person", "calendar_year", "info", "identifier", "pensioner", "code")]
            ),
        ),
        migrations.RunPython(update_dialects, null_method),
        migrations.RunPython(migre_dirfsummaries, null_method),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
