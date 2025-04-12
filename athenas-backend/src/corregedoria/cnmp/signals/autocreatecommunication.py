# -*- coding: utf-8 -*-
"""
Sinais usados para criar automaticamente as comunicações
"""
import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from contrib.utils import getLogger
from standard.models import Configuration
from datetime import date, timedelta
from rh.models import (
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoRemocaoMembro,
    MovimentacaoTitularizacao,
)
from corregedoria.cirdir.models import ControlInformation
from corregedoria.cnmp.models import Communication


log = getLogger(__name__)


@receiver(post_save, sender=ControlInformation)
def submitted_control_information(sender, instance, created, **kargs):
    cfg = Configuration.get_or_create("corregedoria")
    gen = False
    try:
        if (
            getattr(instance, "_run_signal", True)
            and instance.employee.tipo == "M"
            and instance.year == date.today().year
        ):
            log.info("verificando dados srdir de: {}".format(str(instance.employee)))

            if instance.address_submitted_by and instance.pendency_address is False:
                log.info("Necessario criar uma comunicacao. Endereco atualizado")
                gen = True

            if (
                instance.teaching_1st_semestry_submitted_by
                and instance.pendency_teaching_1st_semestry is False
            ):
                log.info("Necessario criar uma comunicacao. Docencia 1st atualizado")
                gen = True

            if (
                instance.teaching_2nd_semestry_submitted_by
                and instance.pendency_teaching_2nd_semestry is False
            ):
                log.info("Necessario criar uma comunicacao. Docencia 2st atualizado")
                gen = True

        try:
            if gen:
                log.info("Criando comunicacao")
                Communication.generate(employee=instance.employee)
        except Exception as e:
            log.exception("Erro ao criar comunicacao")

    except Exception as e:
        log.exception(e)


@receiver(post_save, sender=MovimentacaoPosse)
@receiver(post_save, sender=MovimentacaoPromocao)
@receiver(post_save, sender=MovimentacaoRemocaoMembro)
@receiver(post_save, sender=MovimentacaoTitularizacao)
def possession_movement_employee(sender, instance, created, **kargs):
    if created:
        cfg = Configuration.get_or_create("corregedoria")
        try:
            if instance.servidor.tipo == "M":
                log.info(
                    "Movimentacao criada/alterada para {}".format(
                        str(instance.servidor)
                    )
                )

                try:
                    log.info(
                        "verificando a necessidade de criar uma comunicacao ao SCMMP."
                    )
                    Communication.generate(employee=instance.servidor)
                except Exception as e:
                    log.exception("Erro ao criar comunicacao")

        except Exception as e:
            log.exception(e)
