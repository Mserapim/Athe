#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime, locale
from django.contrib.syndication.views import Feed

import {{app_name}}
from lib.rpc import CMSClient

class NewsFeed(Feed):

    title = '{{site_title}}'
    link = 'http://www.mp.to.gov.br/web/'
    description = 'Últimas notícias'

    def items(self):
        return CMSClient('{{app_slug}}').get_posts({
            'areas__slug__in':['destaque', 'outras-noticias'], 'page':1, 'length':30
        }).get('list', [])

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return item['text']

    def item_link(self, item):
        return 'http://www.mp.to.gov.br%s%s' % ({{app_name}}.APPVROOT, item['slug'])

    def item_pubdate(self, item):
        date = item['published_date'].split('/'); date.reverse(); date = [int(i) for i in date]
        return datetime.datetime( *date )

