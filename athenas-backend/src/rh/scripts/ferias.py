# -.- coding: utf-8 -.-

import django
import os
import pstats
import cProfile, pstats, io
from pstats import SortKey
import sys
from io import StringIO
import time

from django.db import reset_queries

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from rh.ferias.models import *
from rh.models import (
    Lotacao,
    MovimentacaoSubstituicao,
    MovimentacaoSubstituicaoMembro,
    Replacement,
)


def ferias():
    # for pas in PeriodoAquisitivoServidorMembro.objects.filter(servidor__matricula=97309).filter(pk=15085):
    #     print(pas, pas.pk)
    #     for usu in pas.usufrutos.filter():
    # if usu.estado in (PASU_HOMOLOGADO, PASU_FRUINDO, PASU_AUTORIZADO_CI, PASU_EMALTERACAO, PASU_NOVO, PASU_SUBSTITUTO):
    #     print(usu, usu.get_estado_display())
    #     print(PeriodoAquisitivoServidorUsufruto.get_conflitos(pasus=[usu.pk]))
    # print(pas.conflitos(usu))
    # print(pas.conflitos_afastamento(usu))
    # print(pas.conflitos_substituicao(usu))
    # print(pas.conflitos_contratos(usu))
    for employee in Servidor.objects.filter(
        ativo=True,
        tipo="M",
        # matricula__in=[
        #     #97909
        #     88408,
        #     # 92108,
        #     # 98910,
        #     # 32201,
        #     # 51204,
        # ]
    ):
        # print(employee)
        # print('workplace_owner')
        # for rs in employee.owner_substitution_vacation():
        #     print(rs, Lotacao.objects.get(pk=rs))
        # print('my_replacement_substitute_vacation')
        # for rpl in [rs.get('registry') for rs in employee.replacement_substitutes_vacation().values()]:
        #     print(rpl)

        for usu in (
            PeriodoAquisitivoServidorUsufruto.objects.filter(
                estado__in=(
                    PASU_HOMOLOGADO,
                    PASU_FRUINDO,
                    PASU_AUTORIZADO_CI,
                    PASU_EMALTERACAO,
                    PASU_NOVO,
                    PASU_SUBSTITUTO,
                )
            )
            .filter(periodo_aquisitivo_servidor__servidor__tipo="M")
            .filter(periodo_aquisitivo_servidor__servidor=employee)
            .order_by("periodo_aquisitivo_servidor__servidor", "-data_inicio")
        ):  # .filter(pk=31814):
            if usu.estado in (
                PASU_HOMOLOGADO,
                PASU_FRUINDO,
                PASU_AUTORIZADO_CI,
                PASU_EMALTERACAO,
                PASU_NOVO,
                PASU_SUBSTITUTO,
            ):

                inicio = time.time()
                rs = PeriodoAquisitivoServidorUsufruto.get_conflitos(pasus=[usu.pk])
                fim = time.time()
                duration = fim - inicio

                inicio1 = time.time()
                rs1 = usu.pas.check_all_conflict(usu, limit=1)
                fim1 = time.time()
                duration1 = fim1 - inicio1
                if duration > 25:
                    # if True:
                    #     print(f'duration {duration}')
                    print(f"duration | duration1 - {duration} | {duration1}")
                    print(
                        f"{usu} | {usu.get_estado_display()} | {usu.periodo_aquisitivo_servidor.servidor}"
                    )
                    print(rs)
                    print(rs1)
                    print("-----------------------")

                # cProfile.run(f'PeriodoAquisitivoServidorUsufruto.get_conflitos(pasus=[{usu.pk}])', 'ferias')
                # p = pstats.Stats('ferias')
                # p.strip_dirs().sort_stats(SortKey.TIME).print_stats(0)
                # print(pas.conflitos(usu))
                # print(pas.conflitos_afastamento(usu))
                # print(pas.conflitos_substituicao(usu))
                # print(pas.conflitos_contratos(usu))


def test():
    for employee in Servidor.objects.filter(
        tipo="M",
        ativo=True,
        # matricula__in=[
        #     99310,
        #     # 32201,
        #     # 51204,
        #     # 77207,
        #     145417,
        #     155418,
        #     7591,
        #     92108,
        #     145817
        # ]
    ):
        # print(employee)
        # replacement_substitutes = employee.replacement_substitutes()
        # print(f'Substituições Tabela: {replacement_substitutes.count()}')
        # for rs in replacement_substitutes:
        #     print(rs)

        # replacement_substitutes_vacation = employee.replacement_substitutes_vacation()
        # print(f'Substituições para férias: {len(replacement_substitutes_vacation)}')
        # for rs in replacement_substitutes_vacation:
        #     print(replacement_substitutes_vacation.get(rs).get('substitute'))

        # replacement_substitutes_vacation = employee.replacement_substitutes_vacation()
        # for rs in replacement_substitutes_vacation:
        #     registry = replacement_substitutes_vacation.get(rs).get('registry')
        #     rpl = Replacement.objects.get(pk=rs)
        #     print(f'{rpl} | {rpl.substitute.pk} | {Servidor.objects.filter(matricula=registry).last()}')
        # for rs in employee.replacement_substitutes_employees():
        #     print(rs)
        # for rs in employee.replacement_to_substitute_tbl().values():
        #     print(rs)
        # for rs in employee.replacement_to_substitute():
        #     print(rs)
        # for rs in employee.replacement_to_substitute_employees():
        #     print(rs)
        # for rs in employee.owner_substitution_vacation():
        #     print(rs)
        if not employee.owner_substitution_vacation():
            print(employee)
            print(employee.owner_locations.last())
            print(employee.departures().last())
            print("---------------")


def test_workplace():
    for workplace in Lotacao.objects.filter(
        executionorgan__isnull=False,
        electoral_zone=False,
        # pk__in=[
        #     578
        #     # 423, 424, 425,
        #     44017,
        #     386, 542, 543, 387, 541,
        #     364, 371, 365, 368
        # ]
    ).order_by("order_nome"):
        print(f"{workplace.pk} {workplace}")

        owner_for_substitution = workplace.owner_substitution_vacation()
        if not owner_for_substitution:
            pass
            # print(f'{workplace} | {workplace.owner} | {MovimentacaoPosse.objects.filter(quadro__cargo__lotacao_responsavel=workplace, ativo=True)}')
            # print('---------------')
        else:
            print("TITULAR:")
            for rs in owner_for_substitution:
                print(
                    f"{Servidor.objects.filter(matricula=rs).last()} | {workplace.owner.last()}"
                )
                # if Servidor.objects.filter(matricula=rs).last() != workplace.owner.last():
                #     print(workplace)
                #     print(f'{Servidor.objects.filter(matricula=rs).last()} | {workplace.owner.last()}')
        print("Substitutos:")
        for rs in workplace.replacement_substitutes_employees():
            # print(Servidor.objects.filter(matricula=rs).last())
            print(rs)

        replacement_substitutes_tbl = workplace.replacement_substitutes_tbl()
        for rpl in replacement_substitutes_tbl:
            registry = replacement_substitutes_tbl.get(rpl).get("registry")
            print(f"{Replacement.objects.get(pk=rpl)} | {registry}")
        print("---------------")


def run():
    # test()
    # test_workplace()
    ferias()
    # test_method()
    # for m in MovimentacaoSubstituicao.objects.filter(servidor_substituido__ativo=True, servidor_substituido__tipo='M').filter(
    #     Q(data_fim=None) |
    #     Q(data_fim__gte=datetime.datetime.now().date()) |
    #     Q(afastamento__data_fim=None) | Q(afastamento__data_fim__gte=datetime.datetime.now().date())
    # ):
    #     emp = m.servidor_substituido
    #     # if not emp.owner_locations_can_substitute().filter(pk=m.place).exists():
    #     if m.place and not emp.owner_locations_can_substitute.filter(pk=m.place.pk).exists():
    #         print(m.afastamento.__str_restful__() if m.afastamento else 'Não existe afastamento!', m.servidor_substituido, m)
    #         print(f'Local da substituição: {m.place}')
    #         print(f'Não faz parte dos locais de substituição.')

    #         print(f'Locais atuais:')
    #         for l in emp.owner_locations_can_substitute:
    #             print(l)
    #         print('--------------------------------')


if __name__ == "__main__":
    run()
