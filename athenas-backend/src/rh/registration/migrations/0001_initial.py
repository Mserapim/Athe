# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0060_auto_20180227_1602"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0004_auto_20180201_1933"),
    ]

    operations = [
        migrations.CreateModel(
            name="DigitalDocument",
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
                    "document_type",
                    models.IntegerField(verbose_name="Tipo de Documento"),
                ),
                (
                    "state",
                    models.IntegerField(
                        default=1, verbose_name="Estado de processamento"
                    ),
                ),
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
                    "file",
                    models.ForeignKey(
                        verbose_name="Arquivo",
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="FormInformation",
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
                ("sent_at", models.DateTimeField(default=None, null=True, blank=True)),
                (
                    "validated_at",
                    models.DateTimeField(default=None, null=True, blank=True),
                ),
                (
                    "received_at",
                    models.DateTimeField(default=None, null=True, blank=True),
                ),
                (
                    "state",
                    models.IntegerField(default=1, verbose_name="Estado", blank=True),
                ),
                ("address_can_edit", models.BooleanField(default=True)),
                (
                    "address_type_street",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Endere\xe7o - Tipo do Logradouro",
                        choices=[
                            (1, "AVENIDA"),
                            (2, "PRA\xc7A"),
                            (3, "VIELA"),
                            (4, "PONTO - SERA EXCLUIDO"),
                            (5, "VIADUTO"),
                            (7, "OUTROS - SERA EXCLUIDO"),
                            (8, "RUA"),
                            (9, "QUADRA"),
                        ],
                    ),
                ),
                ("address_type_street_diff", models.BooleanField(default=False)),
                (
                    "address_type_address",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Endere\xe7o - Tipo do Endere\xe7o",
                        choices=[
                            (1, "Residencial"),
                            (2, "Comercial"),
                            (3, "Institucional"),
                            (4, "Profissional"),
                            (5, "Via p\xfablica"),
                            (6, "N\xe3o informado"),
                        ],
                    ),
                ),
                ("address_type_address_diff", models.BooleanField(default=False)),
                ("address_city_diff", models.BooleanField(default=False)),
                (
                    "address_public_place",
                    models.CharField(
                        max_length=80,
                        null=True,
                        verbose_name="Endere\xe7o - Logradouro",
                        blank=True,
                    ),
                ),
                ("address_public_place_diff", models.BooleanField(default=False)),
                (
                    "address_district",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="Endere\xe7o - Bairro",
                        blank=True,
                    ),
                ),
                ("address_district_diff", models.BooleanField(default=False)),
                (
                    "address_zip_code",
                    models.CharField(
                        max_length=10, null=True, verbose_name="CEP", blank=True
                    ),
                ),
                ("address_zip_code_diff", models.BooleanField(default=False)),
                (
                    "address_number",
                    models.CharField(
                        max_length=10,
                        null=True,
                        verbose_name="Endere\xe7o - N\xfamero",
                        blank=True,
                    ),
                ),
                ("address_number_diff", models.BooleanField(default=False)),
                (
                    "address_complement",
                    models.CharField(
                        max_length=30,
                        null=True,
                        verbose_name="Endere\xe7o - Complemento",
                        blank=True,
                    ),
                ),
                ("address_complement_diff", models.BooleanField(default=False)),
                (
                    "phone_main",
                    models.CharField(
                        default="",
                        max_length=13,
                        null=True,
                        verbose_name="Telefone Principal",
                        blank=True,
                    ),
                ),
                ("phone_main_diff", models.BooleanField(default=False)),
                ("phone_main_can_edit", models.BooleanField(default=True)),
                (
                    "contact_emergency_name",
                    models.CharField(
                        max_length=80,
                        null=True,
                        verbose_name="Nome do Contato de Emerg\xeancia",
                        blank=True,
                    ),
                ),
                ("contact_emergency_name_diff", models.BooleanField(default=False)),
                ("contact_emergency_name_can_edit", models.BooleanField(default=True)),
                (
                    "contact_emergency_phone",
                    models.CharField(
                        default="",
                        max_length=13,
                        null=True,
                        verbose_name="Telefone de Emerg\xeancia",
                        blank=True,
                    ),
                ),
                ("contact_emergency_phone_can_edit", models.BooleanField(default=True)),
                ("contact_emergency_phone_diff", models.BooleanField(default=False)),
                ("cnh_can_edit", models.BooleanField(default=True)),
                (
                    "cnh",
                    models.CharField(
                        default="",
                        max_length=11,
                        null=True,
                        verbose_name="CNH",
                        blank=True,
                    ),
                ),
                ("cnh_diff", models.BooleanField(default=False)),
                (
                    "cnh_categoria",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="CNH - Categoria",
                        blank=True,
                    ),
                ),
                ("cnh_categoria_diff", models.BooleanField(default=False)),
                (
                    "cnh_expedition_date",
                    models.DateField(
                        null=True,
                        verbose_name="CNH - Data da Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("cnh_expedition_date_diff", models.BooleanField(default=False)),
                (
                    "cnh_first_date",
                    models.DateField(
                        null=True,
                        verbose_name="CNH - Data da primeira habilita\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("cnh_first_date_diff", models.BooleanField(default=False)),
                ("cnh_state_diff", models.BooleanField(default=False)),
                (
                    "cnh_validity_date",
                    models.DateField(
                        null=True, verbose_name="CNH - Data de Validade", blank=True
                    ),
                ),
                ("cnh_validity_date_diff", models.BooleanField(default=False)),
                ("professional_council_can_edit", models.BooleanField(default=True)),
                (
                    "professional_council",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="Conselho Profissional",
                        blank=True,
                    ),
                ),
                ("professional_council_diff", models.BooleanField(default=False)),
                ("professional_council_state_diff", models.BooleanField(default=False)),
                (
                    "professional_council_expedition_date",
                    models.DateField(
                        null=True,
                        verbose_name="Conselho Profissional - Data da Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "professional_council_expedition_date_diff",
                    models.BooleanField(default=False),
                ),
                (
                    "professional_council_validity_date",
                    models.DateField(
                        null=True,
                        verbose_name="Conselho Profissional - Data de Validade",
                        blank=True,
                    ),
                ),
                (
                    "professional_council_validity_date_diff",
                    models.BooleanField(default=False),
                ),
                (
                    "professional_council_issuer",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="Conselho Profissional - Org\xe3o de Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                (
                    "professional_council_issuer_diff",
                    models.BooleanField(default=False),
                ),
                ("cpf_can_edit", models.BooleanField(default=True)),
                (
                    "cpf",
                    models.CharField(
                        max_length=14, null=True, verbose_name="CPF", blank=True
                    ),
                ),
                ("cpf_doc_digital_required", models.BooleanField(default=True)),
                ("cpf_diff", models.BooleanField(default=False)),
                ("ctps_can_edit", models.BooleanField(default=True)),
                (
                    "ctps",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="CTPS",
                        blank=True,
                    ),
                ),
                ("ctps_diff", models.BooleanField(default=False)),
                ("ctps_state_diff", models.BooleanField(default=False)),
                (
                    "serie_ctps",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="CTPS - S\xe9rie",
                        blank=True,
                    ),
                ),
                ("serie_ctps_diff", models.BooleanField(default=False)),
                ("data_nascimento_can_edit", models.BooleanField(default=True)),
                ("data_nascimento", models.DateField(null=True, blank=True)),
                ("data_nascimento_diff", models.BooleanField(default=False)),
                (
                    "doador",
                    models.BooleanField(
                        default=True, verbose_name="Doador de \xf3rg\xe3os"
                    ),
                ),
                ("doador_can_edit", models.BooleanField(default=True)),
                ("doador_diff", models.BooleanField(default=False)),
                ("email_pessoal_can_edit", models.BooleanField(default=True)),
                (
                    "email_pessoal",
                    models.CharField(
                        default="",
                        max_length=40,
                        null=True,
                        verbose_name="E-mail Pessoal",
                        blank=True,
                    ),
                ),
                ("email_pessoal_diff", models.BooleanField(default=False)),
                ("estado_civil_can_edit", models.BooleanField(default=True)),
                (
                    "estado_civil",
                    models.IntegerField(
                        default=1,
                        null=True,
                        verbose_name="Estado civ\xedl",
                        choices=[
                            (1, "SOLTEIRO"),
                            (2, "CASADO"),
                            (3, "VIUVO"),
                            (4, "SEPARADO JUDICIALMENTE"),
                            (5, "DIVORCIADO"),
                            (6, "UNIAO ESTAVEL"),
                            (7, "N\xc3O FOI DEFINIDO NO CADASTRO - SERA EXCLUIDO"),
                        ],
                    ),
                ),
                ("estado_civil_diff", models.BooleanField(default=False)),
                ("fator_rh_can_edit", models.BooleanField(default=True)),
                (
                    "fator_rh",
                    models.IntegerField(
                        default=2,
                        null=True,
                        verbose_name="Fator RH",
                        blank=True,
                        choices=[(1, "-"), (2, "+")],
                    ),
                ),
                ("fator_rh_diff", models.BooleanField(default=False)),
                ("foto_can_edit", models.BooleanField(default=True)),
                ("foto_diff", models.BooleanField(default=False)),
                ("grau_instrucao_can_edit", models.BooleanField(default=True)),
                (
                    "grau_instrucao",
                    models.IntegerField(
                        default=8,
                        null=True,
                        verbose_name="Grau de Instru\xe7\xe3o",
                        blank=True,
                        choices=[
                            (1, "ANALFABETO"),
                            (2, "ALFABETIZADO SEM CURSOS REGULARES"),
                            (3, "SERA EXCLUIDO 4"),
                            (4, "FUNDAMENTAL COMPLETO"),
                            (5, "M\xc9DIO INCOMPLETO"),
                            (6, "MEDIO COMPLETO OU EQUIVALENTE LEGAL"),
                            (7, "SUPERIOR INCOMPLETO"),
                            (8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"),
                            (9, "ESPECIALIZA\xc7\xc3O/P\xd3S"),
                            (10, "MESTRADO"),
                            (11, "DOUTORADO"),
                            (12, "SERA EXCLUIDO"),
                            (13, "SERA EXCLUIDO 1"),
                            (14, "SERA EXCLUIDO 2"),
                            (15, "AT\xc9 O 5o ANO INCOMPLETO DO ENSINO FUNDAMENTAL"),
                            (16, "5o ANO COMPLETO DO ENSINO FUNDAMENTAL"),
                            (17, "DO 6o AO 9o ANO DO ENSINO FUNDAMENTAL INCOMPLETO"),
                            (18, "N\xc3O INFORMADO"),
                        ],
                    ),
                ),
                ("grau_instrucao_diff", models.BooleanField(default=False)),
                ("municipio_naturalidade_can_edit", models.BooleanField(default=True)),
                ("municipio_naturalidade_diff", models.BooleanField(default=False)),
                ("nis_can_edit", models.BooleanField(default=True)),
                (
                    "nis",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="NIS",
                        blank=True,
                    ),
                ),
                ("nis_diff", models.BooleanField(default=False)),
                ("nome_can_edit", models.BooleanField(default=True)),
                (
                    "nome",
                    models.CharField(
                        default="", max_length=100, verbose_name="Nome", blank=True
                    ),
                ),
                ("nome_diff", models.BooleanField(default=False)),
                ("nome_doc_digital_required", models.BooleanField(default=True)),
                (
                    "nome_conjuge",
                    models.CharField(
                        max_length=80,
                        null=True,
                        verbose_name="Nome C\xf4njuge",
                        blank=True,
                    ),
                ),
                ("nome_conjuge_diff", models.BooleanField(default=False)),
                ("nome_conjuge_can_edit", models.BooleanField(default=True)),
                (
                    "nome_mae",
                    models.CharField(
                        max_length=80, null=True, verbose_name="Nome M\xe3e", blank=True
                    ),
                ),
                ("nome_mae_diff", models.BooleanField(default=False)),
                ("nome_mae_can_edit", models.BooleanField(default=True)),
                (
                    "nome_pai",
                    models.CharField(
                        max_length=80, null=True, verbose_name="Nome Pai", blank=True
                    ),
                ),
                ("nome_pai_can_edit", models.BooleanField(default=True)),
                ("nome_pai_diff", models.BooleanField(default=False)),
                ("pis_pasep_can_edit", models.BooleanField(default=True)),
                (
                    "pis_pasep",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="PIS/PASEP",
                        blank=True,
                    ),
                ),
                ("pis_pasep_diff", models.BooleanField(default=False)),
                ("raca_cor_can_edit", models.BooleanField(default=True)),
                (
                    "raca_cor",
                    models.IntegerField(
                        default=5,
                        null=True,
                        verbose_name="Ra\xe7a/Cor",
                        choices=[
                            (1, "PARDA"),
                            (2, "AMARELA"),
                            (3, "NEGRA"),
                            (4, "IND\xcdGENA"),
                            (5, "N\xc3O INFORMADO"),
                            (6, "BRANCA"),
                        ],
                    ),
                ),
                ("raca_cor_diff", models.BooleanField(default=False)),
                ("reservista_can_edit", models.BooleanField(default=True)),
                (
                    "reservista",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="Reservista",
                        blank=True,
                    ),
                ),
                ("reservista_diff", models.BooleanField(default=False)),
                (
                    "classe_reservista",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="Reservista - Classe",
                        blank=True,
                    ),
                ),
                ("classe_reservista_diff", models.BooleanField(default=False)),
                ("rg_can_edit", models.BooleanField(default=True)),
                (
                    "rg",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RG",
                        blank=True,
                    ),
                ),
                ("rg_diff", models.BooleanField(default=False)),
                (
                    "rg_data_expedicao",
                    models.DateField(
                        null=True,
                        verbose_name="RG - Data da Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("rg_data_expedicao_diff", models.BooleanField(default=False)),
                (
                    "rg_orgao",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RG - Org\xe3o",
                        blank=True,
                    ),
                ),
                ("rg_orgao_diff", models.BooleanField(default=False)),
                ("rg_uf_diff", models.BooleanField(default=False)),
                ("ric_can_edit", models.BooleanField(default=True)),
                (
                    "ric",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RIC",
                        blank=True,
                    ),
                ),
                ("ric_diff", models.BooleanField(default=False)),
                (
                    "ric_expedition_date",
                    models.DateField(
                        null=True,
                        verbose_name="RIC - Data da Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("ric_expedition_date_diff", models.BooleanField(default=False)),
                (
                    "ric_issuer",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RIC - Org\xe3o Emissor",
                        blank=True,
                    ),
                ),
                ("ric_issuer_diff", models.BooleanField(default=False)),
                ("ric_state_diff", models.BooleanField(default=False)),
                ("rne_can_edit", models.BooleanField(default=True)),
                (
                    "rne",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RNE",
                        blank=True,
                    ),
                ),
                ("rne_diff", models.BooleanField(default=False)),
                (
                    "rne_expedition_date",
                    models.DateField(
                        null=True,
                        verbose_name="RNE - Data da Expedi\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("rne_expedition_date_diff", models.BooleanField(default=False)),
                (
                    "rne_issuer",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="RNE - Org\xe3o Emissor",
                        blank=True,
                    ),
                ),
                ("rne_issuer_diff", models.BooleanField(default=False)),
                ("rne_state_diff", models.BooleanField(default=False)),
                ("sangue_can_edit", models.BooleanField(default=True)),
                (
                    "sangue",
                    models.IntegerField(
                        default=4,
                        blank=True,
                        verbose_name="Tipo Sangu\xedneo",
                        choices=[(1, "B"), (2, "AB"), (3, "O"), (4, "A")],
                    ),
                ),
                ("sangue_diff", models.BooleanField(default=False)),
                ("sexo_can_edit", models.BooleanField(default=True)),
                (
                    "sexo",
                    models.CharField(
                        blank=True,
                        max_length=1,
                        null=True,
                        verbose_name="Sexo",
                        choices=[("M", "MASCULINO"), ("F", "FEMININO")],
                    ),
                ),
                ("sexo_diff", models.BooleanField(default=False)),
                ("sexual_orientation_can_edit", models.BooleanField(default=True)),
                (
                    "sexual_orientation",
                    models.PositiveSmallIntegerField(
                        default=5,
                        null=True,
                        verbose_name="Orienta\xe7\xe3o Sexual",
                        blank=True,
                        choices=[
                            (1, "HETEROSSEXUAL"),
                            (2, "HOMOSSEXUAL"),
                            (3, "BISSEXUAL"),
                            (4, "ASSEXUAL"),
                            (5, "N\xc3O INFORMADA"),
                        ],
                    ),
                ),
                ("sexual_orientation_diff", models.BooleanField(default=False)),
                ("social_name_can_edit", models.BooleanField(default=True)),
                (
                    "social_name",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Nome Social",
                        blank=True,
                    ),
                ),
                ("social_name_diff", models.BooleanField(default=False)),
                ("titulo_eleitor_can_edit", models.BooleanField(default=True)),
                (
                    "titulo_eleitor",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="T\xedtulo Eleitor",
                        blank=True,
                    ),
                ),
                ("titulo_eleitor_diff", models.BooleanField(default=False)),
                ("municipio_titulo_diff", models.BooleanField(default=False)),
                (
                    "secao_titulo",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="T\xedtulo de Eleitor - Se\xe7\xe3o",
                        blank=True,
                    ),
                ),
                ("secao_titulo_diff", models.BooleanField(default=False)),
                (
                    "zona_titulo",
                    models.CharField(
                        default="",
                        max_length=30,
                        null=True,
                        verbose_name="T\xedtulo de Eleitor - Zona",
                        blank=True,
                    ),
                ),
                ("zona_titulo_diff", models.BooleanField(default=False)),
                (
                    "address_city",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Endere\xe7o - Cidade",
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "cnh_state",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="CNH - Estado",
                        blank=True,
                        to="rh.Estado",
                        null=True,
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
                    "ctps_state",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="CTPS - Estado",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "employee",
                    models.ForeignKey(
                        to="rh.Servidor", on_delete=django.db.models.deletion.PROTECT
                    ),
                ),
                (
                    "foto",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Foto",
                        blank=True,
                        to="ged.Arquivo",
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
                    "municipio_naturalidade",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Naturalidade",
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "municipio_titulo",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="T\xedtulo de Eleitor - Municipio",
                        blank=True,
                        to="rh.Localidade",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "professional_council_state",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="Conselho Profissional - Estado",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "received_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "rg_uf",
                    models.ForeignKey(
                        verbose_name="RG - UF",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ric_state",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="RIC - Estado",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "rne_state",
                    models.ForeignKey(
                        related_name="+",
                        verbose_name="RNE - Estado",
                        blank=True,
                        to="rh.Estado",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "sent_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "validated_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("sent_at",),
                "verbose_name": "Formul\xe1rio de Informa\xe7\xf5es - Recadastramento",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Validation",
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
                ("text", models.TextField(null=True, blank=True)),
                (
                    "state",
                    models.IntegerField(default=5, verbose_name="Estado", blank=True),
                ),
                (
                    "validated_at",
                    models.DateTimeField(default=None, null=True, blank=True),
                ),
                (
                    "fi_sent_at",
                    models.DateTimeField(default=None, null=True, blank=True),
                ),
                (
                    "fi_received_at",
                    models.DateTimeField(default=None, null=True, blank=True),
                ),
                (
                    "annotation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                    ),
                ),
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
                    "fi_received_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "fi_sent_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
                (
                    "form_information",
                    models.ForeignKey(
                        to="registration.FormInformation",
                        on_delete=django.db.models.deletion.PROTECT,
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
                    "validated_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "verbose_name": "Valida\xe7\xe3o de Recadastramento Funcional",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="form_information",
            field=models.ForeignKey(
                related_name="digital_documents",
                blank=True,
                to="registration.FormInformation",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="digitaldocument",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
