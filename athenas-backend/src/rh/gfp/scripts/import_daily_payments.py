# -*- coding: utf-8 -*-
"""
    Este script corrige as publicações de movimentação dos colaboradores.
    Escrevendo as publicações que estão em DeclaracaoAtividade para PossessionCollaborator.
"""

from datetime import datetime
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import PessoaFisica, SocialSecurityConfig, SocialSecurityEmployee
from rh.gfp.models import Periodo, Folha
from rh.gfp.tools.import_payroll import import_payments

log = getLogger(__name__)


set_current_user("athenas")


def run():

    def rm_payroll(period):
        print(f"APAGANDO CONTRACHEQUES de diárias de {period}")
        for payroll in Folha.objects.filter(periodo=period, tipo_folha__pk=175):
            Folha.objects.filter(pk=payroll.pk).update(status=1)
            payroll.refresh_from_db()
            # print(payroll.status)
            for l in payroll.lancamentos.filter():
                # print(l)
                l.delete()
            for c in payroll.paychecks.filter():
                # print(c)
                try:
                    c.delete()
                except Exception as err:
                    print(err)
            try:
                payroll.delete()
            except Exception as err:
                print(err)

        for natural_person in PessoaFisica.objects.filter(
            servidor__type_by_possession="COE"
        ):
            for employee in natural_person.servidor_set.filter():
                print(f"APAGANDO SERVIDOR E CONTRACHEQUE: {employee}")
                try:
                    employee.paychecks.filter().delete()
                    employee.delete()
                except Exception as err:
                    print(err)

    query = Periodo.objects.filter(ano=2022, mes=8).exclude(mes=13)
    for period in query.order_by("ano", "mes"):
        rm_payroll(period)
        # import_payments(1, period)

    # print('CRIANDO SEGURIDADE SOCIAL')
    # start_validity = datetime(2010, 1, 1).date()
    # ss = SocialSecurityConfig.objects.get(pk=1) # INSS
    # ss = SocialSecurityConfig.objects.get(pk=3) # IGEPREV
    # for natural_person in PessoaFisica.objects.filter(pk__in=natpks):
    #     for employee in natural_person.servidor_set.filter():
    #         sse, created = SocialSecurityEmployee.objects.get_or_create(
    #             employee=employee, social_security_config=ss, start_validity=start_validity)
    #         print(created, sse)


if __name__ == "__main__":
    run()
