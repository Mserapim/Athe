# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0043_auto_20170427_1353"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocsDataSpecificSpecialized",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("rh.docsdadosespecificos",),
        ),
        migrations.CreateModel(
            name="DocumentSpecialized",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("rh.documento",),
        ),
        migrations.CreateModel(
            name="NaturalPersonSpecialized",
            fields=[],
            options={
                "proxy": True,
            },
            bases=("rh.pessoafisica",),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="capacidade",
            field=models.IntegerField(
                default=1, null=True, choices=[(1, "V\xc1LIDO"), (2, "INV\xc1LIDO")]
            ),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="tipo",
            field=models.IntegerField(
                null=True,
                verbose_name="Tipo",
                choices=[
                    (1, "C\xd4NJUGE"),
                    (2, "COMPANHEIRO(A)"),
                    (3, "FILHO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS"),
                    (4, "FILHO INV\xc1LIDO(A) ABSOLUTAMENTE INCAPAZ, TUTOR/CURADOR"),
                    (5, "PAI(M\xc3E) COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (
                        6,
                        "IRM\xc3O N\xc3O EMANCIPADO MENOR DE 21 ANOS E GUARDA JUDICIAL",
                    ),
                    (7, "IRM\xc3O(A) ABSOLUTAMENTE INCAPAZ, TUTOR/CURADOR"),
                    (8, "ENTEADO N\xc3O EMANCIPADO MENOR DE 21"),
                    (9, "ENTEADO ABSOLUTAMENTE INCAPAZ, TUTOR/CURADOR"),
                    (
                        10,
                        "MENORTUTELADO \xd1 EMANCIPADO < 21 DEPEND\xcaNCIAECON\xd4MICA/GUARDA",
                    ),
                    (11, "MENOR ABSOLUTAMENTE INCAPAZ DO QUAL SEJA TUTOR OU CURADOR"),
                    (12, "AV\xd3S COM DEPENDENCIA ECONOMICA"),
                    (13, "BISAV\xd3S COM DEPENDENCIA ECONOMICA"),
                    (
                        14,
                        "NETO(A)\xd1EMANCIPADO<21 DEPEND\xcaNCIAECON\xd4MICA E GUARDAJUDICIAL",
                    ),
                    (
                        15,
                        "BISNETO(A)\xd1EMANCIPADO<21DEPEND\xcaNCIAECON\xd4MICA EGUARDAJUDICIAL",
                    ),
                    (16, " EX-C\xd4NJUGE"),
                    (
                        17,
                        "FILHO/ENTEADOUNIVERSIT\xc1RIO/CURSANDOESCT\xc9CNICA2\xbaGRAUAT\xc924ANOS",
                    ),
                    (18, "AGREGADO/OUTROS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="docsdadosespecificos",
            name="especificidade",
            field=models.IntegerField(
                verbose_name="Especificidade",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR.ZONA"),
                    (2, "T\xcdTULO DE ELEITOR.SE\xc7\xc3O"),
                    (3, "T\xcdTULO DE ELEITOR.UF"),
                    (4, "CNH.CATEGORIA"),
                    (5, "RESERVISTA.CLASSE"),
                    (6, "CTPS.S\xc9RIE"),
                    (7, "T\xcdTULO DE ELEITOR.MUNICIPIO"),
                    (8, "CTPS.UF"),
                    (9, "RIC.EMISSOR"),
                    (10, "RNE.EMISSOR"),
                    (11, "CONSELHO PROFISSIONAL.EMISSOR"),
                    (12, "CNH.DATA PRIMEIRA HABILITA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo de Documento",
                choices=[
                    (1, "T\xcdTULO DE ELEITOR"),
                    (2, "CNH"),
                    (3, "CTPS"),
                    (5, "NIS"),
                    (6, "PIS/PASEP"),
                    (7, "IPSEP"),
                    (8, "INSS"),
                    (9, "RESERVISTA"),
                    (10, "CONSELHO PROFISSIONAL"),
                    (11, "RIC"),
                    (12, "RNE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="employeeworkplacehistory",
            name="employee_workplace",
            field=models.ForeignKey(
                related_name="history_servidor_lotacao",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="employeeworkplacehistory",
            name="lotacao",
            field=models.ForeignKey(
                related_name="history_servidores_lotacao",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Lota\xe7\xe3o/Designa\xe7\xe3o",
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="employeeworkplacehistory",
            name="movimentacao_posse",
            field=models.ForeignKey(
                related_name="history_lotacoes",
                on_delete=django.db.models.deletion.SET_NULL,
                to="rh.MovimentacaoPosse",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="endereco",
            name="tipo_endereco",
            field=models.IntegerField(
                verbose_name="Tipo do Endere\xe7o",
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
        migrations.AlterField(
            model_name="endereco",
            name="tipo_logradouro",
            field=models.IntegerField(
                verbose_name="Tipo do Logradouro",
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
        migrations.AlterField(
            model_name="foreigninformation",
            name="classification_permanence",
            field=models.IntegerField(
                default=1,
                verbose_name="Classifica\xe7\xe3o de ingresso",
                choices=[
                    (1, "Visto permanente"),
                    (2, "Visto tempor\xe1rio"),
                    (3, "Asilado"),
                    (4, "Refugiado"),
                    (5, "Solicitante de Ref\xfagio"),
                    (6, "Residente em pa\xeds fronteiri\xe7o ao Brasil"),
                    (7, "Deficiente f\xedsico e com mais de 51 anos"),
                    (
                        8,
                        "Com resid\xeancia provis\xf3ria e anistiado, em situa\xe7\xe3o",
                    ),
                    (9, "Perman\xeancia no Brasil em raz\xe3o de filhos ou c\xf4njuge"),
                    (10, "Beneficiado pelo acordo entre pa\xedses do Mercosul"),
                    (11, "Dependente de agente diplom\xe1tico e/ou consular"),
                    (12, "Beneficiado pelo Tratado de Amizade, Coopera\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="necessidadeespecial",
            name="deficiency_type",
            field=models.PositiveSmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de defici\xeancia",
                blank=True,
                choices=[
                    (1, "F\xedsica"),
                    (2, "Visual"),
                    (3, "Auditiva"),
                    (4, "Mental"),
                    (5, "Intelectual"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="estado_civil",
            field=models.IntegerField(
                default=1,
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
        migrations.AlterField(
            model_name="pessoafisica",
            name="grau_instrucao",
            field=models.IntegerField(
                default=8,
                blank=True,
                verbose_name="Grau de Instru\xe7\xe3o",
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
                    (15, "At\xe9 o 5o ano incompleto do Ensino Fundamental"),
                    (16, "5o ano completo do Ensino Fundamental"),
                    (17, "Do 6o ao 9o ano do Ensino Fundamental incompleto"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="raca_cor",
            field=models.IntegerField(
                default=5,
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
        migrations.AlterField(
            model_name="telefone",
            name="tipo_telefone",
            field=models.IntegerField(
                verbose_name="Tipo de Telefone",
                choices=[
                    (1, "RESIDENCIAL"),
                    (2, "COMERCIAL"),
                    (3, "CELULAR"),
                    (4, "FAX"),
                    (5, "INSTITUCIONAL"),
                ],
            ),
        ),
    ]
