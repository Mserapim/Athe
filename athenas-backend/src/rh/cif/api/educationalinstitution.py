# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk, nil_new_unicode
from contrib.utils import getLogger
from rh.cif.models import EducationalInstitution

log = getLogger(__name__)


class CifEducationalInstitution(Restful):

    _model = EducationalInstitution

    full_text_index = (
        "nome__icontains",
        "razao_social__icontains",
        "county__nome__icontains",
        "cnpj__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.educational.Manage")')

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "county" in params:
            if params.get("county") != "":
                field = getattr(self.Model, "county")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(county=query.get(pk=params.get("county")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(county=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        cnpj = instance.cnpj
        cnpj = "%s.%s.%s/%s-%s" % (
            cnpj[0:2],
            cnpj[2:5],
            cnpj[5:8],
            cnpj[8:12],
            cnpj[12:],
        )

        rst.update(
            cnpj=str(instance.cnpj),
            cnpj_unicode=str(cnpj),
            data_alteracao=nil_date(instance.data_alteracao, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            nome=nil_new_unicode(instance.nome, ""),
            # pessoajuridica_ptr=instance.pessoajuridica_ptr,
            created_at=nil_datetime(instance.created_at, None),
            razao_social=nil_new_unicode(instance.razao_social, ""),
            modified_at=nil_datetime(instance.modified_at, None),
            # pessoa_ptr=instance.pessoa_ptr,
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            county=nil_pk(instance.county, None),
            county_unicode=nil_new_unicode(instance.county, ""),
        )

        return rst
