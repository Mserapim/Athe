# -*- coding: utf-8 -*-

from datetime import date

from contrib.utils import getLogger
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rh.gfp.models import BankingEmployeeTypePayroll
from rh.gfp.models import ContraCheque as Paycheck
from rh.gfp.models import DadoBancarioServidorFolha

log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


@receiver(post_save, sender=BankingEmployeeTypePayroll)
def change_data_banking_person(sender, instance, **kwargs):
    """Change Contracheque.dado_bancario_pessoa after changes in BankingEmployeeTypePayroll."""
    query = Paycheck.objects.filter(
        servidor__pessoa_fisica=instance.person,
        folha__tipo_folha=instance.type_of_payroll,
        folha__status__in=[1, 2],
        folha__dt_pagamento__gt=date.today(),
    ).exclude(dado_bancario_pessoa=instance.banking_person)

    for cc in query:
        log.info("CONSOLIDATING %s" % cc)
        cc.consolidate(changes=4, save=True)

    return True


@receiver(post_delete, sender=DadoBancarioServidorFolha)
@receiver(post_save, sender=DadoBancarioServidorFolha)
def update_paychecks_after_change_bank_information(sender, **kargs):
    dbsf = kargs.get("instance", None)
    log.info("UPDATE PAYCHECKS %s" % dbsf.dado_bancario_pessoa)

    if dbsf:
        # UPDATING PAYCHECKS Servidores -------------------------
        for paycheck in Paycheck.objects.filter(
            servidor__pessoa_fisica=dbsf.dado_bancario_pessoa.pessoa,
            folha__tipo_folha=dbsf.tipo_folha,
            folha__status__in=[1, 2],
        ):
            paycheck.consolidate()  # Consolidando as informações bancárias
            log.debug("CHANGE paychecks: %s" % paycheck)
