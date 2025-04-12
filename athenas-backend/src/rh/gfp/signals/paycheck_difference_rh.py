# -*- coding: utf-8 -*-

from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.gfp.models import MovimentacaoEnquadramento, MovimentacaoProgressao
from rh.gfp.models import Periodo as Period


log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


@receiver(post_save, sender=MovimentacaoProgressao)
# @receiver(post_delete, sender=MovimentacaoProgressao)
@receiver(post_save, sender=MovimentacaoEnquadramento)
# @receiver(post_delete, sender=MovimentacaoEnquadramento)
def change_salary_progression(sender, instance, **kwargs):

    last_period = Period.objects.order_by("-ano", "-mes").first()
    effective_diff_range = NewDateRange(date(2015, 5, 1), last_period.end_date)
    log.debug(
        "PAYCHECKDIFFERENCE SIGNALS: %s > %s %s [%s] (%s)"
        % (sender, instance, effective_diff_range, instance.old_fields, kwargs)
    )

    diff_range = NewDateRange()

    if kwargs.get("created", False):
        diff_range += NewDateRange(
            instance.data_inicio_vigencia, instance.expected_date
        )
        # log.debug('PAYCHECKDIFFERENCE SIGNALS: DIFF %s' % diff_range)
    elif set(instance.old_fields.keys()).intersection(
        set(["referencia_nivel2d", "data_inicio_vigencia", "data_fim_vigencia"])
    ):
        old_range = NewDateRange(
            instance.old_fields.get(
                "data_inicio_vigencia", instance.data_inicio_vigencia
            ),
            instance.old_fields.get("data_fim_vigencia", instance.data_fim_vigencia),
        )
        new_range = NewDateRange(
            instance.data_inicio_vigencia, instance.data_fim_vigencia
        )
        diff_range += old_range + new_range

        if set(instance.old_fields.keys()).intersection(
            set(["data_inicio_vigencia", "data_fim_vigencia"])
        ):
            diff_range = diff_range - (old_range.intersect(new_range))

    log.debug(
        "PAYCHECKDIFFERENCE SIGNALS: DIFF %s"
        % diff_range.intersect(effective_diff_range)
    )

    return diff_range.intersect(effective_diff_range)
