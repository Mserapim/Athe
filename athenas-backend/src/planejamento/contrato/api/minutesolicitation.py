# -*- coding: utf-8 -*-
import json
import locale
import types
from datetime import date

from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.template import loader
from num2words import num2words

from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, getLogger
from edocs.protocolo.models import Movimentacao
from planejamento.contrato.models import (
    MinuteSolicitation,
    MinuteSolicitationAction,
    MinuteSolicitationCommitmentNote,
    MinuteSolicitationItem,
    MinuteSolicitationItemDescription,
    MinuteSolicitationPayment,
    MinuteSolicitationRequisition,
    MinuteSupervisor,
    BalancedSolicitationItem,
)
from rh.models import Cargo, MovimentacaoPosse, Servidor
from standard.models import Configuration

log = getLogger(__name__)


class PHMMinuteSolicitation(RestfulDRY):

    _model = MinuteSolicitation

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()
    full_text_index = (
        "number__icontains",
        "minute__number__icontains",
        "edoc__codigo__icontains",
    )
    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    def get_content_edoc(self, *args):
        obj = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            solicitation = self._model.objects.get(pk=self.request.POST.get("pk"))
            if solicitation.check_minute_out_of_validity:
                obj.update(
                    message="Não é possivel gerar o EDOC para um pedido com ata vencida."
                )
            else:
                obj.update(
                    success=True,
                    document={"content": solicitation.content_edoc, "appends": []},
                )
        except self.Model.DoesNotExist:
            obj.update(message="Não consegui encontrar o pedido desejado.")
        except Exception as e:
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def generate_solicitation_edoc(self, *args):
        movimentation_id = int(self.request.POST.get("movimentationId"))
        solicitation_id = int(self.request.POST.get("solicitationId"))

        try:
            movimentation = Movimentacao.objects.get(id=movimentation_id)
            solicitation = self._model.objects.get(pk=solicitation_id)
            solicitation.edoc = movimentation.protocolo
            solicitation.save()

        except Movimentacao.DoesNotExist:
            raise Exception("Não foi possível encontrar o EDOC")

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteSolicitation, self).model_to_dict(instance)

        _dict_.update({"edoc_display": instance.edoc_display})

        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutesolicitation.MinuteSolicitationManage")'
        )


class PHMMinuteSolicitationAction(RestfulDRY):

    _model = MinuteSolicitationAction

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    def minute_within_validity(self, *args):
        obj = {"success": False, "display_info": False, "message": ""}
        action = self.request.POST.get("action")
        solicitation = self.request.POST.get("solicitation")

        try:
            solicitation = MinuteSolicitation.objects.get(id=solicitation)

            if solicitation.check_minute_out_of_validity and action in ["3", "7"]:
                obj.update(
                    display_info=True,
                    message="A Ata está fora do período de vigência. Gostaria de continuar?",
                )
            obj.update(success=True)

        except MinuteSolicitation.DoesNotExist:
            obj.update(message="Não foi possível encontrar o pedido.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteSolicitationAction, self).model_to_dict(instance)

        _dict_.update({"actions_list": instance.actions_list()})

        return _dict_

    def get_actions_list(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            obj.update(actions_list=MinuteSolicitationAction.actions_list())
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def verify_generate_agreement(self, *args):
        obj = {"success": False, "message": ""}

        try:

            s = MinuteSolicitation.objects.get(
                pk=int(self.request.POST.get("solicitation"))
            )

            generate_agreement = False

            for i in s.minute.minuteitems.all():
                if i.generate_agreement:
                    generate_agreement = True

            if generate_agreement:
                obj.update(
                    before_generate_agreement=True,
                    message="Para esse pedido é necessário a elaboração de um contrato. Deseja continuar?",
                )

            obj.update(success=True)

        except MinuteSolicitation.DoesNotExist:
            obj.update(message="Não foi possível encontrar a solicitação.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def do_post(self, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "responseText": "Teste teste teste",
        }

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
            raise Exception(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            params = self.get_params(self.request.POST, check_case=True)

            try:
                MinuteSolicitationAction.objects.create(
                    solicitation=params["solicitation"],
                    observation=params["observation"],
                    action=params["action"],
                    user=params["user"],
                )
            except Exception as e:
                rst.update(message=f"Erro ao tentar salvar a ação. {e}.")
            else:
                generate_agreement = False
                s = MinuteSolicitation.objects.get(pk=params["solicitation"].pk)

                for i in s.minute.minuteitems.all():
                    if i.generate_agreement:
                        generate_agreement = True

                if generate_agreement and params["action"] == 3:
                    rst.update(
                        success=True,
                        message="Para esse pedido é necessário a elaboração de um contrato.",
                    )
                    raise Exception(
                        "Para esse pedido é necessário a elaboração de um contrato."
                    )
                else:
                    rst.update(success=True, message="Ação registrada com sucesso.")
                    raise Exception("Ação registrada com sucesso.")

        return rst

    def update_status_minute_solicitation(self, *args):
        """Metódo para alterar status do pedido"""

        obj = {"success": False, "message": ""}

        solicitation = self.request.POST.get("solicitation")
        action = self.request.POST.get("action")

        try:
            minute_solicitation = MinuteSolicitation.objects.get(id=int(solicitation))
            minute_solicitation.update_status_minute_solicitation(action)
        except MinuteSolicitation.DoesNotExist:
            obj.update(message="Não foi possível encontrar o pedido.")
        except Exception as e:
            log.exception(e)
            raise Exception(e)
        else:
            obj.update(success=True, message="Ação registrada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))


class PHMMinuteSolicitationItem(RestfulDRY):

    _model = MinuteSolicitationItem

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            balanced_oid=instance.balanced_oid,
            is_rebalanced=instance.is_rebalanced,
            description=instance.item.description,
            brand=instance.item.brand,
            unit_value=float(instance.item.unitary_value),
        )

        return rst

    def get_query(self):
        query = super(PHMMinuteSolicitationItem, self).get_query()
        query = query.order_by("item__group", "item__line", "item")

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutesolicitation.MinuteSolicitationItemManage")'
        )


class PHMRebalancedSolicitationItem(RestfulDRY):

    _model = BalancedSolicitationItem

    def do_post(self, *args, **kwargs):
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
        }

        params = self.get_params(self.request.POST, check_case=False)

        try:
            obj, created = BalancedSolicitationItem.objects.get_or_create(
                solicitation_item=params["solicitation_item"]
            )

            obj.description = params["description"]
            obj.brand = params["brand"]
            obj.unit_value = params["unit_value"]

            obj.save()

            rst.update(success=True, message="Rebalanceamento registrado com sucesso.")
        except Exception as e:
            raise Exception(e)


class PHMMinuteSolicitationItemDescription(RestfulDRY):

    _model = MinuteSolicitationItemDescription


class PHMMinuteSolicitationCommitmentNote(RestfulDRY):

    _model = MinuteSolicitationCommitmentNote

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "number__icontains",
        "parent__number__icontains",
    )

    def get_query(self):
        query = super(PHMMinuteSolicitationCommitmentNote, self).get_query()
        query = query.order_by("parent", "id")

        return query

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)

                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                exception_message = ""
                for key, values in e.message_dict.items():
                    for value in values:
                        if key == "__all__":
                            exception_message += " {}".format(value)
                        else:
                            exception_message += " {}: {}".format(
                                self._model._meta.get_field_by_name(key)[
                                    0
                                ].verbose_name,
                                value,
                            )
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message=exception_message,
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistidos com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            log.debug(
                "COUNT UPDATE FOR %s [%s,]: %s"
                % (self.Model.__name__, pk, self.Model.objects.filter(pk=pk).count())
            )
            params = self.get_params(self.request.PUT, check_case=True)
            log.debug("POST GETPARAMS....")
            inst = self.Model.objects.get(pk=pk)
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que deseja atualizar. pk: %s model: %s ctr: %s"
                % (pk, self.Model.__name__, self.__class__.__name__)
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            if self.can_update_fields_values is not None:
                params = {
                    k: v
                    for k, v in list(params.items())
                    if k in self.can_update_fields_values
                }

            self.fill_instance_values(inst, params)
            try:
                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                exception_message = ""
                for key, values in e.message_dict.items():
                    for value in values:
                        if key == "__all__":
                            exception_message += " {}".format(value)
                        else:
                            exception_message += " {}: {}".format(
                                self._model._meta.get_field_by_name(key)[
                                    0
                                ].verbose_name,
                                value,
                            )
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message=exception_message,
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistidos com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteSolicitationCommitmentNote, self).model_to_dict(
            instance
        )

        _dict_.update(
            {
                "provider_display": instance.get_provider,
                "balance": instance.get_balance(),
            }
        )

        return _dict_


class PHMMinuteSolicitationPayment(RestfulDRY):

    _model = MinuteSolicitationPayment

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "bank_order__icontains",
        "commitmentnote__number__icontains",
    )

    def payment_solicitation(self, *args):
        obj = {"success": True, "message": "Nada feito ainda."}

        orders = self._model.objects.filter(
            pk__in=self.request.POST.get("solicitations").split(",")
        )

        total = self._model.objects.filter(
            pk__in=self.request.POST.get("solicitations").split(",")
        ).aggregate(Sum("value"))

        tpl = loader.get_template("solicitation/solicitation_report.html")

        minute = orders.last().commitmentnote.solicitation.minute

        obj.update(
            message=tpl.render(
                {
                    "instance": {
                        "numero_ata": minute.number,
                        "processo": minute.process_number,
                        "processo_mae": minute.parent_process,
                        "nome_fornecedor": minute.provider,
                        "cnpj_fornecedor": minute.provider.pessoajuridica.cnpj,
                        "fiscais": orders.last().commitmentnote.solicitation.minute.get_active_supervisor,
                        "pedidos": orders.all(),
                        "total": total["value__sum"],
                    }
                }
            )
        )

        self.renderer(obj)

    def pay(self, *args):
        """Registra a ordem bancária de uma solicitação de pagamento."""
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            m = self._model.objects.get(pk=self.request.POST.get("pk"))
            if m.bank_order:
                obj.update(
                    message="Já existe uma ordem bancária cadastrada. Para alterar, reverta o pagamento."
                )
            else:
                m.bank_order = self.request.POST.get("bank_order")
                m.payment_date = DateUtils.str_to_date(
                    self.request.POST.get("payment_date")
                )
                m._action = "pay"
                m.save()
                obj.update(success=True, message="Pagamento realizado com sucesso.")
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def unpay(self, *args):
        """Apaga a ordem bancária de uma solicitação de pagamento."""

        obj = {"success": False, "message": "Nada foi feito ainda."}
        try:
            m = self._model.objects.get(pk=self.request.POST.get("pk"))
            m._action = "unpay"
            if not m.bank_order:
                obj.update(
                    message="Não existe uma ordem bancária cadastrada. Para alterar, reverta o pagamento."
                )
            else:
                m.save()
                obj.update(success=True, message="Pagamento desfeito com sucesso.")
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_query(self):
        query = super(PHMMinuteSolicitationPayment, self).get_query()
        query = query.order_by("bank_order", "commitmentnote__number")

        return query

    def get_logged_employee_id(self, *args):
        obj = {}
        minute = self.request.POST.get("minute")
        user = get_current_user()
        try:
            supervisor = MinuteSupervisor.objects.get(
                Q(minute=minute) & Q(employee__user=user) & Q(end=None)
            )
            if supervisor:
                obj["logged_employee_id"] = supervisor.employee.id
            else:
                obj["logged_employee_id"] = 0
        except MinuteSupervisor.DoesNotExist:
            obj["logged_employee_id"] = 0

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteSolicitationPayment, self).model_to_dict(instance)

        if instance.modified_by:
            self.responsible = instance.modified_by
        else:
            self.responsible = instance.created_by

        employee = Servidor.objects.get(user=self.responsible)

        if instance.start_reference_period and instance.end_reference_period:
            period = (
                instance.start_reference_period.strftime("%d/%m/%Y")
                + " até "
                + instance.end_reference_period.strftime("%d/%m/%Y")
            )
        else:
            period = ""

        _dict_.update(
            {
                "user_display": employee.pessoa_fisica.nome,
                "period_display": period,
            }
        )

        return _dict_


class PHMMinuteSolicitationManager(RestfulDRY):

    _model = MinuteSolicitation

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "minute__number__icontains",
        "minute__process_number__icontains",
        "number__icontains",
        "edoc__codigo__icontains",
    )

    def get_query(self):
        query = super(PHMMinuteSolicitationManager, self).get_query().distinct()
        query = query.order_by("situation", "-number")

        user = get_current_user()

        group_views = {
            1: "hiring-minute-financial",
            2: "hiring-minute-manager",
            3: "hiring-minute-supervisor",
            4: "hiring-minute-view-all",
        }

        # Se for gestor geral ou financeiro, visualiza todos
        if user.groups.filter(
            Q(name=group_views.get(2)) | Q(name=group_views.get(4))
        ).exists():
            query = query.all()

        # Se for fiscal, visualiza os que ele é gestor ou responsável
        elif user.groups.filter(name=group_views.get(3)).exists():
            subordinates = user.servidor.subordinados.all()
            query = query.filter(
                Q(minute__minutesupervisors__employee__user=user)
                | Q(minute__minutesupervisors__employee__in=subordinates),
                Q(minute__minutesupervisors__end=None),
            )

        else:
            query = query.none()

        return query

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteSolicitationManager, self).model_to_dict(instance)

        _dict_.update(
            {
                "minute_process_number_display": instance.minute_process_number_display,
                "main_supervisors_display": instance.main_supervisors_display(),
                "edoc_display": instance.edoc_display,
            }
        )

        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerManage")'
        )

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            solicitation = self.get_query().get(pk=args[0])

            rst.update(
                success=True, document={"content": solicitation.rendered, "appends": []}
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)


class PHMMinuteSolicitationManagerAdmin(PHMMinuteSolicitationManager):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerManageAdmin")'
        )


class PHMMinuteSolicitationRequisition(RestfulDRY):

    _model = MinuteSolicitationRequisition
    _MinuteSolicitation = MinuteSolicitation

    force_upper = False

    def to_requisit(self, *args):
        rst = {
            "success": True,
            "message": "Nada foi feito ainda.",
            "document": "Sem informações",
        }

        pk = self.request.POST.get("pk")

        try:
            solicitation = self._MinuteSolicitation.objects.get(pk=pk)

            # Antes de mudar o status, temos que verificar se há algum item no pedido
            # Solicitação formalizada por meio do echamado T-035209
            qtd_items = MinuteSolicitationItem.objects.filter(
                solicitation__id=pk
            ).count()

            if solicitation.situation is solicitation.EDITING and qtd_items > 0:
                solicitation.situation = solicitation.SOLICITED
                solicitation.save()
            elif qtd_items == 0:
                raise Exception("O pedido precisa de pelo menos um item cadastrado.")
            else:
                raise Exception('O pedido precisar estar "Em Edição".')
        except Exception as e:
            rst.update(success=False, message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))

    def renderer_edoc(self, *args):
        rst = {
            "success": True,
            "message": "Nada foi feito ainda.",
            "document": "Sem informações",
        }

        pk = self.request.POST.get("pk")

        try:
            solicitation = self._MinuteSolicitation.objects.get(pk=pk)
            edoc_content = solicitation.content_edoc
            rst.update(document=edoc_content)
        except Exception as e:
            rst.update(success=False, message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(rst))
