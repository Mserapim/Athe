# -*- coding: utf-8 -*-
from contrib.newrest import RestfulTree
from contrib.utils import getLogger
from judicial.models import LegalClassification
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class EJudLegalClassification(RestfulTree):

    _model = LegalClassification

    folder_index = "father"

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    exclude_fields = ["legalclassification_ptr"]

    full_text_index = (
        "path_cache__icontains",
        "cnmp_code__icontains",
    )

    def export_as_html(self, args=[]):
        self.response.write(self.Model.export_as_html())

    def model_to_node(self, instance):
        rst = RestfulTree.model_to_node(self, instance)

        rst.update(text=instance.cnmp_unicode)

        return rst

    def get_params(self, *args, **kargs):
        params = super(EJudLegalClassification, self).get_params(*args, **kargs)
        log.info(params)

        if "version" in params:
            if params.get("version") != "":
                field = getattr(self.Model, "version")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(version=query.get(pk=params.get("version")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(version=None)

        if "father" in params:
            if params.get("father") != "":
                field = getattr(self.Model, "father")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(father=query.get(pk=params.get("father")))
                except Exception as e:
                    params.pop("father")
            else:
                params.update(father=None)

        for flag in [
            "administrative_classification",
            "judicial_classification",
            "helper_can_sign",
            "collaborator_can_sign",
            "suspend_deadline",
            "extend_deadline",
        ]:
            if flag in params:
                args = {flag: params.get(flag, "off").lower() == "on"}
                params.update(args)

        return params

    def model_to_dict(self, instance):
        _dict_ = RestfulTree.model_to_dict(self, instance)

        _dict_.update(
            version=nil_pk(instance.version, None),
            version_unicode=nil_unicode(instance.version, None),
            title=instance.title,
            cnmp_code=instance.cnmp_code,
            path_cache=instance.path_cache,
            glossary=instance.glossary,
            administrative_classification=instance.administrative_classification,
            judicial_classification=instance.judicial_classification,
            helper_can_sign=instance.helper_can_sign,
            collaborator_can_sign=instance.collaborator_can_sign,
            suspend_deadline=instance.suspend_deadline,
            extend_deadline=instance.extend_deadline,
        )

        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"glossary": "Sem informações"},
        }

        try:

            legalmatter = self.get_query().get(pk=args[0])
            rst.update(
                success=True,
                document={
                    "glossary": legalmatter.glossary,
                },
            )
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não foi possível encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
