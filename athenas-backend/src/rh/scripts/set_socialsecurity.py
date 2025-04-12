# -*- coding: utf-8 -*-
from datetime import date
from django.db.models import Count
from contrib.middleware import set_current_user
from rh.models import (
    Servidor as Employee,
    SocialSecurityConfig,
    PessoaJuridica,
    SocialSecurityEmployee,
)


def migrate_configs_social_security():
    set_current_user("athenas")
    employees = Employee.objects.all()
    for employee in employees:
        print(employee)
        ssc = SocialSecurityConfig.objects.by_organ(
            employee.organ_social_security
        ).filter(regime=employee.regime_previdenciario)
        print(ssc)
        if ssc.exists():
            if employee.data_referencia_ferias:
                new_ssc = ssc.currents_at(
                    employee.data_exercicio or employee.data_referencia_ferias
                ).last()
                print(employee.data_referencia_ferias, new_ssc)
                start = employee.data_exercicio or employee.data_referencia_ferias
                # if employee.data_desligamento and employee.data_desligamento < employee.data_referencia_ferias:
                #     start = employee.data_exercicio
                sse = SocialSecurityEmployee.objects.get_or_create(
                    employee=employee,
                    social_security_config=new_ssc,
                    start_validity=start,
                )  # ,
                # end_validity=employee.data_desligamento)
                print("%s CRIOU o " % ("Opaaa," if sse[1] else "NAO"), sse[0])


def get_config_from_organ(start, organ, regimes):
    configs = []
    for regime in regimes:
        ss = SocialSecurityConfig.objects.filter(organ=organ, regime=regime)
        # print(ss)
        if not ss.exists():
            ssc = SocialSecurityConfig.objects.get_or_create(
                organ=organ,
                regime=regime,
                mass_segregation_plan=1,
                start_validity=start,
            )
        else:
            # print('VAI ATUALIZAR A DATA', start)
            if organ.pk == 1813:  # igeprev
                print(ss.exclude(mass_segregation_plan=1).update(start_validity=start))
            else:
                print(ss.update(start_validity=start))
            ssc = ss.last(), False
        configs.append(ssc)
    return configs


def create_configs():
    organs = PessoaJuridica.objects.annotate(
        employees=Count("employees_organ_social_security")
    ).filter(employees__gt=0)
    for o in organs:
        # print(o)
        employees_o = o.employees_organ_social_security.filter(
            data_referencia_ferias__isnull=False
        )
        date_list = [s.data_exercicio or s.data_referencia_ferias for s in employees_o]
        date_list.append(o.created_at.date())
        regimes_o = set(sorted([x.regime_previdenciario for x in employees_o]))
        print(regimes_o)
        l_ssc = get_config_from_organ(min(date_list), o, list(regimes_o))
        for ssc in l_ssc:
            print("%s CRIOU o " % ("Opaaa," if ssc[1] else "NAO"), ssc[0])
