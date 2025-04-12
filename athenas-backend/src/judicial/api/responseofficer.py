# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import ResponseOfficer
from contrib.utils import DateUtils, person_from_user, employee_from_user
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_date
from rh.models import Pessoa as Person
from django.contrib.auth.models import User


log = getLogger(__name__)


class EJudResponseOfficer(Restful):

    _model = ResponseOfficer

    force_upper = False

    def sign(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        pk = args[0] if args else 0

        try:
            obj = self.Model.objects.get(pk=pk)
            obj.sign()
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar a manifestação desejada.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Documento assinado com sucesso.",
                instance=self.model_to_dict(obj),
            )

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "diligence" in params:
            if params.get("diligence") != "":
                field = getattr(self.Model, "diligence")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(diligence=query.get(pk=params.get("diligence")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(diligence=None)

        return params

    def get_by_diligence(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda."}

        oid = args[0] if args else 0

        try:
            query = self.Model.objects.filter(diligence__pk=oid)
            if query.exists():
                response_officer = query.first()

                rst.update(
                    success=True,
                    message="Dados processados com sucesso",
                    instance=self.model_to_dict(response_officer),
                )
            else:
                rst.update(
                    success=False, message="Diligencia sem resposta", instance=None
                )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            text=instance.text,
            diligence=nil_pk(instance.diligence, None),
            diligence_unicode=nil_unicode(instance.diligence, None),
            diligence_formated_number=(
                ("*" * 3)
                if not instance.diligence
                else instance.diligence.formated_number
            ),
        )

        return rst
