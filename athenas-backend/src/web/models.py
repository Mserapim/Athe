# !/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, hashlib, os, re, string, random, calendar
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import urlopen

from django.conf import settings
from django.template.defaultfilters import slugify, striptags
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    CharField,
    SlugField,
    BooleanField,
    IntegerField,
    FloatField,
    DateField,
    DateTimeField,
    TextField,
    OneToOneField,
    ForeignKey,
    ManyToManyField,
    EmailField,
    URLField,
    Q,
    Sum,
    Manager,
    CASCADE,
    SET_NULL,
    PROTECT,
)

from contrib import ezjson
from contrib.utils import getLogger
from contrib.helpers import Resize, BaseConverter
from contrib.middleware import get_current_user

from ged.models import Arquivo as GedFile
from rh.models import Comarca as County, Pessoa as Person, AnonymousPerson
from web.social.share import Twitter


log = getLogger("CMSTRACK - %s" % __name__)


class WebUser(Model):

    def is_token_web_user(self):
        return hasattr(self, "tokenwebuser")

    def is_lawyer_user(self):
        if hasattr(self.person, "pessoafisica"):
            return hasattr(self.person.pessoafisica, "lawyer")
        return False

    def user_kind(self):
        kind = "individual"
        if self.is_token_web_user():
            kind = "token"
        elif self.is_lawyer_user():
            kind = "lawyer"
        return kind


class RegularWebUser(WebUser):

    username = CharField(max_length=100, db_index=True)
    password = CharField(max_length=128, db_index=True)
    salt = CharField(max_length=10, default="%$&@")
    email = EmailField(null=True)
    password_expires = DateTimeField(null=True)

    person = OneToOneField(
        Person, related_name="web_user", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    @classmethod
    def sugest_password(self, min_size=5, max_size=8):
        alphabet = "".join(["!@#$%&", string.ascii_letters, string.digits])

        random.seed(hash(os.urandom(4096)))
        alphabet = list(alphabet)
        random.shuffle(alphabet)
        alphabet = "".join(alphabet)
        return "".join(
            [random.choice(alphabet) for x in range(random.randint(min_size, max_size))]
        )

    @classmethod
    def sugest_username(klass, base):
        if not klass.objects.filter(username=base).exists():
            return base
        else:
            count = klass.objects.filter(username__icontains=base).count()
            for number in range(count, count + 5):
                sugested = "%s%d" % (base, number)
                if not klass.objects.filter(username=sugested).exists():
                    return sugested
            return None

    @classmethod
    def authenticate(cls, username, password):
        qs = cls.objects.filter(username=username)
        if qs.exists():
            user = qs.latest("id")
            if user.check_password(password):
                return user

    def __digest_password(self, password):
        return hashlib.sha512(("%s%s" % (password, self.salt)).encode()).hexdigest()

    def set_password(self, password):
        self.password = self.__digest_password(password)

    def check_password(self, password):
        return self.__digest_password(password) == self.password

    def __str__(self):
        return "%s <%s>" % (
            self.username,
            self.email if self.email else "sem email cadastrado",
        )


class PasswordChangeRequest(Model):
    created_at = DateTimeField(auto_now_add=True, null=True)
    key = CharField(max_length=64, db_index=True)
    valid = BooleanField(default=True, db_index=True)
    user = ForeignKey(
        RegularWebUser,
        related_name="password_change_requests",
        null=True,
        on_delete=CASCADE,
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = hashlib.sha256(os.urandom(4096)).hexdigest()
        super(PasswordChangeRequest, self).save(*args, **kwargs)


class TokenWebUser(WebUser):
    token = CharField(max_length=150, db_index=True)

    person = OneToOneField(
        AnonymousPerson, related_name="anonymous_web_user", null=True, on_delete=CASCADE
    )

    def save(self, *args, **kwargs):

        if not self.pk:
            salt = 238327
            number = TokenWebUser.objects.all().count() + 1

            if not self.token:
                self.token = BaseConverter.baseN_encode(number + salt)

            person_name = "Anonymous person for TokenWebUser %s" % self.token
            self.person, created = AnonymousPerson.objects.get_or_create(
                nome=person_name
            )

        super(TokenWebUser, self).save(*args, **kwargs)


class CommonManager(Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


# Criado depois do modelo Area, por isso Area não herda de Common
class Common(Model):

    objects = CommonManager()

    name = CharField(max_length=150)
    slug = SlugField(max_length=150, blank=True)

    def natural_key(self):
        return (self.slug,)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)

        # create and change unique slug
        if self.slug != slug:
            qs = Common.objects.filter(slug=slug)
            if qs.exists():
                # raise Exception('Este nome já está em uso. Escolha outro.')
                slug = "%s-%s" % (slug, qs.count())
            self.slug = slug
        super(Common, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class Module(Common):
    """
    Módulos existentes:
        post => Posts
        link => Links
        poll => Polls
        pgj-actions => PGJ Actions
    """

    pass


class Category(Common):
    parent = ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    path = CharField(blank=True, max_length=200)
    no_root_path = CharField(blank=True, max_length=200)
    position = IntegerField("Ordem", default=9999, db_index=True, blank=True)
    computed_position = CharField(
        "Ordem com subnível", max_length=20, default="", db_index=True, blank=True
    )
    url = CharField("Url", max_length=400, default="", db_index=True, blank=True)

    def walk_through_parents(self):
        if self.parent:
            return self.parent.walk_through_parents() + [self.parent.name]
        return []

    def path_nodes(self):
        return self.walk_through_parents() + [self.name]

    def make_path(self):
        return " > ".join(self.path_nodes())

    def root_category_name(self):
        nodes = self.path.split(" > ")
        return nodes[0] if len(nodes) > 1 else self.name

    def no_root_make_path(self):
        nodes = self.path_nodes()
        return " > ".join(nodes[1:]) if len(nodes) > 1 else self.make_path()

    def compute_parents_positions(self):
        return (
            self.parent.compute_parents_positions() + [str(self.parent.position)]
            if self.parent
            else []
        )

    def compute_position(self):
        return "".join(self.compute_parents_positions() + [str(self.position)])

    def descendants(self):
        items = []
        qs = self.children.order_by("position").distinct()
        for child in qs:
            if child.url or child.posts.exists():
                items.append(child)
            if child.children.all().exists():
                items = items + child.descendants()
        return items

    def save(self, *args, **kwargs):
        self.computed_position = self.compute_position()
        self.path = self.make_path()
        self.no_root_path = self.no_root_make_path()
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.path


class AreaManager(Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Area(Model):

    KINDS_OF_CONTENT_CHOICES = (
        ("area", "Area"),
        ("link", "Link"),
        ("post", "Post"),
        ("pgj-actions", "PGJ Actions"),
    )

    objects = AreaManager()

    name = CharField("Nome", max_length=128, db_index=True)
    fullname = CharField("Nome completo", max_length=256)
    slug = SlugField("Slug", max_length=256, db_index=True)
    active = BooleanField("Ativo", default=True, db_index=True)
    as_link = BooleanField("Como link", default=False, db_index=True)
    can_share = BooleanField("Pode compartilhar", default=False, db_index=True)
    kind_of_content = CharField(
        "Tipo de conteúdo",
        max_length=100,
        default="area",
        choices=KINDS_OF_CONTENT_CHOICES,
    )
    items_no_searchable = BooleanField(
        "Remover da pesquisa?", default=False, db_index=True, blank=True
    )
    icon_area = ForeignKey(GedFile, null=True, blank=True, on_delete=PROTECT)
    icon_area_path_cache = CharField(
        "Path do ícone", max_length=200, null=True, blank=True
    )
    parent = ForeignKey(
        "self",
        verbose_name="Subitens",
        null=True,
        related_name="children",
        on_delete=CASCADE,
    )
    modules = ManyToManyField(Module, related_name="sites")

    categories = ManyToManyField(Category, related_name="sites", blank=True)

    @property
    def leaf(self):
        return not self.children.exists()

    def descendants(self, pk_only=False):
        items = []
        for child in self.children.all():
            mixed = child.pk if pk_only else child
            items.append(mixed)
            if child.children.all().exists():
                items = items + child.descendants(pk_only)
        return items

    @property
    def path(self):
        if self.parent is None:
            return self.name
        else:
            return ", ".join([self.name, self.parent.path])

    def calculate_height(self):
        if self.parent is None:
            return 0
        else:
            return 1 + self.parent.calculate_height()

    def natural_key(self):
        return (self.slug,)

    def is_site(self):
        return self.parent is None

    def get_path(self):
        if self.is_site():
            return "/%s" % self.slug
        return "%s/%s" % (self.parent.get_path(), self.slug)

    def get_absolute_url(self):
        if self.parent:
            return "%s/%s" % (self.parent.slug, self.slug)
        return "/%s" % self.slug

    def resize_image(self, coord, size, force_save=False):
        try:
            path = self.icon_area.absolute_path
            if not os.path.exists(path):
                path = os.path.join(settings.MEDIA_ROOT, "files/blank.jpg")

            if self.icon_area.mimetype not in ["image/jpeg", "image/png"]:
                raise Exception("Erro: arquivo %s não é um arquivo de imagem." % path)
            resizer = Resize(path, force_save)
            resizer.do({coord: size})
            url = resizer.permalink()
        except Exception as e:
            url = ""
            log.error(
                "%s => [params] path: %s, coord: %s, size: %s" % (e, path, coord, size)
            )
            log.exception(e)
        return url

    def create_icon_path_cache(self, coord="square", size=200):
        self.icon_area_path_cache = None
        if self.icon_area:
            self.icon_area_path_cache = self.resize_image(coord, size)

    def save(self, *args, **kwargs):
        self.fullname = (
            "%s / %s" % (self.parent, self.name) if self.parent else "%s" % self.name
        )
        slug = slugify(self.name)

        # create and change unique slug
        if self.slug != slug:
            if Area.objects.filter(parent=self.parent, slug=slug, active=True).exists():
                raise Exception("Este nome de área já está em uso. Escolha outro.")
            self.slug = slug

        self.create_icon_path_cache()
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        return self.fullname


class WebGroupManager(Manager):

    def get_by_natural_key(self, name):
        return self.get(name=name)


class WebGroup(Model):

    objects = WebGroupManager()

    name = CharField("Nome", max_length=128, db_index=True)
    can_add = BooleanField("Pode Criar", default=False, db_index=True)
    can_change = BooleanField("Pode Alterar", default=False, db_index=True)
    can_delete = BooleanField("Pode Deletar", default=False, db_index=True)
    can_publish = BooleanField("Pode Publicar", default=False, db_index=True)
    active = BooleanField("Ativo", default=True, db_index=True)

    area = ForeignKey(
        Area, related_name="groups", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    users = ManyToManyField(User, related_name="web_groups")

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return "%s - %s" % (self.name, self.area)


class ContentManager(Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Content(Model):

    MONTH_CHOICES = [
        (month, calendar.month_name[month].capitalize()) for month in list(range(1, 13))
    ]

    objects = ContentManager()

    title = CharField("Post", max_length=256)
    slug = CharField("Slug", max_length=256, db_index=True, blank=True)
    credits = CharField("Créditos", max_length=256, null=True, blank=True)
    create_date = DateTimeField(
        "Data de criação", db_index=True, auto_now_add=True, blank=True
    )
    updated_at = DateTimeField(
        "Atualizando em", null=True, auto_now=True, db_index=True, blank=True
    )
    ref_year = IntegerField("Ano de referência", null=True, blank=True, db_index=True)
    ref_month = IntegerField(
        "Mês de referência", null=True, blank=True, db_index=True, choices=MONTH_CHOICES
    )
    published = BooleanField("Publicado", default=False, db_index=True, blank=True)
    published_date = DateTimeField(
        "Data de publicação", null=True, db_index=True, blank=True
    )
    publication_start = DateTimeField(
        "Inicio da publicação", null=True, db_index=True, blank=True
    )
    publication_end = DateTimeField(
        "Fim da publicação", null=True, db_index=True, blank=True
    )
    active = BooleanField("Ativo", default=True, db_index=True, blank=True)
    position = IntegerField("Ordem", default=9999, db_index=True, blank=True)
    has_comment = BooleanField(
        "Tem comentário", default=False, db_index=True, blank=True
    )
    has_tag = BooleanField("Tem tag", default=False, db_index=True, blank=True)
    has_meta = BooleanField("Tem metadados", default=False, db_index=True, blank=True)
    as_link = BooleanField("Como link?", default=False, db_index=True, blank=True)
    as_gallery = BooleanField("Como galeria?", default=False, db_index=True, blank=True)
    views = IntegerField("Visualizações", default=0, db_index=True, blank=True)

    areas = ManyToManyField(
        Area, through="ContentArea", verbose_name="Áreas", related_name="contents"
    )

    class Meta:
        unique_together = (("slug", "create_date"),)

    def natural_key(self):
        return (self.slug,)

    @property
    def specialization(self):
        subclasses = [sc.__name__.lower() for sc in self.__class__.__subclasses__()]

        descendant = None
        for name in subclasses:
            if hasattr(self, name):
                descendant = getattr(self, name)
                break

        return descendant

    @classmethod
    def if_published(cls):
        today = datetime.date.today()
        dynamic = Q(publication_start__lte=today, publication_end__gte=today)
        static = Q(published=True)
        return dynamic | static

    def publish(self, start=None, end=None):
        if isinstance(start, datetime.date) and isinstance(end, datetime.date):
            self.published_date = start
            self.publication_start = start
            self.publication_end = end
        else:
            self.published = True
        self.published_date = (
            start if isinstance(start, datetime.datetime) else datetime.datetime.now()
        )

    def unpublish(self):
        self.publication_start = None
        self.publication_end = None
        # self.published_date = None  # Não deve ser setado como None para saber se a enquete foi finalizada
        self.published = False

    def is_published(self):
        static = self.published
        today = datetime.date.today()
        dynamic = (
            self.publication_start
            and self.publication_end
            and self.publication_start.date() >= today <= self.publication_end.date()
        )
        return bool(static or dynamic)

    def clear_cache(self):
        site = "__nosite__"

        areas = []
        if isinstance(self, Multimedia) and hasattr(self, "posts"):
            areas = self.posts.all().latest("id").areas.filter(active=True)
        else:
            areas = self.areas.filter(active=True)

        if areas.exists():
            site = areas[0].parent or areas[0]

        for area in areas:
            pars = dict(
                app_slug=site.slug,
                area=area.slug,
                slug=self.slug,
                secret_key=settings.WEB_SECRET_KEY,
            )

            conn = None
            try:
                conn = urlopen(
                    "%s/site-manager/clear-cache/?%s" % (settings.WEB, urlencode(pars))
                )
            except Exception as e:
                log.exception(e)
                log.info(pars)
            else:
                if conn is None:
                    raise Exception("Não foi possível conectar com o servidor web")

                response = conn.read()
                if not response:
                    raise Exception("Não foi possível obter resposta do servidor web")

                try:
                    response = ezjson.load(response.decode())
                except Exception as e:
                    log.exception(e)
                    log.info(response)
                    raise Exception("A resposta não está no formato json")
                else:
                    if not response["success"]:
                        raise Exception(
                            "Não foi possível realizar a limpeza do cache. %s"
                            % response["message"]
                        )

    def create_slug(self):
        slug = "%s/%s" % (self.published_date.strftime("%Y/%m/%d"), slugify(self.title))
        qs = Content.objects.filter(slug=slug)
        if qs.exists():
            now = datetime.datetime.now()
            slug = "%s/%s-%s" % (
                self.published_date.strftime("%Y/%m/%d"),
                now.strftime("%f"),
                slugify(self.title),
            )
        return slug

    def is_slug_changed(self):
        test = slugify(self.title)
        current = re.sub(r"^([0-9\-]{7})", "", self.slug.split("/")[-1])
        return test != current

    def save(self, *args, **kwargs):
        if self.is_published():
            if self.slug:
                if self.is_slug_changed():
                    current_url_key = self.slug
                    self.slug = self.create_slug()

                    post = getattr(self, "post", None)

                    qs_link = Link.objects.filter(url_embed__icontains=current_url_key)
                    if qs_link.exists() and post:
                        for link in qs_link:
                            link.url_embed = post.get_absolute_url()
                            link.save()
            else:
                self.slug = self.create_slug()

            if self.id:
                self.clear_cache()

        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Post(Content):
    text = TextField("Texto", null=True, blank=True)
    shared = BooleanField("Compartilhado?", default=False, db_index=True, blank=True)
    has_link = BooleanField("Tem link?", default=False, db_index=True, blank=True)
    has_file = BooleanField("Tem arquivo?", default=False, db_index=True, blank=True)
    has_image = BooleanField("Tem imagem?", default=False, db_index=True, blank=True)
    has_audio = BooleanField("Tem audio?", default=False, db_index=True, blank=True)
    has_video = BooleanField("Tem vídeo?", default=False, db_index=True, blank=True)
    is_index = BooleanField(
        "Página Principal?", default=False, db_index=True, blank=True
    )
    no_searchable = BooleanField(
        "Remover da pesquisa?", default=False, db_index=True, blank=True
    )

    # content_ptr = OneToOneField(Content, parent_link=True, related_name='post_child', blank=True, on_delete=CASCADE)  # Parametro "on_delete" adicionado. (Django 2)

    categories = ManyToManyField(Category, related_name="posts", blank=True)

    @property
    def abstract(self):
        text = striptags(self.text)
        length = len(text)
        size = 200 if length >= 200 else length
        return text[:size]

    def get_absolute_url(self):
        qs = self.areas.filter(active=True)
        site = qs[0].parent.slug if qs.exists() and qs[0].parent else "portal"
        return "/%s/%s" % (site, self.slug)

    def get_domain_absolute_url(self):
        return "https://%s%s" % (settings.WEB_DOMAIN, self.get_absolute_url())

    def get_hashtags(self):
        return [
            "#%s" % "".join([hashtag.lower() for hashtag in tag.slug.split("-")])
            for tag in self.tags.filter(active=True)
        ]

    def share(self):
        if self.is_published():
            return Twitter().tweet_by_model(self)
        return "É necessário publicar para compartilhar."

    def check_files(self):
        """Checks if exists any associate file in current post.
        If not, then sets as False the flag has_file"""
        self.has_file = self.files.filter(active=True).exists()

    def check_images(self):
        """Checks if exists any associate image in current post.
        If not, then sets as False the flag has_image"""
        self.has_image = self.images.filter(active=True).exists()

    def check_audios(self):
        """Checks if exists any associate audio in current post.
        If not, then sets as False the flag has_audio"""
        self.has_audio = self.audios.filter(active=True).exists()

    def check_videos(self):
        """Checks if exists any associate video in current post.
        If not, then sets as False the flag has_video"""
        self.has_video = self.videos.filter(active=True).exists()

    def check_attachments(self):
        """Checks if exists any associate multimedia file (file, image, audio and video)
        in current post. If not, then sets as False the flag has_image"""
        self.check_files()
        self.check_images()
        self.check_audios()
        self.check_videos()

    def breadcrumb(self):
        link = Link.objects.filter(
            Link.if_published(), active=True, url_embed__endswith=self.slug
        ).last()
        if link:
            nodes = self.__breadcrumb_nodes(link)
            pieces = ['<li class="badge">%s</li>' % node.strip() for node in nodes]
            return " ".join(pieces)
        return ""

    def __breadcrumb_nodes(self, node):
        if node:
            steps = []
            if hasattr(node, "parent") and node.parent:
                steps = self.__breadcrumb_nodes(node.parent) + steps
            steps.append(node.title)
        return steps


class Multimedia(Content):
    url_embed = CharField(max_length=400, db_index=True, default="#", blank=True)
    ged = ForeignKey(
        GedFile,
        verbose_name="Arquivo",
        null=True,
        related_name="web_media",
        on_delete=CASCADE,
    )
    public_access = BooleanField(verbose_name="Acesso público", default=True)

    def check_type(self):
        types = ["link", "image", "video", "audio", "file"]
        for t in types:
            if hasattr(self, t):
                return t

    def get_link(self, coord="width", size=800):
        if self.ged and self.is_image_like():
            return self.resize_image(coord, size)

    def is_public(self):
        if self.ged:
            return self.ged.acesso == 3
        return self.public_access

    def is_image_like(self):
        return (
            isinstance(self, Image) or isinstance(self, Video) or isinstance(self, Link)
        )

    def get_image_path(self):
        path = self.ged.absolute_path
        if not os.path.exists(path):
            path = os.path.join(settings.MEDIA_ROOT, "files/blank.jpg")
        return path

    def resize_image(self, coord, size, force_save=False):
        try:
            path = self.get_image_path()
            if self.ged.mimetype not in ["image/jpeg", "image/png"]:
                raise Exception("Erro: arquivo %s não é um arquivo de imagem." % path)
            resizer = Resize(path, force_save)
            resizer.do({coord: size})
            url = resizer.permalink()
        except Exception as e:
            url = ""
            log.error(
                "%s => [params] path: %s, coord: %s, size: %s" % (e, path, coord, size)
            )
            log.exception(e)
        return url

    def get_absolute_url(self, coord="width", size=800):
        return self.get_link(coord=coord, size=size)

    def save(self, *args, **kwargs):

        if self.ged:
            self.ged.acesso = 3 if self.public_access else 2
            self.ged.save()

        if not getattr(self, "_is_link", False) and not self.published:
            self.publish()

        if self.ged and self.is_image_like():
            if self.ged.mimetype not in ["image/jpeg", "image/png"]:
                raise Exception(
                    "Permitido somente arquivo de imagem. Você está cadastrando um tipo %s"
                    % self.ged.mimetype
                )

            for coord in getattr(settings, "IMAGE_SIZES", []):
                mode, size = coord.split("|")
                log.info("Image mode and size: %s, %s" % (mode, size))
                Resize(self.get_image_path(), force=True).do({mode: size})

        super(Multimedia, self).save(*args, **kwargs)


class Link(Multimedia):

    KIND_LINK_CHOICES = (
        (0, "Super"),
        (1, "Externo"),
        (2, "Para Área"),
        (3, "Para Post"),
        (4, "Para Galeria"),
    )

    is_banner = BooleanField("É banner", default=False, db_index=True)
    fullname = CharField("Nome completo", max_length=500)
    kind = IntegerField(
        "Tipo de Link", choices=KIND_LINK_CHOICES, default=1, db_index=True
    )

    parent = ForeignKey("self", related_name="children", null=True, on_delete=CASCADE)

    def has_child(self):
        return bool(
            [
                child
                for child in self.children.filter(active=True)
                if child.is_published()
            ]
        )

    def cascade_publish(self, func_name, **kwargs):

        apply_to = lambda x: getattr(x, func_name)(**kwargs)

        qs = self.children.filter(active=True)
        for link in qs:
            link.cascade_publish(func_name, **kwargs)

        if self.kind == 3:
            slug = "/".join(self.url_embed.split("/")[-4:])
            post = Post.objects.filter(active=True, slug=slug).first()
            if post:
                apply_to(post)
                post.save()

        apply_to(self)
        self.save()

    def walk_through_parents(self):
        if self.parent:
            return self.parent.walk_through_parents() + [self.parent.title]
        return []

    def make_fullname(self):
        return "/ ".join(self.walk_through_parents() + [self.title])

    def walk_through_parent_links(self, depth=0):
        parents = []
        if getattr(self, "parent", None):

            if depth < 10:
                depth += 1
                parents = self.parent.walk_through_parent_links(depth)
                depth -= 1
            else:
                print(
                    "\nMAX_DEPTH: %s %s\n"
                    % (self.pk, " / ".join(parents + [self.title]))
                )
        return parents + [self.title]

    def descendants(self, pk_only=False):
        items = []
        for child in self.children.all():
            mixed = child.pk if pk_only else child
            items.append(mixed)
            if child.children.all().exists():
                items = items + child.descendants(pk_only)
        return items

    def make_fullname(self):
        return " / ".join(self.walk_through_parent_links())

    def save(self, *args, **kwargs):

        if not getattr(self, "_no_fullname", False):
            self.fullname = self.make_fullname()[:500]

        if getattr(self, "content", None):
            self.url_embed = self.content.specialization.get_absolute_url()

        self._is_link = True

        super(Link, self).save(*args, **kwargs)

    def __str__(self):
        return self.fullname


class Image(Multimedia):
    posts = ManyToManyField(Post, verbose_name="Posts", related_name="images")


class Video(Multimedia):
    posts = ManyToManyField(Post, verbose_name="Posts", related_name="videos")

    def get_video_url(self):
        url = "https://youtube.com/embed/%s?autoplay=1" % self.get_video_code()
        return url

    def get_video_code(self):
        video_code = ""

        embed_code = self.url_embed.replace("\\", "")

        if embed_code.startswith("<iframe"):
            match = re.search(
                '<.+ src="([a-zA-Z0-9_:\-\./\?=]+)".*>.*</.+>', embed_code
            )
            if match and len(match.groups()) > 0:
                video_code = match.groups()[0].split("/")[-1]
                if "?" in video_code:
                    video_code = video_code.split("?")[0]

        elif embed_code.startswith("http"):
            parsed = urlparse.urlparse(embed_code)
            video_code = parse_qs(parsed.query).get("v")
            if isinstance(video_code, list):
                video_code = video_code[0]

        return video_code


class Audio(Multimedia):
    posts = ManyToManyField(Post, verbose_name="Posts", related_name="audios")


class File(Multimedia):
    posts = ManyToManyField(Post, verbose_name="Posts", related_name="files")

    class Meta:
        ordering = ["position", "ref_month", "title"]

    def get_link(self, *args, **kwargs):
        return self.get_absolute_url()

    def get_absolute_url(self):
        if self.ged:
            return self.ged.no_logged_permalink()

    def __str__(self):
        title = self.title
        if self.ref_month:
            title = "%s - %s" % (self.ref_month, self.title)
        return title


class ContentArea(Model):
    original = BooleanField("Original", default=False, db_index=True, blank=True)

    area = ForeignKey(
        Area, verbose_name="Área", related_name="content_area", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    content = ForeignKey(
        Content, verbose_name="Post", related_name="content_area", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s em %s" % (self.content, self.area.fullname)


class Tag(Model):
    name = CharField("Nome", max_length=128)
    slug = SlugField("Slug", max_length=384, db_index=True)
    active = BooleanField("Ativo", default=True, db_index=True)

    contents = ManyToManyField(Content, verbose_name="Contents", related_name="tags")

    def get_absolute_url(self):
        qs_contents = self.contents.filter(active=True)
        qs_areas = (
            qs_contents[0].areas.filter(active=True)
            if qs_contents.exists()
            else qs_contents.none()
        )
        site = (
            qs_areas[0].parent.slug
            if qs_areas.exists() and qs_areas[0].parent
            else "portal"
        )
        return "/%s/tags/%s" % (site, self.slug)

    def __str__(self):
        return "%s" % self.name


class MetaKey(Model):
    title = CharField("Título", max_length=128)
    name = CharField("Chave", max_length=128, db_index=True)
    active = BooleanField("Ativo", default=True, db_index=True)

    site = ForeignKey(
        Area, null=True, related_name="metadata_keys", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s" % self.title


class MetaValue(Model):
    value = CharField("Valor", max_length=384, db_index=True)
    active = BooleanField("Ativo", default=True, db_index=True)

    key = ForeignKey(
        MetaKey, verbose_name="Chave", related_name="meta_values", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    contents = ManyToManyField(Content, verbose_name="Posts", related_name="metadata")

    def __str__(self):
        return "%s [%s]: %s" % (self.key.title, self.key.name, self.value)


class Comment(Model):
    person_name = CharField("Nome", max_length=256)
    person_email = CharField("Email", max_length=256, null=True, blank=True)
    created_at = DateTimeField("Data de criação", auto_now_add=True, blank=True)
    text = TextField("Comentário")
    active = BooleanField("Ativo", default=True, db_index=True, blank=True)

    user = ForeignKey(
        User, related_name="web_comments", null=True, blank=True, on_delete=CASCADE
    )
    contents = ForeignKey(
        Content, verbose_name="Post", related_name="comments", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        permissions = (("can_disable_comment", "Pode desativar um comentário."),)

    @property
    def author_name(self):
        name = self.person_name
        if (
            getattr(self, "user", None)
            and getattr(self.user, "servidor", None)
            and getattr(self.user.servidor, "pessoa_fisica", None)
        ):
            name = self.user.servidor.pessoa_fisica.nome
        return " ".join([part.capitalize() for part in name.split(" ")])

    @property
    def author_email(self):
        return self.user.email if getattr(self, "user", None) else self.person_email

    @property
    def author_username(self):
        return self.user.username if getattr(self, "user", None) else ""

    def count_comments_per_time(self, hours=24, kind="all"):
        user = get_current_user()
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(hours=hours)

        total_comments = 0
        query_filter = None
        if user:
            query_filter = Q(user=user) & Q(created_at__range=[start_date, end_date])
            if kind == "same":
                query_filter = query_filter & Q(contents=self.contents)

            total_comments = self.__class__.objects.filter(query_filter).count()

        return total_comments

    def validate_comments_all_posts(self):
        if self.count_comments_per_time() >= 15:
            raise Exception("Quantidade total de comentários excedida.")

    def validate_comments_same_post(self):
        if self.count_comments_per_time(kind="same") >= 3:
            raise Exception("Quantidade total de comentários excedida para este post.")

    def validate(self):
        if not self.pk:
            self.validate_comments_all_posts()
            self.validate_comments_same_post()

    def __str__(self):
        return "%s" % self.person_name

    def save(self, *args, **kwargs):
        self.validate()

        user = get_current_user()
        if user:
            self.user = user

        super().save(*args, **kwargs)


class Poll(Content):
    show_partial = BooleanField("Exibir resultado parcial?", default=False)

    def is_finished(self):
        now = datetime.datetime.now()
        static = self.published_date and not self.published
        dynamic = self.publication_end and now > self.publication_end
        return bool(static or dynamic)

    def is_on(self):
        return self.is_published() and not self.is_finished()

    def is_locked(self):
        return self.is_published() or self.is_finished()

    def vote(self, choice):

        if not isinstance(choice, Choice):
            choice = self.choices.filter(active=True, pk=choice).first()

        if not choice:
            raise Exception("Essa alternativa não existe")

        choice.votes += 1
        choice.save()

    def __str__(self):
        return str(self.title)


class Choice(Model):
    choice = CharField("Alternativa", max_length=256)
    active = BooleanField("Ativo", default=True, db_index=True)
    votes = IntegerField("Votos", default=0, db_index=True)

    poll = ForeignKey(
        Poll, verbose_name="Enquete", related_name="choices", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    @property
    def percent(self):
        total = (
            self.poll.choices.filter(active=True)
            .aggregate(total=Sum("votes"))
            .get("total")
            or 0
        )
        return round(((100 * float(self.votes)) / total), 1) if total > 0 else 0

    def __str__(self):
        return str(self.choice)


class MapMarker(Model):
    latitude = FloatField()
    longitude = FloatField()

    @property
    def coordinates(self):
        return (self.latitute, self.longitude)

    def __str__(self):
        return "Coordinates: %s, %s" % (self.latitude, self.longitude)


class Map(Content):
    map_type_id = CharField(max_length=50, default="roadmap")
    zoom = IntegerField(null=True, default=6)
    min_zoom = IntegerField(null=True, default=6)
    max_zoom = IntegerField(null=True)
    zoom_control = BooleanField(default=False)
    draggable = BooleanField(default=False)
    disable_default_ui = BooleanField(default=False)

    center = OneToOneField(
        MapMarker, related_name="centered_map", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    markers = ManyToManyField(MapMarker, related_name="maps")


# Modelos específicos para as atuações do Ministério Público
class CountyMarker(Model):
    marker = OneToOneField(
        MapMarker, null=True, related_name="county_marker", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    county = OneToOneField(
        County, related_name="county_marker", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s | %s, %s" % (
            self.county.nome,
            self.marker.latitude,
            self.marker.longitude,
        )


class ProsecutorActionStatus(Common):
    pass


class ProsecutorAction(Post):
    doc_number = IntegerField(db_index=True)
    start_date = DateField(db_index=True)
    decision_date = DateField(db_index=True, null=True)
    filing = TextField(null=True)

    status = ForeignKey(
        ProsecutorActionStatus, related_name="prosecutor_actions", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    county = ForeignKey(
        County, null=True, related_name="prosecutor_actions", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def clean_title(self):
        replaces = ["Auto", "auto", "Nº", "nº", "N º", "n º"]
        for r in replaces:
            self.title = self.title.replace(r, "")
        return self.title

    def get_number(self):
        return int("".join(re.findall(r"\d", self.title)))

    def save(self, *args, **kwargs):
        self.title = "Auto nº %s" % self.clean_title()
        self.doc_number = self.get_number()
        super(ProsecutorAction, self).save(*args, **kwargs)
