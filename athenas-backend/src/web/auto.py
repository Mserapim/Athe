#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os, random
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.template.defaultfilters import addslashes

from contrib.utils import getLogger
from web.models import Area, Post, Image, File, Link, WebGroup, ContentArea

log = getLogger(__file__)


def make_site(site):
    return Site(site).create()


class Site(object):

    def __init__(self, site):
        self.__site = site
        self.__user = User.objects.get(username="tonyreis")
        self.__lorem_ipsum = [
            """
                Magna pulvinar sit diam sociis, eros montes ac! Sociis enim, velit, phasellus? Porttitor
                eros purus augue, cursus turpis. Adipiscing nunc magnis et nisi scelerisque, sed enim
                integer turpis?
                """,
            """
                Dignissim ridiculus, tortor arcu massa mid pulvinar enim, vel dolor, ridiculus
                magnis purus, elit. Aliquet cursus tincidunt? Mauris. Adipiscing porta. Et nec? Porta.
                Augue hac lacus pulvinar et, ut a etiam! Nisi, nisi cum purus augue magnis, lacus!
                Amet pid, egestas scelerisque montes mus? Egestas amet diam ut nascetur facilisis! Ultrices tortor?
                """,
            """
                Mauris nascetur hac amet? Proin habitasse. Ridiculus eu, odio nunc duis diam sociis elit
                tortor habitasse? Tincidunt mattis adipiscing sit sagittis, ac duis lectus tristique hac.
                Tempor scelerisque, lectus, nunc dis elit habitasse, auctor vut adipiscing proin amet porta aliquet.
                """,
        ]

        self.__menu = Area(
            name="Menu Esquerdo",
            as_link=False,
            can_share=False,
            parent_id=site.id,
            kind_of_content="link",
        )
        self.__tops = Area(
            name="Topos",
            as_link=False,
            can_share=False,
            parent_id=site.id,
            kind_of_content="link",
        )
        self.__banners = Area(
            name="Banners",
            as_link=False,
            can_share=False,
            parent_id=site.id,
            kind_of_content="link",
        )
        self.__news = Area(
            name="Destaque",
            as_link=True,
            can_share=False,
            parent_id=site.id,
            kind_of_content="post",
        )

        self.__areas = [
            self.__menu,
            self.__tops,
            self.__banners,
            self.__news,
            Area(
                name="Popups",
                as_link=False,
                can_share=False,
                parent_id=site.id,
                kind_of_content="link",
            ),
            Area(
                name="Galerias",
                as_link=True,
                can_share=False,
                parent_id=site.id,
                kind_of_content="post",
            ),
            Area(
                name="Páginas",
                as_link=True,
                can_share=False,
                parent_id=site.id,
                kind_of_content="post",
            ),
            Area(
                name="Outras Notícias",
                as_link=True,
                can_share=False,
                parent_id=site.id,
                kind_of_content="post",
            ),
        ]

        self.__posts = [
            Post(
                title="Post de Exemplo na Área %s",
                # abstract= addslashes(self.__lorem_ipsum[0]).replace('\n', ''),
                text=addslashes(
                    "".join(["<p>%s</p>" % p for p in self.__lorem_ipsum])
                ).replace("\n", ""),
                position=9999,
                as_link=False,
                credits="Fulano de Tal",
                published=True,
            ),
            Post(
                title="Outro Post de Exemplo na Área %s",
                # abstract= addslashes(self.__lorem_ipsum[0]).replace('\n', ''),
                text=addslashes(
                    "".join(["<p>%s</p>" % p for p in self.__lorem_ipsum])
                ).replace("\n", ""),
                position=9999,
                as_link=False,
                credits="Fulano de Tal",
                published=True,
            ),
        ]

        self.__links = [
            Link(title="Item 1", position=1, kind=0, url_embed="#", published=True),
            Link(title="Item 1.1", position=1, kind=0, url_embed="#", published=True),
            Link(title="Item 1.1.1", position=1, kind=0, url_embed="#", published=True),
            Link(title="Item 1.1.2", position=1, kind=0, url_embed="#", published=True),
            Link(title="Item 1.2", position=1, kind=0, url_embed="#", published=True),
            Link(
                title="Google",
                position=9999,
                kind=1,
                url_embed="http://google.com",
                published=True,
            ),
            Link(
                title="Galerias",
                position=9999,
                kind=4,
                url_embed="galerias",
                published=True,
            ),
        ]

        self.__banner = Link(
            title="Verificador de Documentos",
            position=1,
            kind=1,
            url_embed="http://athenas.mp.to.gov.br/athenas/docsverify/",
        )

        self.__top = Link(title="Topo", position=1, kind=0, url_embed="#")

    def __create_area(self, area):
        area.save()

        # Retirar este trecho, quando evoluir o sistema de permissões do cms
        if not WebGroup.objects.filter(area=area).exists():
            WebGroup(
                area=area,
                name="Administração %s" % area,
                can_add=True,
                can_change=True,
                can_delete=True,
                can_publish=True,
            ).save()
        # ------------------------------------------------------------------

    def __create_post(self, post, area):
        post.title = post.title % area
        post.publish()
        post.save()

        if not post.areas.filter(id=area.id).exists():
            ContentArea(area=area, content=post.content_ptr).save()

    def __create_link(self, link, area, is_banner=False, is_top=False):
        link.is_banner = is_banner
        if is_banner or is_top:
            image = "banner.jpg" if is_banner else "top.jpg"
            path = os.path.join(settings.MEDIA_ROOT, "files", image)
            with open(path, "rb") as f:
                link.save_file(f, self.__user)

        link.publish()
        link.save()

        if not link.areas.filter(id=area.id).exists():
            ContentArea(area=area, content=link.content_ptr).save()

    def __create_attachment(self, kind, post):
        media = kind()
        media.credits = "Fulano de Tal"

        index = random.randint(1, 5)
        filename = "image%s.jpg" % index
        media.title = "Imagem %s" % index
        mime = "image/jpeg"
        if isinstance(media, File):
            index = random.randint(1, 2)
            filename = "file%s.pdf" % index
            media.title = "Arquivo %s" % index
            mime = "application/pdf"

        path = os.path.join(settings.MEDIA_ROOT, "files", filename)
        with open(path, "rb") as _file:
            _file.content_type = mime
            media.save_file(_file, self.__user)

        media.save()

        media.posts.add(post)
        post.check_attachments()
        post.save()

    # def __create_package(self):
    #     app_slug = self.__site.slug
    #     app_name = self.__site.slug.replace('-', '_')
    #     site_title = self.__site.title
    #     portal_slug = 'portal'
    #     now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    #     #tmp = tempfile.gettempdir()
    #     static_path = os.path.join('/'.join(__file__.split('/')[:-1]), 'static')
    #     template_path = os.path.join(static_path, 'package-templates')
    #     packages_path = os.path.join(static_path, 'packages')
    #     package_file = os.path.join(packages_path, '%s_%s.zip' % (now, app_name))
    #     package_path = os.path.join(packages_path, '%s_%s_package' % (now, app_name))
    #     app_path = os.path.join(package_path, app_name)

    #     if os.access(packages_path, os.W_OK):
    #         if not os.path.exists(package_path): os.mkdir(package_path)
    #         if not os.path.exists(app_path): os.mkdir(app_path)

    #         for template in ('__init__.py.tpl', 'feeds.py.tpl', 'urls.py.tpl', 'views.py.tpl', 'LEIAME.tpl'):
    #             path = os.path.join(template_path, template)
    #             with codecs.open(path, 'r', 'utf-8') as t:
    #                 base = app_path if template != 'LEIAME.tpl' else package_path
    #                 template = template.replace('.tpl', '')
    #                 module_path = os.path.join(base, template)
    #                 with codecs.open(module_path, 'w', 'utf-8') as module:
    #                     content = t.read()
    #                     for place_holder in ('app_name', 'app_slug', 'site_title', 'portal_slug'):
    #                         content = content.replace('{{%s}}' % place_holder, eval(place_holder))
    #                     module.write(content)

    #         #with ZipFile(package_file, 'w') as z:
    #         os.chdir(package_path)
    #         z = ZipFile(package_file, 'w')
    #         z.write(app_name)
    #         z.write('LEIAME')
    #         for f in os.listdir(app_name):
    #             if f is not 'LEIAME':
    #                 z.write(os.path.join(app_name, f))
    #         z.close()
    #         shutil.rmtree(package_path)
    #     else:
    #         raise Exception('Have no permissions to create web app in %s.' % packages_path)
    #     link = package_file.split('/')
    #     link = os.path.join('/%s/static/web' % settings.CONTEXT, *link[link.index('static')+1:])
    #     return link

    def create(self):
        with transaction.atomic():
            for a in self.__areas:
                self.__create_area(a)

            for p in self.__posts:
                self.__create_post(p, self.__news)
                self.__create_attachment(Image, p)
                self.__create_attachment(File, p)

            for i in range(len(self.__links)):
                if i == 1 or i == 4:
                    self.__links[i].parent_id = self.__links[0].id
                elif i == 2 or i == 3:
                    self.__links[i].parent_id = self.__links[1].id
                self.__create_link(self.__links[i], self.__menu)

            self.__create_link(self.__banner, self.__banners, is_banner=True)
            self.__create_link(self.__top, self.__tops, is_top=True)

        # return self.__create_package()
