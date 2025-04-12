# -*- coding: utf-8 -*-
import json
from contrib.newrest import Restful
from contrib.utils import getLogger
from django.db import transaction
from contrib.nil import nil_pk, nil_unicode
from judicial.api.partlawsuit import BasePartLawsuit
from judicial.models import GeneralMotion, LegalClassification, OutCourtLawsuit

from rh.models import Lotacao

log = getLogger(__name__)


class EJudGeneralMotion(BasePartLawsuit, Restful):

    _model = GeneralMotion

    def get_params(self, *args, **kargs):
        params = super(EJudGeneralMotion, self).get_params(*args, **kargs)

        if "legal_classification" in params:
            if params.get("legal_classification") != "":
                field = getattr(self.Model, "legal_classification")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        legal_classification=query.get(
                            pk=params.get("legal_classification")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("O movimento deve ser informado.")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudGeneralMotion, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                name=instance.name,
                content=instance.content,
                legal_classification=nil_pk(instance.legal_classification, None),
                legal_classification_unicode=nil_unicode(
                    instance.legal_classification, None
                ),
            )

        return rst

    def sign_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                parts = []
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                name = self.request.POST.get("name", None)
                legal_classification = LegalClassification.objects.get(
                    pk=self.request.POST.get("legal_classification", None)
                )
                content = self.request.POST.get("content", None)

                for lw in lawsuits:
                    obj, created = GeneralMotion.objects.get_or_create(
                        lawsuit=lw,
                        name=name,
                        content=content,
                        legal_classification=legal_classification,
                    )
                    obj.sign_part()
                    obj.create_cache_document()
                    parts.append(obj.pk)

        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(
                success=True,
                message="Documento(s) inserido(s) no(s) procedimento(s).",
                parts=parts,
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def save_batch(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            with transaction.atomic():
                parts = []
                lawsuits = OutCourtLawsuit.objects.filter(
                    pk__in=self.request.POST.getlist("lawsuits")
                )
                name = self.request.POST.get("name", None)
                legal_classification = LegalClassification.objects.get(
                    pk=self.request.POST.get("legal_classification", None)
                )
                content = self.request.POST.get("content", None)

                for lw in lawsuits:
                    obj = GeneralMotion()
                    obj.lawsuit = lw
                    obj.name = name
                    obj.content = content
                    obj.legal_classification = legal_classification

                    obj.save()
                    parts.append(obj.pk)

        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(
                success=True,
                message="Documentos salvos nos procedimentos. É necessário assinar.",
                parts=parts,
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))
