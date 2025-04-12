# -*- coding: utf-8 -*-

from django import forms
from django.db.models.query_utils import Q

from auditoria.models import LineLog
from contrib import extjs
from contrib.decorator import is_public, login_required, tab
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, get_json_engine, getLogger
from ged.forms import FileUploadField
from rh import models as rh_models
from rh.afastamento import models as afastamento_models
from rh.api.publicacao import RHPublicacaoRestful
from rh.const import MOTIVO_SUBSTITUICAO, PERIODO_FERIAS_CHOICES
from rh.utils import feature_flag_arquimedes, FeatureFlagDisabledError
from rh.views import (
    RHAnotacaoFolgaAniversario,
    RHAnotacaoFolgaCompensacao,
    RHAnotacaoLicenca,
    RHAnotacaoRecesso,
    RHCargo,
    RHCurso,
    RHLocalidade,
    RHOrgaoGeral,
    RHPessoaFisica,
    RHPessoaFisicaSimplificado,
    RHPessoaFisicaSimplificadoSemDocumento,
    RHPublicacao,
    RHQuadro,
    RHServidor,
    RHUnidadeAdministrativa,
)
from standard.views import AutoCompleteField

json = get_json_engine()

log = getLogger(__name__)


class CustomAutocomplete(extjs.ExtWidget):

    def autocomplete(self, args=[]):

        # TODO: Realizar tarefa relatada no ticket #190

        qs = []
        model = None
        obj = {}

        """"""
        if len(args) > 0:
            if args[0] == "Servidor":
                model = rh_models.Servidor
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(matricula__icontains=self.request.POST.get("query", ""))
                    )
            elif args[0] == "MovimentacaoPosse":
                model = rh_models.MovimentacaoPosse
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            servidor__matricula__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
            elif args[0] == "Lotacao":
                model = rh_models.Lotacao
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(nome__icontains=self.request.POST.get("query", "")))
        """"""

        if model is not None and len(qs) > 0:
            q = None
            for qn in qs:
                q = qn if q is None else Q(q | qn)
            if args[0] == "MovimentacaoPosse" and "pk" not in self.request.POST:
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r}
                        for r in model.objects.filter(q).exclude(ativo=False)
                    ]
                )
            else:
                obj.update(
                    result=[
                        {"pk": r.pk, "description": r} for r in model.objects.filter(q)
                    ]
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class AFABaseLicencaAfastamento(extjs.ExtCrud):
    class Form(forms.ModelForm):
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.BaseLicencaAfastamento
            exclude = [
                "movimentacaopessoal_ptr",
                "baselicencaafastamento_ptr",
                "anotacao_geral",
                "anotacao_geral_nomeacao",
                "anotacao_geral_exercicio",
                "ativo",
                "data_alteracao",
                "motivo",
                "tipo",
                "estado",
                "prorroga_progressao",
                "created_by",
                "modified_by",
                "created_at",
                "modified_at",
                "agendado_arquimedes",
                "situation_unicode",
                "annotation_class",
                "publicacao_alteracao_id",
                "movimentacaopessoal_ptr_id",
                "baselicencasaudejuntamedica_ptr_id",
                "anotacao_geral_id",
                "acompanhado_id",
                "servidor_id",
                "publicacao_movimentacao_id",
                "licencasaude_ptr_id",
                "atestado_medico_id",
                "profissional_saude_id",
                "atestado_junta_medica_id",
                "publicacao_fim_id",
                "licenca_ptr_id",
                "created_by_id",
                "modified_by_id",
                "documento_solicitacao_id",
                "baselicencaafastamento_ptr_id",
            ]

    def __init__(self, request, response, response_format=False):
        super(AFABaseLicencaAfastamento, self).__init__(
            request, response, response_format
        )

        self.titles = {
            "PANEL": "%s" % self.Form.Meta.model._meta.verbose_name,
            "LIST": "Gerenciador de %s" % self.Form.Meta.model._meta.verbose_name,
            "NEW": "Novo(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "EDIT": "Editando um(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "DELETE": "Removendo um(a) %s" % self.Form.Meta.model._meta.verbose_name,
            "FILTER": "NOT_DEFINED_IN_CONTROLLER",
        }

    @login_required(type="JSON")
    def commit(self, args=[]):
        autorization = self.request.user.is_superuser
        model = self.Form.Meta.model

        actions_translate = {"NEW": "add", "EDIT": "change", "DELETE": "delete"}

        action_translate_number = {"NEW": 1, "EDIT": 2, "DELETE": 4}

        if not autorization:
            perm = "{package}.{action}_{model}".format(
                package=model._meta.app_label,
                model=model.__name__.lower(),
                action=actions_translate[args[0]],
            )
            autorization = self.request.user.has_perm(perm)

            self.log.info(
                "%s %s realizar %s"
                % (self.request.user, "pode" if autorization else "não pode", perm)
            )

        # TODO: INCLUIR VIAGEM NOVAMENTE APÓS RODRIGO REALIZAR MANUTENÇÃO EM SOFTWARE DE DIÁRIAS
        if model.__name__ in ("FeriasAfastamento",):  # 'Viagem'):
            obj = {
                "result": False,
                "messageException": "Não é possível Criar/Alterar/Apagar %s através deste Gerenciador."
                % model._meta.verbose_name,
                "validate": True,
                "exception": "toolkit.exception.CrudDelete",
                "html": "",
            }
        elif autorization and self.request.user.is_active:

            linelog = LineLog()
            linelog.user = self.request.user
            linelog.level = action_translate_number[args[0]]
            linelog.read_request(self.request)
            linelog.status = 0

            if len(args) == 3:
                validate = bool(args[2] != 1)
            else:
                validate = True

            try:
                if args[0] == "NEW":
                    frm = self.Form(self.request.POST)
                else:
                    inst = self.Form.Meta.model.objects.get(pk=int(args[1]))
                    frm = self.Form(self.request.POST, instance=inst)

                obj = {
                    "result": False,
                    "html": "",
                    "validate": validate,
                }

                if frm.is_valid() or validate:
                    if args[0] == "NEW":
                        inst = self.Form.Meta.model()
                        frm = self.Form(self.request.POST, instance=inst)

                        try:
                            linelog.status = 1

                            linelog.json_description = {
                                "action": "NEW",
                                "new": {},
                                "post": dict(self.request.POST),
                                "get": dict(self.request.GET),
                            }

                            for field in inst._meta.fields:
                                linelog.json_description["new"][field.name] = (
                                    field.value_from_object(inst)
                                )

                            frm.save()
                            obj["cid"] = inst.pk
                            obj["cvalue"] = inst
                            obj["result"] = True
                        except Exception as exception:
                            self.log.exception(exception)
                            linelog.status = 0
                            linelog.json_description["message"] = exception
                            obj["exception"] = "toolkit.exception.CrudSave"
                            obj["messageException"] = exception
                    elif args[0] == "EDIT":
                        inst = self.Form.Meta.model.objects.get(pk=int(args[1]))

                        old = {}
                        for field in inst._meta.fields:
                            old[field.name] = field.value_from_object(inst)

                        prorrogacao = self.request.POST.getlist("prorrogacao")

                        for pro in inst.prorrogacao.filter().exclude(
                            pk__in=prorrogacao
                        ):
                            inst.prorrogacao.remove(pro)

                        frm = self.Form(self.request.POST, instance=inst)
                        try:
                            new = {}
                            for field in inst._meta.fields:
                                new[field.name] = field.value_from_object(inst)

                            linelog.json_description = {
                                "action": "EDIT",
                                "new": new,
                                "old": old,
                            }

                            frm.save()
                            obj["cid"] = inst.pk
                            obj["cvalue"] = inst
                            linelog.status = 1

                            obj["result"] = True
                        except Exception as exception:
                            self.log.exception(exception)
                            linelog.json_description["error"] = {
                                "type": exception.__class__.__name__,
                                "message": exception,
                            }
                            obj["exception"] = "toolkit.exception.CrudSave"
                            obj["messageException"] = exception
                    elif args[0] == "DELETE":
                        inst = self.Form.Meta.model.objects.get(pk=int(args[1]))

                        old = {}
                        for field in inst._meta.fields:
                            old[field.name] = field.value_from_object(inst)

                        frm = self.Form(self.request.POST, instance=inst)

                        try:
                            linelog.json_description = {"action": "DELETE", "old": old}

                            inst.delete()
                            linelog.status = 1

                            obj["result"] = True
                        except Exception as exception:
                            linelog.json_description["error"] = {
                                "type": exception.__class__.__name__,
                                "message": exception,
                            }
                            obj["exception"] = "toolkit.exception.CrudDelete"
                            obj["messageException"] = exception
            except Exception as err:
                self.log.exception(err)
                obj = {
                    "result": False,
                    "exception": "toolkit.exception.Bug",
                    "messageException": "Ocorreu um erro processando a operação. Contacte a equipe de desenvolvimento para reportar o erro.",
                }

            try:
                linelog.save()
            except Exception as err:
                self.log.exception(err)
        else:
            obj = {"result": False, "exception": "toolkit.exception.Permission"}

            linelog = LineLog()
            linelog.user = self.request.user
            linelog.level = 0
            linelog.status = 0
            linelog.read_request(self.request)

            try:
                linelog.save()
            except Exception as err:
                self.log.exception(err)

            if not self.request.user.is_active:
                obj["messageException"] = (
                    "O usuário não está ativo, devido a isto não é possível alterar dados."
                )
            else:
                obj["messageException"] = "Você não tem permissão para esta ação."

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))


class AFAAfastamento(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Início",
            required=False,
        )
        publicacao_fim = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Fim",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Afastamento
            exclude = [
                "afastamento_ptr",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class AFALicenca(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Licenca
            exclude = [
                "licenca_ptr",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class AFAAusencia(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Concessão",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Ausencia
            exclude = [
                "ausencia_ptr",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "publicacao_fim",
                "prorrogacao",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "data_inicio", "data_prevista"]},
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAViagem(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Viagem
            exclude = [
                "viagem_ptr",
                "publicacao_movimentacao",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "data_inicio", "data_prevista"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAFeriasAfastamento(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.FeriasAfastamento
            exclude = [
                "feriasafastamento_ptr",
                "publicacao_movimentacao",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "anotacao_aquisicao",
                "publicacao_movimentacao",
                "ano",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFARecesso(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        anotacao_aquisicao = AutoCompleteField(
            model=rh_models.AnotacaoRecesso,
            controller=RHAnotacaoRecesso,
            label="Anotação de Aquisição",
            required=False,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Recesso
            exclude = [
                "recesso_ptr",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "anotacao_aquisicao",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAFolgaCompensacao(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        anotacao_aquisicao = AutoCompleteField(
            model=rh_models.AnotacaoFolgaCompensacao,
            controller=RHAnotacaoFolgaCompensacao,
            label="Anotação de Aquisição",
            required=False,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.FolgaCompensacao
            exclude = [
                "folgacompensacao_ptr",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "anotacao_aquisicao",
                "publicacao_movimentacao",
                "turno",
                "ano",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAFolgaEleitoral(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        anotacao_aquisicao = AutoCompleteField(
            model=rh_models.AnotacaoLicenca,
            controller=RHAnotacaoLicenca,
            label="Anotação de Aquisição",
            required=False,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.FolgaEleitoral
            exclude = [
                "folgaeleitoral_ptr",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "ano", "data_inicio"]},
        {"title": "Alterações", "field": ["alteracao", "publicacao_alteracao"]},
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAFolgaAniversario(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        data_inicio = forms.DateField(label="Usufruto")
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        anotacao_aquisicao = AutoCompleteField(
            model=afastamento_models.FolgaAniversario.anotacao_classe,
            controller=RHAnotacaoFolgaAniversario,
            label="Anotação de Aquisição",
            required=False,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.FolgaAniversario
            exclude = [
                "folgaaniversario_ptr",
                "remunerado",
                "concessao_durante_estagio_prob",
                "data_referencia",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
                "data_prevista",
                "data_fim",
                "anotacao_aquisicao",
                "publicacao_movimentacao",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": ["servidor", "ano", "turno", "data_inicio", "data_prevista"],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAtuacaoGrupoTrabalho(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.AtuacaoGrupoTrabalho
            exclude = [
                "atuacaogrupotrabalho_ptr",
                "publicacao_movimentacao",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {"title": "Dados", "field": ["servidor", "data_inicio", "data_prevista"]},
        {"title": "Designações", "field": ["designation_exercise"]},
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFADesempenhoFuncao(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            # controller=RHPublicacaoRestful,
            controller=RHPublicacaoRestful,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.DesempenhoFuncao
            exclude = [
                "desempenhofuncao_ptr",
                "publicacao_movimentacao",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "anotacao_aquisicao",
                "ano",
                "turno",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAPlantao(AFABaseLicencaAfastamento):
    class Form(AFABaseLicencaAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        anotacao_aquisicao = AutoCompleteField(
            model=rh_models.AnotacaoLicenca,
            controller=RHAnotacaoLicenca,
            label="Anotação de Aquisição",
            required=False,
        )
        publicacao_alteracao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Revogação/Alteração",
            required=False,
        )

        class Meta:
            model = afastamento_models.Plantao
            exclude = [
                "plantao_ptr",
                "publicacao_movimentacao",
                "remunerado",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "prorrogacao",
                "suspensao_contagem_ferias",
                "publicacao_fim",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 400,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class AFAProfissionalSaude(extjs.ExtCrud):
    class Form(forms.ModelForm):
        pessoa_fisica = AutoCompleteField(
            label="Profissional Saúde",
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificado,
            required=False,
        )

        class Meta:
            exclude = []
            model = afastamento_models.ProfissionalSaude


class AFALicencaSaude(AFALicenca):
    class Form(AFALicenca.Form):
        atestado_medico = FileUploadField(label="Atestado Médico", required=False)
        profissional_saude = AutoCompleteField(
            label="Profissional Saúde",
            model=afastamento_models.ProfissionalSaude,
            controller=AFAProfissionalSaude,
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaSaude
            exclude = AFALicenca.Form.Meta.exclude + ["licencasaude_ptr", "remunerado"]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Prazo Solicitado",
                "sortable": True,
                "dataIndex": "prazo_solicitado",
                "key": "prazo_solicitado",
                "width": 100,
            },
            {
                "header": "Prazo Concedido",
                "sortable": True,
                "dataIndex": "prazo_concedido",
                "key": "prazo_solicitado",
                "width": 100,
            },
            {
                "header": "Aprovação",
                "sortable": True,
                "dataIndex": "aprovacao",
                "key": "aprovacao",
                "width": 60,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "codigo_internacional_doenca",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaSaude3Dias(AFALicencaSaude):
    class Form(AFALicencaSaude.Form):
        class Meta:
            model = afastamento_models.LicencaSaude3Dias
            exclude = AFALicencaSaude.Form.Meta.exclude + [
                "prazo_concedido",
                "prorrogacao",
                "publicacao_movimentacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "codigo_internacional_doenca",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaSaude30Dias(AFALicencaSaude):
    class Form(AFALicencaSaude.Form):
        class Meta:
            model = afastamento_models.LicencaSaude30Dias
            exclude = AFALicencaSaude.Form.Meta.exclude + [
                "prazo_concedido",
                "prorrogacao",
                "publicacao_movimentacao",
            ]


class AFABaseLicencaSaudeJuntaMedica(AFALicencaSaude):
    class Form(AFALicencaSaude.Form):
        documento_solicitacao = FileUploadField(
            label="Documento Solicitação", required=False
        )
        atestado_junta_medica = FileUploadField(
            label="Atestado Junta Médica", required=False
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.BaseLicencaSaudeJuntaMedica
            exclude = AFALicencaSaude.Form.Meta.exclude + [
                "baselicencasaudejuntamedica_ptr"
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "data_envio",
                "data_retorno",
                "prazo_concedido",
                "codigo_internacional_doenca",
            ],
        },
        {
            "title": "Informações",
            "field": [
                "documento_solicitacao",
                "atestado_junta_medica",
                "documento",
                "parecer",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaSaudeJuntaMedica(AFABaseLicencaSaudeJuntaMedica):
    class Form(AFABaseLicencaSaudeJuntaMedica.Form):
        prazo_solicitado = forms.IntegerField(label="Prazo Solicitado", required=True)
        documento_solicitacao = FileUploadField(
            label="Documento Solicitação", required=False
        )
        atestado_junta_medica = FileUploadField(
            label="Atestado Junta Médica", required=False
        )

        class Meta:
            model = afastamento_models.LicencaSaudeJuntaMedica
            exclude = AFABaseLicencaSaudeJuntaMedica.Form.Meta.exclude + [
                "licencasaudejuntamedica_ptr"
            ]

    def get_query(self):
        return afastamento_models.LicencaSaudeJuntaMedica.objects.filter()

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Prazo Solicitado",
                "sortable": True,
                "dataIndex": "prazo_solicitado",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Prazo Concedido",
                "sortable": True,
                "dataIndex": "prazo_concedido",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Aprovação",
                "sortable": True,
                "dataIndex": "aprovacao",
                "key": "aprovacao",
                "width": 60,
            },
            {
                "header": "Data Envio",
                "sortable": True,
                "dataIndex": "data_envio",
                "key": "data_envio",
                "width": 80,
            },
            {
                "header": "Data Retorno Junta",
                "sortable": True,
                "dataIndex": "data_retorno",
                "key": "data_retorno",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "acompanhado",
                "grau_parentesco",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "data_envio",
                "data_retorno",
                "prazo_concedido",
                "codigo_internacional_doenca",
            ],
        },
        {
            "title": "Informações",
            "field": [
                "documento_solicitacao",
                "atestado_junta_medica",
                "documento",
                "parecer",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaDoencaPessoaFamilia(AFABaseLicencaSaudeJuntaMedica):
    class Form(AFABaseLicencaSaudeJuntaMedica.Form):
        prazo_solicitado = forms.IntegerField(label="Prazo Solicitado", required=True)
        acompanhado = AutoCompleteField(
            label="Acompanhado",
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificadoSemDocumento,
        )

        class Meta:
            model = afastamento_models.LicencaDoencaPessoaFamilia
            exclude = AFABaseLicencaSaudeJuntaMedica.Form.Meta.exclude

    def get_query(self):
        return afastamento_models.LicencaDoencaPessoaFamilia.objects.filter()

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 220,
            },
            {
                "header": "Acompanhado",
                "sortable": True,
                "dataIndex": "acompanhado",
                "key": "acompanhado",
                "width": 120,
            },
            {
                "header": "Parentesco",
                "sortable": True,
                "dataIndex": "grau_parentesco",
                "key": "grau_parentesco",
                "width": 80,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Prazo Solicitado",
                "sortable": True,
                "dataIndex": "prazo_solicitado",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Prazo Concedido",
                "sortable": True,
                "dataIndex": "prazo_concedido",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Aprovação",
                "sortable": True,
                "dataIndex": "aprovacao",
                "key": "aprovacao",
                "width": 60,
            },
            {
                "header": "Data Envio",
                "sortable": True,
                "dataIndex": "data_envio",
                "key": "data_envio",
                "width": 80,
            },
            {
                "header": "Data Retorno Junta",
                "sortable": True,
                "dataIndex": "data_retorno",
                "key": "data_retorno",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "crianca",
                "data_parto",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "data_envio",
                "data_retorno",
                "prazo_concedido",
                "codigo_internacional_doenca",
                "natimorto",
            ],
        },
        {
            "title": "Informações",
            "field": [
                "documento_solicitacao",
                "atestado_junta_medica",
                "documento",
                "parecer",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaMaternidade(AFABaseLicencaSaudeJuntaMedica):
    class Form(AFABaseLicencaSaudeJuntaMedica.Form):
        crianca = AutoCompleteField(
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificado,
            label="Criança",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaMaternidade
            exclude = AFABaseLicencaSaudeJuntaMedica.Form.Meta.exclude

    def get_query(self):
        return afastamento_models.LicencaMaternidade.objects.filter()

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 220,
            },
            {
                "header": "Filho(a)",
                "sortable": True,
                "dataIndex": "crianca",
                "key": "crianca",
                "width": 120,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Prazo Solicitado",
                "sortable": True,
                "dataIndex": "prazo_solicitado",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Prazo Concedido",
                "sortable": True,
                "dataIndex": "prazo_concedido",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Aprovação",
                "sortable": True,
                "dataIndex": "aprovacao",
                "key": "aprovacao",
                "width": 60,
            },
            {
                "header": "Data Envio",
                "sortable": True,
                "dataIndex": "data_envio",
                "key": "data_envio",
                "width": 80,
            },
            {
                "header": "Data Retorno Junta",
                "sortable": True,
                "dataIndex": "data_retorno",
                "key": "data_retorno",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "crianca",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "profissional_saude",
                "atestado_medico",
                "prazo_solicitado",
                "aprovacao",
                "data_envio",
                "data_retorno",
                "prazo_concedido",
                "codigo_internacional_doenca",
            ],
        },
        {
            "title": "Informações",
            "field": [
                "documento_solicitacao",
                "atestado_junta_medica",
                "documento",
                "parecer",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaAdocao(AFABaseLicencaSaudeJuntaMedica):
    class Form(AFABaseLicencaSaudeJuntaMedica.Form):
        crianca = AutoCompleteField(
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificadoSemDocumento,
            label="Filho(a)",
            required=False,
        )
        profissional_saude = AutoCompleteField(
            label="Profissional Saúde",
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificado,
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaAdocao
            exclude = AFABaseLicencaSaudeJuntaMedica.Form.Meta.exclude

    def get_query(self):
        return afastamento_models.LicencaAdocao.objects.filter()

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 220,
            },
            {
                "header": "Filho(a)",
                "sortable": True,
                "dataIndex": "crianca",
                "key": "crianca",
                "width": 120,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Prevista Fim",
                "sortable": True,
                "dataIndex": "data_prevista",
                "key": "data_prevista",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
            {
                "header": "Prazo Solicitado",
                "sortable": True,
                "dataIndex": "prazo_solicitado",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Prazo Concedido",
                "sortable": True,
                "dataIndex": "prazo_concedido",
                "key": "prazo_solicitado",
                "width": 90,
            },
            {
                "header": "Aprovação",
                "sortable": True,
                "dataIndex": "aprovacao",
                "key": "aprovacao",
                "width": 60,
            },
            {
                "header": "Data Envio",
                "sortable": True,
                "dataIndex": "data_envio",
                "key": "data_envio",
                "width": 80,
            },
            {
                "header": "Data Retorno Junta",
                "sortable": True,
                "dataIndex": "data_retorno",
                "key": "data_retorno",
                "width": 100,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "conjuge",
                "orgao",
                "orgao_destino",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaAfastamentoConjuge(AFALicenca):
    class Form(AFALicenca.Form):
        conjuge = AutoCompleteField(
            model=rh_models.PessoaFisica, controller=RHPessoaFisica, label="Cônjuge"
        )
        orgao = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Orgão/Entidade do Cônjuge",
        )
        orgao_destino = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Destino da Transferência",
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaAfastamentoConjuge
            exclude = AFALicenca.Form.Meta.exclude + [
                "licencaafastamentoconjuge_ptr",
                "remunerado",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "data_inicio_servico",
                "data_fim_servico",
                "publicacao_movimentacao",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaServicoMilitar(AFALicenca):
    class Form(AFALicenca.Form):
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaServicoMilitar
            exclude = AFALicenca.Form.Meta.exclude + [
                "licencaservicomilitar_ptr",
                "remunerado",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "cargo_eletivo",
                "partido",
                "localidade",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaAtividadePolitica(AFALicenca):
    class Form(AFALicenca.Form):
        localidade = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Localidade"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaAtividadePolitica
            exclude = [
                "licencaatividadepolitica_ptr",
                "prorrogacao",
            ] + AFALicenca.Form.Meta.exclude


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "curso",
                "instituicao",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaCapacitacao(AFALicenca):
    class Form(AFALicenca.Form):
        curso = AutoCompleteField(
            model=rh_models.Curso, controller=RHCurso, label="Curso"
        )
        instituicao = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Instituição",
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaCapacitacao
            exclude = AFALicenca.Form.Meta.exclude + [
                "licencacapacitacao_ptr",
                "remunerado",
            ]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 220,
            },
            {
                "header": "Curso",
                "sortable": True,
                "dataIndex": "curso",
                "key": "curso",
                "width": 120,
            },
            {
                "header": "Instituição",
                "sortable": True,
                "dataIndex": "instituicao",
                "key": "instituicao",
                "width": 220,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaInteresseParticular(AFALicenca):
    class Form(AFALicenca.Form):
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = afastamento_models.LicencaInteresseParticular
            exclude = AFALicenca.Form.Meta.exclude + [
                "licencainteresseparticular_ptr",
                "remunerado",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "data_inicio",
                "data_prevista",
                "publicacao_movimentacao",
                "entidade",
                "tipo_entidade",
                "cargo",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFALicencaMandatoClassista(AFALicenca):
    class Form(AFALicenca.Form):
        entidade = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Entidade",
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=True,
        )

        class Meta:
            model = afastamento_models.LicencaMandatoClassista
            exclude = [
                "licencamandatoclassista_ptr",
                "prorrogacao",
                "remunerado",
            ] + AFALicenca.Form.Meta.exclude


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "posse",
                "publicacao_movimentacao",
                "publicacao_fim",
                "quadro_destino",
                "orgao",
                "data_inicio",
                "data_prevista",
                "onus",
                "contribuicao",
                "transito_pela_folha",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoOutroOrgao(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        posse = AutoCompleteField(
            model=rh_models.MovimentacaoPosse,
            controller="RHMovimentacaoPosse",
            label="Servidor",
        )
        quadro_destino = AutoCompleteField(
            model=rh_models.Quadro,
            controller=RHQuadro,
            label="Cargo Destino",
            required=False,
        )
        orgao = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Órgão Destino",
        )

        class Meta:
            model = afastamento_models.AfastamentoOutroOrgao
            exclude = AFAAfastamento.Form.Meta.exclude + [
                "servidor",
                "remunerado",
            ]

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
                "header": "Posse",
                "sortable": True,
                "dataIndex": "posse",
                "key": "movimentacao_posse",
                "width": 320,
            },
            {
                "header": "Quadro destino",
                "sortable": True,
                "dataIndex": "quadro_destino",
                "key": "quadro_destino",
                "width": 320,
            },
            {
                "header": "Ônus",
                "sortable": True,
                "dataIndex": "onus",
                "key": "onus",
                "width": 80,
            },
            {
                "header": "Contribuição",
                "sortable": True,
                "dataIndex": "contribuicao",
                "key": "contribuicao",
                "width": 80,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "cargo_eletivo",
                "partido",
                "localidade",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoMandatoEletivo(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        localidade = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Localidade"
        )

        class Meta:
            model = afastamento_models.AfastamentoMandatoEletivo
            exclude = AFAAfastamento.Form.Meta.exclude + ["prorrogacao", "remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "instituicao",
                "curso",
                "localidade",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoEstudar(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        instituicao = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Instituição",
        )
        curso = AutoCompleteField(
            model=rh_models.Curso, controller=RHCurso, label="Curso"
        )
        localidade = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Localidade"
        )

        class Meta:
            model = afastamento_models.AfastamentoEstudar
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Curso",
                "sortable": True,
                "dataIndex": "curso",
                "key": "curso",
                "width": 120,
            },
            {
                "header": "Instituição",
                "sortable": True,
                "dataIndex": "instituicao",
                "key": "instituicao",
                "width": 120,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "orgao",
            ],
        },
        {"title": "Objetivo", "field": ["objetivo"]},
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoMissao(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        orgao = AutoCompleteField(
            model=rh_models.UnidadeAdministrativa,
            controller=RHUnidadeAdministrativa,
            label="Órgão",
        )

        class Meta:
            model = afastamento_models.AfastamentoMissao
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoEleitoral(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )

        class Meta:
            model = afastamento_models.AfastamentoEleitoral
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "localidade",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoServirJuri(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        localidade = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Localidade"
        )

        class Meta:
            model = afastamento_models.AfastamentoServirJuri
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "publicacao_fim",
                "data_prevista",
                "curso",
                "carga_horaria",
            ],
        },
        {"title": "Instituição", "field": ["instituicao"]},
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoTreinamento(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        curso = AutoCompleteField(
            model=rh_models.Curso, controller=RHCurso, label="Curso", required=True
        )

        class Meta:
            model = afastamento_models.AfastamentoTreinamento
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "localidade_origem",
                "localidade_destino",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoDeslocamento(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        localidade_origem = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Origem"
        )
        localidade_destino = AutoCompleteField(
            model=rh_models.Localidade, controller=RHLocalidade, label="Destino"
        )

        class Meta:
            model = afastamento_models.AfastamentoDeslocamento
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoCompeticao(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Início",
        )

        class Meta:
            model = afastamento_models.AfastamentoCompeticao
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "orgao",
                "cargo",
                "remunerado",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoCursoConcurso(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )
        orgao = AutoCompleteField(
            model=rh_models.OrgaoGeral, controller=RHOrgaoGeral, label="Órgão"
        )
        cargo = AutoCompleteField(
            model=rh_models.Cargo, controller=RHCargo, label="Cargo", required=False
        )

        class Meta:
            model = afastamento_models.AfastamentoCursoConcurso
            exclude = [
                "afastamento_ptr",
                "concessao_durante_estagio_prob",
                "suspensao_estagio_prob",
                "efetivo_exercicio",
                "suspensao_contagem_ferias",
                "remunerado",
            ] + AFABaseLicencaAfastamento.Form.Meta.exclude

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
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "key": "servidor",
                "width": 320,
            },
            {
                "header": "Órgão",
                "sortable": True,
                "dataIndex": "orgao",
                "key": "orgao",
                "width": 220,
            },
            {
                "header": "Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 80,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "publicacao_fim",
                "data_inicio",
                "data_prevista",
                "prazo_anos",
                "prazo_meses",
                "prazo_dias",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoPrisao(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )

        class Meta:
            model = afastamento_models.AfastamentoPrisao
            exclude = AFAAfastamento.Form.Meta.exclude + ["remunerado"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
                "prazo_dias",
                "remunerado",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoSuspensao(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor, controller=RHServidor, label="Servidor"
        )

        class Meta:
            model = afastamento_models.AfastamentoSuspensao
            exclude = AFAAfastamento.Form.Meta.exclude + ["publicacao_fim"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoComparecimentoJuizo(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor,
            controller=RHServidor,
            label="Servidor",
            required=True,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Início",
            required=False,
        )

        class Meta:
            model = afastamento_models.AfastamentoComparecimentoJuizo
            exclude = AFAAfastamento.Form.Meta.exclude + ["publicacao_fim"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
            ],
        },
        {"title": "Prorrogações", "field": ["prorrogacao"]},
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAfastamentoCandidatura(AFAAfastamento):
    class Form(AFAAfastamento.Form):
        servidor = AutoCompleteField(
            model=rh_models.Servidor,
            controller=RHServidor,
            label="Servidor",
            required=True,
        )
        publicacao_movimentacao = AutoCompleteField(
            model=rh_models.Publicacao,
            controller=RHPublicacao,
            label="Documento Início",
            required=False,
        )

        class Meta:
            model = afastamento_models.AfastamentoCandidatura
            exclude = AFAAfastamento.Form.Meta.exclude + ["publicacao_fim"]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
                "data_fim",
                "motivo_prisao",
            ],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaDoacaoSangue(AFAAusencia):
    class Form(AFAAusencia.Form):
        class Meta:
            model = afastamento_models.AusenciaDoacaoSangue
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausenciadoacaosangue_ptr",
                "alteracao",
                "publicacao_alteracao",
                "prorrogacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaEleitor(AFAAusencia):
    class Form(AFAAusencia.Form):
        class Meta:
            model = afastamento_models.AusenciaEleitor
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausenciaeleitor_ptr",
                "prorrogacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "data_casamento",
                "conjuge",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaCasamento(AFAAusencia):
    class Form(AFAAusencia.Form):
        conjuge = AutoCompleteField(
            model=rh_models.PessoaFisica, controller=RHPessoaFisica, label="Cônjuge"
        )

        class Meta:
            model = afastamento_models.AusenciaCasamento
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausenciacasamento_ptr",
                "prorrogacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "crianca",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaNascimento(AFAAusencia):
    class Form(AFAAusencia.Form):
        crianca = AutoCompleteField(
            model=rh_models.PessoaFisica,
            controller=RHPessoaFisicaSimplificadoSemDocumento,
            label="Criança",
            required=False,
        )

        class Meta:
            model = afastamento_models.AusenciaNascimento
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausencianascimento_ptr",
                "prorrogacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "pessoa",
                "vinculo",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaFalecimento(AFAAusencia):
    class Form(AFAAusencia.Form):
        pessoa = AutoCompleteField(
            model=rh_models.PessoaFisica, controller=RHPessoaFisica, label="Pessoa"
        )

        class Meta:
            model = afastamento_models.AusenciaFalecimento
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausenciafalecimento_ptr",
                "prorrogacao",
            ]


@tab(
    [
        {
            "title": "Dados",
            "field": [
                "servidor",
                "publicacao_movimentacao",
                "curso",
                "data_inicio",
                "data_prevista",
            ],
        },
        {
            "title": "Alterações",
            "field": ["alteracao", "publicacao_alteracao", "data_fim"],
        },
        {"title": "Texto", "field": ["anota", "texto"]},
    ]
)
class AFAAusenciaConclusao(AFAAusencia):
    class Form(AFAAusencia.Form):
        curso = AutoCompleteField(
            model=rh_models.Curso, controller=RHCurso, label="Curso"
        )

        class Meta:
            model = afastamento_models.AusenciaConclusao
            exclude = AFAAusencia.Form.Meta.exclude + [
                "ausenciaconclusao_ptr",
                "prorrogacao",
            ]


class AFAGestorAfastamento(extjs.ExtWidget):

    @login_required("JSON")
    def json(self, args=[]):
        departamento = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            departamento = "expediente"
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            "new toolkit.rh.gestorafastamento.GestorAfastamento({departamento: '%s'})"
            % departamento
        )

    @is_public()
    def constants(self, args=[]):
        if hasattr(AFAGestorAfastamento, "__cache_constants") is False:
            obj = {
                "PERIODO": PERIODO_FERIAS_CHOICES,
                "MOTIVO": MOTIVO_SUBSTITUICAO,
            }

            AFAGestorAfastamento.__cache_constants = obj
        else:
            obj = AFAGestorAfastamento.__cache_constants

        self.response["content-type"] = "text/javascript"
        self.response.write(
            "toolkit.rh.gestorafastamento.utils.CHOICES = %s" % json.encode(obj)
        )

    def apply_base_exclude(self):
        try:
            qsExclude = []

            if not self.request.POST.get("onlyComparecimentoJuizo", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentocomparecimentojuizo=None))
            if not self.request.POST.get("onlyCandidatura", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentocandidatura=None))
            if not self.request.POST.get("onlyCompeticao", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentocompeticao=None))
            if not self.request.POST.get("onlyCursoFormacaoConcurso", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentocursoconcurso=None))
            if not self.request.POST.get("onlyDeslocamento", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentodeslocamento=None))
            if not self.request.POST.get("onlyJusticaEleitoral", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentoeleitoral=None))
            if not self.request.POST.get("onlyEstudar", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentoestudar=None))
            if not self.request.POST.get("onlyExercicioMandato", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentomandatoeletivo=None))
            if not self.request.POST.get("onlyMissao", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentomissao=None))
            if not self.request.POST.get("onlyPrisao", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentoprisao=None))
            if not self.request.POST.get("onlyServirOutroOrgao", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentooutroorgao=None))
            if not self.request.POST.get("onlyServirJuri", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentoservirjuri=None))
            if not self.request.POST.get("onlySuspensao", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentosuspensao=None))
            if not self.request.POST.get("onlySindicanciaAdm", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentosindicanciaadm=None))
            if not self.request.POST.get("onlyTreinamento", None) == "true":
                qsExclude.append(~Q(afastamento__afastamentotreinamento=None))

            if not self.request.POST.get("onlyAfastamentoConjuge", None) == "true":
                qsExclude.append(~Q(licenca__licencaafastamentoconjuge=None))
            if not self.request.POST.get("onlyAtividadePolitica", None) == "true":
                qsExclude.append(~Q(licenca__licencaatividadepolitica=None))
            if not self.request.POST.get("onlyCapacitacao", None) == "true":
                qsExclude.append(~Q(licenca__licencacapacitacao=None))
            if not self.request.POST.get("onlyMandatoClassista", None) == "true":
                qsExclude.append(~Q(licenca__licencamandatoclassista=None))
            if not self.request.POST.get("onlyDoencaFamilia", None) == "true":
                qsExclude.append(
                    ~Q(
                        licenca__licencasaude__baselicencasaudejuntamedica__licencadoencapessoafamilia=None
                    )
                )
            if not self.request.POST.get("onlyMaternidade", None) == "true":
                qsExclude.append(
                    ~Q(
                        licenca__licencasaude__baselicencasaudejuntamedica__licencamaternidade=None
                    )
                )
            if not self.request.POST.get("onlyServicoMilitar", None) == "true":
                qsExclude.append(~Q(licenca__licencaservicomilitar=None))
            if not self.request.POST.get("onlyTratamento3dias", None) == "true":
                qsExclude.append(~Q(licenca__licencasaude__licencasaude3dias=None))
            if not self.request.POST.get("onlyTratamento30dias", None) == "true":
                qsExclude.append(~Q(licenca__licencasaude__licencasaude30dias=None))
            if not self.request.POST.get("onlyTratamentoJuntaMedica", None) == "true":
                qsExclude.append(
                    ~Q(
                        licenca__licencasaude__baselicencasaudejuntamedica__licencasaudejuntamedica=None
                    )
                )
            if not self.request.POST.get("onlyInteresseParticular", None) == "true":
                qsExclude.append(~Q(licenca__licencainteresseparticular=None))
            if not self.request.POST.get("onlyTutoria", None) == "true":
                qsExclude.append(
                    ~Q(
                        licenca__licencasaude__baselicencasaudejuntamedica__licencaadocao=None
                    )
                )

            if not self.request.POST.get("onlyAlistamentoEleitor", None) == "true":
                qsExclude.append(~Q(ausencia__ausenciaeleitor=None))
            if not self.request.POST.get("onlyCasamento", None) == "true":
                qsExclude.append(~Q(ausencia__ausenciacasamento=None))
            if not self.request.POST.get("onlyDoacaoSangue", None) == "true":
                qsExclude.append(~Q(ausencia__ausenciadoacaosangue=None))
            if not self.request.POST.get("onlyFalecimento", None) == "true":
                qsExclude.append(~Q(ausencia__ausenciafalecimento=None))
            if not self.request.POST.get("onlyConclusaoTcc", None) == "true":
                qsExclude.append(~Q(ausencia__ausenciaconclusao=None))
            if not self.request.POST.get("onlyNascimento", None) == "true":
                qsExclude.append(~Q(ausencia__ausencianascimento=None))

            if not self.request.POST.get("onlyRecessoForense", None) == "true":
                qsExclude.append(
                    ~Q(afastamento__situation_unicode="Recesso Forense - Membros")
                )
        except Exception as err:
            log.exception(err)
        return qsExclude

    def exclude_departure(self):
        qsExclude = self.apply_base_exclude()

        if not self.request.POST.get("onlyFerias", None) == "true":
            qsExclude.append(~Q(feriasafastamento=None))

        if not self.request.POST.get("onlyViagem", None) == "true":
            qsExclude.append(~Q(viagem=None))

        if not self.request.POST.get("onlyFolgaCompensacao", None) == "true":
            qsExclude.append(~Q(folgacompensacao=None))

        if not self.request.POST.get("onlyFolgaEleitoral", None) == "true":
            qsExclude.append(~Q(folgaeleitoral=None))

        if not self.request.POST.get("onlyFolgaAniversario", None) == "true":
            qsExclude.append(~Q(folgaaniversario=None))

        if not self.request.POST.get("onlyAtuacaoGrupoTrabalho", None) == "true":
            qsExclude.append(~Q(atuacaogrupotrabalho=None))

        if not self.request.POST.get("onlyDesempenhoFuncao", None) == "true":
            qsExclude.append(~Q(desempenhofuncao=None))

        if not self.request.POST.get("onlyPlantao", None) == "true":
            qsExclude.append(~Q(plantao=None))

        if not self.request.POST.get("onlyRecesso", None) == "true":
            qsExclude.append(~Q(recesso=None))

        qexclude = None
        for qN in qsExclude:
            qexclude = qN if qexclude is None else Q(qexclude | qN)

        return qexclude

    def exclude_situation(self):
        qsExclude = []
        if not self.request.POST.get("onlyAtivo", None) == "true":
            qsExclude.append(Q(estado=rh_models.ATIVO))
        if not self.request.POST.get("onlyAgendado", None) == "true":
            qsExclude.append(Q(estado=rh_models.AGENDADO))
        if not self.request.POST.get("onlyCancelado", None) == "true":
            qsExclude.append(Q(estado=rh_models.CANCELADO))
        if not self.request.POST.get("onlyEncerrado", None) == "true":
            qsExclude.append(Q(estado=rh_models.ENCERRADO))

        qexclude = None
        for qN in qsExclude:
            qexclude = qN if qexclude is None else Q(qexclude | qN)

        return qexclude

    def exclude_alteration(self):
        qsExclude = []
        # if not self.request.POST.get('onlyCancellation', None) == 'true':
        #     qs.append(Q(alteracao=rh_models.CANCELADO))
        # else:
        #     qsExclude.append(Q(alteracao=rh_models.CANCELADO))
        if not self.request.POST.get("onlyInterruption", None) == "true":
            qsExclude.append(Q(alteracao=rh_models.INTERRUPCAO))
        if not self.request.POST.get("onlyRequest", None) == "true":
            qsExclude.append(Q(alteracao=rh_models.ALTERACAO))
        if not self.request.POST.get("onlyRevocation", None) == "true":
            qsExclude.append(Q(alteracao=rh_models.REVOGACAO))
        if not self.request.POST.get("onlySuspension", None) == "true":
            qsExclude.append(Q(alteracao=rh_models.SUSPENSAO))

        qexclude = None
        for qN in qsExclude:
            qexclude = qN if qexclude is None else Q(qexclude | qN)

        return qexclude

    def filter_type_employee(self):
        tipo_servidor = []
        if self.request.POST.get("tipoServidor", False):
            tipo_servidor.append(self.request.POST.get("tipoServidor"))
        else:
            tipo_servidor = ["M", "S"]

        if (
            get_current_user().has_perm("afastamento.ver_membros") is False
            and "M" in tipo_servidor
        ):
            tipo_servidor.remove("M")
        if (
            get_current_user().has_perm("afastamento.ver_servidores") is False
            and "S" in tipo_servidor
        ):
            tipo_servidor.remove("S")

        return Q(servidor__tipo__in=tipo_servidor)

    def apply_filter(self, query):
        try:
            # qs = []
            qToSearch = None
            if self.request.POST.get("keyword", False):
                keyword = self.request.POST.get("keyword", "")
                qkeyword = Q(servidor__pessoa_fisica__nome__icontains=keyword) | Q(
                    servidor__matricula__icontains=keyword
                )
                pk = None
                try:
                    pk = int(keyword)
                except Exception:
                    pass
                # TODO: MUDAR!!!
                if pk:
                    qkeyword = qkeyword | Q(pk=keyword)

                qToSearch = qkeyword

            qdata = None
            if (
                self.request.POST.get("dataInicio", "") != ""
                and self.request.POST.get("dataFim", "") == ""
            ):
                if self.request.POST.get("checkAlteracao", False) == "true":
                    qdata = Q(
                        modified_at__gte=DateUtils.str_to_date(
                            self.request.POST.get("dataInicio")
                        )
                    )
                else:
                    qdata = Q(
                        data_inicio__gte=DateUtils.str_to_date(
                            self.request.POST.get("dataInicio")
                        )
                    )
            elif (
                self.request.POST.get("dataFim", "") != ""
                and self.request.POST.get("dataInicio", "") == ""
            ):
                if self.request.POST.get("checkAlteracao", False) == "true":
                    qdata = Q(
                        modified_at__lte=DateUtils.str_to_date(
                            self.request.POST.get("dataFim")
                        )
                    )
                else:
                    qdata = Q(
                        data_fim__lte=DateUtils.str_to_date(
                            self.request.POST.get("dataFim")
                        )
                    )
            elif (
                self.request.POST.get("dataInicio", "") != ""
                and self.request.POST.get("dataFim", "") != ""
            ):
                if self.request.POST.get("checkAlteracao", False) == "true":
                    qdata = Q(
                        modified_at__gte=DateUtils.str_to_date(
                            self.request.POST.get("dataInicio")
                        )
                    ) & Q(
                        modified_at__lte=DateUtils.str_to_date(
                            self.request.POST.get("dataFim")
                        )
                    )
                else:
                    qdata = Q(
                        data_inicio__gte=DateUtils.str_to_date(
                            self.request.POST.get("dataInicio")
                        )
                    ) & Q(
                        data_fim__lte=DateUtils.str_to_date(
                            self.request.POST.get("dataFim")
                        )
                    )

            if qdata:
                qToSearch = qToSearch & qdata if qToSearch else qdata
            return query.filter(qToSearch) if qToSearch else query

        except Exception as err:
            self.log.exception(err)

    @login_required(type="JSON")
    def list(self, args=[]):
        obj = {"result": [], "totalRows": 0}
        sort = self.request.POST.get("sort", "data_inicio")
        sort_estado = self.request.POST.get("sort", "estado")
        direction = self.request.POST.get("dir", "ASC")

        start = int(self.request.POST.get("start", 0))
        limit = int(self.request.POST.get("limit", 0))
        end = start + limit

        qs_exclude_situation = self.exclude_situation()
        qs_exclude_alteration = self.exclude_alteration()
        qs_exclude_departure = self.exclude_departure()

        query = afastamento_models.BaseLicencaAfastamento.objects.filter(
            self.filter_type_employee()
        )

        if qs_exclude_situation:
            query = query.exclude(qs_exclude_situation)

        if qs_exclude_alteration:
            query = query.exclude(qs_exclude_alteration)

        if qs_exclude_departure:
            query = query.exclude(qs_exclude_departure)

        query = query.order_by(
            "%s%s" % ("-" if direction == "DESC" else "", sort), "%s" % sort_estado
        )

        query = self.apply_filter(query)

        obj.update(totalRows=query.count())

        query = query[start:end]

        result = []

        for afastamento in query:
            try:
                scheduled = afastamento.pending_period
                days = afastamento.pending_period_days
                if not scheduled and days == float("-inf"):
                    days = "Período com data fim não definida."
                item = {
                    "pk": afastamento.pk,
                    "data_inicio": (
                        DateUtils.date_to_str(afastamento.data_inicio)
                        if afastamento.data_inicio
                        else ""
                    ),
                    "data_fim": (
                        DateUtils.date_to_str(afastamento.data_fim)
                        if afastamento.data_fim
                        else ""
                    ),
                    "data_prevista": (
                        DateUtils.date_to_str(afastamento.data_prevista)
                        if afastamento.data_prevista
                        else ""
                    ),
                    "servidor": afastamento.servidor,
                    "servidor_matricula": afastamento.servidor.matricula,
                    "servidor_pk": afastamento.servidor.pk,
                    "servidor_tipo": (
                        "membro" if afastamento.servidor.membro else "servidor"
                    ),
                    "motivo": afastamento.situation_unicode,
                    "status": afastamento.get_estado_display(),
                    "alteracao": afastamento.get_alteracao_display(),
                    "controller": afastamento.controller,
                    "anotacao": (
                        afastamento.anotacao_geral.pk
                        if afastamento.anotacao_geral
                        else None
                    ),
                    "anotacao_class": afastamento.annotation_class,
                    "agendamento": {
                        "existe_agendamento": scheduled,
                        "title": (
                            "Possui Substituição/Inativação"
                            if scheduled
                            else ("Substituição/Inativação período pendente: %s" % days)
                        ),
                    },
                    "created_at": (
                        DateUtils.datetime_to_str(afastamento.created_at)
                        if afastamento.created_at
                        else "----"
                    ),
                    "created_by": (
                        afastamento.created_by if afastamento.created_by else "----"
                    ),
                    "modified_at": (
                        DateUtils.datetime_to_str(afastamento.modified_at)
                        if afastamento.modified_at
                        else "----"
                    ),
                    "modified_by": (
                        afastamento.modified_by if afastamento.modified_by else "----"
                    ),
                }
            except Exception as err:
                self.log.exception(err)
            else:
                result.append(item)

        obj.update(**{"result": result})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
