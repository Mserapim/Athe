# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.gfp.models import FolhaEvento as Entry

log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


@receiver(post_save, sender=Entry)
@receiver(post_delete, sender=Entry)
def update_difference_if_exists(sender, instance, **kwargs):
    """Salva PaycheckDifference se o lançamento é proveniente de uma diferença."""
    log.info("LOAD SIGNAL %s: DIF: %s" % (__name__, instance.paycheck_difference))
    if instance.paycheck_difference:
        pd = instance.paycheck_difference
        pd.save()

    return True
