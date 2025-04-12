# -*- coding: utf-8 -*-
import os
import json


class __Config(object):

    def __init__(self):
        self._loaded = False
        self._configuration = {}
        self._load()

    @property
    def is_loaded(self):
        return self._loaded

    def _load(self):
        try:
            config_file = os.environ.get("ATHENAS_CONFIG_FILE", "config.json")
            with open(config_file, "rt") as fd:
                self._configuration = json.load(fd)
            self._loaded = True
        except Exception:
            self._configuration = {}

    def get(self, name, value):
        if not self.is_loaded:
            self._load()

        return self._configuration.get(name, value)


_config = __Config()


def config(name, default="", cast=lambda x: x, use_secret=False):
    if use_secret:
        str = get_secret(name, default)
    else:
        str = os.environ.get(name, _config.get(name, default))

    return cast(str)


def get_secret(key, default):
    value = os.getenv(key, default)
    str_secret = ""
    if os.path.isfile(value):
        with open(value) as f:
            str_secret = "".join(line.rstrip() for line in f)

    return str(str_secret)


def config_file_content(name, default=b"", cast=lambda x: x):
    filepath = config(name, None)
    data = default

    if filepath and os.path.exists(filepath):
        with open(filepath, "rb") as fd:
            for chunk in iter(lambda: fd.read(8192), b""):
                data += chunk

    return cast(data)
