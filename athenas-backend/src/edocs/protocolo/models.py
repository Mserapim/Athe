# -.- coding: utf-8 -.-
import codecs
import hashlib
import json
import os
import re
from base64 import b64encode
from datetime import datetime
from importlib import import_module

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.db.models import F, Func, Q
from django.template import loader
from django.utils.cache import caches

from ged.models import Arquivo
from auditoria.models import LineLog
from contrib.decorator import deprecated, to_search
from contrib.middleware import get_current_user, set_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger
from default.websocket import RemoteEmmiter
from rh.models import Localidade, Lotacao, OrgaoGeral, Pessoa, PessoaFisica, Servidor
from standard import models as standard_models
from standard.models import AuditTimestampModel, Choice
from edocs.protocolo.const import MIDIA_ORIGEM


log = getLogger()


def grant_list(x):
    return x if isinstance(x, (list, tuple, set)) else ([x] if x and x != "" else [])


def log_LineLog(level=70, status=2, kwargs=None):
    prepared = {}

    for attr, value in list(kwargs.items()):
        if isinstance(value, models.Model):
            prepared.update({attr: value.pk})
            prepared.update({"%s_unicode" % attr: str(value)})
        else:
            prepared.update({attr: value})

    try:
        linelog = LineLog(level=level)
        linelog.status = status
        linelog.json_description = prepared
        linelog.user = get_current_user()
        linelog.save()
    except Exception as err:
        log.exception(err)
        log.warn("Não realizou auditoria!!!")


# ########################################## MANAGER INÍCIO ############################
class MovimentacaoManager(object):
    """
    Deve-se utilizar o método criar_movimentação para enviar(criar) movimentações
    de um protocolo às pessoas ou departamentos.
    Caso haja necessidade de realizar outras implementações, é obrigatório observar a
    chamada dos métodos:
        atualiza_movimentacao_enviada(movimentacao_pk, data)
    Pois esté método organiza a movimentação de origem.
    Desta forma uma possível imple
    """

    @classmethod
    def criar_movimentacao_sem_envio_interessado(cls, kwargs):
        """
        Este método é responsável por movimentar um Protocolo para n pessoas ou lotações.
        Quando a movimentação for finalizada não envia para o interessado.
        @param movimentacao_pk int - pk da Movimentacao.
        @param Protocolo - protocolo.
        @param OrgaoGeral - orgao_geral_origem, instância da lotação que está enviando.
        @param Lista de OrgaoGeral - orgao_geral_destino, instância da lotação que está recebendo.
        @param Servidor - servidor_origem, servidor que está enviando.
        @param boolean - deferido.
        @param data_encaminhamento - data e hora de encaminhamento.
        @param text - parecer, parecer de envio.
        @param boolean - urgente.
        @param Lista de Pessoa - Destinatario.
        @param data_finalizado - data e hora de finalização.
        """
        if "movimentacao_pk" not in kwargs:
            raise Exception("A pk da movimentação de origem deve ser informada!")
        for lotacao_destino in kwargs.get("orgao_geral_destino", []):
            new_kwargs = kwargs
            new_kwargs.update({"orgao_geral_destino": lotacao_destino})
            Movimentacao.criar_movimentacao(new_kwargs)
        for destinatario in kwargs.get("destinatario", []):
            new_kwargs = kwargs
            new_kwargs.update({"destinatario": destinatario})
            Movimentacao.criar_movimentacao(new_kwargs)
        cls.atualiza_movimentacao_enviada(
            kwargs.get("movimentacao_pk"), kwargs.get("data_finalizado")
        )

    @classmethod
    def criar_movimentacao(cls, kwargs):
        """
        Este método é responsável por movimentar um Protocolo para n pessoas ou lotações.
        Quando a movimentação for finalizada não envia para o interessado.
        @param movimentacao_pk int - pk da Movimentacao.
        @param Protocolo - protocolo.
        @param OrgaoGeral - orgao_geral_origem, instância da lotação que está enviando.
        @param Lista de OrgaoGeral - orgao_geral_destino, instância da lotação que está recebendo.
        @param Servidor - servidor_origem, servidor que está enviando.
        @param boolean - deferido.
        @param data_encaminhamento - data e hora de encaminhamento.
        @param text - parecer, parecer de envio.
        @param boolean - urgente.
        @param Lista de Pessoa - Destinatario.
        @param data_finalizado - data e hora de finalização.
        """
        if "movimentacao_pk" not in kwargs:
            raise Exception("A pk da movimentação de origem deve ser informada!")
        for lotacao_destino in kwargs.get("orgao_geral_destino", []):
            new_kwargs = kwargs
            new_kwargs.update({"orgao_geral_destino": lotacao_destino})
            Movimentacao.criar_movimentacao(new_kwargs)
        for destinatario in kwargs.get("destinatario", []):
            new_kwargs = kwargs
            new_kwargs.update({"destinatario": destinatario})
            Movimentacao.criar_movimentacao(new_kwargs)
        cls.envia_finalizado_interessado(kwargs)
        cls.atualiza_movimentacao_enviada(
            kwargs.get("movimentacao_pk"), kwargs.get("data_finalizado")
        )

    @classmethod
    def envia_movimentacao_por_lotacao(cls, kwargs):
        """
        Este método é responsável por organizar o envio às Lotacoes.
        @param movimentacao_pk(int): Movimentação de origem.
        @param protocolo(Protocolo): Protocolo que está sendo enviado.
        @param orgao_geral_origem(OrgaoGeral): Lotacao de origem.
        @param servidor_origem(Servidor): Servidor de origem.
        @param deferido(boolean): atributo indicando se a movimentação foi deferida(e o Protocolo).
        @param data_encaminhamento(datetime): data do encaminhamento.
        @param parecer(text): parecer da Movimentacao.
        @param urgente(boolean): atributo indicando se é urgente.
        @param lotacoes_destino(list): Lotacoes que devem receber o Protocolo.
        @param data_finalizado(datetime): data da finalização.
        @return dict - {'result': True se não ocorrer problemas, False de outra forma, 'message': '' se não ocorrer problemas, de outra forma
        envia a mensagem do erro}
        """
        result = True
        message = ""
        erros = []
        err = ""
        movimentacao_pk = kwargs.get("movimentacao_pk")
        lotacoes_destino = kwargs.pop("lotacoes_destino", [])
        data_finalizado = kwargs.get("data_finalizado", None)
        try:
            # ENVIO A LOTACOES
            for lot_destino in lotacoes_destino:
                kwargs.update({"orgao_geral_destino": lot_destino})
                try:
                    protocolo = kwargs.get("protocolo")
                    protocolo.my_origin.Movimentacao().criar_movimentacao(kwargs)
                except Exception as e:
                    log.exception(e)
                    erros.append(lot_destino)
            if len(erros) == 0:
                cls.atualiza_movimentacao_enviada(movimentacao_pk, data_finalizado)
            elif len(erros) > 0:
                for l in erros:
                    err += str(OrgaoGeral.objects.get(pk=int(l)))
                raise Exception("Não enviado às lotações: " + err.encode("utf-8"))
        except Exception as err:
            result = False
            message = str(err)
            log.info(message)
        return result, message

    @classmethod
    def envia_movimentacao_por_pessoa(cls, kwargs):
        """
        Este método é responsável por organizar o envio às Pessoas.
        @param movimentacao_pk(int): Movimentação de origem.
        @param protocolo(Protocolo): Protocolo que está sendo enviado.
        @param orgao_geral_origem(OrgaoGeral): Lotacao de origem.
        @param servidor_origem(Servidor): Servidor de origem.
        @param deferido(boolean): atributo indicando se a movimentação foi deferida(e o Protocolo).
        @param data_encaminhamento(datetime): data do encaminhamento.
        @param parecer(text): parecer da Movimentacao.
        @param urgente(boolean): atributo indicando se é urgente.
        @param servidor_lotacao_destino(list): [pk do Servidor, pk da Lotacao].
        @param data_finalizado(datetime): data da finalização.
        @return dict - {'result': True se não ocorrer problemas, False de outra forma, 'message': '' se não ocorrer problemas, de outra forma
        envia a mensagem do erro}
        """
        erros = []
        result = True
        message = ""
        err = ""
        movimentacao_pk = kwargs.get("movimentacao_pk")
        servidor_lotacao_destino = kwargs.pop("servidor_lotacao_destino", [])
        data_finalizado = kwargs.get("data_finalizado", None)
        try:
            # ENVIO A PESSOAS
            pessoas_enviadas = []
            for sl in servidor_lotacao_destino:
                destinatario = sl[0]
                if destinatario not in pessoas_enviadas:
                    kwargs.update({"destinatario": int(destinatario)})
                    kwargs.update({"orgao_geral_destino": int(sl[1])})
                    try:
                        protocolo = kwargs.get("protocolo")
                        protocolo.my_origin.Movimentacao().criar_movimentacao(kwargs)
                    except Exception as e:
                        log.exception(e)
                        erros.append(destinatario)
                    else:
                        pessoas_enviadas.append(destinatario)
            if len(erros) == 0:
                cls.atualiza_movimentacao_enviada(movimentacao_pk, data_finalizado)
            elif len(erros) > 0:
                for l in erros:
                    err += str(Pessoa.objects.get(pk=int(l)))
                raise Exception("Não enviado às pessoas: " + err.encode("utf-8"))
        except Exception as e:
            log.exception(e)
            result = False
            message = str(e)
        return result, message

    @classmethod
    def atualiza_movimentacao_enviada(cls, movimentacao, data_finalizado):
        """
        Este método atualiza movimentação de origem para enviada.
        Também finaliza caso a data de finalização seja preenchida.
        """
        Movimentacao.objects.filter(pk=movimentacao).update(
            encaminhado=True, data_finalizado=data_finalizado
        )

    @classmethod
    def get_movimentacao(cls, pk):
        """
        Este método retorna a Movimentacao referenciada pelo pk.
        @param int - pk da Movimentacao
        @return Movimentacao/None
        """
        if isinstance(pk, list):
            pk = pk[0]
        try:
            return Movimentacao.objects.get(pk=int(pk))
        except Exception:
            return None

    @classmethod
    def is_movimentacao(cls, movimentacao):
        """
        Este método verifica se a movimentação foi encontrado corretamente.
        Apresenta exceção caso a movimentação não seja encontrada.
        """
        if not movimentacao:
            raise Exception("Movimentação não encontrada!")
        return True

    @classmethod
    def is_recebido(cls, movimentacao):
        """
        Este método verifica se a Movimentacao já foi recebida.
        @param Movimentacao - movimentacao.
        @return True caso tenha recebido, de outra forma False
        """
        try:
            if (
                movimentacao.data_recebimento is None
                or movimentacao.servidor_destino is None
            ):
                return False
            return True
        except Exception as e:
            log.exception(e)
        return False

    @classmethod
    def is_servidor_destinatario(cls, servidor, movimentacao):
        """
        Este método verifica se o Servidor é o destinatário da Movimentacao informada.
        @param Servidor - servidor.
        @param Movimentacao - movimentacao.
        @return True se for o destinatário, de outra forma False.
        """
        try:
            if servidor.pessoa_fisica.nome == "athenas" or (
                movimentacao.destinatario
                and movimentacao.destinatario.pk == servidor.pessoa_fisica.pk
            ):
                return True
        except Exception as e:
            log.exception(e)
        return False

    @classmethod
    def envia_finalizado_interessado(cls, kwargs):
        """
        Este método envia para o interessado caso ele possa receber essa finalização.
        As premissas são: -todas as movimentações de "folha" estarem finalizadas;
        -e ele ainda não ter recebido uma movimentação finalizada.
        """
        if ProtocoloManager.is_movimentacoes_finalizadas(
            kwargs.get("protocolo")
        ) and not (
            ProtocoloManager.is_interessado_recebeu_finalizado(
                ProtocoloManager.get_protocolo(kwargs.get("protocolo")),
                kwargs.get("orgao_geral_origem"),
            )
        ):
            kwargs.update(
                {
                    "parecer": "Protocolo finalizado em todas movimentações. Verifique os pareceres do seu protocolo."
                }
            )
            cls.envia_interessado(kwargs)

    @classmethod
    def envia_interessado(cls, kwargs):
        """
        Este método envia para o interessado em qualquer hipótese.
        """
        from contrib.utils import dump_dict

        dump_dict(kwargs)

        protocolo = kwargs.get("protocolo")
        interessado = protocolo.interessado
        mov = cls.get_movimentacao(kwargs.get("movimentacao_pk"))
        kwargs.update({"orgao_geral_destino": int(protocolo.orgao_geral_origem.pk)})
        if (
            protocolo.lotacao_criacao
            and protocolo.lotacao_criacao.lotacao.ouvidoria
            and not kwargs.get("parecer", None)
        ):
            kwargs.update(
                parecer="Movimentação finalizada por %s em %s."
                % (
                    str(mov.lotacao_destino) if mov else "",
                    DateUtils.datetime_to_str(kwargs.get("data_finalizado")),
                )
            )
        elif not kwargs.get("parecer", None):
            servidor_origem = kwargs.get("servidor_origem")
            servidor_origem = (
                servidor_origem
                if isinstance(servidor_origem, Servidor)
                else Servidor.objects.get(pk=servidor_origem)
            )
            kwargs.update(
                {
                    "parecer": "Movimentação finalizada por %s em %s."
                    % (
                        (
                            str(servidor_origem.pessoa_fisica)
                            + " - "
                            + str(mov.lotacao_destino)
                            if mov
                            else ""
                        ),
                        DateUtils.datetime_to_str(kwargs.get("data_finalizado")),
                    )
                }
            )
        kwargs.update({"destinatario": int(interessado.pk)})
        Movimentacao.criar_movimentacao(kwargs)
        log.info("Enviado com sucesso ao interessado: %s" % str(interessado))

        return True

    @classmethod
    def is_movimentacao_finalizada(cls, movimentacao):
        """
        Este método verifica se a Movimentacao foi finalizada.
        @param Movimentacao - movimentacao.
        @return True, de outra forma False.
        """
        # if movimentacao and not movimentacao.data_finalizado is None:
        #     return True
        # return False
        return movimentacao and movimentacao.data_finalizado

    @classmethod
    def get_lotacao_origem(cls, movimentacao):
        """
        Este método retorna o local de origem baseado na movimentação.
        Geralmente baseando-se na movimentação que está enviando.
        """
        origem = (
            movimentacao.lotacao_destino
            if movimentacao.lotacao_destino
            else movimentacao.lotacao_criacao
        )
        if origem is None:
            raise Exception("Lotação de origem não encontrada!")
        return origem

    """
    ##########################################################
        AÇÕES
    ##########################################################
    """

    @classmethod
    def desfazer_envio(cls, movimentacao):
        """
        Este método é responsável por desfazer o envio de uma ou mais movimentações.
        Assim todos envios serão desfeitos.
        O envio não é desfeito caso: -a nova movimentação já tenha sido recebida;
        -ela tenha sido finalizada;
        """
        cls.is_movimentacao(movimentacao)
        try:
            qprotocolo = Q(protocolo=movimentacao.protocolo)
            qlotacao_destino_eq_lotacao_origem = Q(
                lotacao_destino=movimentacao.lotacao_origem
            )
            qencaminhado = Q(encaminhado=True)
            m_up = Movimentacao.objects.filter(
                Q(qprotocolo & qlotacao_destino_eq_lotacao_origem & qencaminhado)
            ).latest("pk")
            log.debug(m_up)
            qlotacao_origem = Q(lotacao_origem=movimentacao.lotacao_origem)
            mv = Movimentacao.objects.filter(Q(qprotocolo & qlotacao_origem)).exclude(
                passo__lte=m_up.passo
            )
            log.debug(mv)
        except Exception as e:
            log.exception(e)
            raise Exception(
                "Não pode desfazer pois a movimentação já foi recebida em algum local!"
            )
        mv_delete = []
        for m in mv:
            if m.passo > m_up.passo and not m.data_recebimento:
                mv_delete.append(m.pk)
            else:
                mv_delete = []
                break
        if mv_delete:
            Movimentacao.objects.filter(pk__in=mv_delete).delete()
            Movimentacao.objects.filter(pk=m_up.pk).update(
                encaminhado=False, data_finalizado=None
            )
            # if m_up.passo == 0:
            #     Movimentacao.objects.filter(pk=m_up.pk).update(data_encaminhamento=None)
            Protocolo.objects.filter(pk=m_up.protocolo.pk).update(data_finalizado=None)
        else:
            raise Exception(
                "Não pode desfazer pois a movimentação já foi recebida em algum local!"
            )

    @deprecated
    @classmethod
    def finalizar(cls, movimentacao, servidor_origem, parecer=None):
        """
        Este método é responsável por finalizar o Protocolo enviando apenas para o interessado.
        A movimentação já deve estar previamente recebida.
        """
        # TODO: MÉTODO DEPRECIADO PARA EDOCS, OBSERVAR IMPLEMENTAÇÕES DO SISTEMA DE PROCESSOS
        data = datetime.now()
        movimentacao = (
            cls.get_movimentacao(movimentacao)
            if not isinstance(movimentacao, Movimentacao)
            else movimentacao
        )
        if ProtocoloManager.is_finalizado(movimentacao):
            raise Exception("Já finalizado.")

        movimentacao.validate_not_send()

        location_origin = None
        if not movimentacao.lotacao_destino and not movimentacao.lotacao_criacao:
            if servidor_origem.work_locations.exists():
                location_origin = servidor_origem.work_locations.first().pk
            else:
                raise Exception("Lotação de origem não encontrada!")
        else:
            location_origin = cls.get_lotacao_origem(movimentacao).pk

        if cls.is_recebido(movimentacao):
            kwargs = {
                "movimentacao_pk": movimentacao.pk,
                "protocolo": movimentacao.protocolo,
                "orgao_geral_origem": location_origin,
                "servidor_origem": servidor_origem,
                "data_finalizado": data,
                "data_encaminhamento": data,
                "parecer": parecer,
            }
            if cls.envia_interessado(kwargs):
                cls.atualiza_movimentacao_enviada(movimentacao.pk, data)
                movimentacao.protocolo.do_close()
        else:
            raise Exception("Antes de finalizar é necessário receber.")
        return data

    @classmethod
    def receber(cls, movimentacao, servidor):
        """
        Este método é responsável por receber as movimentações dos Protocolos.
        """
        cls.is_movimentacao(movimentacao)
        for mov in movimentacao:
            cls.receber_movimentacao(mov, servidor)

    @classmethod
    def receber_movimentacao(cls, movimentacao, servidor):
        """
        Este método recebe cada Movimentacao do Protocolo.
        """
        mov = cls.get_movimentacao(movimentacao)
        if not cls.is_recebido(mov):
            if ProtocoloManager.is_servidor_pertence_lotacao(
                servidor, mov.lotacao_destino
            ) or cls.is_servidor_destinatario(servidor, mov):
                try:
                    Movimentacao.objects.filter(pk=mov.pk).update(
                        data_recebimento=datetime.now(), servidor_destino=servidor
                    )
                    Movimentacao.objects.filter(pk=mov.pk)
                except Exception as e:
                    log.exception(e)
                    raise Exception(
                        "Ocorreu um erro recebendo o protocolo, contacte a administração do sistema."
                    )
            else:
                raise Exception(
                    "O protocolo não pertence ao servidor ou a esta lotação."
                )
        else:
            raise Exception(
                "O protocolo %s já foi recebido por %s em %s às %s!"
                % (
                    mov.protocolo.codigo,
                    str(mov.servidor_destino.pessoa_fisica),
                    DateUtils.datetime_to_str(mov.data_recebimento),
                    mov.data_recebimento.strftime("%H:%M"),
                )
            )

    @classmethod
    def marcar_nao_recebido_movimentacao(cls, movimentacao, servidor):
        """
        Este método marca cada Movimentacao do Protocolo como não recebido.
        """
        cls.is_movimentacao(movimentacao)
        for m in movimentacao:
            mov = cls.get_movimentacao(m)
            if cls.is_recebido(mov):
                if ProtocoloManager.is_servidor_pertence_lotacao(
                    servidor, mov.lotacao_destino
                ) or cls.is_servidor_destinatario(servidor, mov):
                    Movimentacao.objects.filter(pk=mov.pk).update(
                        data_recebimento=None, servidor_destino=None
                    )
                else:
                    raise Exception(
                        "O protocolo não pertence ao servidor ou a esta lotação!"
                    )
            else:
                raise Exception("O protocolo ainda não foi recebido!")

    @classmethod
    def permissao_movimentacao(cls, movimentacao):
        """
        Este método verifica as permissões sobre o protocolo apresentando uma exceção caso não possua.
        """
        for m in movimentacao:
            mov = cls.get_movimentacao(int(m))
            cls.is_movimentacao(mov)
            if not cls.is_recebido(mov):
                raise Exception(
                    "A movimentação %s ainda não foi recebido!" % mov.protocolo.codigo
                )
            elif mov.encaminhado is True:
                raise Exception(
                    "A movimentação %s já foi enviado!" % mov.protocolo.codigo
                )
            elif cls.is_movimentacao_finalizada(
                mov
            ) or ProtocoloManager.is_protocolo_finalizado(mov.protocolo):
                raise Exception(
                    "A movimentação %s já foi finalizado!" % mov.protocolo.codigo
                )
        return True


class ProtocoloManager(object):

    orgao = "07"
    unidade_administrativa = ["010", "050"]

    @classmethod
    def generate_code(cls, serial):
        numero = cls.orgao + cls.unidade_administrativa[0] + serial
        primeiro_dv = cls.get_primeiro_dv(numero)
        segundo_dv = cls.get_segundo_dv(numero, primeiro_dv)
        return numero + str(primeiro_dv) + str(segundo_dv)

    @classmethod
    def get_digito_verificador(cls, numero):
        """
        Este método  realiza o gerênciamento das funções que geram os dígitos verificadores para o número (ex:'35041.000387/2000-19')
        de parâmetro.
        """
        primeiro_dv = cls.get_primeiro_dv(numero)
        if primeiro_dv != -1:
            segundo_dv = get_segundo_dv(numero, primeiro_dv)
        else:
            return -1
        return str(primeiro_dv) + str(segundo_dv)

    @classmethod
    def dv_is_valid(cls, numero):
        """
        Este método verifica se o número (ex:'35041.000387/2000-19') possui o dígito verificador correto.
        """
        numero = numero.split("-")
        if cls.get_digito_verificador(numero[0]) == numero[1]:
            return True
        return False

    @classmethod
    def get_primeiro_dv(cls, numero):
        """
        Este método gera o primeiro dígito verificador para o número (ex:'35041.000387/2000') de parâmetro.
        """
        try:
            exp = re.compile(r"\.|/|-")
            numero = "%s" % (numero,)
            numero = exp.sub("", numero)
            numero_invertido = numero[::-1]
            peso = 2
            soma = 0
            modulo = 11
            if len(numero_invertido) == 15:
                for dig in numero_invertido:
                    soma += peso * int(dig)
                    peso += 1
            resto = soma % modulo
            dv = modulo - resto
            if dv == 11:
                return 1
            if dv == 10:
                return 1
            if dv == 0:
                return 1
            else:
                return dv
        except Exception as ecp:
            raise ecp
            return -1

    @classmethod
    def get_segundo_dv(cls, numero, p_dv):
        """
        Este método gera o segundo dígito verificador para o número (ex:'35041.000387/2000-1') e o primeiro dígito verificador, p_dv
        informados por parâmetro.
        """
        try:
            exp = re.compile(r"\.|/|-")
            numero = "%s-%d" % (
                numero,
                p_dv,
            )
            numero = exp.sub("", numero)
            numero_invertido = numero[::-1]
            peso = 2
            soma = 0
            modulo = 11
            if len(numero_invertido) == 16:
                for dig in numero_invertido:
                    soma += peso * int(dig)
                    peso += 1
            resto = soma % modulo
            dv = modulo - resto
            if dv == 11:
                return 1
            if dv == 10:
                return 1
            if dv == 0:
                return 1
            else:
                return dv
        except Exception as ecp:
            raise ecp
            return -1

    # numero = "35041.000387/2000"
    # dv_is_valid(numero + '-' + get_digito_verificador(numero))

    @classmethod
    def generate_serial(cls, pk, year):
        serial = str(pk) + str(year)
        zeros = "0" * (10 - len(serial))
        return zeros + serial

    @classmethod
    def is_protocolo(cls, protocolo):
        """
        Este método verifica se o protocolo foi encontrado corretamente.
        Apresenta exceção caso o protocolo não seja encontrado.
        """
        if not protocolo:
            raise Exception(
                "Problemas na movimentação, protocolo não encontrado! \nTente outra vez!"
            )
        return True

    @classmethod
    def get_protocolo(cls, protocolo):
        """
        Este método retorna o Protocolo referenciado pelo protocolo.
        @param int - protocolo do Protocolo
        @return Protocolo/None
        """
        log.debug("protocolo: %s", protocolo)
        p = None

        try:
            if isinstance(protocolo, Protocolo):
                p = protocoloa123
            else:
                p = Protocolo.objects.get(pk=int(protocolo))
        except Protocolo.DoesNotExist:
            p = None
        finally:
            return p

    @classmethod
    def is_protocolo_finalizado(cls, protocolo):
        """
        Este método verifica se o Protocolo foi finalizado.
        @param Protocolo - protocolo.
        @return True, de outra forma False.
        """
        # if protocolo and not protocolo.data_finalizado is None:
        #     return True
        # return False
        return protocolo and protocolo.data_finalizado

    @classmethod
    def is_finalizado(cls, movimentacao):
        """
        Este método verifica se o Protocolo OU a Movimentacao foram finalizados.
        @param Movimentacao - movimentacao.
        @return True, de outra forma False.
        """
        return cls.is_protocolo_finalizado(
            movimentacao.protocolo
        ) or MovimentacaoManager.is_movimentacao_finalizada(movimentacao)

    @classmethod
    def is_movimentacoes_finalizadas(cls, protocolo):
        """
        Este método verifica se todas as movimentações do protocolo foram finalizadas.
        Assim, habilitando finalização do protocolo.
        """
        token = True
        for m in Movimentacao.objects.filter(
            Q(protocolo=protocolo.pk) & Q(encaminhado=False)
        ):
            if m.data_finalizado is None:
                token = False
        log.info(
            "As movimentações %s finalizadas!" % ("foram" if token else "não foram")
        )
        return token

    @classmethod
    def is_interessado_recebeu_finalizado(cls, protocolo, lotacao_origem):
        """
        Este método verifica se o interessado(do protocolo) recebeu alguma movimentação
        finalizada do último remetente.
        """
        token = False
        try:
            token = protocolo.movimentacoes.filter(
                Q(lotacao_origem=lotacao_origem)
                & Q(destinatario=protocolo.interessado)
                & ~Q(data_finalizado=None)
            ).count()
        except Exception:
            pass
        log.info(
            "O interessado %s %s recebeu a última movimentação!"
            % (protocolo.interessado, ("já" if token else "não"))
        )
        return token

    @classmethod
    def is_servidor_pertence_lotacao(cls, servidor, lotacao):
        """
        Este método verifica se o Servidor pertence a uma Lotacao. Esta Lotacao deve estar ativa.
        @param Servidor - servidor.
        @param Movimentacao - movimentacao.
        @return True se pertencer, de outra forma False.
        """
        # return servidor.work_assignment.filter(lotacao=lotacao).exists()
        return servidor.work_locations_effective_exercise.filter(pk=lotacao.pk).exists()

    @classmethod
    def set_anexo(cls, anexos, movimentacao, editar=False):
        """
        Este método anexa os arquivos à Movimentacao.
        @param post - POST.
        @return True se for realizado sem problemas, de outra forma False.
        """
        try:
            for a in anexos:
                if not movimentacao.anexos.filter(pk=int(a)):
                    movimentacao.anexos.add(Anexo.objects.get(pk=int(a)))
            if editar:
                for a in movimentacao.anexos.all():
                    if not str(a.pk) in anexos:
                        movimentacao.anexos.remove(a)
        except Exception as e:
            log.exception(e)
            return False
        return True

    @classmethod
    def set_referencia(cls, referencias, protocolo, editar=False):
        """
        Este método referencia os Protocolos escolhidos ao Protocolo.
        @param post - POST.
        @return True se for realizado sem problemas, de outra forma False.
        """
        try:
            for r in referencias:
                if not protocolo.referencias.filter(pk=int(r)):
                    protocolo.referencias.add(Referencia.objects.get(pk=int(r)))
            if editar:
                for r in protocolo.referencias.all():
                    if not str(r.pk) in referencias:
                        protocolo.referencias.remove(r)
        except Exception as e:
            log.exception(e)
            return False
        return True

    @classmethod
    def get_referenciado_por(cls, protocolo):
        """
        Este método retorna uma lista com todos os protocolos que referenciaram o protocolo parâmetro.
        Esta lista é utilizada pelo método view.
        @param Protocolo - protocolo.
        @return list
        """
        referenciado_por = []
        for referenciado in Protocolo.objects.filter(referencias__protocolo=protocolo):
            obj["referenciado_por"].append(
                {
                    "codigo": referenciado.codigo,
                    "assunto": str(referenciado.assunto),
                    "resumo": str(referenciado.resumo),
                }
            )
        return referenciado_por

    @classmethod
    def get_referencias(cls, protocolo):
        """
        Este método retorna uma lista com todas referências de um protocolo.
        Esta lista é utilizada pelo método view.
        @param Protocolo - protocolo.
        @return list
        """
        referencias = []
        for referencia in protocolo.referencias.all():
            referencias.append(
                {
                    "codigo": referencia.protocolo.codigo,
                    "assunto": str(referencia.protocolo.assunto),
                    "resumo": str(referencia.protocolo.resumo),
                }
            )
        return referencias

    @classmethod
    def get_anexos_from_protocolo(cls, protocolo):
        """
        Este método retorna uma lista com todos os anexos de um protocolo.
        @param Protocolo - protocolo.
        @return list
        """
        anexos = []
        try:
            for movimentacao in protocolo.movimentacoes.filter(~Q(anexos=None)):
                for a in movimentacao.anexos.all():
                    anexos.append(a)
        except Exception as e:
            log.exception(e)

        return anexos

    """
    ##########################################################
        AÇÕES.
    ##########################################################
    """

    @classmethod
    def delete_protocolo(cls, codigo):
        """
        Este método é responsável por marcar o protocolo como excluído.
        """
        try:
            if Movimentacao.objects.filter(protocolo__codigo=codigo).count() > 1:
                raise Exception()
            else:
                Protocolo.objects.filter(codigo=codigo).update(excluido=True)
        except Exception:
            raise Exception(
                "Não é possível excluir este protocolo pois ele já foi movimentado!"
            )

    @classmethod
    def carregar_protocolo(cls, movimentacao, protocolo):
        """
        Este método encontra o protocolo, verifica as permissões e retorna algumas
        informações: [{id, description},{recebido:boolean, msg }, {encaminhado:boolean}]
        @return result, perm_envio, message
        """
        perm_envio = True
        message = ""
        result = []
        mov = MovimentacaoManager.get_movimentacao(movimentacao)
        MovimentacaoManager.is_movimentacao(mov)
        prot = Protocolo.objects.get(codigo=protocolo)
        cls.is_protocolo(prot)
        valor = {"id": prot.id, "description": str(prot)}
        result.append(valor)

        valor = {"recebido": True, "msg": ""}
        if not MovimentacaoManager.is_recebido(mov):
            valor = {"recebido": False, "msg": "Este protocolo ainda não foi recebido!"}
        result.append(valor)

        valor = {"encaminhado": False}
        if mov.encaminhado is True:
            message = "Este protocolo já foi enviado!"
            perm_envio = False
        if cls.is_finalizado(mov):
            message = "Este protocolo já foi finalizado!"
            perm_envio = False
        result.append(valor)
        return result, perm_envio, message

    @classmethod
    def get_lotacao_criacao(cls, servidor_pk):
        """
        Este método retorna a primeira lotação com acesso_protocolo_geral encontrado.
        """
        lotacao_criacao = None
        employee_workplace = Servidor.objects.get(pk=servidor_pk).work_assignment
        if employee_workplace.filter(lotacao__acesso_protocolo_geral=True).exists():
            lotacao_criacao = (
                employee_workplace.filter(lotacao__acesso_protocolo_geral=True)
                .latest("data_vigencia_inicio")
                .lotacao
            )
        return lotacao_criacao

    @classmethod
    def get_orgao_geral(cls, pk):
        """
        Este método retorna um OrgaoGeral.
        """
        try:
            return OrgaoGeral.objects.get(pk=int(pk))
        except Exception:
            return None

    @classmethod
    def get_pessoa(cls, pk):
        try:
            return Pessoa.objects.get(pk=int(pk))
        except Exception:
            return None

    @classmethod
    def novo_protocolo(cls, kwargs):
        tipo_documento = TipoDocumento.objects.get(pk=kwargs.get("tipo_documento"))
        orgao_geral = cls.get_orgao_geral(kwargs.get("orgao_geral"))
        interessado = cls.get_pessoa(kwargs.get("interessado"))
        if interessado is None or orgao_geral is None:
            raise Exception(
                "Problemas na Criação do Protocolo!\nServidor não encontrado!"
            )
        protocolo = None
        chancela = kwargs.get("chancela", None)
        midia = kwargs.get("midia") if kwargs.get("midia") != "" else None
        assunto = kwargs.get("assunto", None)
        servidor_origem = Servidor.objects.get(pk=kwargs.get("servidor"))
        protocolo_externo = kwargs.get("numero_externo", None)
        resumo = kwargs.get("resumo")

        lotacao_criacao = ProtocoloManager.get_lotacao_criacao(servidor_origem.pk)

        try:
            protocolo = Protocolo.objects.get(codigo=kwargs.get("codigo"))
        except Exception:
            protocolo = Protocolo(
                interessado=interessado,
                chancela=chancela,
                midia=midia,
                assunto=assunto,
                orgao_geral_origem=orgao_geral,
                lotacao_criacao=lotacao_criacao,
                servidor_origem=servidor_origem,
                protocolo_externo=protocolo_externo,
                resumo=resumo,
                tipo_documento=tipo_documento,
            )
        else:
            protocolo.interessado = interessado
            protocolo.chancela = chancela
            protocolo.midia = midia
            protocolo.assunto = assunto
            protocolo.orgao_geral_origem = orgao_geral
            protocolo.lotacao_criacao = lotacao_criacao
            protocolo.servidor_origem = servidor_origem
            protocolo.protocolo_externo = protocolo_externo
            protocolo.resumo = resumo
            protocolo.tipo_documento = tipo_documento
        finally:
            protocolo.save()
            from app.database import force_database

            with force_database("default"):
                if not ProtocoloManager.set_anexo(
                    kwargs.get("anexos"),
                    protocolo.movimentacoes.get(passo=0),
                    editar=True,
                ):
                    raise Exception(
                        "Os arquivos não foram anexados ao protocolo, tenten novamente!"
                    )
                if not ProtocoloManager.set_referencia(
                    kwargs.get("referencias"), protocolo, editar=True
                ):
                    raise Exception(
                        "As referências a outros protocolos não foram criadas, tente novamente!"
                    )


# ########################################## MANAGER FIM ############################


class EDOCUtils:

    @staticmethod
    def valida_tamanho_textfield(label, valor, tamanho):
        """
        Este método é responsável por validar o tamanho do campo informado.
        """
        if valor and len(valor) > tamanho:
            raise Exception(
                "O campo %s excedeu o seu tamanho limite de %s caracteres!"
                % (label, tamanho)
            )


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "descricao", "type": "text"},
    ]
)
class TipoDocumento(standard_models.CObject):
    habilita = models.BooleanField(default=False)

    class Meta:
        ordering = ("nome",)


class TipoAssunto(standard_models.CObject):
    pass


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "arquivo__filename", "type": "text"},
        {"name": "arquivo__group__nome", "type": "text"},
        {"name": "arquivo__user__username", "type": "text"},
    ]
)
class Anexo(standard_models.CObject):
    arquivo = models.ForeignKey(
        Arquivo, null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


class Etiqueta(standard_models.CObject):
    protocolo = models.OneToOneField(
        "Protocolo", null=False, blank=False, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    carimbo_tempo = models.DateTimeField(auto_now_add=True)
    localidade = models.CharField(max_length=100)
    orgao = models.CharField(max_length=100)
    label_inferior = models.CharField(max_length=100)


@to_search(
    [
        {"name": "protocolo__interessado__nome", "type": "text"},
        {"name": "protocolo__assunto", "type": "text"},
        {"name": "protocolo__orgao_geral_origem__nome", "type": "text"},
        {"name": "protocolo__orgao_geral_destino__nome", "type": "text"},
        {"name": "protocolo__lotacao_criacao__nome", "type": "text"},
        {"name": "protocolo__servidor_origem__pessoa_fisica__nome", "type": "text"},
        {"name": "protocolo__protocolo_externo", "type": "text"},
        {"name": "protocolo__chancela", "type": "text"},
    ]
)
class Referencia(AuditTimestampModel):
    protocolo = models.ForeignKey(
        "Protocolo", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    movimentacao = models.ForeignKey(
        "Movimentacao", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{0}".format(self.protocolo)


class Protocolo(AuditTimestampModel):

    AUDITABLE = {
        "exclude": [
            "id",
        ]
    }

    interessado = models.ForeignKey(
        Pessoa, related_name="prot_interessado", on_delete=models.PROTECT
    )
    assunto = models.CharField(max_length=255, db_index=True, blank=True)
    orgao_geral_origem = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Origem",
        related_name="prot_orgao_origem",
        on_delete=models.PROTECT,
    )
    orgao_geral_destino = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Destino",
        related_name="prot_orgao_destino",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    lotacao_criacao = models.ForeignKey(
        OrgaoGeral,
        verbose_name="Lotação de Criação",
        related_name="prot_lotacao_criacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    servidor_origem = models.ForeignKey(
        Servidor, related_name="prot_servidor_origem", on_delete=models.PROTECT
    )
    protocolo_externo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Número Externo",
        db_index=True,
    )
    resumo = models.TextField(null=True, blank=True)
    referencias = models.ManyToManyField(
        "Referencia",
        symmetrical=True,
        related_name="prot_referencias",
        verbose_name="Referências",
    )
    tipo_documento = models.ForeignKey(
        "TipoDocumento", related_name="prot_tipo_documento", on_delete=models.PROTECT
    )
    deferido = models.BooleanField(null=True, blank=True)
    encaminhado = models.BooleanField(default=False, blank=True)
    grupo = models.BooleanField(default=False, blank=True)
    habilitado = models.BooleanField(default=False, blank=True)
    codigo = models.CharField(
        max_length=50, unique=True, db_index=True, blank=True
    )  # este campo será composto por: ano(4 dígitos) + dígito verificador(2), mas o código geral será composto por: órgao(2) + unidade administrativa(3) + serial(6) + "/" + este campo código
    data_criacao = models.DateTimeField(auto_now_add=True, db_index=True)
    serial = models.CharField(
        max_length=10, null=True, blank=True, db_index=True
    )  # será o id da entidade + ano
    excluido = models.BooleanField(default=False)
    chancela = models.CharField(
        max_length=30, null=True, blank=True, default="0000", db_index=True
    )
    midia = models.IntegerField(
        choices=list(MIDIA_ORIGEM.items()), null=True, blank=True, db_index=True
    )
    data_finalizado = models.DateTimeField(
        null=True, blank=True, default=None, db_index=True
    )
    com_workflow = models.BooleanField(default=False)
    cache_rendered = models.TextField(null=True, blank=True)

    # Com a implantação do app document_access, essa flag terá
    # outra responsabilidade, ou seja, será True quando um documento for
    # classificado, ou False se não houver classificação ou for
    # desclassificado.
    sigiloso = models.BooleanField(default=False)

    special_type = models.CharField(max_length=60, db_index=True, null=True, blank=True)
    # Searchable vector
    search_vector = SearchVectorField(null=True)

    manager = ProtocoloManager()

    class Meta:
        indexes = (GinIndex(fields=["search_vector"]),)
        permissions = (("has_general_protocol", "Tem protocolo geral."),)

    @property
    def _template_renderer(self):
        return loader.get_template("protocolo/protocol.html")

    def _renderer(self):
        return self._template_renderer.render(self.params)

    @property
    def my_origin(self):
        if self.special_type and hasattr(self, self.special_type):
            return getattr(self, self.special_type)

        return self

    @property
    def params(self):
        return {"protocol": self}

    @property
    def attachment_list(self):
        return self.attachments.filter(
            pk__in=self.attachments.order_by("attach").distinct("attach")
        ).order_by("created_at")

    def sign_document(self):
        ProtocolLegalSign.sign(self)

    def unsign_document(self):
        ProtocolLegalSign.remove_signatures(self)

    @property
    def renderer_legal_signs(self):
        tpl = loader.get_template("protocolo/legalSigns.html")
        return tpl.render({"protocol": self})

    @property
    def rendered_content(self):
        return (
            self.cache_rendered if self.cache_rendered else self.my_origin._renderer()
        )

    @property
    def rendered(self):
        if self.can_read:
            data = (
                self.cache_rendered
                if self.cache_rendered
                else self.my_origin._renderer()
            )

            if self.valid_signatures.exists():
                data += self.renderer_legal_signs
        else:
            data = loader.get_template("protocolo/access-denied.html").render(
                {"protocol": self}
            )

        return data

    @property
    @deprecated
    def appends_of_document_cachefile(self):
        cache_path = getattr(settings, "CACHE", {}).get("dir", "/tmp")
        protocol_cache_part_dir = self.codigo[-6:]
        protocol_cache_dir = os.path.join(
            cache_path,
            "edoc",
            protocol_cache_part_dir[0:4],
            protocol_cache_part_dir[4:],
        )

        log.debug("Protocol Cache Directory: %s", protocol_cache_dir)
        if not os.path.exists(protocol_cache_dir):
            os.makedirs(protocol_cache_dir)

        return os.path.join(protocol_cache_dir, "%s.html" % self.codigo)

    @property
    def cache_key(self):
        return f"edoc.{self.codigo}"

    def invalidate_appendix_cache(self):
        cache = caches["default"]
        cache.delete(self.cache_key)

    @property
    def appends_of_document(self):
        return self.appendix_cache()

    def build_appendix_cache(self, movement_id=None):
        """Cria o cache do protocolo"""
        cache = caches["default"]

        movement = selected = None
        if movement_id:
            try:
                movement = Movimentacao.objects.get(pk=movement_id)
            except Movimentacao.DoesNotExist:
                # Caso não exista movimentação, o erro será deliberadamente suprimido.
                # Isso se faz necessário porque movimentações podem ser excluídas,
                # como no caso da feature de desfazer movimentações.
                movement = None
            else:
                if movement.child_of:
                    selected = movement.child_of.pk

        template = loader.get_template("protocolo/unified/movements.html")
        page_movements = template.render({"protocol": self, "selected": selected})

        key = self.cache_key
        cache.set(key, page_movements, timeout=None)

        return page_movements

    def appendix_cache(self, movement_id=None):
        """Retorna o cache do protocolo

        Esse cache consiste em um apêndice de movimentações, e é
        construído a partir da junção dos caches de todas e somente
        as movimentações que possuem descendentes.
        """
        # Validação do controle de acesso a documentos.
        if not self.can_read:
            return []

        # Recupera apêndice a partir do cache Redis.
        cache = caches["default"]
        key = self.cache_key
        page_movements = cache.get(key)

        # Se não tem cache, constrói um.
        if not page_movements:
            page_movements = self.build_appendix_cache(movement_id)

        return [page_movements]

    @property
    def was_sent(self):
        return self.movimentacoes.filter(passo__gt=0).exists()

    @classmethod
    def docketing(
        cls,
        subject,
        document_type,
        interested=None,
        home_court=None,
        external_number=None,
        content=None,
        movement_id=None,
        seal_number=None,
        media=None,
        with_workflow=False,
        is_collaborative=False,
    ):
        """Cria um protocolo novo ou atualiza um existente.

        Se for um protocolo existente, ele só será atualizado se
        ainda não foi movimentado.
        """
        if interested is None or home_court is None:
            raise Exception(
                "Não foi possível identificar quem está enviando o protocolo."
            )

        with transaction.atomic():
            employee = employee_from_user(get_current_user())

            if movement_id:
                movement = Movimentacao.objects.get(pk=movement_id)
                protocol = movement.protocolo.my_origin
                if movement.passo > 0 or protocol.was_sent:
                    raise Exception(
                        "Não posso modificar um protocolo que já foi movimentado."
                    )
            else:
                movement = None
                protocol = cls()

            protocol.interessado = interested
            protocol.chancela = seal_number
            protocol.midia = media if media else None
            protocol.protocolo_externo = external_number
            protocol.assunto = subject
            protocol.orgao_geral_origem = home_court
            protocol.lotacao_criacao = employee.general_protocol.first()
            protocol.servidor_origem = employee
            protocol.resumo = content if content else protocol.resumo
            protocol.tipo_documento = document_type
            protocol.save()

            if movement is None:
                movement = protocol.movimentacoes.get(passo=0)

            if is_collaborative:
                movement.destinatario = None

            movement.with_workflow = with_workflow
            movement.save()

        return protocol

    @classmethod
    def Movimentacao(cls):
        return Movimentacao

    def __str__(self):
        return "{0} - {1}".format(self.codigo, self.assunto)

    def custo_passo(self, passo):
        custo = datetime.now() - datetime.now()
        try:
            mov = self.movimentacoes.get(passo=passo)
        except Movimentacao.DoesNotExist:
            custo = datetime.now() - datetime.now()
        else:
            data_fim = None
            if self.movimentacoes.filter(passo=(passo + 1)).exists():
                next_mov = self.movimentacoes.get(passo=(passo + 1))
                data_fim = next_mov.data_encaminhamento
            else:
                data_fim = datetime.now()
            custo = (
                data_fim.date() - mov.data_encaminhamento.date()
                if mov.data_encaminhamento.date()
                else ""
            )
        return custo

    @property
    def cronologic_moviments(self):
        return self.movimentacoes.exclude(passo=0).order_by("passo")

    @property
    def cronologic_moviments_simple(self):
        return self.movimentacoes.exclude(passo=0).order_by("-passo")[:5]

    @property
    def fathers_of_moviment(self):
        fathers = []
        for moviment in self.cronologic_moviments:
            father = moviment.child_of
            if father:
                if father not in fathers:
                    fathers.append(father)

        return fathers

    @property
    def valid_signatures(self):
        return self.legal_signs.filter(invalidated_at=None)

    @property
    def was_changed(self):
        fields = [
            "sigiloso",
            "assunto",
            "resumo",
            "protocolo_externo",
            "tipo_documento",
        ]
        return set(fields).intersection(set(self.old_fields.keys()))

    def validate_seal(self):
        if not self.is_valid_seal():
            raise Exception(
                "Não foi possível gravar as informações.\nPor favor "
                "retire os caracteres que não são permitidos na chancela."
            )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.save_new(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            if self.was_changed:
                self.unsign_document()

    def save_new(self, *args, **kwargs):
        """Valida chancela, cria serial e código e faz primeira movimentação."""
        self.validate_seal()
        super().save(*args, **kwargs)  # We need pk to generate our serial.
        self.serial = ProtocoloManager.generate_serial(self.pk, self.data_criacao.year)
        self.codigo = ProtocoloManager.generate_code(self.serial)
        super().save(
            *args, **kwargs
        )  # Save again here, otherwise 'codigo' won't persist.
        self.create_first_movement()

    def create_first_movement(self):
        """Cria a primeira movimentação do protocolo.

        Na primeira movimentação o destinatário será o próprio
        servidor de origem.
        """
        Movimentacao.criar_movimentacao(
            {
                "protocolo": self,
                "orgao_geral_origem": (
                    self.orgao_geral_origem.pk if self.orgao_geral_origem else None
                ),
                "orgao_geral_destino": (
                    self.orgao_geral_origem.pk if self.orgao_geral_origem else None
                ),
                "servidor_origem": (
                    self.servidor_origem.pk if self.servidor_origem else None
                ),
                "servidor_destino": (
                    self.servidor_origem.pk if self.servidor_origem else None
                ),
                "lotacao_criacao": (
                    self.lotacao_criacao.pk if self.lotacao_criacao else None
                ),
                "data_recebimento": self.data_criacao,
                "data_encaminhamento": self.data_criacao,
                "parecer": self.resumo,
                "passo": 0,
                "destinatario": (
                    self.servidor_origem.pessoa_fisica.pk
                    if self.servidor_origem.pessoa_fisica
                    else None
                ),
            }
        )

    def is_valid_seal(self):
        """Valida chancela."""
        if not self.chancela or re.match(r"^[\d]{0,30}$", self.chancela, re.IGNORECASE):
            return True
        return False

    def movements_termination(self):
        """
        :py:function:: movements_termination(self)

        This method returns a Movimentacao.queryset which has no children.

        :return: queryset of Movimentacao
        :rtype: queryset
        """
        return self.movimentacoes.filter(Q(derivative_for=None))

    @property
    def movements_termination_closed(self):
        """
        :py:function:: movements_termination_closed(self)

        This property verifies if all movements termination were ended.

        :return: boolean True if all were closed, otherwise False
        :rtype: boolean
        """
        return (
            self.movements_termination().count()
            == self.movements_termination().filter(~Q(data_finalizado=None)).count()
        )

    def do_close(self):
        """
        :py:function:: do_close(self)

        This method closes the Protocolo. It uses sefl.movements_termination_closed to decide.

        :return: boolean True if it was closed, otherwise False
        :rtype: boolean
        """
        done = True
        if self.movements_termination_closed:
            self.data_finalizado = datetime.now()
            self.save()
            log.info(
                "Protocolo %s finalizado %s."
                % (self.codigo, DateUtils.date_to_str(self.data_finalizado))
            )
        else:
            done = False
        return done

    def do_reopen(self):
        """
        :py:function:: do_reopen(self)

        This method reopens the Protocolo.

        :return: boolean True if it was reopened, otherwise False
        :rtype: boolean
        """
        self.data_finalizado = None
        self.save()
        log.info(
            "Protocolo %s reaberto %s."
            % (self.codigo, DateUtils.datetime_to_str(datetime.now()))
        )

    @property
    def references(self):
        """
        :py:function:: references(self)

        This property returns all references.

        :return: queryset Referencia
        :rtype: queryset
        """
        return Referencia.objects.filter(
            pk__in=self.movimentacoes.filter(~Q(referencia=None)).values("referencia")
        )

    @property
    def control_type(self):
        """Retorna o Nível de Acesso para este protocolo, se houver."""
        if self.control:
            return self.control.control_type
        return None

    @property
    def legal_prerogative(self):
        """Retorna a Hipótese Legal para este protocolo, se houver."""
        if self.control:
            return self.control.legal_prerogative
        return None

    @property
    def protocol_control(self):
        result = None

        if hasattr(self, "protocol_control"):
            result = self.protocol_control

        return result

    @property
    def can_read(self):
        """Retorna True se o usuário corrente estiver autorizado a ler
        o conteúdo do documento. Caso contrário, retorna False.

        Verifica se este procotolo possui controle de acesso. Se possui,
        então verifica se o usuário corrente está autorizado a ler o seu
        conteúdo. Mas se não existe controle de acesso, retorna True por
        padrão.
        """
        if self.control:
            return self.control.can_read
        return True

    @property
    def control(self):
        """Retorna o controle de acesso correspondente, caso exista (model Control, app document_access)."""
        return getattr(self, "protocol_control", None)


class PermissaoEdoc(AuditTimestampModel):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=6)

    def __str__(self):
        return "{0}".format(self.nome)


class CompartilharCaixa(AuditTimestampModel):
    pessoa_fisica_dono = models.OneToOneField(
        PessoaFisica, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    pessoa_fisica = models.ManyToManyField(
        PessoaFisica, symmetrical=False, related_name="pessoa_compartilhada"
    )
    permissao = models.ManyToManyField(PermissaoEdoc, symmetrical=False)

    class Meta:
        db_table = "protocolo_comp_caixa"


class CompartilharProtocolo(AuditTimestampModel):
    pessoa_fisica = models.ManyToManyField(
        PessoaFisica, symmetrical=False, related_name="pessoa_comp_prot"
    )
    lotacao = models.ManyToManyField(
        OrgaoGeral, symmetrical=False, related_name="lotacao_comp_prot"
    )
    protocolo = models.ForeignKey(
        Protocolo,
        related_name="protocolo_comp_prot",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    permissao = models.ManyToManyField(PermissaoEdoc, symmetrical=False)

    class Meta:
        db_table = "protocolo_comp_prot"


class Movimentacao(AuditTimestampModel):
    protocolo = models.ForeignKey(
        Protocolo, related_name="movimentacoes", on_delete=models.PROTECT
    )
    lotacao_origem = models.ForeignKey(
        OrgaoGeral, related_name="mov_lotacao_origem", on_delete=models.PROTECT
    )
    lotacao_destino = models.ForeignKey(
        OrgaoGeral,
        related_name="mov_lotacao_destino",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    lotacao_criacao = models.ForeignKey(
        OrgaoGeral,
        related_name="mov_lotacao_criacao",
        verbose_name="Lotação de Criação",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    servidor_origem = models.ForeignKey(
        Servidor, related_name="mov_servidor_origem", on_delete=models.PROTECT
    )
    servidor_destino = models.ForeignKey(
        Servidor,
        related_name="mov_servidor_destino",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    destinatario = models.ForeignKey(
        Pessoa,
        related_name="mov_destinatario",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    anexos = models.ManyToManyField("Anexo", related_name="movimentacao")
    deferido = models.BooleanField(null=True, blank=True)
    parecer = models.TextField(null=True, blank=True)
    encaminhado = models.BooleanField(default=False)
    data_recebimento = models.DateTimeField(null=True, blank=True)
    data_encaminhamento = models.DateTimeField(null=True, blank=True, db_index=True)
    passo = models.IntegerField(db_index=True)
    urgente = models.BooleanField(default=False)
    data_finalizado = models.DateTimeField(
        null=True, blank=True, default=None, db_index=True
    )
    cache_rendered = models.TextField(null=True)
    # cache_send_at = models.DateTimeField(null=True, blank=True)
    child_of = models.ForeignKey(
        "self", related_name="derivative_for", null=True, on_delete=models.PROTECT
    )
    reopen_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="moviment_reopen",
    )
    reopen_at = models.DateTimeField(null=True, blank=True)
    physical = models.BooleanField(default=False)
    with_workflow = models.BooleanField(default=False)
    confidential = models.BooleanField(default=False)

    manager = MovimentacaoManager()

    class Meta:
        ordering = ["data_encaminhamento"]

    @property
    def cache_key(self):
        return f"edoc.{self.protocolo.codigo}.{self.pk}"

    def invalidate_cache(self):
        """Deleta o cache desta movimentação

        Este método é a contraparte do método cache.

        Este método também deleta o cache do protocolo. Assim, na próxima
        requisição de renderização, o cache do protocolo será reconstruído
        com informação atualizada.

        Outrossim, este método é chamado sempre que o envio de uma
        movimentação é desfeito. Desta forma, quando o cache do protocolo
        for reconstruído, é bem provável que ele não incluirá o cache desta
        movimentação, já que ela deixará de ter movimentações filhas.

        Por fim, este método também é chamado sempre que o "cache de recebido"
        (ver método received_cache) de uma movimentação filha for deletado.
        """
        cache = caches["default"]
        cache.delete(self.cache_key)
        self.protocolo.invalidate_appendix_cache()

    @property
    def cache(self):
        """Retorna o cache desta movimentação

        Se não houver cache, será criado.

        Este cache é utilizado no tile do EDOC e aparece na forma dos
        campos "Remetente", "Enviado em" e "Parecer", além de ser composto
        pelos "caches de recebidos" (ver método received_cache) os
        quais representam as movimentações filhas.
        """
        cache = caches["default"]
        cache_key = self.cache_key
        render = cache.get(cache_key)

        if not render:
            template = loader.get_template("protocolo/unified/movement.html")
            render = template.render({"movement": self})
            cache.set(cache_key, render, timeout=None)

        return render

    @property
    def received_cache_key(self):
        part_1 = self.protocolo.codigo
        part_2 = self.child_of.pk if self.child_of else self.pk
        part_3 = self.pk

        return f"edoc.{part_1}.{part_2}.{part_3}"

    def invalidate_received_cache(self):
        """Deleta o "cache de recebido"

        O "cache de recebido" (na falta de um nome melhor) consiste
        em uma table row (tr) de HTML composta pelas colunas "Destinatário",
        "Recebido por" e "Recebido em".

        Este método, além de deletar o "cache de recebido", se houver uma
        movimentação pai, o cache dele também será deletado e, por
        consequência, o cache do protocolo.

        Outrossim, esse método é chamado sempre que uma movimentação é recebida.
        """
        cache = caches["default"]
        cache.delete(self.received_cache_key)
        if self.child_of:
            self.child_of.invalidate_cache()

    @property
    def received_cache(self):
        """Retorna o "cache de recebido"

        Se o cache não existir, ele será gerado.

        O "cache de recebido" (na falta de um nome melhor) consiste em
        uma table row (tr) de HTML com as colunas "Destinatário",
        "Recebido por" e "Recebido em", e é utilizado para compor o cache
        da movimentação pai.
        """
        cache = caches["default"]
        key = self.received_cache_key
        row = cache.get(key)

        if not row:
            template = loader.get_template("protocolo/unified/movement_received.html")
            row = template.render({"child": self})
            cache.set(key, row, timeout=None)

        return row

    @property
    def is_delivery_pending(self):
        if hasattr(self, "envelops"):
            return self.envelops.filter(
                delivery_state__in=[Envelop.PENDENT, Envelop.IN_DELIVERY]
            ).exists()

        return False

    @property
    def renderer_legal_signs(self):
        tpl = loader.get_template("protocolo/moviment-signs.html")

        return tpl.render({"movement": self})

    @property
    def send_at(self):
        if self.derivative_for.exists():
            return self.derivative_for.first().data_encaminhamento
        else:
            return None

    @property
    def rendered_content(self):
        data = self.rendered

        if self.legal_signs.exists():
            data += self.renderer_legal_signs

        return data

    @property
    def rendered_content_unified(self):
        return (
            self.derivative_for.first().rendered_content
            if self.derivative_for.exists()
            else None
        )

    @property
    def rendered(self):
        tpl = loader.get_template("protocolo/moviment-detail.html")

        return tpl.render(
            {
                "desambiguation_code": hashlib.new("md5", os.urandom(4096)).hexdigest(),
                "movement": self,
            }
        )

    @property
    def has_child(self):
        return self.protocolo.movimentacoes.filter(child_of=self).exists()

    @deprecated
    def validate_not_from_edoc(self):
        log.info(
            ">>>> Não é mais necessário utilizar essa validação, pois o edoc vai funcionar como api para outros softwares."
        )
        if (
            hasattr(self.protocolo, "processo") and self.protocolo.processo
        ) or self.with_workflow:
            raise Exception("Processo não pode ser finalizado através do EDOCs.")
        return True

    def validate_general_organ_disabled(self, general_organ):
        if not self.with_workflow and not general_organ.habilita_protocolo:
            raise Exception(
                "Não autorizado o envio de documento para %s!" % general_organ
            )
        return True

    def validate_person_disabled(self, person, close):
        # FIXME: MODIFICAR IMPLEMENTAÇÃO QUANDO O MÉTODO DE FINALIZAÇÃO MUDAR
        if not self.with_workflow and not close and not person.enable_protocol:
            raise Exception("Não autorizado o envio de documento para %s!" % person)
        return True

    def validate_close(self):
        if self.protocolo.data_finalizado or self.data_finalizado:
            raise Exception(
                "Protocolo finalizado %s. Não é possível movimentar."
                % (
                    DateUtils.date_to_str(
                        self.protocolo.data_finalizado or self.data_finalizado
                    )
                )
            )
        return True

    def validate_not_send(self, reopen=False):
        if not reopen:
            self.validate_close()
        return True

    def undo(self, ignore_workflow=False):
        log.info("undo - Passo: %s", self.passo)

        children = self.derivative_for.all()
        with transaction.atomic():
            for child in children:
                child.undo_specific(
                    check_destination=False, ignore_workflow=ignore_workflow
                )

    def undo_specific(self, check_destination=True, ignore_workflow=False):
        log.info("undo_specific - Passo: %s", self.passo)

        if self.with_workflow and not ignore_workflow:
            raise Exception(
                "Operação não permitida para o protocolo %s." % self.protocolo.codigo
            )

        if self.data_recebimento:
            raise Exception(
                "Não foi possível desfazer o envio do protocolo %s, pois o destinatário já o recebeu."
                % self.protocolo.codigo
            )

        with transaction.atomic():
            father = self.child_of
            if father:
                if father.derivative_for.all().count() > 1:
                    if (
                        check_destination
                        and self.data_finalizado
                        and self.destinatario.pk == self.protocolo.interessado.pk
                    ):
                        raise Exception(
                            "Não é possível desfinalizar esta movimentação pois ela foi endereçada ao interessado."
                        )
                else:
                    if father.data_finalizado:
                        father.data_finalizado = None
                        father.save()

                    if father.encaminhado:
                        father.encaminhado = False
                        father.save()

                    if self.protocolo.data_finalizado:
                        self.protocolo.data_finalizado = None
                        self.protocolo.save()

                    self.invalidate_cache()

                if self.destinations.exists():
                    self.destinations.update(
                        movement_undone_at=datetime.now(),
                        movement_undone_by=get_current_user(),
                    )

                self.delete()
            else:
                raise Exception(
                    "Não foi possível localizar a movimentação que gerou esta movimentação."
                )

    def validate_possession_for_do_send(self):
        if (
            not self.inbox_queryset().filter(pk=self.pk).exists()
            and not self.closedbox_queryset().filter(pk=self.pk).exists()
        ):
            raise Exception(
                "O protocolo não está mais sob sua posse, desta forma não pode ser movimentado."
            )
        else:
            log.debug("inbox %d", self.inbox_queryset().filter(pk=self.pk).count())

    def validate_destinations(
        self, person_destination, location_destination, group_person, group_location
    ):
        if (
            len(grant_list(person_destination)) == 0
            and len(grant_list(location_destination)) == 0
            and len(grant_list(group_person)) == 0
            and len(grant_list(group_location)) == 0
        ):
            raise Exception(
                "Você deve selecionar pelo menos um destinatário para a movimentação do documento."
            )

    def _send_to_group_person(
        self,
        queryset=None,
        location_origin=None,
        employee_origin=None,
        references=None,
        attachments=None,
        advice=None,
        opinion=None,
        urgency=None,
        close=None,
        reopen=None,
        physical=None,
        with_workflow=None,
        confidential=False,
    ):
        from edocs.protocolo.task.dispatch import async_send_to_person
        from celery import group

        def iterator(queryset):
            for person in queryset:
                yield {
                    "location_origin": location_origin.pk,
                    "person": person.pk,
                    "location": None,
                    "employee_origin": employee_origin.pk,
                    "references": references,
                    "attachments": attachments,
                    "advice": advice,
                    "opinion": opinion,
                    "urgency": urgency,
                    "close": close,
                    "reopen": reopen,
                    "physical": physical,
                    "with_workflow": with_workflow,
                    "confidential": confidential,
                }

        group(
            [
                async_send_to_person.s(
                    **{
                        "user_id": get_current_user().pk,
                        "movement_id": self.pk,
                        "opts": opts,
                    }
                )
                for opts in iterator(queryset)
            ]
        )()

    def _send_to_group_location(
        self,
        queryset=None,
        location_origin=None,
        employee_origin=None,
        references=None,
        attachments=None,
        advice=None,
        opinion=None,
        urgency=None,
        close=None,
        reopen=None,
        physical=None,
        with_workflow=None,
        confidential=False,
    ):
        from edocs.protocolo.task.dispatch import async_send_to_location
        from celery import group

        def iterator(queryset):
            for location in queryset:
                yield {
                    "location_origin": location_origin.pk,
                    "person": None,
                    "location": location.pk,
                    "employee_origin": employee_origin.pk,
                    "references": references,
                    "attachments": attachments,
                    "advice": advice,
                    "opinion": opinion,
                    "urgency": urgency,
                    "close": close,
                    "reopen": reopen,
                    "physical": physical,
                    "with_workflow": with_workflow,
                    "confidential": confidential,
                }

        group(
            [
                async_send_to_location.s(
                    **{
                        "user_id": get_current_user().pk,
                        "movement_id": self.pk,
                        "opts": opts,
                    }
                )
                for opts in iterator(queryset)
            ]
        )()

    def get_location_origin(self):
        location_origin = None

        if self.lotacao_destino:
            location_origin = self.lotacao_destino
        elif employee_from_user(get_current_user()).work_locations.exists():
            location_origin = employee_from_user(
                get_current_user()
            ).work_locations.first()
        elif employee_from_user(
            get_current_user()
        ).work_assignment_effective_exercise.exists():
            location_origin = (
                employee_from_user(get_current_user())
                .work_assignment_effective_exercise.first()
                .lotacao
            )

        return location_origin

    def do_send(
        self,
        person_destination=None,
        location_destination=None,
        group_person=None,
        group_location=None,
        employee_origin=None,
        references="{}",
        attachments="{}",
        advice="",
        opinion=False,
        urgency=False,
        close=False,
        reopen=False,
        physical=False,
        with_workflow=False,
        confidential=None,
        use_async=False,
    ):
        from edocs.protocolo.task.dispatch import async_dispatch_envelop

        person_destination = person_destination or []
        location_destination = location_destination or []
        group_person = group_person or []
        group_location = group_location or []

        if not self.protocolo.can_read:
            raise Exception(
                "Não foi possível concluir a ação pois você não tem acesso ao conteúdo sigiloso."
            )

        with_workflow = True if self.with_workflow else with_workflow

        person_destination = grant_list(person_destination)

        if (
            close or reopen
        ) and self.protocolo.interessado.pk not in person_destination:
            person_destination.append(self.protocolo.interessado.pk)

        self.validate_possession_for_do_send()
        self.validate_destinations(
            person_destination, location_destination, group_person, group_location
        )

        if close or reopen:
            send_by = str(employee_from_user(get_current_user()).pessoa_fisica)
            send_by += (
                (" - %s" % str(self.lotacao_destino)) if self.lotacao_destino else ""
            )

            if not advice and close:
                advice = "Movimentação finalizada por %s em %s." % (
                    send_by,
                    DateUtils.datetime_to_str(datetime.now()),
                )
            elif not advice and reopen:
                advice = "Protocolo reaberto por %s em %s." % (
                    send_by,
                    DateUtils.datetime_to_str(datetime.now()),
                )

        location_origin = self.get_location_origin()

        if not location_origin:
            departament = "RH - 63 32167565."
            if get_current_user().servidor.membro:
                departament = "EXPEDIENTE - 63 32167538."
            raise Exception(
                "Não foi possível encontrar uma lotação ativa. Por favor, entre em contato com %s"
                % departament
            )

        employee_sender = (
            employee_origin
            if employee_origin
            else employee_from_user(get_current_user())
        )
        confidential = self.protocolo.sigiloso if confidential is None else confidential

        with transaction.atomic():
            self.validate_not_send(reopen=reopen)
            envelop = Envelop.factory(
                movement=self,
                **{
                    "employee_origin": employee_sender,
                    "references": references,
                    "attachments": attachments,
                    "advice": advice,
                    "opinion": opinion,
                    "close": close,
                    "reopen": reopen,
                    "urgency": urgency,
                    "physical": physical,
                    "with_workflow": with_workflow,
                    "confidential": confidential,
                    "location_origin": location_origin,
                },
            )

            for pk in grant_list(person_destination):
                person = Pessoa.objects.get(pk=pk)
                self.validate_person_disabled(person, close)

                person_destination = PersonDestination.objects.create(
                    person=person, envelop=envelop
                )

            for pk in grant_list(group_person):
                group = GroupPerson.objects.get(pk=pk)
                log.debug(["group person", group])
                for person in group.destinations.all():
                    person_destination = PersonDestination.objects.create(
                        person=person, envelop=envelop
                    )
                    log.debug(["result", person, envelop.pk])

            for pk in grant_list(location_destination):
                location = OrgaoGeral.objects.get(pk=pk)
                self.validate_general_organ_disabled(location)

                location_destination = LocationDestination.objects.create(
                    general_organ=location, envelop=envelop
                )

            for pk in grant_list(group_location):
                group = GroupGeneralOrgan.objects.get(pk=pk)
                for general_organ in group.destinations.all():
                    destination = LocationDestination.objects.create(
                        general_organ=general_organ, envelop=envelop
                    )

            if not use_async:
                envelop.dispatch()
            else:
                transaction.on_commit(lambda: async_dispatch_envelop.delay(envelop.pk))

    def _do_send_to(
        self,
        location_origin,
        person,
        location,
        employee_origin=None,
        references="{}",
        attachments="{}",
        advice="",
        opinion=False,
        urgency=False,
        close=False,
        reopen=False,
        physical=False,
        with_workflow=False,
        confidential=False,
    ):

        employee_sender = (
            employee_origin
            if employee_origin
            else employee_from_user(get_current_user())
        )

        dispatch = Movimentacao(
            protocolo=self.protocolo,
            lotacao_origem=location_origin,
            lotacao_destino=location,
            servidor_origem=employee_sender,
            servidor_destino=None,
            destinatario=person,
            data_encaminhamento=datetime.now(),
            deferido=opinion,
            parecer=advice,
            urgente=urgency,
            data_finalizado=datetime.now() if close else None,
            passo=None,
            data_recebimento=None,
            child_of=self,
            reopen_by=get_current_user() if reopen else None,
            reopen_at=datetime.now() if reopen else None,
            physical=physical,
            with_workflow=with_workflow,
            confidential=confidential,
        )

        dispatch.save()

        attachments = json.loads(attachments)
        for params in attachments.get("create", []):
            dispatch.do_attach(
                params.get("title"), params.get("attach"), params.get("observation")
            )

        references = json.loads(references)
        for params in references.get("create", []):
            log.debug(json.dumps(params, indent=4))
            dispatch.do_reference(params.get("protocolo"), params.get("observation"))

        if len(attachments) > 0 or len(references) > 0:
            dispatch.protocolo.cache_rendered = None
            dispatch.protocolo.cache_rendered = self.protocolo.rendered_content
            dispatch.protocolo.save()

        dispatch.cache_rendered = None
        dispatch.cache_rendered = dispatch.rendered
        if dispatch.deferido:
            MovimentLegalSign.sign(dispatch)
        dispatch.save()

    def do_attach(self, title, attach, observation):
        self.attachments.add(
            Attachment(
                title=title,
                attach=Arquivo.objects.get(pk=attach),
                observation=observation,
            ),
            bulk=False,
        )

    def do_reference(self, protocol, observation):
        if protocol:
            self.referencia_set.add(
                Referencia(
                    protocolo=Protocolo.objects.get(pk=protocol),
                    observation=observation,
                ),
                bulk=False,
            )

    @property
    def can_close_protocol(self):
        return self.inbox_queryset().filter(pk=self.pk).exists()

    @property
    def can_reopen_close_protocol(self):
        return (
            self.closedbox_queryset().filter(pk=self.pk).exists()
            and self.protocolo.interessado
            == employee_from_user(get_current_user()).pessoa_fisica.pessoa_ptr
        )

    @deprecated
    def close_protocol(self):
        if not self.can_close_protocol:
            raise Exception(
                "Você não pode finalizar o protocolo %s." % self.protocolo.codigo
            )
        MovimentacaoManager.finalizar(self, employee_from_user(get_current_user()))
        self.protocolo.data_finalizado = datetime.now()
        self.protocolo.save()

    def undo_close(self):
        """
        Este método é responsável por finalizar o Protocolo enviando apenas para o interessado.
        A movimentação já deve estar previamente recebida.
        """
        if not self.can_reopen_close_protocol:
            raise Exception(
                "Apenas o interessado pode reabrir o protocolo %s."
                % self.protocolo.codigo
            )
        if not self.protocolo.data_finalizado:
            raise Exception(
                "O protocolo %s não está finalizado." % self.protocolo.codigo
            )

        self.do_send(
            person_destination=[],
            location_destination=[],
            references='{"create":[],"update":[],"delete":[]}',
            attachments='{"create":[],"update":[],"delete":[]}',
            advice="",
            opinion=False,
            urgency=False,
            close=False,
            reopen=True,
        )

    def do_close(self):
        """
        Este método é responsável por finalizar o Protocolo enviando apenas para o interessado.
        A movimentação já deve estar previamente recebida.
        """
        if not self.can_close_protocol:
            raise Exception(
                "Você não pode finalizar o protocolo %s." % self.protocolo.codigo
            )

        self.do_send(
            person_destination=[],
            location_destination=[],
            references='{"create":[],"update":[],"delete":[]}',
            attachments='{"create":[],"update":[],"delete":[]}',
            advice="",
            opinion=False,
            urgency=False,
            close=True,
        )

    @classmethod
    def closedbox_queryset(klass):
        from edocs.protocolo.utils import EDOCBoxQuery

        employee = employee_from_user(get_current_user())
        work_locations_effective_exercise = employee.work_locations_effective_exercise
        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk") for row in work_locations_effective_exercise.values("pk")
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
    def outbox_queryset(klass):
        from edocs.protocolo.utils import EDOCBoxQuery

        employee = employee_from_user(get_current_user())
        work_locations_effective_exercise = employee.work_locations_effective_exercise
        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk") for row in work_locations_effective_exercise.values("pk")
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
    def inbox_queryset(klass):
        from edocs.protocolo.utils import EDOCBoxQuery

        employee = employee_from_user(get_current_user())
        if not employee:
            return Movimentacao.objects.none()

        work_locations_effective_exercise = employee.work_locations_effective_exercise
        box_params = {
            "servidor": employee,
            "lotacoes": [
                row.get("pk") for row in work_locations_effective_exercise.values("pk")
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

    @property
    def is_received(self):
        return not self.can_receive

    @property
    def can_receive(self):
        """A movimentação pode ser recebida?"""
        is_inside_the_inbox = self.inbox_queryset().filter(pk=self.pk).exists()
        is_inside_the_closedbox = self.closedbox_queryset().filter(pk=self.pk).exists()
        return not self.data_recebimento and (
            is_inside_the_inbox or is_inside_the_closedbox
        )

    @property
    def can_unreceive(self):
        return (
            not self.can_receive and self.inbox_queryset().filter(pk=self.pk).exists()
        )

    def sign_document(self):
        if not self.is_received:
            self.sign_received()

        protocol = self.protocolo
        protocol.sign_document()

    def sign_received(self):
        """Marca a movimentação como recebida"""
        if not self.can_receive:
            raise Exception(
                'Não posso receber o movimento do protocolo "%s", pois já foi recebido.'
                % self.protocolo.codigo
            )
        else:
            self.servidor_destino = employee_from_user(get_current_user())
            self.data_recebimento = datetime.now()
            self.save()
            self.invalidate_received_cache()

    def sign_unreceived(self):
        if not self.can_unreceive:
            raise Exception(
                'Não posso mais desfazer o recebimento do protocolo "%s".'
                % self.protocolo.codigo
            )
        else:
            self.servidor_destino = None
            self.data_recebimento = None
            self.save()
            self.invalidate_received_cache()

    @property
    def custo_passo(self):
        return self.protocolo.custo_passo(self.passo)

    def __str__(self):
        return "{0}".format(self.protocolo)

    def next_step(self):
        query = self.protocolo.movimentacoes.order_by("passo")
        if self.pk:
            query = query.exclude(pk=self.pk)

        return (query.last().passo + 1) if query.exists() else 0

    def save(self, *args, **kwargs):
        if not self.pk and not self.passo:
            self.passo = self.next_step()

        self.protocolo.refresh_from_db()
        if not self.protocolo.cache_rendered and self.passo > 0:
            self.protocolo.cache_rendered = self.protocolo.rendered_content
        elif self.passo == 0:
            self.protocolo.cache_rendered = None

        self.protocolo.save()

        super(Movimentacao, self).save(*args, **kwargs)

        try:
            if os.path.exists(self.protocolo.appends_of_document_cachefile):
                os.unlink(self.protocolo.appends_of_document_cachefile)
        except Exception as e:
            log.exception(e)

    def delete(self, *args, **kwags):
        if self.derivative_for.exists():
            raise Exception(
                "Não é possível remover uma movimentação que possui derivações!"
            )
        super(Movimentacao, self).delete(*args, **kwags)

    @classmethod
    def criar_movimentacao(cls, kwargs):
        """
        Este método é responsável por movimentar um Protocolo.
        OBS: Este método não atualiza a movimentação de origem para o status de encaminhado=True.
        A lotacao_criacao só marcada caso o protocolo seja criado em uma lotação que
        possua propriedade de protocolo geral.
        @param Protocolo - protocolo.
        @param OrgaoGeral - orgao_geral_origem, instância da lotação que está enviando.
        @param OrgaoGeral - orgao_geral_destino, instância da lotação que está recebendo.
        @param Servidor - servidor_origem, servidor que está enviando.
        @param boolean - deferido.
        @param data_encaminhamento - data e hora de encaminhamento.
        @param text - parecer, parecer de envio.
        @param boolean - urgente.
        @param Pessoa - Destinatario.
        @param data_finalizado - data e hora de finalização.
        """

        try:
            with transaction.atomic():
                if "data_recebimento" not in kwargs:
                    kwargs.update({"data_recebimento": None})

                protocolo = kwargs.get("protocolo", None)
                lotacao_origem = kwargs.get("orgao_geral_origem", None)
                lotacao_origem = (
                    OrgaoGeral.objects.get(pk=lotacao_origem)
                    if lotacao_origem
                    else lotacao_origem
                )
                lotacao_destino = kwargs.get("orgao_geral_destino", None)

                def get_servidor(pk):
                    return Servidor.objects.get(pk=pk) if pk else None

                servidor_origem = kwargs.get("servidor_origem", None)
                servidor_origem = (
                    servidor_origem
                    if isinstance(servidor_origem, Servidor)
                    else get_servidor(servidor_origem)
                )
                servidor = servidor_origem
                servidor_destino = kwargs.get("servidor_destino", None)
                servidor_destino = (
                    servidor_destino
                    if isinstance(servidor_destino, Servidor)
                    else get_servidor(servidor_destino)
                )

                """
                FIXME: para manter a compatibilidade o servidor_origem será convertido no dicionario para inteiro
                """
                kwargs.update(servidor_origem=servidor_origem.pk)

                destinatario = kwargs.get("destinatario", None)
                lotacao_criacao = (
                    OrgaoGeral.objects.get(pk=int(kwargs.get("lotacao_criacao")))
                    if not kwargs.get("lotacao_criacao") is None
                    and kwargs.get("lotacao_criacao") != ""
                    else None
                )
                if not lotacao_criacao and lotacao_origem:
                    lotacao_criacao = (
                        ProtocoloManager.get_lotacao_criacao(servidor.pk)
                        if Movimentacao.objects.filter(protocolo=protocolo.pk).exists()
                        == 0
                        else None
                    )
                    cls.validacao_criar_movimentacao(kwargs)

                Movimentacao(
                    protocolo=protocolo,
                    lotacao_criacao=lotacao_criacao,
                    lotacao_origem=lotacao_origem,
                    lotacao_destino=(
                        OrgaoGeral.objects.get(pk=lotacao_destino)
                        if lotacao_destino
                        else lotacao_destino
                    ),
                    servidor_origem=servidor_origem,
                    servidor_destino=servidor_destino,
                    destinatario=(
                        destinatario
                        if destinatario is None or destinatario == "None"
                        else Pessoa.objects.get(pk=destinatario)
                    ),
                    data_encaminhamento=kwargs.get(
                        "data_encaminhamento", datetime.now()
                    ),
                    deferido=kwargs.get("deferido"),
                    parecer=kwargs.get("parecer"),
                    urgente=kwargs.get("urgente", False),
                    data_finalizado=kwargs.get("data_finalizado"),
                    passo=kwargs.get("passo", None),
                    data_recebimento=kwargs.get("data_recebimento", None),
                    confidential=protocolo.sigiloso,
                ).save()
        except Exception as err:
            log.exception(err)
            log_LineLog(level=70, status=0, kwargs=kwargs)
            raise err

        log_LineLog(level=70, status=1, kwargs=kwargs)

    @classmethod
    def validacao_criar_movimentacao(cls, kwargs):
        if "protocolo" not in kwargs:
            raise Exception("O protocolo é obrigatório!")
        if "orgao_geral_origem" not in kwargs:
            raise Exception("O órgão geral de origem é obrigatório!")
        if "servidor_origem" not in kwargs:
            raise Exception("O servidor de origem é obrigatório!")
        if "destinatario" not in kwargs and "orgao_geral_destino" not in kwargs:
            raise Exception(
                "O destinatário ou órgão geral de destino deve ser preenchido!"
            )

    @property
    def sender_of_movement(self):
        return (
            self.derivative_for.first().servidor_origem.pessoa_fisica
            if self.has_child
            else self.servidor_origem.pessoa_fisica
        )

    @property
    def workplace_sender(self):
        return (
            self.derivative_for.first().lotacao_origem
            if self.has_child
            else self.lotacao_origem
        )

    @property
    def child_of_movement(self):
        return self.derivative_for.filter().order_by("lotacao_destino", "destinatario")

    @classmethod
    def edoc_detail(cls, **kargs):
        buf = "ID|ID DA ORIGEM|N DO PROTOCOLO|ASSUNTO|AREA ORGANIZACIONAL(ponto inicial)|INTERESSADO|TRANSITO - ORIGEM|TRANSITO - SERVIDOR ORIGEM|TRANSITO - LOCAL DESTINO|TRANSITO - SERVIDOR DESTINO|TRANSITO - QUEM RECEBEU|DATA CHEGADA|DATA RECEBIMENTO|DATA SAIDA|DATA FINALIZACAO|PERMANENCIA(8 horas como jornada)|PERMANENCIA - HORAS UTEIS(8 horas como jornada)|CHEGOU FINALIZADA\n"
        workplace_origin = kargs.get("workplace_origin")
        workplace_destination = kargs.get("workplace_destination")

        feedback = kargs.get(
            "feedback", (lambda progress_message, progress, **kargs: False)
        )

        if kargs.get("user"):
            set_current_user(kargs.get("user"))
        else:
            raise Exception("Não existe usuário logado.")

        protocol_pks = []

        if workplace_origin:
            protocol_pks += [
                pk[0]
                for pk in Movimentacao.objects.filter(
                    lotacao_origem__pk=workplace_origin
                ).values_list("protocolo__pk")
            ]

        if workplace_destination:
            protocol_pks += [
                pk[0]
                for pk in Movimentacao.objects.filter(
                    lotacao_destino__pk=workplace_destination
                ).values_list("protocolo__pk")
            ]

        inbox = Movimentacao.inbox_queryset()
        outbox = Movimentacao.outbox_queryset()
        closedbox = Movimentacao.closedbox_queryset()

        protocol_pks_found = []
        protocol_pks_found += [
            pk[0]
            for pk in inbox.filter(protocolo__pk__in=protocol_pks).values_list(
                "protocolo__pk"
            )
        ]
        protocol_pks_found += [
            pk[0]
            for pk in outbox.filter(protocolo__pk__in=protocol_pks).values_list(
                "protocolo__pk"
            )
        ]
        protocol_pks_found += [
            pk[0]
            for pk in closedbox.filter(protocolo__pk__in=protocol_pks).values_list(
                "protocolo__pk"
            )
        ]

        qname = (
            Q(protocolo__pk__in=protocol_pks_found)
            & Q(with_workflow=False)
            & Q(protocolo__processo=None)
        )

        query = Movimentacao.objects.filter(qname).exclude(passo=0)

        if kargs.get("finalized", 1) == 2:
            query = query.filter(~Q(protocolo__data_finalizado=None))
        elif kargs.get("finalized", 1) == 3:
            query = query.filter(protocolo__data_finalizado=None)

        if kargs.get("subject"):
            query = query.filter(protocolo__assunto__icontains=kargs.get("subject"))
        if kargs.get("edoc_code"):
            query = query.filter(protocolo__codigo=kargs.get("edoc_code"))
        if kargs.get("date_created"):
            query = query.annotate(
                date_created=Func(F("protocolo__data_criacao"), function="DATE")
            )
            query = query.filter(
                date_created=DateUtils.str_to_date(kargs.get("date_created"))
            )
        if kargs.get("date_start"):
            query = query.filter(
                data_encaminhamento__gte=DateUtils.str_to_date(kargs.get("date_start"))
            )
        if kargs.get("date_end"):
            query = query.filter(
                data_encaminhamento__lte=DateUtils.str_to_date(kargs.get("date_end"))
            )

        count = 1
        total = query.count()
        limit = 20000
        if total > limit:
            raise Exception(
                "Resultado máximo(%s linhas) excedido. Utilize os campos A partir de e Até para filtrar."
                % limit
            )
        with codecs.open(
            "%s/%s" % (settings.CACHE_PATH, kargs.get("filename", "edoc_detail.csv")),
            "w+a",
            "utf-8",
        ) as fd:
            fd.write(buf)
            for move in query.order_by("protocolo__codigo", "passo"):
                feedback(
                    "%(message_progress)s",
                    progress=((100.0 * float(count)) / float(total)),
                    message_progress="<p>Gerando arquivo, linha %s de %s</p>"
                    % (count, total),
                )
                arrived_at = move.data_encaminhamento
                send_at = move.send_at
                elapsed_time_unicode = "Não foi possível definir"
                try:
                    elapsed_time_unicode, elapsed_time = move.elapsed_time()
                except Exception as err:
                    log.exception(err)
                buf_step = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (
                    move.pk,
                    move.child_of.pk if move.child_of else "",
                    str(move.protocolo.codigo),
                    str(move.protocolo.assunto),
                    str(move.protocolo.orgao_geral_origem),
                    str(move.protocolo.interessado),
                    str(move.lotacao_origem),
                    str(move.servidor_origem),
                    str(move.lotacao_destino or ""),
                    str(move.destinatario or ""),
                    str(move.servidor_destino or ""),
                    DateUtils.datetime_to_str(arrived_at) if arrived_at else "",
                    (
                        DateUtils.datetime_to_str(move.data_recebimento)
                        if move.data_recebimento
                        else ""
                    ),
                    DateUtils.datetime_to_str(send_at) if send_at else "",
                    (
                        DateUtils.datetime_to_str(move.data_finalizado)
                        if move.data_finalizado
                        else ""
                    ),
                    elapsed_time_unicode,
                    elapsed_time,
                    "SIM" if move.data_finalizado else "NÃO",
                )
                log.info("writting...%s of %s" % (count, total))
                fd.write(buf_step)
                count += 1
        feedback(
            "%(message_progress)s",
            progress=((100.0 * float(count)) / float(total)) if total else 100,
            message_progress="<p>Gerando arquivo ...%s -> %s</p>"
            % (count if total else total, total),
        )

    def business_time(self, date_start=None, date_end=None):
        if not date_start:
            date_start = self.data_encaminhamento
        if not date_end:
            date_end = self.send_at
            if not date_end:
                date_end = datetime.now()
        return DateUtils.tempo_de_expediente(date_start, date_end)

    def elapsed_time(self, date_start=None, date_end=None):
        business_time = self.business_time(date_start=date_start, date_end=date_end)
        elapsed = relativedelta(days=business_time.days, seconds=business_time.seconds)
        # Um dia de 24 horas contém 3 dias de expediente
        elapsed.days = elapsed.days * 3
        # Converte as horas excedentes para dia de expediente
        elapsed.days = elapsed.days + int(elapsed.hours / 8)
        elapsed.hours = elapsed.hours % 8
        days = str(elapsed.days) + "d " if elapsed.days > 0 else ""
        hours = str(elapsed.hours) + "h " if elapsed.hours > 0 else ""
        minutes = str(elapsed.minutes) + "min" if elapsed.minutes > 0 else ""
        res_hours = 0
        if elapsed.days > 0:
            res_hours += elapsed.days * 8
        if elapsed.hours > 0:
            res_hours += elapsed.hours
        if elapsed.minutes > 0:
            res_hours += float(elapsed.minutes) / float(60)
        return days + hours + minutes, res_hours

    def is_personal_sending(self):
        """Verifica se o movimento foi destinado a uma pessoa e não a uma lotação."""
        return True if self.destinatario else False

    def is_unique_exercise(self):
        """Verifica se é quem vai receber possui apenas uma lotação ativa."""
        employee = employee_from_user(get_current_user())
        log.info(employee.work_locations_effective_exercise.count())
        return True if employee.work_locations_effective_exercise.count() < 2 else False


class Attachment(AuditTimestampModel):
    moviment = models.ForeignKey(
        Movimentacao, related_name="attachments", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    protocol = models.ForeignKey(
        Protocolo,
        related_name="attachments",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    title = models.CharField(max_length=260, blank=False)
    attach = models.ForeignKey(
        Arquivo, related_name="+", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    observation = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("title",)

    def save(self, *args, **kwags):
        if self.moviment:
            self.protocol = self.moviment.protocolo

        if self.title == "":
            self.title = self.attach.filename

        super(Attachment, self).save(*args, **kwags)


class Impressora(AuditTimestampModel):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    driver = models.SmallIntegerField(
        choices=standard_models.Choice.get_choices_for("protocolo", "PRINTER_DRIVER"),
        default=1,
        verbose_name="Tipo da Impressora",
    )
    lotacao = models.ForeignKey(
        Lotacao, verbose_name="Localização", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    host = models.CharField(max_length=100, verbose_name="Endereço")
    port = models.IntegerField(verbose_name="Porta")

    def __str__(self):
        return " - ".join([self.nome, str(self.lotacao)])


class EDOCBoxManager:

    @classmethod
    def remove_lotacao_da_pessoa(cls, lotacao_pessoa, lotacao_destino):
        """
        Este método remove todas lotações que se relacionam com Pessoa, para que ela não receba um documento duas vezes.
        @param list - Lista de lotações das pessoas.
        @return list - Lista com o(s) pk(s).
        """
        lotacoes_destino = lotacao_destino
        if lotacoes_destino:
            for l in lotacao_pessoa:
                if l in lotacoes_destino:
                    lotacoes_destino.remove(lotacoes_destino.index(str(l)))
        return lotacoes_destino

    @classmethod
    def is_lotacoes_em_organograma(cls, lotacoes_destino):
        """
        Este método verifica se as lotações estão no organograma.
        Apresenta exceção caso as lotações não estejam no organograma.
        """
        general_organ = OrgaoGeral.objects.filter(
            Q(pk__in=lotacoes_destino) & Q(habilita_protocolo=False)
        )
        if general_organ.exists():
            raise Exception(
                "Não movimentado! Lotação(ões) não autorizado para envio! %s"
                % general_organ.latest("pk")
            )
        return True

    @classmethod
    def is_destino(cls, lotacoes_destino, pessoa_lotacoes, servidor_lotacoes):
        """
        Este método verifica se existe destinos definidos para a movimentação.
        Apresenta exceção caso nenhum destino seja encontrado.
        """
        if not lotacoes_destino and not pessoa_lotacoes and not servidor_lotacoes:
            raise Exception(
                "Problemas na movimentação, destino não encontrado! \nTente outra vez!"
            )
        return True


class LegalSign(models.Model):
    who = models.ForeignKey(
        User, related_name="sign_documents", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    when = models.DateTimeField()
    plain_content = models.TextField()
    content = models.TextField()
    content_sign = models.CharField(max_length=100, db_index=True)
    invalidated_at = models.DateTimeField(null=True, blank=True)
    invalidated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="sign_invalided_documents",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    @property
    def qrcode(self):
        pass
        # import pyqrcode
        # import io
        # import base64

        # tag = pyqrcode.create(self.permalink)
        # data = io.BytesIO()
        # tag.png(data, scale=2)

        # return base64.b64encode(data.getvalue()).decode()

    @property
    def who_person(self):
        if employee_from_user(self.who, False):
            return str(employee_from_user(self.who, False).pessoa_fisica)
        else:
            return (
                self.who.get_full_name()
                if self.who.get_full_name()
                else self.who.username
            )

    def _fill(self):
        self.who = get_current_user()
        self.when = datetime.now()

    @property
    def permalink(self):
        return "https://%s/%s/portal/servicos/checar-assinatura/%s" % (
            getattr(settings, "WEB_DOMAIN", "mpto.mp.br"),
            getattr(settings, "WEB_CONTEXT", "web"),
            self.content_sign,
        )

    @classmethod
    def sign(klass):
        raise Exception("Abstract method")

    @classmethod
    def remove_signatures(cls):
        raise Exception("Abstract method")


class MovimentLegalSign(LegalSign):
    moviment = models.ForeignKey(
        Movimentacao, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, moviment):
        LegalSign._fill(self)
        log.debug("Fill with moviment %s", moviment)
        self.moviment = moviment
        self.plain_content = self.moviment.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha1", self.content).hexdigest()

    @classmethod
    def sign(klass, moviment):
        log.debug("Sign moviment %s", moviment)

        obj = klass()
        obj._fill(moviment)

        log.debug(obj.moviment)

        obj.save()


class ProtocolLegalSign(LegalSign):
    protocol = models.ForeignKey(
        Protocolo, related_name="legal_signs", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _fill(self, protocol):
        LegalSign._fill(self)
        self.protocol = protocol
        self.plain_content = self.protocol.rendered
        self.content = b64encode(self.plain_content.encode("utf-8"))
        self.content_sign = hashlib.new("sha1", self.content).hexdigest()

    def _disable(self):
        self.invalidated_at = datetime.now()
        self.invalidated_by = get_current_user()
        self.save()

    def _invalid_signature(self, protocol, all_of=False):
        query = Q(who=get_current_user(), invalidated_at=None)

        if all_of:
            query = Q(invalidated_at=None)

        for sign in protocol.legal_signs.filter(query):
            sign._disable()

    @classmethod
    def sign(klass, protocol):
        obj = klass()
        obj._invalid_signature(protocol)
        obj._fill(protocol)
        obj.save()

        protocol.cache_rendered = None
        protocol.save()

    @classmethod
    def remove_signatures(cls, protocol):
        obj = cls()
        obj._invalid_signature(protocol, all_of=True)


class GroupPerson(models.Model):
    """
    Esse Modelo define listas de distribuição que serão utilizadas para envio de documentos via aplicação e-docs
    """

    title = models.CharField(max_length=100, verbose_name="Título")
    persons = models.ManyToManyField(
        Pessoa, related_name="in_group_person", verbose_name="Pessoas"
    )
    level_access = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("protocolo", "LEVEL_ACCESS"),
        verbose_name="Acesso",
    )
    department = models.ForeignKey(
        Lotacao,
        on_delete=models.CASCADE,
        related_name="group_person",
        verbose_name="Departamento",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)
    all_employees = models.BooleanField(default=False, verbose_name="Servidores")
    all_members = models.BooleanField(default=False, verbose_name="Membros")
    all_prosecutors = models.BooleanField(default=False, verbose_name="Promotores")
    all_attorneys = models.BooleanField(default=False, verbose_name="Procuradores")
    locality = models.ForeignKey(
        Localidade,
        on_delete=models.CASCADE,
        related_name="group_person",
        verbose_name="Localidade",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        verbose_name = "Grupo de Pessoas"
        ordering = ["title"]
        permissions = (
            (
                "group_person_admin_global_distribution",
                "Pode administrar lista de distribuição global",
            ),
        )

    def __str__(self):
        return "%s" % self.title

    @property
    def destinations(self):
        query_part = []

        if self.persons.all().exists():
            query_part.append(models.Q(pk__in=self.persons.all()))

        if self.all_employees:
            query_part.append(
                models.Q(
                    pk__in=Pessoa.objects.filter(
                        pessoafisica__servidor__ativo=True,
                        pessoafisica__servidor__tipo="S",
                    ).values("pk")
                )
            )

        if self.all_members:
            query_part.append(
                models.Q(
                    pk__in=Pessoa.objects.filter(
                        pessoafisica__servidor__ativo=True,
                        pessoafisica__servidor__tipo="M",
                    ).values("pk")
                )
            )

        if self.all_prosecutors:
            query_part.append(
                models.Q(
                    pk__in=Servidor.objects.filter(
                        movimentacaopessoal__movimentacaoposse__quadro__cargo__configs__cbo__codigo=242235,
                        ativo=True,
                        movimentacaopessoal__movimentacaoposse__ativo=True,
                        movimentacaopessoal__movimentacaoposse__quadro__cargo__tipo_lei_cargo="EF",
                    )
                    .distinct()
                    .values("pessoa_fisica__pk")
                )
            )

        if self.all_attorneys:
            query_part.append(
                models.Q(
                    pk__in=Servidor.objects.filter(
                        movimentacaopessoal__movimentacaoposse__quadro__cargo__configs__cbo__codigo=242210,
                        ativo=True,
                        movimentacaopessoal__movimentacaoposse__ativo=True,
                        movimentacaopessoal__movimentacaoposse__quadro__cargo__tipo_lei_cargo="EF",
                    )
                    .distinct()
                    .values("pessoa_fisica__pk")
                )
            )

        query = None
        if query_part:
            for part in query_part:
                query = part if not query else part | query
        else:
            query = models.Q(pk=0)

        query = Pessoa.objects.filter(query).exclude(enable_protocol=False)

        if self.locality:
            query = query.filter(
                pessoafisica__servidor__servidor_lotacao__lotacao__localidade=self.locality,
                pessoafisica__servidor__servidor_lotacao__designacao=True,
                pessoafisica__servidor__servidor_lotacao__ativo=True,
            )

        return Pessoa.objects.filter(pk__in=query.values("pk"))

    def _validate(self):
        self._validate_permission()
        self._validade_fields()

    def _validate_permission(self):
        older = self.__class__.objects.get(pk=self.pk) if self.pk else None
        self.level_access = int(self.level_access or 0)
        user = get_current_user()

        if (
            older
            and older.level_access == 1
            and not user.has_perm("protocolo.group_person_admin_global_distribution")
        ):
            raise Exception("Você não pode administrar listas de distribuição global.")
        elif self.level_access == 1 and not user.has_perm(
            "protocolo.group_person_admin_global_distribution"
        ):
            raise Exception("Você não pode administrar listas de distribuição global.")

        self.department = None if self.level_access == 1 else self.department

        if self.level_access == 2 and not self.department:
            raise Exception(
                "Quando o nivel de acesso for departamental o campo departamento é obrigatório."
            )

    def _validade_fields(self):
        if not self.title:
            raise Exception("Você deve informar um título para a lista.")

        if self.level_access == 0:
            raise Exception("Você deve escolher um nível de acesso.")

    def save(self, *args, **kwags):
        self._validate()
        super(GroupPerson, self).save(*args, **kwags)

    def delete(self, *args, **kwags):
        user = get_current_user()

        if int(self.level_access | 0) == 1 and not user.has_perm(
            "protocolo.group_person_admin_global_distribution"
        ):
            raise Exception("Você não tem permissão para remover um lista global.")

        super(GroupPerson, self).delete(*args, **kwags)


class GroupGeneralOrgan(models.Model):
    """ """

    title = models.CharField(max_length=100, verbose_name="Título")
    general_organ = models.ManyToManyField(
        OrgaoGeral, related_name="in_group_general_organ", verbose_name="Orgão Geral"
    )
    level_access = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("protocolo", "LEVEL_ACCESS"),
        verbose_name="Acesso",
    )
    department = models.ForeignKey(
        Lotacao,
        on_delete=models.CASCADE,
        related_name="group_general_organ",
        verbose_name="Departamento",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)

    all_work_location = models.BooleanField(
        default=False, verbose_name="Todos Locais de Trabalho"
    )

    class Meta:
        verbose_name = "Grupo de Órgão Geral"
        ordering = ["title"]
        permissions = (
            (
                "group_general_organ_admin_global_distribution",
                "Pode administrar lista de distribuição global",
            ),
        )

    def __str__(self):
        return "%s" % self.title

    @property
    def destinations(self):
        query_part = []

        if self.general_organ.all().exists():
            query_part.append(models.Q(pk__in=self.general_organ.all()))

        if self.all_work_location:
            query_part.append(
                models.Q(pk__in=OrgaoGeral.objects.exclude(lotacao=None).values("pk"))
            )

        query = None
        if query_part:
            for part in query_part:
                query = part if not query else part | query
        else:
            query = models.Q(pk=0)

        return OrgaoGeral.objects.filter(query).exclude(habilita_protocolo=False)

    def _validate(self):
        self._validate_permission()
        self._validade_fields()

    def _validate_permission(self):
        older = self.__class__.objects.get(pk=self.pk) if self.pk else None
        self.level_access = int(self.level_access or 0)
        user = get_current_user()

        if (
            older
            and older.level_access == 1
            and not user.has_perm(
                "protocolo.group_general_organ_admin_global_distribution"
            )
        ):
            raise Exception("Você não pode administrar listas de distribuição global.")
        elif self.level_access == 1 and not user.has_perm(
            "protocolo.group_general_organ_admin_global_distribution"
        ):
            raise Exception("Você não pode administrar listas de distribuição global.")

        self.department = None if self.level_access == 1 else self.department

        if self.level_access == 2 and not self.department:
            raise Exception(
                "Quando o nivel de acesso for departamental o campo departamento é obrigatório."
            )

    def _validade_fields(self):
        if not self.title:
            raise Exception("Você deve informar um título para a lista.")

        if self.level_access == 0:
            raise Exception("Você deve escolher um nível de acesso.")

    def save(self, *args, **kwags):
        self._validate()
        super(GroupGeneralOrgan, self).save(*args, **kwags)

    def delete(self, *args, **kwags):
        user = get_current_user()

        if int(self.level_access | 0) == 1 and not user.has_perm(
            "protocolo.group_general_organ_admin_global_distribution"
        ):
            raise Exception("Você não tem permissão para remover um lista global.")

        super(GroupGeneralOrgan, self).delete(*args, **kwags)


class Envelop(AuditTimestampModel):
    PENDENT, IN_DELIVERY, FINISHED, EMPTY = range(1, 5)
    delivery_state = models.SmallIntegerField(
        choices=(
            (PENDENT, "pendent"),
            (IN_DELIVERY, "in-delivery"),
            (FINISHED, "finished"),
            (EMPTY, "empty"),
        ),
        default=PENDENT,
    )
    movement = models.ForeignKey(
        Movimentacao, related_name="envelops", on_delete=models.CASCADE
    )
    employee_origin = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    references = models.TextField()
    attachments = models.TextField()
    advice = models.TextField()
    urgency = models.BooleanField(default=False)
    opinion = models.BooleanField(default=False)
    close = models.BooleanField(default=False)
    reopen = models.BooleanField(default=False)
    physical = models.BooleanField(default=False)
    with_workflow = models.BooleanField(default=False)
    confidential = models.BooleanField(default=None)
    finished_at = models.DateTimeField(null=True)
    location_origin = models.ForeignKey(
        OrgaoGeral, related_name="lotacao_origem", on_delete=models.CASCADE
    )

    class DuplicatedOpenEnvelopError(Exception):

        def __init__(self, movement):
            super().__init__(
                "O protocolo %s já foi movimentado." % movement.protocolo.codigo
            )

    def __str__(self):
        return "Passo %d do protocolo %s" % (
            self.movement.passo,
            self.movement.protocolo.codigo,
        )

    @classmethod
    def factory(cls, movement, **options):
        query = Envelop.objects.filter(movement=movement)
        query = query.exclude(delivery_state__in=[cls.FINISHED, cls.EMPTY])

        if query.exists():
            raise cls.DuplicatedOpenEnvelopError(movement)

        return cls.objects.create(movement=movement, **options)

    def _fill_attachments(self, movement):
        for params in json.loads(self.attachments).get("create", []):
            if params.get("attach"):
                movement.do_attach(
                    params.get("title"), params.get("attach"), params.get("observation")
                )

    def _fill_references(self, movement):
        for params in json.loads(self.references).get("create", []):
            movement.do_reference(params.get("protocolo"), params.get("observation"))

    def _factory_movement(self, destination):
        return Movimentacao.objects.create(
            protocolo=self.movement.protocolo,
            lotacao_origem=self.location_origin,
            lotacao_destino=getattr(destination, "general_organ", None),
            servidor_origem=self.employee_origin,
            servidor_destino=None,
            destinatario=getattr(destination, "person", None),
            data_encaminhamento=datetime.now(),
            deferido=self.opinion,
            parecer=self.advice,
            urgente=self.urgency,
            data_finalizado=datetime.now() if self.close else None,
            passo=None,
            data_recebimento=None,
            child_of=self.movement,
            reopen_by=get_current_user() if self.reopen else None,
            reopen_at=datetime.now() if self.reopen else None,
            physical=self.physical,
            with_workflow=self.with_workflow,
            confidential=self.confidential,
        )

    def _rebuild_cache(self):
        protocol_cache_build = import_module(
            "edocs.protocolo.task.dispatch"
        ).async_protocol_cache_build

        self.movement.invalidate_cache()
        protocol = self.movement.protocolo
        protocol_cache_build(protocol.pk)

    def _notify_dispatch(self):
        who = ""
        if self.movement.destinatario:
            RemoteEmmiter.emmit_for_user(
                self.created_by, "edoc-load-boxes", envelop_id=self.pk
            )
        else:
            RemoteEmmiter.emmit_for_worklocation(
                self.movement.lotacao_destino, "edoc-load-boxes", envelop_id=self.pk
            )

    def _reopen_or_close(self):
        self.movement.protocolo.do_close()

        if self.reopen:
            self.movement.protocolo.do_reopen()
        else:
            self.movement.encaminhado = True
            self.movement.data_finalizado = self.finished_at if self.close else None
            self.movement.save()

    def _update_confidentiality(self):
        if self.confidential is not None:
            self.movement.protocolo.sigiloso = self.confidential
            self.movement.protocolo.save()

    def _update_state(self, new_status):
        self.delivery_state = new_status
        self.save()

    def _mark_as_delivering(self):
        self._update_state(self.IN_DELIVERY)

    def _mark_as_finished(self):
        self.finished_at = datetime.now()
        self._update_state(self.FINISHED)

    def _mark_as_empty(self):
        self._update_state(self.EMPTY)

    @property
    def _has_new_attachments(self):
        return len(json.loads(self.attachments).get("create", []))

    @property
    def _has_new_references(self):
        return len(json.loads(self.references).get("create", []))

    def _update_rendered_content(self):
        if self._has_new_attachments or self._has_new_references:
            protocol = self.movement.protocolo
            protocol.cache_rendered = None
            protocol.cache_rendered = protocol.rendered_content
            protocol.save()

    def _post_dispatch(self):
        self._update_rendered_content()
        self._rebuild_cache()
        self._mark_as_finished()
        self._notify_dispatch()
        self._reopen_or_close()
        self._update_confidentiality()

    def dispatch(self, verbose=False):
        if self.delivery_state not in [Envelop.PENDENT, Envelop.IN_DELIVERY]:
            return

        with transaction.atomic():
            set_current_user(self.created_by)
            self._mark_as_delivering()

            destinations = self.destinations.filter(
                created_movement=None, movement_undone_at=None
            )

            for destination in destinations:
                destination = destination.my_origin
                movement = self._factory_movement(destination)
                movement.cache_rendered = None
                movement.cache_rendered = movement.rendered
                self._fill_attachments(movement)
                self._fill_references(movement)
                if movement.deferido:
                    MovimentLegalSign.sign(movement)
                movement.save()
                destination.created_movement = movement
                destination.save()

            if destinations.exists():
                self._post_dispatch()
            else:
                self._mark_as_empty()


class CommomDestination(models.Model):
    destionation_type = models.CharField(max_length=60, db_index=True, blank=True)
    envelop = models.ForeignKey(
        Envelop, related_name="destinations", on_delete=models.CASCADE
    )
    created_movement = models.ForeignKey(
        Movimentacao,
        related_name="destinations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    movement_undone_at = models.DateTimeField(
        verbose_name="Movimentação desfeita em", null=True, blank=True
    )
    movement_undone_by = models.ForeignKey(
        User,
        verbose_name="Movimentação desfeita por",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.destionation_type):
                return getattr(self, self.destionation_type, self)
            else:
                return self
        else:
            return self

    @property
    def target(self):
        raise NotImplementedError("Not implemented")


class PersonDestination(CommomDestination):
    person = models.ForeignKey(Pessoa, on_delete=models.CASCADE)

    @property
    def target(self):
        return self.person

    def __str__(self):
        return "%s" % (self.person)

    def save(self, *args, **kwargs):
        self.destionation_type = self._meta.model_name
        super().save(*args, **kwargs)


class LocationDestination(CommomDestination):
    general_organ = models.ForeignKey(OrgaoGeral, on_delete=models.CASCADE)

    @property
    def target(self):
        return self.general_organ

    def __str__(self):
        return "%s" % (self.general_organ)

    def save(self, *args, **kwargs):
        self.destionation_type = self._meta.model_name
        super().save(*args, **kwargs)
