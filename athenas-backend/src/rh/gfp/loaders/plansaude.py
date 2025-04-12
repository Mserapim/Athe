# -*- coding: utf-8 -*-

from rh.gfp.loaders import gfp_loader
from contrib.utils import getLogger
from standard.models import RunCodeManager

log = getLogger("rh.gfp.loaders.plansaude")


class PlanSaudeLoader(gfp_loader.GFPLoader):

    CODE_TYPE = "latin-1"
    TRUNK_CR_NL = True
    HEADER_LINES = 1
    EVENTO_NUMERO = ""
    RETURN_ONLY_ERRORS = True

    def pre_validate(self):
        super().pre_validate()
        if not self.evento:
            raise self.ValidateError(
                "Para carregar esse é arquivo é preciso informar o evento"
            )

    def _convert_valor(self, valor):
        return round(int(valor) / 100.0, 2)

    def _convert_qnt(self, valor):
        return int(valor)

    def get_cod(self):
        return "XX"

    def get_identification_obj(self, obj):
        return "%015s%s%05d%s%s" % (
            obj.get("matricula", ""),
            obj.get("tipo", "X"),
            self.payroll.pk,
            obj.get("evento").numero,
            self.get_cod(),
        )

    def get_typeof(self):
        return "PLANSAUDE"

    def remove_events(self, paycheck, params):
        params_ = {}
        if "pk" in params:
            params_["pk"] = params["pk"]
        else:
            params_["evento"] = params.get("evento")

        fe = paycheck.lancamentos.get(**params_)
        params_ = {
            "evento": fe.evento,
            "info": fe.info,
            "valor": fe.valor,
            "prazo": fe.prazo,
            "qnt": fe.qnt,
            "pct": fe.pct,
        }

        deleteds = paycheck.delete_evento([fe.pk])
        paycheck.consolidate()
        if deleteds:
            params_["pk"] = deleteds[0].pk
        return params_

    def update_event(self, paycheck, params):
        params_ = params.copy()
        if "id" not in params_:
            lancamento = paycheck.lancamentos.filter(evento=params_.get("evento"))
            if "info" in params_ and params_.get("info"):
                params_["id"] = lancamento.get(info=params_.get("info")).pk
            else:
                params_["id"] = lancamento.get().pk

        if params["evento"].automatico and params["evento"].calculo:
            # Incluindo um evento automatico
            calc = params["evento"].calculo.cls(
                paycheck.servidor,
                paycheck.folha,
                params["evento"],
                params=params,
                pension=paycheck.pensioner,
            )
            params_.update(calc.calcular())

        fe, created, old_fields = paycheck.update_or_create_entry(True, True, **params_)
        paycheck.consolidate()
        params_.update({"pk": fe.pk})
        return params_


@RunCodeManager.register("gfp-loader-plansaude-comparticipacao")
class PlansaudeComparticipacaoLoader(PlanSaudeLoader):
    """
    2789;OTAVIO BARROS DA SILVA;72830;1;8306;I
    FILE_PLAN COMPARTICIPACAO
    0: 19798; MATRICULA
    3: NILZA DAS GRACAS SILVA; NOME
    5: 1; PRAZO
    6: 2159; VALOR
    7: I; TIPO
    """

    CONFIG = {"matricula": 0, "prazo": 5, "valor": 6, "tipo": 7}

    def get_cod(self):
        return "CP"


@RunCodeManager.register("gfp-loader-plansaude-mensalidade")
class PlansaudeMensalidade(PlanSaudeLoader):
    """
    FILE_PLAN MENSALIDADE
    100310;;;ROBSON BATISTA DOS SANTOS;98621491168;3;A
    0: 19798; MATRICULA
    3: NILZA DAS GRACAS SILVA; NOME
    4: 0123456789; CPF
    5: 1; QNT;
    6: I; TIPO (I/A/E)
    """

    CONFIG = {"matricula": 0, "qnt": 5, "tipo": 6}

    def get_cod(self):
        return "ME"


@RunCodeManager.register("gfp-loader-plansaude-taxa")
class PlansaudeTaxaInscricao(PlanSaudeLoader):
    """
    FILE_PLAN TAXA INSCRICAO
    0: 19798; MATRICULA
    3: NILZA DAS GRACAS SILVA; NOME
    5: 1; QNT;
    6: 1147; VALOR
    7: I; TIPO (I/A/E)
    """

    CONFIG = {"matricula": 0, "qnt": 5, "valor": 6, "tipo": 7}

    def get_cod(self):
        return "TX"


@RunCodeManager.register("gfp-loader-plansaude-dependente")
class PlansaudeDependenteIndireto(PlanSaudeLoader):
    """
    FILE_PLAN DEPENDENTE INDIRETO
    029901;;;KEDIMA PEREIRA LIMA;;F;22160;I
    0: 19798; MATRICULA
    3: NILZA DAS GRACAS SILVA; NOME
    5: F;
    6: 2159; VALOR
    7: I; TIPO (I/A/E)
    """

    CONFIG = {
        "matricula": 0,
        # 'evento': 4,
        "valor": 6,
        "tipo": 7,
    }

    def get_cod(self):
        return "DI"


@RunCodeManager.register("gfp-loader-plansaude-parcelamento")
class PlansaudeParcelamento(PlanSaudeLoader):
    """
    FILE_PLAN PARCELAMENTO'
    105610;;;GILCIFRAN ANDRADE MIRANDA;51400;9822;12;A
    0: 105610; MATRICULA
    3: GILCIFRAN ANDRADE MIRANDA; NOME
    4: 51400; EVENTO
    5: 9822; VALOR
    6: 12; QNT
    7: A; TIPO (I/A/E)
    """

    CONFIG = {"matricula": 0, "valor": 5, "qnt": 6, "tipo": 7}

    def get_cod(self):
        return "PA"


@RunCodeManager.register("gfp-loader-plansaude-devolucoes")
class PlansaudeDevolucao(PlanSaudeLoader):
    """
    FILE_PLAN DEVOLUCOES'
    105610;;;GILCIFRAN ANDRADE MIRANDA;12345678910;042016;ME;1;9822;I
    0: 105610; MATRICULA
    3: GILCIFRAN ANDRADE MIRANDA; NOME
    4: 012345678910; CPF
    5: 042016; REFERENCIA (MMAAAA)
    6: ME; TIPO RECEITA (TX|DI|CP|PA|ME|DM|DD)
    7: 1; PARCELAS
    8: 9822; VALOR
    9: I; TIPO (I)
    """

    CONFIG = {
        "matricula": 0,
        "reference_month": 6,
        "reference_year": 6,
        "qnt": 7,
        "valor": 8,
        "tipo": 9,
    }

    def _convert_reference_year(self, reference):
        return int(reference[2:6])

    def _convert_reference_month(self, reference):
        return int(reference[0:2])

    def get_cod(self):
        return "DV"
