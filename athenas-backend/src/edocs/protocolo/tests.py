# -.- coding: utf-8 -.-
from django.db.models import Q
from edocs.protocolo.models import *
from edocs.protocolo.utils import *
from rh.models import Servidor, Lotacao, ServidorLotacao
from datetime import datetime
from dateutil.relativedelta import relativedelta
from contrib.utils import getLogger
from default.testting import AthenasTestCase
from rh.tests_api.utils import mock
from contrib.middleware import set_current_user, get_current_user
from contrib.utils import user_from_person
from django.contrib.auth.models import User
from edocs.protocolo.utils import EDOCBoxQuery
from engine.mq.models import Task

# Movimentacao.objects.filter(pk__in=[328502, 328500]).update(
#     encaminhado=False, data_finalizado=None, data_encaminhamento=None)

# #-.- coding: utf-8 -.-
# from edocs.protocolo.models import Protocolo, Movimentacao
# protocolos = Protocolo.objects.filter(codigo__in=
#     (
#         '07010098046201575',
#         '07010097379201587',
#         '07010097389201512',
#         '07010098047201511',
#     )
# )
# for protocolo in protocolos:
#     print(u'----------->>>PROTOCOLO')
#     print('codigo:', protocolo.codigo)
#     print('lotacao_criacao:', protocolo.lotacao_criacao)
#     print('orgao_geral_origem:', protocolo.orgao_geral_origem)
#     print('orgao_geral_destino:', protocolo.orgao_geral_destino)
#     print('servidor_origem:', protocolo.servidor_origem)
#     print('interessado:', protocolo.interessado)
#     print(u'-----MOVIMENTAÇÕES-------')
#     movimentacoes = Movimentacao.objects.filter(protocolo=protocolo)
#     for mov in movimentacoes:
#         print('pk:', mov.pk, 'passo:', mov.passo)
#         print('lotacao_criacao:', mov.lotacao_criacao)
#         print('lotacao_origem:', mov.lotacao_origem)
#         print('lotacao_destino:', mov.lotacao_destino)
#         print('servidor_origem:', mov.servidor_origem)
#         print('servidor_destino:', mov.servidor_destino)
#         print('data_encaminhamento:', mov.data_encaminhamento)
#         print('encaminhado:', mov.encaminhado)
#         print('data_finalizado:', mov.data_finalizado)
#         print('created_by:', mov.created_by)
#         print('created_at:', mov.created_at)
#         print('modified_by:', mov.modified_by)
#         print('modified_at:', mov.modified_at)
#         print('------------')


log = getLogger(__name__)


def setUpModule():
    RHConfiguracaoTests.setUpModule()


def tearDownModule():
    RHConfiguracaoTests.tearDownModule()


class EdocsTestCase(AthenasTestCase):

    @unittest.skip("skipping test")
    def test(self):
        self.teste()
        # self.teste([
        #     '07010098046201575',
        #     '07010097379201587',
        # ])
        # self.teste([
        #     '07010097389201512',
        #     '07010098047201511',
        # ])

    @unittest.skip("skipping teste")
    def teste(self, codigo=[]):
        print("#############################################")
        protocolos = Protocolo.objects.filter(
            codigo__in=[
                "07010098177201552",
            ]
        )
        for protocolo in protocolos:
            print("----------->>>PROTOCOLO")
            print("codigo:", protocolo.codigo)
            print("lotacao_criacao:", protocolo.lotacao_criacao)
            print("orgao_geral_origem:", protocolo.orgao_geral_origem)
            print("orgao_geral_destino:", protocolo.orgao_geral_destino)
            print("servidor_origem:", protocolo.servidor_origem)
            print("interessado:", protocolo.interessado)
            print("-----MOVIMENTAÇÕES-------")
            movimentacoes = Movimentacao.objects.filter(protocolo=protocolo)
            for mov in movimentacoes.order_by("passo"):
                print("pk:", mov.pk, "passo:", mov.passo)
                print("lotacao_criacao:", mov.lotacao_criacao)
                print("lotacao_origem:", mov.lotacao_origem)
                print("lotacao_destino:", mov.lotacao_destino)
                print("servidor_origem:", mov.servidor_origem)
                print("servidor_destino:", mov.servidor_destino)
                print("data_encaminhamento:", mov.data_encaminhamento)
                print("encaminhado:", mov.encaminhado)
                print("data_finalizado:", mov.data_finalizado)
                print("created_by:", mov.created_by)
                print("created_at:", mov.created_at)
                print("modified_by:", mov.modified_by)
                print("modified_at:", mov.modified_at)
                print("------------")

    def show(self):
        from auditoria.models import LineLog

        l = LineLog.objects.latest("pk")
        print(l.get_status_display(), l.json_description)
        p = Protocolo.objects.latest("pk")
        print(
            "\nPROTOCOLO:",
            p,
            "PK:",
            p.pk,
            "| CRIADO EM:",
            DateUtils.datetime_to_str(p.created_at),
            "MOVIMENTAÇÕES:",
            p.movimentacoes.count(),
        )

    # @unittest.skip('skipping')
    def test_novo_protocolo(self):

        Protocolo.objects.latest("pk").delete()

        servidor = Servidor.objects.get(matricula=94109)
        interessado = Servidor.objects.get(matricula=94109)
        tipo_documento = TipoDocumento.objects.latest("pk").pk
        lotacao_origem = Lotacao.objects.get(pk=553)
        codigo = ""
        chancela = ""
        midia = None
        assunto = "TESTE TESTE TESTE FINALIZAÇÃO DE DOCUMENTOS"
        numero_externo = ""
        resumo = "TESTE TESTE TESTE FINALIZAÇÃO DE DOCUMENTOS"
        sigiloso = False
        anexos = []
        referencias = []

        ProtocoloManager.novo_protocolo(
            {
                "servidor": servidor.pk,
                "tipo_documento": tipo_documento,
                "orgao_geral": lotacao_origem.pk,
                "interessado": interessado.pessoa_fisica.pk,
                "codigo": codigo,
                "chancela": chancela,
                "midia": midia,
                "assunto": assunto,
                "numero_externo": numero_externo,
                "resumo": resumo,
                "sigiloso": sigiloso,
                "anexos": anexos,
                "referencias": referencias,
            }
        )
        self.show()
        protocolo = Protocolo.objects.latest("pk")
        protocolo.save()
        self.show()

        move = protocolo.movimentacoes.filter().get()

        set_current_user(User.objects.get(username="gustavodettenborn"))

        move.do_send(
            location_destination=[546, 554, 544],
            references='{"create":[],"update":[],"delete":[]}',
            attachments='{"create":[],"update":[],"delete":[]}',
        )

        close = False
        destiny = [43793, 447]
        count = 0
        for move in protocolo.movimentacoes.filter().order_by("-passo")[0:2]:
            # ORIGINAL
            # employee = ServidorLotacao.objects.filter(
            #     ativo=True, servidor__ativo=True).filter(lotacao=move.lotacao_destino).latest('pk').servidor
            # REFACTORING
            employee = (
                ServidorLotacao.work_assignment_exercise()
                .filter(servidor__ativo=True, lotacao=move.lotacao_destino)
                .latest("pk")
                .servidor
            )
            print(employee)
            print(move)
            print(move.lotacao_destino)
            set_current_user(employee.user)
            move.sign_received()
            move.do_send(
                close=close,
                location_destination=destiny[count],
                references='{"create":[],"update":[],"delete":[]}',
                attachments='{"create":[],"update":[],"delete":[]}',
            )
            close = not close
            count += 1

    @unittest.skip("skipping test_nova_movimentacao")
    def test_nova_movimentacao(self):
        servidor = Servidor.objects.get(matricula=5790)
        movimentacoes = (
            EDOCBoxQuery(
                servidor=servidor,
                lotacoes=[lotacao.pk for lotacao in servidor.work_assignment],
                valor=None,
                lotacoes_protocolo_geral=[
                    lotacao.pk if lotacao.acesso_protocolo_geral else None
                    for lotacao in servidor.work_assignment
                ],
            )
            .get_caixa_entrada()
            .exclude(EDOCBoxQuery.get_finalizado_recebido())
            .filter(protocolo__processo=None)
        )
        for movimentacao in movimentacoes.order_by("-pk"):
            if MovimentacaoManager.is_recebido(movimentacao):
                self.movimentacao(movimentacao)
                break

    @unittest.skip("skipping test_nova_movimentacao_lote")
    def test_nova_movimentacao_lote(self):
        servidor = Servidor.objects.get(matricula=5790)
        movimentacoes = (
            EDOCBoxQuery(
                servidor=servidor,
                lotacoes=[lotacao.pk for lotacao in servidor.work_assignment],
                valor=None,
                lotacoes_protocolo_geral=[
                    lotacao.pk if lotacao.acesso_protocolo_geral else None
                    for lotacao in servidor.work_assignment
                ],
            )
            .get_caixa_entrada()
            .exclude(EDOCBoxQuery.get_finalizado_recebido())
            .filter(protocolo__processo=None)
        )
        for movimentacao in movimentacoes.order_by("-pk")[0:5]:
            if MovimentacaoManager.is_recebido(movimentacao):
                self.movimentacao(movimentacao)

    def movimentacao(self, movimentacao):
        pessoa_lotacoes = []
        lotacoes_destino = []
        servidor_lotacoes = []
        result_lotacao, message_lotacao = True, ""
        result_pessoa, message_pessoa = True, ""

        servidor = Servidor.objects.get(matricula=5790)

        protocolo = movimentacao.protocolo
        ProtocoloManager.is_protocolo(protocolo)

        if movimentacao.with_workflow:
            raise Exception(
                "Este protocolo não pode ser movimentado por aqui. Ele possui software especifico para isto."
            )

        # self.is_destino_definido_from_post()

        # if self.is_destino_nao_definido_and_concluido_definido_from_post():
        #     try:
        #         servidor_lotacoes = [[protocolo.interessado.pk, protocolo.orgao_geral_origem.pk]]
        #     except: pass
        # else:
        #     servidor_lotacoes, pessoa_lotacoes = self.get_servidor_lotacoes_e_pessoa_lotacoes_from_post()

        servidor_lotacoes = []
        pessoa_lotacoes = []

        movimentacao = protocolo.movimentacoes.latest("pk")
        MovimentacaoManager.is_movimentacao(movimentacao)

        # lotacoes_destino = self.remove_lotacao_da_pessoa(pessoa_lotacoes)
        lotacoes_destino = [
            546,
        ]

        EDOCBoxManager.is_lotacoes_em_organograma(lotacoes_destino)

        # self.is_destino(lotacoes_destino, pessoa_lotacoes, servidor_lotacoes)

        deferido = False
        urgente = False
        data_encaminhamento = datetime.now()
        # data_finalizado = data_encaminhamento if self.is_concluido_from_post() else None
        data_finalizado = None
        # parecer = self.get_parecer_from_post(data_encaminhamento)
        parecer = ""

        kwargs = {
            "movimentacao_pk": movimentacao.pk,
            "protocolo": protocolo.pk,
            # 'orgao_geral_origem': MovimentacaoManager.get_lotacao_origem(movimentacao).pk,
            "orgao_geral_origem": (
                movimentacao.lotacao_destino.pk
                if movimentacao.lotacao_destino != None
                else movimentacao.lotacao_criacao.pk
            ),
            "servidor_origem": servidor.pk,
            "deferido": deferido,
            "data_encaminhamento": data_encaminhamento,
            "parecer": parecer,
            "urgente": urgente,
            "destinatario": None,
            "data_finalizado": data_finalizado,
        }

        if lotacoes_destino:
            kwargs.update({"lotacoes_destino": lotacoes_destino})
            result_lotacao, message_lotacao = (
                MovimentacaoManager.envia_movimentacao_por_lotacao(kwargs)
            )
        # if servidor_lotacoes:
        #     kwargs.update({'servidor_lotacao_destino': servidor_lotacoes})
        #     result_pessoa, message_pessoa = MovimentacaoManager.envia_movimentacao_por_pessoa(kwargs)

        if (result_lotacao is False) and (result_pessoa is False):
            raise Exception(message_lotacao + message_pessoa)
        else:
            MovimentacaoManager.envia_finalizado_interessado(kwargs)

        # if not ProtocoloManager.set_anexo(self.get_anexos_from_post(), movimentacao):
        #     raise Exception(u'Anexos não incluídos! Tente novamente!')

        # if not ProtocoloManager.set_referencia(self.get_referencias_from_post(), protocolo):
        #     raise Exception(u'Referências não incluídas! Tente novamente!')

        protocolo.deferido = deferido
        protocolo.save()

        print(protocolo, protocolo.pk)

        self.show()


class MovimentacaoTestCase(unittest.TestCase):

    def test_child_of(self):
        print("\n")
        # protocols = Protocolo.objects.filter(
        #     created_at__gte=datetime(2015, 8, 1)).filter(Q(processo=None) | Q(com_workflow=True))
        # print(protocols.count())
        # for protocol in protocols:
        #     if protocol.movimentacoes.count() > 4:
        #         break
        # print protocol
        # protocol = Protocolo.objects.latest('pk')
        protocol = Protocolo.objects.get(codigo="07010110377201591")
        # Protocolo.objects.filter(codigo='07010001430201059').update(data_finalizado=None)
        print("PROTOCOLO")
        print(
            protocol,
            " - CLOSED: ",
            protocol.data_finalizado,
            protocol.modified_by,
            protocol.modified_at,
        )
        print("\nMOVIMENTACAÇÕES")
        for move in protocol.movimentacoes.filter(Q(derivative_for=None)).order_by(
            "passo"
        ):
            print(
                move.pk,
                move.protocolo.codigo,
                " - CLOSED: ",
                move.data_finalizado,
                " - PASSO:",
                move.passo,
                " - CHILDS:",
                move.has_child,
                " - ENVIADO POR:",
                move.servidor_origem,
                " -- ENVIADO PARA:",
                str(move.lotacao_destino or move.destinatario),
            )
        print("\nMOVIMENTACAÇÕES")
        for move in protocol.movimentacoes.filter().order_by("passo"):
            print(
                move.pk,
                move.protocolo.codigo,
                " - CLOSED: ",
                move.data_finalizado,
                " - PASSO:",
                move.passo,
                move.child_of.passo if move.child_of else "no father",
                "CHILDS:",
                move.has_child,
                " - ENVIADO POR:",
                move.servidor_origem,
                " -- ENVIADO PARA:",
                str(move.lotacao_destino or move.destinatario),
            )
            # print move.child_of.derivative_for.filter().count() if move.child_of else 'no father'
            print("-----------------------------------------")
        print(protocol.do_close())

    def test_undo(self):
        print("\n")
        # protocols = Protocolo.objects.filter(
        #     created_at__gte=datetime(2015, 8, 1)).filter(Q(processo=None) | Q(com_workflow=True))
        # print(protocols.count())
        # for protocol in protocols:
        #     if protocol.movimentacoes.count() > 4:
        #         break
        # print protocol
        # protocol = Protocolo.objects.latest('pk')
        protocol = Protocolo.objects.get(codigo="07010123888201653")
        # Protocolo.objects.filter(codigo='07010001430201059').update(data_finalizado=None)
        log.debug("PROTOCOLO")
        log.debug(
            "%s  - CLOSED:  %s %s %s "
            % (
                protocol,
                protocol.data_finalizado,
                protocol.modified_by,
                protocol.modified_at,
            )
        )
        log.debug("\nMOVIMENTACAÇÕES")
        for move in protocol.movimentacoes.filter().order_by("passo"):
            log.debug(
                "%s %s  - CLOSED:  %s  - PASSO: %s - CHILDS: %s - RECEBIDO: %s  - ENVIADO POR: %s  -- ENVIADO PARA: %s "
                % (
                    move.pk,
                    move.protocolo.codigo,
                    move.data_finalizado,
                    move.passo,
                    move.has_child,
                    move.data_recebimento,
                    move.servidor_origem,
                    str(move.lotacao_destino or move.destinatario),
                )
            )
            try:
                move.undo()
            except Exception as err:
                log.debug(str(err))
            log.debug("----------------------------------------")


# tester edocs.protocolo.tests -t MovimentacaoTestCase
# tester edocs.protocolo.tests -t EdocsTestCase
# tester edocs.protocolo.tests -t EdocsTestCase; tester edocs.protocolo.tests -t MovimentacaoTestCase;

# -na caixa principal não aparecerá a movimentação finalizada
# -na caixa finalizado mostrar por padrão as movimentações não recebidas, e adicionar filtro para mostrar todas movimentações


class BoxTestCase(unittest.TestCase):

    def inbox_queryset(klass):
        # from edocs.protocolo.utils import EDOCBoxQuery

        # inbox = None

        # employee = employee_from_user(get_current_user())
        # box_params = {
        #     'servidor': employee,
        #     'lotacoes': employee.work_locations,
        # }

        # if employee.work_locations.filter(acesso_protocolo_geral=True).exists():
        #     box_params.update(
        #         lotacoes_protocolo_geral=employee.work_locations.filter(acesso_protocolo_geral=True)
        #     )

        # box = EDOCBoxQuery(**box_params)

        # return box.get_caixa_entrada().exclude(box.get_role_exclude()).filter(
        #     protocolo__processo=None
        # ).filter(
        #     data_finalizado=None,
        #     protocolo__data_finalizado=None
        # ).order_by('-data_encaminhamento')

        # return inbox
        pass

    def test_inbox_person_refactoring(self):
        pass

    def test_outbox_queryset_refactoring(self):
        # original = Movimentacao.objects.filter(self.get_regra_caixa_saida_refactoring_original())
        # refactoring = Movimentacao.objects.filter(self.get_regra_caixa_saida())
        # log.debug('original %s' % original.count())
        # log.debug('refactoring %s' % refactoring.count())
        # for new in refactoring.exclude(pk__in=original.values('pk')):
        #     log.debug(unicode(new))
        #     log.debug(new.protocolo.sigiloso)

        for employee in Servidor.objects.filter(
            ativo=True,
            # matricula=22999,
        ):
            box_params = {
                "servidor": employee,
                "lotacoes": employee.work_locations,
            }

            if employee.work_locations.filter(acesso_protocolo_geral=True).exists():
                box_params.update(
                    lotacoes_protocolo_geral=employee.work_locations.filter(
                        acesso_protocolo_geral=True
                    )
                )

            box = EDOCBoxQuery(**box_params)

            refactoring = (
                box.get_caixa_saida()
                .exclude(box.get_role_exclude())
                .filter(protocolo__processo=None)
            )
            original = (
                box.get_caixa_saida_refactoring_original()
                .exclude(box.get_role_exclude())
                .filter(protocolo__processo=None)
            )
            # print('')
            # print('original %s' % original.count())
            # print('refactoring %s' % refactoring.count())

            qsigiloso = Q(protocolo__sigiloso=True)
            qnao_sigiloso = ~qsigiloso

            qlotacao_destino_none = Q(lotacao_destino=None)
            qlotacao_destino_nao_none = ~qlotacao_destino_none
            qdestinatario_none = Q(destinatario=None)
            qdestinatario_nao_none = ~qdestinatario_none
            qlotacao_origem = Q(lotacao_origem__in=employee.work_locations)
            qservidor_destino_none = Q(lotacao_destino=None)
            qservidor_destino_nao_none = ~qservidor_destino_none
            qlotacao_origem_lotacao_destino_nao_none = (
                qlotacao_origem & qlotacao_destino_nao_none
            )
            qlotacao_origem_servidor_destino_nao_none = Q(
                qlotacao_origem & qservidor_destino_nao_none
            ) | Q(qlotacao_origem & qdestinatario_nao_none)
            qdepartamento = Q(
                qlotacao_origem_servidor_destino_nao_none
                | qlotacao_origem_lotacao_destino_nao_none
            )

            # print(refactoring.exclude(pk__in=original.values('pk')).exclude(qdepartamento).count())
            print(employee)
            assert (
                not refactoring.exclude(pk__in=original.values("pk"))
                .exclude(qdepartamento)
                .exists()
            )

            # for new in refactoring.exclude(pk__in=original.values('pk')):
            #     print(unicode(new))
            #     print(new.protocolo.sigiloso)

    def test_closedbox_refactoring(self):
        pass


class EDOCDetailTestCase(unittest.TestCase):

    def test(self):
        from edocs.protocolo.task.reports import edoc_detail
        from engine.mq.models import Task

        # count_greater = 0
        # for workplace in Lotacao.objects.filter(organograma=True):
        #     for exercise in workplace.employee_exercise:
        #         user = user_from_person(exercise.servidor.pessoa_fisica)
        #         if user and employee_from_user(user):
        #             set_current_user(user)
        #             # workplace_origin = workplace.pk
        #             workplace_origin = None
        #             # workplace_destination = None
        #             workplace_destination = workplace.pk

        #             protocol_pks = []
        #             inbox = Movimentacao.inbox_queryset()
        #             outbox = Movimentacao.outbox_queryset()
        #             closedbox = Movimentacao.closedbox_queryset()

        #             if workplace_origin:
        #                 protocol_pks += [pk[0] for pk in inbox.filter(lotacao_origem=workplace_origin).values_list('protocolo__pk')]
        #                 protocol_pks += [pk[0] for pk in outbox.filter(lotacao_origem=workplace_origin).values_list('protocolo__pk')]
        #                 protocol_pks += [pk[0] for pk in closedbox.filter(lotacao_origem=workplace_origin).values_list('protocolo__pk')]

        #             if workplace_destination:
        #                 protocol_pks += [pk[0] for pk in inbox.filter(lotacao_destino=workplace_destination).values_list('protocolo__pk')]
        #                 protocol_pks += [pk[0] for pk in outbox.filter(lotacao_destino=workplace_destination).values_list('protocolo__pk')]
        #                 protocol_pks += [pk[0] for pk in closedbox.filter(lotacao_destino=workplace_destination).values_list('protocolo__pk')]

        #             qname = Q(protocolo__pk__in=protocol_pks)

        #             query = Movimentacao.objects.filter(qname).exclude(passo=0)
        #             query = query.filter(~Q(protocolo__data_finalizado=None))
        #             if count_greater < query.count():
        #                 workplace_greater, user_greater, count_greater = workplace, user, query.count()
        # print(u'%s - %s - total %s' % (workplace_greater, user_greater, count_greater))

        # set_current_user('franciscosantos')
        set_current_user("marcossilva")

        Movimentacao.edoc_detail(
            task=None,
            workplace_origin=None,
            workplace_destination=580,
            edoc_code=None,
            date_created=None,
            date_start=None,
            date_end=None,
            finalized=None,
            filename="edoc_detail_%s.csv" % 1,
            subject=None,
            user=get_current_user(),
            # feedback=feedback
        )


class EDOCBoxTestCase(unittest.TestCase):

    @classmethod
    def inbox_queryset(cls, employee):
        if not employee:
            return Movimentacao.objects.none()

        work_locations_effective_exercise = employee.work_locations_effective_exercise

        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk")
                for row in employee.work_locations_effective_exercise.values("pk")
            ],
        }

        if work_locations_effective_exercise.filter(
            acesso_protocolo_geral=True
        ).exists():
            box_params.update(
                lotacoes_protocolo_geral=work_locations_effective_exercise.filter(
                    acesso_protocolo_geral=True
                )
            )

        box = EDOCBoxQuery(**box_params)

        return (
            box.get_caixa_entrada()
            .filter(data_finalizado=None, protocolo__data_finalizado=None)
            .order_by("-data_encaminhamento")
        )

    @classmethod
    def outbox_queryset(cls, employee):

        work_locations_effective_exercise = employee.work_locations_effective_exercise

        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk")
                for row in employee.work_locations_effective_exercise.values("pk")
            ],
        }

        if work_locations_effective_exercise.filter(
            acesso_protocolo_geral=True
        ).exists():
            box_params.update(
                lotacoes_protocolo_geral=work_locations_effective_exercise.filter(
                    acesso_protocolo_geral=True
                )
            )

        box = EDOCBoxQuery(**box_params)

        return (
            box.get_caixa_saida()
            .filter(protocolo__processo=None)
            .order_by("-data_encaminhamento")
        )

    @classmethod
    def closedbox_queryset(cls, employee):
        work_locations_effective_exercise = employee.work_locations_effective_exercise
        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk")
                for row in employee.work_locations_effective_exercise.values("pk")
            ],
        }

        if work_locations_effective_exercise.filter(
            acesso_protocolo_geral=True
        ).exists():
            box_params.update(
                lotacoes_protocolo_geral=work_locations_effective_exercise.filter(
                    acesso_protocolo_geral=True
                )
            )

        box = EDOCBoxQuery(**box_params)
        return (
            box.get_caixa_entrada()
            .filter(protocolo__processo=None)
            .exclude(data_finalizado=None, protocolo__data_finalizado=None)
            .order_by("-data_encaminhamento")
        )

    @classmethod
    def get_qdepartamento_entrada(cls, lotacoes):
        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso
        qservidor_destino_none = Q(servidor_destino=None)
        qdestino_none = Q(lotacao_destino=None)
        qdestinatario_none = Q(destinatario=None)
        qlotacao_origem = Q(lotacao_origem__in=lotacoes)
        qdestino_destinatario_none_e_lotacao_origem = Q(
            qdestino_none
            & qdestinatario_none
            & qlotacao_origem
            & qservidor_destino_none
        )
        qlotacao_destino = Q(lotacao_destino__in=lotacoes)
        qdestino_not_none_qdestinatario_none_qlotacao_destino = (
            qdestinatario_none & qlotacao_destino
        )
        qdepartamento = qnao_sigiloso & Q(
            qdestino_destinatario_none_e_lotacao_origem
            | qdestino_not_none_qdestinatario_none_qlotacao_destino
        )
        qdepartamento = qdepartamento | Q(
            Q(qsigiloso & qdestinatario_none)
            & Q(
                qdestino_destinatario_none_e_lotacao_origem
                | qdestino_not_none_qdestinatario_none_qlotacao_destino
            )
        )
        return qdepartamento

    @classmethod
    def get_qgeral_entrada(cls, protocolo_geral):
        qsigiloso = Q(protocolo__sigiloso=True)
        qnao_sigiloso = ~qsigiloso
        qlotacao_criacao = Q(lotacao_criacao__in=protocolo_geral)
        qlotacao_destino_none_lotacao_criacao = (
            Q(lotacao_destino=None) & qlotacao_criacao
        )
        qlotacao_criacao_none_lotacao_destino = Q(
            lotacao_criacao=None, lotacao_destino__in=protocolo_geral, destinatario=None
        )
        qgeral = qnao_sigiloso & Q(
            qlotacao_criacao
            | qlotacao_destino_none_lotacao_criacao
            | qlotacao_criacao_none_lotacao_destino
        )
        return qgeral

    @classmethod
    def get_qpessoal_entrada(cls):
        qservidor_destino = Q(servidor_destino=self.servidor)
        qdestinatario = Q(destinatario=self.servidor.pessoa_fisica)
        qpessoal = qdestinatario | qservidor_destino
        return qpessoal

    def test_receive_send_task(self):
        from edocs.protocolo.utils import EDOCBoxQuery
        from edocs.protocolo.task.rh_reference import receive_send
        from engine.mq.models import Task

        set_current_user(User.objects.get(username="vilmaroliveira"))
        print(get_current_user())

        employee = employee_from_user(get_current_user())
        if not employee:
            return Movimentacao.objects.none()

        work_locations_effective_exercise = (
            employee.work_locations_effective_exercise.filter(pk__in=[420])
        )
        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk") for row in work_locations_effective_exercise.values("pk")
            ],
        }

        advice = (
            """ Movimentação realizada em decorrência dos ATOS 125/2018 e 126/2018. """
        )

        params = {}
        params.update(
            physical=False,
            opinion=False,
            urgency=False,
            close=False,
        )
        params = params
        params.update(
            advice=str(advice),
            location_destination=45319,
            references='{"protocolo": "", "observation": ""}',
        )
        print(params)

        # self.get_qdepartamento_entrada() | self.get_qgeral_entrada()
        # box = Movimentacao.inbox_queryset()
        print("box_params")
        print(box_params)
        box = EDOCBoxQuery(**box_params)

        query = box.get_caixa_entrada()
        query = query.filter(
            box.get_qdepartamento_entrada() | box.get_qgeral_entrada()
        ).filter(data_finalizado=None, protocolo__data_finalizado=None)
        count = 0
        total = query.count()
        print("total: %d" % total)

        values = query.values("pk")
        buff = "CÓDIGO\n"
        for move in Movimentacao.objects.filter(pk__in=values).order_by("created_at"):
            # print(move, move.lotacao_destino)
            count += 1
            receive_send.delay(
                User.objects.get(username="vilmaroliveira").pk,
                User.objects.get(username="thaislopes").pk,
                move.pk,
                params.get("physical"),  # physical=
                params.get("opinion"),  # opinion=
                params.get("urgency"),  # urgency=
                params.get("close"),  # close=
                params.get("advice"),  # advice=
                params.get("references"),  # references=
                params.get("location_destination"),  # references=
            )
            # self.receive_send(move, **params_p1)
            b = "%s" % move.protocolo.codigo
            print("PROTOCOLO: %s - %d DE %d" % (b, count, total))
            buff += "%s\n" % b
        print(buff)

        # if move.protocolo.resumo == protocol_p1.resumo:
        #     count += 1
        #     receive_send.delay(
        #         move.pk,
        #         params_p1.get('physical'),  # physical=
        #         params_p1.get('opinion'),  # opinion=
        #         params_p1.get('urgency'),  # urgency=
        #         params_p1.get('close'),  # close=
        #         params_p1.get('advice'),  # advice=
        #         params_p1.get('references')  # references=
        #     )
        #     # self.receive_send(move, **params_p1)
        #     print u'%s - P1: %s' % (move.protocolo.codigo, count)
        # elif move.protocolo.resumo == protocol_p2.resumo:
        #     count += 1
        #     receive_send.delay(
        #         move.pk,
        #         params_p2.get('physical'),  # physical=
        #         params_p2.get('opinion'),  # opinion=
        #         params_p2.get('urgency'),  # urgency=
        #         params_p2.get('close'),  # close=
        #         params_p2.get('advice'),  # advice=
        #         params_p2.get('references')  # references=
        #     )
        #     # self.receive_send(move, **params_p2)
        #     print u'%s - P2: %s' % (move.protocolo.codigo, count)
        print(count)

    @unittest.skip("")
    def test(self):
        # # query = EDOCBoxTestCase.get_qdepartamento_entrada([44161])
        # # print Movimentacao.objects.filter(query).query
        # for employee in Servidor.objects.filter(ativo=True):
        #     print employee
        #     # EDOCBoxTestCase.get_qdepartamento_entrada([458])
        #     print 'EDOCBoxTestCase.inbox_queryset (%s)' % EDOCBoxTestCase.inbox_queryset(employee).count()
        #     print 'EDOCBoxTestCase.outbox_queryset (%s)' % EDOCBoxTestCase.outbox_queryset(employee).count()
        #     print 'EDOCBoxTestCase.closedbox_queryset (%s)' % EDOCBoxTestCase.closedbox_queryset(employee).count()
        #     print '----------------------------------------------'
        set_current_user(User.objects.get(username="sachanoleto"))
        print(get_current_user())

        protocol_p1 = Protocolo.objects.get(codigo="07010202549201811")

        advice_p1 = """Por duplicidade de informações e idêntica composição textual de demandas, a presente denúncia é considerada não apita a prosseguimento.

        Toda via, informamos também a existência de procedimento com esta temática, podendo ser acompanhada sob nº 07010202549201811.



        São os esclarecimentos.



        Ouvidoria

        Ministério Público do Tocantins"""

        protocol_p2 = Protocolo.objects.get(codigo="07010207977201813")

        advice_p2 = """Por duplicidade de informações e idêntica composição textual de demandas, a presente denúncia é considerada não apita a prosseguimento.

        Toda via, informamos também a existência de procedimento com esta temática, podendo ser acompanhada sob nº 07010207977201813.



        São os esclarecimentos.



        Ouvidoria

        Ministério Público do Tocantins"""

        params = {}
        params.update(
            physical=False,
            opinion=False,
            urgency=False,
            close=True,
        )
        params_p1 = params
        params_p1.update(
            advice=str(advice_p1),
            references='{"protocolo": "%s", "observation": ""}' % protocol_p1,
        )
        params_p2 = params
        params_p2.update(
            advice=str(advice_p2),
            references='{"protocolo": "%s", "observation": ""}' % protocol_p2,
        )
        print(params)
        box = Movimentacao.inbox_queryset()
        count = 0
        for move in box.order_by("created_at"):
            if move.protocolo.resumo == protocol_p1.resumo:
                count += 1
                self.receive_send(move, **params_p1)
                print("%s - P1: %s" % (protocol_p1.codigo, count))
            elif move.protocolo.resumo == protocol_p2.resumo:
                count += 1
                self.receive_send(move, **params_p2)
                print("%s - P2: %s" % (protocol_p2.codigo, count))
        print(count)

    def receive_send(self, move, **params):
        try:
            move.sign_received()
        except Exception as err:
            print(str(err))
        try:
            move.do_send(**params)
        except Exception as err:
            print(str(err))
