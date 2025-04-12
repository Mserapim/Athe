# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger, DateUtils
from judicial.models import LegacyImport
from contrib.nil import nil_display, nil_pk, nil_unicode
from contrib.nil import nil_date
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudLegacyImport(BasePartLawsuit, Restful):

    _model = LegacyImport

    def get_params(self, *args, **kargs):
        params = super(EJudLegacyImport, self).get_params(*args, **kargs)

        relateds = ["location", "major_interested", "main_matter", "city_location"]

        for related in relateds:
            if related in params:
                if params.get(related) != "":
                    field = getattr(self.Model, related)

                    query = field.get_queryset()

                    try:
                        params.update({related: query.get(pk=params.get(related))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({related: None})

        if params.get("instauration_date", None):
            try:
                params.update(
                    instauration_date=DateUtils.str_to_date(
                        params.get("instauration_date")
                    )
                )
            except Exception as e:
                log.exception(e)
                params.pop("instauration_date")

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudLegacyImport, self).complement_model_to_dict(instance)

        rst.update(
            external_code=instance.external_code,
            import_code=instance.import_code,
            legacy_title=instance.legacy_title,
            remaining_days=instance.remaining_days,
            type_lawsuit=instance.type_lawsuit,
            instauration_date=nil_date(instance.instauration_date, None),
            type_lawsuit_display=nil_display(instance, "type_lawsuit", None),
            city_location=nil_pk(instance.city_location, None),
            city_location_unicode=nil_unicode(instance.city_location, None),
            location=nil_pk(instance.location, None),
            location_unicode=nil_unicode(instance.location, None),
            main_matter=nil_pk(instance.main_matter, None),
            main_matter_unicode=nil_unicode(instance.main_matter, None),
            major_interested=nil_pk(instance.major_interested, None),
            major_interested_unicode=nil_unicode(instance.major_interested, None),
        )

        return rst
