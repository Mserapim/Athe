# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.apd.models import Commission

log = getLogger(__name__)


class ApdCommission(Restful):
    """Classe representativa do modelo Commission."""

    _model = Commission

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.commission.Manage")')

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)

        if "publication" in params:
            if params.get("publication") != "":
                field = getattr(self.Model, "publication")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(publication=query.get(pk=params.get("publication")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(publication=None)

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                params.update(end_date=None)

        if "previus_commission" in params:
            if params.get("previus_commission") != "":
                field = getattr(self.Model, "previus_commission")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        previus_commission=query.get(
                            pk=params.get("previus_commission")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previus_commission=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                params.update(start_date=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            publication=nil_pk(instance.publication, None),
            publication_unicode=str(instance.publication) or None,
            end_date=nil_date(instance.end_date, None),
            previus_commission=nil_pk(instance.previus_commission, None),
            previus_commission_unicode=str(instance.previus_commission) or None,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            start_date=nil_date(instance.start_date, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
        )

        return rst
