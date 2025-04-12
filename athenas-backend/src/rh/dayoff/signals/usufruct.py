# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.dayoff.models import Usufruct, AcquisitionPeriod


log = getLogger(__name__)


def update_acquisition_period_cache(acquisition_period):
    AcquisitionPeriod.objects.filter(pk=acquisition_period.pk).update(
        booked_days_cache=acquisition_period.booked_days,
        real_days_cache=acquisition_period.real_days,
        days_to_enjoy_cache=acquisition_period.days_to_enjoy,
        paid_days_cache=acquisition_period.paid_days,
        days_not_booked_cache=acquisition_period.days_not_booked,
    )


@receiver(post_save, sender=Usufruct)
@receiver(post_delete, sender=Usufruct)
def update_acquisition_period(sender, instance, **kargs):
    if instance.acquisition_period:
        transaction.on_commit(
            lambda: update_acquisition_period_cache(instance.acquisition_period)
        )
        transaction.on_commit(
            lambda: instance.acquisition_period.update_status(update_usufructs=False)
        )
        transaction.on_commit(lambda: instance.acquisition_period.update_annotation())
