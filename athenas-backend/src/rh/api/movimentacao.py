# -*- coding: utf-8 -*-

from django.db.models import Q

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.models import MovimentacaoEnquadramento, MovimentacaoProgressao
from rh.models import (
    HistoricoMovTeletrabalho,
    MovimentacaoAposentadoria,
    MovimentacaoConcessao,
    MovimentacaoDesligamento,
    MovimentacaoPessoal,
    MovimentacaoRedistribuicao,
    MovimentacaoEstabilizacao,
    TerminationBenefitMovement,
    MovimentacaoTeletrabalho,
    MetaTeletrabalho,
)

log = getLogger(__name__)


class RHMovimentacaoPessoalRestful(RestfulDRY):

    force_upper = False

    _model = MovimentacaoPessoal

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    exclude_fields = [
        "rhobject_ptr",
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
        "movimentacaopessoal_ptr",
    ]

    force_persist_boolean_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.pessoal.Manage")')


class RHFiredMoveAllRestful(RHMovimentacaoPessoalRestful):

    full_text_index = (
        # 'servidor_substituido__pessoa_fisica__nome__icontains',
    ) + RHMovimentacaoPessoalRestful.full_text_index

    _model = MovimentacaoDesligamento

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + []


class RHFiredMoveRestful(RHFiredMoveAllRestful):

    full_text_index = (
        # 'servidor_substituido__pessoa_fisica__nome__icontains',
    ) + RHFiredMoveAllRestful.full_text_index

    _model = MovimentacaoDesligamento

    exclude_fields = RHFiredMoveAllRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.fired.Manage")')

    def get_query(self):
        query = super(RHFiredMoveRestful, self).get_query()
        return query.exclude(~Q(movimentacaoaposentadoria=None))


class RHRetirementMoveRestful(RHFiredMoveAllRestful):

    full_text_index = () + RHFiredMoveAllRestful.full_text_index

    _model = MovimentacaoAposentadoria

    exclude_fields = RHFiredMoveAllRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.fired.retirement.Manage")')


class RHTerminationBenefitMoveRestful(RHFiredMoveAllRestful):

    full_text_index = () + RHFiredMoveAllRestful.full_text_index

    _model = TerminationBenefitMovement

    exclude_fields = RHFiredMoveAllRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.fired.terminationbenefit.Manage")'
        )

    def factoryModel(self, *args, **kargs):
        after_organ = kargs.get("after_organ")
        termination_reason = kargs.get("termination_reason")

        if "after_organ" in kargs:
            kargs.pop("after_organ")
        if "termination_reason" in kargs:
            kargs.pop("termination_reason")

        inst = super().factoryModel(*args, **kargs)
        inst._after_organ = after_organ
        inst._termination_reason = termination_reason

        return inst


class RHConcessionMoveRestful(RHMovimentacaoPessoalRestful):

    full_text_index = (
        # 'servidor_substituido__pessoa_fisica__nome__icontains',
    ) + RHMovimentacaoPessoalRestful.full_text_index

    _model = MovimentacaoConcessao

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.concession.Manage")')


class RHRedistributionMoveRestful(RHMovimentacaoPessoalRestful):

    full_text_index = (
        # 'servidor_substituido__pessoa_fisica__nome__icontains',
    ) + RHMovimentacaoPessoalRestful.full_text_index

    _model = MovimentacaoRedistribuicao

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.redistribution.Manage")')


class RHStabilization(RHMovimentacaoPessoalRestful):

    full_text_index = (
        # 'servidor_substituido__pessoa_fisica__nome__icontains',
    ) + RHMovimentacaoPessoalRestful.full_text_index

    _model = MovimentacaoEstabilizacao

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.stabilization.Manage")')


class GFPProgressionAllRestful(RHMovimentacaoPessoalRestful):

    _model = MovimentacaoProgressao

    full_text_index = () + RHMovimentacaoPessoalRestful.full_text_index

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + []


class GFPProgression(GFPProgressionAllRestful):

    _model = MovimentacaoProgressao

    full_text_index = () + GFPProgressionAllRestful.full_text_index

    exclude_fields = GFPProgressionAllRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.progression.Manage")')

    def get_query(self):
        return (
            super(GFPProgression, self)
            .get_query()
            .exclude(~Q(movimentacaoenquadramento=None))
            .order_by("-data_inicio_vigencia", "-data_referencia", "-expected_date")
        )

    def model_to_dict(self, instance):
        _dict = super().model_to_dict(instance)
        _dict.update(
            {
                "type_progression": (
                    "Horizontal"
                    if instance.type_progression == "H"
                    else "Vertical" if instance.type_progression == "V" else "Inicial"
                ),
            }
        )
        return _dict


class GFPLegalFraming(GFPProgressionAllRestful):

    _model = MovimentacaoEnquadramento

    full_text_index = () + GFPProgressionAllRestful.full_text_index

    exclude_fields = GFPProgressionAllRestful.exclude_fields + []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.progression.legalframing.Manage")'
        )


class RHMovimentacaoTeletrabalho(RHMovimentacaoPessoalRestful):

    _model = MovimentacaoTeletrabalho

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.teletrabalho.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(RHMovimentacaoTeletrabalho, self).model_to_dict(instance)
        _dict_.update(
            {
                "qtd_bloqueios": (
                    instance.qtd_bloqueios if instance.qtd_bloqueios else 0
                ),
                "qtd_dias_bloqueados": instance.qtd_dias_bloqueados,
                "icons": instance.icons,
            }
        )
        return _dict_

    def do_post(self):
        if self.validate_aprovador():
            return self.validate_aprovador()
        return super().do_post()

    def do_put(self, pk=None):
        if self.validate_aprovador():
            return self.validate_aprovador()
        return super().do_put(pk)

    def validate_aprovador(self):
        try:
            if self.request.POST:
                aprovador = self.request.POST.get("aprovador", None)
            elif self.request.PUT:
                aprovador = self.request.PUT.get("aprovador", None)
            if not aprovador:
                value = {
                    "success": False,
                    "message": "O campo Aprovador deve ser preenchido",
                }
                return value
        except Exception as error:
            log.error(error)


class RHMetaTeletrabalho(RestfulDRY):

    _model = MetaTeletrabalho

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.teletrabalho.meta.Manage")')

    def get_query(self):
        return self._model.manager.filter()

    def do_delete(self, pk=None):
        """
        Executa uma requisição DELETE.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "delete",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para inativar %s."
                % self.Model._meta.object_name
            )
        else:
            rst.update(self.do_delete_single(pk))

        return rst

    def do_delete_single(self, pk):
        """Inativa uma instância.

        :param pk: Chave primária de uma instância.
        :type pk: Integer
        """
        rst = {
            "success": False,
            "message": "Não foi possível inativar o item selecionado",
        }

        try:
            inst = self.Model.manager.get(pk=pk)
        except self.Model.DoesNotExist:
            rst.update(message="Não foi encontrado o item selecionado.")
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            try:
                if inst.active is True:
                    inst.inactivate()
                    rst.update({"message": "Inativado com sucesso!", "success": True})
                else:
                    rst.update(
                        {"message": "O item já está inativado!", "success": True}
                    )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)

        return rst


class RHHistoricoMovTeletrabalho(RestfulDRY):

    _model = HistoricoMovTeletrabalho

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.teletrabalho.historico.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(RHHistoricoMovTeletrabalho, self).model_to_dict(instance)
        _dict_.update(
            {"anexo_id": instance.get_anexo_id, "anexo_nome": instance.get_anexo_nome}
        )
        return _dict_
