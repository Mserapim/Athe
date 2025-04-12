#!/usr/bin/env python
# -*- coding:utf-8 -*-

from contrib.decorator import is_public
from contrib.utils import getLogger
from web.services.rpc import CMSServer
from contrib.controller import DefaultController, JsonResponseController

log = getLogger(__file__)


class Services(JsonResponseController):

    @is_public()
    def cms(self, args=[]):
        response = "Indique o procedimento correto."
        if args:
            server = CMSServer()
            procedure = {
                "areas": server.get_areas,
                "links": server.get_links,
                "posts": server.get_posts,
                "files": server.get_files,
                "images": server.get_images,
                "post": server.get_post,
                "tags": server.get_tags,
                "official_docs": server.get_official_docs,
                "cloud_tags": server.get_cloud_tags,
                "search": server.search,
                "search_docs": server.search_docs,
                "pgj_actions_amount_by_county": server.pgj_actions_amount_by_county,
                "pgj_actions_by_county": server.pgj_actions_by_county,
                "batch": server.batch,
                "pong": server.pong,
            }
            # log.info(args)
            params = self.request.GET.dict()

            if "_dc" in params:
                params.pop("_dc")

            response = procedure[args[0]](params)
        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"
        self.render(response)
