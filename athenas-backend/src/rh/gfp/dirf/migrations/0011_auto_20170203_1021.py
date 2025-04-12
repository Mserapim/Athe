# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0010_auto_20170127_1553"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="ajuda_custo",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="data_geracao",
            field=models.DateTimeField(
                default=datetime.datetime(2017, 2, 3, 10, 21, 25, 76197),
                auto_now_add=True,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="decimoterceiro",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="decimoterceiro_imposto",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="decimoterceiro_outro",
            field=models.CharField(default=b"", max_length=60),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="idenizacao",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="imposto_retido",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="informacao_complementar",
            field=models.CharField(default=b"", max_length=400),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="lucro_dividendo",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="outros",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="parcela_isenta",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="pensao_alimenticia",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="pensao_aposentado",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="previdencia_oficial",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="previdencia_privada",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="qnt_meses",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="rendimento",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="rendimento_molestia",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="servico_prestado",
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="dirfresumos",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "BPFDEC-RTRT"),
                    (2, "BPFDEC-RTPO"),
                    (3, "BPFDEC-RTDP"),
                    (4, "BPFDEC-RTIRF"),
                    (5, "BPFDEC-RIDAC"),
                    (6, "BPFDEC-RIIRP"),
                    (7, "BPFDEC-RIAP"),
                    (8, "BPFDEC-RIO"),
                    (9, "BPFRRA-RTRT"),
                    (10, "BPFRRA-RTPO"),
                    (11, "BPFRRA-RTIRF"),
                    (12, "BPFRRA-DAJUD"),
                    (13, "BPFDEC-RTPA"),
                    (14, "BPFRRA-RTPA"),
                    (15, "BPFDEC-RTRT-13"),
                    (16, "BPFDEC-RTPO-13"),
                    (17, "BPFDEC-RTIRF-13"),
                    (18, "BPFDEC-RIIRP-13"),
                    (19, "BPFDEC-RTDP-13"),
                    (20, "BPFDEC-RIO-13"),
                    (21, "BPFRRA-RIMOG"),
                    (22, "BPFRRA-QTMESES"),
                    (23, "BPJDEC-RTRT"),
                    (24, "BPJDEC-RTIRF"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dirfsummary",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "BPFDEC-RTRT"),
                    (2, "BPFDEC-RTPO"),
                    (3, "BPFDEC-RTDP"),
                    (4, "BPFDEC-RTIRF"),
                    (5, "BPFDEC-RIDAC"),
                    (6, "BPFDEC-RIIRP"),
                    (7, "BPFDEC-RIAP"),
                    (8, "BPFDEC-RIO"),
                    (9, "BPFRRA-RTRT"),
                    (10, "BPFRRA-RTPO"),
                    (11, "BPFRRA-RTIRF"),
                    (12, "BPFRRA-DAJUD"),
                    (13, "BPFDEC-RTPA"),
                    (14, "BPFRRA-RTPA"),
                    (15, "BPFDEC-RTRT-13"),
                    (16, "BPFDEC-RTPO-13"),
                    (17, "BPFDEC-RTIRF-13"),
                    (18, "BPFDEC-RIIRP-13"),
                    (19, "BPFDEC-RTDP-13"),
                    (20, "BPFDEC-RIO-13"),
                    (21, "BPFRRA-RIMOG"),
                    (22, "BPFRRA-QTMESES"),
                    (23, "BPJDEC-RTRT"),
                    (24, "BPJDEC-RTIRF"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="token",
            name="extra_info",
            field=models.CharField(default=b"", max_length=30, verbose_name="Info"),
        ),
        migrations.AlterField(
            model_name="token",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1,
                blank=True,
                choices=[
                    (1, "BPFDEC-RTRT"),
                    (2, "BPFDEC-RTPO"),
                    (3, "BPFDEC-RTDP"),
                    (4, "BPFDEC-RTIRF"),
                    (5, "BPFDEC-RIDAC"),
                    (6, "BPFDEC-RIIRP"),
                    (7, "BPFDEC-RIAP"),
                    (8, "BPFDEC-RIO"),
                    (9, "BPFRRA-RTRT"),
                    (10, "BPFRRA-RTPO"),
                    (11, "BPFRRA-RTIRF"),
                    (12, "BPFRRA-DAJUD"),
                    (13, "BPFDEC-RTPA"),
                    (14, "BPFRRA-RTPA"),
                    (15, "BPFDEC-RTRT-13"),
                    (16, "BPFDEC-RTPO-13"),
                    (17, "BPFDEC-RTIRF-13"),
                    (18, "BPFDEC-RIIRP-13"),
                    (19, "BPFDEC-RTDP-13"),
                    (20, "BPFDEC-RIO-13"),
                    (21, "BPFRRA-RIMOG"),
                    (22, "BPFRRA-QTMESES"),
                    (23, "BPJDEC-RTRT"),
                    (24, "BPJDEC-RTIRF"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="token",
            name="tipo",
            field=models.IntegerField(
                blank=True, null=True, choices=[(1, "RENDIMENTO"), (2, "DESPESA")]
            ),
        ),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
