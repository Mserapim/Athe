# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from contrib.utils import getLogger
from default.websocket import RemoteEmmiter

from common.internal_security.models import IncidentReport

log = getLogger(__name__)


@receiver(post_save, sender=IncidentReport)
def emmit_alarm(sender, instance, signal, **kargs):
    if instance.pk:
        RemoteEmmiter.emmit(
            "main",
            "internal-security-alarm",
            {"alarm_sound": True if not instance.received_by else False},
        )
