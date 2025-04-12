# -*- coding: utf-8 -*-
from adm.patrimonio.models import Movimento
from contrib.utils import DateUtils, employee_from_user, getLogger, person_from_user
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from engine.notification.models import Message, Notification
from rh.models import Servidor

log = getLogger(__name__)


@receiver(pre_save, sender=Movimento)
def movimento_localizacao_send_menssage(sender, instance, **kargs):
    log.info("* " * 60)
    if instance.pk and instance.responsavel_destino:
        older = Movimento.objects.get(pk=instance.pk)
        instance.status = int(instance.status)
        message = None
        target = None

        instance.status = int(instance.status or 0)

        if older.status == 1 and instance.status == 2:
            """
            aguardando recebimento
            """
            log.info("enviando mensagem de aguardando recebimento.")
            message = Message.objects.get(mid="PAT_MOV_PEDIDO_RECEBIMENTO")
            target = [instance.responsavel_destino]
        elif older.status in (1, 2) and instance.status == 3:
            """
            aguardando validação
            """
            log.info("enviando mensagem de aguardando validação.")
            message = Message.objects.get(mid="PAT_MOVD_VALIDAR")
            query = Servidor.objects.filter(
                Q(
                    user__user_permissions__content_type__app_label="patrimonio",
                    user__user_permissions__codename__in=(
                        "validate_movimento",
                        "admin_movimento",
                    ),
                )
                | Q(
                    user__groups__permissions__content_type__app_label="patrimonio",
                    user__groups__permissions__codename__in=(
                        "validate_movimento",
                        "admin_movimento",
                    ),
                )
            )
            target = [employee for employee in query]
        elif older.status == 2 and instance.status == 1:
            """
            reaberto
            """
            log.info("enviando mensagem de reabertura.")
            message = Message.objects.get(mid="PAT_MOV_REABERTO")
            target = (employee_from_user(instance.movimentado_por),)
        elif older.status == 3 and instance.status == 4:
            """
            validado
            """
            log.info("movimentação validada.")
            message = Message.objects.get(mid="PAT_MOV_VALIDADO")
            target = (employee_from_user(instance.movimentado_por),)
        elif older.status == 4 and instance.status == 6:
            """Autorizado"""
            log.info("movimento autorizado.")
            message = Message.objects.get(mid="PAT_MOV_AUTHORIZED")
            target = [
                employee_from_user(instance.movimentado_por),
                instance.responsavel_destino,
            ]
        elif instance.status == 5:
            """
            cancelado
            """
            log.info("movimentação cancelada.")

        target = [dest for dest in target if dest] if target else []

        if message and target:
            params = {
                "cedente": str(person_from_user(instance.movimentado_por)),
                "numero": "%05d/%d" % (instance.numero, instance.ano),
                "movimentado": DateUtils.date_to_str(instance.movimentado),
            }

            log.info(
                "Send notification for %s", ", ".join([str(dest) for dest in target])
            )

            Notification.notify_all(message, target, sender=None, **params)
        else:
            log.debug((message, target))
    elif instance.pk is None:
        log.info("Não preciso notificar criação de de movimentação.")
    log.info("* " * 60)


@receiver(pre_save, sender=Movimento)
def movimento_responsavel_send_menssage(sender, instance, **kargs):
    if instance.pk is not None and instance.responsavel_destino is not None:
        older = Movimento.objects.get(pk=instance.pk)
        instance.status = int(instance.status)
        message = None
        target = None

        if older.status == 1 and instance.status == 2:
            """
            aguardando recebimento
            """
            log.info("enviando mensagem de aguardando recebimento.")
            message = Message.objects.get(mid="PAT_MOV_PEDIDO_RECEBIMENTO")
            target = (instance.responsavel_destino,)
        elif older.status == 2 and instance.status == 3:
            """
            aguardando validação
            """
            log.info("enviando mensagem de aguardando validação.")
            message = Message.objects.get(mid="PAT_MOV_VALIDAR")
            query = Servidor.objects.filter(
                Q(
                    user__user_permissions__content_type__app_label="patrimonio",
                    user__user_permissions__codename__in=(
                        "validate_movimento",
                        "admin_movimento",
                    ),
                )
                | Q(
                    user__groups__permissions__content_type__app_label="patrimonio",
                    user__groups__permissions__codename__in=(
                        "validate_movimento",
                        "admin_movimento",
                    ),
                )
            )
            target = [employee for employee in query]
        elif older.status == 2 and instance.status == 1:
            """
            reaberto
            """
            log.info("enviando mensagem de reabertura.")
            message = Message.objects.get(mid="PAT_MOV_REABERTO")
            target = (employee_from_user(instance.movimentado_por),)
        elif older.status == 3 and instance.status == 4:
            """
            validado
            """
            log.info("movimentação validada.")
            message = Message.objects.get(mid="PAT_MOV_VALIDADO")
            target = (
                instance.responsavel_destino,
                employee_from_user(instance.movimentado_por),
            )
        elif instance.status == 5:
            """
            cancelado
            """
            log.info("movimentação cancelada.")

        target = [dest for dest in target if dest] if target else []

        if message is not None and target is not None:
            params = {
                "cedente": str(person_from_user(instance.movimentado_por)),
                "favorecido": str(instance.responsavel_destino.pessoa_fisica),
                "numero": "%05d/%d" % (instance.numero, instance.ano),
                "movimentado": DateUtils.date_to_str(instance.movimentado),
            }

            log.info(
                "Send notification for %s", ", ".join([str(dest) for dest in target])
            )

            Notification.notify_all(message, target, sender=None, **params)
    elif instance.pk is None:
        log.info("Não preciso notificar criação de de movimentação.")
