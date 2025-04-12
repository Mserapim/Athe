# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.gfp.models import MovimentacaoProgressao
from rh.models import MovimentacaoAposentadoria, MovimentacaoDesligamento

log = getLogger(__name__)


@receiver(pre_delete, sender=MovimentacaoAposentadoria)
@receiver(pre_delete, sender=MovimentacaoDesligamento)
def resignation_move_undo(sender, instance, **kwargs):
    MovimentacaoProgressao.finish_progression_by_fire(instance, undo=True)
