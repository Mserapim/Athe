# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import DistributionTable
from contrib.nil import nil_pk, nil_unicode, nil_date


log = getLogger(__name__)


class EJudDistributionTable(Restful):

    _model = DistributionTable

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "end_document" in params:
            if params.get("end_document") != "":
                field = getattr(self.Model, "end_document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(end_document=query.get(pk=params.get("end_document")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(end_document=None)

        if "matter" in params:
            if params.get("matter") != "":
                field = getattr(self.Model, "matter")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(matter=query.get(pk=params.get("matter")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(matter=None)

        if "sectional" in params:
            if params.get("sectional") != "":
                field = getattr(self.Model, "sectional")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(sectional=query.get(pk=params.get("sectional")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(sectional=None)

        if "execution_organ" in params:
            if params.get("execution_organ") != "":
                field = getattr(self.Model, "execution_organ")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        execution_organ=query.get(pk=params.get("execution_organ"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(execution_organ=None)

        if "document" in params:
            if params.get("document") != "":
                field = getattr(self.Model, "document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(document=query.get(pk=params.get("document")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(document=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        nil_vigencia = lambda d, v: nil_date(d.data_vigencia, v) if d else v

        rst.update(
            end_document=nil_pk(instance.end_document, None),
            end_document_unicode=nil_unicode(instance.end_document, None),
            end_document_vigencia=nil_vigencia(instance.end_document, None),
            matter=nil_pk(instance.matter, None),
            matter_unicode=nil_unicode(instance.matter, None),
            sectional=nil_pk(instance.sectional, None),
            sectional_unicode=nil_unicode(instance.sectional, "SEM DESTINÇÃO"),
            execution_organ=nil_pk(instance.execution_organ, None),
            execution_organ_unicode=nil_unicode(instance.execution_organ, None),
            document=nil_pk(instance.document, None),
            document_unicode=nil_unicode(instance.document, None),
            document_vigencia=nil_vigencia(instance.document, None),
            factor=float(instance.factor or 0),
        )

        return rst
