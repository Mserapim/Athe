# -*- coding: utf-8 -*-

from django.db.models import Q

from contrib.utils import getLogger
from rh.gfp.models import ContraCheque as Paycheck  # , Evento

# from rh.pensao import models as pensao_models
# from standard.models import RunCodeManager

log = getLogger(__name__)


# @receiver(post_save, sender=FolhaEvento)
def post_save_folha_evento_to_pensao_folha_evento(sender, instance, **kargs):
    """
    Este sinal tem o objetivo de atualizar uma PensaoFolhaEvento quando uma FolhaEvento for
    criada para o um Pensionista por Morte
    """
    if instance.oIds:
        pensions = instance.servidor.pensao_pagador.exclude(
            Q(data_inicio__gt=instance.contracheque.folha.date_range.last)
            | (
                ~Q(data_fim=None)
                & Q(data_fim__lt=instance.contracheque.folha.date_range.first)
            )
        ).filter(event_employee__genre_event=instance.evento.genre_event)
        if pensions:
            pensions = pensions.filter(pensionista__in=instance.oIds)

        if pensions.exists():
            paycheck, created = Paycheck.objects.get_or_create(
                servidor=instance.contracheque.servidor,
                folha=instance.contracheque.folha,
                pensioner=pensions.first().pensionista,
            )
            log.debug(
                ">> 1 SIGNAL PENSAO POST SAVE %s oIds (%s) %d - %s %s"
                % (
                    instance,
                    instance.oIds,
                    pensions.count(),
                    paycheck,
                    "C" if created else "E",
                )
            )
            paycheck.recalculate()
            log.debug(
                ">> 2 SIGNAL PENSAO POST SAVE %s oIds (%s) %d - %s %s"
                % (
                    instance,
                    instance.oIds,
                    pensions.count(),
                    paycheck,
                    "C" if created else "E",
                )
            )
    # if instance.servidor.pensao_pagador.exclude(pensaomorte=None).exists():
    #     log.debug('SIGNAL PENSAO MORTE POST SAVE %s' % instance.__class__.__name__)

    #     instance.origem_pensao.all().update(valor="0.00")

    #     pensoes = instance.servidor.pensao_pagador.exclude(
    #         Q(pensaomorte=None) |
    #         Q(data_inicio__gt=instance.contracheque.folha.date_range.last) |
    #         (
    #             ~Q(data_fim=None) &
    #             Q(data_fim__lt=instance.contracheque.folha.date_range.first)
    #         )
    #     )

    #     for pensao in pensoes:
    #         pensao = pensao.pensaomorte

    #         if pensao.eventos.filter(evento=instance.evento).exists() and pensao.eventos.get(evento=instance.evento).tipo_folhas.filter(id=instance.folha.tipo_folha.id):
    #             pensao_evento = pensao.eventos.get(evento=instance.evento)
    #             pensao_folha_evento, created = pensao.lancamentos.get_or_create(pensao=pensao, folha=instance.folha, evento=pensao_evento.evento)

    #             pensao_folha_evento.folha_evento = instance
    #             pensao_folha_evento.valor = "%.2f" % pensao_evento.apply_to_value(instance.valor)
    #             pensao_folha_evento.save()

    #         else:
    #             log.warn(u'A configuração da partilha para %s não foi definida para o evento %s.' % (pensao.pensionista, instance.evento))

    # elif instance.servidor.pensao_pagador.exclude(pensaoalimenticia=None):  # .filter(pensaoalimenticia__evento_pensao=instance.evento).exists():

    #     if instance.servidor.pensao_pagador.filter(pensaoalimenticia__evento_pensao__genre_event=instance.evento.genre_event) and instance.oIds:
    #         # if instance.servidor.pensao_pagador.filter(pensaoalimenticia__evento_pensao=instance.evento) and instance.oIds:
    #         log.debug(u'*SIGNAL PENSAO ALIMENTICIA POST SAVE %s oIds (%s)' % (instance, instance.vars))
    #         pensao = instance.servidor.pensao_pagador.get(pk=instance.oIds[0])
    #         eps = instance.folha.tipo_folha.eventos_pensao.filter(pensaoalimenticiaevento__pensao_alimenticia=pensao, evento_principal=True)
    #         if eps.exists():
    #             evento_principal = eps.get()
    #             pensao_folha_evento, created = pensao.lancamentos.get_or_create(folha=instance.folha, evento=evento_principal.evento)
    #             pensao_folha_evento.valor = 0.0
    #             pensao_folha_evento.valor_base = 0.0
    #             for fe in instance.contracheque.lancamentos.filter(evento__genre_event=instance.evento.genre_event):
    #                 if pensao.pk in fe.oIds:
    #                     log.debug('SIGNAL PENSAO: %s (%s)  %s >> %s' % (fe.oIds, pensao_folha_evento.valor, fe.valor, fe))
    #                     pensao_folha_evento.valor += float(fe.valor) if fe.evento.tipo == 'D' else -float(fe.valor)
    #                     pensao_folha_evento.valor_base += float(fe.valor_base) if fe.evento.tipo == 'D' else -float(fe.valor_base)
    #             pensao_folha_evento.save()
    #             pensao.lancamentos.filter(folha=instance.folha).exclude(pk__in=[pensao_folha_evento.pk, ]).delete()
    #     # elif instance.servidor.pensao_pagador.filter(pensaoalimenticia__evento_pensao__genre_event=instance.evento.genre_event) and instance.paycheck_difference:
    #     #     log.debug(u'*SIGNAL PENSAO ALIMENTICIA POST SAVE %s oIds (%s)' % (instance, instance.vars))


# @receiver(post_delete, sender=FolhaEvento)
def post_delete_folha_evento(sender, instance, **kargs):

    # Apagando os PensaoFolhaEvento que foram gerado a partir
    for pfe in instance.origem_pensao.all():
        pfe.delete()

    # Apagando os PensaoFolhaEvento que foram originados a partir dessa pensao e esse evento
    # pensao_models.PensaoFolhaEvento.objects.filter(folha=instance.folha, pensao__in=[p for p in instance.evento.eventos_origem_pensao.filter(servidor=instance.servidor, pensao_ptr__in=(instance.oIds or []))]).delete()
