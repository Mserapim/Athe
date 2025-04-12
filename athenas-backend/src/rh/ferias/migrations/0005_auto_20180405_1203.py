# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0004_auto_20170201_1456"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoaquisitivoservidorusufruto",
            name="data_fim_cache",
            field=models.DateField(
                help_text="Data fim da frui\xc3\xa7\xc3\xa3o desse per\xc3\xadodo de f\xc3\xa9rias.",
                null=True,
                verbose_name="Data Fim Cache",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="dias_antecedencia_fruicao",
            field=models.SmallIntegerField(
                default=15,
                help_text="Dias de anteced\xc3\xaancia entre a marca\xc3\xa7\xc3\xa3o/altera\xc3\xa7\xc3\xa3o e a frui\xc3\xa7\xc3\xa3o",
                verbose_name="Anteced\xeancia frui\xe7\xe3o (dias)",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="dias_por_periodo",
            field=models.SmallIntegerField(
                default="30",
                help_text="Quantidade de dias m\xc3\xa1xima que pode ser usufru\xc3\xaddo em um per\xc3\xadodo.",
                verbose_name="Dias por per\xedodo",
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="max_divisoes",
            field=models.SmallIntegerField(
                default=2,
                help_text="Quantidade m\xc3\xa1xima de divis\xc3\xb5es que um per\xc3\xadodo de f\xc3\xa9rias pode ser usufru\xc3\xaddo.",
                verbose_name="M\xe1ximo de divis\xf5es",
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="meses_exercicio",
            field=models.SmallIntegerField(
                default=12,
                help_text="Tempo de exerc\xc3\xadcio, em meses, para adquirir direito a frui\xc3\xa7\xc3\xa3o de um periodo de f\xc3\xa9rias",
                verbose_name="Tempo de exerc\xedcio (meses)",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="meses_max_fruicao",
            field=models.SmallIntegerField(
                default=12,
                help_text="Tempo m\xc3\xa1ximo (em meses) para o gozo dos dias de f\xc3\xa9rias. OBS.: XX meses - 1 dia",
                verbose_name="M\xe1ximo frui\xe7\xe3o (meses)",
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="meses_prescricao",
            field=models.SmallIntegerField(
                default=24,
                help_text="Tempo m\xc3\xa1ximo (em meses) para o gozo dos dias de f\xc3\xa9rias, antes de prescreverem.",
                verbose_name="Prescri\xe7\xe3o (meses)",
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="min_dias_por_divisao",
            field=models.SmallIntegerField(
                default="10",
                help_text="Quantidade m\xc3\xadnima de dias que pode ser dividida o per\xc3\xadodo de usufruto.",
                verbose_name="Quantidade m\xednimo de dias por divis\xe3o",
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="modo",
            field=models.CharField(
                default="CONTINUO",
                help_text="Modo de avalia\xc3\xa7\xc3\xa3o do per\xc3\xadodo aquisitivo. ANUAL: per\xc3\xaddo por ano. CONTINUO: per\xc3\xadodo de acordo com a data de exerc\xc3\xadcio do servidor.",
                max_length=30,
                verbose_name="Modo de aquisi\xe7\xe3o",
                choices=[("CONTINUO", "Cont\xc3\xadnuo"), ("ANUAL", "Anual")],
            ),
        ),
        migrations.AlterField(
            model_name="configuracao",
            name="quantidade_periodos",
            field=models.SmallIntegerField(
                default=1,
                help_text="Quantidade de per\xc3\xadodos em um ano (12 meses).Ex.: Servidor = 1 periodo por ano (12 meses), Membro= 2 per\xc3\xadodos por ano",
                verbose_name="Per\xedodos",
                choices=[
                    (1, "\xdanico"),
                    (2, "Semestre"),
                    (3, "Quadrimestre"),
                    (4, "Trimestre"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="ano_aquisicao",
            field=models.SmallIntegerField(
                help_text="Ano de aquisi\xe7\xe3o do per\xedodo",
                verbose_name="Ano de aquisi\xe7\xe3o",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="configuracao",
            field=models.ForeignKey(
                verbose_name="Configura\xe7\xe3o de f\xe9rias",
                to="ferias.Configuracao",
                help_text="A configura\xc3\xa7\xc3\xa3o de f\xc3\xa9rias utilizado para esse per\xc3\xadodo aquisitivo.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="data_fim_prev",
            field=models.DateField(
                help_text="Data para finaliza\xc3\xa7\xc3\xa3o das marca\xc3\xa7\xc3\xb5es de f\xc3\xa9rias.",
                null=True,
                verbose_name="Final de Previs\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="data_homologacao_prev",
            field=models.DateField(
                help_text="Data prevista para homologa\xc3\xa7\xc3\xa3o do per\xc3\xadodo aquisitivo.",
                null=True,
                verbose_name="Data de Homologa\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="data_inicio_prev",
            field=models.DateField(
                help_text="Data para in\xc3\xadcio das marca\xc3\xa7\xc3\xb5es de f\xc3\xa9rias.",
                verbose_name="In\xedcio de Previs\xe3o",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="data_publicacao",
            field=models.DateTimeField(
                help_text="Data em que o per\xedodo aquisitivo foi publicado.",
                null=True,
                verbose_name="Data de Publica\xe7\xe3o",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="mes_fruicao",
            field=models.SmallIntegerField(
                blank=True,
                help_text="M\xc3\xaas para frui\xc3\xa7\xc3\xa3o coletiva, caso haja",
                null=True,
                verbose_name="M\xeas de frui\xe7\xe3o",
                choices=[
                    (1, "JANEIRO"),
                    (2, "FEVEREIRO"),
                    (3, "MAR\xc7O"),
                    (4, "ABRIL"),
                    (5, "MAIO"),
                    (6, "JUNHO"),
                    (7, "JULHO"),
                    (8, "AGOSTO"),
                    (9, "SETEMBRO"),
                    (10, "OUTUBRO"),
                    (11, "NOVEMBRO"),
                    (12, "DEZEMBRO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivo",
            name="periodo",
            field=models.SmallIntegerField(
                default=1,
                help_text="Per\xedodo (\xfanico/semestre/quadrimestre) do ano que gerou esse per\xedodo aquisitivo quando as f\xe9rias s\xe3o anuais. Ex.: 2 -> para f\xe9rias anuais com per\xedodo aquisitivo no segundo semestre do ano.",
                verbose_name="Per\xedodo",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="bloqueado",
            field=models.BooleanField(
                default=False,
                help_text="Informa se o PAS pode ser manipulado por algu\xe9m, normalmente \xe9 bloqueado quando se cria um per\xedodo anterior.",
                verbose_name="Bloqueado",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="data_fim_aquisicao",
            field=models.DateField(
                help_text="Data de referencia para o calculo do per\xedodo aquisitivo .",
                verbose_name="Fim aquisi\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="data_fim_usufruto",
            field=models.DateField(
                help_text="Data m\xe1xima para que se possa usufruir esse per\xedodo.",
                null=True,
                verbose_name="Fim usufruto",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="data_inicio_aquisicao",
            field=models.DateField(
                help_text="", verbose_name="In\xedcio aquisi\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="data_inicio_usufruto",
            field=models.DateField(
                help_text="Data m\xednima para que se possa usufruir esse per\xedodo.",
                verbose_name="In\xedcio usufruto",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="data_referencia",
            field=models.DateField(
                help_text="Data de referencia para o calculo do per\xc3\xadodo aquisitivo .",
                verbose_name="Data de refer\xeancia",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="estado",
            field=models.SmallIntegerField(
                default=1,
                help_text="Situa\xe7\xe3o atual desse per\xedodo aquisitivo",
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (8, "Indenizado Total ou Parcialmente"),
                    (1, "Aguardando Libera\xe7\xe3o p/ Marca\xe7\xe3o"),
                    (2, "Em Andamento"),
                    (4, "Fru\xedda"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="folha_evento_terco_constitucional",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="gfp.FolhaEvento",
                help_text="Refer\xeancia \xe0 folha e evento que gerou o pagamento do ter\xe7o constitucional para o per\xedodo aquisitivo.",
                null=True,
                verbose_name="Folha Evento",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="pago_sem_folha",
            field=models.BooleanField(
                default=False,
                help_text="Informa se o PAS foi pago antes da entrada em vigencia do sistema e a folha n\xe3o pode ser indicada com precis\xe3o.",
                verbose_name="Pago sem folha",
            ),
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="periodo_aquisitivo",
            field=models.ForeignKey(
                related_name="paservidores",
                verbose_name="Per\xedodo aquisitivo",
                to="ferias.PeriodoAquisitivo",
                help_text="O per\xc3\xadodo aquisitivo refente a que o servidor tem direito.",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="periodoaquisitivoservidor",
            name="quantidade_dias",
            field=models.SmallIntegerField(
                default=30,
                help_text="Quantidade de dias a que o servidor tem direito para o per\xedodo em quest\xe3o.",
                verbose_name="Quantidade de dias",
            ),
        ),
    ]
