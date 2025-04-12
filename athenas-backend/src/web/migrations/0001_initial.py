# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ged", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Area",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128, verbose_name="Nome", db_index=True
                    ),
                ),
                (
                    "fullname",
                    models.CharField(max_length=256, verbose_name="Nome completo"),
                ),
                ("slug", models.SlugField(max_length=256, verbose_name="Slug")),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "as_link",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Como link"
                    ),
                ),
                (
                    "can_share",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Pode compartilhar"
                    ),
                ),
                (
                    "kind_of_content",
                    models.CharField(
                        default="area",
                        max_length=100,
                        verbose_name="Tipo de conte\xc3\xbado",
                        choices=[
                            ("area", "Area"),
                            ("link", "Link"),
                            ("post", "Post"),
                            ("pgj-actions", "PGJ Actions"),
                        ],
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "choice",
                    models.CharField(max_length=256, verbose_name="Alternativa"),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "votes",
                    models.IntegerField(default=0, verbose_name="Votos", db_index=True),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("person_name", models.CharField(max_length=256, verbose_name="Nome")),
                (
                    "person_email",
                    models.CharField(max_length=256, null=True, verbose_name="Email"),
                ),
                ("text", models.TextField(verbose_name="Coment\xc3\xa1rio")),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Common",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(max_length=150)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Content",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=256, verbose_name="Post")),
                ("slug", models.SlugField(max_length=256, verbose_name="Slug")),
                (
                    "credits",
                    models.CharField(
                        max_length=256,
                        null=True,
                        verbose_name="Cr\xc3\xa9ditos",
                        blank=True,
                    ),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Data de cria\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Publicado"
                    ),
                ),
                (
                    "published_date",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Data de publica\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "publication_start",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Inicio da publica\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "publication_end",
                    models.DateTimeField(
                        null=True,
                        verbose_name="Fim da publica\xc3\xa7\xc3\xa3o",
                        db_index=True,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "position",
                    models.IntegerField(
                        default=9999, verbose_name="Ordem", db_index=True
                    ),
                ),
                (
                    "has_comment",
                    models.BooleanField(
                        default=False,
                        db_index=True,
                        verbose_name="Tem coment\xc3\xa1rio",
                    ),
                ),
                (
                    "has_tag",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem tag"
                    ),
                ),
                (
                    "has_meta",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem metadados"
                    ),
                ),
                (
                    "as_link",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Como link?"
                    ),
                ),
                (
                    "as_gallery",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Como galeria?"
                    ),
                ),
                (
                    "views",
                    models.IntegerField(
                        default=0,
                        verbose_name="Visualiza\xc3\xa7\xc3\xb5es",
                        db_index=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ContentArea",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "original",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Original"
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        related_name="content_area",
                        verbose_name="\xc3\x81rea",
                        to="web.Area",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="CountyMarker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "county",
                    models.OneToOneField(
                        related_name="county_marker",
                        to="rh.Comarca",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Map",
            fields=[
                (
                    "content_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Content",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("map_type_id", models.CharField(default="roadmap", max_length=50)),
                ("zoom", models.IntegerField(default=6, null=True)),
                ("min_zoom", models.IntegerField(default=6, null=True)),
                ("max_zoom", models.IntegerField(null=True)),
                ("zoom_control", models.BooleanField(default=False)),
                ("draggable", models.BooleanField(default=False)),
                ("disable_default_ui", models.BooleanField(default=False)),
            ],
            options={},
            bases=("web.content",),
        ),
        migrations.CreateModel(
            name="MapMarker",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MetaKey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        unique=True, max_length=128, verbose_name="Chave", db_index=True
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MetaValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "value",
                    models.CharField(
                        unique=True, max_length=384, verbose_name="Valor", db_index=True
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "key",
                    models.ForeignKey(
                        related_name="meta_values",
                        verbose_name="Chave",
                        to="web.MetaKey",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Module",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.common",),
        ),
        migrations.CreateModel(
            name="Multimedia",
            fields=[
                (
                    "content_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Content",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "url_embed",
                    models.CharField(default="#", max_length=400, db_index=True),
                ),
            ],
            options={},
            bases=("web.content",),
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                (
                    "multimedia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Multimedia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "is_banner",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="\xc3\x89 banner"
                    ),
                ),
                (
                    "fullname",
                    models.CharField(max_length=256, verbose_name="Nome completo"),
                ),
                (
                    "kind",
                    models.IntegerField(
                        default=1,
                        db_index=True,
                        verbose_name="Tipo de Link",
                        choices=[
                            (0, "Super"),
                            (1, "Externo"),
                            (2, "Para \xc3\x81rea"),
                            (3, "Para Post"),
                            (4, "Para Galeria"),
                        ],
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        related_name="children",
                        to="web.Link",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.multimedia",),
        ),
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "multimedia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Multimedia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.multimedia",),
        ),
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "multimedia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Multimedia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.multimedia",),
        ),
        migrations.CreateModel(
            name="Audio",
            fields=[
                (
                    "multimedia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Multimedia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.multimedia",),
        ),
        migrations.CreateModel(
            name="PasswordChangeRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("key", models.CharField(max_length=64, db_index=True)),
                ("valid", models.BooleanField(default=True, db_index=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Poll",
            fields=[
                (
                    "content_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Content",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "restricted",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Enquete restrita?"
                    ),
                ),
                (
                    "show_partial",
                    models.BooleanField(
                        default=False, verbose_name="Exibir resultado parcial?"
                    ),
                ),
                (
                    "users_who_voted",
                    models.ManyToManyField(
                        related_name="polls_voted", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={},
            bases=("web.content",),
        ),
        migrations.CreateModel(
            name="PollConditions",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("expression", models.CharField(max_length=256)),
                ("value", models.CharField(max_length=256, null=True)),
                ("description", models.CharField(max_length=256)),
                (
                    "polls",
                    models.ManyToManyField(related_name="conditions", to="web.Poll"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "content_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Content",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("text", models.TextField(null=True, verbose_name="Texto")),
                (
                    "shared",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Compartilhado?"
                    ),
                ),
                (
                    "has_link",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem link?"
                    ),
                ),
                (
                    "has_file",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem arquivo?"
                    ),
                ),
                (
                    "has_image",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem imagem?"
                    ),
                ),
                (
                    "has_audio",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem audio?"
                    ),
                ),
                (
                    "has_video",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Tem v\xc3\xaddeo?"
                    ),
                ),
                (
                    "is_index",
                    models.BooleanField(
                        default=False,
                        db_index=True,
                        verbose_name="P\xc3\xa1gina Principal?",
                    ),
                ),
            ],
            options={},
            bases=("web.content",),
        ),
        migrations.CreateModel(
            name="ProsecutorAction",
            fields=[
                (
                    "post_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Post",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("doc_number", models.IntegerField(db_index=True)),
                ("start_date", models.DateField(db_index=True)),
                ("decision_date", models.DateField(null=True, db_index=True)),
                ("filing", models.TextField(null=True)),
                (
                    "county",
                    models.ForeignKey(
                        related_name="prosecutor_actions",
                        to="rh.Comarca",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.post",),
        ),
        migrations.CreateModel(
            name="ProsecutorActionStatus",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.common",),
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=128, verbose_name="Nome")),
                ("slug", models.SlugField(max_length=384, verbose_name="Slug")),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "contents",
                    models.ManyToManyField(
                        related_name="tags", verbose_name="Contents", to="web.Content"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "multimedia_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.Multimedia",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "posts",
                    models.ManyToManyField(
                        related_name="videos", verbose_name="Posts", to="web.Post"
                    ),
                ),
            ],
            options={},
            bases=("web.multimedia",),
        ),
        migrations.CreateModel(
            name="WebGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=128, verbose_name="Nome", db_index=True
                    ),
                ),
                (
                    "can_add",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Pode Criar"
                    ),
                ),
                (
                    "can_change",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Pode Alterar"
                    ),
                ),
                (
                    "can_delete",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Pode Deletar"
                    ),
                ),
                (
                    "can_publish",
                    models.BooleanField(
                        default=False, db_index=True, verbose_name="Pode Publicar"
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, db_index=True, verbose_name="Ativo"
                    ),
                ),
                (
                    "area",
                    models.ForeignKey(
                        related_name="groups", to="web.Area", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "users",
                    models.ManyToManyField(
                        related_name="web_groups", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="WebUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TokenWebUser",
            fields=[
                (
                    "webuser_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.WebUser",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("token", models.CharField(max_length=150, db_index=True)),
            ],
            options={},
            bases=("web.webuser",),
        ),
        migrations.CreateModel(
            name="RegularWebUser",
            fields=[
                (
                    "webuser_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="web.WebUser",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("username", models.CharField(max_length=100, db_index=True)),
                ("password", models.CharField(max_length=128, db_index=True)),
                ("salt", models.CharField(default="%$&@", max_length=10)),
                ("email", models.EmailField(max_length=75, null=True)),
                (
                    "person",
                    models.OneToOneField(
                        related_name="web_user",
                        to="rh.Pessoa",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("web.webuser",),
        ),
        migrations.AddField(
            model_name="prosecutoraction",
            name="status",
            field=models.ForeignKey(
                related_name="prosecutor_actions",
                to="web.ProsecutorActionStatus",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="post",
            name="post",
            field=models.ForeignKey(
                related_name="posts",
                verbose_name="Subitens",
                to="web.Post",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="passwordchangerequest",
            name="user",
            field=models.ForeignKey(
                related_name="password_change_requests",
                to="web.RegularWebUser",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="multimedia",
            name="ged",
            field=models.ForeignKey(
                verbose_name="Arquivo",
                to="ged.Arquivo",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="metakey",
            name="contents",
            field=models.ManyToManyField(
                related_name="metadata", verbose_name="Posts", to="web.Content"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="map",
            name="center",
            field=models.OneToOneField(
                related_name="centered_map",
                to="web.MapMarker",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="map",
            name="markers",
            field=models.ManyToManyField(related_name="maps", to="web.MapMarker"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="image",
            name="posts",
            field=models.ManyToManyField(
                related_name="images", verbose_name="Posts", to="web.Post"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="file",
            name="posts",
            field=models.ManyToManyField(
                related_name="files", verbose_name="Posts", to="web.Post"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="countymarker",
            name="marker",
            field=models.OneToOneField(
                related_name="county_marker",
                null=True,
                to="web.MapMarker",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contentarea",
            name="content",
            field=models.ForeignKey(
                related_name="content_area",
                verbose_name="Post",
                to="web.Content",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="content",
            name="areas",
            field=models.ManyToManyField(
                related_name="contents",
                verbose_name="\xc3\x81reas",
                through="web.ContentArea",
                to="web.Area",
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="content",
            unique_together=set([("slug", "create_date")]),
        ),
        migrations.AddField(
            model_name="comment",
            name="contents",
            field=models.ForeignKey(
                related_name="comments",
                verbose_name="Post",
                to="web.Content",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="choice",
            name="poll",
            field=models.ForeignKey(
                related_name="choices",
                verbose_name="Enquete",
                to="web.Poll",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="audio",
            name="posts",
            field=models.ManyToManyField(
                related_name="audios", verbose_name="Posts", to="web.Post"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="area",
            name="modules",
            field=models.ManyToManyField(related_name="sites", to="web.Module"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="area",
            name="parent",
            field=models.ForeignKey(
                related_name="children",
                verbose_name="Subitens",
                to="web.Area",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
    ]
