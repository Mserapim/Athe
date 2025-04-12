# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0063_auto_20180529_2058"),
        ("protocolo", "0017_auto_20180115_1048"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("processo", "0007_auto_20180130_1018"),
        ("contrato", "0015_auto_20180508_2034"),
    ]

    operations = [
        migrations.CreateModel(
            name="Minute",
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
                    "number",
                    models.CharField(max_length=30, verbose_name="N\xfamero da Ata"),
                ),
                (
                    "notice_number",
                    models.CharField(
                        max_length=30,
                        null=True,
                        verbose_name="N\xfamero do Edital",
                        blank=True,
                    ),
                ),
                ("minute_object", models.TextField(verbose_name="Objeto da Ata")),
                (
                    "adhesions_quantity",
                    models.IntegerField(verbose_name="Quantidade de Ades\xc3\xb5es"),
                ),
                (
                    "begin_validity",
                    models.DateField(verbose_name="In\xedcio da Vig\xeancia"),
                ),
                (
                    "end_validity",
                    models.DateField(verbose_name="T\xe9rmino da Vig\xeancia"),
                ),
                ("signature_date", models.DateField(verbose_name="Data da Assinatura")),
                (
                    "bidding_type",
                    models.SmallIntegerField(
                        verbose_name="Tipo de Licita\xc3\xa7\xc3\xa3o",
                        choices=[
                            (1, "Dispensa de Licita\xe7\xe3o"),
                            (2, "Inexigibilidade de Licita\xe7\xe3o"),
                            (3, "Preg\xe3o Eletr\xf4nico"),
                            (4, "Preg\xe3o Presencial"),
                            (5, "Ades\xe3o a Ata SRP"),
                            (6, "Concorr\xeancia"),
                            (100, "Registro de Pre\xe7o"),
                        ],
                    ),
                ),
                (
                    "publication_date",
                    models.DateField(
                        null=True, verbose_name="Data da Publica\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "official_diary",
                    models.CharField(
                        max_length=50,
                        null=True,
                        verbose_name="N\xfamero do Di\xe1rio Oficial",
                        blank=True,
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor Total",
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "object_execution",
                    models.TextField(verbose_name="Execu\xc3\xa7\xc3\xa3o do Objeto"),
                ),
                (
                    "days_for_notice",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (90, "3 meses antes do vencimento"),
                            (100, "N\xe3o avisar"),
                            (120, "4 meses antes do vencimento"),
                            (180, "6 meses antes do vencimento"),
                        ],
                    ),
                ),
                ("status", models.SmallIntegerField(default=1, verbose_name="Status")),
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
                    "management_organ",
                    models.ForeignKey(
                        related_name="minutes",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rh.OrgaoGeral",
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
                    "parent_process",
                    models.ForeignKey(
                        related_name="minutesparent",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="processo.Processo",
                        null=True,
                    ),
                ),
                (
                    "process_number",
                    models.ForeignKey(
                        related_name="minutes",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="processo.Processo",
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        related_name="minutes", to="rh.Pessoa", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "hiring_minute",
                "permissions": (("view_all_minutes", "Can view all minutes"),),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteAction",
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
                ("date", models.DateTimeField(auto_now_add=True)),
                ("action", models.SmallIntegerField()),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "minute",
                    models.ForeignKey(
                        related_name="minuteactions",
                        to="contrato.Minute",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "hiring_minuteaction",
            },
        ),
        migrations.CreateModel(
            name="MinuteItem",
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
                ("description", models.TextField(verbose_name="Descri\xe7\xe3o")),
                (
                    "unit_measure",
                    models.SmallIntegerField(
                        blank=True, null=True, choices=[(None, "Nenhum")]
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        null=True, verbose_name="Quantidade", blank=True
                    ),
                ),
                (
                    "unitary_value",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor Unit\xe1rio",
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "total_value",
                    models.DecimalField(
                        null=True,
                        verbose_name="Valor Total",
                        max_digits=18,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "group",
                    models.CharField(
                        max_length=10, null=True, verbose_name="Grupo/Item", blank=True
                    ),
                ),
                (
                    "line",
                    models.CharField(
                        max_length=10, null=True, verbose_name="Linha", blank=True
                    ),
                ),
                (
                    "item_balance",
                    models.PositiveIntegerField(
                        null=True, verbose_name="Saldo do item", blank=True
                    ),
                ),
                (
                    "brand",
                    models.TextField(
                        null=True, verbose_name="Marca/Modelo", blank=True
                    ),
                ),
                (
                    "generate_agreement",
                    models.BooleanField(default=False, verbose_name="Gera contrato?"),
                ),
                ("status", models.SmallIntegerField(default=1)),
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
                    "minute",
                    models.ForeignKey(
                        related_name="minuteitems",
                        to="contrato.Minute",
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
                    "parent",
                    models.ForeignKey(
                        related_name="subitems",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="contrato.MinuteItem",
                        null=True,
                    ),
                ),
            ],
            options={
                "db_table": "hiring_minuteitem",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteItemAction",
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
                ("date", models.DateTimeField(auto_now_add=True)),
                ("action", models.SmallIntegerField()),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "item",
                    models.ForeignKey(
                        related_name="minuteitemactions",
                        to="contrato.MinuteItem",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "hiring_minuteitemaction",
            },
        ),
        migrations.CreateModel(
            name="MinuteItemComplementaryDescription",
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
                    "characteristic",
                    models.CharField(max_length=128, verbose_name="Caracter\xedstica"),
                ),
                (
                    "description",
                    models.CharField(max_length=128, verbose_name="Descri\xe7\xe3o"),
                ),
                (
                    "minuteitem",
                    models.ForeignKey(
                        related_name="minuteitemcomplementarydescriptions",
                        to="contrato.MinuteItem",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "hiring_minuteitemcomplementarydescription",
            },
        ),
        migrations.CreateModel(
            name="MinuteSolicitation",
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
                    "number",
                    models.CharField(
                        max_length=30,
                        null=True,
                        verbose_name="N\xfamero do Pedido",
                        blank=True,
                    ),
                ),
                ("justification", models.TextField(verbose_name="Justificativa")),
                (
                    "situation",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Situa\xe7\xe3o", blank=True
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
                    "edoc",
                    models.OneToOneField(
                        related_name="minutesolicitation",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to="protocolo.Protocolo",
                        verbose_name="Edoc",
                    ),
                ),
                (
                    "minute",
                    models.ForeignKey(
                        related_name="minutesolicitations",
                        verbose_name="Minuta",
                        to="contrato.Minute",
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
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitation",
                "permissions": (
                    ("change_minutesolicitation_situation", "Can change situation."),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteSolicitationAction",
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
                ("date", models.DateTimeField(auto_now_add=True)),
                ("action", models.SmallIntegerField()),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "solicitation",
                    models.ForeignKey(
                        related_name="minutesolicitationactions",
                        to="contrato.MinuteSolicitation",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "user",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "hiring_minutesolicitationaction",
            },
        ),
        migrations.CreateModel(
            name="MinuteSolicitationCommitmentNote",
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
                ("number", models.CharField(max_length=20)),
                ("value", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "kind",
                    models.IntegerField(
                        choices=[(1, "Ordin\xe1rio"), (2, "Estimativo"), (3, "Global")]
                    ),
                ),
                (
                    "classification",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        choices=[
                            (1, "Material de Consumo"),
                            (2, "Material Permanente"),
                            (3, "Servi\xe7o"),
                            (4, "Obras e Instala\xe7\xf5es"),
                        ],
                    ),
                ),
                (
                    "reinforcement_reversal",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        choices=[(1, "Estorno"), (100, "Refor\xe7o")],
                    ),
                ),
                ("origin", models.SmallIntegerField()),
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
                (
                    "parent",
                    models.ForeignKey(
                        related_name="minutesolicitationcommitmentnotes",
                        blank=True,
                        to="contrato.MinuteSolicitationCommitmentNote",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "solicitation",
                    models.ForeignKey(
                        related_name="minutesolicitationcommitmentnotes",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contrato.MinuteSolicitation",
                    ),
                ),
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitationcommitmentnote",
                "permissions": (
                    (
                        "request_minutesolicitationcommitmentnote_reinforcement",
                        "Can request a commitmentnote reinforcement of the solicitation.",
                    ),
                    (
                        "request_minutesolicitationcommitmentnote_reversal",
                        "Can request a commitmentnote reversal of the solicitation",
                    ),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteSolicitationItem",
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
                ("quantity", models.PositiveIntegerField(verbose_name="Quantidade")),
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
                    "item",
                    models.ForeignKey(
                        related_name="minutesolicitationitems",
                        on_delete=django.db.models.deletion.PROTECT,
                        verbose_name="Item",
                        to="contrato.MinuteItem",
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
                    "solicitation",
                    models.ForeignKey(
                        related_name="minutesolicitationitems",
                        verbose_name="Solicita\xe7\xe3o",
                        to="contrato.MinuteSolicitation",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitationitem",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteSolicitationItemDescription",
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
                    "item_description",
                    models.ForeignKey(
                        related_name="solicitationitemdescriptions",
                        to="contrato.MinuteItemComplementaryDescription",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "solicitation_item",
                    models.ForeignKey(
                        related_name="solicitationitemdescriptions",
                        to="contrato.MinuteSolicitationItem",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitationitemdescription",
            },
        ),
        migrations.CreateModel(
            name="MinuteSolicitationPayment",
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
                ("observation", models.TextField(null=True, blank=True)),
                ("value", models.DecimalField(max_digits=18, decimal_places=2)),
                (
                    "start_reference_period",
                    models.DateField(
                        null=True,
                        verbose_name="Inicio do periodo referencia",
                        blank=True,
                    ),
                ),
                (
                    "end_reference_period",
                    models.DateField(
                        null=True,
                        verbose_name="Fim do periodo de referencia",
                        blank=True,
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, "Aguardando Pagamento"),
                            (2, "Pago"),
                            (3, "N\xe3o pago"),
                        ],
                    ),
                ),
                ("bank_order", models.CharField(max_length=20, null=True, blank=True)),
                (
                    "payment_date",
                    models.DateField(
                        null=True, verbose_name="Data do pagamento", blank=True
                    ),
                ),
                ("invoice", models.CharField(max_length=100, null=True, blank=True)),
                (
                    "commitmentnote",
                    models.ForeignKey(
                        related_name="minutesolicitationpayments",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contrato.MinuteSolicitationCommitmentNote",
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
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="minutesolicitationpayments",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-id",),
                "db_table": "hiring_minutesolicitationpayment",
                "permissions": (
                    ("do_minutesolicitationpayment", "Can do payment of solicitation."),
                    (
                        "undo_minutesolicitationpayment",
                        "Can undo payment of solicitation.",
                    ),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MinuteSupervisor",
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
                    "kind",
                    models.PositiveSmallIntegerField(
                        verbose_name="Tipo", choices=[(1, "Titular"), (2, "Substituto")]
                    ),
                ),
                (
                    "publication_document",
                    models.CharField(
                        max_length=250, null=True, verbose_name="Portaria", blank=True
                    ),
                ),
                ("publication_document_date", models.DateField(null=True, blank=True)),
                (
                    "begin",
                    models.DateField(null=True, verbose_name="In\xedcio", blank=True),
                ),
                ("end", models.DateField(null=True, verbose_name="Fim", blank=True)),
                (
                    "observation",
                    models.TextField(
                        null=True, verbose_name="Observa\xe7\xe3o", blank=True
                    ),
                ),
                (
                    "classifications",
                    models.ManyToManyField(
                        related_name="minutesupervisors",
                        verbose_name="Classifica\xe7\xf5es",
                        to="contrato.SupervisorClassification",
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
                    "employee",
                    models.ForeignKey(
                        related_name="minutesupervisors",
                        verbose_name="Servidor",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "minute",
                    models.ForeignKey(
                        related_name="minutesupervisors",
                        verbose_name="Ata",
                        to="contrato.Minute",
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
            ],
            options={
                "db_table": "hiring_minutesupervisor",
                "permissions": (
                    ("close_minutesupervisor", "Can close the supervisor of minutes"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RemoveField(
            model_name="gestor",
            name="user",
        ),
        migrations.RemoveField(
            model_name="contrato",
            name="gestor",
        ),
        migrations.RemoveField(
            model_name="contrato",
            name="responsaveis",
        ),
        migrations.DeleteModel(
            name="Gestor",
        ),
        migrations.AlterUniqueTogether(
            name="minutesolicitationitemdescription",
            unique_together=set([("solicitation_item", "item_description")]),
        ),
    ]
