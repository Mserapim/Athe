# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import RapporteurDocument
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_display
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit
from django.db import transaction


log = getLogger(__name__)


class CouncilRapporteurDocument(BasePartLawsuit, Restful):

    _model = RapporteurDocument

    force_upper = False

    def reconsiderate(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                rapporteur_document = self.get_query().get(
                    pk=self.request.POST.get("pk")
                )
                instance = rapporteur_document.reconsiderate()

            rst.update(
                success=True,
                message="Voto reconsiderado",
                instance=self.model_to_dict(instance),
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o voto que deseja reconsiderar, talvez você não tenha acesso ao mesmo."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "lawsuit" in params:
            if params.get("lawsuit") != "":
                field = getattr(self.Model, "lawsuit")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(lawsuit=query.get(pk=params.get("lawsuit")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lawsuit=None)

        return params

    def model_to_dict(self, instance):
        rst = super(CouncilRapporteurDocument, self).model_to_dict(instance)

        rst.update(
            content=instance.content,
            rapporteur_vote_type=instance.rapporteur_vote_type,
            rapporteur_vote_type_display=nil_display(
                instance, "rapporteur_vote_type", None
            ),
        )

        return rst
