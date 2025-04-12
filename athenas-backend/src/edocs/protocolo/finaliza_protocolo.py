# -*- coding:utf-8 -*-

import sys
import json
import urllib.parse
from datetime import datetime

from django.db.models import Q
from django.contrib.auth.models import User

# import httplib2

from unicodedata import normalize
from contrib.utils import DateUtils, getLogger
from contrib.middleware import set_current_user
from rh.models import Servidor, PessoaFisica, Lotacao
from edocs.protocolo.utils import EDOCBoxQuery
from edocs.protocolo.models import *

log = getLogger()


class ConcludeProtocol:

    def show_percentage_done(self, index, total, text=""):
        sys.stdout.write(
            "[        %.2f%%  ----- 100.00%%        %s]\n"
            % (float(index) / float(total) * 100, text)
        )
        sys.stdout.flush()

    def receive(self, move, employee):
        try:
            print("RECEIVING:")
            move.sign_received()
            print("__________________OK!")
        except Exception as err:
            print(str(err))

    def conclude(self, move, employee, opinion=None, date_send=None):
        print("CONCLUDING:")
        try:
            move.do_close()
            self.update_child_of(move, date_send)
            self.move_do_close(move, employee, opinion, date_send)
            if not move.protocolo.do_close():
                self.move_do_close_legacy(move, employee, opinion, date_send)
                Protocolo.objects.filter(pk=move.protocolo.pk).update(
                    data_finalizado=date_end
                )
                print("____CLOSE LEGACY____")
        except Exception as err:
            print(str(err))
        print("__________________OK!")

    def move_do_close_legacy(self, move, employee, opinion=None, date_send=None):
        try:
            date_close = datetime.now()
            update = {
                "modified_by": User.objects.get(username="athenas"),
                "modified_at": date_close,
                "data_finalizado": date_close,
            }
            if date_send:
                update.update({"data_encaminhamento": date_send})
            Movimentacao.objects.filter(protocolo=move.protocolo, passo__gt=0).exclude(
                ~Q(data_finalizado=None)
            ).update(**update)
        except Exception as err:
            print(str(err))

    def move_do_close(self, move, employee, opinion=None, date_send=None):
        try:
            date_close = datetime.now()
            update = {
                "modified_by": User.objects.get(username="athenas"),
                "modified_at": date_close,
                "data_finalizado": date_close,
            }
            if date_send:
                update.update({"data_encaminhamento": date_send})
            move.protocolo.movements_termination().update(**update)
        except Exception as err:
            print(str(err))

    def update_child_of(self, move, date_send):
        if date_send:
            Movimentacao.objects.filter(child_of=move).update(
                data_encaminhamento=date_send
            )

    def conclude_all(self):
        print("----------CONCLUDE-ALL----------------")
        for employee in Servidor.objects.filter(ativo=True):
            for workplace in employee.work_locations_effective_exercise:
                moves = EDOCBoxQuery(
                    servidor=employee,
                    lotacoes=[
                        workplace.pk,
                    ],
                    lotacoes_protocolo_geral=[],
                    valor=None,
                ).get_caixa_entrada()
                # moves = moves.exclude(EDOCBoxQuery.get_finalizado_recebido())
                moves = moves.filter(EDOCBoxQuery.get_finalizado())
                moves = moves.filter(protocolo__processo=None)
                moves = moves.filter(with_workflow=False)

                print(
                    "================================================================================"
                )
                print(
                    "Concluindo todas as finalizadas:", moves.count(), " - ", employee
                )
                self.run(moves, employee)

    def receive_all(self, employee=None, opinion=None):
        print("----------RECEIVE-ALL----------------")
        for employee in Servidor.objects.filter(ativo=True):
            for workplace in employee.work_locations_effective_exercise:
                moves = EDOCBoxQuery(
                    servidor=employee,
                    lotacoes=[
                        workplace.pk,
                    ],
                    lotacoes_protocolo_geral=[],
                    valor=None,
                ).get_caixa_entrada()
                moves = moves.exclude(EDOCBoxQuery.get_finalizado_recebido())
                moves = moves.filter(protocolo__processo=None)
                moves = moves.filter(with_workflow=False)

                print(
                    "================================================================================"
                )
                print(
                    "Receber todas as movimentacações:", moves.count(), " - ", employee
                )
                self.run(moves, employee, conclude=False)

    def receive_all_from_employee(
        self,
        workplace=[],
        workplace_general_protocol=[],
        employee=None,
        opinion=None,
        date_end=None,
        date_send=None,
    ):
        date_end = datetime.now() if not date_end else date_end
        print("----------RECEIVE-ALL-FROM-EMPLOYEE----------------")
        moves = EDOCBoxQuery(
            servidor=employee,
            lotacoes=workplace,
            lotacoes_protocolo_geral=workplace_general_protocol,
            valor=None,
        ).get_caixa_entrada()
        moves = moves.exclude(EDOCBoxQuery.get_finalizado_recebido())
        moves = moves.filter(protocolo__processo=None)
        moves = moves.filter(with_workflow=False)
        moves = moves.filter(protocolo__data_criacao__lte=date_end)

        print(
            "================================================================================"
        )
        print("Receber todas as movimentacações:", moves.count(), " - ", employee)
        self.run(moves, employee, conclude=False, date_send=date_send)

    def conclude_from_employee_workplace(
        self,
        workplace=[],
        workplace_general_protocol=[],
        employee=None,
        opinion=None,
        date_end=None,
        date_send=None,
    ):
        print("----------CONCLUDE-FROM-EMPLOYEE-WORKPLACE----------------")
        if not employee:
            raise Exception("Employee not provided")

        date_end = datetime.now() if not date_end else date_end
        set_current_user(employee.user)

        moves = EDOCBoxQuery(
            servidor=employee,
            lotacoes=workplace_general_protocol + workplace,
            lotacoes_protocolo_geral=workplace,
            valor=None,
        ).get_caixa_entrada()
        moves = moves.exclude(EDOCBoxQuery.get_finalizado_recebido())
        moves = moves.filter(protocolo__processo=None)
        moves = moves.filter(with_workflow=False)
        moves = moves.filter(protocolo__data_criacao__lte=date_end)
        print(
            "================================================================================"
        )
        print(
            "Finalizando os protocolos da(s) lotação(ões):",
            [
                str(lot)
                for lot in Lotacao.objects.filter(
                    pk__in=workplace_general_protocol + workplace
                )
            ],
            " - total:",
            moves.count(),
            " - ",
            employee,
        )
        self.run(moves, employee, opinion=opinion, date_send=date_send)

    def conclude_from_workplace(
        self,
        workplace=[],
        workplace_general_protocol=[],
        employee=None,
        opinion=None,
        date_end=None,
        date_send=None,
    ):
        print("----------CONCLUDE-FROM-WORKPLACE----------------")
        if not employee:
            raise Exception("Employee not provided")

        date_end = datetime.now() if not date_end else date_end
        set_current_user(employee.user)

        moves = EDOCBoxQuery(
            servidor=employee,
            lotacoes=workplace_general_protocol + workplace,
            lotacoes_protocolo_geral=workplace,
            valor=None,
        ).get_caixa_entrada()
        moves = moves.exclude(EDOCBoxQuery.get_finalizado_recebido())
        moves = moves.filter(protocolo__processo=None)
        moves = moves.filter(with_workflow=False)
        moves = moves.filter(protocolo__data_criacao__lte=date_end)
        print(
            "================================================================================"
        )
        print(
            "Finalizando os protocolos da(s) lotação(ões):",
            [
                str(lot)
                for lot in Lotacao.objects.filter(
                    pk__in=workplace_general_protocol + workplace
                )
            ],
            " - total:",
            moves.count(),
            " - ",
            employee,
        )
        self.run(moves, employee, opinion=opinion, date_send=date_send)

    def run(
        self, moves, employee, receive=True, conclude=True, opinion=None, date_send=None
    ):
        count = 1
        total = moves.count()
        for move in moves:
            print("")
            print(
                "MOVE PK: ",
                move.pk,
                " - CODE:",
                move.protocolo.codigo,
                " - TOTAL",
                total,
                "-->",
                count,
            )
            self.show_percentage_done(count, total)
            count += 1
            if receive:
                self.receive(move, employee)
            if conclude:
                self.conclude(move, employee, opinion, date_send)
        print("TOTAL realizado:", total)


# print '----------EDOC-FINALIZANDO-MOVIMENTAÇÕES----------------'
# lotacao = 554
# servidor = User.objects.get(username='mariamascarenhas').servidor.get()
# data_inicio = datetime(2010, 1, 1)
# data_fim = datetime(2011, 12, 31)
# print u'Finalizar protocolos do período com início em %s até %s.\nUtilizando o servidor %s e lotação %s' % (
#   DateUtils.date_to_str(data_inicio), DateUtils.date_to_str(data_fim), servidor, lotacao
# )
# instance = FinalizaProtocolo(data_inicio, data_fim, lotacao, servidor=servidor)
# print instance.finaliza_protocolo_em_serie(instance.caixa.get_caixa_entrada().filter(
#     data_finalizado=None,
#     protocolo__data_criacao__gte=data_inicio,
#     protocolo__data_criacao__lte=data_fim).order_by('-passo')
# )
# lotacao = 554
# servidor = User.objects.get(username='mariamascarenhas').servidor.get()
# data_inicio = datetime(2009, 1, 1)
# data_fim = datetime(2013, 12, 31)
# instance = FinalizaProtocolo(data_inicio, data_fim, lotacao, servidor=servidor)
# print instance.recebe_protocolos(instance.get_movimentacao_finalizada_nao_recebida())

# print '--------------------------'
# data_inicio = datetime(2012, 1, 1)
# data_fim = datetime(2012, 12, 31)
# print u'Finalizar protocolos do período com início em %s até %s.\nUtilizando o servidor %s e lotação %s' % (
#   DateUtils.date_to_str(data_inicio), DateUtils.date_to_str(data_fim), servidor, lotacao
# )
# instance = FinalizaProtocolo(data_inicio, data_fim,   lotacao, servidor=servidor)
# print instance.finaliza_protocolo_em_serie(instance.caixa.get_caixa_entrada().filter(
#     data_finalizado=None,
#     protocolo__tipo_documento__pk=11,
#     protocolo__data_criacao__gte=data_inicio,
#     protocolo__data_criacao__lte=data_fim).order_by('-passo')
# )


#####SÓ REALIZAR COM ORDEM EXPRESSA
# print '--------------------------'
# lotacao = None
# servidor = User.objects.get(username='athenas').servidor.get()
# data_inicio = datetime(2009, 1, 1)
# data_fim = datetime(2013, 12, 31)
# print u'Finalizar protocolos do período com início em %s até %s.\nUtilizando o servidor %s e lotação %s' % (
#   DateUtils.date_to_str(data_inicio), DateUtils.date_to_str(data_fim), servidor, lotacao
# )
# instance = FinalizaProtocolo(data_inicio, data_fim, lotacao, servidor=servidor)
# print instance.recebe_protocolos(instance.get_movimentacao_finalizada_nao_recebida())


class FinalizaProtocolo:

    url = "http://localhost:8080"

    def __init__(
        self,
        data_inicio=datetime.now(),
        data_fim=datetime.now(),
        lotacao=None,
        movimentacao=[],
        servidor=None,
    ):
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.lotacao = lotacao
        self.movimentacao = movimentacao
        self.servidor = servidor
        self.http = httplib2.Http()
        self.url_receber = "%s/athenas/EDOCBox/receber/" % self.url
        self.url_desfazer_envio = "%s/athenas/EDOCBox/desfazer_envio/" % self.url
        self.url_finalizar = "%s/athenas/EDOCBox/finalizar/" % self.url
        self.url_session_information = (
            "%s/athenas/Application/get_session_information" % self.url
        )
        self.url_login = "%s/athenas/ExtLogin/connect/" % self.url
        # self.caixa = EDOCBoxQuery(
        #     servidor=self.get_servidor(),
        #     lotacoes=[self.lotacao],
        #     lotacoes_protocolo_geral=self.get_lotacoes_servidor_protocolo_geral(),
        #     valor=None
        # )
        # self.login()

    @staticmethod
    def set_user_ativo(user):
        """
        Este método marca o usuário do athenas como ativo para login.
        """
        User.objects.filter(pk=user).update(is_active=True)

    @staticmethod
    def get_user():
        """
        Este método retorna o usuário athenas.
        """
        try:
            user = User.objects.get(username="athenas")
        except:
            user = User(username="athenas")
            user.save()
        user.set_password("athenas")
        return user

    @staticmethod
    def get_pessoa_fisica():
        """
        Este método retorna a pessoa física athenas.
        """
        try:
            pessoa_fisica = PessoaFisica.objects.get(nome="athenas")
        except:
            pessoa_fisica = PessoaFisica(nome="athenas")
            pessoa_fisica.save()
        return pessoa_fisica

    def get_servidor_pk(self):
        """
        Este método retorna a pk do servidor.
        """
        return self.get_servidor().pk

    def get_servidor(self):
        """
        Este método retorna a instância do servidor.
        """
        if not self.servidor:
            try:
                self.servidor = Servidor.objects.get(
                    matricula=0, pessoa_fisica__nome="athenas"
                )
            except:
                user = self.get_user()
                servidor = Servidor()
                servidor.pessoa_fisica = self.get_pessoa_fisica()
                servidor.user = user
                servidor.matricula = 00000
                servidor.matricula_origem = "athenas"
                servidor.save()
                self.servidor = servidor
        return self.servidor

    def get_lotacoes_servidor_protocolo_geral(self):
        """
        Este método retorna a relação dos pks das lotações/designações (protocolo_geral) que o servidor logado possui.
        @return list - lotações/designações, caso não existe retorna [].
        """
        try:
            if not self.lotacoes_protocolo_geral:
                self.lotacoes_protocolo_geral = [
                    workplace.pk if workplace.acesso_protocolo_geral else None
                    for workplace in self.get_servidor().work_locations_effective_exercise
                ]
        except:
            return []
        return self.lotacoes_protocolo_geral

    def login(self):
        """
        Este método realiza o login do usuário athenas.
        """
        body = {
            "login": self.get_servidor().user.username,
            "passwd": self.get_servidor().user.password,
            "theme": 0,
        }
        #        body = {'login': self.get_servidor().user.username, 'passwd': '123', 'theme':0}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        response, content = self.http.request(
            self.url_login, "POST", headers=headers, body=urllib.parse.urlencode(body)
        )
        self.headers = {"Cookie": response["set-cookie"]}
        if json.loads(content)["success"] == False:
            print("Login não funcionou!!!")
        response, content = self.http.request(
            self.url_session_information, "GET", headers=self.headers
        )
        if json.loads(content)["is_auth"] == False:
            print("Login não funcionou!!!")
        else:
            print("Login sucesso!!!")
            return True
        return False

    def receber(self, pars):
        response, content = self.http.request(
            self.url_receber,
            "POST",
            headers=self.headers,
            body=urllib.parse.urlencode(
                {"movimentacao": pars["movimentacao"], "servidor": pars["servidor"]}
            ),
        )
        if json.loads(content)["success"] == False:
            # print content
            return False
        return True

    def finalizar(self, pars):
        response, content = self.http.request(
            self.url_finalizar,
            "POST",
            headers=self.headers,
            body=urllib.parse.urlencode(pars),
        )
        if json.loads(content)["success"] == False:
            valor = normalize("NFKD", json.loads(content)["msg"]).encode(
                "ascii", "ignore"
            )
            try:
                if valor.index("de finalizar e necessario receber!"):
                    m = Movimentacao.objects.get(pk=pars["movimentacao"])
                    if m.data_recebimento is None:
                        Movimentacao.objects.filter(pk=pars["movimentacao"]).update(
                            data_recebimento=datetime.now()
                        )
                    if m.servidor_destino is None:
                        Movimentacao.objects.filter(pk=pars["movimentacao"]).update(
                            servidor_destino=Servidor.objects.get(
                                matricula=0, pessoa_fisica__nome="athenas"
                            )
                        )
                    response, content = self.http.request(
                        self.url_finalizar,
                        "POST",
                        headers=self.headers,
                        body=urllib.parse.urlencode(pars),
                    )
                    if json.loads(content)["success"] == False:
                        # print content
                        return False
                if valor.index("movimentacao ja foi encaminhada!"):
                    return False
            except:
                print(content)
                return False
        return True

    def get_protocolo_para_finalizar(self, movimentacao=[]):
        for m in movimentacao:
            if not m.protocolo.pk in prot:
                parametro.append(
                    {
                        "concluir": "on",
                        "movimentacao": m.pk,
                        "protocolo": m.protocolo.codigo,
                        "servidor": self.get_servidor_pk(),
                        "recebido": True if m.data_recebimento else False,
                    }
                )
                prot.append(m.protocolo.pk)
        return parametro

    def get_protocolo_para_receber_nao_recebidos(self):
        """ """
        parametro = []
        movimentacao = Movimentacao.objects.filter(
            Q(protocolo__data_criacao__gte=self.data_inicio)
            & Q(protocolo__data_criacao__lte=self.data_fim)
            & ~Q(data_finalizado=None)
            & Q(Q(data_recebimento=None) | Q(servidor_destino=None))
        ).order_by("-data_encaminhamento")
        for m in movimentacao:
            parametro.append(
                {
                    "concluir": "on",
                    "movimentacao": m.pk,
                    "protocolo": m.protocolo.codigo,
                    "servidor": self.get_servidor_pk(),
                    "recebido": True if m.data_recebimento else False,
                }
            )
        return parametro

    def get_movimentacao_finalizada_nao_recebida(self):
        """
        Este método retorna todos os protocolos finalizados que não foram recebidos.
        """
        parametro = []
        movimentacao = Movimentacao.objects.filter(
            Q(protocolo__data_criacao__gte=self.data_inicio)
            & Q(protocolo__data_criacao__lte=self.data_fim)
            & ~Q(data_finalizado=None)
            & Q(Q(data_recebimento=None) | Q(servidor_destino=None))
        ).order_by("-data_encaminhamento")
        if self.lotacao:
            movimentacao = movimentacao.filter(
                Q(lotacao_criacao__pk=self.lotacao)
                | Q(destinatario__pk=self.get_servidor().pessoa_fisica.pk)
            )
        for m in movimentacao:
            parametro.append(
                {
                    "concluir": "on",
                    "movimentacao": m.pk,
                    "protocolo": m.protocolo.codigo,
                    "servidor": self.get_servidor_pk(),
                    "recebido": True if m.data_recebimento else False,
                }
            )
        return parametro

    def finaliza_protocolo_em_serie(self, movimentacoes=[]):
        """
        Este método finaliza os protocolos e movimentações baseado na data de início e fim.
        Porém, pode receber diretamente as movimentações(pks) que devem ser finalizadas.
        """
        count = 0
        err = []

        quantidade_movimentacoes_caixa_entrada = self.caixa.get_caixa_entrada()
        quantidade_movimentacoes_caixa_saida = self.caixa.get_caixa_saida()

        parametro = []
        prot = []
        for m in movimentacoes:
            if not m.protocolo.pk in prot:
                parametro.append(
                    {
                        "concluir": "on",
                        "movimentacao": m.pk,
                        "protocolo": m.protocolo.codigo,
                        "servidor": self.get_servidor_pk(),
                        "recebido": True if m.data_recebimento else False,
                    }
                )
                prot.append(m.protocolo.pk)

        print(
            """
            Implementação para finalizar protocolos pendentes entre %s e %s.
            O primeiro passo é receber todos protocolos para que eles possam ser enviados.
        """
            % (
                DateUtils.date_to_str(self.data_inicio),
                DateUtils.date_to_str(self.data_fim),
            )
        )
        if len(parametro) > 0:
            self.recebe_movimentacao_nao_finalizada(parametro)
        print("%s protocolos devem ser finalizados..." % len(parametro))
        for pars in parametro:
            try:
                p = {
                    "concluir": "on",
                    "movimentacao": pars["movimentacao"],
                    "protocolo": pars["protocolo"],
                    "servidor": pars["servidor"],
                }
                if not self.finalizar(p):
                    err.append(["Protocolo não finalizado!", p])
                else:
                    count += 1
                    # print count
            except Exception as e:
                err.append(["Protocolo não finalizado!", p])
                print(e)
        if len(err):
            print("erros")
            print(err)

        try:
            print(
                "Caixa de entrada: \n\r -ANTES de finalizar %s \n\r -DEPOIS de finalizar %s"
                % (
                    quantidade_movimentacoes_caixa_entrada.count(),
                    self.caixa.get_caixa_entrada().count(),
                )
            )
            print(
                "Caixa de saida: \n\r -ANTES de finalizar %s \n\r -DEPOIS de finalizar %s"
                % (
                    quantidade_movimentacoes_caixa_saida.count(),
                    self.caixa.get_caixa_saida().count(),
                )
            )
        except Exception as e:
            log.exception(e)

    def recebe_movimentacao_nao_finalizada(self, parametro=None):
        count = 0
        err = []
        print("%s protocolos devem ser recebidos..." % len(parametro))
        for pars in parametro:
            try:
                if pars["recebido"] is False:
                    p = {
                        "concluir": "on",
                        "movimentacao": pars["movimentacao"],
                        "protocolo": pars["protocolo"],
                        "servidor": pars["servidor"],
                    }
                    if not self.receber(p):
                        err.append(["Protocolo não recebido!", p])
                    else:
                        count += 1
                        # print count
                else:
                    print("Já foi recebido!")
            except Exception as e:
                err.append(["Protocolo não recebido!", p])
                print(e)
        if len(err):
            print("erros")
            print(err)
        print("Total %s e %s foram recebidos!" % (len(parametro), count))

    def recebe_protocolos(self, parametro=None):
        count = 0
        err = []
        parametro = (
            self.get_protocolo_para_receber_nao_recebidos()
            if not parametro
            else parametro
        )
        print("%s protocolos devem ser recebidos..." % len(parametro))
        for pars in parametro:
            try:
                if pars["recebido"] is False:
                    p = {
                        "concluir": "on",
                        "movimentacao": pars["movimentacao"],
                        "protocolo": pars["protocolo"],
                        "servidor": pars["servidor"],
                    }
                    if not self.receber(p):
                        err.append(["Protocolo não recebido!", p])
                    else:
                        count += 1
                        # print count
                else:
                    print("Já foi recebido!")
            except Exception as e:
                err.append(["Protocolo não recebido!", p])
                print(e)
        if len(err):
            print("erros")
            print(err)
        print("Total %s e %s foram recebidos!" % (len(parametro), count))

    def desfazer_envio_finalizados_por_lotacao(self):
        """
        Este método desfaz a finalização de documentos.
        """
        prot = []
        movimentacao = Movimentacao.objects.filter(
            ~Q(protocolo__data_finalizado=None)
            & Q(lotacao_origem__pk=self.lotacao)
            & ~Q(data_recebimento=None)
            & Q(servidor_destino=self.get_servidor())
            & Q(servidor_origem=self.get_servidor())
        ).order_by("-passo")
        count = 0
        count_realizado = 0
        print(
            "Desfazendo envio de protocolos finalizados apenas para a lotação %s"
            % Lotacao.objects.get(pk=self.lotacao)
        )
        for m in movimentacao:
            if not m.protocolo.pk in prot:
                count += 1
                prot.append(m.protocolo.pk)
                Movimentacao.objects.filter(pk=m.pk).update(
                    data_recebimento=None, servidor_destino=None
                )
                Protocolo.objects.filter(pk=m.protocolo.pk).update(data_finalizado=None)
                realizado = self.desfazer_envio(m.pk)
                # print u'Tetando desfazer envio de %s... %s' % (m.pk, u'realizado com sucesso!' if realizado else u'não realizado!')
                if realizado:
                    count_realizado += 1
        print(
            "Tentou-se desfazer o envio de %s e realizou-se %s"
            % (count, count_realizado)
        )

    def desfazer_envio_finalizados_por_lotacao_movimentacao(self):
        """
        Este método desfaz a finalização de documentos pela movimentação.
        """
        movimentacao = Movimentacao.objects.get(pk=self.movimentacao)
        count = 0
        count_realizado = 0
        print(
            "Desfazendo envio da movimentação %s do protocolo %s"
            % (movimentacao.pk, movimentacao.protocolo.codigo)
        )
        count += 1
        Movimentacao.objects.filter(pk=movimentacao.pk).update(data_finalizado=None)
        Protocolo.objects.filter(pk=movimentacao.protocolo.pk).update(
            data_finalizado=None
        )
        realizado = self.desfazer_envio(movimentacao.pk)
        if realizado:
            count_realizado += 1
        print(
            "Tentou-se desfazer o envio de %s e realizou-se %s"
            % (count, count_realizado)
        )

    def desfazer_envio(self, movimentacao):
        response, content = self.http.request(
            self.url_desfazer_envio,
            "POST",
            headers=self.headers,
            body=urllib.parse.urlencode({"movimentacao": movimentacao}),
        )
        if json.loads(content)["success"] == False:
            print(content)
            return False
        return True
