# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from esocial.models import (
    S1000,
    S1005,
    S1010,
    S1020,
    S1070,
    S1200,
    S1202,
    S1207,
    S1210,
    S1298,
    S1299,
    S2200,
    S2205,
    S2206,
    S2210,
    S2220,
    S2230,
    S2231,
    S2240,
    S2298,
    S2299,
    S2300,
    S2306,
    S2399,
    S2400,
    S2405,
    S2410,
    S2416,
    S2418,
    S2420,
    S3000,
    S5001,
    S5002,
    S5011,
    S5012,
    S5501,
    Event,
    PayrollPeriod,
)

log = getLogger(__name__)


@receiver(post_save, sender=Event)
@receiver(post_save, sender=S1000)
@receiver(post_save, sender=S1005)
@receiver(post_save, sender=S1010)
@receiver(post_save, sender=S1020)
@receiver(post_save, sender=S1070)
@receiver(post_save, sender=S1200)
@receiver(post_save, sender=S1202)
@receiver(post_save, sender=S1207)
@receiver(post_save, sender=S1210)
@receiver(post_save, sender=S1298)
@receiver(post_save, sender=S1299)
@receiver(post_save, sender=S2200)
@receiver(post_save, sender=S2205)
@receiver(post_save, sender=S2206)
@receiver(post_save, sender=S2230)
@receiver(post_save, sender=S2231)
@receiver(post_save, sender=S2298)
@receiver(post_save, sender=S2299)
@receiver(post_save, sender=S2300)
@receiver(post_save, sender=S2306)
@receiver(post_save, sender=S2399)
@receiver(post_save, sender=S3000)
@receiver(post_save, sender=S5001)
@receiver(post_save, sender=S5002)
@receiver(post_save, sender=S5011)
@receiver(post_save, sender=S5012)
@receiver(post_save, sender=S5501)
@receiver(post_save, sender=S2400)
@receiver(post_save, sender=S2405)
@receiver(post_save, sender=S2410)
@receiver(post_save, sender=S2416)
@receiver(post_save, sender=S2418)
@receiver(post_save, sender=S2420)
@receiver(post_save, sender=S2210)
@receiver(post_save, sender=S2220)
@receiver(post_save, sender=S2240)
def update_cache(sender, instance, **kwargs):
    """Atualiza todos eventos que foram modificados por instance."""
    if isinstance(instance, Event):
        instance = instance.event

    if instance.modify_event:
        transaction.on_commit(lambda: instance.modify_event.event.update_cache())

    close_event = getattr(instance, "close_event", None)
    if close_event:
        transaction.on_commit(lambda: close_event.event.update_cache())


@receiver(post_save, sender=Event)
@receiver(post_save, sender=S1200)
@receiver(post_save, sender=S1202)
@receiver(post_save, sender=S1207)
@receiver(post_save, sender=S1210)
@receiver(post_save, sender=S1299)
@receiver(post_save, sender=S2299)
@receiver(post_save, sender=S2399)
def update_totalizer(sender, instance, **kwargs):
    """Atualiza os totalizadores."""
    if isinstance(instance, Event):
        instance = instance.event

    if isinstance(instance, (S1298, S1299)):
        transaction.on_commit(
            lambda: PayrollPeriod.update_cache_by_period(
                instance.competence_month, instance.competence_year
            )
        )

    if isinstance(instance, (S1200, S1202, S1207, S1210, S1299, S2299, S2399)):
        transaction.on_commit(lambda: instance.update_totalizer())


# @receiver(post_save, sender=Event)
# @receiver(post_save, sender=S3000)
# @receiver(post_save, sender=S1200)
# @receiver(post_save, sender=S1202)
# @receiver(post_save, sender=S1207)
# def update_entry(sender, instance, **kwargs):
#     """Atualiza o FolhaEvento."""
#     if isinstance(instance, Event):
#         instance = instance.event

#     if isinstance(instance, S3000):
#         if not instance.modify_event:
#             print(f'S3000 {instance} não possui modify_event')
#         if instance.process_status > 5 and instance.modify_event:
#             instance = instance.modify_event.event
#         else:
#             return False

#     if isinstance(instance, (S1200, S1202, S1207)):
#         transaction.on_commit(lambda: S1200.update_demonstrative_item(instance))


@receiver(post_save, sender=Event)
@receiver(post_save, sender=S2200)
@receiver(post_save, sender=S2300)
@receiver(post_save, sender=S2400)
@receiver(post_save, sender=S2298)
def update_employee(sender, instance, **kwargs):
    """Atualiza o Servidor de cada cadastro."""
    if isinstance(instance, Event):
        instance = instance.event

    if isinstance(instance, (S2200, S2300, S2400, S2298)):
        transaction.on_commit(lambda: S2200.update_employee(instance))


@receiver(post_save, sender=Event)
@receiver(post_save, sender=S2230)
@receiver(post_save, sender=S2231)
def update_departure(sender, instance, **kwargs):
    """Atualiza o BaseLicencaAfastamento de cada cadastro."""
    if isinstance(instance, Event):
        instance = instance.event

    if isinstance(instance, (S2230, S2231)):
        transaction.on_commit(lambda: S2230.update_departure(instance))
