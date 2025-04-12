# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import OrdinaceReformulated
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class EJudOrdinaceReformulated(BasePartLawsuit, Restful):

    _model = OrdinaceReformulated

    def get_params(self, *args, **kargs):
        params = super(EJudOrdinaceReformulated, self).get_params(*args, **kargs)

        relateds = ["location", "major_interested", "main_matter"]

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

        return params

    def complement_model_to_dict(self, instance):
        rst = super(EJudOrdinaceReformulated, self).complement_model_to_dict(instance)

        if instance.can_read:
            rst.update(
                change_title=instance.change_title,
                type_ordinace=instance.type_ordinace,
                type_ordinace_display=nil_display(instance, "type_ordinace", None),
                number_part=int(instance.number_part or 0),
                year_number=int(instance.year_number or 0),
                major_interested=nil_pk(instance.major_interested, None),
                major_interested_unicode=nil_unicode(instance.major_interested, None),
                formated_code=instance.formated_code or "não definido ainda".upper(),
                content=instance.content,
                extract_of_port=instance.extract_of_port,
                main_matter=nil_pk(instance.main_matter, None),
                main_matter_unicode=nil_unicode(instance.main_matter, None),
            )

        return rst

    def addition(self, *args, **kargs):
        rst = {"success": False, "message": "Nada foi feito ainda"}

        try:
            ordinance = self.get_query().get(pk=self.request.POST.get("pk", 0))
            instance = ordinance.create_supplement_instance()
            log.debug(instance.pk)
            rst.update(pk=instance.pk)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Portaria preparada para ser aditada.")

        self.renderer(rst)
