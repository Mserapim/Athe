# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes REST para o Edocs - processo.

:Classes:
  :class:`EdocProcesso`.
"""

import xmlrpc.client
from unicodedata import normalize
from datetime import datetime

from django.db.models import Q
from django.http import QueryDict
from django import forms

from contrib.utils import getLogger, DateUtils, employee_from_user
from contrib.newrest import Restful
from contrib import extjs
from rh.models import Pessoa, OrgaoGeral, ServidorLotacao, Lotacao

from standard.models import Configuration

from edocs.protocolo.utils import EDOCBoxQuery
from edocs.protocolo.models import (
    ProtocoloManager,
    MovimentacaoManager,
    TipoDocumento,
    Movimentacao,
    Protocolo,
    EDOCBoxManager,
    Impressora,
)
from edocs.processo.models import (
    Processo,
    Assunto,
    Situacao,
    MovimentacaoProcesso,
    Referencia,
    Justificativa,
)

from contrib.nil import nil_pk, nil_unicode
from edocs.processo.models import ProcessMatter

log = getLogger(__name__)


class EpadProcesso(Restful):

    _model = Processo

    force_upper = False

    full_text_index = (
        "protocolo__processo__codigo_processo__icontains",
        "protocolo__codigo__icontains",
        "protocolo__protocolo_externo__icontains",
        "protocolo__processo__assunto_processo__nome__icontains",
        "servidor_origem__pessoa_fisica__nome__icontains",
        "lotacao_origem__nome__icontains",
        "lotacao_destino__nome__icontains",
        "protocolo__processo__interessados__nome__contains",
    )

    lotacoes = []

    lotacoes_protocolo_geral = []

    servidor = None

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.Manager",{})')

    def fill_instance_m2m(self, instance, values):
        super(EpadProcesso, self).fill_instance_m2m(instance, values)
        # if 'anexos' in values:
        #     field = getattr(instance.movimentacoes.get(passo=0), 'anexos', None)
        #     field.clear()
        #     value = values.get('anexos')
        #     for item in value:
        #         field.add(item)

    def get_params(self, *args, **kargs):
        params = super(EpadProcesso, self).get_params(*args, **kargs)

        log.info(params)

        params.update(servidor_origem=self.get_servidor())
        try:
            params.update(
                interessado=Pessoa.objects.get(pk=int(params.get("interessado", 0)))
            )
        except Exception:
            params.update(interessado=self.get_servidor().pessoa_fisica.pessoa_ptr)
        if "orgao_geral_origem" in params:
            if params.get("orgao_geral_origem", "") == "":
                raise Exception("Favor selecionar uma origem")
            params.update(
                orgao_geral_origem=OrgaoGeral.objects.get(
                    pk=int(params.get("orgao_geral_origem"))
                )
            )
            params.update(
                lotacao_criacao=ProtocoloManager.get_lotacao_criacao(
                    self.get_servidor().pk
                )
            )

        if "interessado" in params and "orgao_geral_origem" in params:
            if (
                params.get("interessado") is None
                or params.get("orgao_geral_origem") is None
            ):
                raise Exception(
                    "Problemas na Criação do Protocolo!\nServidor não encontrado!"
                )

        if "interessados" in params:
            interessados = params.get("interessados", "")
            if interessados == "":
                interessados = []
            else:
                if isinstance(interessados, (list, tuple)) is False:
                    interessados = [interessados]
            params.update(interessados=[Pessoa.objects.get(pk=p) for p in interessados])

        tipo_documento = TipoDocumento.objects.get(pk=37)  # Processo Administrativo
        params.update(tipo_documento=tipo_documento)

        if "assunto_processo" in params:
            params.pop("assunto_processo")

        if "paginas" in params:
            if params.get("paginas", "") == "":
                raise Exception("Favor informar quantidade de páginas")
            try:
                params.update(paginas=int(params.get("paginas")))
            except Exception:
                raise Exception("Página: informe um número válido")

        if "volume" in params:
            if params.get("volume", "") == "":
                raise Exception("Favor informar volume atual")
            try:
                params.update(volume=Processo.roman_to_int(str(params.get("volume"))))
            except Exception:
                raise Exception("Volume: informe um número romano válido")

        if "sigiloso" in params:
            params.update(sigiloso=params.get("sigiloso", "off").lower() == "on")

        if "midia" in params:
            if params.get("midia") == "":
                params.update(midia=None)
            else:
                params.update(midia=int(params.get("midia")))

        if "ano" in params:
            if params.get("ano") == "":
                raise Exception("Ano não foi informado.")
            else:
                params.update(ano=int(params.get("ano")))

        # if 'anexos' in params:
        #     anexos = params.get('anexos', [])
        #     if (anexos == ''):
        #             anexos = []
        #     else:
        #         if type(anexos) not in [list, tuple]:
        #             anexos = [anexos]
        #     params.update(
        #         anexos=[Anexo.objects.get(pk=int(a)) for a in anexos],
        #     )

        if "referencias" in params:
            referencias = params.get("referencias", [])
            if referencias == "":
                referencias = []
            else:
                if isinstance(referencias, (list, tuple)) is False:
                    referencias = [referencias]
            params.update(
                referencias=[Referencia.objects.get(pk=int(r)) for r in referencias],
            )

        if "excluido" in params:
            params.update(excluido=True)

        # params.update(com_workflow=True)

        if "codigo_processo" in params:
            del params["codigo_processo"]

        # log.info(params)
        return params

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        if isinstance(instance, Movimentacao) is True:
            protocolo = instance.protocolo

            ultima_mov = Movimentacao.objects.filter(protocolo=protocolo).order_by(
                "-passo"
            )[0]

            localizacao_atual = (
                str(ultima_mov.destinatario)
                if ultima_mov.destinatario is not None
                else ""
            )
            localizacao_atual = localizacao_atual + " - "
            localizacao_atual = (
                localizacao_atual + str(ultima_mov.lotacao_destino)
                if ultima_mov.lotacao_destino is not None
                else ""
            )

            # Anexos mostrados em 'Window Editar' e 'openWindow'
            # anexos = []
            # for a in instance.attachments.filter():
            #     anexos.append({
            #         'pk': a.pk,
            #         'nome': a.title,
            #         'descricao': a.observation,
            #         'link': a.attach.permalink(),
            #         'enviado_por': unicode(a.created_by),
            #     })
            # Lista de interessados para mostrar em openWindow
            interessados = []
            for i in protocolo.processo.interessados.all():
                interessados.append(
                    {
                        0: i.pk,
                        1: i.nome,
                    }
                )

            dias_criacao_processo = (
                (datetime.now() - protocolo.data_criacao).days
                if protocolo.data_finalizado is None
                else ""
            )

            _dict_.update(
                # Parametros do gridPanel principal e Window Editar / Open
                status={
                    "recebido": MovimentacaoManager.is_recebido(instance),
                    # 'attache': (instance.protocolo.movimentacoes.filter(~Q(anexos=None)).values('anexos').count() > 0),
                    "attache": instance.protocolo.attachments.filter().exists(),
                    "urgente": instance.urgente,
                    "finalizado": (
                        True if ProtocoloManager.is_finalizado(instance) else False
                    ),
                    "compartilhado": False,
                    "locked": False,
                    "encaminhado": instance.encaminhado,
                    "situacao_locked": (
                        hasattr(instance, "movimentacaoprocesso")
                        and instance.movimentacaoprocesso.situacao.pk == 1
                    ),
                },
                codigo=protocolo.codigo,
                codigo_processo=protocolo.processo.codigo_processo,
                protocolo_externo=protocolo.protocolo_externo,
                midia_display=protocolo.get_midia_display(),
                movimentacao=instance.pk,
                data=(
                    DateUtils.datetime_to_str(instance.data_encaminhamento)
                    if instance.data_encaminhamento
                    else ""
                ),
                origem=str(instance.servidor_origem)
                + " - "
                + str(instance.lotacao_origem),
                posicao=localizacao_atual,
                assunto_processo=nil_pk(protocolo.processo.assunto_processo, None),
                assunto_display=protocolo.processo.process_matter_subject,
                paginas=protocolo.processo.paginas,
                situacao_display=(
                    instance.movimentacaoprocesso.situacao.nome
                    if hasattr(instance, "movimentacaoprocesso")
                    and instance.movimentacaoprocesso.situacao is not None
                    else None
                ),
                passo=instance.passo,
                volume=Processo.int_to_roman(protocolo.processo.volume),
                interessados=interessados,
                primeiro_interessado=(
                    protocolo.processo.interessados.all()[0].nome
                    if protocolo.processo.interessados.count() > 0
                    else None
                ),
                custo=str(instance.custo_passo.days) + " dias",
                # Parametros utilizados na window Editar e Open
                id=protocolo.pk,
                caixa=protocolo.processo.caixa,
                orgao_geral_origem=(
                    protocolo.orgao_geral_origem.pk
                    if protocolo.orgao_geral_origem is not None
                    else ""
                ),
                tipo_documento=(
                    protocolo.tipo_documento.pk
                    if protocolo.tipo_documento is not None
                    else None
                ),
                tipo_documento_unicode=(
                    str(protocolo.tipo_documento)
                    if protocolo.tipo_documento is not None
                    else None
                ),
                sigiloso=protocolo.sigiloso,
                resumo=protocolo.resumo,
                # servidor_origem == Protocolado por
                protocolado_por=str(protocolo.servidor_origem),
                # anexos=anexos,
                dias_criacao=str(dias_criacao_processo) + " dia(s)",
            )
        else:
            if isinstance(instance, Processo) is True:
                _dict_.update(
                    codigo=instance.codigo,
                    assunto=nil_pk(instance.processo.assunto_processo, None),
                    orgao_geral_origem=(
                        instance.orgao_geral_origem.pk
                        if instance.orgao_geral_origem is not None
                        else ""
                    ),
                    protocolo_externo=instance.protocolo_externo,
                    midia_display=instance.get_midia_display(),
                    sigiloso=instance.sigiloso,
                    resumo=instance.resumo,
                    primeira_movimentacao=instance.movimentacoes.order_by("-passo")[
                        0
                    ].pk,
                )
        return _dict_

    def get_query(self):
        """:returns: QuerySet com movimentações da caixa de entrada ou saída."""
        query = EDOCBoxQueryProcesso(
            servidor=self.get_servidor(),
            lotacoes=self.get_lotacoes_servidor(),
            lotacoes_protocolo_geral=self.get_lotacoes_servidor_protocolo_geral(),
        )
        if self.request.META.get("HTTP_BOX", "1") == "1":
            # Caixa Entrada
            query = query.get_caixa_entrada().exclude(
                EDOCBoxQueryProcesso.get_finalizado_recebido()
            )
        else:
            # Caixa Saída
            query = query.get_caixa_saida()

        query = query.filter(protocolo__processo__isnull=False).order_by(
            "-data_encaminhamento"
        )

        return query

    def action_open_processo(self, args=[]):
        """Action que retorna dados para preencher o 'OpenWindow' de um processo.

        :param args[0]: Código do processo.

        :returns: Dicionário com dados pertinentes ao processo.
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        # Permissão para acessar informações dos interesssados
        # Se processo não for sigiloso permite o acesso
        # Se processo for sigiloso verifica se passou pela sua caixa de entrada ou saida ao menos uma movimentação do Processo
        acesso_interessados = False
        try:
            codigo = args[0]
            processo = Processo.objects.get(codigo=codigo)

            # Seleciona uma movimentação qualquer do processo para executar o self.model_to_dict que irá extrair as informações do processo
            # As informações a serem utilizadas são apenas as pertinentes ao processo referenciado por suas movimentaçoes
            movimentacao = processo.movimentacoes.all()[0]

            lista_movs = processo.movimentacoes.all().values_list("pk", flat=True)

            # Segurança -- Verifica se permite o acesso às informações de interessado caso o processo seja sigiloso
            if processo.sigiloso is True:
                query = EDOCBoxQueryProcesso(
                    servidor=self.get_servidor(),
                    lotacoes=self.get_lotacoes_servidor(),
                    lotacoes_protocolo_geral=self.get_lotacoes_servidor_protocolo_geral(),
                )
                caixa_entrada = query.get_caixa_entrada().filter(
                    protocolo__processo__isnull=False
                )
                caixa_saida = query.get_caixa_saida().filter(
                    protocolo__processo__isnull=False
                )

                if (caixa_entrada.filter(pk__in=lista_movs).count() > 0) or (
                    caixa_saida.filter(pk__in=lista_movs).count() > 0
                ):
                    # Se passou pela caixa do usuário logado, então permite o acesso às informações
                    acesso_interessados = True
            else:
                #  Processo não é sigiloso - Pode consultar
                acesso_interessados = True
            #

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            if acesso_interessados is True:
                obj.update(
                    {
                        "instance": self.model_to_dict(movimentacao),
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )
            else:
                obj.update(
                    {
                        "instance": EpadProcesso.model_to_dict_low_permission(processo),
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    @classmethod
    def model_to_dict_low_permission(cls, instance):
        """Cópia de EpadProcessoComum - model_to_dict. Para gerar o dicionário sem os interessados do Processo"""
        _dict_ = {
            "pk": instance.pk,
            "unicode": str(instance),
        }
        ultima_mov = Movimentacao.objects.filter(
            protocolo=instance.protocolo_ptr
        ).order_by("-passo")[0]
        ultima_mov = ultima_mov.movimentacaoprocesso
        localizacao_atual = (
            str(ultima_mov.destinatario) if ultima_mov.destinatario is not None else ""
        )
        localizacao_atual = localizacao_atual + " - "
        localizacao_atual = (
            localizacao_atual + str(ultima_mov.lotacao_destino)
            if ultima_mov.lotacao_destino is not None
            else ""
        )
        # anexos = []
        # for a in ProtocoloManager.get_anexos_from_protocolo(instance):
        #     anexos.append({
        #         'pk': a.pk,
        #         'nome': a.nome,
        #         'descricao': a.descricao,
        #         'link': a.arquivo.permalink(),
        #         'enviado_por': DateUtils.datetime_to_str(a.arquivo.created) if a.arquivo.created is not None else None,
        #     })
        _dict_.update(
            codigo=instance.codigo,
            codigo_processo=instance.codigo_processo,
            protocolo_externo=instance.protocolo_externo,
            movimentado=(
                DateUtils.datetime_to_str(ultima_mov.data_encaminhamento)
                if ultima_mov.data_encaminhamento
                else ""
            ),
            assunto_display=instance.processo.process_matter_subject,
            custo=str(ultima_mov.custo_passo.days) + " dias",
            remetente=str(ultima_mov.servidor_origem)
            + " - "
            + str(ultima_mov.lotacao_origem),
            posicao=localizacao_atual,
            situacao_display=(
                ultima_mov.situacao.nome if ultima_mov.situacao is not None else None
            ),
            paginas=instance.paginas,
            volume=Processo.int_to_roman(instance.volume),
            # Utilizado por Window e OpenWindow
            caixa=instance.caixa,
            id=instance.pk,
            protocolado_por=str(instance.servidor_origem),
            # tipo_documento=instance.tipo_documento.pk if instance.tipo_documento is not None else None,
            tipo_documento_unicode=(
                str(instance.tipo_documento)
                if instance.tipo_documento is not None
                else None
            ),
            resumo=instance.resumo,
            sigiloso=instance.sigiloso,
            # Sigilo de Interessados
            interessados=[],
            # anexos=anexos,
        )
        return _dict_

    def get_servidor(self):
        """
        Este método retorna o Servidor que está logado no sistema.

        :returns: Servidor
        """
        if not self.servidor:
            self.servidor = employee_from_user(self.request.user)
        return self.servidor

    def get_lotacoes_servidor(self):
        """
        Este método retorna a relação dos pks das lotações/designações que o servidor logado possui.
        :returns: list - lotações/designações, caso não existe retorna [].
        """
        if not self.lotacoes:
            self.lotacoes = [
                lotacao.pk
                for lotacao in self.get_servidor().work_locations_effective_exercise
            ]
        return self.lotacoes

    def get_lotacoes_servidor_protocolo_geral(self):
        """
        Este método retorna a relação dos pks das lotações/designações (protocolo_geral) que o servidor logado possui.
        :returns: list - lotações/designações, caso não existe retorna [].
        """
        employee = self.get_servidor()
        if employee and not self.lotacoes_protocolo_geral:
            self.lotacoes_protocolo_geral = [
                lotacao.pk
                for lotacao in employee.work_locations_effective_exercise
                if lotacao.acesso_protocolo_geral
            ]
        return self.lotacoes_protocolo_geral

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "document": {
                "content": "Somente um teste",
            },
        }

        try:
            # log.info(args[0])
            travel_report = self._model.objects.get(pk=args[0])
            rst.update(
                success=True,
                document={
                    # 'content': travel_report.rend,
                    "content": travel_report.render_process,
                },
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possível encontrar o documento. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)


class EpadProcessoComum(EpadProcesso):
    """
    **Classe** Restful para consultar todos os processos sem a informação de interessado.
    """

    full_text_index = (
        "codigo_processo__icontains",
        "codigo__icontains",
        "protocolo_externo__icontains",
        "assunto_processo__nome__icontains",
        "resumo__icontains",
        "process_matter__legal_matter__cnmp_code__icontains",
        "assunto__icontains",
    )

    def action_open_processo(self, args=[]):
        """Action que retorna dados para preencher o 'OpenWindow' de um processo.

        :param args[0]: Código do processo.

        :returns: Dicionário com dados pertinentes ao processo.
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            codigo = args[0]
            # Consultando pelo codigo do Protocolo
            # Nesta action retorna o Processo, e em model_to_dict não retorna os interessados
            # Podendo ser alterado para mostrar os interessados dos Processos que não são sigilosos
            instance = Processo.objects.get(codigo=codigo)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(
                {
                    "instance": self.model_to_dict(instance),
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.consulta.Manager",{})')

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        # ultima_mov = Movimentacao.objects.filter(protocolo=instance.protocolo_ptr).order_by("-passo")[0]
        # ultima_mov = ultima_mov.movimentacaoprocesso
        ultima_mov = MovimentacaoProcesso.objects.filter(
            protocolo=instance.protocolo_ptr
        ).latest("passo")
        localizacao_atual = (
            str(ultima_mov.destinatario) if ultima_mov.destinatario else ""
        )
        localizacao_atual += " - "
        localizacao_atual += (
            str(ultima_mov.lotacao_destino) if ultima_mov.lotacao_destino else ""
        )
        # anexos = []
        # for a in instance.attachments.filter():
        #     anexos.append({
        #         'pk': a.pk,
        #         'nome': a.nome,
        #         'descricao': a.descricao,
        #         'link': a.arquivo.permalink() if a.arquivo else '',
        #         'enviado_por': DateUtils.datetime_to_str(a.arquivo.created) if a.arquivo is not None else None,
        #     })
        _dict_.update(
            codigo=instance.codigo,
            codigo_processo=instance.codigo_processo,
            protocolo_externo=instance.protocolo_externo,
            movimentado=(
                DateUtils.datetime_to_str(ultima_mov.data_encaminhamento)
                if ultima_mov.data_encaminhamento
                else ""
            ),
            assunto_display=instance.processo.process_matter_subject,
            custo=str(ultima_mov.custo_passo.days) + " dias",
            remetente=str(ultima_mov.servidor_origem)
            + " - "
            + str(ultima_mov.lotacao_origem),
            posicao=localizacao_atual,
            situacao_display=(
                ultima_mov.situacao.nome if ultima_mov.situacao is not None else None
            ),
            paginas=instance.paginas,
            volume=Processo.int_to_roman(instance.volume),
            passo=ultima_mov.passo,
            # Utilizado por Window e OpenWindow
            caixa=instance.caixa,
            id=instance.pk,
            protocolado_por=str(instance.servidor_origem),
            # tipo_documento=instance.tipo_documento.pk if instance.tipo_documento is not None else None,
            tipo_documento_unicode=(
                str(instance.tipo_documento)
                if instance.tipo_documento is not None
                else None
            ),
            resumo=instance.resumo,
            sigiloso=instance.sigiloso,
            # Sigilo de Interessados
            interessados=[],
            # anexos=anexos,
            assunto_processo=nil_pk(instance.assunto_processo, None),
            orgao_geral_origem=(
                instance.orgao_geral_origem.pk
                if instance.orgao_geral_origem is not None
                else ""
            ),
            movimentacao=ultima_mov.pk,
        )
        return _dict_

    def get_query(self):
        """:returns: QuerySet com todas instâncias de Processo."""
        return self.Model.objects.filter().order_by("-ano", "-numero")


class EpadProcessoAdmin(EpadProcessoComum):
    """
    **Classe** Restful para consultar todos os processo, sem saber o interessado, mas permite cadastrar processo manualmente.
    """

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.admin.Manager",{})')

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "manual" in params:
            params.update(manual=True)

        if "unidade_gestora" in params:
            cod_processo = "%4d.%s.%05d" % (
                int(params.get("ano")),
                params.get("unidade_gestora"),
                int(params.get("numero")),
            )
            params.update(codigo_processo=cod_processo)

        log.info(params)

        return params


class EpadMovimentacao(Restful):

    _model = MovimentacaoProcesso

    force_upper = False

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)

        encaminhado_para = (
            str(instance.destinatario) if instance.destinatario is not None else ""
        )
        encaminhado_para = encaminhado_para + " - "
        encaminhado_para = (
            encaminhado_para + str(instance.lotacao_destino)
            if instance.lotacao_destino is not None
            else ""
        )

        _dict_.update(
            encaminhado=(
                DateUtils.datetime_to_str(instance.data_encaminhamento)
                if instance.data_encaminhamento is not None
                else ""
            ),
            encaminhado_por=(
                str(instance.servidor_origem) + " - " + str(instance.lotacao_origem)
                if instance.data_encaminhamento is not None
                else ""
            ),
            encaminhado_para=(
                encaminhado_para if instance.data_encaminhamento is not None else ""
            ),
            recebido=(
                DateUtils.datetime_to_str(instance.data_recebimento)
                if instance.data_recebimento is not None
                else ""
            ),
            recebido_por=(
                str(instance.servidor_destino.pessoa_fisica)
                if instance.servidor_destino is not None
                and instance.data_recebimento is not None
                else ""
            ),
            parecer=instance.parecer,
            paginas=instance.paginas,
            situacao=instance.situacao.nome if instance.situacao is not None else None,
            volume=(
                Processo.int_to_roman(instance.volume)
                if instance.volume is not None
                else None
            ),
            custo=str(instance.custo_passo.days) + " dias",
        )
        return _dict_

    def action_desfazer_envio(self, args=[]):
        """Action que desfaz envio de uma movimentação."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            params = self.get_params(self.request.POST)
            params.update(
                movimentacao=Movimentacao.objects.get(pk=params.get("movimentacao", ""))
            )

            MovimentacaoManager.desfazer_envio(params.get("movimentacao"))

        except Movimentacao.DoesNotExist as e:
            obj.update(message="Movimentação não encontrada!")
            log.exception(e)
        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def action_movimentacoes_processo(self, args=[]):
        """Action que retorna todas as movimentações de um processo.

        :param args[0]: Código do processo.
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            codigo = args[0]
            query = MovimentacaoProcesso.objects.filter(
                protocolo__codigo=codigo
            ).order_by("-passo")
            query = self.do_page(query)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def action_receber_movimentacoes(self, args=[]):
        """Action que recebe movimentacoes
        :param args: Lista de movimentacoes
        :type args: list
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception("Servidor não encontrado!")
            MovimentacaoManager.receber(args, employee)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def action_marcar_nao_recebido(self, args=[]):
        """Action que marca movimentacoes como não recebidas
        :param args: Lista de movimentacoes
        :type args: list
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception("Servidor não encontrado!")
            MovimentacaoManager.marcar_nao_recebido_movimentacao(args, employee)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def action_finalizar(self, args=[]):
        """Action que finaliza protocolo
        :param args: Lista de movimentacoes
        :type args: list
        """
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            employee = employee_from_user(self.request.user)
            if not employee:
                raise Exception("Servidor não encontrado!")
            MovimentacaoManager.finalizar(args[0], employee)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def nova_movimentacao_lote(self, args=[]):
        """Action que realiza movimentação em lote"""
        rst = {
            "success": False,
            "message": "Não foi processado ainda",
        }

        try:
            params = self.get_params(self.request.POST)
            log.debug(params)

            if "selecteds" not in params:
                raise Exception("Movimentações não encontradas")

            if (params.get("lotacao_destino", "") == "") and (
                params.get("pessoa", "") == ""
            ):
                raise Exception("É necessário selecionar um destinatário para enviar")

            selecteds = params.get("selecteds", [])
            if isinstance(selecteds, (list, tuple)) is False:
                if selecteds == "":
                    selecteds = []
                else:
                    selecteds = [selecteds]

            for pk in selecteds:
                movimentacao = Movimentacao.objects.get(pk=pk)
                requisicao = {
                    "protocolo": movimentacao.protocolo.codigo,
                    "movimentacao": movimentacao.pk,
                    "pessoa": params.get("pessoa", ""),
                    "lotacao_destino": params.get("lotacao_destino", ""),
                    "parecer": params.get("parecer", ""),
                }

                ultima_mov = Movimentacao.objects.filter(
                    protocolo=movimentacao.protocolo
                ).order_by("-passo")[0]
                ultima_mov_processo = ultima_mov.movimentacaoprocesso

                if "urgente" in params:
                    requisicao.update(urgente=params.get("urgente"))
                if "caixa" in params:
                    requisicao.update(caixa=params.get("caixa"))
                if "situacao" in params:
                    requisicao.update(situacao=params.get("situacao"))
                else:
                    requisicao.update(situacao=ultima_mov_processo.situacao.pk)

                self.request.POST = QueryDict("")
                self.request.POST = self.request.POST.copy()
                self.request.POST.update(requisicao)
                log.debug(self.request.POST)

                if MovimentacaoManager.is_recebido(movimentacao):
                    obj_return = self.nova_movimentacao(render=False)
                    if obj_return.get("success") is False:
                        log.debug(obj_return.get("message"))
                        raise Exception(obj_return.get("message"))
                else:
                    raise Exception(
                        "Antes de movimentar o protocolo %s é necessário recebê-lo!"
                        % movimentacao.protocolo.codigo
                    )

        except Movimentacao.DoesNotExist as e:
            rst.update(message="Movimentação não encontrada!")
            log.exception(e)
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def nova_movimentacao(self, args=[], render=True):
        """Action que cria movimentação"""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }

        servidor_lotacoes = []
        pessoa_lotacoes = []
        lotacoes_destino = []
        servidor_lotacoes = []
        result_lotacao = False
        result_pessoa = False
        message_lotacao = ""
        message_pessoa = ""

        try:
            params = self.get_params(self.request.POST)
            log.debug(params)
            log.info(params.get("pessoa"))
            if "protocolo" not in params:
                raise Exception("Parâmetro protocolo é necessário")

            concluir = False
            if "concluir" in params:
                concluir = True

            if (params.get("lotacao_destino", "") == "") and (
                params.get("pessoa", "") == ""
            ):
                if "concluir" not in params:
                    raise Exception(
                        "É necessário selecionar um destinatário para enviar"
                    )

            if (params.get("lotacao_destino", "") != "") and (
                params.get("pessoa", "") == ""
            ):
                if not ServidorLotacao.objects.filter(
                    lotacao=Lotacao.objects.get(pk=params.get("lotacao_destino")),
                    ativo=True,
                ).exists():
                    raise Exception(
                        "Essa Lotação não possui nenhum servidor(a) a ela vinculada!"
                    )

            protocolo = Protocolo.objects.get(codigo=params.get("protocolo", ""))
            processo = protocolo.processo

            if not (processo.assunto_processo or processo.process_matter.filter()):
                raise Exception("É necessário definir o Assunto do processo.")

            self.valida_posse_processo(processo)

            ultima_mov = Movimentacao.objects.filter(protocolo=protocolo).order_by(
                "-passo"
            )[0]
            ultima_mov_processo = ultima_mov.movimentacaoprocesso

            # Processo arquivado não altera situação
            if ultima_mov_processo.situacao.pk == 1:
                params.update(situacao=1)

            if params.get("situacao", "") == "":
                raise Exception("É necessário informar uma situação")

            if (params.get("lotacao_destino", "") == "") and (
                params.get("pessoa", "") == ""
            ):
                # Neste ponto temos a certeza que 'concluir' está em params
                servidor_lotacoes = [
                    [protocolo.interessado.pk, protocolo.orgao_geral_origem.pk]
                ]
            else:
                if "pessoa" in params:
                    pessoa = params.get("pessoa", [])
                    if isinstance(pessoa, (list, tuple)) is False:
                        if pessoa == "":
                            pessoa = []
                        else:
                            pessoa = [pessoa]

                    servidor_lotacoes, pessoa_lotacoes = self.get_lotacao_da_pessoa(
                        pessoa, concluir, protocolo
                    )
                    if pessoa != [] and (not servidor_lotacoes or not pessoa_lotacoes):
                        # Neste ponto temos a certeza de que há pessoa em params
                        raise Exception(
                            "Protocolo não movimentado! Impossível enviar às Pessoas selecionadas."
                        )

            if "movimentacao" not in params:
                raise Exception("Parâmetro movimentação é necessário")
            movimentacao = Movimentacao.objects.get(pk=params.get("movimentacao", 0))

            if "lotacao_destino" in params:
                lotacoes_destino = params.get("lotacao_destino", [])
                if isinstance(lotacoes_destino, (list, tuple)) is False:
                    if lotacoes_destino == "":
                        lotacoes_destino = []
                    else:
                        lotacoes_destino = [lotacoes_destino]
                lotacoes_destino = [int(ld) for ld in lotacoes_destino]

            # Removendo lotações da pessoa destinataria das lotacoes destinatarias
            # Enviando apenas para destinatario (especifico), e cancela envio da lotacao (geral)
            for l in pessoa_lotacoes:
                if l in lotacoes_destino:
                    lotacoes_destino.remove(l)
            # Isso evita que a pessoa destinataria receba mais de uma movimentacao na cx. entrada

            EDOCBoxManager.is_lotacoes_em_organograma(lotacoes_destino)

            if not lotacoes_destino and not pessoa_lotacoes and not servidor_lotacoes:
                raise Exception(
                    "Problemas na movimentação, destino não encontrado! \nTente outra vez!"
                )

            deferido = None
            if "deferido" in params:
                if params.get("deferido") == "True":
                    deferido = True
                elif params.get("deferido") == "False":
                    deferido = False
                else:
                    deferido = None

            urgente = True if "urgente" in params else False
            data_encaminhamento = datetime.now()
            data_finalizado = data_encaminhamento if concluir is True else None
            parecer = self.get_parecer(
                params.get("parecer", ""), data_encaminhamento, concluir
            )
            employee = employee_from_user(self.request.user)

            kwargs = {
                "movimentacao_pk": movimentacao.pk,
                "protocolo": protocolo,
                "orgao_geral_origem": MovimentacaoManager.get_lotacao_origem(
                    movimentacao
                ).pk,
                "servidor_origem": employee.pk if employee else None,
                "deferido": deferido,
                "data_encaminhamento": data_encaminhamento,
                "parecer": parecer,
                "urgente": urgente,
                "destinatario": None,
                "data_finalizado": data_finalizado,
            }

            kwargs.update({"lotacoes_destino": lotacoes_destino})
            # Caso seja necessário alterar nova_movimentacao (para 1 processo apenas) colocando os campos pagina e volume diretamente
            # if 'paginas' in params:
            #     if params.get('paginas', '') == '':
            #         raise Exception('Favor informar quantidade de páginas')
            #     try:
            #         kwargs.update(paginas=int(params.get('paginas')))
            #     except Exception:
            #         raise Exception('Página: informe um número válido')
            #     processo.paginas = kwargs.get('paginas')
            #     processo.save()
            # else:
            #     kwargs.update(paginas=processo.paginas)

            # if 'volume' in params:
            #     if params.get('volume', '') == '':
            #         raise Exception('Favor informar volume atual')
            #     try:
            #         kwargs.update(volume=Processo.roman_to_int(str(params.get('volume'))))
            #     except Exception:
            #         raise Exception('Volume: informe um número romano válido')
            #     processo.volume = kwargs.get('volume')
            #     processo.save()
            # else:
            #     kwargs.update(volume=processo.volume)

            kwargs.update(paginas=processo.paginas)
            kwargs.update(volume=processo.volume)
            if "situacao" in params:
                kwargs.update(situacao=Situacao.objects.get(pk=params.get("situacao")))
            # result_lotacao, message_lotacao = MovimentacaoManager.envia_movimentacao_por_lotacao(kwargs)

            if lotacoes_destino:
                kwargs.update({"lotacoes_destino": lotacoes_destino})
                result_lotacao, message_lotacao = (
                    MovimentacaoManager.envia_movimentacao_por_lotacao(kwargs)
                )
            elif servidor_lotacoes:
                kwargs.update({"servidor_lotacao_destino": servidor_lotacoes})
                result_pessoa, message_pessoa = (
                    MovimentacaoManager.envia_movimentacao_por_pessoa(kwargs)
                )

            if result_lotacao is False and result_pessoa is False:
                log.debug(message_lotacao)
                raise Exception("Ocorreu um erro ao enviar para o destinatario")
            # else:
            #     MovimentacaoManager.envia_finalizado_interessado(kwargs)

            if "caixa" in params:
                processo.caixa = params.get("caixa")
                processo.save()

            # if 'anexos' in params:
            #     anexos = params.get('anexos', [])
            #     if isinstance(anexos, (list, tuple)) is False:
            #         if (anexos == ''):
            #             anexos = []
            #         else:
            #             anexos = [anexos]
            #     for a in anexos:
            #         if movimentacao.anexos.filter(pk=int(a)).exists() is False:
            #             movimentacao.anexos.add(Anexo.objects.get(pk=int(a)))

            referencias = Referencia.objects.filter(processo=processo)
            ultima_mov = Movimentacao.objects.filter(
                protocolo=processo.protocolo_ptr
            ).order_by("-passo")[0]
            ultima_mov_processo = ultima_mov.movimentacaoprocesso
            for r in referencias:
                ultima_mov_processo.historico_referencias.add(r)

            if "interessados" in params:
                interessados = params.get("interessados", [])
                if isinstance(interessados, (list, tuple)) is False:
                    if interessados == "":
                        interessados = []
                    else:
                        interessados = [interessados]
                for i in interessados:
                    if processo.interessados.filter(pk=int(i)).exists() is False:
                        processo.interessados.add(Pessoa.objects.get(pk=int(i)))

        except Protocolo.DoesNotExist as e:
            obj.update(
                message="Problemas na movimentação, protocolo não encontrado! \nTente outra vez!"
            )
            log.exception(e)
        except Movimentacao.DoesNotExist as e:
            obj.update(message="Movimentação não encontrada!")
            log.exception(e)
        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        if render is True:
            rendererer = self.get_renderer(
                self.request.META.get("HTTP_ACCEPT", "text/json")
            )
            rendererer(obj)
        return obj

    def action_imprimir_etiqueta(self, args=[]):
        """Action que imprime etiqueta."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            params = self.get_params()
            log.debug(params)

            if params.get("impressora", "") == "":
                raise Exception("Favor preencher o campo impressora")

            if params.get("quantidade", "") == "":
                raise Exception("Favor preencher o campo quantidade")

            impressora = Impressora.objects.get(pk=int(params.get("impressora")))
            movimentacao = Movimentacao.objects.get(
                pk=int(params.get("movimentacao", ""))
            )
            host = xmlrpc.client.ServerProxy(
                "http://{0}:{1}".format(impressora.host, impressora.port)
            )
            destino = (
                movimentacao.destinatario.nome
                if movimentacao.destinatario is not None
                else movimentacao.lotacao_destino.nome
            )

            if not host.impP(
                {
                    "assunto": normalize(
                        "NFKD", movimentacao.protocolo.processo.assunto_processo.nome
                    ).encode("ascii", "ignore"),
                    "entrada": movimentacao.protocolo.data_criacao.strftime(
                        "%d/%m/%Y %H:%M"
                    ),
                    "origem": normalize(
                        "NFKD", movimentacao.protocolo.orgao_geral_origem.nome
                    ).encode("ascii", "ignore"),
                    "destino": normalize("NFKD", destino).encode("ascii", "ignore"),
                    "codigo": movimentacao.protocolo.codigo,
                },
                int(self.request.POST.get("quantidade")),
            ):
                raise Exception("Erro na máquina de impressão.")
            else:
                log.info("Host de impressão não encontrado.")

        except Movimentacao.DoesNotExist as e:
            obj.update(message="Movimentação não encontrada!")
            log.exception(e)
        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def get_lotacao_da_pessoa(self, pessoa, concluir, protocolo):
        """
        Este método retorna todas Lotacao e todas ServidorLotacao encontradas de acordo com a lista de pk(s) informados.
        Apenas servidores possuem Lotacao. Para os interessados será retornado o Órgão de Origem que foi preenchido
        no momento da criação do Protocolo.
        :param pessoa: - Pk(s) de Pessoa.
        :type pessoa: list
        :returns: lista de ServidorLotacao, lista de Lotacao.
        """
        servidor_lotacoes = []
        pessoa_lotacoes = []
        # pessoas_pk = []
        # ENCONTRA AS LOTAÇÕES DOS SERVIDORES
        for sl in (
            ServidorLotacao.work_assignment_exercise()
            .filter(servidor__pessoa_fisica__pk__in=pessoa)
            .exclude(lotacao=None)
        ):
            # pessoas_pk.append(sl.servidor.pessoa_fisica.pk)
            if sl.lotacao is None:
                raise Exception("%s não possui lotação ou designação!" % sl.servidor)
            servidor_lotacoes.append([sl.servidor.pessoa_fisica.pk, sl.lotacao.pk])
            pessoa_lotacoes.append(sl.lotacao.pk)

        # ENCONTRA OS ÓRGÃOS DE ORIGEM DOS INTERESSADOS(PESSOAS)
        if concluir is True:
            for p in pessoa:
                servidor_lotacoes.append([int(p), protocolo.orgao_geral_origem.pk])
                pessoa_lotacoes.append(protocolo.orgao_geral_origem.pk)
        return servidor_lotacoes, pessoa_lotacoes

    def get_parecer(self, parecer, data_encaminhamento, concluir):
        if concluir is True:
            if parecer == "" or parecer is None:
                employee = employee_from_user(self.request.user)
                if employee and employee.matricula == 0:
                    parecer = (
                        "Movimentação finalizada em %s pelo software limpeza da caixa de entrada."
                        % (DateUtils.datetime_to_str(data_encaminhamento))
                    )
                else:
                    parecer = "Movimentacação finalizada em %s." % (
                        DateUtils.datetime_to_str(data_encaminhamento)
                    )

        return parecer

    def valida_posse_processo(self, pk_processo):
        """Método que valida o envio de um processo, verificando se este processo ainda encontra-se na caixa de entrada
        da pessoa que está tentando envia-lo."""
        log.info("VALIDANDO POSSE DO PROCESSO")
        employee = employee_from_user(self.request.user)
        lotacoes_protocolo_geral = [
            lotacao.pk
            for lotacao in employee.work_locations_effective_exercise
            if lotacao.acesso_protocolo_geral
        ]

        query = EDOCBoxQueryProcesso(
            servidor=employee,
            lotacoes=employee.work_locations_effective_exercise,
            lotacoes_protocolo_geral=lotacoes_protocolo_geral,
        )
        caixa_entrada = query.get_caixa_entrada().filter(
            protocolo__processo__isnull=False
        )

        processo = Processo.objects.get(pk=pk_processo)
        if not caixa_entrada.filter(protocolo__processo__pk__in=[processo.pk]).exists():
            raise Exception(
                "Esse Processo já foi movimentado e não encontra-se mais em sua posse. Atualize sua caixa de entrada!"
            )


class EpadAssunto(Restful):

    _model = Assunto

    force_upper = False

    full_text_index = ("nome__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            nome=instance.nome,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor preencher os campos obrigatórios")

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.assunto.Manager",{})')


class EpadSituacao(Restful):

    _model = Situacao

    force_upper = False

    full_text_index = ("nome__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            nome=instance.nome,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor preencher os campos obrigatórios")

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.situacao.Manager",{})')


class EpadReferencia(Restful):

    _model = Referencia

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            processo=instance.processo.pk,
            processo_codigo=instance.processo.codigo_processo,
            processo_codigo_protocolo=instance.processo.codigo,
            referenciado=instance.referenciado.pk,
            referenciado_codigo=instance.referenciado.codigo_processo,
            referenciado_codigo_protocolo=instance.referenciado.codigo,
            tipo=instance.tipo,
            tipo_display=instance.get_tipo_display(),
            descricao=instance.descricao,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "processo" in params:
            if params.get("processo", "") == "":
                raise Exception("Favor informar o Processo")
            params.update(processo=Processo.objects.get(pk=params.get("processo")))
        if "referenciado" in params:
            if params.get("referenciado", "") == "":
                raise Exception("Favor informar o Processo referenciado")
            params.update(
                referenciado=Processo.objects.get(pk=params.get("referenciado"))
            )
        if "tipo" in params:
            if params.get("tipo", "") == "":
                raise Exception("Favor informar o tipo")
            params.update(tipo=int(params.get("tipo") or 0))
            if params.get("tipo") == 0:
                raise Exception("Tipo inválido")

        if "descricao" in params:
            if params.get("descricao", "") == "":
                raise Exception("Favor informar a descrição")

        if "processo" in params and "referenciado" in params:
            if params.get("processo").pk == params.get("referenciado").pk:
                raise Exception("Não é permitido referenciar o próprio processo")

        params.update(data=datetime.now().date())

        log.debug(params)

        return params


class EpadConfig(Restful):

    _model = Configuration

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            slug=instance.application,
            situacao_novo_processo=instance.get("situacao_novo_processo"),
        )
        return _dict_

    def json(self, args=[]):
        cfg = Configuration.get_or_create("epad")
        dicio = '{"values": {"pk": %d, "situacao_novo_processo": %d}}' % (
            cfg.pk,
            int(cfg.get("situacao_novo_processo") or 0),
        )
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.processo.config.Manager", %s)' % dicio)

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)
        cfg = Configuration.get_or_create("epad")

        if "situacao_novo_processo" in params:
            cfg.set("situacao_novo_processo", params.get("situacao_novo_processo"))
            del params["situacao_novo_processo"]

        return params


class EpadJustificativa(Restful):

    _model = Justificativa

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            processo=instance.processo.pk,
            processo_codigo=instance.processo.codigo_processo,
            movimentacao=instance.movimentacao.pk,
            usuario=instance.usuario.username,
            valor_antigo=instance.valor_antigo,
            valor_novo=instance.valor_novo,
            tipo=instance.tipo,
            tipo_display=instance.get_tipo_display(),
            justificativa=instance.justificativa,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "processo" in params:
            params.update(processo=Processo.objects.get(pk=params.get("processo")))

        if "movimentacao" in params:
            params.update(
                movimentacao=MovimentacaoProcesso.objects.get(
                    pk=params.get("movimentacao")
                )
            )

        if "tipo" in params:
            params.update(tipo=int(params.get("tipo") or 0))
            if params.get("tipo") == 0:
                raise Exception("Tipo inválido")

        if "volume" in params:
            if params.get("volume", "") == "":
                raise Exception("Favor informar o volume")
            params.update(valor_novo=Processo.roman_to_int(str(params.get("volume"))))

        if "paginas" in params:
            if params.get("paginas", "") == "":
                raise Exception("Favor informar a pagina")
            params.update(valor_novo=int(params.get("paginas")))

        if "justificativa" in params:
            if params.get("justificativa", "") == "":
                raise Exception("Favor informar a justificativa")
            # if len(str(params.get('justificativa'))) < 26:
            #     raise Exception('Favor informar uma justificativa maior')
            if len(params.get("justificativa")) < 26:
                raise Exception("Favor informar uma justificativa maior")

        params.update(usuario=self.request.user)

        log.debug(params)

        return params


class EDOCBoxQueryProcesso(EDOCBoxQuery):

    def get_qdepartamento_entrada(self):
        """Sobrescrita do método para permitir visualizar os processos sigilosos de seu departamento"""
        qservidor_destino_none = Q(servidor_destino=None)
        qdestino_none = Q(lotacao_destino=None)
        qdestinatario_none = Q(destinatario=None)
        qlotacao_origem = Q(lotacao_origem__in=self.lotacoes)
        qdestino_destinatario_none_e_lotacao_origem = Q(
            qdestino_none
            & qdestinatario_none
            & qlotacao_origem
            & qservidor_destino_none
        )
        # qdestino_destinatario_none_e_lotacao_origem = Q(qdestino_none & qdestinatario_none & qlotacao_origem)
        # qdestino_destinatario_none_e_lotacao_origem = Q(qdestinatario_none & qlotacao_origem)
        qlotacao_destino = Q(lotacao_destino__in=self.lotacoes)
        # qdestino_not_none_qdestinatario_none_qlotacao_destino = qdestinatario_none & qlotacao_destino & qservidor_destino_none
        qdestino_not_none_qdestinatario_none_qlotacao_destino = (
            qdestinatario_none & qlotacao_destino
        )
        # log.debug("qdestino_not_none_qdestinatario_none_qlotacao_destino %s" % Movimentacao.objects.filter(
        #   qdestino_not_none_qdestinatario_none_qlotacao_destino).count())
        # log.debug("qdestino_destinatario_none_e_lotacao_origem %s" % Movimentacao.objects.filter(
        #   qdestino_destinatario_none_e_lotacao_origem).count())
        qdepartamento = Q(
            qdestino_destinatario_none_e_lotacao_origem
            | qdestino_not_none_qdestinatario_none_qlotacao_destino
        )
        return qdepartamento

    def get_qgeral_entrada(self):
        # TODO: VERIFICAR AQUI NA ENTRADA GERAL
        qlotacao_criacao = Q(lotacao_criacao__in=self.lotacoes_protocolo_geral)
        qlotacao_destino_none_lotacao_criacao = (
            Q(lotacao_destino=None) & qlotacao_criacao
        )
        # qlotacao_criacao_none_lotacao_destino = Q(lotacao_criacao = None, lotacao_destino__in=self.lotacoes_protocolo_geral)
        qlotacao_criacao_none_lotacao_destino = Q(
            lotacao_criacao=None,
            lotacao_destino__in=self.lotacoes_protocolo_geral,
            destinatario=None,
        )
        qgeral = Q(
            qlotacao_criacao
            | qlotacao_destino_none_lotacao_criacao
            | qlotacao_criacao_none_lotacao_destino
        )
        return qgeral

    def get_regra_caixa_saida(self):

        qpasso_maoirq_zero = Q(passo__gt=0)
        qnao_excluido = Q(protocolo__excluido=False)
        qdefault = Q(qnao_excluido & qpasso_maoirq_zero)

        qservidor_origem = Q(servidor_origem=self.servidor.pk)
        qpessoal = qservidor_origem
        qpessoal = qservidor_origem | Q(
            Q(servidor_destino=self.servidor.pk)
            | Q(destinatario=self.servidor.pessoa_fisica.pk)
        )

        qlotacao_destino_none = Q(lotacao_destino=None)
        qlotacao_destino_nao_none = ~qlotacao_destino_none
        qdestinatario_none = Q(destinatario=None)
        qdestinatario_nao_none = ~qdestinatario_none
        qlotacao_origem = Q(lotacao_origem__in=self.lotacoes)
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

        qpasso_eq_1 = Q(passo=1)
        qlotacao_criacao = Q(
            protocolo__lotacao_criacao__in=self.lotacoes_protocolo_geral
        )
        qlotacao_criacao_lotacao_destino_nao_none = (
            qlotacao_criacao & qlotacao_destino_nao_none
        )
        qlotacao_criacao_servidor_destino_destinatario_nao_none = Q(
            qlotacao_criacao & qservidor_destino_nao_none
        ) | Q(qlotacao_criacao & qdestinatario_nao_none)
        qgeral = qpasso_eq_1 & Q(
            qlotacao_criacao_servidor_destino_destinatario_nao_none
            | qlotacao_criacao_lotacao_destino_nao_none
        )

        q = qdefault & Q(qpessoal | qdepartamento | qgeral)

        if self.valor:
            q = q & self.get_qbusca(self.valor)

        return q


class EPADPrintMovimentacao(extjs.ExtReportBuild):

    report_src = "/to/mpe/processo/movimentacao/documento_movimentacoes"
    filename = "movimentacao_processo.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/processo/movimentacao/",
        },
    ]

    titles = {
        "TITLE": "Movimentação - Geral",
        "SUB_TITLE": "Impressão do Relatório Geral - Movimentação Geral",
    }

    class Form(forms.Form):
        protocolo = forms.CharField()


class EPADPrintAthenasRecebimento(extjs.ExtReportBuild):

    report_src = "/to/mpe/processo/recebimento/protocolo"
    filename = "protocolo_recibo.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/processo/recebimento",
        },
    ]

    titles = {
        "TITLE": "Protocolo - Geral",
        "SUB_TITLE": "Impressão do Relatório Geral - Protocolo Geral",
    }

    class Form(forms.Form):
        movimentacoes = forms.ModelMultipleChoiceField(
            queryset=Movimentacao.objects.all(), label="Movimentações"
        )


class EPADProcessMatter(Restful):

    _model = ProcessMatter

    def get_params(self, *args, **kargs):

        params = super(EPADProcessMatter, self).get_params(*args, **kargs)

        if "principal" in params:
            params.update(principal=params.get("principal", "off").lower() == "on")

        if "legal_matter" in params:
            if params.get("legal_matter") != "":
                field = getattr(self.Model, "legal_matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(legal_matter=query.get(pk=params.get("legal_matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(legal_matter=None)

        if "process" in params:
            if params.get("process") != "":
                try:
                    params.update(
                        process=Processo.objects.get(pk=params.get("process"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("O processo não foi informado")

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            legal_matter=nil_pk(instance.legal_matter, None),
            legal_matter_unicode=nil_unicode(instance.legal_matter, None),
            process=nil_pk(instance.process, None),
            process_unicode=nil_unicode(instance.process, None),
            principal=instance.principal,
        )

        return rst

    def define_principal(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            process = Processo.objects.filter(pk=params.get("process", 0)).first()

            if process:

                if process.process_matter.filter(pk=args[0]).exists():
                    matter = process.process_matter.get(pk=args[0])
                    if not matter.principal:
                        process.process_matter.filter().update(principal=False)
                        matter.principal = True
                        matter.save()
                        rst.update(
                            success=True, message="Assunto definido como principal."
                        )
                    rst.update(
                        success=True,
                        message="Assunto já encontra-se definido como principal.",
                    )
                else:
                    rst.update(
                        message="Não foi possível modificar o assunto selecionado."
                    )

            else:
                rst.update(message="Processo não encontrado.")

        except self.Model.MultipleObjectsReturned:
            rst.update(
                message="Ocorreu um erro ao definir o assunto principal do processo"
            )
        except self.Model.DoesNotExist:
            rst.update(message="O processo não foi encontrado")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
