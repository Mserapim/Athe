# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import Q
from django.dispatch import receiver
from rh.models import (
    MovimentacaoPosse,
    MovimentacaoAproveitamento,
    MovimentacaoPromocao,
    MovimentacaoRemocaoMembro,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoReversao,
    MovimentacaoTitularizacao,
)

from corregedoria.cirdir.models import ControlInformation
from contrib.middleware import set_current_user, get_current_user
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoAproveitamento)
@receiver(post_save, sender=MovimentacaoPromocao)
@receiver(post_save, sender=MovimentacaoRemocaoMembro)
@receiver(post_save, sender=MovimentacaoReadaptacao)
@receiver(post_save, sender=MovimentacaoReconducao)
@receiver(post_save, sender=MovimentacaoReintegracao)
@receiver(post_save, sender=MovimentacaoReversao)
@receiver(post_save, sender=MovimentacaoTitularizacao)
def signals_cirdir_movimentacao_posse(sender, instance=None, **kargs):
    pass
    # previous_user = get_current_user()
    # try:
    #     log.debug(">>>>>>> INICIANDO CONTROLE DE INFORMACOES CIRDIR >>>>>>> %s" % (instance.servidor))
    #
    #     with transaction.atomic():
    #         if instance.ativo and instance.servidor.tipo in ['M', 'S']:
    #             set_current_user(User.objects.get(username='athenas'))
    #             ControlInformation.create_control_information_to_employee(employee=instance.servidor, closed=False, user=previous_user)
    #             set_current_user(previous_user)
    #
    #     log.debug(">>>>>>> FINALIZANDO CONTROLE DE INFORMÃÇÕES CIRDIR >>>>>>> %s" % (instance.servidor))
    #
    # except Exception as e:
    #     log.debug(e)
    # finally:
    #     set_current_user(previous_user)
