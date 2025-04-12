# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.cif.models import ControlInformationMember, ReferencePeriod
from rh.models import (
    MovimentacaoAproveitamento,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoRemocaoMembro,
    MovimentacaoReversao,
    MovimentacaoTitularizacao,
)

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
def signals_cif_movimentacao_posse(sender, instance=None, **kargs):
    try:
        log.debug(
            ">>> CONTROLE DE INFORMÃÇÕES MEMBROS - CIF >>>>>>>>>>>>> %s"
            % (instance.servidor)
        )
        with transaction.atomic():

            if (
                instance.ativo
                and instance.servidor.tipo == "M"
                and instance.quadro.cargo.tipo_lei_cargo == "EF"
            ):
                references_period = ReferencePeriod.objects.filter(
                    Q(start_date__lte=instance.data_exercicio)
                    & (Q(end_date=None) | Q(end_date__gte=instance.data_exercicio)),
                    main_period=True,
                )
                refperiod = (
                    references_period.latest("id")
                    if references_period.exists()
                    else ReferencePeriod.objects.filter(main_period=True).latest("id")
                )
                cif = ControlInformationMember.objects.filter(
                    employee__servidor=instance.servidor
                )
                try:
                    m = MovimentacaoPosse.objects.filter(
                        servidor_id=instance.servidor.id, ativo=True
                    ).first()
                except Exception:
                    raise ("Não há movimentação de posse ativa.")
                if cif.exists():
                    if cif.filter(status=1).exists():
                        log.info("Atualizando controle de informações ativos")
                        cif_change = cif.latest("id")
                        cif_change.employee = m
                        cif_change.save()
                    else:
                        log.info(
                            "Criando novo controle de informações a partir de um outro"
                        )
                        old_cif = cif.latest("id")
                        new_cif = ControlInformationMember(
                            employee=m,
                            referenceperiod=refperiod,
                            previous_controlinformation=old_cif,
                        )
                        new_cif.save()
                        new_cif.copy_controlinformation(old_information=old_cif)
                else:
                    log.info("Criando novo membro no gestor")
                    ControlInformationMember(
                        employee=instance.movimentacaoposse,
                        referenceperiod=refperiod,
                    ).save()
            else:
                pass
                # log.info('Já existe controle de informações para este Membro')

        log.debug(
            ">>> FINALIZANDO CONTROLE DE INFORMÃÇÕES MEMBROS - CIF >>>>>>>>>>>>> %s"
            % (instance.servidor)
        )

    except Exception as e:
        log.debug(e)


# @receiver(post_save, sender=MovimentacaoDesligamento)
# @receiver(post_delete, sender=MovimentacaoDesligamento)
# @receiver(post_save, sender=MovimentacaoAposentadoria)
# @receiver(post_delete, sender=MovimentacaoAposentadoria)
# def signals_cif_movimentacao_desligamento(sender, instance=None, **kargs):
#     try:
#         print ">>> DESLIGAMENTO EM CONTROLE DE INFORMÃÇÕES MEMBROS - CIF >>>>>>>>>>>>>"
#         cifs = ControlInformationMember.objects.filter(employee=instance.movimentacao_posse, status=1)
#         for cif in cifs:
#             cif.status = 2
#             cif.save()
#             log.info('Controle de Informações de: %s está sendo inativada' % cif)

#     except Exception, e:
#         log.debug(e)
