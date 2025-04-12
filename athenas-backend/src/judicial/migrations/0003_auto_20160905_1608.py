# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0002_populate"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recomendation",
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
                ("content", models.TextField()),
            ],
            options={
                "abstract": False,
            },
            bases=("judicial.partlawsuit",),
        ),
        migrations.AddField(
            model_name="outcourtlawsuit",
            name="attached_lawsuit",
            field=models.ForeignKey(
                related_name="has_connected",
                blank=True,
                to="judicial.OutCourtLawsuit",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="attacheddocument",
            name="attached_type",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Documentos"),
                    (2, "Galeria de Fotos"),
                    (3, "Galeria de Videos"),
                    (4, "Galeria de \xc1udio"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="attempt",
            field=models.SmallIntegerField(
                null=True, verbose_name="tentativas de entrega", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="delivered",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="a diligencia foi entregue ao destinatario ou nao",
                choices=[(1, "Entregue"), (2, "N\xe3o Entregue")],
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="delivery_date",
            field=models.DateTimeField(
                null=True, verbose_name="Momento da entrega", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="exit_date",
            field=models.DateTimeField(
                null=True, verbose_name="data e hora de saida para entrega", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="file_delivery",
            field=models.OneToOneField(
                related_name="+",
                null=True,
                blank=True,
                to="ged.Arquivo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="observation",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="return_date",
            field=models.DateTimeField(
                null=True, verbose_name="data e hora de retorno da entrega", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="deliveryattempt",
            name="type_vehicle",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                choices=[(1, "Ve\xedculo Oficial"), (2, "Ve\xedculo Particular")],
            ),
        ),
        migrations.AlterField(
            model_name="dilationperiod",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Noticia de Fato"),
                    (2, "Inquerito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Noticia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="diligence",
            name="delivery_status",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="status da entrega",
                blank=True,
                choices=[
                    (1, "Redigindo a diligencia"),
                    (2, "Aguardando Distribu\xe7\xe3o"),
                    (3, "Aguardando Confirma\xe7\xe3o do Oficial"),
                    (4, "Entrega em andamento"),
                    (5, "Entrega Conclu\xedda"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="glosary",
            name="classification_type",
            field=models.SmallIntegerField(
                null=True, choices=[(1, "Movimento"), (2, "N\xe3o Procedimental")]
            ),
        ),
        migrations.AlterField(
            model_name="judicialdiligence",
            name="who_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="legalground",
            name="text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="manifestation",
            name="who_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="ordinace",
            name="type_ordinace",
            field=models.SmallIntegerField(
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPATAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="type_lawsuit",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo do Processo",
                choices=[
                    (1, "Noticia de Fato"),
                    (2, "Inquerito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Noticia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="partlawsuitaccess",
            name="motivation",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Envolve menor indefeso"),
                    (2, "Quebra de sigilo banc\xe1rio"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="personhasaccess",
            name="state",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Autorizado"),
                    (2, "Autorizado com limita\xe7\xf5es"),
                    (3, "Autoriza\xe7\xe3o revogada"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="decision_type",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Reconsiderar Indeferimento"),
                    (2, "Mater o Indeferimento"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="rejection_fact_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "N\xe3o presente a legitimidade do MP"),
                    (
                        2,
                        "O fato n\xe3o constitui viola\xe7\xe3o de direito e interesses difuso",
                    ),
                    (3, "O fato j\xe1 se encontrar solucionado"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="rejectionfact",
            name="type_ordinace",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPATAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="remittanceexternal",
            name="organ",
            field=models.ForeignKey(
                related_name="in_remittance_external",
                to="rh.OrgaoGeral",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="incident",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                choices=[
                    (101, "Conex\xe3o"),
                    (102, "Preven\xe7\xe3o"),
                    (201, "Impedimento"),
                    (202, "Suspei\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="triageconcurrence",
            name="incident_type",
            field=models.SmallIntegerField(
                default=1,
                blank=True,
                choices=[(1, "Sem incidente"), (2, "Positivo"), (3, "Negativo")],
            ),
        ),
    ]
