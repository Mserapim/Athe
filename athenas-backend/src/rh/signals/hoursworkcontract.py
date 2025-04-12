# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from rh.models import (
    HoursWorkContract,
    EmployeeHoursWorkContractWorkload,
    HoursWorkContractWorkload,
    WorkHourInterval,
)


@receiver(post_save, sender=EmployeeHoursWorkContractWorkload)
@receiver(post_delete, sender=EmployeeHoursWorkContractWorkload)
def update_quantity_active(sender, instance, **kargs):
    HoursWorkContractWorkload.update_quantity_active(
        instance.hours_work_contract_workload
    )


@receiver(post_save, sender=WorkHourInterval)
@receiver(post_delete, sender=WorkHourInterval)
def update_duration(sender, instance, **kargs):
    HoursWorkContract.update_duration(instance.hours_work_contract)
