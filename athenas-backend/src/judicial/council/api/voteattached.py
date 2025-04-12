# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.api.attached import EJudAttached
from judicial.council.models import VoteAttached
from contrib.nil import nil_pk, nil_unicode


log = getLogger(__name__)


class CouncilVoteAttached(EJudAttached):

    _model = VoteAttached

    def get_params(self, *args, **kargs):
        params = EJudAttached.get_params(self, *args, **kargs)

        if "vote" in params:
            if params.get("vote") != "":
                field = getattr(self.Model, "vote")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(vote=query.get(pk=params.get("vote")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(vote=None)

        return params

    def model_to_dict(self, instance):
        rst = EJudAttached.model_to_dict(self, instance)

        rst.update(
            vote=nil_pk(instance.vote, None),
            vote_unicode=nil_unicode(instance.vote, None),
        )

        return rst
