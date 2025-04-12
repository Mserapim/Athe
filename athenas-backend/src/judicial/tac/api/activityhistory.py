# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.tac.models import ActivityHistory, Activity
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime


log = getLogger(__name__)


class TacActivityHistory(Restful):

    _model = ActivityHistory

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "activity" in params:
            if params.get("activity") != "":
                field = getattr(self.Model, "activity")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(activity=query.get(pk=params.get("activity")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(activity=None)

        if "author" in params:
            if params.get("author") != "":
                field = getattr(self.Model, "author")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(author=query.get(pk=params.get("author")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(author=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            realized=instance.realized,
            realized_display=nil_display(instance, "realized", None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            description=instance.description,
            activity=nil_pk(instance.activity, None),
            activity_unicode=nil_unicode(instance.activity, None),
            author=nil_pk(instance.author, None),
            author_unicode=nil_unicode(instance.author, None),
            created_at=nil_datetime(instance.created_at, None),
            time=int(instance.time or 0),
            modified_at=nil_datetime(instance.modified_at, None),
            modified_at_unicode=DateUtils.date_to_str(instance.modified_at),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            time_type=instance.time_type,
            time_type_display=nil_display(instance, "time_type", None),
        )

        return rst

    def apply_history(self, args=[]):
        rst = {"success": False, "values": {}}
        try:
            activity_history = self._model.objects.get(pk=self.request.POST["pk"])
            activity = Activity.objects.get(pk=activity_history.activity_id)
            activity.act_history = activity_history
            activity.description = activity_history.description
            activity.time_type = activity_history.time_type
            activity.time = activity_history.time
            activity.realized = activity_history.realized
            activity.save()
        except Exception as e:
            log.info(e)
        else:
            rst.update(success=True)
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
