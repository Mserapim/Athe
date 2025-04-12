# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0043_auto_20180410_1427"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutCourtLawsuitLog",
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
                (
                    "type_lawsuit",
                    models.SmallIntegerField(
                        verbose_name="Tipo do Processo",
                        choices=[
                            (1, "Not\xedcia de Fato"),
                            (2, "Inqu\xe9rito Civil P\xfablico"),
                            (3, "Procedimento Preparat\xf3rio"),
                            (4, "Procedimento Investigat\xf3rio Criminal"),
                            (5, "Not\xedcia de Fato Criminal"),
                            (6, "Em instaura\xe7\xe3o"),
                            (7, "Procedimento Administrativo"),
                            (8, "Carta Precat\xf3ria"),
                        ],
                    ),
                ),
                ("deadline_days", models.IntegerField(null=True)),
                ("initiator_at", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "ordering": ["pk"],
            },
        ),
        migrations.AlterField(
            model_name="archivementnoticeoffice",
            name="cause",
            field=models.SmallIntegerField(
                choices=[
                    (1, "O fato j\xe1 encontra-se solucionado"),
                    (2, "N\xe3o houve recurso"),
                ]
            ),
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
            model_name="dearchivingdispatch",
            name="dearchiving_type",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Surgimento de novas provas"),
                    (2, "Arquivamento Indevido"),
                ]
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
            name="type_vehicle",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Tipo de veiculo usado para a rezalizacao da diligencia",
                choices=[
                    (1, "Ve\xedculo Oficial"),
                    (2, "Ve\xedculo Particular"),
                    (3, "Correios ou outro terceiro"),
                ],
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
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
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
                    (6, "Publica\xe7\xe3o em di\xe1rio Oficial"),
                    (7, "Entrega pelo \xd3rg\xe3o de Execu\xe7\xe3o"),
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
                choices=[
                    (1, "Interessado"),
                    (2, "Apontado"),
                    (3, "Testemunha"),
                    (4, "\xd3rg\xe3o de Execu\xe7\xe3o"),
                    (5, "\xd3rg\xe3o P\xfablico"),
                    (6, "Empresa Privada"),
                ],
            ),
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
                    (5, "\xd3rg\xe3o P\xfablico"),
                    (6, "Empresa Privada"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="officerdiligence",
            name="status",
            field=models.SmallIntegerField(
                default=1, null=True, choices=[(1, "Ativo"), (2, "Inativo")]
            ),
        ),
        migrations.AlterField(
            model_name="ordinace",
            name="type_ordinace",
            field=models.SmallIntegerField(
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="ordinacereformulated",
            name="type_ordinace",
            field=models.SmallIntegerField(
                choices=[
                    (2, "INQU\xc9RITO CIVIL P\xdaBLICO"),
                    (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
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
                    (1, "Not\xedcia de Fato"),
                    (2, "Inqu\xe9rito Civil P\xfablico"),
                    (3, "Procedimento Preparat\xf3rio"),
                    (4, "Procedimento Investigat\xf3rio Criminal"),
                    (5, "Not\xedcia de Fato Criminal"),
                    (6, "Em instaura\xe7\xe3o"),
                    (7, "Procedimento Administrativo"),
                    (8, "Carta Precat\xf3ria"),
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
                    (3, "Preserva\xe7\xe3o da intimidade"),
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
                    (2, "Manter o Indeferimento"),
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
                    (4, "O fato j\xe1 \xe9 objeto de investiga\xe7\xe3o ou ACP"),
                    (
                        5,
                        "N\xe3o traz ind\xedcios m\xednimos para in\xedcio de investiga\xe7\xe3o",
                    ),
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
                    (3, "PROCEDIMENTO PREPARAT\xd3RIO"),
                    (4, "PROCEDIMENTO INVESTIGATORIO CRIMINAL"),
                    (7, "PROCEDIMENTO ADMINISTRATIVO"),
                ],
            ),
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
        migrations.AlterField(
            model_name="workerreminder",
            name="priority",
            field=models.SmallIntegerField(
                choices=[(1, "Normal"), (2, "Urgente"), (3, "Imediata")]
            ),
        ),
        migrations.AddField(
            model_name="outcourtlawsuitlog",
            name="lawsuit",
            field=models.ForeignKey(
                related_name="logs",
                to="judicial.OutCourtLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="outcourtlawsuitlog",
            name="location",
            field=models.ForeignKey(
                related_name="in_log", to="rh.OrgaoGeral", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="outcourtlawsuitlog",
            name="part",
            field=models.ForeignKey(
                related_name="in_log",
                to="judicial.PartLawsuit",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
