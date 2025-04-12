# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_display, nil_pk
from contrib.utils import getLogger
from rh.apd.models import DecisionCommission, MemberCommission

log = getLogger(__name__)


class ApdDecisionCommission(Restful):
    """Classe representativa do modelo DecisionCommission."""

    _model = DecisionCommission

    force_upper = False

    def get_params(self, *args, **kargs):
        """GET PARAMS."""
        params = Restful.get_params(self, *args, **kargs)
        member_commission = MemberCommission.objects.get(
            member=self.request.user.servidor
        )
        params.update(member_commission=member_commission)
        if "resource_evaluation" in params:
            if params.get("resource_evaluation") != "":
                field = getattr(self.Model, "resource_evaluation")

                # mater compatibilidade com django-1.4.x
                # get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
                # query = get_queryset()
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        resource_evaluation=query.get(
                            pk=params.get("resource_evaluation")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(resource_evaluation=None)

        # if 'member_commission' in params:
        #     if params.get('member_commission') != '':
        #         field = getattr(self.Model, 'member_commission')

        #         # mater compatibilidade com django-1.4.x
        #         get_queryset = getattr(field, 'get_queryset', getattr(field, 'get_query_set'))
        #         query = get_queryset()

        #         try:
        #             params.update(
        #                 member_commission=query.get(pk=params.get('member_commission'))
        #             )
        #         except Exception as e:
        #             log.exception(e)
        #             raise e
        #     else:
        # params.update(member_commission=None)

        return params

    def model_to_dict(self, instance):
        """MODEL TO DICT."""
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            resource_evaluation=nil_pk(instance.resource_evaluation, None),
            resource_evaluation_unicode=instance.resource_evaluation or None,
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=instance.modified_by or None,
            text=instance.text,
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            decision=instance.decision,
            decision_display=nil_display(instance, "decision", None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=instance.created_by or None,
            member_commission=nil_pk(instance.member_commission, None),
            member_commission_unicode=instance.member_commission or None,
        )

        return rst
