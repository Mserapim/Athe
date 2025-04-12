# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0017_minute_data_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="minute",
            name="adhesions_quantity",
            field=models.IntegerField(
                verbose_name="Quantidade de Ades\xc3\xb5es",
                choices=[
                    (1, "1"),
                    (2, "2"),
                    (3, "3"),
                    (4, "4"),
                    (5, "5"),
                    (100, "Nenhuma"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minute",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Status",
                choices=[
                    (1, "Ativa"),
                    (2, "Conclu\xedda"),
                    (3, "Cancelada"),
                    (4, "Revogada"),
                    (5, "Suspensa"),
                    (6, "Finalizada"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minuteaction",
            name="action",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Solicitar Cancelamento"),
                    (2, "Solicitar Revoga\xe7\xe3o"),
                    (3, "Solicitar Suspens\xe3o"),
                    (4, "Finalizar Ata"),
                    (5, "Solicitar de Pagamento"),
                    (6, "Lan\xe7ar Pagamento"),
                    (7, "Desfazer Pagamento"),
                    (100, "Cadastro da Ata"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="minuteitem",
            name="item_balance",
            field=models.DecimalField(
                null=True,
                verbose_name="Saldo do item",
                max_digits=18,
                decimal_places=2,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="minuteitem",
            name="quantity",
            field=models.DecimalField(
                null=True,
                verbose_name="Quantidade",
                max_digits=10,
                decimal_places=2,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="minuteitem",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Ativo"),
                    (2, "Desativado"),
                    (3, "Revogado"),
                    (4, "Aditivado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minuteitem",
            name="unit_measure",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (None, "Nenhum"),
                    (61, "UN"),
                    (56, "SV"),
                    (15, "CX"),
                    (40, "M2"),
                    (1, "AMPOLA"),
                    (2, "BALDE"),
                    (3, "BANDEJ"),
                    (4, "BARRA"),
                    (5, "BISNAGA"),
                    (6, "BLOCO"),
                    (7, "BOBINA"),
                    (8, "BOMB"),
                    (9, "CAPS"),
                    (10, "CART"),
                    (11, "CENTO"),
                    (12, "CJ"),
                    (13, "CM"),
                    (14, "CM2"),
                    (16, "CX2"),
                    (17, "CX3"),
                    (18, "CX5"),
                    (19, "CX10"),
                    (20, "CX15"),
                    (21, "CX20"),
                    (22, "CX25"),
                    (23, "CX50"),
                    (24, "CX100"),
                    (25, "DISP"),
                    (26, "DUZIA"),
                    (27, "EMBAL"),
                    (28, "FARDO"),
                    (29, "FOLHA"),
                    (30, "FRASCO"),
                    (31, "GALAO"),
                    (32, "GF"),
                    (33, "GRAMAS"),
                    (34, "JOGO"),
                    (35, "KG"),
                    (36, "KIT"),
                    (37, "LATA"),
                    (38, "LITRO"),
                    (39, "M"),
                    (41, "M3"),
                    (42, "MILHEI"),
                    (43, "ML"),
                    (44, "MWH"),
                    (45, "PACOTE"),
                    (46, "PALETE"),
                    (47, "PARES"),
                    (48, "P\xc7"),
                    (49, "POTE"),
                    (50, "K"),
                    (51, "RESMA"),
                    (52, "ROLO"),
                    (53, "SACO"),
                    (54, "SACOLA"),
                    (55, "SER"),
                    (57, "TAMBOR"),
                    (58, "TANQUE"),
                    (59, "TON"),
                    (60, "TUBO"),
                    (62, "VASIL"),
                    (63, "VIDRO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minuteitemaction",
            name="action",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Reativar"),
                    (2, "Desativar"),
                    (3, "Revogar"),
                    (4, "Aditivar"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitation",
            name="situation",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (1, "Em Edi\xe7\xe3o"),
                    (2, "Solicitado"),
                    (3, "Aprovado"),
                    (4, "Recusado"),
                    (5, "Cancelado"),
                    (6, "Requisitado"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationaction",
            name="action",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Adicionar"),
                    (2, "Solicitar Aprova\xe7\xe3o"),
                    (3, "Aprovar"),
                    (4, "Recusar"),
                    (5, "Cancelar"),
                    (6, "Requisitar"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="minutesolicitationcommitmentnote",
            name="origin",
            field=models.SmallIntegerField(choices=[(1, "PGJ"), (2, "FUNDO")]),
        ),
        migrations.AlterField(
            model_name="minutesolicitationitem",
            name="quantity",
            field=models.DecimalField(
                verbose_name="Quantidade", max_digits=10, decimal_places=2
            ),
        ),
    ]
