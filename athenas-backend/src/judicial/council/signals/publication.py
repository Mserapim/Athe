# -*- coding: utf-8 -*-
from django.db.models.signals import pre_save
from rh.models import Publicacao as Publication
from django.dispatch import receiver
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(pre_save, sender=Publication)
def detect_publication_date_for_convocationnotice(instance, **kargs):
    log.debug("-> ------------------------------------------ <-")
    # log.debug(kargs)
    if not instance.pk:
        return

    older = Publication.objects.get(pk=instance.pk)
    log.info("Older loaded %s", older)

    if older.data_publicacao != instance.data_publicacao:
        log.info("Publication date changed and is set for %s", instance.data_publicacao)
        for convocation in instance.convocation_notices.filter():
            convocation.convocation_state = 3
            convocation.estimate_deadline(instance.data_publicacao)
            convocation.with_check_sign = False
            convocation.save()
