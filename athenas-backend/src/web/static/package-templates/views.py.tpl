#-*- coding:utf-8 -*-

from django.conf import settings
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from lib.cache import do_cache
from lib.snippets import pagination, menu
from lib.rpc import CMSClient, KIND_LINK_CHOICES
from lib.helpers import render, image_thumb, video_thumb, get_logger, dict2object, batch2pars

log = get_logger(__file__)
app_name = '{{app_slug}}'
app_vroot = '%s/%s/' % (settings.VROOT, app_name)
items_per_page = 20
client = CMSClient(app_name)
portal_client = CMSClient('{{portal_slug}}')

def test(request):
    pass

@do_cache(app_name)
def index(request):
    try:
        client.be_lazy()
        data = dict2object(
            batch2pars(
                client \
                    .get_post({'is_index':True, 'image-width':250, 'page':1, 'length':1}, 'post') \
                    .get_links({'areas__slug':'banners', 'page':1, 'length':10, 'image-width':170}, 'banners') \
                .call()
            )
        )
        data.post = image_thumb(data.post, 30, 'square')
        data.post.front_image = data.post.images[0] if data.post.images else None
        return render('templates/default/index-lite.tpl', _vars(vars(data)))
    except:
        client.be_lazy()
        data = dict2object(
            client \
                .get_posts({'areas__slug':'destaque', 'image-width':290, 'page':1, 'length':4 }, 'highlights') \
                .get_posts({'areas__slug':'destaque', 'image-width':64, 'image-cut-mode':'square', 'start':4, 'length':4 }, 'news') \
                .get_posts({'areas__slug':'outras-noticias', 'image-width':64, 'image-cut-mode':'square', 'page':1, 'length':6 }, 'news2') \
                .get_links({'areas__slug':'banners', 'page':1, 'length':10, 'image-width':170}, 'banners') \
            .call()
        )
        pars = { 'highlights': data.highlights.list, 'another_highlights': data.news.list + data.news2.list, 'banners': data.banners.list }
        return render('templates/default/index.tpl', _vars(pars))

@do_cache(app_name)
def show(request, area_slug=None, slug=None):
    image_width = 400
    image_cut_mode = 'width'
    view = 'templates/default/show.tpl'

    post = dict2object(client.get_post({
            'slug': slug, 'areas__slug': area_slug,
            'image-width': image_width, 'image-cut-mode': image_cut_mode
        })
    )
    post.front_image = post.images[0] if post.images else None

    if post.as_gallery:
        post = image_thumb(post, 165, 'square')
        view = 'templates/default/gallery.tpl'
    else:
        post = image_thumb(post, 30, 'square')
        post = video_thumb(post, 191, 'width')
    return render(view, _vars({'post': post, 'page_title': post.title}))

@do_cache(app_name)
def posts(request, slug, page=1):
    posts_pars = { 'image-width':64, 'image-cut-mode':'square', 'page':page, 'length':items_per_page }

    area = {'name':'Notícias'}
    if slug == 'noticias': posts_pars['areas__slug__in'] = ['destaque', 'outras-noticias']
    else:
        areas = dict2object(client.get_areas({'slug':slug, 'page':1, 'length':1}))
        if getattr(areas, 'list', 0) > 0:
            area = areas.list[0]; posts_pars['areas__slug'] = slug
        else: area = ''

    client.be_lazy()
    data = dict2object(
        client \
            .get_posts(posts_pars, 'posts') \
            .get_links({'areas__slug':'banners', 'page':1, 'length':10, 'image-width':170}, 'banners') \
        .call()
    )

    pars = {
        'area':area,
        'posts': data.posts.list,
        'banners' :data.banners.list,
        'pagination': pagination(page, items_per_page, data.posts.total, request)
    }
    return render('templates/default/list-with-area-slug.tpl', _vars(pars))

@do_cache(app_name)
def tags(request, slug=None, page=1):
    client.be_lazy()
    data = dict2object(
        client \
            .get_posts({'tags__slug':slug, 'image-width':64, 'image-cut-mode':'square', 'page':page, 'length':items_per_page }, 'posts') \
            .get_tags({'slug':slug, 'page':1, 'length':1}, 'tags') \
            .get_links({'areas__slug':'banners', 'page':1, 'length':10, 'image-width':170}, 'banners')
        .call()
    )

    tag = data.tags.list[0]; tag.name = 'Tag: %s' % tag.name

    pars = {
        'area':tag, 'posts': data.posts.list, 'banners' :data.banners.list,
        'pagination': pagination(page, items_per_page, data.posts.total, request)
    }
    return render('templates/default/list.tpl', _vars(pars))

@do_cache(app_name)
def search(request):

    SEARCH_OPTS = dict(
        docs = dict(template='templates/default/docs-list.tpl', function=client.search_docs),
        posts = dict(template='templates/default/list.tpl', function=client.search)
    )

    terms = request.GET.get('terms', '').encode('u8')
    page = request.GET.get('page', 1)
    kind = request.GET.get('kind', 'posts')
    length = items_per_page * int(page)
    start = length - items_per_page

    key = '%s:%s' % (kind, slugify(terms))
    option = SEARCH_OPTS[kind]
    results = request.session.get(key)

    if not results:
        results = option['function']({'terms':terms})
        request.session[key] = results

    results = results.get('list', [])

    pars = {
        'area':{'name':'Pesquisa por: %s' % terms},
        'posts': results[start:length],
        'banners': client.get_links({'areas__slug':'banners', 'page':1, 'length':10, 'image-width':170}).get('list', []),
        'pagination': pagination(page, items_per_page, len(results), request)
    }

    return render(option['template'], _vars(pars))

def _vars(pars={}):

    portal_client.be_lazy()
    pars.update(
        batch2pars(
            portal_client \
                .get_cloud_tags(alias='cloudtags') \
                .get_links({'parent__slug__icontains': 'centros-de-apoio'}, 'caops') \
                .get_links({'parent__slug__icontains': 'servicos'}, 'services') \
                .get_links({'parent__slug__icontains': 'outros-links'}, 'another_links') \
                .get_links({'parent__slug__icontains': 'institucional'}, 'institutional') \
                .get_links({'parent__slug__icontains': 'administracao-superior'}, 'admsup') \
                .get_links({'areas__slug': 'presenca', 'image-width': 20}, 'presence') \
            .call()
        )
    )

    client.be_lazy()
    pars.update(
        batch2pars(
            client \
                .get_links({'areas__slug':'menu-esquerdo', 'length':1000}, 'left_menu') \
                .get_links({'areas__slug':'popups', 'image-width':400, 'page':1, 'length':2}, 'popups') \
                .get_links({'areas__slug':'topos', 'image-width':1000, 'page':1, 'length':2}, 'tops') \
            .call()
        )
    )

    default_title = '{{site_title}}'
    title = pars.get('page_title', '')
    title = '%s%s' % (default_title, ' - %s' % title if title else '')

    pars.update({
        'page_title': title,
        'site_name': default_title,
        'app_vroot': app_vroot,
        'app_name': app_name
    })

    return pars

