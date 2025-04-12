# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Area'
        db.create_table(
            "web_area",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "parent",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="children", null=True, to=orm["web.Area"]
                    ),
                ),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=128, null=True, db_index=True
                    ),
                ),
                (
                    "fullname",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=256, null=True, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
                (
                    "as_link",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Area"])

        # Adding model 'WebGroup'
        db.create_table(
            "web_webgroup",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "area",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="groups", to=orm["web.Area"]
                    ),
                ),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=128, null=True, db_index=True
                    ),
                ),
                (
                    "can_add",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "can_change",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "can_delete",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "can_publish",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["WebGroup"])

        # Adding M2M table for field users on 'WebGroup'
        db.create_table(
            "web_webgroup_users",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("webgroup", models.ForeignKey(orm["web.webgroup"], null=False)),
                ("user", models.ForeignKey(orm["auth.user"], null=False)),
            ),
        )
        db.create_unique("web_webgroup_users", ["webgroup_id", "user_id"])

        # Adding model 'Content'
        db.create_table(
            "web_content",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "title",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                ("abstract", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=256, unique=True, null=True, db_index=True
                    ),
                ),
                (
                    "credits",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "create_date",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, db_index=True, blank=True
                    ),
                ),
                (
                    "published",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "published_date",
                    self.gf("django.db.models.fields.DateTimeField")(
                        null=True, db_index=True
                    ),
                ),
                (
                    "publication_start",
                    self.gf("django.db.models.fields.DateTimeField")(
                        null=True, db_index=True
                    ),
                ),
                (
                    "publication_end",
                    self.gf("django.db.models.fields.DateTimeField")(
                        null=True, db_index=True
                    ),
                ),
                (
                    "highlight",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
                (
                    "position",
                    self.gf("django.db.models.fields.IntegerField")(
                        default=9999, db_index=True
                    ),
                ),
                (
                    "has_comment",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_tag",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_meta",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Content"])

        # Adding model 'Post'
        db.create_table(
            "web_post",
            (
                (
                    "content_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Content"], unique=True, primary_key=True
                    ),
                ),
                (
                    "post",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="posts", null=True, to=orm["web.Post"]
                    ),
                ),
                ("text", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "has_link",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_file",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_image",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_audio",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "has_video",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Post"])

        # Adding model 'Multimedia'
        db.create_table(
            "web_multimedia",
            (
                (
                    "content_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Content"], unique=True, primary_key=True
                    ),
                ),
                ("url_embed", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "ged",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["ged.Arquivo"], null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Multimedia"])

        # Adding model 'Link'
        db.create_table(
            "web_link",
            (
                (
                    "multimedia_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Multimedia"], unique=True, primary_key=True
                    ),
                ),
                (
                    "is_banner",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "parent",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="children", null=True, to=orm["web.Link"]
                    ),
                ),
                (
                    "fullname",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "external",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Link"])

        # Adding model 'Image'
        db.create_table(
            "web_image",
            (
                (
                    "multimedia_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Multimedia"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Image"])

        # Adding M2M table for field posts on 'Image'
        db.create_table(
            "web_image_posts",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("image", models.ForeignKey(orm["web.image"], null=False)),
                ("post", models.ForeignKey(orm["web.post"], null=False)),
            ),
        )
        db.create_unique("web_image_posts", ["image_id", "post_id"])

        # Adding model 'Video'
        db.create_table(
            "web_video",
            (
                (
                    "multimedia_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Multimedia"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Video"])

        # Adding M2M table for field posts on 'Video'
        db.create_table(
            "web_video_posts",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("video", models.ForeignKey(orm["web.video"], null=False)),
                ("post", models.ForeignKey(orm["web.post"], null=False)),
            ),
        )
        db.create_unique("web_video_posts", ["video_id", "post_id"])

        # Adding model 'Audio'
        db.create_table(
            "web_audio",
            (
                (
                    "multimedia_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Multimedia"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Audio"])

        # Adding M2M table for field posts on 'Audio'
        db.create_table(
            "web_audio_posts",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("audio", models.ForeignKey(orm["web.audio"], null=False)),
                ("post", models.ForeignKey(orm["web.post"], null=False)),
            ),
        )
        db.create_unique("web_audio_posts", ["audio_id", "post_id"])

        # Adding model 'File'
        db.create_table(
            "web_file",
            (
                (
                    "multimedia_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["web.Multimedia"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["File"])

        # Adding M2M table for field posts on 'File'
        db.create_table(
            "web_file_posts",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("file", models.ForeignKey(orm["web.file"], null=False)),
                ("post", models.ForeignKey(orm["web.post"], null=False)),
            ),
        )
        db.create_unique("web_file_posts", ["file_id", "post_id"])

        # Adding model 'ContentArea'
        db.create_table(
            "web_contentarea",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "area",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="content_area", to=orm["web.Area"]
                    ),
                ),
                (
                    "content",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="content_area", to=orm["web.Content"]
                    ),
                ),
                (
                    "original",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["ContentArea"])

        # Adding model 'Action'
        db.create_table(
            "web_action",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "content",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="action", to=orm["web.Content"]
                    ),
                ),
                (
                    "user",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="actions", to=orm["auth.User"]
                    ),
                ),
                (
                    "act",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Action"])

        # Adding model 'Pendency'
        db.create_table(
            "web_pendency",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "description",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=384, null=True
                    ),
                ),
                (
                    "create_date",
                    self.gf("django.db.models.fields.DateTimeField")(db_index=True),
                ),
                (
                    "resolved_date",
                    self.gf("django.db.models.fields.DateTimeField")(
                        null=True, db_index=True
                    ),
                ),
                (
                    "resolved",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "action",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="pendencies", null=True, to=orm["web.Action"]
                    ),
                ),
                (
                    "reviser",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="pendencies", null=True, to=orm["auth.User"]
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Pendency"])

        # Adding model 'Tag'
        db.create_table(
            "web_tag",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=128, null=True
                    ),
                ),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=384, null=True, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Tag"])

        # Adding M2M table for field contents on 'Tag'
        db.create_table(
            "web_tag_contents",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("tag", models.ForeignKey(orm["web.tag"], null=False)),
                ("content", models.ForeignKey(orm["web.content"], null=False)),
            ),
        )
        db.create_unique("web_tag_contents", ["tag_id", "content_id"])

        # Adding model 'MetaKey'
        db.create_table(
            "web_metakey",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "key",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=128, unique=True, null=True, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["MetaKey"])

        # Adding M2M table for field contents on 'MetaKey'
        db.create_table(
            "web_metakey_contents",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("metakey", models.ForeignKey(orm["web.metakey"], null=False)),
                ("content", models.ForeignKey(orm["web.content"], null=False)),
            ),
        )
        db.create_unique("web_metakey_contents", ["metakey_id", "content_id"])

        # Adding model 'MetaValue'
        db.create_table(
            "web_metavalue",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "value",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=384, unique=True, null=True, db_index=True
                    ),
                ),
                (
                    "key",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="meta_values", to=orm["web.MetaKey"]
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["MetaValue"])

        # Adding model 'Category'
        db.create_table(
            "web_category",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=128, null=True
                    ),
                ),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=384, null=True, db_index=True
                    ),
                ),
                (
                    "create_date",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, db_index=True, blank=True
                    ),
                ),
                (
                    "area",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="categories", null=True, to=orm["web.Area"]
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Category"])

        # Adding M2M table for field contents on 'Category'
        db.create_table(
            "web_category_contents",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("category", models.ForeignKey(orm["web.category"], null=False)),
                ("content", models.ForeignKey(orm["web.content"], null=False)),
            ),
        )
        db.create_unique("web_category_contents", ["category_id", "content_id"])

        # Adding model 'Comment'
        db.create_table(
            "web_comment",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "person_name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "person_email",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                ("text", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "contents",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="comments", to=orm["web.Content"]
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Comment"])

        # Adding model 'Poll'
        db.create_table(
            "web_poll",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "description",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=384, null=True, db_index=True
                    ),
                ),
                (
                    "create_date",
                    self.gf("django.db.models.fields.DateTimeField")(db_index=True),
                ),
                (
                    "votes",
                    self.gf("django.db.models.fields.IntegerField")(
                        default=0, db_index=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Poll"])

        # Adding model 'Choice'
        db.create_table(
            "web_choice",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "question",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=256, null=True
                    ),
                ),
                (
                    "poll",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="choices", to=orm["web.Poll"]
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=True, db_index=True
                    ),
                ),
            ),
        )
        db.send_create_signal("web", ["Choice"])

    def backwards(self, orm):

        # Deleting model 'Area'
        db.delete_table("web_area")

        # Deleting model 'WebGroup'
        db.delete_table("web_webgroup")

        # Removing M2M table for field users on 'WebGroup'
        db.delete_table("web_webgroup_users")

        # Deleting model 'Content'
        db.delete_table("web_content")

        # Deleting model 'Post'
        db.delete_table("web_post")

        # Deleting model 'Multimedia'
        db.delete_table("web_multimedia")

        # Deleting model 'Link'
        db.delete_table("web_link")

        # Deleting model 'Image'
        db.delete_table("web_image")

        # Removing M2M table for field posts on 'Image'
        db.delete_table("web_image_posts")

        # Deleting model 'Video'
        db.delete_table("web_video")

        # Removing M2M table for field posts on 'Video'
        db.delete_table("web_video_posts")

        # Deleting model 'Audio'
        db.delete_table("web_audio")

        # Removing M2M table for field posts on 'Audio'
        db.delete_table("web_audio_posts")

        # Deleting model 'File'
        db.delete_table("web_file")

        # Removing M2M table for field posts on 'File'
        db.delete_table("web_file_posts")

        # Deleting model 'ContentArea'
        db.delete_table("web_contentarea")

        # Deleting model 'Action'
        db.delete_table("web_action")

        # Deleting model 'Pendency'
        db.delete_table("web_pendency")

        # Deleting model 'Tag'
        db.delete_table("web_tag")

        # Removing M2M table for field contents on 'Tag'
        db.delete_table("web_tag_contents")

        # Deleting model 'MetaKey'
        db.delete_table("web_metakey")

        # Removing M2M table for field contents on 'MetaKey'
        db.delete_table("web_metakey_contents")

        # Deleting model 'MetaValue'
        db.delete_table("web_metavalue")

        # Deleting model 'Category'
        db.delete_table("web_category")

        # Removing M2M table for field contents on 'Category'
        db.delete_table("web_category_contents")

        # Deleting model 'Comment'
        db.delete_table("web_comment")

        # Deleting model 'Poll'
        db.delete_table("web_poll")

        # Deleting model 'Choice'
        db.delete_table("web_choice")

    models = {
        "auth.group": {
            "Meta": {"object_name": "Group"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "unique": "True", "null": "True"},
            ),
            "permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Permission']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "auth.permission": {
            "Meta": {
                "ordering": "('content_type__app_label', 'content_type__model', 'codename')",
                "unique_together": "(('content_type', 'codename'),)",
                "object_name": "Permission",
            },
            "codename": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
        },
        "auth.user": {
            "Meta": {"object_name": "User"},
            "date_joined": (
                "django.db.models.fields.DateTimeField",
                [],
                {"default": "datetime.datetime.now"},
            ),
            "email": (
                "django.db.models.fields.EmailField",
                [],
                {"max_length": "75", "null": "True", "blank": "True"},
            ),
            "first_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True", "blank": "True"},
            ),
            "groups": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Group']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "is_active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "is_staff": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "is_superuser": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "last_login": (
                "django.db.models.fields.DateTimeField",
                [],
                {"default": "datetime.datetime.now"},
            ),
            "last_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True", "blank": "True"},
            ),
            "password": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True"},
            ),
            "user_permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Permission']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "username": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "unique": "True", "null": "True"},
            ),
        },
        "contenttypes.contenttype": {
            "Meta": {
                "ordering": "('name',)",
                "unique_together": "(('app_label', 'model'),)",
                "object_name": "ContentType",
                "db_table": "'django_content_type'",
            },
            "app_label": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "model": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "gecap.areaconhecimento": {
            "Meta": {
                "ordering": "['codigo_cnpq', 'titulo']",
                "object_name": "AreaConhecimento",
            },
            "cache_codigo_cnpq": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "codigo_cnpq": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "sub_area_de": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'sub_areas'",
                    "null": "True",
                    "to": "orm['gecap.AreaConhecimento']",
                },
            ),
            "titulo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
        },
        "ged.arquivo": {
            "Meta": {
                "unique_together": "(('file', 'user'),)",
                "object_name": "Arquivo",
            },
            "acesso": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "copia_de": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "created": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "file": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "32", "null": "True"},
            ),
            "filename": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "260", "null": "True", "blank": "True"},
            ),
            "group": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Lotacao']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mimetype": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['auth.User']"},
            ),
        },
        "notification.message": {
            "Meta": {"object_name": "Message", "db_table": "'eng_message'"},
            "default_params": (
                "django.db.models.fields.CharField",
                [],
                {
                    "default": "'{}'",
                    "max_length": "400",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "header": (
                "django.db.models.fields.CharField",
                [],
                {"default": "''", "max_length": "30", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "message": ("django.db.models.fields.TextField", [], {"null": "True"}),
            "mid": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "unique": "True", "null": "True", "blank": "True"},
            ),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'INFO'", "max_length": "10", "null": "True"},
            ),
        },
        "notification.notification": {
            "Meta": {"object_name": "Notification", "db_table": "'eng_notification'"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "msg": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'notifications'",
                    "to": "orm['notification.Message']",
                },
            ),
            "params": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "400", "null": "True"},
            ),
            "sender_ct": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'notifications_send'",
                    "null": "True",
                    "to": "orm['contenttypes.ContentType']",
                },
            ),
            "sender_id": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "status": (
                "django.db.models.fields.PositiveSmallIntegerField",
                [],
                {"default": "2"},
            ),
            "target_ct": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'notifications_receive'",
                    "to": "orm['contenttypes.ContentType']",
                },
            ),
            "target_id": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'SYS'", "max_length": "10", "null": "True"},
            ),
        },
        "rh.banco": {
            "Meta": {"ordering": "['nome']", "object_name": "Banco"},
            "agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "dv_agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True", "blank": "True"},
            ),
            "dv_conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True"},
            ),
            "numero_convenio": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
            "tem_convenio": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "rh.capacidade": {
            "Meta": {"object_name": "Capacidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.circunscricao": {
            "Meta": {"object_name": "Circunscricao"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.comarca": {
            "Meta": {"object_name": "Comarca"},
            "circunscricao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Circunscricao']", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "grupo_comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.GrupoComarca']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "validacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
        },
        "rh.curso": {
            "Meta": {"object_name": "Curso"},
            "area_conhecimento": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['gecap.AreaConhecimento']", "null": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.dadobancario": {
            "Meta": {"ordering": "['banco']", "object_name": "DadoBancario"},
            "agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "banco": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Banco']"},
            ),
            "conta_corrente_completa": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "tipo_conta": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.docsdadosespecificos": {
            "Meta": {"object_name": "DocsDadosEspecificos"},
            "especificidade": ("django.db.models.fields.IntegerField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "valor": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True"},
            ),
        },
        "rh.documento": {
            "Meta": {"object_name": "Documento"},
            "arquivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "dados_especificos": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.DocsDadosEspecificos']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "data_expedicao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_validade": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "estado_expedicao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True"},
            ),
            "tipo_documento": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.endereco": {
            "Meta": {"object_name": "Endereco"},
            "bairro": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "cep": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True"},
            ),
            "complemento": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "logradouro": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "municipio": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']", "null": "True"},
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "tipo_endereco": ("django.db.models.fields.IntegerField", [], {}),
            "tipo_logradouro": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.entrancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Entrancia"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.estado": {
            "Meta": {"ordering": "['nome']", "object_name": "Estado"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "ibge": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "pais": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Pais']"},
            ),
            "siafi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True"},
            ),
            "tse": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
        },
        "rh.grupocomarca": {
            "Meta": {"object_name": "GrupoComarca"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.incapacidade": {
            "Meta": {"object_name": "InCapacidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.instancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Instancia"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.localidade": {
            "Meta": {"object_name": "Localidade"},
            "cep": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "9", "null": "True", "blank": "True"},
            ),
            "comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Comarca']", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "distancia_capital": (
                "django.db.models.fields.DecimalField",
                [],
                {
                    "null": "True",
                    "max_digits": "6",
                    "decimal_places": "2",
                    "blank": "True",
                },
            ),
            "estado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']"},
            ),
            "ibge": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicador_municipio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "microregiao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.MicroRegiao']", "null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "sede_termo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "siafi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
        },
        "rh.lotacao": {
            "Meta": {
                "ordering": "['nome']",
                "object_name": "Lotacao",
                "_ormbases": ["rh.OrgaoGeral"],
            },
            "acesso_protocolo_geral": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "administrativo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "andar": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True", "blank": "True"},
            ),
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True", "blank": "True"},
            ),
            "comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Comarca']", "null": "True", "blank": "True"},
            ),
            "entrancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Entrancia']", "null": "True", "blank": "True"},
            ),
            "executivo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "grupo": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Lotacao']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "grupo_lotacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "localidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']"},
            ),
            "orgaogeral_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.OrgaoGeral']", "unique": "True", "primary_key": "True"},
            ),
            "pai": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'lotacoes_subordinadas'",
                    "null": "True",
                    "to": "orm['rh.Lotacao']",
                },
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'responsavel_por'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "sala": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
            "telefone": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Telefone']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "rh.mesoregiao": {
            "Meta": {"object_name": "MesoRegiao"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.microregiao": {
            "Meta": {"object_name": "MicroRegiao"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "meso_regiao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.MesoRegiao']"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.orgaogeral": {
            "Meta": {"ordering": "['nome']", "object_name": "OrgaoGeral"},
            "abreviacao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True", "blank": "True"},
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "esfera_governamental": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "poder": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "8", "null": "True", "blank": "True"},
            ),
        },
        "rh.pais": {
            "Meta": {"ordering": "['nome']", "object_name": "Pais"},
            "ddi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nacionalidade": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "nome_completo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
        },
        "rh.pessoa": {
            "Meta": {"ordering": "('nome',)", "object_name": "Pessoa"},
            "dado_bancario": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.DadoBancario']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "endereco": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Endereco']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "telefone": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Telefone']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "rh.pessoafisica": {
            "Meta": {
                "ordering": "('nome', 'cpf')",
                "object_name": "PessoaFisica",
                "_ormbases": ["rh.Pessoa"],
            },
            "cpf": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "14", "null": "True", "blank": "True"},
            ),
            "data_cadastro": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "null": "True", "blank": "True"},
            ),
            "data_nascimento": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_obito": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "doador": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "documento": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Documento']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "email_pessoal": (
                "django.db.models.fields.EmailField",
                [],
                {"max_length": "75", "null": "True", "blank": "True"},
            ),
            "estado_civil": ("django.db.models.fields.IntegerField", [], {}),
            "fator_rh": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "foto": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "municipio_naturalidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']", "null": "True", "blank": "True"},
            ),
            "nome_conjuge": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "nome_mae": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "nome_pai": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "pessoa_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.Pessoa']", "unique": "True", "primary_key": "True"},
            ),
            "raca_cor": ("django.db.models.fields.IntegerField", [], {}),
            "rg": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "rg_data_expedicao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "rg_orgao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "rg_uf": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']", "null": "True", "blank": "True"},
            ),
            "sangue": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "sexo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "1", "null": "True", "blank": "True"},
            ),
        },
        "rh.servidor": {
            "Meta": {
                "ordering": "('pessoa_fisica__nome', 'pessoa_fisica__cpf', 'matricula')",
                "object_name": "Servidor",
            },
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "capacidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Capacidade']", "null": "True", "blank": "True"},
            ),
            "classificacao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "curso": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Curso']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "data_referencia_ferias": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_registro": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now_add": "True", "null": "True", "blank": "True"},
            ),
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "incapacidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.InCapacidade']", "null": "True", "blank": "True"},
            ),
            "matricula": (
                "django.db.models.fields.IntegerField",
                [],
                {"unique": "True"},
            ),
            "matricula_origem": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "numero_cartao_ponto": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "pessoa_fisica": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.PessoaFisica']"},
            ),
            "servidor_tipo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.TipoServidor']"},
            ),
            "situacao_servidor": ("django.db.models.fields.IntegerField", [], {}),
            "tipo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'S'", "max_length": "1", "null": "True", "blank": "True"},
            ),
            "tipo_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.TipoOrigem']", "null": "True", "blank": "True"},
            ),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'servidor'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
            "vpi": (
                "django.db.models.fields.DecimalField",
                [],
                {
                    "null": "True",
                    "max_digits": "18",
                    "decimal_places": "12",
                    "blank": "True",
                },
            ),
        },
        "rh.telefone": {
            "Meta": {"object_name": "Telefone"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "publico": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "tipo_telefone": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.tipoorigem": {
            "Meta": {"object_name": "TipoOrigem"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.tiposervidor": {
            "Meta": {"ordering": "['nome']", "object_name": "TipoServidor"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "entrancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Entrancia']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicativo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "1", "null": "True"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "web.action": {
            "Meta": {"object_name": "Action"},
            "act": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "content": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'action'", "to": "orm['web.Content']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'actions'", "to": "orm['auth.User']"},
            ),
        },
        "web.area": {
            "Meta": {"object_name": "Area"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "as_link": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "fullname": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True", "db_index": "True"},
            ),
            "parent": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'children'", "null": "True", "to": "orm['web.Area']"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "256", "null": "True", "db_index": "True"},
            ),
        },
        "web.audio": {
            "Meta": {"object_name": "Audio", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'audios'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.category": {
            "Meta": {"object_name": "Category"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "area": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'categories'",
                    "null": "True",
                    "to": "orm['web.Area']",
                },
            ),
            "contents": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'categories'",
                    "null": "True",
                    "to": "orm['web.Content']",
                },
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "db_index": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "384", "null": "True", "db_index": "True"},
            ),
        },
        "web.choice": {
            "Meta": {"object_name": "Choice"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "poll": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'choices'", "to": "orm['web.Poll']"},
            ),
            "question": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
        },
        "web.comment": {
            "Meta": {"object_name": "Comment"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'comments'", "to": "orm['web.Content']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "person_email": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "person_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "text": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.content": {
            "Meta": {"object_name": "Content"},
            "abstract": ("django.db.models.fields.TextField", [], {"null": "True"}),
            "actions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'contents'",
                    "null": "True",
                    "through": "orm['web.Action']",
                    "to": "orm['auth.User']",
                },
            ),
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "areas": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'contents'",
                    "null": "True",
                    "through": "orm['web.ContentArea']",
                    "to": "orm['web.Area']",
                },
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "db_index": "True", "blank": "True"},
            ),
            "credits": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "has_comment": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_meta": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_tag": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "highlight": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "position": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "9999", "db_index": "True"},
            ),
            "publication_end": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "publication_start": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "published": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "published_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {
                    "max_length": "256",
                    "unique": "True",
                    "null": "True",
                    "db_index": "True",
                },
            ),
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
        },
        "web.contentarea": {
            "Meta": {"object_name": "ContentArea"},
            "area": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'content_area'", "to": "orm['web.Area']"},
            ),
            "content": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'content_area'", "to": "orm['web.Content']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "original": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
        },
        "web.file": {
            "Meta": {"object_name": "File", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'files'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.image": {
            "Meta": {"object_name": "Image", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'images'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.link": {
            "Meta": {"object_name": "Link", "_ormbases": ["web.Multimedia"]},
            "external": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "fullname": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "is_banner": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "parent": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'children'", "null": "True", "to": "orm['web.Link']"},
            ),
        },
        "web.metakey": {
            "Meta": {"object_name": "MetaKey"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'metadatas'",
                    "null": "True",
                    "to": "orm['web.Content']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "key": (
                "django.db.models.fields.CharField",
                [],
                {
                    "max_length": "128",
                    "unique": "True",
                    "null": "True",
                    "db_index": "True",
                },
            ),
        },
        "web.metavalue": {
            "Meta": {"object_name": "MetaValue"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "key": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'meta_values'", "to": "orm['web.MetaKey']"},
            ),
            "value": (
                "django.db.models.fields.CharField",
                [],
                {
                    "max_length": "384",
                    "unique": "True",
                    "null": "True",
                    "db_index": "True",
                },
            ),
        },
        "web.multimedia": {
            "Meta": {"object_name": "Multimedia", "_ormbases": ["web.Content"]},
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "ged": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True"},
            ),
            "url_embed": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.pendency": {
            "Meta": {"object_name": "Pendency"},
            "action": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'pendencies'",
                    "null": "True",
                    "to": "orm['web.Action']",
                },
            ),
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"db_index": "True"},
            ),
            "description": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "384", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "resolved": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "resolved_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "reviser": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'pendencies'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "web.poll": {
            "Meta": {"object_name": "Poll"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"db_index": "True"},
            ),
            "description": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "384", "null": "True", "db_index": "True"},
            ),
            "votes": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "0", "db_index": "True"},
            ),
        },
        "web.post": {
            "Meta": {"object_name": "Post", "_ormbases": ["web.Content"]},
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "has_audio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_file": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_image": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_link": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_video": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "post": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'posts'", "null": "True", "to": "orm['web.Post']"},
            ),
            "text": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.tag": {
            "Meta": {"object_name": "Tag"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'tags'",
                    "null": "True",
                    "to": "orm['web.Content']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "384", "null": "True", "db_index": "True"},
            ),
        },
        "web.video": {
            "Meta": {"object_name": "Video", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'videos'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.webgroup": {
            "Meta": {"object_name": "WebGroup"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "area": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'groups'", "to": "orm['web.Area']"},
            ),
            "can_add": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_change": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_delete": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_publish": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True", "db_index": "True"},
            ),
            "users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'web_groups'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
    }

    complete_apps = ["web"]
