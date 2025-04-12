# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from judicial.api.legalclassification import EJudLegalClassification
from judicial.models import LegalClassification, LegalClass
from raf.models import Quiz
from django.db.models import Q
from . import util

log = getLogger(__name__)


class RAFLegalClass(EJudLegalClassification):

    _model = LegalClass

    full_text_index = (
        "path_cache__icontains",
        "cnmp_code__icontains",
    )
    #
    # def create_up_path_legalclassification(self, classification_code, taxonomy_type):
    #     spath = ''
    #     retorno = []
    #     while (classification_code is not None):
    #         classification = LegalClassification.objects.filter(cnmp_code=classification_code, taxonomy_type=taxonomy_type).first()
    #         if classification is None:
    #             break
    #         spath = spath + str(classification.id)
    #         if classification.father is None:
    #             break
    #         classification_code = str(classification.father.cnmp_code)
    #         if (classification_code is not None):
    #             spath = spath + ','
    #     if len(spath) > 0:
    #         spath = spath[0:-1]
    #         retorno = spath.split(',')
    #     return retorno

    def create_down_path_legalclassification(self, classification_code, taxonomy_type):
        retorno = []
        while classification_code is not None:
            classification = LegalClassification.objects.filter(
                cnmp_code=classification_code, taxonomy_type=taxonomy_type
            ).first()
            if classification:
                if classification.id not in retorno:
                    retorno.append(classification.id)
                if classification.children.all().count() > 0:
                    for c in classification.children.all():
                        for item in self.create_down_path_legalclassification(
                            c.cnmp_code, taxonomy_type
                        ):
                            if item not in retorno:
                                retorno.append(item)
            classification_code = None
        return retorno

    def get_listclasses(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            keyword = params.get("keyword")
            quiz = Quiz.objects.filter(pk=params.get("quiz")).first()
            legalclasses = []
            excludeclasses = []
            for lc in quiz.legalclasses.all():
                legalclasses = legalclasses + self.create_down_path_legalclassification(
                    lc.cnmp_code, "legalclass"
                )
            for le in quiz.exclude_classes.all():
                excludeclasses = (
                    excludeclasses
                    + self.create_down_path_legalclassification(
                        le.cnmp_code, "legalclass"
                    )
                )
            lista = []
            if keyword:
                lista = (
                    LegalClass.objects.filter(pk__in=legalclasses)
                    .exclude(pk__in=excludeclasses)
                    .filter(
                        Q(cnmp_code__icontains=keyword)
                        | Q(path_cache__icontains=keyword)
                    )
                )
            else:
                lista = LegalClass.objects.filter(pk__in=legalclasses).exclude(
                    pk__in=excludeclasses
                )
            if lista.count() == 0:
                lista = LegalClass.objects.all()
            data = []
            data = [
                {
                    "pk": a.pk,
                    "unicode": a.path_cache,
                    "cnmp_code": a.cnmp_code,
                }
                for a in lista
            ]
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=lista.count(),
                collection=data,
            )
        return self.renderer(rst)
