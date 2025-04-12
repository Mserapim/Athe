# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.dispatch import receiver
from judicial.models import DistributionTable
from contrib.utils import getLogger

log = getLogger(__name__)


@receiver(post_save, sender=DistributionTable)
def organize_execution_organ(instance, *args, **kwargs):
    log.info("Analizando tabela de distribuição para %s", instance.execution_organ)
    execution_organ = instance.execution_organ

    if instance.execution_organ.active_matters.exists():
        log.info("Este Órgão de Execução é especializado em:")
        for dconf in instance.execution_organ.active_matters:
            log.info(" * %s", dconf.matter)
        if execution_organ.general_distribution:
            log.info("Corrigindo configuração do Órgão de Execução")
            execution_organ.general_distribution = False
            execution_organ.save()
    else:
        log.info("Este Órgão de Execução não é especializado.")
        if not execution_organ.general_distribution:
            log.info("Corrigindo configuração do Órgão de Execução")
            execution_organ.general_distribution = True
            execution_organ.save()
