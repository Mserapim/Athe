from django.conf.urls.defaults import *
from {{app_name}}.feeds import NewsFeed

urlpatterns = patterns('{{app_name}}.views',
    (r'test/?$', 'test'),
    (r'feed/?$', NewsFeed()),

    (r'search/?$', 'search'),

    (r'(?P<area_slug>[a-z0-9\-]+)/(?P<slug>[\d]+\/[\d]+\/[\d]+\/[a-z0-9\-]+)/?$', 'show'),
    (r'(?P<slug>[\d]+\/[\d]+\/[\d]+\/[a-z0-9\-]+)/?$', 'show'),

    (r'tags/(?P<slug>[a-z0-9\-]+)/(?P<page>[0-9]+)?/?$', 'tags'),
    (r'tags/(?P<slug>[a-z0-9\-]+)/?$', 'tags'),

    #(r'(?P<slug>[noticias]+)/(?P<page>[0-9]+)?/?$', 'posts'),
    #(r'(?P<slug>[noticias]+)/?$', 'posts'),

    (r'(?P<slug>[a-z0-9\-]+)/(?P<page>[0-9]+)?/?$', 'posts'),
    (r'(?P<slug>[a-z0-9\-]+)/?$', 'posts'),

    (r'', 'index'),
)

