# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.tac.models import Activity
from contrib.utils import DateUtils
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from django.db import transaction
from datetime import date

log = getLogger(__name__)


class TacActivity(Restful):

    _model = Activity

    force_upper = False

    full_text_index = ("description__icontains",)

    def fill_process_number_fine(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                query = self.get_query().filter(
                    pk__in=self.request.POST.getlist("pkset")
                )
                for activity in query:
                    activity.fill_process_number_fine(
                        self.request.POST.get("process_number_fine")
                    )

            rst.update(
                success=True,
                message="Foram preenchidos %d itens com este número de procedimento."
                % query.count(),
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        if "tac" in params:
            if params.get("tac") != "":
                field = getattr(self.Model, "tac")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(tac=query.get(pk=params.get("tac")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(tac=None)

        if "realized" in params:
            if params.get("realized") == "":
                params.update(realized=2)

        if "time_type" in params:
            if params.get("time_type") == "":
                params.update(time_type=0)

        if "time" in params:
            if params.get("time") == "":
                params.update(time=0)

        if "fine_value" in params:
            if params.get("fine_value") == "":
                params.update(fine_value=0)

        if "repair_value" in params:
            if params.get("repair_value") == "":
                params.update(repair_value=0)

        if "process_number_fine" in params:
            if params.get("process_number_fine") == "":
                params.update(process_number_fine="")
                params.update(realized=2)
            else:
                params.update(realized=3)

        return params

    def deadline_left_days(self, instance):

        message = "---"

        if instance.deadline:
            if instance.realized == 0:
                tmp_date = instance.deadline - date.today()
                days = tmp_date.days

                if days >= 1:
                    if days == 1:
                        message = "Resta %s dia" % days
                    else:
                        message = "Restam %s dias" % days

                elif days <= -1:
                    if days == -1:
                        message = "Atrasado à %s dia" % (days * -1)
                    else:
                        message = "Atrasado à %s dias" % (days * -1)

                elif days == 0:
                    message = "Último dia"
        else:
            message = ""

        return message

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        rst.update(
            icons=instance.icons,
            tac=nil_pk(instance.tac, None),
            tac_unicode=nil_unicode(instance.tac, None),
            act_history=nil_pk(instance.act_history, None),
            act_history_unicode=nil_unicode(instance.act_history, None),
            revision_realized=int(instance.activity_history.count()),
            realized=instance.realized,
            realized_display=nil_display(instance, "realized", None),
            description=instance.description,
            time=int(instance.time or 0),
            time_type=instance.time_type,
            time_type_display=nil_display(instance, "time_type", None),
            process_number_fine=nil_unicode(instance.process_number_fine, None),
            fine_value=int(instance.fine_value or 0),
            repair_value=int(instance.repair_value or 0),
            deadline=nil_datetime(instance.deadline, None),
            deadline_left_days=self.deadline_left_days(instance),
        )

        return rst
