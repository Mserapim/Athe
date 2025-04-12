# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0001_initial"),
        ("rh", "0001_initial"),
        ("concurso", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vaga",
            name="local",
            field=models.ForeignKey(
                related_name="vagas",
                verbose_name="Local",
                to="rh.Localidade",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="selecaoestagio",
            name="inscricao",
            field=models.OneToOneField(
                related_name="para_estagio",
                verbose_name="Inscri\xc3\xa7\xc3\xa3o",
                to="concurso.Inscricao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="inscricao",
            name="protocolo",
            field=models.OneToOneField(
                related_name="inscricao",
                verbose_name="Protocolo",
                to="protocolo.Protocolo",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="inscricao",
            name="vaga",
            field=models.ForeignKey(
                related_name="inscricoes",
                verbose_name="Vaga",
                to="concurso.Vaga",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="concurso",
            name="cidade_evento",
            field=models.ForeignKey(
                related_name="concursos", to="rh.Localidade", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
