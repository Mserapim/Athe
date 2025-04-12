# -*- coding: utf-8 -*-
from judicial.models import OutCourtLawsuit, NotifyStack
from django.db.models.signals import pre_save
from django.dispatch import receiver
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(pre_save, sender=OutCourtLawsuit)
def register_notify_stack(sender, instance, signal, **kargs):
    if instance.pk:
        older = instance.__class__.objects.get(pk=instance.pk)
        if older.location.pk != instance.location.pk:
            NotifyStack.create_for(instance)
        elif older.cache_number == "--" and instance.cache_number != "--":
            NotifyStack.create_for(instance)
