# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0014_auto_20180403_1703"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="agreementsupervisor",
            options={
                "verbose_name": "Fiscal de Contrato",
                "permissions": (
                    ("can_close_supervisor", "Pode encerrar atua\xe7\xe3o de fiscal"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="acaocontrato",
            name="tipo",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Pedir Prorroga\xe7\xe3o"),
                    (2, "Aceitar Pedido de Prorroga\xe7\xe3o"),
                    (3, "Negar Pedido de Prorroga\xe7\xe3o"),
                    (4, "Pedir Licita\xe7\xe3o"),
                    (5, "Negar Licita\xe7\xe3o"),
                    (6, "Licitar"),
                    (7, "Finalizar Contrato"),
                    (8, "Pedir Recis\xe3o Contratual"),
                    (9, "Aceitar Pedido de Recis\xe3o Contratual"),
                    (10, " Negar Pedido de Recis\xe3o Contratual"),
                    (11, "Alertar Vencimento do Contrato"),
                    (12, "Solicita\xe7\xe3o de Pagamento"),
                    (13, "Lan\xe7ar Pagamento"),
                    (100, "Cadastro do Contrato"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="agreementsupervisor",
            name="kind",
            field=models.PositiveSmallIntegerField(
                verbose_name="Tipo", choices=[(1, "Titular"), (2, "Substituto")]
            ),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="status",
            field=models.SmallIntegerField(
                default=100,
                choices=[
                    (1, "Solicitada Prorroga\xe7\xe3o"),
                    (2, "Solicitada a Licita\xe7\xe3o"),
                    (3, "Solicitada a Recis\xe3o"),
                    (4, "Finalizado"),
                    (100, "Em Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="envionefornecedor",
            name="prorrogacao",
            field=models.IntegerField(
                blank=True, null=True, choices=[(1, "N\xe3o"), (100, "Sim")]
            ),
        ),
        migrations.AlterField(
            model_name="notaempenho",
            name="reforco_estorno",
            field=models.SmallIntegerField(
                blank=True, null=True, choices=[(1, "Estorno"), (100, "Refor\xe7o")]
            ),
        ),
        migrations.AlterField(
            model_name="supervisorclassification",
            name="kind",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Administrativo"), (2, "T\xe9cnico"), (3, "Requisitante")]
            ),
        ),
        migrations.AlterUniqueTogether(
            name="agreementsupervisor",
            unique_together=set([]),
        ),
    ]
