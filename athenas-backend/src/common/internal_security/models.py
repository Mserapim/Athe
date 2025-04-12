# -*- coding: utf-8 -*-
from django.db import models
from django.template import loader
from datetime import datetime
from contrib.middleware import get_current_user
from contrib.utils import getLogger, employee_from_user

from standard.models import Choice


log = getLogger(__name__)


class EmotionalState(models.Model):
    person = models.ForeignKey(
        "rh.Pessoa", related_name="emotional_state_reports", on_delete=models.PROTECT
    )
    reported_by = models.ForeignKey(
        "auth.User",
        related_name="emotional_state_reports",
        blank=True,
        on_delete=models.PROTECT,
    )
    reported_at = models.DateTimeField(auto_now_add=True, blank=True)
    emotional_state = models.SmallIntegerField(
        default=1,
        choices=(
            (1, "Verde"),
            (2, "Laranja"),
            (3, "Vermelho"),
        ),
    )
    observation = models.TextField(null=True, blank=True)

    def save(self, *args, **kwags):
        if not self.pk:
            self.reported_at = datetime.now()
            self.reported_by = get_current_user()

        super(EmotionalState, self).save(*args, **kwags)


class IncidentReport(models.Model):
    reported_by = models.ForeignKey(
        "auth.User",
        related_name="as_reporter_security_incidentes",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    reported_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    received_by = models.ForeignKey(
        "auth.User",
        related_name="as_receiver_security_incidentes",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    received_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        "auth.User",
        related_name="as_closer_security_incidentes",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    type_finish = models.SmallIntegerField(
        choices=Choice.get_choices_for("internal_security", "CLOSE_OPTIONS"),
        blank=True,
        null=True,
    )
    amount_click = models.SmallIntegerField(default=1)

    class Meta:
        permissions = (
            ("can_admin_incident", "Pode administrar os incidentes"),
            ("can_reginal_admin_incident", "Pode administrar os incidentes regionais"),
            ("can_view_panic_button", "Pode visualizar o botao do panico"),
        )
        ordering = ("-reported_at", "-received_at", "-closed_at")

    @property
    def is_received(self):
        return True if self.received_by else False

    @property
    def rendered(self):
        reported_by = employee_from_user(self.reported_by)

        data = [
            loader.get_template("internal_security/incident_report.html").render(
                {
                    "incident": self,
                    "employee_reported": reported_by,
                    "work_locations": reported_by.work_locations,
                    "employee_received": employee_from_user(self.received_by),
                    "employee_closed": employee_from_user(self.closed_by),
                }
            )
        ]

        return "".join(data)

    def close(self):
        pass

    def increment_amount_click(self, increment=1):
        self.amount_click += increment
        self.skip_validate_received_by = True
        self.save()

    def delete(self, *args, **kwags):
        raise Exception("Não posso remove um incidente, ele deve ser tratado.")

    def receive(self):
        self.received_by = get_current_user()
        self.received_at = datetime.now()
        self.save()

    def finish(self, type_finish):
        if not self.received_by:
            raise Exception("É necessário receber o incidente para alterá-lo.")

        self.closed_by = get_current_user()
        self.closed_at = datetime.now()
        self.type_finish = type_finish
        self.save()

    def validate(self):
        if self.pk:
            if (
                not getattr(self, "skip_validate_received_by", False)
                and not self.received_by
            ):
                raise Exception("É necessário receber o incidente para alterá-lo.")

            older = self.__class__.objects.get(pk=self.pk)

            if older.closed_by:
                raise Exception("Não é possivel alterar um incidente finalizado.")

    def save(self, *args, **kwags):
        self.validate()

        reported_now = False
        if not self.pk and not self.reported_by:
            self.reported_by = get_current_user()
            reported_now = True

        super(IncidentReport, self).save(*args, **kwags)
        IncidentReportLog.register(self)

        if reported_now:
            IncidentPlace.register(self)


class IncidentPlace(models.Model):
    incident = models.ForeignKey(
        IncidentReport, related_name="places", on_delete=models.PROTECT
    )
    place = models.ForeignKey(
        "rh.Lotacao", related_name="in_incident_places", on_delete=models.PROTECT
    )

    @classmethod
    def register(klass, incident):
        employee = employee_from_user(incident.reported_by)
        for place in employee.work_locations_effective_exercise:
            klass.objects.create(incident=incident, place=place)


class IncidentReportLog(models.Model):
    reported_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    reported_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    received_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    received_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    closed_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    closed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    incident_report = models.ForeignKey(
        IncidentReport, related_name="logs", on_delete=models.PROTECT
    )
    at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def register(klass, incident):
        klass.objects.create(
            incident_report=incident,
            reported_by=incident.reported_by,
            reported_at=incident.reported_at,
            received_by=incident.received_by,
            received_at=incident.received_at,
            closed_by=incident.closed_by,
            closed_at=incident.closed_at,
            content=incident.content,
        )
