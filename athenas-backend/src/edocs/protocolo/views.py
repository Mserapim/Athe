# -.- coding: utf-8 -.-

import xmlrpc.client
import socket as sck
from datetime import datetime

from django import forms
from django.db.models.query_utils import Q
from django.db import transaction
from django.http import HttpResponseBadRequest

from contrib import extjs
from contrib.decorator import login_required, tab
from contrib.helpers import clear_to_ascii
from contrib.utils import getLogger, DateUtils, employee_from_user, get_json_engine
from contrib.controller import DefaultController
from contrib.middleware import get_current_user
from engine.mq.models import Task
from auditoria.models import LineLog
from standard.views import AutoCompleteField
from ged.forms import FileUploadField
from edocs.protocolo.const import MIDIA_ORIGEM
from edocs.protocolo.task.reports import edoc_detail
from edocs.protocolo.utils import EDOCBoxQuery
from edocs.protocolo.models import (
    Movimentacao,
    Anexo,
    Protocolo,
    TipoAssunto,
    EDOCBoxManager,
)
from edocs.protocolo.models import (
    TipoDocumento,
    Referencia,
    Impressora,
    ProtocoloManager,
    MovimentacaoManager,
)
from rh.views import RHPessoa, RHLotacao
from rh.models import (
    Pessoa,
    PessoaFisica,
    Servidor,
    Lotacao,
    OrgaoGeral,
    ServidorLotacao,
)


json = get_json_engine()
log = getLogger(__name__)


class CustomAutocomplete(extjs.ExtCrud):

    def autocomplete(self, args=[]):
        qs = []
        model = None
        obj = {}

        """"""
        if len(args) > 0:
            if args[0] == "Pessoa":
                model = Pessoa
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(nome__icontains=self.request.POST.get("query", "")))
            elif args[0] == "OrgaoGeral":
                model = None
                if "pk" in self.request.POST:
                    q = Q(pk=int(self.request.POST.get("pk", 0)))
                elif ServidorLotacao.work_assignment_exercise().filter(
                    servidor=Servidor.objects.get(user=self.request.user),
                    lotacao__acesso_protocolo_geral=True,
                ):
                    q = Q(nome__icontains=self.request.POST.get("query", "")) | Q(
                        descricao__icontains=self.request.POST.get("query", "")
                    )
                else:
                    q = Q(lotacao__pk__in=self.get_lotacoes_servidor())
                obj = {"result": []}
                for row in OrgaoGeral.objects.filter(q):
                    obj["result"].append({"pk": row.pk, "description": str(row)})
            elif args[0] == "Protocolo":
                servidor = Servidor.objects.get(user=self.request.user)
                model = None
                if "pk" in self.request.POST:
                    q = Q(pk=int(self.request.POST.get("pk", 0)))
                else:
                    q1 = Q(protocolo__interessado=self.get_servidor().pessoa_fisica.pk)
                    q2 = Q(servidor_origem=self.get_servidor().pk)
                    q3 = Q(destinatario=self.get_servidor().pessoa_fisica.pk)
                    q4 = Q(
                        lotacao_destino__in=ServidorLotacao.work_assignment_exercise()
                        .filter(servidor=servidor)
                        .values("lotacao")
                    )
                    q = Q(Q(q1 | q2 | q3 | q4) & ~Q(protocolo__data_finalizado=None))
                    protocolo = Movimentacao.objects.filter(q).values("protocolo")
                    obj = {"result": []}
                    for row in Protocolo.objects.filter(pk__in=protocolo):
                        obj["result"].append({"pk": row.pk, "description": str(row)})
        """"""

        if model is not None and len(qs) > 0:
            q = None
            for qn in qs:
                q = qn if q is None else Q(q | qn)
            obj.update(
                result=[
                    {"pk": r.pk, "description": str(r)} for r in model.objects.filter(q)
                ]
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class EDOCAnexo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        arquivo = FileUploadField(label="Arquivo", required=False)

        class Meta:
            model = Anexo
            exclude = [
                "movimentacao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Anexo",
        "LIST": "Gerenciador de Anexo",
        "NEW": "Novo(a) Anexo",
        "EDIT": "Editando um(a) Anexo",
        "DELETE": "Removendo um(a) Anexo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Arquivo",
                "sortable": True,
                "dataIndex": "arquivo",
                "key": "arquivo",
                "width": 240,
            },
            {
                "header": "Movimentação",
                "sortable": True,
                "dataIndex": "movimentacao",
                "key": "movimentacao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))

    def get_query(self):
        return Anexo.objects.filter(arquivo__user=self.request.user)


class EDOCTipoAssunto(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = TipoAssunto
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Tipo de Assunto",
        "LIST": "Gerenciador de Tipo de Assunto",
        "NEW": "Novo(a) Tipo de Assunto",
        "EDIT": "Editando um(a) Tipo de Assunto",
        "DELETE": "Removendo um(a) Tipo de Assunto",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class EDOCTipoDocumento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            model = TipoDocumento
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "descricao",
                "width": 360,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Tipo de Documento",
        "LIST": "Gerenciador de Tipo de Documento",
        "NEW": "Novo(a) Tipo de Documento",
        "EDIT": "Editando um(a) Tipo de Documento",
        "DELETE": "Removendo um(a) Tipo de Documento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Informações",
            "field": [
                "interessado",
                "assunto",
                "orgao_geral_origem",
                "orgao_geral_destino",
                "tipo_documento",
                "protocolo_externo",
                "resumo",
            ],
        },
        {"title": "Referências", "field": ["referencias"]},
    ]
)
class EDOCProtocolo(extjs.ExtCrud):
    class Form(forms.ModelForm):
        resumo = forms.CharField(
            label="Resumo", max_length=2000, required=False, widget=forms.Textarea
        )
        interessado = AutoCompleteField(
            model=Pessoa, controller=RHPessoa, label="Interessado", required=False
        )
        servidor_origem = AutoCompleteField(model=Servidor, label="Servidor")

        class Meta:
            model = Protocolo
            exclude = [
                "lotacao",
                "codigo",
                "data_criacao",
                "deferido",
                "encaminhado",
                "grupo",
                "habilitado",
                "propriedade",
                "serial",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Protocolo",
        "LIST": "Gerenciador de Protocolo",
        "NEW": "Novo(a) Protocolo",
        "EDIT": "Editando um(a) Protocolo",
        "DELETE": "Removendo um(a) Protocolo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args):
        buf = """
        [{'header': 'Chave', 'sortable': true, 'dataIndex': 'id', 'key': 'id'},
         {'header': 'Código', 'sortable': true, 'dataIndex': 'codigo', 'key': 'codigo'},
         {'header': 'Interessando', 'sortable': true, 'dataIndex': 'interessado', 'key': 'interessado'},
         {'header': 'Órgão', 'sortable': true, 'dataIndex': 'orgao_geral_origem', 'key': 'orgao_geral_origem'},
         {'header': 'Resumo', 'sortable': true, 'dataIndex': 'resumo', 'key': 'resumo'}
        ]"""
        self.response["ContextType"] = "text/javascript"
        self.response.write(buf)

    def csv(self, args=[]):
        texto = ""
        for p in Protocolo.objects.filter(
            Q(servidor_origem=Servidor.objects.get(matricula=67807))
        ).order_by("data_criacao"):
            texton = """{codigo}|{data_criacao}\n""".format(
                codigo=str(p.codigo),
                data_criacao=str(p.data_criacao.strftime("%d/%m/%Y")),
            )
            texto += texton
        self.response["content-type"] = "text/javascript"
        self.response.write(texto)


class EDOCReferencia(CustomAutocomplete, extjs.ExtCrud):
    class Form(forms.ModelForm):
        protocolo = AutoCompleteField(
            model=Protocolo, controller=EDOCProtocolo, label="Protocolo"
        )

        class Meta:
            model = Referencia
            exclude = [
                "movimentacao",
                "created_at",
                "modified_by",
                "created_by",
                "modified_at",
            ]

    titles = {
        "PANEL": "Referência",
        "LIST": "Gerenciador de Referência",
        "NEW": "Novo(a) Referência",
        "EDIT": "Editando um(a) Referência",
        "DELETE": "Removendo um(a) Referência",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_query(self):
        servidor = Servidor.objects.get(user=self.request.user)
        lotacao = servidor.work_locations
        q = Q(
            Q(movimentacao__protocolo__interessado=servidor.pessoa_fisica.pk)
            | Q(movimentacao__servidor_origem=servidor)
            | Q(movimentacao__destinatario=servidor)
            | Q(movimentacao__lotacao_destino__in=lotacao)
        )
        return Referencia.objects.filter(q)


class EDOCBox(CustomAutocomplete, extjs.ExtWidget):

    lotacoes = []

    lotacoes_protocolo_geral = []

    servidor = None

    """
    ############################################
    AÇÕES INÍCIO
    ############################################
    """

    @login_required(type="JSON")
    def json(self, args=[]):
        write = "new toolkit.edocs.protocolo.Box(false)"
        try:
            if (
                self.get_servidor()
                .work_assignment.filter(lotacao__acesso_protocolo_geral=True)
                .exists()
            ):
                write = "new toolkit.edocs.protocolo.Box(true)"
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(write)

    @login_required(type="JSON")
    def finalizar(self, args=[]):
        """
        Este método é responsável por finalizar o Protocolo.
        @return json - Retorna {'success': True/False, 'msg': ''} com a resposta do procedimento.
        """
        obj = {"success": True, "msg": ""}
        try:
            MovimentacaoManager.finalizar(
                self.get_movimentacao_from_post(),
                (
                    self.request.POST.get("servidor")
                    if self.request.POST.get("servidor")
                    else self.get_servidor().pk
                ),
            )
        except Exception as e:
            self.log.exception(e)
            obj = {"success": False, "msg": str(e)}
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def desfazer_envio(self, args=[]):
        """
        Este método é responsável por desfazer a movimentação de alguns protocolos.
        @return json - Retorna {'success': True/False } com a resposta.
        """
        obj = {"success": True}
        try:
            MovimentacaoManager.desfazer_envio(
                MovimentacaoManager.get_movimentacao(self.get_movimentacao_from_post())
            )
        except Exception as e:
            self.log.exception(e)
            obj = {"success": False, "msg": str(e)}
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def receber(self, args=[]):
        """
        Este método é responsável por receber as movimentações dos Protocolos.
        @return json - Retorna obj = { 'msg': '', 'success': True } como resposta.
        """
        obj = {"msg": "", "success": True}
        linelog = LineLog(level=66, status=1)
        linelog.read_request(self.request)
        try:
            MovimentacaoManager.receber(
                self.get_movimentacao_from_post(), self.get_servidor()
            )
        except Exception as e:
            self.log.exception(e)
            linelog.json_description["messageException"] = str(e)
            linelog.status = 0
            obj = {"success": False, "msg": str(e)}
        linelog.save()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def marcar_nao_recebido(self, args=[]):
        """
        Este método é responsável por marcar, as movimentações dos Protocolos, como não recebido.
        @return json - Retorna obj = { 'msg': '', 'success': True } como resposta.
        """
        obj = {"msg": "", "success": True}
        linelog = LineLog(level=72, status=1)
        linelog.read_request(self.request)
        try:
            MovimentacaoManager.marcar_nao_recebido_movimentacao(
                self.get_movimentacao_from_post(), self.get_servidor()
            )
        except Exception as e:
            self.log.exception(e)
            linelog.json_description["messageException"] = str(e)
            linelog.status = 0
            obj = {"success": False, "msg": str(e)}
        linelog.save()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def view(self, args=[]):
        obj = {}
        try:
            if args[0] == "geral":
                obj = self.view_geral(self.request.POST.get("codigo"))
            elif args[0] == "movimentos":
                obj = self.view_movimentos(self.request.POST.get("codigo"))
        except Exception as e:
            self.log.exception(e)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def permissao_protocolo(self, args=[]):
        """
        Este método verifica as permissões sobre o protocolo e retorna uma resposta.
        """
        obj = {"perm_envio": True, "msg": ""}
        try:
            MovimentacaoManager.permissao_movimentacao(
                self.request.POST.getlist("selecteds")
            )
        except Exception as e:
            self.log.exception(e)
            obj = {"perm_envio": False, "msg": str(e)}
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def carregar_protocolo(self, args=[]):
        """
        Este método encontra o protocolo, verifica as permissões e o retorna.
        """
        try:
            result, perm_envio, message = ProtocoloManager.carregar_protocolo(
                self.get_movimentacao_from_post(), self.request.POST.get("codigo")
            )
        except Exception as e:
            self.log.exception(e)
            result, perm_envio, message = [], False, ""
        obj = {"result": result, "perm_envio": perm_envio, "msg": message}
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def commit(self, args=[]):
        obj = {}
        if len(args) > 0 and args[0] == "novo_protocolo":
            obj = self.novo_protocolo()
        elif len(args) > 0 and args[0] == "nova_movimentacao":
            obj = self.nova_movimentacao()
        elif len(args) > 0 and args[0] == "nova_movimentacao_lote":
            obj = self.nova_movimentacao_lote()
        elif len(args) > 0 and args[0] == "imprimir":
            obj = self.imprimir()
        elif len(args) > 0 and args[0] == "delete_protocolo":
            obj = self.delete_protocolo()
        elif len(args) > 0 and args[0] == "new_conf":
            obj = self.new_commit_conf()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def validate(self, args=[]):
        obj = {}
        if len(args) > 0 and args[0] == "novo_protocolo":
            obj = self.novo_protocolo_validate()
        elif len(args) > 0 and args[0] == "nova_movimentacao":
            obj = self.nova_movimentacao_validate()
        elif len(args) > 0 and args[0] == "nova_movimentacao_lote":
            obj = self.nova_movimentacao_validate_lote()
        elif len(args) > 0 and args[0] == "imprimir":
            obj = self.validate_imprimir()
        elif len(args) > 0 and args[0] == "new_conf":
            obj = self.new_validate_conf()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_store(self, args=[]):
        obj = {"result": []}
        try:
            if args:
                store = {
                    "in": self.get_store_in,
                    "out": self.get_store_out,
                    "movimentar": self.get_store_movimentar,
                    "tipo_documento": self.get_store_tipo_documento,
                    "destino": self.get_store_destino,
                    "protocolo": self.get_store_protocolo,
                    "dados_protocolo": self.get_store_dados_protocolo,
                    "impressora": self.get_store_impressora,
                    "midia": self.get_store_midia_origem,
                    "orgao_geral_origem": self.get_store_orgao_geral_origem,
                    "not": self.get_store_not,
                }
                obj = store.get(args[0])()
        except Exception as e:
            self.log.exception(e)

        if not obj:
            obj = store.get("not")()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_parecer(self, args=[]):
        """
        Este método retorna o parecer da Movimentacao.
        """
        obj = {"parecer": "Parecer não encontrado."}
        try:
            obj = {
                "parecer": str(
                    MovimentacaoManager.get_movimentacao(
                        self.get_movimentacao_from_post()
                    ).parecer
                )
            }
        except Exception as e:
            self.log.exception(e)
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_conf_values(self, args=[]):
        obj = {"pessoa_dono": None, "pessoa": [], "permissao": []}
        try:
            comp_caixa = CompartilharCaixa.objects.get(
                pessoa_fisica_dono=self.get_servidor().pessoa_fisica
            )
            obj["pessoa_dono"] = comp_caixa._fisica_dono.pk
            for p in comp_caixa.pessoa_fisica.all():
                pessoa = {"pk": p.pk, "description": p.nome}
                obj["pessoa"].append(pessoa)
            for p in comp_caixa.permissao.all():
                permissao = {"pk": p.pk, "description": p.nome}
                obj["permissao"].append(permissao)
        except Exception as e:
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def novo_protocolo(self):
        obj = {"result": True, "errors": []}
        linelog = LineLog(level=67, status=1)
        linelog.read_request(self.request)
        try:
            ProtocoloManager.novo_protocolo(
                {
                    "servidor": self.get_servidor().pk,
                    "tipo_documento": self.request.POST.get("tipo_documento"),
                    "orgao_geral": self.request.POST.get("orgao_geral_origem"),
                    "interessado": self.get_interessado_from_post(),
                    "codigo": self.request.POST.get("codigo"),
                    "chancela": self.request.POST.get("chancela", None),
                    "midia": self.request.POST.get("midia", None),
                    "assunto": self.request.POST.get("assunto", None),
                    "numero_externo": self.request.POST.get("numero_externo", None),
                    "resumo": self.request.POST.get("resumo"),
                    "anexos": self.get_anexos_from_post(),
                    "referencias": self.get_referencias_from_post(),
                }
            )
        except Exception as e:
            self.log.exception(e)
            obj = {"result": False, "message": str(e)}
            linelog.json_description["messageException"] = obj["message"]
            linelog.status = 0
        linelog.save()
        return obj

    @login_required(type="JSON")
    def nova_movimentacao_lote(self):
        """
        Este método recebe o pedido para movimentação em lote e
        realiza a movimentação de cada Movimentacao.
        """
        obj = {"success": True, "result": [], "msg": ""}

        try:
            with transaction.atomic():
                for pk in self.request.POST.getlist("selecteds"):
                    movimentacao = MovimentacaoManager.get_movimentacao(int(pk or 0))
                    MovimentacaoManager.is_movimentacao(movimentacao)
                    self.request.POST = {
                        "protocolo": movimentacao.protocolo.pk,
                        "movimentacao": movimentacao.pk,
                        "pessoa": self.get_pessoas_from_post(),
                        "lotacao_destino": self.get_lotacao_destino_from_post(),
                        "parecer": self.request.POST.get("parecer"),
                    }
                    if MovimentacaoManager.is_recebido(movimentacao):
                        obj_return = self.nova_movimentacao()
                        if not obj_return.get("result", None):
                            raise Exception(obj_return.get("message"))
                    else:
                        raise Exception(
                            "Antes de movimentar o protocolo %s é necessário recebê-lo!"
                            % movimentacao.protocolo.codigo
                        )
        except Exception as err:
            obj.update(success=False, msg=str(err))
            raise err

        return obj

    @login_required(type="JSON")
    def nova_movimentacao(self):
        obj = {"result": True, "message": ""}
        pessoa_lotacoes = []
        lotacoes_destino = []
        servidor_lotacoes = []
        result_lotacao, message_lotacao = True, ""
        result_pessoa, message_pessoa = True, ""

        linelog = LineLog(level=68, status=0)
        linelog.read_request(self.request)

        try:
            protocolo = ProtocoloManager.get_protocolo(
                self.request.POST.get("protocolo", None)
            )
            ProtocoloManager.is_protocolo(protocolo)

            # if protocolo.com_workflow:
            #     raise Exception('Este protocolo não pode ser movimentado por aqui. Ele possui software especifico para isto.')

            self.is_destino_definido_from_post()

            if self.is_destino_nao_definido_and_concluido_definido_from_post():
                try:
                    servidor_lotacoes = [
                        [protocolo.interessado.pk, protocolo.orgao_geral_origem.pk]
                    ]
                except:
                    pass
            else:
                servidor_lotacoes, pessoa_lotacoes = (
                    self.get_servidor_lotacoes_e_pessoa_lotacoes_from_post()
                )

            movimentacao = MovimentacaoManager.get_movimentacao(
                self.request.POST.get("movimentacao", None)
            )
            if movimentacao.with_workflow:
                raise Exception(
                    "Este protocolo não pode ser movimentado por aqui. Ele possui software especifico para isto."
                )
            MovimentacaoManager.is_movimentacao(movimentacao)

            lotacoes_destino = self.remove_lotacao_da_pessoa(pessoa_lotacoes)

            EDOCBoxManager.is_lotacoes_em_organograma(lotacoes_destino)

            self.is_destino(lotacoes_destino, pessoa_lotacoes, servidor_lotacoes)

            deferido = self.get_deferido_from_post()
            urgente = True if self.request.POST.get("urgente", False) == "on" else False
            data_encaminhamento = datetime.now()
            data_finalizado = (
                data_encaminhamento if self.is_concluido_from_post() else None
            )
            parecer = self.get_parecer_from_post(data_encaminhamento)

            kwargs = {
                "movimentacao_pk": movimentacao.pk,
                "protocolo": protocolo,
                "orgao_geral_origem": MovimentacaoManager.get_lotacao_origem(
                    movimentacao
                ).pk,
                "servidor_origem": self.get_servidor().pk,
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
            if servidor_lotacoes:
                kwargs.update({"servidor_lotacao_destino": servidor_lotacoes})
                result_pessoa, message_pessoa = (
                    MovimentacaoManager.envia_movimentacao_por_pessoa(kwargs)
                )

            if (result_lotacao is False) and (result_pessoa is False):
                raise Exception(message_lotacao + message_pessoa)
            else:
                self.log.debug("=> %(protocolo)s", kwargs)
                MovimentacaoManager.envia_finalizado_interessado(kwargs)

            if not ProtocoloManager.set_anexo(
                self.get_anexos_from_post(), movimentacao
            ):
                raise Exception("Anexos não incluídos! Tente novamente!")

            if not ProtocoloManager.set_referencia(
                self.get_referencias_from_post(), protocolo
            ):
                raise Exception("Referências não incluídas! Tente novamente!")

            protocolo.deferido = deferido
            protocolo.save()

            linelog.status = 1
            # TODO: CONSTRUIR ESQUEMA DE TRANSAÇÃO PARA ESTE PROCESSO
        except Exception as e:
            linelog.json_description["messageException"] = str(e)
            self.log.exception(str(e))
            obj["result"] = False
            obj["message"] = str(e)
        linelog.save()
        return obj

    def printer_device_zebra(self, printer, moviment):
        host = xmlrpc.client.ServerProxy(
            "http://{0}:{1}".format(printer.host, printer.port)
        )
        destino = (
            moviment.destinatario.nome
            if moviment.destinatario
            else moviment.lotacao_destino.nome
        )

        rst = host.impP(
            {
                "assunto": clear_to_ascii(moviment.protocolo.assunto),
                "entrada": moviment.protocolo.data_criacao.strftime("%d/%m/%Y %H:%M"),
                "origem": clear_to_ascii(moviment.protocolo.orgao_geral_origem.nome),
                "destino": clear_to_ascii("NFKD", destino),
                "codigo": moviment.protocolo.codigo,
            },
            int(self.request.POST.get("quantidade")),
        )

        log.debug("%s" % rst)

        if not rst:
            return {"success": False, "msg": "=== Erro na máquina de impressão ==="}
        else:
            return {"success": True}

    def printer_device_tsc_m240(self, printer, moviment):
        destino = (
            moviment.destinatario.nome
            if moviment.destinatario
            else moviment.lotacao_destino.nome
        )
        tpl = "\n".join(
            [
                "CLS",
                'BARCODE 5,30,"128M",70,0,0,2,1,"%(codigo)s"',
                'TEXT 30,5,"0",0,6,7,"PROCURADORIA GERAL DE JUSTICA DO ESTADO DO TOCANTINS"',
                'TEXT 295,105,"0",0,7,7,"%(codigo)s"',
                'TEXT 5,110,"0",0,8,8,"ENTRADA: %(entrada)s"',
                'TEXT 5,140,"0",0,8,8,"ASSUNTO: %(assunto)s"',
                'TEXT 5,170,"0",0,8,8,"INTERESSADO: %(interessado)s"',
                'TEXT 5,200,"0",0,8,8,"DESTINO: %(destino)s"',
                "PRINT 1,%(quantidade)d",
                "",
            ]
        )

        params = {
            "assunto": clear_to_ascii(moviment.protocolo.assunto),
            "entrada": DateUtils.datetime_to_str(moviment.protocolo.data_criacao),
            "codigo": moviment.protocolo.codigo,
            "interessado": clear_to_ascii(moviment.protocolo.interessado.nome),
            "destino": clear_to_ascii(destino),
            "quantidade": int(self.request.POST.get("quantidade") or 0),
        }

        try:
            fd = sck.create_connection((printer.host, printer.port))
            tpl_send = (tpl % params).encode()
            fd.send(tpl_send)
            fd.close()
        except Exception as e:
            return {"success": False, "msg": str(e)}
        else:
            return {"success": True}

    @login_required(type="JSON")
    def imprimir(self):
        obj = {"result": True, "errors": []}
        device_router = {1: self.printer_device_zebra, 2: self.printer_device_tsc_m240}

        try:
            printer = Impressora.objects.get(
                pk=int(self.request.POST.get("impressora"))
            )
            moviment = Movimentacao.objects.get(
                pk=int(self.request.POST.get("movimentacao"))
            )
            obj = device_router.get(printer.driver, lambda x, y: None)(
                printer, moviment
            )
        except Exception as err:
            self.log.exception(err)
        return obj

    @login_required(type="JSON")
    def delete_protocolo(self):
        obj = {"result": True, "errors": []}
        linelog = LineLog(level=65, status=0)
        linelog.read_request(self.request)
        try:
            ProtocoloManager.delete_protocolo(self.request.POST.get("protocolo"))
            linelog.status = 1
        except Exception as e:
            self.log.exception(e)
            obj = {"result": False, "message": str(e)}
            linelog.json_description["messageException"] = obj["message"]
        linelog.save()
        return obj

    """
    ################
    FIM AÇÕES
    ################
    """

    def view_geral(self, codigo):
        obj = {}
        try:
            pt = Protocolo.objects.get(codigo=codigo)
            obj = {
                "numero": pt.codigo,
                "protocolo_externo": str(pt.protocolo_externo),
                "chancela": (
                    pt.chancela is None and "NÃO FOI CHANCELADO" or pt.chancela
                ),
                "midia": self.get_midia(pt.midia),
                "assunto": str(pt.assunto),
                "tipo": str(pt.tipo_documento),
                "origem": str(pt.servidor_origem),
                "interessado": self.get_interessado(pt),
                "resumo": pt.resumo,
                "anexos": self.get_anexos(pt, self.get_servidor()),
                "referencias": ProtocoloManager.get_referencias(pt),
                "referenciado_por": ProtocoloManager.get_referenciado_por(pt),
                "com_copia_para": "",
            }
        except Exception as e:
            self.log.exception(e)
        return obj

    def view_movimentos(self, codigo):
        obj = {"totalRows": 0, "result": []}
        try:
            mv = Movimentacao.objects.filter(protocolo__codigo=codigo).order_by(
                "-passo"
            )
            obj["totalRows"] = mv.count()
            start = int(self.request.POST.get("start", 0))
            end = start + int(self.request.POST.get("limit", 50))
            mv = mv[start:end]
            if not mv is None and len(mv) > 0:
                for m in mv:
                    item = {
                        "movimentacao": "",
                        "encaminhado": "",
                        "encaminhado_por": "",
                        "encaminhado_para": "",
                        "recebido": "",
                        "recebido_por": "",
                    }
                    item["movimentacao"] = m.pk
                    if not m.data_encaminhamento is None:
                        item["encaminhado"] = m.data_encaminhamento.strftime(
                            "%d/%m/%Y %H:%M"
                        )
                        item["encaminhado_por"] = (
                            str(m.servidor_origem) + " - " + str(m.lotacao_origem)
                        )
                        item["encaminhado_para"] = (
                            (not m.destinatario is None and str(m.destinatario) or "")
                            + " - "
                            + (
                                not m.lotacao_destino is None
                                and str(m.lotacao_destino)
                                or ""
                            )
                        )
                    if not m.data_recebimento is None:
                        item["recebido"] = m.data_recebimento.strftime("%d/%m/%Y %H:%M")
                        item["recebido_por"] = (
                            str(m.servidor_destino.pessoa_fisica)
                            if m.servidor_destino
                            else ""
                        )
                    else:
                        item["recebido"] = ""
                    obj["result"].append(item)
        except:
            self.log.exception("Protocolo não encontrado!")
        return obj

    def novo_protocolo_validate(self):
        obj = {"result": True, "errors": []}
        if not "assunto" in self.request.POST or self.request.POST.get("assunto") == "":
            obj["errors"].append(
                {"field": "assunto", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        if (
            not "tipo_documento" in self.request.POST
            or self.request.POST.get("tipo_documento") == ""
        ):
            obj["errors"].append(
                {"field": "tipo_documento", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        return obj

    def nova_movimentacao_validate_lote(self):
        obj = {"result": True, "errors": []}
        if (
            not "lotacao_destino" in self.request.POST
            or self.request.POST.get("lotacao_destino") == ""
        ) and (
            not "pessoa" in self.request.POST or self.request.POST.get("pessoa") == ""
        ):
            obj["errors"].append(
                {
                    "field": "lotacao_destino",
                    "message": "É necessário preencher o campo Enviar p/ Lotação ou Enviar p/ pessoa para enviar",
                }
            )
            obj["result"] = False
        return obj

    def nova_movimentacao_validate(self):
        obj = {"result": True, "errors": []}
        if (
            not "protocolo" in self.request.POST
            or self.request.POST.get("protocolo") == ""
        ):
            obj["errors"].append(
                {"field": "protocolo", "message": "Este campo é obrigatório."}
            )
            obj["result"] = False
        if (
            not "lotacao_destino" in self.request.POST
            or self.request.POST.get("lotacao_destino") == ""
        ) and (
            not "pessoa" in self.request.POST or self.request.POST.get("pessoa") == ""
        ):
            if not "concluir" in self.request.POST:
                obj["errors"].append(
                    {
                        "field": "lotacao_destino",
                        "message": "É necessário preencher o campo Enviar p/ Lotação ou Enviar p/ pessoa para enviar",
                    }
                )
                obj["result"] = False
        return obj

    def validate_imprimir(self):
        obj = {"success": True, "msg": "", "errors": []}
        if (
            not "impressora" in self.request.POST
            or self.request.POST.get("impressora") == ""
        ):
            obj["errors"].append(
                {"field": "impressora", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        if (
            not "quantidade" in self.request.POST
            or self.request.POST.get("quantidade") == ""
        ):
            obj["errors"].append(
                {"field": "quantidade", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        return obj

    def new_validate_conf(self):
        obj = {"result": True, "errors": []}
        if not "pessoa" in self.request.POST or self.request.POST.get("pessoa") == "":
            obj["errors"].append(
                {"field": "pessoa", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        if (
            not "permissao" in self.request.POST
            or self.request.POST.get("permissao") == ""
        ):
            obj["errors"].append(
                {"field": "permissao", "messsage": "Este campo é obrigatório."}
            )
            obj["result"] = False
        return obj

    def get_anexos_from_post(self):
        if "anexos" in self.request.POST:
            return self.request.POST.getlist("anexos")
        return []

    def get_referencias_from_post(self):
        if "referencias" in self.request.POST:
            return self.request.POST.getlist("referencias")
        return []

    @classmethod
    def get_interessado(cls, protocolo):
        return str(protocolo.interessado) + " - " + str(protocolo.orgao_geral_origem)

    def get_pessoas_from_post(self):
        """
        Este método retorna uma lista com pk(s) das Pessoas que foram selecionadas para receber a Movimentacao.
        @return list - Lista com o(s) pk(s). Lista vazia se nenhuma foi selecionada.
        """
        try:
            if "pessoa" in self.request.POST:
                try:
                    return self.request.POST.getlist("pessoa")
                except:
                    try:
                        return (
                            self.request.POST.get("pessoa")
                            if isinstance(self.request.POST.get("pessoa"), list)
                            else [self.request.POST.get("pessoa")]
                        )
                    except:
                        return self.request.POST["pessoa"]
        except Exception as e:
            self.log.exception(e)
        return []

    def get_lotacao_destino_from_post(self):
        """
        Este método retorna uma lista com o(s) pk(s) das Lotacao(s) que foram selecionadas para receber Movimentacao.
        @param post - POST.
        @return list - Lista com o(s) pk(s).
        """
        if "lotacao_destino" in self.request.POST:
            try:
                return self.request.POST.getlist("lotacao_destino")
            except:
                try:
                    return (
                        self.request.POST.get("lotacao_destino")
                        if isinstance(self.request.POST.get("lotacao_destino"), list)
                        else [self.request.POST.get("lotacao_destino")]
                    )
                except:
                    return self.request.POST["lotacao_destino"]
        return []

    def remove_lotacao_da_pessoa(self, lotacao_pessoa):
        """
        Este método remove todas lotações que se relacionam com Pessoa, para que ela não receba um documento duas vezes.
        @param list - Lista de lotações das pessoas.
        @return list - Lista com o(s) pk(s).
        """
        lotacoes_destino = self.get_lotacao_destino_from_post()
        if lotacoes_destino:
            for l in lotacao_pessoa:
                if l in lotacoes_destino:
                    lotacoes_destino.remove(lotacoes_destino.index(str(l)))
        return lotacoes_destino

    def new_commit_conf(self):
        obj = {"result": True, "errors": []}
        try:
            pessoa = self.request.POST.getlist("pessoa") or None
            permissao = self.request.POST.getlist("permissao") or None
            comp_caixa = CompartilharCaixa(
                pessoa_fisica_dono=self.get_servidor().pessoa_fisica
            )
            comp_caixa.save()
            for p in pessoa:
                comp_caixa.pessoa_fisica.add(PessoaFisica.objects.get(pk=int(p)))
            for p in permissao:
                comp_caixa.permissao.add(PermissaoEdoc.objects.get(pk=int(p)))
            comp_caixa.save()
        except Exception as e:
            obj = {"result": False, "errors": str(e)}
        return obj

    def get_sort_movimentacao(self, movimentacao):
        if "sort" in self.request.POST:
            translate = {
                "codigo": "protocolo__codigo",
                "protocolo_externo": "protocolo__protocolo_externo",
                "midia": "protocolo__midia",
                "chancela": "protocolo__chancela",
                "interessado": "protocolo__interessado",
                "assunto": "protocolo__assunto",
                "data": "data_encaminhamento",
            }
            if self.request.POST.get("dir") == "ASC":
                movimentacao = movimentacao.order_by(
                    "%s" % translate.get(self.request.POST.get("sort"), "id")
                )
            else:
                movimentacao = movimentacao.order_by(
                    "-%s" % translate.get(self.request.POST.get("sort"), "id")
                )
        else:
            movimentacao = movimentacao.order_by("-data_encaminhamento")
        return movimentacao

    @classmethod
    def get_informacao_caixa(cls, movimentacao):
        # log.debug(movimentacao.protocolo.com_workflow)
        return {
            "status": {
                "recebido": MovimentacaoManager.is_recebido(movimentacao),
                "attache": Anexo.objects.filter(
                    movimentacao__protocolo=movimentacao.protocolo
                ).exists(),
                "urgente": movimentacao.urgente,
                "finalizado": ProtocoloManager.is_finalizado(movimentacao),
                "compartilhado": False,
                "locked": movimentacao.with_workflow,
            },
            "codigo": movimentacao.protocolo.codigo,
            "protocolo_externo": movimentacao.protocolo.protocolo_externo != None
            and movimentacao.protocolo.protocolo_externo
            or "",
            "chancela": movimentacao.protocolo.chancela != None
            and movimentacao.protocolo.chancela
            or "",
            "midia": cls.get_midia(movimentacao.protocolo.midia),
            "movimentacao": movimentacao.pk,
            "data": (
                movimentacao.data_encaminhamento.strftime("%d/%m/%Y %H:%M:%S")
                if movimentacao.data_encaminhamento
                else ""
            ),
            "interessado": cls.get_interessado(movimentacao.protocolo),
            "origem": str(movimentacao.servidor_origem)
            + " - "
            + str(movimentacao.lotacao_origem),
            "posicao": (
                not movimentacao.destinatario is None
                and str(movimentacao.destinatario)
                or ""
            )
            + " - "
            + (
                not movimentacao.lotacao_destino is None
                and str(movimentacao.lotacao_destino)
                or ""
            ),
            "assunto": (
                str(movimentacao.protocolo.assunto)
                if not movimentacao.protocolo.assunto is None
                else ""
            ),
            "passo": movimentacao.passo,
        }

    def constroe_caixa_entrada(self):
        """
        Este método constroe a caixa de entrada.
        """

        movimentacao = EDOCBoxQuery(
            servidor=self.get_servidor(),
            lotacoes=self.get_lotacoes_servidor(),
            valor=self.request.POST.get("valor", None),
            lotacoes_protocolo_geral=self.get_lotacoes_servidor_protocolo_geral(),
        ).get_caixa_entrada()

        movimentacao = movimentacao.exclude(EDOCBoxQuery.get_finalizado_recebido())
        movimentacao = movimentacao.filter(protocolo__processo=None)

        obj = {"totalRows": movimentacao.count(), "result": []}
        start = int(self.request.POST.get("start", 0))
        end = start + int(self.request.POST.get("limit", 50))

        movimentacao = self.get_sort_movimentacao(movimentacao)
        for mov in movimentacao[start:end]:
            obj["result"].append(self.get_informacao_caixa(mov))
        return obj

    def constroe_caixa_saida(self):
        """
        Este método constroe a caixa de saída.
        """
        movimentacao = EDOCBoxQuery(
            servidor=self.get_servidor(),
            lotacoes=self.get_lotacoes_servidor(),
            valor=self.request.POST.get("valor", None),
            lotacoes_protocolo_geral=self.get_lotacoes_servidor_protocolo_geral(),
        ).get_caixa_saida()

        obj = {"totalRows": movimentacao.count(), "result": []}
        start = int(self.request.POST.get("start", 0))
        end = start + int(self.request.POST.get("limit", 50))

        movimentacao = self.get_sort_movimentacao(movimentacao)
        query = movimentacao[start:end]
        for mov in query:
            obj["result"].append(self.get_informacao_caixa(mov))
        return obj

    def is_destino_definido_from_post(self):
        """
        Este método verifica se o destino foi preenchido no POST.
        Caso esteja sendo concluído, não há necessidade de preencher.
        """
        if (not "lotacao_destino" in self.request.POST) and (
            not "pessoa" in self.request.POST
        ):
            if not self.is_concluido_from_post():
                raise Exception("Escolher Pessoa ou Lotação para enviar.")
        return True

    def is_destino_nao_definido_and_concluido_definido_from_post(self):
        """
        Este método verifica se o destino foi preenchido no POST.
        Caso esteja sendo concluído, não há necessidade de preencher.
        """
        if (
            (not "lotacao_destino" in self.request.POST)
            and (not "pessoa" in self.request.POST)
            and self.is_concluido_from_post()
        ):
            return True
        return False

    def is_concluido_from_post(self):
        """
        Este método verifica se a movimentação foi concluída no POST.
        """
        return True if "concluir" in self.request.POST else False

    def is_deferido_from_post(self):
        """
        Este método verifica se a movimentação foi deferida no POST.
        """
        return True if "deferido" in self.request.POST else False

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

    def get_deferido_from_post(self):
        deferido = None
        if self.is_deferido_from_post():
            deferido = (
                False
                if self.request.POST.get("deferido") in ("False", "False")
                else True
            )
        return deferido

    def get_parecer_from_post(self, data_encaminhamento):
        """
        Este método retorna o parecer da movimentação informado no POST.
        """
        parecer = self.request.POST.get("parecer", None)
        if self.is_concluido_from_post():
            if parecer == "" or parecer is None:
                if self.get_servidor().matricula == 0:
                    parecer = "Movimentação finalizada em {0} pelo software limpeza da caixa de entrada.".format(
                        data_encaminhamento.strftime("%d/%m/%Y %H:%M")
                    )
                else:
                    parecer = "Movimentacação finalizada em {0}.".format(
                        data_encaminhamento.strftime("%d/%m/%Y %H:%M")
                    )
        return parecer

    def get_servidor_lotacoes_e_pessoa_lotacoes_from_post(self):
        """
        Este método retorna as lotações dos servidores e os òrgãos de origem das pessoas.
        Apresenta exceção caso não haja destino.
        """
        pessoas_id = self.get_pessoas_from_post()
        servidor_lotacoes, pessoa_lotacoes = self.get_lotacao_da_pessoa_from_post(
            pessoas_id
        )
        if pessoas_id and (not servidor_lotacoes or not pessoa_lotacoes):
            raise Exception(
                "Protocolo não movimentado! Impossível enviar às Pessoas selecionadas."
            )
        return servidor_lotacoes, pessoa_lotacoes

    def get_interessado_from_post(self):
        """
        Este método retorna o interessado definido no POST.
        """
        interessado = None
        try:
            if "interessado" in self.request.POST:
                interessado = Pessoa.objects.get(
                    pk=int(self.request.POST.get("interessado"))
                )
        except:
            pass
        interessado = (
            interessado != None
            and interessado.pk
            or self.get_servidor().pessoa_fisica.pessoa_ptr.pk
        )
        return interessado

    def get_store_in(self):
        obj = {"totalRows": 0, "result": []}
        try:
            obj = self.constroe_caixa_entrada()
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_out(self):
        obj = {"totalRows": 0, "result": []}
        try:
            obj = self.constroe_caixa_saida()
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_movimentar(self):
        obj = {"result": []}
        try:
            if args[1]:
                protocolo_codigo = args[1]
                if protocolo_codigo != -1:
                    movimentacoes = Movimentacao.objects.filter(
                        protocolo__codigo=protocolo_codigo
                    )
                    if "sort" in self.request.POST:
                        if self.request.POST.get("dir") == "ASC":
                            movimentacoes = movimentacoes.order_by(
                                "protocolo__" + self.request.POST.get("sort")
                            )
                        else:
                            movimentacoes = movimentacoes.order_by(
                                "-protocolo__" + self.request.POST.get("sort")
                            )
                    for movs in movimentacoes:
                        valor = {
                            "local": "Não encontrado.",
                            "interessado": "Não encontrado.",
                            "data": "Não encontrado.",
                        }
                        if not movs.lotacao_destino is None:
                            valor["local"] = movs.lotacao_destino.nome
                            valor["interessado"] = self.get_interessado(movs.protocolo)
                            valor["data"] = movs.data_encaminhamento.strftime(
                                "%d/%m/%Y %H:%m"
                            )
                            obj["result"].append(valor)
                else:
                    raise Exception("Não encontrado.")
            else:
                raise Exception("Não encontrado.")
        except Exception as e:
            self.log.exception(e)
            obj["result"].append(
                {"local": str(e), "interessado": str(e), "data": str(e)}
            )
        return obj

    def get_store_tipo_documento(self):
        obj = []
        try:
            if (
                self.get_servidor()
                .work_assignment.filter(lotacao__acesso_protocolo_geral=True)
                .exists()
            ):
                tp_doc = TipoDocumento.objects.all()
            else:
                tp_doc = TipoDocumento.objects.filter(habilita=True).order_by("nome")
            for row in tp_doc:
                obj.append([row.id, str(row)])
        except Exception as e:
            self.log.exception(e)
            obj.append(["", ""])
        return obj

    def get_store_destino(self):
        obj = {"result": []}
        try:
            for lotacao in Lotacao.objects.all():
                obj["result"].append({"id": lotacao.id, "description": str(lotacao)})
        except Exception as e:
            self.log.exception(e)
            obj["result"].append({"id": "", "description": ""})
        return obj

    def get_store_protocolo(self):
        obj = {"result": []}
        try:
            for movimentacao in Movimentacao.objects.filter(
                Q(protocolo__servidor_origem=servidor)
                | Q(lotacao_destino__in=self.get_lotacoes_servidor())
            ):
                if (movimentacao.encaminhado == False) and (
                    movimentacao.protocolo.servidor_origem == servidor
                ):
                    obj["result"].append(
                        {
                            "id": movimentacao.protocolo.id,
                            "description": str(movimentacao.protocolo),
                        }
                    )
                elif not movimentacao.lotacao_destino is None:
                    if movimentacao.lotacao_destino.pk in self.get_lotacoes_servidor():
                        obj["result"].append(
                            {
                                "id": movimentacao.protocolo.pk,
                                "description": str(movimentacao.protocolo),
                            }
                        )
        except Exception as e:
            self.log.exception(e)
            obj["result"].append({"id": "", "description": ""})
        return obj

    def get_store_dados_protocolo(self):
        valor = {
            "id": "",
            "orgao_geral_origem": "",
            "interessado": "",
            "chancela": "",
            "midia": "",
            "tipo_documento": "",
            "numero_externo": "",
            "sigiloso": "",
            "resumo": "",
            "assunto": "",
            "anexos": "",
            "referencias": "",
        }
        try:
            protocolo = Protocolo.objects.get(codigo=self.request.POST.get("codigo"))
            try:
                passo = len(Movimentacao.objects.filter(protocolo=protocolo))
            except:
                passo = 0
            anexos = []
            [
                anexos.append([a.pk, str(a)])
                for a in ProtocoloManager.get_anexos_from_protocolo(protocolo)
            ]
            referencias = []
            [referencias.append([r.pk, str(r)]) for r in protocolo.referencias.all()]
            valor = {
                "id": protocolo.pk,
                "orgao_geral_origem": protocolo.orgao_geral_origem != None
                and [protocolo.orgao_geral_origem.pk, str(protocolo.orgao_geral_origem)]
                or "",
                "interessado": protocolo.interessado != None
                and [protocolo.interessado.pk, str(self.get_interessado(protocolo))]
                or "",
                "chancela": protocolo.chancela != None and protocolo.chancela or "",
                "midia": (
                    [protocolo.midia, EDOCBox.get_midia(protocolo.midia)]
                    if protocolo.midia
                    else [None, "---------"]
                ),
                "tipo_documento": protocolo.tipo_documento != None
                and [protocolo.tipo_documento.pk, str(protocolo.tipo_documento)]
                or "",
                "numero_externo": protocolo.protocolo_externo != None
                and protocolo.protocolo_externo
                or "",
                "sigiloso": protocolo.sigiloso != None and protocolo.sigiloso or "",
                "resumo": protocolo.resumo != None and protocolo.resumo or "",
                "assunto": protocolo.assunto != None and protocolo.assunto or "",
                "anexos": anexos,
                "referencias": referencias,
                "passo": passo,
            }
        except Exception as e:
            self.log.exception(e)
        obj = {"result": [valor]}
        return obj

    def get_store_impressora(self):
        obj = {"result": []}
        try:
            for protocolo in Impressora.objects.all():
                obj["result"].append(
                    {"id": protocolo.pk, "description": str(protocolo)}
                )
        except Exception as e:
            self.log.exception(e)
            obj["result"].append({"id": "", "description": ""})
        return obj

    def get_store_midia_origem(self):
        obj = [["", ""]]
        try:
            for m in MIDIA_ORIGEM:
                obj.append([int(m), str(MIDIA_ORIGEM[m])])
        except Exception as e:
            self.log.exception(e)
            obj.append(["", ""])
        return obj

    def get_store_orgao_geral_origem(self):
        obj = [["", ""]]
        try:
            for protocolo in OrgaoGeral.objects.filter(
                Q(pk__in=self.get_lotacoes_servidor())
            ):
                obj.append([protocolo.pk, str(protocolo)])
        except Exception as e:
            self.log.exception(e)
            obj.append(["", ""])
        return obj

    def get_store_not(self):
        obj = [["", ""]]
        self.log.info("No match any if.")
        obj["result"].append({"id": None, "description": ""})
        return obj

    @classmethod
    def get_midia(cls, key):
        """
        Este método retorna o unicode da mídia a partir da key.
        @param int - key.
        @return str - unicode da mídia, caso não encontre retorna um texto vazio.
        """
        if key:
            try:
                return MIDIA_ORIGEM[key]
            except:
                pass
        return ""

    def get_servidor(self):
        """
        Este método retorna o Servidor que está logado no sistema.
        @return Servidor
        """
        if not self.servidor:
            self.servidor = employee_from_user(self.request.user)
        return self.servidor

    def get_lotacoes_servidor(self):
        """
        Este método retorna a relação dos pks das lotações/designações que o servidor logado possui.
        @return list - lotações/designações, caso não existe retorna [].
        """
        try:
            if not self.lotacoes:
                self.lotacoes = [
                    lotacao.pk for lotacao in self.get_servidor().work_locations
                ]
        except:
            self.lotacoes = []
        return self.lotacoes

    def get_lotacoes_servidor_protocolo_geral(self):
        """
        Este método retorna a relação dos pks das lotações/designações (protocolo_geral) que o servidor logado possui.
        @return list - lotações/designações, caso não existe retorna [].
        """
        try:
            if not self.lotacoes_protocolo_geral:
                self.lotacoes_protocolo_geral = [
                    lotacao.pk if lotacao.acesso_protocolo_geral else None
                    for lotacao in self.get_servidor().work_locations
                ]
        except:
            return []
        return self.lotacoes_protocolo_geral

    def get_lotacao_da_pessoa_from_post(self, pessoa=[]):
        """
        Este método retorna todas Lotacao e todas ServidorLotacao encontradas de acordo com a lista de pk(s) informados.
        Apenas servidores possuem Lotacao. Para os interessados será retornado o Órgão de Origem que foi preenchido
        no momento da criação do Protocolo.
        @param list - Pk(s) de Pessoa.
        @return list de ServidorLotacao, list de Lotacao.
        """
        pessoas_e_lotacoes = []
        lotacoes = []
        pessoas_pk = []
        # ENCONTRA AS LOTAÇÕES DOS SERVIDORES
        for sl in (
            ServidorLotacao.work_assignment_exercise()
            .filter(servidor__pessoa_fisica__pk__in=pessoa)
            .exclude(lotacao=None)
        ):
            pessoas_pk.append(sl.servidor.pessoa_fisica.pk)
            if sl.lotacao is None:
                raise Exception("%s não possui lotação ou designação!" % sl.servidor)
            pessoas_e_lotacoes.append([sl.servidor.pessoa_fisica.pk, sl.lotacao.pk])
            lotacoes.append(sl.lotacao.pk)

        # ENCONTRA OS ÓRGÃOS DE ORIGEM DOS INTERESSADOS(PESSOAS)
        if self.is_concluido_from_post():
            for p in pessoa:
                protocolo = ProtocoloManager.get_protocolo(
                    self.request.POST.get("protocolo", None)
                )
                ProtocoloManager.is_protocolo(protocolo)
                pessoas_e_lotacoes.append([int(p), protocolo.orgao_geral_origem.pk])
                lotacoes.append(protocolo.orgao_geral_origem.pk)
        return pessoas_e_lotacoes, lotacoes

    def get_movimentacao_from_post(self):
        """
        Este método extrai as Movimentacoes do post, verificando se o valor foi informado através de list ou int do POST.
        @param POST - post.
        @return list - Lista de Movimentacao.
        """
        mov = []
        try:
            if "movimentacao" in self.request.POST:
                try:
                    mov = self.request.POST.getlist("movimentacao")
                except:
                    try:
                        mov = (
                            self.request.POST.get("movimentacao")
                            if isinstance(self.request.POST.get("movimentacao"), list)
                            else [self.request.POST.get("movimentacao")]
                        )
                    except:
                        mov = self.request.POST["movimentacao"]
        except Exception as e:
            self.log.exception(e)
        return mov

    @classmethod
    def get_anexos(cls, protocolo, servidor):
        """
        Este método retorna uma lista com todos os anexos de um protocolo.
        Esta lista é utilizada pelo método view.
        @param Protocolo - protocolo.
        @param Servidor - servidor.
        @return list
        """
        anexos = []
        for anexo in ProtocoloManager.get_anexos_from_protocolo(protocolo):
            anexos.append(
                {
                    "nome": anexo.nome,
                    "descricao": anexo.descricao,
                    "link": anexo.arquivo.permalink(),
                    "enviado_por": " %s"
                    % (anexo.arquivo.created.strftime("%d/%m/%Y %H:%M:%S")),
                }
            )
        return anexos


class EDOCImpressora(extjs.ExtCrud):
    class Form(forms.ModelForm):
        lotacao = AutoCompleteField(
            model=Lotacao,
            father="EDOCImpressora",
            controller=RHLotacao,
            label="Lotação",
        )

        class Meta:
            model = Impressora
            exclude = ["created_at", "modified_by", "created_by", "modified_at"]

    titles = {
        "PANEL": "Impressora",
        "LIST": "Gerenciador de Impressora",
        "NEW": "Novo(a) Impressora",
        "EDIT": "Editando um(a) Impressora",
        "DELETE": "Removendo um(a) Impressora",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "nome",
                "key": "nome",
                "width": 240,
            },
            {
                "header": "Lotação",
                "sortable": True,
                "dataIndex": "lotacao",
                "key": "lotacao",
                "width": 240,
            },
            {
                "header": "Host",
                "sortable": True,
                "dataIndex": "host",
                "key": "host",
                "width": 120,
            },
            {
                "header": "Porta",
                "sortable": True,
                "dataIndex": "port",
                "key": "port",
                "width": 120,
            },
        ]
        self.response.write(json.encode(obj))


class EDOCPrintAssEspecial(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/protocolo_oracle_ass_especial/ass_especial"
    filename = "ass_especial.pdf"

    titles = {
        "TITLE": "Protocolo - Assessoria Especial",
        "SUB_TITLE": "Impressão do Relatório Geral - Assessoria Especial",
    }

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/protocolo_oracle_ass_especial/",
        },
    ]

    class Form(forms.Form):
        documento = forms.CharField(label="Documento", max_length=200, required=False)
        assunto = forms.CharField(label="Assunto", max_length=200, required=False)
        remetente = forms.CharField(label="Remetente", max_length=200, required=False)
        origem = forms.CharField(label="Origem", max_length=200, required=False)
        destino = forms.CharField(label="Destino", max_length=200, required=False)
        cidade = forms.CharField(label="Cidade", max_length=200, required=False)
        data_inicio = forms.DateField(label="Data Início", required=False)
        data_final = forms.DateField(label="Data Fim", required=False)


class EDOCPrintGeral(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/protocolo_oracle_geral/geral"
    filename = "protocolo_geral.pdf"

    titles = {
        "TITLE": "Protocolo - Geral",
        "SUB_TITLE": "Impressão do Relatório Geral - Protocolo Geral",
    }

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/protocolo_oracle_geral/",
        },
    ]

    class Form(forms.Form):
        documento = forms.CharField(label="Documento", max_length=200, required=False)
        assunto = forms.CharField(label="Assunto", max_length=200, required=False)
        remetente = forms.CharField(label="Remetente", max_length=200, required=False)
        origem = forms.CharField(label="Origem", max_length=200, required=False)
        destino = forms.CharField(label="Destino", max_length=200, required=False)
        cidade = forms.CharField(label="Cidade", max_length=200, required=False)
        data_inicio = forms.DateField(label="Data Início", required=False)
        data_final = forms.DateField(label="Data Fim", required=False)


class EDOCPrintExpediente(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/protocolo_mysql_expediente/expediente"
    filename = "expediente.pdf"
    datasource = "expediente-mysql"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/protocolo_mysql_expediente/",
        }
    ]

    titles = {
        "TITLE": "Protocolo - Expediente",
        "SUB_TITLE": "Impressão do Relatório Geral - Expediente",
    }

    class Form(forms.Form):
        documento = forms.CharField(label="Documento", max_length=200, required=False)
        assunto = forms.CharField(label="Assunto", max_length=200, required=False)
        remetente = forms.CharField(label="Remetente", max_length=200, required=False)
        origem = forms.CharField(label="Origem", max_length=200, required=False)
        destino = forms.CharField(label="Destino", max_length=200, required=False)
        cidade = forms.CharField(label="Cidade", max_length=200, required=False)
        data_inicio = forms.DateField(label="Data Início", required=False)
        data_final = forms.DateField(label="Data Fim", required=False)


class EDOCPrintAthenas(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/athenas/protocolo"
    filename = "protocolo_athenas.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/athenas/",
        },
    ]

    titles = {
        "TITLE": "Protocolo - Geral",
        "SUB_TITLE": "Impressão do Relatório Geral - Protocolo Geral",
    }

    class Form(forms.Form):
        protocolo = forms.CharField(label="Protocolo", max_length=200, required=False)
        chancela = forms.CharField(label="Chancela", max_length=200, required=False)
        criacao_inicio = forms.DateField(
            label="Data de Criação - Início", required=False
        )
        criacao_final = forms.DateField(label="Data de Criação - Final", required=False)
        interessado = AutoCompleteField(
            model=Pessoa, label="Interessado", controller=RHPessoa, required=False
        )
        assunto = forms.CharField(label="Assunto", max_length=200, required=False)
        resumo = forms.CharField(label="Resumo", max_length=200, required=False)
        remetente = AutoCompleteField(
            model=Pessoa, controller=RHPessoa, label="Remetente", required=False
        )
        envio_inicio = forms.DateField(label="Data de Envio - Início", required=False)
        envio_final = forms.DateField(label="Data de Envio - Final", required=False)
        destinatario = AutoCompleteField(
            model=Pessoa, controller=RHPessoa, label="Destinatário", required=False
        )
        recebimento_inicio = forms.DateField(
            label="Data de Recebimento - Início", required=False
        )
        recebimento_final = forms.DateField(
            label="Data de Recebimento - Final", required=False
        )


class EDOCPrintAthenasRecebimento(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/athenas/recebimento/protocolo"
    filename = "protocolo_athenas.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/athenas/recebimento",
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


class EDOCPrintAthenasProtocolo(extjs.ExtReportBuild):

    report_src = "/to/mpe/protocolo/athenas/documento_movimentacoes"
    filename = "protocolo_athenas.pdf"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/protocolo/athenas/",
        },
    ]

    titles = {
        "TITLE": "Protocolo - Geral",
        "SUB_TITLE": "Impressão do Relatório Geral - Protocolo Geral",
    }

    class Form(forms.Form):
        protocolo = forms.CharField()


class EDOCReportDetail(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.edocs.protocolo.tasks.EdocDetail()")

    def renderer(self, data):
        import json

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    @login_required(type="JSON")
    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            if self.request.POST.get("workplace_origin") or self.request.POST.get(
                "workplace_destination"
            ):
                Task.start(
                    edoc_detail,
                    workplace_origin=self.request.POST.get("workplace_origin"),
                    workplace_destination=self.request.POST.get(
                        "workplace_destination"
                    ),
                    edoc_code=self.request.POST.get("edoc_code"),
                    date_created=self.request.POST.get("date_created"),
                    date_start=self.request.POST.get("date_start"),
                    date_end=self.request.POST.get("date_end"),
                    finalized=self.request.POST.get("finalized"),
                    subject=self.request.POST.get("subject"),
                    user=get_current_user().pk,
                    success="""<p>Arquivo <span style="font-weight:bold">Movimentações a partir de %(mov_message)s</span> foi gerado com sucesso.
                    Para fazer o download clique no <a href="/athenas/EDOCReportDetail/file/?uuid=%(uuid)s">link</a>.
        </p>
        <p>Este arquivo está disponível para download até dia <span style="font-weight:bold">%(deadline)s</span></p>""",
                )
            else:
                raise Exception("Prencha Local de origem ou Local onde esteve.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Movimentações a partir de %s, você será avisado quando o mesmo for concluído."
                % (
                    str(
                        OrgaoGeral.objects.get(
                            pk=(
                                self.request.POST.get("workplace_origin")
                                or self.request.POST.get("workplace_destination")
                            )
                        )
                    )
                ),
            )
        self.renderer(rst)

    def file(self, args=[]):
        import json

        cache_path = settings.CACHE_PATH
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )
            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")
                self.response["Content-Type"] = "application/csv"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )
                with open(os.path.join(cache_path, filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                # task.state = 'downloaded'
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo para o usuário logado.</h1>"
            )
