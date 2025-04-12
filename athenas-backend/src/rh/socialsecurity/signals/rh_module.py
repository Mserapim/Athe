# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.models import MovimentacaoPosse
from rh.socialsecurity.models import RetirementPrevision

log = getLogger("RH.MODELS")


# @receiver(post_delete, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoPosse)
def align_possession_on_employmentbond(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if (
                instance.servidor.type_by_possession in ["EFE", "ECM", "EFC"]
                and instance.data_exercicio
            ):
                rp, created = RetirementPrevision.objects.get_or_create(
                    natural_person=instance.servidor.pessoa_fisica
                )
                end_date = (
                    (instance.data_desligamento + relativedelta(days=-1))
                    if instance.data_desligamento
                    else None
                )
                eb, created = rp.employmentbonds.update_or_create(
                    employer="%s" % instance.quadro.cargo.unidade_administrativa,
                    pension_system=instance.servidor.regime_social_security,
                    possession=instance,
                    defaults={
                        "begin_date": instance.data_exercicio,
                        "end_date": end_date,
                        "deduction": 0,
                        "public_employee": True,
                        "with_pgj": True,
                        "pension_system": instance.servidor.regime_previdenciario,
                    },
                )
                log.info("Update SocialSecurity %s" % instance.servidor.pessoa_fisica)
    except Exception as e:
        log.debug(e)
