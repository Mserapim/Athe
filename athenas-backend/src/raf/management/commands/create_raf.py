# -*- coding: utf-8 -*-
from optparse import make_option

from contrib.daterange import NewDateRange
from contrib.middleware import set_current_user
from contrib.utils import Locker
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from raf.models import FunctionalActivityReport, WorkerLocation, YearBase
from rh.models import Servidor

# from judicial.models import *
# from raf.models import *
# from rh.models import *

set_current_user(User.objects.get(username="athenas"))


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            "--month",
            default=None,
            type=int,
            dest="month",
            help="""Mês de referência para análise/criação do RAF.""",
        ),
        make_option(
            "--year",
            default=None,
            type=int,
            dest="year",
            help="""Ano de referência para análise/criação do RAF.""",
        ),
        make_option(
            "--registration",
            default=None,
            dest="registration",
            help="""Matrícula do membro para análise/criação de RAF.""",
        ),
    )

    def handle(self, month, year, registration, *args, **kargs):

        lock_file = Locker.create_lock("create_raf")

        list_of_employees = Servidor.objects.filter(tipo="M", ativo=True)
        if registration:
            list_of_employees = list_of_employees.filter(matricula=registration)
        month_reference = NewDateRange.from_month(month=month, year=year)
        print(
            "*======================================================================================================*"
        )
        print("  > Mes de Referencia: %s/%s" % (month, year))
        print(
            "*======================================================================================================*"
        )
        print(
            "  ***************************************************************************************"
        )
        for membro in list_of_employees.order_by("pessoa_fisica__nome"):
            if membro.ativo:
                print(
                    "    Membro: %s - cod:[MP%s]"
                    % (membro.pessoa_fisica.nome, membro.matricula)
                )
                raf = FunctionalActivityReport.objects.filter(
                    employee=membro, month=month, year=year
                ).first()
                if raf is None:
                    print("      -- Criando RAF")
                    raf = FunctionalActivityReport()
                    raf.employee = membro
                    raf.month = month
                    raf.year = year
                    raf.yearbase = YearBase.objects.get(activated=True)
                    raf.closed = True
                    raf.save()
                listaD = membro._raw_locations()
                listaExercicio = listaD.filter(
                    ~Q(lotacao__executionorgan=None)
                    & Q(designacao=True)
                    & Q(
                        Q(
                            data_vigencia_inicio__range=[
                                month_reference.first,
                                month_reference.last,
                            ]
                        )
                        | Q(
                            Q(data_vigencia_inicio__lte=month_reference.first)
                            & Q(
                                Q(
                                    data_vigencia_fim__range=[
                                        month_reference.first,
                                        month_reference.last,
                                    ]
                                )
                                | Q(data_vigencia_fim__gte=month_reference.last)
                                | Q(data_vigencia_fim=None)
                            )
                        )
                    )
                )
                if listaExercicio.order_by("lotacao__nome").count() > 0:
                    for d in listaExercicio:
                        worklocation = WorkerLocation.objects.filter(
                            raf=raf, location=d.lotacao
                        ).first()
                        if worklocation is None:
                            print(
                                "      > Adicionando lotacao: %s"
                                % (d.lotacao.order_nome)
                            )
                            worklocation = WorkerLocation()
                            worklocation.raf = raf
                            worklocation.location = d.lotacao
                            worklocation.save()
            print(
                "  ***************************************************************************************"
            )
        print(
            "*======================================================================================================*"
        )
        Locker.remove_lock(lock_file)
