# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Q

from contrib.middleware import get_current_user
from contrib.utils import DateUtils, getLogger
from default.testting import AthenasTestCase
from planejamento.contrato.models import Supervisor
from rh.ferias.models import (
    PASU_ALTERADO,
    PASU_FRUIDO,
    PASU_FRUINDO,
    PASU_HOMOLOGADO,
    PASU_INTERROMPIDO,
    PASU_SUSPENSO,
    AlteracaoPASU,
    AnotacaoFerias,
    FeriasAfastamento,
    PeriodoAquisitivo,
    PeriodoAquisitivoServidor,
    PeriodoAquisitivoServidorAdmin,
    PeriodoAquisitivoServidorMembro,
    PeriodoAquisitivoServidorUsufruto,
    VacationConflict,
)
from rh.models import Publicacao, Servidor, User
from rh.tests_api.utils import mock

log = getLogger(__name__)


class OutPut:

    def __init__(self, **kargs):
        self.verbose = False

    def _print(self, text, verbose=False):
        if verbose or self.verbose:
            print(text)


class FeriasTestCase(AthenasTestCase, OutPut):

    def setUp(self):
        self.verbose = False
        self.ferias_conf_test = FeriasConfTest()
        self.pa = self.ferias_conf_test.create_pa()
        self._print(self.pa)

    def tearDown(self):
        self.delete_all()

    def delete_all(self):
        try:
            for pa in self.ferias_conf_test.pa:
                pa.delete()
        except Exception as err:
            self._print("__delete_all__")
            self._print(err)
        try:
            for pasu in self.ferias_conf_test.pasu:
                pasu.delete()
        except Exception as err:
            self._print("__delete_all__")
            self._print(err)

    def unmark_all(self):
        try:
            self._print("unmark_all")
            self._print(len(self.ferias_conf_test.pasu))
            for pasu in self.ferias_conf_test.pasu:
                pasu.desmarcar()
            self.ferias_conf_test.pasu = []
        except Exception as err:
            self._print("__unmark_all__")
            self._print(err)

    @unittest.skip("skipping test_general")
    def test_general(self):
        self.verbose = True
        self._print("\n", True)
        for servidor in Servidor.objects.filter(tipo="M", ativo=True).filter(
            matricula=11092
        ):
            self._print("--------------------------------")
            self._print("SERVIDOR: %s - Ativo:%s" % (servidor, servidor.ativo), True)
            substitutos = servidor.my_substitute()
            servidores_substitutos = []
            self._print("CARGOS")
            for subs in substitutos:
                self._print(
                    "\n\tCARGO: (%s) %s - POSSUI_SUBSTITUTO: %s - EXERCICIO_PLENO: %s - AFASTADO %s"
                    % (
                        subs.get("cargo"),
                        subs.get("cargo_nome"),
                        subs.get("possui_substituto"),
                        subs.get("exercicio_pleno"),
                        subs.get("afastado"),
                    )
                )
                self._print("\tSUBSTITUTOS:")
                for s in subs.get("substitutos"):
                    # self._print('\t\t%s' % s)
                    self._print(
                        "\t\t%s - %s" % (s.get("cargo_subs_nome"), s.get("servidor"))
                    )
                    if (
                        s.get("servidor").matricula != servidor.matricula
                        and s.get("servidor").matricula not in servidores_substitutos
                    ):
                        servidores_substitutos.append(s.get("servidor").matricula)

    @unittest.skip("skipping test_conflitos")
    def test_conflitos(self):
        VacationConflict().conflicts(verbose=True)

    # @unittest.skip('skipping test_chek_conflicts_where_substitute')
    def test_chek_conflicts_where_substitute(self):
        VacationConflict().chek_conflicts_where_substitute(verbose=True)

    @unittest.skip("skipping test_conflicts_where_substitute")
    def test_conflicts_where_substitute(self):
        VacationConflict().conflicts_where_substitute(verbose=True)

    @unittest.skip("skipping test_employee_substitutes")
    def test_employee_substitutes(self):
        employee = Servidor.objects.get(matricula=13293)
        print(employee.my_substitute_employee())
        # print employee.my_substitute()
        for sub in employee.my_substitute():
            print(sub)

    @unittest.skip("skipping test")
    def test(self):
        pass
        # data_inicio = datetime(2014, 1, 1)
        # for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(pk__in=[11974, ]):
        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
            periodo_aquisitivo_servidor__pk=9556
        ):
            # data_inicio__gte=data_inicio,
            # periodo_aquisitivo_servidor__servidor__matricula=74907):
            print(pasu, pasu.get_estado_display())
            #     pasu.estado = PASU_FRUIDO
            #     pasu.data_fim = datetime(2014, 3, 6).date()
            #     pasu.suspenso_em = None
            #     pasu.interrompido = False
            #     pasu.save()
            pas = pasu.pas
            print(pas, pas.pk)
            #     pas.estado = PAS_FRUIDA
            #     pas.save()
            for alt in AlteracaoPASU.objects.filter(pas=pas.pk):
                print(alt)
                print("anotacao", alt.anotacao)
                print(
                    "autorizado",
                    ("SIM" if alt.autorizado else "NAO"),
                    " - DATA",
                    (
                        DateUtils.date_to_str(alt.autorizado_em)
                        if alt.autorizado_em
                        else "-----"
                    ),
                    " - autorizado_por",
                    alt.autorizado_por,
                )
                print("antigos", alt.antigos_pasus.all())
                print("novos", alt.novos_pasus.all())
            print("-------------------")


class FeriasPasusDepartures(unittest.TestCase):

    def test_pasus_departures(self):
        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
            # Q(periodo_aquisitivo_servidor__servidor__matricula=32201) &
            Q(periodo_aquisitivo_servidor__servidor__tipo="M")
            & (
                Q(created_at__gte=datetime(2016, 8, 1).date())
                | Q(modified_at__gte=datetime(2016, 8, 1).date())
            )
        ).order_by(
            "periodo_aquisitivo_servidor__servidor", "created_at", "modified_at"
        ):
            print(pasu.pas.servidor)
            print(
                pasu.get_estado_display(),
                pasu,
                DateUtils.date_to_str(pasu.created_at),
                DateUtils.date_to_str(pasu.modified_at),
            )
            try:
                pasu.save()
            except Exception as err:
                print(err)


class FeriasConfTest(OutPut):

    qtd_years = 4

    def __init__(self, **kargs):
        self.pa = []
        self.pasu = []

    def create_pa(self):
        latest = PeriodoAquisitivo.objects.filter(
            configuracao__tipo_servidor="M", configuracao__meses_exercicio=6
        ).latest("pk")
        new = PeriodoAquisitivo(
            ano_aquisicao=latest.ano_aquisicao + self.qtd_years,
            periodo=latest.periodo,
            # data_publicacao=latest.data_publicacao + relativedelta(year=self.qtd_years),
            configuracao=latest.configuracao,
            data_inicio_prev=latest.data_inicio_prev
            + relativedelta(year=self.qtd_years),
            # data_fim_prev=latest.data_fim_prev + relativedelta(year=self.qtd_years),
            # data_homologacao_prev=latest.data_homologacao_prev + relativedelta(year=self.qtd_years),
            # bloqueado
            # periodo_anterior
            # mes_fruicao
        )
        new.save()
        self.pa.append(new)
        return new

    def create_pasu(self, pas, date_begin, date_end):
        # self._print('__create_pasu__ %s %s' % (date_begin, date_end))
        pasu = None
        try:
            with transaction.atomic():
                pasus = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    periodo_aquisitivo_servidor=pas
                )
                if not pasus.exists():
                    pasu = pas.adicionar_usufruto(date_begin, date_end)
                else:
                    pasu = pasus.latest("pk")
            self.pasu.append(pasu)
        except Exception as err:
            self._print("__create_pasu__")
            self._print(err)
            raise err
        return pasu


class PeriodoAquisitivoServidorMembrotCase(AthenasTestCase):

    def test(self):
        pas = (
            PeriodoAquisitivoServidorMembro.objects.filter(servidor__matricula=6891)
            .order_by("pk")
            .latest("pk")
        )
        print(pas)
        print(pas.substitutos())
        pas.save()


class AlteracaoPASUTestCase(AthenasTestCase):

    classe = AlteracaoPASU

    def test_alteracao_ferias_epoca_oportuna(self):
        pasu = (
            PeriodoAquisitivoServidorUsufruto.objects.filter(
                data_inicio__gt=datetime.now().date()
            )
            .exclude(estado=PASU_ALTERADO)
            .latest("data_inicio")
        )
        print(
            pasu.periodo_aquisitivo_servidor.servidor, pasu, pasu.get_estado_display()
        )
        AlteracaoPASU.alteracao_ferias_epoca_oportuna(
            get_current_user(),
            pasu,
            pasu.periodo_aquisitivo_servidor.servidor,
            pasu.data_inicio,
            pasu.data_fim,
            "from test",
            mock(model=Publicacao, query=(~Q(data_vigencia=None))),
        )


class PeriodoAquisitivoServidorAdminTestCase(unittest.TestCase):

    @unittest.skip("DEPRECATED")
    def test_get_filter_conflitos_refactoring(self):
        for pas in PeriodoAquisitivoServidorAdmin.objects.filter(servidor__tipo="S"):
            print("pas")
            print(pas)
            original = pas._get_filter_conflitos_ORIGINAL()
            refactoring = pas._get_filter_conflitos()
            print("original")
            print(len(original))
            print("refactoring")
            print(len(refactoring))
            assert len(original) == len(refactoring)
            print("---------------------------------")


class PeriodoAquisitivoServidorMembroTestCase(unittest.TestCase):

    def test_get_filter_conflitos(self):
        for pas in PeriodoAquisitivoServidorAdmin.objects.filter(servidor__tipo="M"):
            pas._get_filter_conflitos()


class PeriodoAquisitivoServidorNaoCriadoTestCase(unittest.TestCase):

    def test(self):
        pa = PeriodoAquisitivo.objects.get(pk=107)
        print()
        print(
            pa,
            "¦",
            DateUtils.date_to_str(pa.created_at),
            "¦",
            pa.created_by,
            "¦",
            DateUtils.date_to_str(pa.modified_at),
            "¦",
            pa.modified_by,
        )
        pas = PeriodoAquisitivoServidor.objects.filter(periodo_aquisitivo=pa)
        # print(pas.count())
        employees = pas.values("servidor__pk")
        # print(len(employees))

        for employee in Servidor.objects.filter(ativo=True, tipo="S").exclude(
            pk__in=employees
        ):
            print(
                employee,
                "¦",
                DateUtils.date_to_str(employee.created_at),
                "¦",
                employee.created_by,
                "¦",
                DateUtils.date_to_str(employee.modified_at),
                "¦",
                employee.modified_by,
            )

        # for employee in Servidor.objects.filter(ativo=True, tipo='S', created_at__gte=datetime(2016, 9, 27)):
        #     print employee, '¦', DateUtils.date_to_str(employee.created_at), '¦', employee.created_by, '¦', DateUtils.date_to_str(employee.modified_at), '¦', employee.modified_by
        #     pas = PeriodoAquisitivoServidor.objects.get(periodo_aquisitivo=pa, servidor=employee)
        #     print pas, '¦', DateUtils.date_to_str(pas.created_at), '¦', pas.created_by, '¦', DateUtils.date_to_str(pas.modified_at), '¦', pas.modified_by


class PeriodoAquisitivoServidorUsufrutoEstadoErroTestCase(unittest.TestCase):

    def test(self):
        for pas in PeriodoAquisitivoServidorAdmin.objects.filter(
            servidor__matricula=109911
        ):
            print("--------------------------")
            print(pas)
            for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
                periodo_aquisitivo_servidor=pas
            ):
                print(
                    pasu.pk,
                    pasu,
                    pasu.created_by,
                    DateUtils.date_to_str(pasu.created_at),
                    pasu.modified_by,
                    DateUtils.date_to_str(pasu.modified_at),
                )
                if pasu.suspenso_em:
                    print(DateUtils.datetime_to_str(pasu.suspenso_em))
                    print(pasu.suspenso_por)
                # print('novos')
                # for p_in in pasu.alteracao_out.filter():
                #     print p_in.novos_pasus.filter(), p_in.novos_pasus.values('pk')
                # print('antigos')
                # for p_in in pasu.alteracao_out.filter():
                #     print p_in.antigos_pasus.filter(), p_in.antigos_pasus.values('pk')
                # print('novos')
                # for p_in in pasu.alteracao_in.filter():
                #     print p_in.novos_pasus.filter(), p_in.novos_pasus.values('pk')
                # print('antigos')
                # for p_in in pasu.alteracao_in.filter():
                #     print p_in.antigos_pasus.filter(), p_in.antigos_pasus.values('pk')
                # print('+++++++++++++++++++++++++++++++++')


class PeriodoAquisitivoServidorUsufrutoNaoCriadoTestCase(unittest.TestCase):

    def test(self):
        from rh.afastamento.models import CANCELED

        pasus = PeriodoAquisitivoServidorUsufruto.objects.filter(
            estado__in=[PASU_HOMOLOGADO, PASU_FRUINDO],  # , PASU_FRUIDO],
            periodo_aquisitivo_servidor__servidor__tipo="M",
            periodo_aquisitivo_servidor__servidor__ativo=True,
            # periodo_aquisitivo_servidor__servidor__matricula=32201,
            # data_inicio__gte=datetime.now().date(),
        ).distinct()
        print(pasus.count())
        for pasu in pasus.order_by("data_inicio"):
            ferias_afastamento = FeriasAfastamento.objects.filter(
                servidor=pasu.periodo_aquisitivo_servidor.servidor,
                data_inicio=pasu.data_inicio,
                data_prevista=pasu.data_fim,
                # data_prevista=pasu.data_prevista_fim
            ).exclude(estado=CANCELED)
            if not ferias_afastamento.exists():
                try:
                    FeriasAfastamento(
                        servidor=pasu.periodo_aquisitivo_servidor.servidor,
                        data_inicio=pasu.data_inicio,
                        # data_prevista=pasu.data_prevista_fim,
                        # data_prevista=pasu.data_fim,
                        data_fim=pasu.data_fim,
                        publicacao_movimentacao=None,
                    ).validate()
                except Exception as err:
                    print(
                        pasu,
                        "-",
                        pasu.get_estado_display(),
                        "-",
                        pasu.periodo_aquisitivo_servidor.servidor,
                    )
                    print(err)
                    # send_mail_and_notify(
                    #     source='Erro ao lançar afastamento de férias.',
                    #     message='Erro ao lançar afastamento de férias. %s' % unicode(err),
                    #     err=unicode(err),
                    #     employee=Servidor.objects.filter(user__groups__name__icontains='expediente-afastamento').distinct()
                    # )
                    print("-----------------------------")


class ConlifctAgreementTestCase(unittest.TestCase):

    def test(self):
        # from planejamento.contrato.models import *
        registry = [22999, 46403]
        date_start = datetime(2018, 12, 15).date()
        date_end = datetime(2018, 12, 31).date()
        for employee in Servidor.objects.filter(ativo=True, matricula__in=registry):
            # print(employee)
            res = Supervisor.get_employee_substitutes(
                employee.matricula, date_start, date_end
            )
            # print(res)
            if res:
                print(employee)
                print(res)
        # for agree in Contrato.objects.filter(agreementsupervisors__employee__matricula__in=registry).distinct():
        #    print(agree, DateUtils.date_to_str(agree.data_inicio), DateUtils.date_to_str(agree.data_vencimento) if agree.data_vencimento else '----')


class AnnotationVacation(unittest.TestCase):

    def test(self):
        employee_registry = [
            89608,
            142717,
            80707,
            66707,
            126514,
            139916,
            71607,
            111611,
            72007,
            78907,
            89608,
        ]

        query = AnotacaoFerias.objects.filter(
            resumo__icontains="Escala de Férias 2018 / 2019",
            servidor__matricula__in=employee_registry,
        )

        total = query.count()
        print("total: %s" % total)
        count = 0
        for af in query.order_by("servidor__pessoa_fisica__nome"):
            print(af.servidor)
            res = af.resumo.split(" / ")
            year = None
            if len(res) > 1:
                year = res[1]
                afs = AnotacaoFerias.objects.filter(
                    resumo="Escala de Férias %s / %s" % (int(year) - 1, year)
                )
                publication = None
                if afs.exists():
                    publication = afs[0].publicacao.pk
                pasu = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    periodo_aquisitivo_servidor__periodo_aquisitivo__ano_aquisicao=year,
                    periodo_aquisitivo_servidor__servidor=af.servidor,
                )
                pasu_id = []
                days = 0
                pas = None
                for p in pasu.order_by("created_at"):
                    days += p.dias
                    if days <= 30:
                        pas = p.periodo_aquisitivo_servidor
                        pasu_id.append(p.pk)
                    else:
                        break
                if pas:
                    try:
                        print(
                            pas.create_annotation(
                                params={"publicacao": publication}, pasus_id=pasu_id
                            )
                        )
                        af.delete()
                        count += 1
                    except Exception as err:
                        print(err)
            else:
                res = af.periodo.split("-")
                year = res[0]
                per = "Marcação de Férias %s-%s" % (year, res[1])
                afs = AnotacaoFerias.objects.filter(resumo=per).filter(
                    ~Q(publicacao=None)
                )
                if not afs.exists():
                    per = "Escala de Férias %s-%s" % (year, res[1])
                    afs = AnotacaoFerias.objects.filter(resumo=per).filter(
                        ~Q(publicacao=None)
                    )
                publication = None
                if afs.exists():
                    publication = afs[0].publicacao.pk if afs[0].publicacao else None
                pasu = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    periodo_aquisitivo_servidor__periodo_aquisitivo__ano_aquisicao=year,
                    periodo_aquisitivo_servidor__servidor=af.servidor,
                )
                pasu_id = []
                days = 0
                pas = None
                for p in pasu.order_by("created_at"):
                    days += p.dias
                    if days <= 30:
                        pas = p.periodo_aquisitivo_servidor
                        pasu_id.append(p.pk)
                    else:
                        break
                if pas:
                    try:
                        print(
                            pas.create_annotation(
                                params={"publicacao": publication}, pasus_id=pasu_id
                            )
                        )
                        af.delete()
                        count += 1
                    except Exception as err:
                        print(err)
            print("-----------------------")

        print(
            AnotacaoFerias.objects.filter(
                resumo__icontains="Escala de Férias 2018 / 2019",
                servidor__matricula__in=employee_registry,
            ).count()
        )
        print("total: %d" % total)
        print("realizado: %d" % count)


class PublicationVacationTestCase(unittest.TestCase):

    def test(self):
        info = {
            146: "ATO 00028/2018-CHGAB/DG (DIÁRIO ELETRÔNICO DO MPE nº 635)",  # '2018/2019'
            143: "ATO 00028/2017-CHGAB/DG (DIÁRIO ELETRÔNICO DO MPE nº 406)",  # '2017/2018'
            107: "ATO 00033/2016-CHGAB/DG (DIÁRIO ELETRÔNICO DO MPE nº 169)",  # '2016/2017'
            93: "ATO 00042/2015-CHGAB/DG (DOE TOCANTINS nº 4505)",  # '2015/2016'
            90: "ATO 00032/2014-CHGAB/DG (DOE TOCANTINS nº 4261)",  # '2014/2015'
            85: "ATO 00031/2013-CHGAB/DG (DOE TOCANTINS nº 4013)",  # '2013/2014'
            74: "ATO 00001/2012-CHGAB/DG (DOE TOCANTINS nº 3753)",  # '2012/2013'
            63: "ATO 00001/2011-DG (DOE TOCANTINS nº 3509)",  # '2011/2012'
            56: "ATO 00002/2010-DG (DOE TOCANTINS nº 3272)",  # '2010/2011'
            54: "ATO 00001/2009-DG (DOE TOCANTINS nº 3019)",  # '2009/2010'
            53: "ATO 00027/2008-DG (DOE TOCANTINS nº 2780)",  # '2008/2009'
            55: "ATO 00021/2007-DG (DOE TOCANTINS nº 2538)",  # '2007/2008'
            58: "OUTROS 000SN/2006-PGJ-TO (DOE TOCANTINS nº 2289)",  # '2006/2007'
            66: "OUTROS 000SN/2005-PGJ-TO (DOE TOCANTINS nº 2069)",  # '2005/2006'
            67: "PORTARIA 00671/2004 (DOE TOCANTINS nº 1807)",  # '2004/2005'
            68: "PORTARIA 00698/2003-PGJ-TO (DOE TOCANTINS nº 1569)",  # '2003/2004'
            78: "PORTARIA 00853/2002 (DOE TOCANTINS nº 1342)",  # '2002/2003'
            77: "PORTARIA 00343/2002 (DOE TOCANTINS nº 1201)",  # '2001/2002'
            79: "PORTARIA 00002/2001-PGJ-TO (DOE TOCANTINS nº 1004)",  # '2000/2001'
            73: "PORTARIA 00490/1999 (DOE TOCANTINS nº 869)",  # '1999/2000'
        }

        keys = list(info.keys())
        sorted(keys)

        for key in keys:
            try:
                publication = Publicacao.objects.get(cache_unicode=info.get(key))
                for pa in PeriodoAquisitivo.objects.filter(
                    pk=key, configuracao__tipo_servidor="S"
                ).order_by("ano_aquisicao"):
                    for pas in pa.paservidores.filter():
                        PeriodoAquisitivoServidor.objects.filter(pk=pas.pk).update(
                            homologation_publication=publication
                        )
                        print(pa, pas, publication)
            except Exception as err:
                print(err)
                print(info.get(key))


class VacationReportTestCase(unittest.TestCase):

    def test(self):
        start = datetime(2019, 1, 1).date()
        end = datetime(2019, 1, 31).date()

        print(DateUtils.date_to_str(start))
        print(DateUtils.date_to_str(end))

        query = Q(autorizado_em__gte=start, autorizado_em__lte=end)

        def check(pasu):
            found = []
            for p in PeriodoAquisitivoServidorUsufruto.objects.filter(
                Q(
                    periodo_aquisitivo_servidor__servidor=pasu.periodo_aquisitivo_servidor.servidor
                )
                & query
            ):
                if (
                    pasu.data_inicio == p.data_inicio and pasu.data_fim == p.data_fim
                ):  # and pasu.estado == p.estado:
                    print(
                        p,
                        " | ",
                        p.get_estado_display(),
                        " | ",
                        DateUtils.date_to_str(p.created_at),
                        " | ",
                        p.created_by,
                    )
                    found.append(p.pk)
            return found

        pasus_found = []
        for alt in (
            AlteracaoPASU.objects.filter(justificativa__icontains="desligamento")
            .filter(query)
            .filter(
                antigos_pasus__periodo_aquisitivo_servidor__servidor__ativo=True,
                antigos_pasus__periodo_aquisitivo_servidor__servidor__tipo="S",
                # antigos_pasus__periodo_aquisitivo_servidor__servidor__matricula__in=[46403, 65507]
            )
            .order_by(
                "antigos_pasus__periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome"
            )
            .distinct()
        ):
            a = alt.antigos_pasus.filter().values(
                "periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome"
            )
            print(
                a[0].get("periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome")
            )
            print(alt)
            for p in alt.antigos_pasus.filter():
                # print(p)
                pasus_found += check(p)
            print("----------------------------")
        print(pasus_found)

        registry = []

        for pasu in PeriodoAquisitivoServidorUsufruto.objects.filter(
            # query &
            Q(periodo_aquisitivo_servidor__servidor__tipo="S")
            & (Q(data_inicio__gte=start) & Q(data_inicio__lte=end))
            & Q(estado__in=[PASU_INTERROMPIDO, PASU_SUSPENSO])
        ):
            if (
                pasu.periodo_aquisitivo_servidor.servidor.is_comissionado
                and not pasu.periodo_aquisitivo_servidor.servidor.is_efetivo
            ):
                # print pasu.periodo_aquisitivo_servidor.servidor, pasu
                registry.append(pasu.periodo_aquisitivo_servidor.servidor.matricula)

        for pasu in (
            PeriodoAquisitivoServidorUsufruto.objects.filter(
                query
                & Q(periodo_aquisitivo_servidor__servidor__tipo="S")
                & Q(periodo_aquisitivo_servidor__servidor__matricula__in=registry)
                &
                # (Q(data_inicio__gte=start) & Q(data_inicio__lte=end)) #&
                Q(estado__in=[PASU_FRUIDO, PASU_FRUINDO, PASU_HOMOLOGADO])
            )
            .exclude(
                # pk__in=pasus_found
            )
            .order_by("periodo_aquisitivo_servidor__servidor__pessoa_fisica__nome")
        ):
            # if pasu.alteracao_in.exists() or pasu.alteracao_out.exists():
            # print pasu, pasu.periodo_aquisitivo_servidor.servidor
            if (
                pasu.periodo_aquisitivo_servidor.servidor.is_comissionado
                and not pasu.periodo_aquisitivo_servidor.servidor.is_efetivo
            ):
                print(
                    pasu.pk,
                    "|",
                    pasu,
                    "|",
                    pasu.get_estado_display(),
                    "|",
                    pasu.periodo_aquisitivo_servidor.servidor,
                    pasu.autorizado_por,
                )


def users_pk(names):
    users = User.objects.filter(username__in=names)
    count = users.count()

    # print(len(names), count)
    pks = []
    for user in users:
        # print(user.pk, user)
        pks.append(user.pk)
    return pks


class CheckErrorsTestCase(unittest.TestCase):

    def test_expediente(self):
        names = [
            "athenas",
            "nataliabarbosa",
            "elenilsoncorreia",
            "eliaslima",
            "williamgomes",
            "carolinesouza",
            "luismilhomem",
            "emannuellaoliveira",
            "ludmillarodrigues",
        ]
        users = users_pk(names)
        print("PERÍODOS COM MAIS DE 30 DIAS MARCADOS:")
        for pas in PeriodoAquisitivoServidor.objects.filter(
            servidor__ativo=True,
            servidor__tipo__in=[
                "M",
            ],
        ).order_by("servidor", "periodo_aquisitivo"):
            if pas.dias_marcados < 30 and pas.dias_marcados > 0 and not pas.paid_days:
                print(pas, pas.dias_marcados)

        # print('PARCELAS NÃO INTERROMPIDAS COM MAIS DE 10 OU 20:')
        # for pas in PeriodoAquisitivoServidor.objects.filter(servidor__ativo=True, servidor__tipo__in=['M', 'S']).order_by('servidor', 'periodo_aquisitivo'):
        #     if not pas.interrompido:
        #         for pasu in pas.usufrutos.filter(Q(dias__lt=10)):
        #             print(pas, pasu, pasu.dias)
