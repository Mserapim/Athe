# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import RejectionFact
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_datetime, nil_display
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudRejectionFact(BasePartLawsuit, Restful):

    _model = RejectionFact

    def sign_decision(self, args=[]):
        rst = {"message": "nada ainda!", "success": False}

        try:
            reject = self.Model.objects.get(pk=args[0])
            reject.sign_decision()
        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possivel encontrar o documento, para buscar a reconsideração."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(message="Reconsideração assinada com sucesso.", success=True)

        self.renderer(rst)

    def store_decision(self, args=[]):
        rst = {"message": "nada ainda!", "success": False}

        try:

            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            if "type_ordinace" in params and not params.get("type_ordinace", 0):
                raise Exception("Informe o campo Instaurar Procedimento")
            if "decision_type" in params and not params.get("decision_type", 0):
                raise Exception("Informe o campo Decisão")

            reject = self.Model.objects.get(pk=args[0])

            reject.type_ordinace = params.get("type_ordinace", None)
            reject.decision_type = params.get("decision_type", None)
            reject.decision_text = params.get("decision_text", "")

            reject.store_decision()

        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possivel encontrar o documento, para buscar a reconsideração."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(message="Reconsideração salva com sucesso.", success=True)

        self.renderer(rst)

    def complement_model_to_dict(self, instance):
        rst = super(EJudRejectionFact, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                despatch=instance.despatch,
                stage=instance.stage,
                rejection_fact_type=instance.rejection_fact_type,
                rejection_fact_type_display=nil_display(
                    instance, "rejection_fact_type", None
                ),
                appeal_formated=instance.appeal_formated,
                decision_type=instance.decision_type,
                decision_type_display=nil_display(instance, "decision_type", None),
                type_ordinace=instance.type_ordinace,
                type_ordinace_display=nil_display(instance, "type_ordinace", None),
                decision_text=instance.decision_text,
                decision_formated=instance.decision_formated,
                decided_by=nil_pk(instance.decided_by, None),
                decided_by_unicode=nil_unicode(instance.decided_by, None),
                decided_at=nil_datetime(instance.decided_at, None),
            )

        return rst

    def renderer_decision_formated(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito até o momento.",
            "document": {
                "content": "Sem informações",
            },
        }

        try:
            decision = self.get_query().get(pk=args[0])
        except self.Model.DoesNotExist as e:
            rst.update(message="Documento desejado não encontrado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            if decision:
                rst.update(
                    success=True, document={"content": decision.decision_formated}
                )

        self.renderer(rst)
