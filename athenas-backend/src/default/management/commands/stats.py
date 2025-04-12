# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

import os
import json

LEVEL_QUIET = 0
LEVEL_ERROR = 1
LEVEL_INFO = 2
LEVEL_DEBUG = 3


class Command(BaseCommand):

    help = """Show stats information."""

    @classmethod
    def log(cls, message):
        (LEVEL_QUIET <= cls.verbosity) and cls.print_message(message)

    @classmethod
    def error(cls, message):
        (LEVEL_ERROR <= cls.verbosity) and cls.print_message(message)

    @classmethod
    def info(cls, message):
        (LEVEL_INFO <= cls.verbosity) and cls.print_message(message)

    @classmethod
    def debug(cls, message):
        (LEVEL_DEBUG <= cls.verbosity) and cls.print_message(message)

    @classmethod
    def print_message(cls, message):
        print(message)

    def prepare(self, data):
        rst = {}

        screen_size = {}
        body_size = {}
        lang = {}
        platform = {}
        vendor = {}

        for info in list(data.values()):
            part = info.get("screen", {})
            str_key = "%(width)sx%(height)s" % part

            screen_size.update({str_key: screen_size.get(str_key, 0) + 1})

            part = info.get("body", {})
            str_key = "%(width)sx%(height)s" % part
            body_size.update({str_key: body_size.get(str_key, 0) + 1})

            part = info.get("navigator", {})
            str_key = part.get("language", "undefined").lower()
            lang.update({str_key: lang.get(str_key, 0) + 1})

            str_key = part.get("platform", "private").lower()
            platform.update({str_key: platform.get(str_key, 0) + 1})

            str_key = part.get("vendor", "private").lower()
            str_key = "mozilla" if str_key == "" else str_key
            vendor.update({str_key: vendor.get(str_key, 0) + 1})

        def percent(params, total):
            for k, v in list(params.items()):
                params.update({k: [v, (float(v) / float(total)) * 100]})
            return params

        total = len(list(data.keys()))
        rst.update(
            screen_size=percent(screen_size, total),
            lang=percent(lang, total),
            platform=percent(platform, total),
            vendor=percent(vendor, total),
        )

        return rst

    def print_stats(self, title, slot, data):
        self.log("")
        self.log("-" * (len(title) + 4))
        self.log("| %s |" % title)
        self.log("-" * (len(title) + 4))

        store = data.get(slot)
        keys = sorted(
            [(k, v[0]) for k, v in list(store.items())],
            key=lambda x: x[1],
            reverse=True,
        )

        keys = keys if len(keys) < 10 else keys[:10]

        position = 0
        for item in keys:
            position += 1
            k = item[0]
            v = store.get(k)
            p = dict(
                list(zip(("key", "position", "count", "percent"), ([k, position] + v)))
            )
            self.log(" %(position)2d. %(key)-20s : %(percent)6.2f%% (%(count)d)" % p)

    def handle(self, verbosity, *args, **kargs):
        self.__class__.verbosity = int(verbosity or 0)
        self.log("-" * 30)
        self.log("Stats")

        from django.conf import settings

        cache_dir = getattr(settings, "CACHE_PATH", None)

        if cache_dir is not None:
            stats_filepath = os.path.join(cache_dir, "stats.cache")

            try:
                self.info("Loading stats from %s" % stats_filepath)
                data = json.load(open(stats_filepath, "r"))
            except IOError:
                self.error("Cant read %s" % stats_filepath)
            else:
                self.log("Process the stats data information...")
                self.log("Number of stats %d" % len(data))

                rst = self.prepare(data)

                self.print_stats("Screen Size", "screen_size", rst)
                self.print_stats("Platform", "platform", rst)
                self.print_stats("Vendor", "vendor", rst)
                self.print_stats("Language", "lang", rst)

        else:
            self.error("The CACHE_PATH configuration not set in settings.")
        self.log("-" * 30)
