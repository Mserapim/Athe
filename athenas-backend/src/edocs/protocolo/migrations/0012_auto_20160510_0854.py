# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0011_auto_20160321_1634"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="observation",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="protocol",
            field=models.ForeignKey(
                related_name="attachments",
                blank=True,
                to="protocolo.Protocolo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="compartilharcaixa",
            name="pessoa_fisica",
            field=models.ManyToManyField(
                related_name="pessoa_compartilhada", to="rh.PessoaFisica"
            ),
        ),
        migrations.AlterField(
            model_name="compartilharcaixa",
            name="pessoa_fisica_dono",
            field=models.OneToOneField(
                to="rh.PessoaFisica", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="compartilharprotocolo",
            name="lotacao",
            field=models.ManyToManyField(
                related_name="lotacao_comp_prot", to="rh.OrgaoGeral"
            ),
        ),
        migrations.AlterField(
            model_name="compartilharprotocolo",
            name="permissao",
            field=models.ManyToManyField(to="protocolo.PermissaoEdoc"),
        ),
        migrations.AlterField(
            model_name="compartilharprotocolo",
            name="pessoa_fisica",
            field=models.ManyToManyField(
                related_name="pessoa_comp_prot", to="rh.PessoaFisica"
            ),
        ),
        migrations.AlterField(
            model_name="etiqueta",
            name="protocolo",
            field=models.OneToOneField(
                to="protocolo.Protocolo", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="movimentacao",
            name="anexos",
            field=models.ManyToManyField(
                related_name="movimentacao", to="protocolo.Anexo"
            ),
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="referencias",
            field=models.ManyToManyField(
                related_name="prot_referencias",
                verbose_name="Refer\xeancias",
                to="protocolo.Referencia",
            ),
        ),
    ]
