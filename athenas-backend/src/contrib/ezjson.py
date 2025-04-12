# !/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import decimal
import re

from django.template.defaultfilters import addslashes

from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


def encode(o, date_format="%Y/%m/%d", max_depth=3):
    return dump(o, date_format="%Y/%m/%d", max_depth=3)


def decode(json, to_object=False):
    load(json, to_object=False)


def dump(o, date_format="%Y/%m/%d", max_depth=3):
    """shortcut to Json.encode"""
    return Json.encode(o, date_format, max_depth)


def load(json, to_object=False):
    """shortcut to Json.decode"""
    return Json.decode(json, to_object)


class Json(object):
    __depth = 0
    __max_depth = None
    __date_format = None

    @classmethod
    def __normalize(self, o):
        """creates the pairs key/value, in json format, of each attribute of the python object, recursively"""
        json = ""

        if isinstance(o, (list, tuple)):
            arr = []
            for i in o:
                i = self.__normalize(i)
                if i:
                    arr.append(i)
            json = "[%s]" % ", ".join(arr)

        elif (
            self.__depth < self.__max_depth
            and hasattr(o, "__dict__")
            or isinstance(o, dict)
        ):
            self.__depth += 1
            dic = vars(o) if hasattr(o, "__dict__") else o
            arr = []
            for k, v in list(dic.items()):
                v = self.__normalize(v)
                if v and not re.match("^_", str(k)):
                    arr.append('"%s":%s' % (k, v))
            json = "{%s}" % ", ".join(arr)
            self.__depth -= 1
        else:
            json = self.__build_js_values(o)
        # log.info(json)
        return json

    @classmethod
    def __build_js_values(self, v):
        """builds json atomic values (like number, string, booleans...) from python constants e objects"""
        if (
            isinstance(
                v,
                (
                    bool,
                    int,
                    float,
                    str,
                    decimal.Decimal,
                    datetime.datetime,
                    datetime.date,
                    datetime.time,
                ),
            )
            or v is None
        ):
            if isinstance(v, bool):
                v = "false" if v is False else "true"
            elif isinstance(v, int):
                v = "%s" % int(v)
            elif isinstance(v, decimal.Decimal):
                v = "%s" % float(v)
            elif isinstance(v, str):
                v = addslashes(v)
                v = '"%s"' % str(v)
            elif isinstance(v, datetime.datetime):
                v = '"%s"' % DateUtils.datetime_to_str(v)
            elif isinstance(v, datetime.date):
                v = '"%s"' % DateUtils.date_to_str(v)
            elif isinstance(v, datetime.time):
                v = '"%s"' % v.strftime("H:M:S")
            elif v is None:
                v = "null"
            return v
        return False

    @classmethod
    def __build_py_values(self, json):
        """converts some javascript constants to python constants"""
        json = re.sub("null|undefined", "None", json)
        json = re.sub("false", "False", json)
        return re.sub("true", "True", json)

    @classmethod
    def __d2o(self, dic):
        """d2o means dictionary to object. this method creates an object from a dict"""
        o = DynaObject()
        for k, v in list(dic.items()):
            if isinstance(v, dict):
                v = self.__d2o(v)
            setattr(o, k, v)
        return o

    @classmethod
    def encode(self, o, date_format="%Y/%m/%d", max_depth=1):
        """
        Creates the json. you may specify the date format for attributes of types datetime.datetime, datetime.date or datetime.time.
        Also, its possible specify the max value to depth of the json serialization, in other words, you may decide how far the
        json serialization can achieve. Like objects inside another objects.
        """
        self.__date_format = date_format
        self.__max_depth = max_depth
        out = self.__normalize(o)
        # log.info(out)
        return out

    @classmethod
    def decode(self, json, to_object=False):
        """Create one python object or dictionary from json"""
        dic = eval(self.__build_py_values(json))
        return self.__d2o(dic) if to_object else dic


class DynaObject(object):
    pass
