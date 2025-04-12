# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import Q

from django.core.exceptions import ValidationError
from contrib.nil import nil_pk
from rh.api.employee import departament_verify
from rh.api.movimentacao import RHMovimentacaoPessoalRestful
from contrib.decorator import login_required
from rh.models import (
    Employee,
    MovimentacaoAproveitamento,
    MovimentacaoPosse,
    MovimentacaoPromocao,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoRemocao,
    MovimentacaoRemocaoMembro,
    MovimentacaoReversao,
    MovimentacaoTitularizacao,
    BenefitMovement,
    PossessionResident,
    RequestMove,
    PossessionCollaborator,
    PossessionTrainee,
    ServidorLotacao,
    Workplace,
    MovimentacaoDiligencia,
    MovimentacaoAuxiliarCoordenacao,
)
from contrib.utils import getLogger

log = getLogger(__name__)


class RHPossessionBaseRestful(RHMovimentacaoPessoalRestful):

    _model = MovimentacaoPosse

    exclude_fields = RHMovimentacaoPessoalRestful.exclude_fields + [
        "movimentacaopessoal_ptr",
        "movimentacaoposse_ptr_unicode",
        "movimentacaoposse_ptr",
    ]

    def model_to_dict(self, instance):
        _dict = super(RHPossessionBaseRestful, self).model_to_dict(instance)
        if ServidorLotacao.objects.filter(
            movimentacao_posse=instance, designacao=True, ativo=True
        ).exists():
            workplace = ServidorLotacao.objects.filter(
                movimentacao_posse=instance, designacao=True, ativo=True
            ).last()
            _dict.update({"lotation": f"{workplace.lotacao.pk}"})
            _dict.update({"lotation_unicode": f"{str(workplace.lotacao)}"})

        instance = instance.my_origin
        job_position_law_display = instance.servidor.type_by_possession
        if getattr(instance, "quadro"):
            job_position_law_display = instance.quadro.cargo.tipo_lei_cargo
        elif instance.servidor.is_requested():
            job_position_law_display = "AC"

        _dict.update({"jobposition_law_display": f"{job_position_law_display}"})
        _dict.update({"is_member": f"{instance.servidor.is_member}"})

        fired = None
        fired_type = ""
        if hasattr(instance, "desligamento"):
            fired = instance.desligamento
            fired_type = "FIRED"
            if hasattr(instance.desligamento, "movimentacaoaposentadoria"):
                fired = instance.desligamento.movimentacaoaposentadoria
                fired_type = "RETIREMENT"
        _dict.update(
            {
                "fired_type": fired_type,
            }
        )
        _dict.update(
            {
                "desligamento": nil_pk(fired, ""),
                "desligamento_unicode": str(fired) or "",
                "description_possession": instance.description_possession,
            }
        )

        paridade_salarial = False
        beneficio_integral = False

        if hasattr(instance, "beneficio_integral"):
            paridade_salarial = instance.paridade_salarial
            beneficio_integral = instance.beneficio_integral

        _dict.update(
            {
                "paridade_salarial": paridade_salarial,
                "beneficio_integral": beneficio_integral,
            }
        )

        return _dict

    def create_lotation(self, instance, work, publication, employee, initial_date):
        """
        Função para criação de lotação

        :params: instance: Instância de MovimentacaoPosse
        :params: work: instância da lotação
        :params: publication: publicação da lotação
        :params: employee: Servidor
        :params: initial_date: Data inicial

        :returns: dict
        """
        try:
            sl, create = ServidorLotacao.objects.get_or_create(
                movimentacao_posse=instance,
                servidor=employee,
                lotacao=work,
                designacao=True,
                defaults={
                    "publicacao": publication,
                    "movimentacao_posse": instance,
                    "servidor": employee,
                    "lotacao": work,
                    "data_vigencia_inicio": initial_date,
                    "designacao": False,
                },
            )
            if create:
                sl.create_work_assignment()
            return {
                "success": True,
                "message": "Dados persistido com sucesso.",
            }

        except Exception as e:
            return {"success": False, "message": f"Falha ao criar a Lotação. {e}"}

    def change_lotation(self, instance, work, publication, employee, initial_date):
        """
        Função para criação de lotação

        :params: instance: Instância de MovimentacaoPosse
        :params: work: instância da lotação
        :params: publication: publicação da lotação
        :params: employee: Servidor
        :params: initial_date: Data inicial

        :returns: dict
        """
        try:
            lotacoes = ServidorLotacao.objects.filter(
                movimentacao_posse=instance,
                publicacao=publication,
                servidor=employee,
                data_vigencia_inicio=initial_date,
            )
            if lotacoes.exists():
                lotacoes.update(lotacao=work)
            else:
                return self.create_lotation(
                    instance, work, publication, employee, initial_date
                )

            return {
                "success": True,
                "message": "Dados persistido com sucesso.",
            }

        except Exception as e:
            return {"success": False, "message": f"Falha ao modificar a Lotação. {e}"}

    def get_instance(self, params):
        """
        Função para retornar a instância de um MovimentacaoPosse a partir da data_posse, quadro de publicação
        :returns: (MovimentacaoPosse) Instância de MovimentacaoPosse
        """
        return self._model.objects.get(
            servidor=params.get("servidor"),
            data_posse=params.get("data_posse"),
            quadro=params.get("quadro"),
            publicacao_movimentacao=params.get("publicacao_movimentacao"),
        )

    def generic_do_post(self):
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

                inst.save(
                    {
                        "label_provision": self.Model._meta.object_name,
                        "lotacao": params.get("lotation"),
                    }
                )
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
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

    def do_post(self):
        """
        Sobrescrita do método do_post para inclusão da lotação na criação dos provimentos
        """
        result = {"success": False, "message": "Não foi processado nada ainda!"}

        params = self.get_params()
        result = self.generic_do_post()

        if params.get("lotation") and result.get("success") == True:
            lotation = params.pop("lotation")
            work = Workplace.objects.get(pk=lotation)

            result = self.create_lotation(
                instance=self.get_instance(params=params),
                work=work,
                publication=params.get("publicacao_movimentacao"),
                employee=params.get("servidor"),
                initial_date=params.get("data_posse"),
            )
        return result

    def do_put(self, pk=None):
        """
        Sobrescrita do método do_put para inclusão da lotação na alteração dos provimentos
        """
        params = self.get_params()

        result = {"success": False, "message": "Não foi processado nada ainda!"}

        if params.get("lotation"):
            work = Workplace.objects.get(pk=params.get("lotation"))
            employee_lotations = ServidorLotacao.objects.filter(
                movimentacao_posse__pk=pk,
                servidor=params.get("servidor"),
            )
            if work not in [lotation.lotacao for lotation in employee_lotations]:
                return {
                    "success": False,
                    "message": "A lotação não poderá ser alterada pelo provimento!",
                }
        result = super().do_put(pk=pk)

        return result

    def do_delete_single(self, pk):
        """
        Sobrescrita do método do_delete_single para deleção das lotações vinculadas aos provimentos
        """
        posse = self._model.objects.get(pk=pk)

        try:
            ServidorLotacao.objects.filter(
                movimentacao_posse=posse, designacao=True
            ).delete()
            ServidorLotacao.objects.filter(
                movimentacao_posse=posse, designacao=False
            ).delete()

        except Exception as e:
            return {"success": False, "message": f"Erro ao excluir as lotações. {e}"}

        return super().do_delete_single(pk=pk)


class RHPossessionRestful(RHPossessionBaseRestful):

    _model = MovimentacaoPosse

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.Manage")')

    def get_query(self):
        query = super(RHPossessionRestful, self).get_query()
        return query.exclude(
            ~Q(movimentacaoaproveitamento=None)
            | ~Q(movimentacaopromocao=None)
            | ~Q(movimentacaopromocao__movimentacaotitularizacao=None)
            | ~Q(movimentacaoremocaomembro=None)
            | ~Q(movimentacaoreadaptacao=None)
            | ~Q(movimentacaoreconducao=None)
            | ~Q(movimentacaoreintegracao=None)
            | ~Q(movimentacaoreversao=None)
            | ~Q(requestmove=None)
            | ~Q(possessiontrainee=None)
            | ~Q(possessioncollaborator=None)
            | ~Q(benefitmovement=None)
        )


class RHAllPossessionsRestful(RHPossessionBaseRestful):

    def get_query(self):
        return (
            super(RHAllPossessionsRestful, self).get_query().order_by("-data_exercicio")
        )


class RHProvision(RHAllPossessionsRestful):

    _model = MovimentacaoPosse

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.provision.Manage", {departament: "%s"})'
            % departament_verify()
        )

    # XXX: MPTO faz filtro para remoção dos cargos tipo_lei_cargo 'AC', em MPMT esses cargos são utilizados
    # def get_query(self):
    #     return super(RHProvision, self).get_query().exclude(
    #         my_type='movimentacaoposse',
    #         quadro__cargo__tipo_lei_cargo='AC'
    #     ).order_by('data_exercicio')
    def get_query(self):
        return super(RHProvision, self).get_query().order_by("data_exercicio")


class RHUseMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoAproveitamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.use.Manage" {action_menu: "Aproveitamento"})'
        )


class RHPromotionMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoPromocao

    def get_query(self):
        query = super(RHPromotionMoveRestful, self).get_query()
        if self._model == MovimentacaoPromocao:
            query = query.exclude(~Q(movimentacaotitularizacao=None))
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.promotion.Manage")'
        )


class RHReadaptationMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoReadaptacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.readaptation.Manage")'
        )


class RHReconductionMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoReconducao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.reconduction.Manage")'
        )


class RHReintegrationMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoReintegracao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.reintegration.Manage")'
        )


class RHRemovalMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoRemocao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.removal.Manage")')


class RHDiligenceMoveRestful(RHMovimentacaoPessoalRestful):

    _model = MovimentacaoDiligencia

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.diligence.Manage")')


class RHMovAuxCoordenationRestful(RHMovimentacaoPessoalRestful):

    _model = MovimentacaoAuxiliarCoordenacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.aux_coordenation.Manage")')

    def model_to_dict(self, instance):
        params = super(RHMovAuxCoordenationRestful, self).model_to_dict(instance)

        comarca = ""
        if instance.servidor_designacao and instance.servidor_designacao.lotacao:
            lotacao = Workplace.objects.get(pk=instance.servidor_designacao.lotacao.pk)
            if lotacao.comarca:
                comarca = lotacao.comarca.nome
        params.update(
            {
                "comarca": comarca,
            }
        )
        return params


class RHRemovalMemberMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoRemocaoMembro

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.removalmember.Manage")'
        )


class RHReversalMoveRestful(RHPossessionBaseRestful):

    _model = MovimentacaoReversao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.reversal.Manage")')


class RHSecuritizationMoveRestful(RHPromotionMoveRestful):

    _model = MovimentacaoTitularizacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.promotion.securitization.Manage")'
        )


# class RHBenefitMoveRestful(RHPossessionBaseRestful):

#     _model = BenefitMovement

#     def json(self, args=[]):
#         self.response['content-type'] = 'text/javascript'
#         self.response.write('Ext._create("rh.movimentacao.possession.benefit.Manage")')


class RHRequestMove(RHPossessionBaseRestful):

    _model = RequestMove

    def get_instance(self, params):
        return self._model.objects.get(
            publicacao_movimentacao=params.get("publicacao_movimentacao"),
            possession_origin_date=params.get("possession_origin_date"),
            data_exercicio=params.get("data_exercicio"),
        )

    def do_post(self):
        params = self.get_params()

        if not params.get("data_exercicio"):
            return {"success": False, "message": "Necessária a Data de Exercício"}

        result = super().generic_do_post()

        if params.get("lotation") and result.get("success") == True:
            lotation = params.pop("lotation")
            work = Workplace.objects.get(pk=lotation)

            result = self.create_lotation(
                instance=self.get_instance(params),
                work=work,
                publication=params.get("publicacao_movimentacao"),
                employee=params.get("servidor"),
                initial_date=params.get("data_exercicio"),
            )

        return result

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.request.Manage")')

    def model_to_dict(self, instance):
        _dict = super(RHPossessionBaseRestful, self).model_to_dict(instance)
        if instance.job_position_origin:
            _dict.update({"jobposition_law_display": f"{instance.job_position_origin}"})

        if ServidorLotacao.objects.filter(
            movimentacao_posse=instance, designacao=True
        ).exists():
            workplace = ServidorLotacao.objects.filter(
                movimentacao_posse=instance, designacao=True
            ).last()
            _dict.update({"lotation": f"{workplace.lotacao.pk}"})
            _dict.update({"lotation_unicode": f"{str(workplace.lotacao)}"})

        return _dict


class RHPossessionTrainee(RHPossessionBaseRestful):

    _model = PossessionTrainee

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.trainee.Manage")')


class RHPossessionResident(RHPossessionBaseRestful):

    _model = PossessionResident

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.resident.Manage")')


class RHPossessionCollaborator(RHPossessionBaseRestful):

    _model = PossessionCollaborator

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.collaborator.Manage")'
        )


class RHBenefitMoveRestful(RHPossessionBaseRestful):

    _model = BenefitMovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.movimentacao.possession.benefit.Manage")')

    @login_required("JSON")
    def reactivation(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = self.request.POST
        # TODO: Fazer validação dos parametros obrigatórios
        try:
            benefit = BenefitMovement.objects.get(pk=params.get("reactivated_benefit"))
            benefit.reactivation(params)

            rst.update(
                {
                    "success": True,
                    "message": "Registro Criado com Sucesso",
                }
            )
        except Exception as err:
            rst.update({"message": str(err)})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class RHReactivatedMoveRestful(RHBenefitMoveRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.movimentacao.possession.benefit.reactivated.Manage")'
        )
