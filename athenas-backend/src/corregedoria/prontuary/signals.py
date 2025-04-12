# -.- coding: utf-8 -.-

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from corregedoria.inspection.models import Inspection
from corregedoria.prontuary.models import Prontuary, InspectionLink
from contrib.utils import getLogger
from django.db import transaction

log = getLogger(__name__)


@receiver(post_save, sender=Inspection)
def signalsave_inspection_inspection(sender, instance=None, **kargs):
    try:
        with transaction.atomic():
            if instance.communicated_organ_execution is True:
                prontuary = Prontuary.objects.filter(employee=instance.employee).first()
                if prontuary is None:
                    prontuary = Prontuary()
                    prontuary.employee = instance.employee
                    prontuary.save()
                if (
                    InspectionLink.objects.filter(
                        prontuary=prontuary, inspection=instance
                    ).exists()
                    is False
                ):
                    if instance.harmedcalculation.harmedcalculation is not True:
                        InspectionLink.objects.filter(prontuary=prontuary).update(
                            active=False
                        )
                    inspectionlink = InspectionLink()
                    inspectionlink.prontuary = prontuary
                    inspectionlink.inspection = instance
                    if instance.harmedcalculation.harmedcalculation is not True:
                        inspectionlink.active = True
                    inspectionlink.save()
    except Exception as e:
        log.debug(e)


# @receiver(post_delete, sender=Inspection)
# def signaldelete_inspection_inspection(sender, instance=None, **kargs):
#     try:
#         with transaction.atomic():
#             if instance.communicated_organ_execution:
#                 prontuary = Prontuary.objects.filter(employee=instance.employee)
#                 if InspectionLink.objects.filter(prontuary=prontuary, inspection=instance).exists() is False:
#                     InspectionLink.objects.filter(prontuary=prontuary).update(active=False)
#                     inspectionlink = InspectionLink()
#                     inspectionlink.prontuary = prontuary
#                     inspectionlink.inspection = instance
#                     inspectionlink.active = True
#                     inspectionlink.save()
#     except Exception, e:
#         pass
