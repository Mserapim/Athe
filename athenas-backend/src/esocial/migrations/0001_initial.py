# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.db import migrations, models
from django.conf import settings
from django.core.management import call_command

import standard.models
import django.db.models.deletion
import os


FIXTURES = (
    "fixtures/initialdb_0001_choices.json",
    "fixtures/initialdb_0002_application.json",
    "fixtures/initialdb_0003_controllers.json",
)


def update_persons(apps, schema_editor):

    from contrib.middleware import set_current_user
    from rh.models import PessoaFisica

    set_current_user("athenas")

    duplicated_persons = {}

    for pf in PessoaFisica.objects.all():
        pf.nome = pf.nome.strip().replace("  ", " ").upper()
        if pf.cpf:
            pf.cpf = pf.cpf.replace(".", "").replace("-", "")
        if pf.old_fields:
            try:
                pf.save()
            except Exception as e:
                PessoaFisica.objects.filter(pk=pf.pk).update(nome=pf.nome, cpf=pf.cpf)
                q_person = PessoaFisica.objects.filter(cpf=pf.cpf)
                if q_person.count() > 1:
                    if pf.cpf not in duplicated_persons:
                        duplicated_persons[pf.cpf] = []
                    duplicated_persons[pf.cpf].append(pf.nome)

    if duplicated_persons:
        print("")
        print(">>ATENCAO<<")
        print(
            ">> Algumas pessoas físicas estão cadastradas duplicadas, possuindo o mesmo CPF!"
        )
        print(
            ">> Esses cadastros dever ser avaliados e corrigidos pois gerará erros no envio do eSocial."
        )
        print(">> Segue listagem dos CPF que estão em mais de uma pessoa física:")
        print("")
        for cpf in duplicated_persons:
            print("%s:%s" % (cpf, ";".join([n for n in duplicated_persons[cpf]])))
        print("")

    Documento = apps.get_model("rh", "Documento")
    for d in Documento.objects.filter(tipo_documento__in=[5, 6]):
        if len(d.numero) < 11 or d.numero == "00000000000":
            d.delete()


def initial_data(*args, **kwargs):
    BASE_DIR = getattr(settings, "BASE_DIR", "")
    print("Running initial data...")

    for fixture in FIXTURES:
        filepath = os.path.join(BASE_DIR, "esocial", fixture)
        print('\033[1mRunning loaddata in fixture "%s"\033[0m' % filepath)
        call_command("loaddata", filepath)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0003_auto_20151014_1609"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistrationQualification",
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
                (
                    "cpf",
                    models.CharField(
                        max_length=11, null=True, verbose_name="CPF", blank=True
                    ),
                ),
                (
                    "nis",
                    models.CharField(
                        max_length=11, null=True, verbose_name="NIS*", blank=True
                    ),
                ),
                (
                    "nome",
                    models.CharField(max_length=100, verbose_name="Nome", blank=True),
                ),
                (
                    "dn",
                    models.DateField(
                        null=True, verbose_name="Data nascimento", blank=True
                    ),
                ),
                (
                    "cod_cpf_inv",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_inv", blank=True
                    ),
                ),
                (
                    "cod_nis_inv",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_nis_inv", blank=True
                    ),
                ),
                (
                    "cod_nome_inv",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_nome_inv", blank=True
                    ),
                ),
                (
                    "cod_dn_inv",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_dn_inv", blank=True
                    ),
                ),
                (
                    "cod_cnis_nis",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cnis_nis", blank=True
                    ),
                ),
                (
                    "cod_cnis_dn",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cnis_dn", blank=True
                    ),
                ),
                (
                    "cod_cnis_obito",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cnis_obito", blank=True
                    ),
                ),
                (
                    "cod_cnis_cpf",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cnis_cpf", blank=True
                    ),
                ),
                (
                    "cod_cnis_cpf_nao_inf",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cnis_cpf_nao_inf", blank=True
                    ),
                ),
                (
                    "cod_cpf_nao_consta",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_nao_consta", blank=True
                    ),
                ),
                (
                    "cod_cpf_nulo",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_nulo", blank=True
                    ),
                ),
                (
                    "cod_cpf_cancelado",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_cancelado", blank=True
                    ),
                ),
                (
                    "cod_cpf_suspenso",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_suspenso", blank=True
                    ),
                ),
                (
                    "cod_cpf_dn",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_cpf_dn", blank=True
                    ),
                ),
                (
                    "cod_cpf_nome",
                    models.CharField(
                        default="",
                        max_length=100,
                        verbose_name="cod_cpf_nome",
                        blank=True,
                    ),
                ),
                (
                    "cod_orientacao_cpf",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_orientacao_cpf", blank=True
                    ),
                ),
                (
                    "cod_orientacao_nis",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="cod_orientacao_nis", blank=True
                    ),
                ),
                (
                    "separador",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="separador", blank=True
                    ),
                ),
                (
                    "reg_desformatado",
                    models.PositiveSmallIntegerField(
                        default=1, verbose_name="reg_desformatado", blank=True
                    ),
                ),
                (
                    "last_qualification_at",
                    models.DateField(
                        null=True, verbose_name="Qualificado em", blank=True
                    ),
                ),
                (
                    "last_modified_person_at",
                    models.DateTimeField(verbose_name="Modificado em", blank=True),
                ),
                (
                    "type_of_person",
                    models.PositiveSmallIntegerField(
                        default=1,
                        choices=[
                            (1, "SERVIDOR ATIVO"),
                            (2, "SERVIDOR INATIVO"),
                            (3, "DEPENDENTE"),
                            (4, "PENSIONISTA"),
                            (5, "ESTAGI\xc1RIO"),
                            (6, "DESCONHECIDO"),
                        ],
                    ),
                ),
                (
                    "qualified",
                    models.BooleanField(default=False, verbose_name="Qualificado?"),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        default=1,
                        choices=[
                            (1, "Aguardando Qualifica\xe7\xe3o"),
                            (2, "Erro nos dados"),
                            (3, "Processado com erro"),
                            (4, "Rejeitado"),
                            (10, "Qualificado"),
                        ],
                    ),
                ),
                (
                    "type_of_last_qualification",
                    models.PositiveSmallIntegerField(
                        default=1,
                        choices=[(1, "N\xc3O QUALIFICADO"), (2, "ONLINE"), (3, "LOTE")],
                    ),
                ),
                ("info", models.TextField(default="", verbose_name="Info", blank=True)),
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
                    "last_modified_person_by",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Modificado por",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "last_qualification_by",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Qualificado por",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
                    "natural_person",
                    models.OneToOneField(
                        related_name="qualification",
                        verbose_name="Pessoa F\xedsica",
                        to="rh.PessoaFisica",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "return_file",
                    models.ForeignKey(
                        verbose_name="Arquivo",
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("status", "-last_qualification_at", "natural_person"),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RunPython(initial_data, _null_function),
        migrations.RunPython(update_persons, _null_function),
    ]
