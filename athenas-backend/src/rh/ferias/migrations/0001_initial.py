# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import standard.models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AlteracaoPASU",
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
                    "autorizado",
                    models.BooleanField(
                        default=False,
                        help_text="Se a autorizacao foi deferida ou indeferida.",
                        verbose_name="Autorizado",
                    ),
                ),
                (
                    "autorizado_em",
                    models.DateField(
                        help_text="Data em que essa parcela foi autorizada pela chefia.",
                        null=True,
                        verbose_name="Autorizado em",
                        blank=True,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now=True)),
                (
                    "justificativa",
                    models.TextField(
                        help_text="Justificativa para a altera\xc3\xa7\xc3\xa3o da parcela de ususfruto.",
                        verbose_name="Justificativa",
                    ),
                ),
            ],
            options={
                "db_table": "frs_alteracao",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Configuracao",
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
                    "nome",
                    models.CharField(
                        help_text="Identifica\xc3\xa7\xc3\xa3o da configura\xc3\xa7\xc3\xa3o",
                        unique=1,
                        max_length=100,
                        verbose_name="Nome",
                    ),
                ),
                (
                    "dias_por_periodo",
                    models.SmallIntegerField(
                        default="30",
                        help_text="Quantidade de dias m\xc3\xa1xima que pode ser usufru\xc3\xaddo em um per\xc3\xadodo.",
                        verbose_name="Dias por per\xc3\xadodo",
                    ),
                ),
                (
                    "quantidade_periodos",
                    models.SmallIntegerField(
                        default=1,
                        help_text="Quantidade de per\xc3\xadodos em um ano (12 meses).Ex.: Servidor = 1 periodo por ano (12 meses), Membro= 2 per\xc3\xadodos por ano",
                        verbose_name="Per\xc3\xadodos",
                        choices=[
                            (1, "\xdanico"),
                            (2, "Semestre"),
                            (3, "Quadrimestre"),
                            (4, "Trimestre"),
                        ],
                    ),
                ),
                (
                    "tipo_servidor",
                    models.CharField(
                        default="SERVIDOR",
                        help_text="Para qual tipo de servidor ser\xc3\xa1 aplicada essa configura\xc3\xa7\xc3\xa3o de f\xc3\xa9rias.",
                        max_length=30,
                        verbose_name="Tipo de servidor",
                        choices=[("S", "Servidor"), ("M", "Membro")],
                    ),
                ),
                (
                    "max_divisoes",
                    models.SmallIntegerField(
                        default=2,
                        help_text="Quantidade m\xc3\xa1xima de divis\xc3\xb5es que um per\xc3\xadodo de f\xc3\xa9rias pode ser usufru\xc3\xaddo.",
                        verbose_name="M\xc3\xa1ximo de divis\xc3\xb5es",
                    ),
                ),
                (
                    "min_dias_por_divisao",
                    models.SmallIntegerField(
                        default="10",
                        help_text="Quantidade m\xc3\xadnima de dias que pode ser dividida o per\xc3\xadodo de usufruto.",
                        verbose_name="Quantidade m\xc3\xadnimo de dias por divis\xc3\xa3o",
                    ),
                ),
                (
                    "modo",
                    models.CharField(
                        default="CONTINUO",
                        help_text="Modo de avalia\xc3\xa7\xc3\xa3o do per\xc3\xadodo aquisitivo. ANUAL: per\xc3\xaddo por ano. CONTINUO: per\xc3\xadodo de acordo com a data de exerc\xc3\xadcio do servidor.",
                        max_length=30,
                        verbose_name="Modo de aquisi\xc3\xa7\xc3\xa3o",
                        choices=[("CONTINUO", "Cont\xc3\xadnuo"), ("ANUAL", "Anual")],
                    ),
                ),
                (
                    "meses_max_fruicao",
                    models.SmallIntegerField(
                        default=12,
                        help_text="Tempo m\xc3\xa1ximo (em meses) para o gozo dos dias de f\xc3\xa9rias. OBS.: XX meses - 1 dia",
                        verbose_name="M\xc3\xa1ximo frui\xc3\xa7\xc3\xa3o (meses)",
                    ),
                ),
                (
                    "meses_prescricao",
                    models.SmallIntegerField(
                        default=24,
                        help_text="Tempo m\xc3\xa1ximo (em meses) para o gozo dos dias de f\xc3\xa9rias, antes de prescreverem.",
                        verbose_name="Prescri\xc3\xa7\xc3\xa3o (meses)",
                    ),
                ),
                (
                    "meses_exercicio",
                    models.SmallIntegerField(
                        default=12,
                        help_text="Tempo de exerc\xc3\xadcio, em meses, para adquirir direito a frui\xc3\xa7\xc3\xa3o de um periodo de f\xc3\xa9rias",
                        verbose_name="Tempo de exerc\xc3\xadcio (meses)",
                        blank=True,
                    ),
                ),
                (
                    "dias_antecedencia_fruicao",
                    models.SmallIntegerField(
                        default=15,
                        help_text="Dias de anteced\xc3\xaancia entre a marca\xc3\xa7\xc3\xa3o/altera\xc3\xa7\xc3\xa3o e a frui\xc3\xa7\xc3\xa3o",
                        verbose_name="Anteced\xc3\xaancia frui\xc3\xa7\xc3\xa3o (dias)",
                        blank=True,
                    ),
                ),
                (
                    "bloquear_conflitos",
                    models.BooleanField(
                        default=False,
                        help_text="Bloquear para marca\xc3\xa7\xc3\xb5es conflitantes com todos os substitutos",
                        verbose_name="Bloquer conflitos",
                    ),
                ),
                (
                    "exigir_autorizacao_chefia_mediata",
                    models.BooleanField(
                        default=False,
                        help_text="Se \xc3\xa9 necess\xc3\xa1rio que a chefia mediata autorize ap\xc3\xb3s a chefia imediata",
                        verbose_name="Autorizacao chefia mediata",
                    ),
                ),
            ],
            options={
                "ordering": ("nome",),
                "db_table": "frs_configuracao",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PeriodoAquisitivo",
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
                    "ano_aquisicao",
                    models.SmallIntegerField(
                        help_text="Ano de aquisi\xc3\xa7\xc3\xa3o do per\xc3\xadodo",
                        verbose_name="Ano de aquisi\xc3\xa7\xc3\xa3o",
                    ),
                ),
                (
                    "periodo",
                    models.SmallIntegerField(
                        default=1,
                        help_text="Per\xc3\xadodo (\xc3\xbanico/semestre/quadrimestre) do ano que gerou esse per\xc3\xadodo aquisitivo quando as f\xc3\xa9rias s\xc3\xa3o anuais. Ex.: 2 -> para f\xc3\xa9rias anuais com per\xc3\xadodo aquisitivo no segundo semestre do ano.",
                        verbose_name="Per\xc3\xadodo",
                    ),
                ),
                (
                    "data_publicacao",
                    models.DateTimeField(
                        help_text="Data em que o per\xc3\xadodo aquisitivo foi publicado.",
                        null=True,
                        verbose_name="Data de Publica\xe7\xe3o",
                    ),
                ),
                (
                    "data_inicio_prev",
                    models.DateField(
                        help_text="Data para in\xc3\xadcio das marca\xc3\xa7\xc3\xb5es de f\xc3\xa9rias.",
                        verbose_name="In\xc3\xadcio de Previs\xc3\xa3o",
                    ),
                ),
                (
                    "data_fim_prev",
                    models.DateField(
                        help_text="Data para finaliza\xc3\xa7\xc3\xa3o das marca\xc3\xa7\xc3\xb5es de f\xc3\xa9rias.",
                        null=True,
                        verbose_name="Final de Previs\xc3\xa3o",
                        blank=True,
                    ),
                ),
                (
                    "data_homologacao_prev",
                    models.DateField(
                        help_text="Data prevista para homologa\xc3\xa7\xc3\xa3o do per\xc3\xadodo aquisitivo.",
                        null=True,
                        verbose_name="Data de Homologa\xc3\xa7\xc3\xa3o",
                        blank=True,
                    ),
                ),
                (
                    "bloqueado",
                    models.BooleanField(
                        default=False,
                        help_text="Os servidores n\xc3\xa3o poder\xc3\xa3o utilizar esse per\xc3\xadodo. Ex.: Cria\xc3\xa7\xc3\xa3o de per\xc3\xadodo anteriores.",
                        verbose_name="Bloqueado",
                    ),
                ),
                (
                    "periodo_anterior",
                    models.BooleanField(
                        default=False,
                        help_text="Informa se o per\xc3\xadodo \xc3\xa9 anterior \xc3\xa0 data atual. Deve ser usado para per\xc3\xadodos anteriores \xc3\xa0 utiliza\xc3\xa7\xc3\xa3o do sistema",
                        verbose_name="Antigo",
                    ),
                ),
                (
                    "mes_fruicao",
                    models.SmallIntegerField(
                        blank=True,
                        help_text="M\xc3\xaas para frui\xc3\xa7\xc3\xa3o coletiva, caso haja",
                        null=True,
                        verbose_name="M\xc3\xaas de frui\xc3\xa7\xc3\xa3o",
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
            ],
            options={
                "ordering": ("-ano_aquisicao", "-periodo"),
                "db_table": "frs_periodoaquisitivo",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PeriodoAquisitivoServidor",
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
                    "data_referencia",
                    models.DateField(
                        help_text="Data de referencia para o calculo do per\xc3\xadodo aquisitivo .",
                        verbose_name="Data de refer\xc3\xaancia",
                        blank=True,
                    ),
                ),
                (
                    "data_inicio_aquisicao",
                    models.DateField(
                        help_text="",
                        verbose_name="In\xc3\xadcio aquisi\xc3\xa7\xc3\xa3o",
                        blank=True,
                    ),
                ),
                (
                    "data_fim_aquisicao",
                    models.DateField(
                        help_text="Data de referencia para o calculo do per\xc3\xadodo aquisitivo .",
                        verbose_name="Fim aquisi\xc3\xa7\xc3\xa3o",
                        blank=True,
                    ),
                ),
                (
                    "data_inicio_usufruto",
                    models.DateField(
                        help_text="Data m\xc3\xadnima para que se possa usufruir esse per\xc3\xadodo.",
                        verbose_name="In\xc3\xadcio usufruto",
                        blank=True,
                    ),
                ),
                (
                    "data_fim_usufruto",
                    models.DateField(
                        help_text="Data m\xc3\xa1xima para que se possa usufruir esse per\xc3\xadodo.",
                        null=True,
                        verbose_name="Fim usufruto",
                        blank=True,
                    ),
                ),
                (
                    "quantidade_dias",
                    models.SmallIntegerField(
                        default=30,
                        help_text="Quantidade de dias a que o servidor tem direito para o per\xc3\xadodo em quest\xc3\xa3o.",
                        verbose_name="Quantidade de dias",
                    ),
                ),
                (
                    "estado",
                    models.SmallIntegerField(
                        default=1,
                        help_text="Situa\xc3\xa7\xc3\xa3o atual desse per\xc3\xadodo aquisitivo",
                        verbose_name="Situa\xc3\xa7\xc3\xa3o",
                        choices=[
                            (8, "Indenizado Total ou Parcialmente"),
                            (1, "Aguardando Libera\xe7\xe3o p/ Marca\xe7\xe3o"),
                            (2, "Em Andamento"),
                            (4, "Fru\xedda"),
                        ],
                    ),
                ),
                (
                    "pago_sem_folha",
                    models.BooleanField(
                        default=False,
                        help_text="Informa se o PAS foi pago antes da entrada em vigencia do sistema e a folha n\xc3\xa3o pode ser indicada com precis\xc3\xa3o.",
                        verbose_name="Pago sem folha",
                    ),
                ),
                (
                    "bloqueado",
                    models.BooleanField(
                        default=False,
                        help_text="Informa se o PAS pode ser manipulado por algu\xc3\xa9m, normalmente \xc3\xa9 bloqueado quando se cria um per\xc3\xadodo anterior.",
                        verbose_name="Bloqueado",
                    ),
                ),
            ],
            options={
                "ordering": ("servidor",),
                "db_table": "frs_paservidor",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PeriodoAquisitivoServidorAdmin",
            fields=[
                (
                    "periodoaquisitivoservidor_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="ferias.PeriodoAquisitivoServidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "frs_paservidoradmin",
            },
            bases=("ferias.periodoaquisitivoservidor",),
        ),
        migrations.CreateModel(
            name="PeriodoAquisitivoServidorMembro",
            fields=[
                (
                    "periodoaquisitivoservidor_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="ferias.PeriodoAquisitivoServidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "frs_paservidormembro",
            },
            bases=("ferias.periodoaquisitivoservidor",),
        ),
        migrations.CreateModel(
            name="PeriodoAquisitivoServidorUsufruto",
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
                    "data_inicio",
                    models.DateField(
                        help_text="In\xc3\xadcio da frui\xc3\xa7\xc3\xa3o desse per\xc3\xadodo de f\xc3\xa9rias.",
                        verbose_name="In\xc3\xadcio",
                    ),
                ),
                (
                    "data_prevista_fim",
                    models.DateField(
                        help_text="Data prevista de fim da frui\xc3\xa7\xc3\xa3o desse per\xc3\xadodo de f\xc3\xa9rias.",
                        null=True,
                        verbose_name="Prevista de Fim",
                        blank=True,
                    ),
                ),
                (
                    "dias",
                    models.SmallIntegerField(
                        default=0,
                        help_text="Quantidade de dias marcados",
                        verbose_name="Dias marcados",
                    ),
                ),
                (
                    "interrompido",
                    models.BooleanField(
                        default=False,
                        help_text="Se a parcela foi interrompida.",
                        verbose_name="Interrompido",
                    ),
                ),
                (
                    "estado",
                    models.SmallIntegerField(
                        default=1,
                        help_text="Situa\xc3\xa7\xc3\xa3o atual",
                        verbose_name="Situa\xc3\xa7\xc3\xa3o",
                        choices=[
                            (512, "N\xe3o autorizado"),
                            (1, "Inclus\xe3o solicitada"),
                            (2, "Autorizado"),
                            (4, "Homologado"),
                            (8, "Altera\xe7\xe3o solicitada"),
                            (128, "Em frui\xe7\xe3o"),
                            (256, "Usufru\xeddo"),
                            (16, "Alterado"),
                            (32, "Interrompido"),
                            (1024, "Substituto"),
                            (64, "Suspenso"),
                        ],
                    ),
                ),
                (
                    "autorizado_em",
                    models.DateField(
                        help_text="Data em que essa parcela foi autorizada pela chefia.",
                        null=True,
                        verbose_name="Autorizado em",
                        blank=True,
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("suspenso_em", models.DateTimeField(null=True, blank=True)),
            ],
            options={
                "db_table": "frs_paservidorusufruto",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="PASUAlteracao",
            fields=[
                (
                    "periodoaquisitivoservidorusufruto_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="ferias.PeriodoAquisitivoServidorUsufruto",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "justificativa",
                    models.TextField(
                        help_text="Justificativa para a altera\xc3\xa7\xc3\xa3o da parcela de ususfruto.",
                        verbose_name="Justificativa",
                    ),
                ),
            ],
            options={
                "db_table": "frs_pasualterado",
            },
            bases=("ferias.periodoaquisitivoservidorusufruto",),
        ),
    ]
