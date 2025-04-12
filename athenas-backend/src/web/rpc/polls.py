# -*- coding:utf-8 -*-

from django.db import transaction

from contrib.decorator import login_required
from contrib.utils import getLogger
from contrib.helpers import err2dict
from contrib.controller import DefaultController

from web.forms import VoteForm
from web.models import Poll


log = getLogger()


class PollsRPC(DefaultController):

    def __init__(self, *args, **kwargs):
        super(PollsRPC, self).__init__(*args, **kwargs)

        self.params = self.request.REQUEST

        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"

    @login_required(type="JSON")
    def list(self, args=[]):
        data = {"total": "0", "list": []}
        site = self.params.get("site")
        if site:
            site_key = "areas" if site.isdigit() else "areas__slug"

            params = {"active": True, site_key: site}

            qs = Poll.objects.filter(Poll.if_published(), **params)

            total = qs.count()
            polls = [
                {
                    "id": poll.id,
                    "title": poll.title,
                    "slug": poll.slug,
                    "show_partials": poll.show_partial,
                    "choices": [
                        {
                            "id": choice.id,
                            "choice": choice.choice,
                            "votes": choice.votes,
                            "percent": choice.percent,
                        }
                        for choice in poll.choices.filter(active=True)
                    ],
                }
                for poll in qs
            ]

            data.update(total=total, list=polls)

        self.render(data)

    @login_required(type="JSON")
    def vote(self, args=[]):
        data = {"success": False, "msg": "Não foi possível computar o voto."}
        form = VoteForm(self.params)
        if form.is_valid():
            poll = form.cleaned_data["poll"]
            choice = form.cleaned_data["choice"]

            try:
                with transaction.atomic():
                    poll.vote(choice)
            except Exception as e:
                data.update(msg=str(e))
                raise e
            else:
                data.update(success=True, msg="Voto computado.")
        else:
            data.update(errors=err2dict(form))

        self.render(data)
