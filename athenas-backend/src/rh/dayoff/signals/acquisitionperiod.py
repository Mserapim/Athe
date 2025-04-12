# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.dayoff.models import AcquisitionPeriod


@receiver(post_save, sender=AcquisitionPeriod)
def update_acquisition_period(sender, instance, **kargs):
    transaction.on_commit(lambda: instance.cancel_activities())
