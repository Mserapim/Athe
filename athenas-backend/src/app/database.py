# -*- coding: utf-8 -*-
import logging
import time

from django.conf import settings
from django.db import connections

log = logging.getLogger("app.database")


class NodeRoute(object):

    def is_alive(klass, db_alias):
        alive = getattr(
            klass, "_".join(["", db_alias, "alive"]), {"schedule": 0, "alive": True}
        )

        if alive.get("schedule", 0) < time.time():
            try:
                cursor = connections[db_alias].cursor()
                cursor.execute("SELECT 1 as ONE")
                cursor.fetchone()
                cursor.close()
            except Exception as e:
                log.exception(e)
                alive.update(alive=False, schedule=time.time() + 5)
            else:
                alive.update(alive=True, schedule=time.time() + 5)

            setattr(klass, "_".join(["", db_alias, "alive"]), alive)

        return alive.get("alive")

    @classmethod
    def get_read_database(klass):
        if not hasattr(klass, "_read_db_alias"):
            db_alias = getattr(settings, "DATABASE_FOR_READ", "readdb")
            if db_alias not in getattr(settings, "DATABASES", {}):
                log.warning(
                    "Não encontrei a configuração de banco para o alias %s", db_alias
                )
                log.warning("Neste caso será retornado o banco de dados default")
                db_alias = "default"
            klass._read_db_alias = db_alias
        return klass._read_db_alias

    @classmethod
    def get_write_database(klass):
        if not hasattr(klass, "_write_db_alias"):
            db_alias = getattr(settings, "DATABASE_FOR_WRITE", "default")
            if db_alias != "default" and db_alias not in getattr(
                settings, "DATABASES", {}
            ):
                log.warning(
                    "Não encontrei a configuração de banco para o alias %s", db_alias
                )
                log.warning("Neste caso será retornado o banco de dados default")
                db_alias = "default"
            klass._write_db_alias = db_alias
        return klass._write_db_alias

    @classmethod
    def counter_write(klass):
        klass._counter_write = getattr(klass, "_counter_write", 0) + 1
        return klass._counter_write

    @classmethod
    def counter_read(klass):
        klass._counter_read = getattr(klass, "_counter_read", 0) + 1
        return klass._counter_read

    def db_for_read(self, model, **hints):
        if not getattr(self, "force_database", None):
            db_alias = self.get_read_database()
            db_alias = (
                db_alias if self.is_alive(db_alias) else self.get_write_database()
            )

            log.info(
                "R(%d): %s for model %s",
                self.counter_read(),
                db_alias,
                ".".join([model._meta.app_label, model._meta.model_name]),
            )

            return db_alias
        else:
            return self.force_database

    def db_for_write(self, model, **hints):
        if not getattr(self, "force_database", None):
            db_alias = self.get_write_database()
            db_alias = db_alias if self.is_alive(db_alias) else None

            log.info(
                "W(%d): %s for model %s",
                self.counter_write(),
                db_alias,
                ".".join([model._meta.app_label, model._meta.model_name]),
            )

            return db_alias
        else:
            return self.force_database

    def allow_relation(self, obj1, obj2, **hints):
        return True


class ForceDatabase:

    def __init__(self, db_alias):
        self.db_alias = db_alias

    def __enter__(self):
        if getattr(NodeRoute, "force_database", None):
            raise Exception("Um banco de dados já foi forçado.")
        else:
            NodeRoute.force_database = self.db_alias

    def __exit__(self, *args, **kwargs):
        NodeRoute.force_database = None


force_database = ForceDatabase
