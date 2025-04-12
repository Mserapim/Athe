# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0042_auto_20170330_1604"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeficiencyInformation",
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
                    "rehabilitation",
                    models.BooleanField(
                        default=False, verbose_name="Reabilita\xe7\xe3o"
                    ),
                ),
                (
                    "quota",
                    models.BooleanField(
                        default=False, verbose_name="Pertencente a cota"
                    ),
                ),
                ("note", models.TextField(null=True, blank=True)),
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Informa\xe7\xf5es de defici\xeancia",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ForeignInformation",
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
                    "classification_permanence",
                    models.IntegerField(
                        default=1, verbose_name="Classifica\xe7\xe3o de ingresso"
                    ),
                ),
                ("date_arrived", models.DateField(verbose_name="Data de chegada")),
                (
                    "married_br",
                    models.BooleanField(
                        default=False, verbose_name="Casado(a) com brasileiro(a)"
                    ),
                ),
                (
                    "son_br",
                    models.BooleanField(
                        default=False, verbose_name="Filhos brasileiros"
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Informa\xe7\xf5es de Estrangeiro",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="dependente",
            name="incapacity",
            field=models.BooleanField(
                default=False, verbose_name="Incapacidade f\xedsica/mental"
            ),
        ),
        migrations.AddField(
            model_name="endereco",
            name="country",
            field=models.ForeignKey(
                related_name="address",
                verbose_name="Pa\xeds(Residentes no Exterior) ",
                blank=True,
                to="rh.Pais",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="endereco",
            name="outsider",
            field=models.BooleanField(default=False, verbose_name="Exterior"),
        ),
        migrations.AddField(
            model_name="necessidadeespecial",
            name="deficiency_type",
            field=models.PositiveSmallIntegerField(
                default=1, null=True, verbose_name="Tipo de defici\xeancia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo Documento",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                    (101, "PORTARIA DE INSTAURA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="capacidade",
            field=models.IntegerField(default=1, null=True),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="tipo",
            field=models.IntegerField(null=True, verbose_name="Tipo"),
        ),
        migrations.AlterField(
            model_name="docsdadosespecificos",
            name="especificidade",
            field=models.IntegerField(verbose_name="Especificidade"),
        ),
        migrations.AlterField(
            model_name="documento",
            name="dados_especificos",
            field=models.ManyToManyField(
                related_name="documentos",
                null=True,
                verbose_name="Dados Espec\xedficos",
                to="rh.DocsDadosEspecificos",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="tipo_documento",
            field=models.IntegerField(verbose_name="Tipo de Documento"),
        ),
        migrations.AlterField(
            model_name="endereco",
            name="tipo_endereco",
            field=models.IntegerField(verbose_name="Tipo do Endere\xe7o"),
        ),
        migrations.AlterField(
            model_name="endereco",
            name="tipo_logradouro",
            field=models.IntegerField(verbose_name="Tipo do Logradouro"),
        ),
        migrations.AlterField(
            model_name="movimentacaoaposentadoria",
            name="reversao",
            field=models.IntegerField(
                default=2,
                verbose_name="Revers\xe3o",
                choices=[(1, "Sim"), (2, "N\xe3o")],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaoaposentadoria",
            name="tipo_aposentadoria",
            field=models.IntegerField(
                default=1,
                choices=[
                    (1, "COMPULS\xd3RIA"),
                    (2, "ESPECIAL"),
                    (3, "IMPLEMENTO DE IDADE"),
                    (4, "INVALIDEZ"),
                    (5, "TEMPO DE CONTRIBUI\xc7\xc3O"),
                    (6, "VOLUNT\xc1RIA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaodesligamento",
            name="tipo_desligamento",
            field=models.IntegerField(
                default=1,
                verbose_name="Tipo de Desligamento",
                choices=[
                    (1, "EXONERA\xc7\xc3O EFETIVO"),
                    (2, "EXONERA\xc7\xc3O COMISSIONADO"),
                    (3, "EXONERA\xc7\xc3O ESTABILIZADO"),
                    (4, "APOSENTADORIA POR INVALIDEZ"),
                    (5, "APOSENTADORIA VOLUNT\xc1RIA"),
                    (6, "POSSE EM OUTRO CARGO"),
                    (7, "FALECIMENTO"),
                    (8, "RESCIS\xc3O"),
                    (9, "DEMISS\xc3O"),
                    (10, "RESERVA REFORMA"),
                    (11, "DISPONIBILIDADE"),
                    (12, "PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                    (13, "FIM REQUISI\xc7\xc3O/ACORDO COOPERA\xc7\xc3O"),
                    (14, "APOSENTADORIA COMPULS\xd3RIA"),
                    (15, "APOSENTADORIA ESPECIAL"),
                    (16, "APOSENTADORIA POR TEMPO DE CONTRIBUI\xc7\xc3O"),
                    (17, "APOSENTADORIA POR IDADE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaoposse",
            name="tipo_movcarreira",
            field=models.CharField(
                default="NOMEACAO",
                max_length=30,
                verbose_name="Provimento",
                choices=[
                    ("TITULARIZACAO", "Titulariza\xe7\xe3o"),
                    ("REVERSAO", "Revers\xe3o"),
                    ("READAPTACAO", "Readapta\xe7\xe3o"),
                    ("NOMEACAO", "Nomea\xe7\xe3o"),
                    ("PROMOCAO", "Promo\xe7\xe3o"),
                    ("APROVEITAMENTO", "Aproveitamento"),
                    ("REMOCAO", "Remo\xe7\xe3o"),
                    ("ENQUADRAMENTO", "Enquadramento"),
                    ("RECONDUCAO", "Recondu\xe7\xe3o"),
                    ("REINTEGRACAO", "Reintegra\xe7\xe3o"),
                    ("PROGRESSAO", "Progress\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaoremocao",
            name="remocao",
            field=models.IntegerField(verbose_name="Remo\xe7\xe3o"),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="documento",
            field=models.ManyToManyField(
                related_name="naturalpersons", null=True, to="rh.Documento", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="estado_civil",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="grau_instrucao",
            field=models.IntegerField(
                default=8, verbose_name="Grau de Instru\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="raca_cor",
            field=models.IntegerField(default=5, verbose_name="Ra\xe7a/Cor"),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(
                verbose_name="Tipo de Publica\xe7\xe3o",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                    (101, "PORTARIA DE INSTAURA\xc7\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="situacao_funcional_cache",
            field=models.CharField(
                default="NOT_FOUND",
                max_length=40,
                choices=[
                    ("ATIVO_FOLGA_ELEITORAL", "Ativo: Fruindo Folga Eleitoral"),
                    (
                        "ATIVO_AFA_OUT_ORG_ONUS_MP",
                        "Ativo: Afastado - Servir a outro \xd3rg\xe3o com \xf4nus para o MP",
                    ),
                    (
                        "INATIVO_DEVOLVIDO",
                        "Inativo: Devolvido ao \xd3rg\xe3o de Origem",
                    ),
                    ("ATIVO_AFA_PRISAO", "Ativo: Afastado - Pris\xe3o"),
                    (
                        "INATIVO_OUTRO_CARGO",
                        "Inativo: Posse em outro cargo inacumul\xe1vel",
                    ),
                    (
                        "ATIVO_AFA_ESTUDAR",
                        "Ativo: Afastado - Estudar no Pa\xeds/Exterior",
                    ),
                    ("ATIVO_LIC_SAUDE", "Ativo: Licenciado - Tratamento de Sa\xfade"),
                    ("ATIVO_AFA_SUSPENSAO", "Ativo: Afastado - Suspens\xe3o"),
                    ("ATIVO_AUS_FALECIMENTO", "Ativo: Ausente - Falecimento"),
                    (
                        "ATIVO_AFA_CURSO_CONCURSO",
                        "Ativo: Afastado - Curso de forma\xe7\xe3o de etapa de concurso p\xfablico",
                    ),
                    (
                        "ATIVO_AFA_MISSAO",
                        "Ativo: Afastado - Miss\xe3o Oficial no Exterior",
                    ),
                    (
                        "ATIVO_ATUACAO_GRUPO_TRAB",
                        "Ativo: Atua\xe7\xe3o em Grupo de Trabalho",
                    ),
                    (
                        "ATIVO_AFA_ELETIVO",
                        "Ativo: Afastado - Exerc\xedcio de Mandato Eletivo",
                    ),
                    ("ATIVO_FERIAS", "Ativo: Fruindo F\xe9rias"),
                    (
                        "ATIVO_LIC_DOENCA",
                        "Ativo: Licenciado - Doen\xe7a em Pessoa da Fam\xedlia",
                    ),
                    (
                        "ATIVO_LIC_AFAST_CONJUGE",
                        "Ativo: Licenciado - Afastamento do Conjuge/Companheiro",
                    ),
                    ("ATIVO_RECESSO", "Ativo: Fruindo Recesso"),
                    ("ATIVO_LIC_MILITAR", "Ativo: Licenciado - Servi\xe7o Militar"),
                    ("ATIVO_AUS_SANGUE", "Ativo: Ausente - Doa\xe7\xe3o de sangue"),
                    ("ATIVO_VIAGEM", "Ativo: Viagem a Servi\xe7o"),
                    ("ATIVO_AUS_ELEITOR", "Ativo: Ausente - Alistamento como eleitor"),
                    ("INATIVO_APO_IDADE", "Inativo: Aposentado - Por idade"),
                    (
                        "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
                        "Ativo: Afastado - Servir a outro \xd3rg\xe3o sem \xf4nus para o MP",
                    ),
                    ("ATIVO_AUS_CASAMENTO", "Ativo: Ausente - Casamento"),
                    ("INATIVO_DEMITIDO", "Inativo: Demitido"),
                    (
                        "ATIVO_LIC_INTERESSE",
                        "Ativo: Licenciado - Tratar de Interesse Particular",
                    ),
                    ("INATIVO_FALECIDO", "Inativo: Falecido"),
                    ("ATIVO_AFA_JURI", "Ativo: Afastado - Servir no Tribunal do Juri"),
                    ("INATIVO_APO_VOLUNTARIO", "Inativo: Aposentado - Volunt\xe1rio"),
                    (
                        "ATIVO_LIC_CAPACITACAO",
                        "Ativo: Licenciado - Capacita\xe7\xe3o ou Especializa\xe7\xe3o (3 meses por quinqu\xeanio)",
                    ),
                    (
                        "ATIVO_FOLGA_COMPENSACAO",
                        "Ativo: Fruindo Folga Compensa\xe7\xe3o",
                    ),
                    ("ATIVO", "Ativo: Em atividade"),
                    (
                        "ATIVO_AFA_DESLOCAMENTO",
                        "Ativo: Afastado - Deslocamento at\xe9 a nova sede",
                    ),
                    (
                        "ATIVO_AUS_CONCLUSAO",
                        "Ativo: Ausente - Finaliza\xe7\xe3o de trabalho de conclus\xe3o de curso",
                    ),
                    (
                        "ATIVO_AFA_TREINAMENTO",
                        "Ativo: Afastado - Treinamento (Palestras/Congressos/Semin\xe1rios/Outros)",
                    ),
                    ("ATIVO_LIC_POLITICA", "Ativo: Licenciado - Atividade Pol\xedtica"),
                    (
                        "ATIVO_AFA_COMPETICAO",
                        "Ativo: Afastado - Competi\xe7\xe3o desportiva ou representa\xe7\xe3o cultural",
                    ),
                    ("ATIVO_LIC_ADOCAO", "Ativo: Licenciado - Tutoria ou Ado\xe7\xe3o"),
                    ("ATIVO_DESEMPENHO_FUNCAO", "Ativo: Desempenho de Fun\xe7\xe3o"),
                    (
                        "ATIVO_AFA_ELEITORAL",
                        "Ativo: Afastado - Convoca\xe7\xe3o da Justi\xe7a Eleitoral",
                    ),
                    ("INATIVO_APO_COMPULSORIO", "Inativo: Aposentado - Compuls\xf3rio"),
                    ("ATIVO_LIC_MATERNIDADE", "Ativo: Licenciado - Maternidade"),
                    (
                        "ATIVO_AFA_DISPONIBILIDADE",
                        "Ativo: Afastado - Em disponibilidade",
                    ),
                    ("INATIVO_APO_INVALIDEZ", "Inativo: Aposentado - Por invalidez"),
                    ("NOT_FOUND", "N\xe3o encontrado"),
                    ("INATIVO_APO_ESPECIAL", "Inativo: Aposentado - Especial"),
                    ("ATIVO_AFA_COMPJUIZO", "Ativo: Afastado - Comparecer a ju\xedzo"),
                    (
                        "INATIVO_APO_TEMPO_CONTRIBUICAO",
                        "Inativo: Aposentado - Por tempo de contribui\xe7\xe3o",
                    ),
                    (
                        "ATIVO_DISPONIBILIDADE",
                        "Ativo: - Em disponibilidade(com onus para origem ou para requisitante?)",
                    ),
                    ("INATIVO_EXONERADO_OFICIO", "Inativo: Exonerado - De of\xedcio"),
                    ("ATIVO_PLANTAO", "Ativo: Fruindo Plant\xe3o de Feriado"),
                    (
                        "ATIVO_LIC_CLASSISTA",
                        "Ativo: Licenciado - Desempenho de Mandato Classista",
                    ),
                    ("ATIVO_FOLGA_ANIVERSARIO", "Ativo: Fruindo Folga Anivers\xe1rio"),
                    (
                        "ATIVO_AUS_NASCIMENTO",
                        "Ativo: Ausente - Nascimento/ado\xe7\xe3o de filho",
                    ),
                    ("INATIVO_EXONERADO_PEDIDO", "Inativo: Exonerado - A pedido"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="situacaofuncional",
            name="situacao",
            field=models.CharField(
                default="ATIVO",
                max_length=30,
                choices=[
                    ("ATIVO_FOLGA_ELEITORAL", "Ativo: Fruindo Folga Eleitoral"),
                    (
                        "ATIVO_AFA_OUT_ORG_ONUS_MP",
                        "Ativo: Afastado - Servir a outro \xd3rg\xe3o com \xf4nus para o MP",
                    ),
                    (
                        "INATIVO_DEVOLVIDO",
                        "Inativo: Devolvido ao \xd3rg\xe3o de Origem",
                    ),
                    ("ATIVO_AFA_PRISAO", "Ativo: Afastado - Pris\xe3o"),
                    (
                        "INATIVO_OUTRO_CARGO",
                        "Inativo: Posse em outro cargo inacumul\xe1vel",
                    ),
                    (
                        "ATIVO_AFA_ESTUDAR",
                        "Ativo: Afastado - Estudar no Pa\xeds/Exterior",
                    ),
                    ("ATIVO_LIC_SAUDE", "Ativo: Licenciado - Tratamento de Sa\xfade"),
                    ("ATIVO_AFA_SUSPENSAO", "Ativo: Afastado - Suspens\xe3o"),
                    ("ATIVO_AUS_FALECIMENTO", "Ativo: Ausente - Falecimento"),
                    (
                        "ATIVO_AFA_CURSO_CONCURSO",
                        "Ativo: Afastado - Curso de forma\xe7\xe3o de etapa de concurso p\xfablico",
                    ),
                    (
                        "ATIVO_AFA_MISSAO",
                        "Ativo: Afastado - Miss\xe3o Oficial no Exterior",
                    ),
                    (
                        "ATIVO_ATUACAO_GRUPO_TRAB",
                        "Ativo: Atua\xe7\xe3o em Grupo de Trabalho",
                    ),
                    (
                        "ATIVO_AFA_ELETIVO",
                        "Ativo: Afastado - Exerc\xedcio de Mandato Eletivo",
                    ),
                    ("ATIVO_FERIAS", "Ativo: Fruindo F\xe9rias"),
                    (
                        "ATIVO_LIC_DOENCA",
                        "Ativo: Licenciado - Doen\xe7a em Pessoa da Fam\xedlia",
                    ),
                    (
                        "ATIVO_LIC_AFAST_CONJUGE",
                        "Ativo: Licenciado - Afastamento do Conjuge/Companheiro",
                    ),
                    ("ATIVO_RECESSO", "Ativo: Fruindo Recesso"),
                    ("ATIVO_LIC_MILITAR", "Ativo: Licenciado - Servi\xe7o Militar"),
                    ("ATIVO_AUS_SANGUE", "Ativo: Ausente - Doa\xe7\xe3o de sangue"),
                    ("ATIVO_VIAGEM", "Ativo: Viagem a Servi\xe7o"),
                    ("ATIVO_AUS_ELEITOR", "Ativo: Ausente - Alistamento como eleitor"),
                    ("INATIVO_APO_IDADE", "Inativo: Aposentado - Por idade"),
                    (
                        "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP",
                        "Ativo: Afastado - Servir a outro \xd3rg\xe3o sem \xf4nus para o MP",
                    ),
                    ("ATIVO_AUS_CASAMENTO", "Ativo: Ausente - Casamento"),
                    ("INATIVO_DEMITIDO", "Inativo: Demitido"),
                    (
                        "ATIVO_LIC_INTERESSE",
                        "Ativo: Licenciado - Tratar de Interesse Particular",
                    ),
                    ("INATIVO_FALECIDO", "Inativo: Falecido"),
                    ("ATIVO_AFA_JURI", "Ativo: Afastado - Servir no Tribunal do Juri"),
                    ("INATIVO_APO_VOLUNTARIO", "Inativo: Aposentado - Volunt\xe1rio"),
                    (
                        "ATIVO_LIC_CAPACITACAO",
                        "Ativo: Licenciado - Capacita\xe7\xe3o ou Especializa\xe7\xe3o (3 meses por quinqu\xeanio)",
                    ),
                    (
                        "ATIVO_FOLGA_COMPENSACAO",
                        "Ativo: Fruindo Folga Compensa\xe7\xe3o",
                    ),
                    ("ATIVO", "Ativo: Em atividade"),
                    (
                        "ATIVO_AFA_DESLOCAMENTO",
                        "Ativo: Afastado - Deslocamento at\xe9 a nova sede",
                    ),
                    (
                        "ATIVO_AUS_CONCLUSAO",
                        "Ativo: Ausente - Finaliza\xe7\xe3o de trabalho de conclus\xe3o de curso",
                    ),
                    (
                        "ATIVO_AFA_TREINAMENTO",
                        "Ativo: Afastado - Treinamento (Palestras/Congressos/Semin\xe1rios/Outros)",
                    ),
                    ("ATIVO_LIC_POLITICA", "Ativo: Licenciado - Atividade Pol\xedtica"),
                    (
                        "ATIVO_AFA_COMPETICAO",
                        "Ativo: Afastado - Competi\xe7\xe3o desportiva ou representa\xe7\xe3o cultural",
                    ),
                    ("ATIVO_LIC_ADOCAO", "Ativo: Licenciado - Tutoria ou Ado\xe7\xe3o"),
                    ("ATIVO_DESEMPENHO_FUNCAO", "Ativo: Desempenho de Fun\xe7\xe3o"),
                    (
                        "ATIVO_AFA_ELEITORAL",
                        "Ativo: Afastado - Convoca\xe7\xe3o da Justi\xe7a Eleitoral",
                    ),
                    ("INATIVO_APO_COMPULSORIO", "Inativo: Aposentado - Compuls\xf3rio"),
                    ("ATIVO_LIC_MATERNIDADE", "Ativo: Licenciado - Maternidade"),
                    (
                        "ATIVO_AFA_DISPONIBILIDADE",
                        "Ativo: Afastado - Em disponibilidade",
                    ),
                    ("INATIVO_APO_INVALIDEZ", "Inativo: Aposentado - Por invalidez"),
                    ("NOT_FOUND", "N\xe3o encontrado"),
                    ("INATIVO_APO_ESPECIAL", "Inativo: Aposentado - Especial"),
                    ("ATIVO_AFA_COMPJUIZO", "Ativo: Afastado - Comparecer a ju\xedzo"),
                    (
                        "INATIVO_APO_TEMPO_CONTRIBUICAO",
                        "Inativo: Aposentado - Por tempo de contribui\xe7\xe3o",
                    ),
                    (
                        "ATIVO_DISPONIBILIDADE",
                        "Ativo: - Em disponibilidade(com onus para origem ou para requisitante?)",
                    ),
                    ("INATIVO_EXONERADO_OFICIO", "Inativo: Exonerado - De of\xedcio"),
                    ("ATIVO_PLANTAO", "Ativo: Fruindo Plant\xe3o de Feriado"),
                    (
                        "ATIVO_LIC_CLASSISTA",
                        "Ativo: Licenciado - Desempenho de Mandato Classista",
                    ),
                    ("ATIVO_FOLGA_ANIVERSARIO", "Ativo: Fruindo Folga Anivers\xe1rio"),
                    (
                        "ATIVO_AUS_NASCIMENTO",
                        "Ativo: Ausente - Nascimento/ado\xe7\xe3o de filho",
                    ),
                    ("INATIVO_EXONERADO_PEDIDO", "Inativo: Exonerado - A pedido"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="telefone",
            name="tipo_telefone",
            field=models.IntegerField(verbose_name="Tipo de Telefone"),
        ),
        migrations.AddField(
            model_name="foreigninformation",
            name="naturalperson",
            field=models.OneToOneField(
                related_name="foreigninformation",
                verbose_name="Pessoa",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="deficiencyinformation",
            name="naturalperson",
            field=models.OneToOneField(
                related_name="deficiencyinformation",
                verbose_name="Pessoa",
                to="rh.PessoaFisica",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
