# -*- coding: utf-8 -*-
import json

from django.db.models.query_utils import Q
from django.core.exceptions import ValidationError
from django.db import transaction

from contrib.utils import getLogger
from rh.api.movimentacao import RHMovimentacaoPessoalRestful
from rh.models import MovimentacaoSubstituicao
from rh.utils import departure_reason_unicode, situation_unicode

log = getLogger(__name__)


class RHMovimentacaoSubstituicaoRestful(RHMovimentacaoPessoalRestful):

    full_text_index = (
        "servidor_substituido__pessoa_fisica__nome__icontains",
    ) + RHMovimentacaoPessoalRestful.full_text_index

    _model = MovimentacaoSubstituicao

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + [
        "movimentacaopessoal_ptr"
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.substituicao.Manage")')

    def get_query(self):
        query = super(RHMovimentacaoSubstituicaoRestful, self).get_query()
        return query

    def model_to_dict(self, instance):
        params = super(RHMovimentacaoSubstituicaoRestful, self).model_to_dict(instance)
        params.update(
            {
                "posse_cargo_unicode": (
                    ("%s" % instance.posse.quadro) if instance.posse else ""
                ),
                "situation_unicode": situation_unicode(
                    instance.data_inicio, instance.data_fim
                ),
                "departure_reason_unicode": departure_reason_unicode(
                    instance.afastamento
                ),
            }
        )
        params.update({"icons": []})

        icons = []
        if not instance.designation_substituted:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-warn",
                    "title": "Designação de servidor substituído não encontrado %s"
                    % (instance.servidor_substituido),
                }
            )
        if (
            instance.substituicao_finalizada() or instance.is_active()
        ) and not instance.designation_substitute:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-warn",
                    "title": "Designação de servidor substituto não encontrado %s"
                    % (instance.servidor),
                }
            )
        if (
            instance.substituicao_finalizada()
            and instance.designation_substitute
            and not instance.designation_substitute.is_finished()
        ):
            icons.append(
                {
                    "iconCls": "icon-core icon-core-warn",
                    "title": "Designação de servidor substituto não finalizada %s"
                    % (instance.designation_substitute),
                }
            )
        params.update({"icons": icons})

        if instance.servidor_substituido.membro:
            identify = self.substitute_unicode(instance)
            if len(identify):
                params.update(
                    {"servidor__unicode": "%s - %s" % (identify.get("order"), instance)}
                )

        return params

    def substitute_unicode(self, instance):
        employee = instance.servidor
        employee_substituted = instance.servidor_substituido
        identify = {"registry": employee.matricula, "order": 0}
        try:
            for (
                employee_workplace
            ) in employee_substituted.my_replacement_employee_workplace().filter(
                servidor__matricula=employee.matricula
            ):
                rpl = employee_substituted.my_replacement_substitute(
                    workplace=(
                        instance.designation_substituted.lotacao
                        if instance.designation_substituted
                        else None
                    ),
                    employee=employee,
                )
                if rpl.exists():
                    rpl = rpl.earliest("order")
                    identify.update({"order": rpl.order})
        except Exception as err:
            log.exception(err)
        return identify

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
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                pay_year = self.request.POST.get("pay_year")
                payment_installments = self.request.POST.get("payment_installments")

                if pay_year and self.validate_int_field(pay_year) is False:
                    rst.update(
                        message="Valor do campo Ano de Pagamento é inválido. Deve ser apenas números."
                    )
                elif (
                    payment_installments
                    and self.validate_int_field(payment_installments) is False
                ):
                    rst.update(
                        message="Valor do campo Parcelas de Pagamento é inválido. Deve ser apenas números."
                    )
                else:
                    try:
                        errors = [
                            {"field": key, "values": value}
                            for key, value in e.message_dict.items()
                        ]
                        rst.update(message=str(errors[0]["values"][0]))
                    except:
                        rst.update(message=str(e))
                    log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def do_put(self, pk=None):
        """Executa uma requisição PUT.

        :param pk: Chave primária de uma instância. (Opcional)
        :type pk: Integer
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name
            )
        else:
            pay_year = self.request.PUT.get("pay_year")
            payment_installments = self.request.POST.get("payment_installments")

            if pay_year and self.validate_int_field(pay_year) is False:
                rst.update(
                    message="Valor do campo Ano de Pagamento é inválido. Deve ser apenas números."
                )
            elif (
                payment_installments
                and self.validate_int_field(payment_installments) is False
            ):
                rst.update(
                    message="Valor do campo Parcelas de Pagamento é inválido. Deve ser apenas números."
                )
            else:
                rst.update(
                    self.do_put_multi()
                    if "filter" in self.request.PUT
                    else self.do_put_single(pk)
                )

        return rst

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        pay_year = self.request.PUT.get("pay_year")
        payment_installments = self.request.POST.get("payment_installments")

        if pay_year and self.validate_int_field(pay_year) is False:
            rst.update(
                message="Valor do campo Ano de Pagamento é inválido. Deve ser apenas números."
            )
        elif (
            payment_installments
            and self.validate_int_field(payment_installments) is False
        ):
            rst.update(
                message="Valor do campo Parcelas de Pagamento é inválido. Deve ser apenas números."
            )
        else:
            try:
                params = self.get_params(self.request.PUT, check_case=True)
                if params.get("able_to_pay"):
                    params.pop("able_to_pay")
                if params.get("consolidated"):
                    params.pop("consolidated")
                if params.get("paid_out"):
                    params.pop("paid_out")

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
                    log.exception(e)
                    rst.update(
                        errors=[
                            {"field": key, "values": value}
                            for key, value in e.message_dict.items()
                        ],
                        message="Alguns campos não foram preenchidos corretamente.",
                    )
                except Exception as e:
                    rst.update(message=str(e))
                    log.exception(e)
                else:
                    rst.update(
                        {
                            "success": True,
                            "message": "Dados persistido com sucesso.",
                            "instance": self.model_to_dict(inst),
                        }
                    )

        return rst

    def do_put_multi(self):
        """Atualiza múltiplas instâncias."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        pay_year = self.request.PUT.get("pay_year")
        payment_installments = self.request.POST.get("payment_installments")

        if pay_year and self.validate_int_field(pay_year) is False:
            rst.update(
                message="Valor do campo Ano de Pagamento é inválido. Deve ser apenas números."
            )
        elif (
            payment_installments
            and self.validate_int_field(payment_installments) is False
        ):
            rst.update(
                message="Valor do campo Parcelas de Pagamento é inválido. Deve ser apenas números."
            )
        else:
            try:
                query = self.do_filter(self.get_query())
                rst.update(count=query.count())
                params = self.get_params(self.request.PUT, check_case=True)

                if params.get("able_to_pay"):
                    params.pop("able_to_pay")
                if params.get("consolidated"):
                    params.pop("consolidated")
                if params.get("paid_out"):
                    params.pop("paid_out")

                if "filter" in params:
                    del params["filter"]

                if self.can_update_fields_values is not None:
                    params = {
                        k: v
                        for k, v in list(params.items())
                        if k in self.can_update_fields_values
                    }

                if not getattr(self, "force_orm_single", False) and not getattr(
                    self, "force_orm_update_single", False
                ):
                    with transaction.atomic():
                        query.update(**params)
                else:
                    with transaction.atomic():
                        for obj in query:
                            self.fill_instance_values(obj, params)
                            if self.use_full_clean:
                                obj.full_clean()
                            obj.save()
                            self.fill_instance_m2m(obj, params)

            except ValidationError as e:
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {"success": True, "message": "Dados atualizados com sucesso."}
                )

        return rst

    def validate_int_field(self, ano):
        try:
            int(ano)
            return True
        except:
            return False
