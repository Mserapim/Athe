# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0053_auto_20171124_1149"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnotacaoBancoDeHoras",
            fields=[
                (
                    "anotacaogeral_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="rh.AnotacaoGeral",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "data_inicio",
                    models.DateField(
                        null=True, verbose_name="Data In\xedcio", blank=True
                    ),
                ),
                (
                    "data_fim",
                    models.DateField(null=True, verbose_name="Data Fim", blank=True),
                ),
            ],
            options={
                "db_table": "rh_anotbancodehoras",
                "verbose_name": "Anota\xe7\xe3o Usufruto Banco de Horas",
            },
            bases=("rh.anotacaogeral",),
        ),
        migrations.AlterField(
            model_name="movimentacaoremocao",
            name="remocao",
            field=models.IntegerField(
                verbose_name="Remo\xe7\xe3o",
                choices=[(1, "OF\xcdCIO"), (2, "REQUERIMENTO"), (3, "PERMUTA")],
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
                    ("ATIVO_USU_BANCO_DE_HORAS", "Ativo: Fruindo Folga Banco de Horas"),
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
                    ("ATIVO_USU_BANCO_DE_HORAS", "Ativo: Fruindo Folga Banco de Horas"),
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
    ]
