# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PollConditions'
        db.create_table(
            "poll_pollconditions",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "expression",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
                (
                    "value",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
                (
                    "description",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("poll", ["PollConditions"])

        # Adding model 'Poll'
        db.create_table(
            "poll_poll",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "title",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
                (
                    "max_of_choices",
                    self.gf("django.db.models.fields.IntegerField")(
                        default=1, db_index=True
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
                    "create_date",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, db_index=True, blank=True
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
        db.send_create_signal("poll", ["Poll"])

        # Adding M2M table for field users_who_voted on 'Poll'
        db.create_table(
            "poll_poll_users_who_voted",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("poll", models.ForeignKey(orm["poll.poll"], null=False)),
                ("user", models.ForeignKey(orm["auth.user"], null=False)),
            ),
        )
        db.create_unique("poll_poll_users_who_voted", ["poll_id", "user_id"])

        # Adding M2M table for field conditions on 'Poll'
        db.create_table(
            "poll_poll_conditions",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("poll", models.ForeignKey(orm["poll.poll"], null=False)),
                (
                    "pollconditions",
                    models.ForeignKey(orm["poll.pollconditions"], null=False),
                ),
            ),
        )
        db.create_unique("poll_poll_conditions", ["poll_id", "pollconditions_id"])

        # Adding model 'BlackList'
        db.create_table(
            "poll_blacklist",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "poll",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        related_name="blacklist",
                        unique=True,
                        null=True,
                        to=orm["poll.Poll"],
                    ),
                ),
            ),
        )
        db.send_create_signal("poll", ["BlackList"])

        # Adding M2M table for field blocked_users on 'BlackList'
        db.create_table(
            "poll_blacklist_blocked_users",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("blacklist", models.ForeignKey(orm["poll.blacklist"], null=False)),
                ("user", models.ForeignKey(orm["auth.user"], null=False)),
            ),
        )
        db.create_unique("poll_blacklist_blocked_users", ["blacklist_id", "user_id"])

        # Adding model 'Choice'
        db.create_table(
            "poll_choice",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "choice",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
                (
                    "meta",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "poll",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="choices", to=orm["poll.Poll"]
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
        db.send_create_signal("poll", ["Choice"])

        # Adding model 'Votes'
        db.create_table(
            "poll_votes",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "poll",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="votes", to=orm["poll.Poll"]
                    ),
                ),
                (
                    "choice",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="votes", to=orm["poll.Choice"]
                    ),
                ),
                (
                    "counted",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "authentic",
                    self.gf("django.db.models.fields.BooleanField")(
                        default=False, db_index=True
                    ),
                ),
                (
                    "signature",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=300, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("poll", ["Votes"])

    def backwards(self, orm):
        # Deleting model 'PollConditions'
        db.delete_table("poll_pollconditions")

        # Deleting model 'Poll'
        db.delete_table("poll_poll")

        # Removing M2M table for field users_who_voted on 'Poll'
        db.delete_table("poll_poll_users_who_voted")

        # Removing M2M table for field conditions on 'Poll'
        db.delete_table("poll_poll_conditions")

        # Deleting model 'BlackList'
        db.delete_table("poll_blacklist")

        # Removing M2M table for field blocked_users on 'BlackList'
        db.delete_table("poll_blacklist_blocked_users")

        # Deleting model 'Choice'
        db.delete_table("poll_choice")

        # Deleting model 'Votes'
        db.delete_table("poll_votes")

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
        "poll.blacklist": {
            "Meta": {"object_name": "BlackList"},
            "blocked_users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'safe_poll_blacklists'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "poll": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'blacklist'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['poll.Poll']",
                },
            ),
        },
        "poll.choice": {
            "Meta": {"object_name": "Choice"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "choice": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "meta": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "poll": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'choices'", "to": "orm['poll.Poll']"},
            ),
        },
        "poll.poll": {
            "Meta": {"object_name": "Poll"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "conditions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'polls'",
                    "null": "True",
                    "to": "orm['poll.PollConditions']",
                },
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "db_index": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "max_of_choices": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "1", "db_index": "True"},
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
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "users_who_voted": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'safe_poll_voted'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "poll.pollconditions": {
            "Meta": {"object_name": "PollConditions"},
            "description": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "expression": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "value": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
        },
        "poll.votes": {
            "Meta": {"object_name": "Votes"},
            "authentic": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "choice": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'votes'", "to": "orm['poll.Choice']"},
            ),
            "counted": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "poll": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'votes'", "to": "orm['poll.Poll']"},
            ),
            "signature": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
        },
    }

    complete_apps = ["poll"]
