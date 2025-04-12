# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.tac.models import ManagementTAC
from contrib.helpers import capitalize_words
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from contrib.middleware import get_current_user


log = getLogger(__name__)


class TacManagementTAC(Restful):

    _model = ManagementTAC

    force_upper = False

    full_text_index = ("description__icontains",)

    def sign(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        pk = args[0]

        try:
            obj = self.Model.objects.get(pk=pk)
            obj.sign_part()
        except self.Model.DoesNotExist:
            rst.update(message="Não consegui encontrar o documento desejado.")
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Documento assinado com sucesso.")

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        log.info(params)
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
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            date_signature=nil_unicode(instance.date_signature, None),
            date_signature_unicode=nil_unicode(instance.date_signature, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            description=instance.description,
            considerations=instance.considerations,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            lawsuit_cache_number=instance.lawsuit.cache_number,
            has_activity_delayed=instance.has_activity_delayed,
            days_to_expiration=instance.days_to_expiration,
            next_date_expiration=nil_datetime(instance.next_date_expiration, None),
        )

        return rst

    def apply_signature(self, args=[]):
        rst = {"success": False, "values": {}}
        try:
            tac = self._model.objects.get(pk=self.request.POST["pk"])
            tac.date_signature = DateUtils.str_to_date(
                self.request.POST["date_signature"]
            )
            tac.author_signature = get_current_user()
            tac.save()
        except Exception as e:
            log.info(e)
        else:
            rst.update(success=True)
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.tac.ManagerTAC')")


class TacManagementAPI(TacManagementTAC):

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update(
            {
                "id": instance.id,
                "lawsuit_kind": instance.lawsuit.get_type_lawsuit_display(),
                "signed": nil_datetime(instance.signed, None),
                "attachments": [
                    self.__fetch_attachments(attach)
                    for attach in instance.attaches.all()
                ],
                "involved_parts": [
                    capitalize_words(str(part))
                    for part in instance.lawsuit.blokes.all()
                ],
            }
        )

        return _dict_

    def __fetch_attachments(self, attach, file_attr="file_descriptor"):
        attach_file = {}
        if hasattr(attach, file_attr):
            attach_file.update(
                {
                    "title": attach.title,
                    "url": getattr(attach, file_attr).no_logged_permalink(),
                }
            )

        return attach_file
