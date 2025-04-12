# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from django.db import models
from standard.models import AuditTimestampModel
from contrib.middleware import get_current_user
from judicial.models import PartLawsuit, type_part_lawsuit, MEANING_TYPE_DOCUMENT
from ged.models import Arquivo
from dateutil.relativedelta import relativedelta
from datetime import date
from standard.models import Choice
from django.db.models import Min

log = getLogger(__name__)


@type_part_lawsuit()
class ManagementTAC(PartLawsuit):
    """
    **Classe** que define Gestor de Termo de Ajuste de Conduta a ser cumprido pelas partes.
    """

    class Meta:
        db_table = "tac_manag_tac"
        permissions = (("manager_tac", "Visão Gestão de TAC"),)

    description = models.TextField()
    considerations = models.TextField()
    date_signature = models.DateField(
        verbose_name="Data da Assinatura do TAC", null=True, blank=True
    )
    author_signature = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    codename = "Termo de Ajustamento de conduta"

    @property
    def meaning_type(self):
        return MEANING_TYPE_DOCUMENT

    def params(self):
        rst = PartLawsuit.params(self)

        execution_organ = self.lawsuit.location

        rst.update(doc=self, execution_organ=execution_organ)

        return rst

    def sign_part(self):
        self.page_number = self.lawsuit.next_page()

        super(ManagementTAC, self).sign_part()

        self.dispatch_comunication(
            subject="Comunicar a %s" % str(self),
        )

        for act in self.activities_tac.filter():
            act.define_deadline_date()

    @property
    def has_activity_delayed(self):
        today = date.today()
        return self.activities_tac.filter(realized=0, deadline__lt=today).exists()

    @property
    def days_to_expiration(self):
        return (
            (self.next_date_expiration - date.today()).days
            if self.next_date_expiration
            else None
        )

    @property
    def next_date_expiration(self):
        query = self.activities_tac.filter(realized=0)
        rst = None

        if query.exists():
            value = query.aggregate(value=Min("deadline")).get("value", None)

            if value:
                rst = value

        return rst

    @classmethod
    def default_icon(klass):
        return "icon-judicial icon-ejud-glosary-conduct-term"

    def save(self, *args, **kwargs):

        super(ManagementTAC, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.read_only:
            raise Exception("Não é possível remover esse item!")
        super(ManagementTAC, self).delete(*args, **kwargs)


class Activity(AuditTimestampModel):
    """
    **Classe** que define cláusualas a serem cumpridas pelo TAC.

    REALIZED_CHOICES:
        0: 'Em andamento',
        1: 'Cumprido',
        2: 'Não cumprido',
        3: 'Executado',
    """

    class Meta:
        db_table = "tac_activity"
        ordering = ("created_at",)
        permissions = (("activity_tac", "Visão Atividade da TAC"),)

    tac = models.ForeignKey(
        ManagementTAC, related_name="activities_tac", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    act_history = models.ForeignKey(
        "ActivityHistory",
        related_name="history",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField()
    time_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("tac", "TIMETYPE_CHOICES"), default=0
    )
    time = models.IntegerField(null=True, blank=True)
    realized = models.SmallIntegerField(
        choices=Choice.get_choices_for("tac", "REALIZED_CHOICES"), default=0
    )

    fine_value = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    repair_value = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    process_number_fine = models.CharField(
        max_length=300, null=True, blank=True, default=""
    )

    deadline = models.DateField(null=True, blank=True)

    AUDITABLE = {
        "fields": [
            "tac",
            "description",
            "time_type",
            "time",
            "realized",
            "created_by",
            "created_at",
        ]
    }

    ICONS = {
        0: {
            "iconCls": "icon-judicial icon-ejud-lawsuit-open",
            "title": "Não informado",
        },
        1: {"iconCls": "icon-gep-recomendou", "title": "Cláusula Cumprida"},
        2: {"iconCls": "icon-gep-nao-recomendou", "title": "Cláusula Não Cumprida"},
    }

    def mark_realized(self, realized=True):
        self.validate_read_only = False
        self.realized = 1 if realized else 2
        self.save()

    def fill_process_number_fine(self, process_number_fine):
        if not self.tac.signed_by or not self.tac.signed_at:
            raise Exception("Não posso executar um termo que ainda não foi assinado.")

        self.process_number_fine = process_number_fine
        self.validate_read_only = False
        self.save()

    @property
    def icon_process_number_fine(self):
        if self.process_number_fine:
            return {
                "iconCls": "icon-judicial icon-ejud-procedimento-preparatorio-in-grid",
                "title": "Executado.",
            }

    @property
    def icons(self):
        icon = []
        icon.append(self.ICONS.get(self.realized))
        icon.append(self.icon_process_number_fine)

        return icon

    def relative_date(self, **kwargs):
        return relativedelta(**kwargs)

    def date_future(self):
        args = {
            0: {},
            1: {"days": self.time},
            2: {"months": self.time},
            3: {"years": self.time},
        }

        tmpdate = self.tac.signed_at if self.tac.signed_at else date.today()
        return tmpdate + self.relative_date(**args.get(self.time_type, 0))

    def define_deadline_date(self):
        if not self.deadline:
            self.deadline = self.date_future()
            self.validate_read_only = False
            self.save()

    @property
    def status(self):
        return {
            0: "Em andamento",
            1: "Cumprido",
            2: "Não cumprido",
            3: "Executado",
            99: "---",
        }.get(self.realized, 99)

    def save(self, *args, **kwargs):
        if self.tac.read_only and getattr(self, "validate_read_only", True):
            raise Exception("Não é possível adicionar essa informação.")

        if not self.time_type:
            self.time = None
            self.repair_value = None
            self.fine_value = None

        super(Activity, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.tac.read_only:
            raise Exception("Não é possível remover esse item!")
        super(Activity, self).delete(*args, **kwargs)


class ActivityHistory(AuditTimestampModel):
    """
    **Classe** que define historico das atividades para o termo de ajuste de conduta.
    """

    class Meta:
        db_table = "tac_activity_history"
        ordering = ("-created_at",)
        permissions = (("activity_history_tac", "Visão Histórico Atividade da TAC"),)

    activity = models.ForeignKey(
        Activity, related_name="activity_history", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.TextField()
    time_type = models.SmallIntegerField(
        choices=Choice.get_choices_for("tac", "TIMETYPE_CHOICES"), default=0
    )
    time = models.IntegerField(null=True)
    realized = models.SmallIntegerField(
        choices=Choice.get_choices_for("tac", "REALIZED_CHOICES"), default=0
    )
    author = models.ForeignKey(
        "auth.User", related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


class Responsible(AuditTimestampModel):
    """
    **Classe** que define os responsável pela execução das cláusulas acordadas.
    """

    class Meta:
        db_table = "tac_responsible"
        ordering = ("responsible_person",)
        permissions = (("responsible_tac", "Visão Resposável Atividade TAC"),)

    responsible_person = models.ForeignKey(
        "rh.Pessoa", related_name="responsible_person", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    activity = models.ForeignKey(
        Activity, related_name="responsible_activity", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s " % self.responsible_person

    def save(self, *args, **kwargs):
        super(Responsible, self).save(*args, **kwargs)


class Document(AuditTimestampModel):
    """
    **Classe** que define os documentos referentes as clásulas a serem cumpridas pelo TAC.
    """

    class Meta:
        db_table = "tac_document"
        ordering = ("activity_document",)

    activity_document = models.ForeignKey(
        Activity, related_name="document_activity", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    title = models.CharField(max_length=150, verbose_name="Document Title")
    description = models.TextField()
    file_document = models.ForeignKey(
        Arquivo, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    accepted = models.SmallIntegerField(
        choices=Choice.get_choices_for("tac", "ACCEPTED"), default=0
    )

    @property
    def get_states(self):
        if int(self.accepted) == 0:
            return "Aceite não informado", "icon-core icon-core-info"
        elif int(self.accepted) == 1:
            return "Documento aceito", "icon-gep-recomendou"
        elif int(self.accepted) == 2:
            return "Documento não aceito", "icon-gep-nao-recomendou"

    @property
    def icons(self):
        return {"iconCls": self.get_states[1], "title": self.get_states[0]}

    def save(self, *args, **kwargs):
        if not self.activity_document.tac.read_only:
            raise Exception(
                "Só posso adicionar documentos de cumprimento a um Termo já assinado."
            )

        self.accepted = int(self.accepted or 0)
        if self.accepted in (1, 2):
            self.activity_document.mark_realized(self.accepted == 1)

        super(Document, self).save(*args, **kwargs)
