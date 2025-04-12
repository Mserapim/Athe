# -*- coding: utf-8 -*-
import json

from contrib.utils import getLogger
from django.contrib.auth.models import User
from django.conf import settings
from django.db import connections
from socket import gethostname


try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

import re


log = getLogger(__name__)

_thread_locals = local()


def current_request():
    return getattr(_thread_locals, "request", None)


def get_current_user():
    return getattr(_thread_locals, "user", None)


def set_current_user(user):

    if isinstance(user, str):
        try:
            user = User.objects.get(username=user)
        except User.DoesNotExist as e:
            log.exception(e)
            raise e
    elif isinstance(user, int):
        try:
            user = User.objects.get(pk=user)
        except User.DoesNotExist as e:
            log.exception(e)
            raise e

    # log.info('Setting user in thread locals (%s)' % user)
    setattr(_thread_locals, "user", user)


class AppDistributedInformation(object):

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        response = response or self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response

    def process_response(self, request, response):
        response["App-Node"] = gethostname()
        return response


class Debug(object):

    def process_response(self, request, response):
        try:
            log.debug("=" * 30)
            log.debug("URI: %s" % request.META.get("REQUEST_URI"))
            log.debug("METHOD: %s" % request.method)
            log.debug("CONTENT_LENGTH: %s" % request.META.get("CONTENT_LENGTH", -1))
            if int(request.META.get("CONTENT_LENGTH", -1)) > 0:
                log.debug("POST: %s" % request.POST)
        except Exception as e:
            log.exception(e)

        return response


class DebugResponse(object):

    def queries(self):
        data = {
            attr: {
                "count": len(connections[attr].queries),
                "totalTime": sum(
                    [float(item.get("time", 0)) for item in connections[attr].queries]
                ),
            }
            for attr in list(connections.databases.keys())
            if len(connections[attr].queries) > 0
        }

        return data

    def process_response(self, request, response):
        try:
            data = json.loads(response.content)
        except Exception:
            log.debug("Can't convert content to JSON")
        else:
            if isinstance(data, dict):
                data.update(TDEBUG={"queries": self.queries()})
                response.content = ""
                response.write(json.dumps(data))

        return response


class StartupLoader(object):

    LOADED = False

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        response = response or self.get_response(request)
        return response

    def doLoad(self):
        StartupLoader.LOADED = True
        for path in getattr(settings, "STARTUP_MODULES", []):
            try:
                log.info("Startup loading %s" % path)
                exec("from %s import *" % path)
            except Exception as e:
                log.exception(e)

    def process_request(self, request):
        from django.conf import settings

        if StartupLoader.LOADED is False:
            self.doLoad()
        else:
            getattr(settings, "STARTUP_VERBOSE", False) and log.debug(
                "StartupLoader already load this."
            )


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        response = response or self.get_response(request)
        return response

    def process_request(self, request):
        _thread_locals.user = getattr(request, "user", None)
        _thread_locals.request = request


class BadPatternRequestMethodData(object):

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        response = response or self.get_response(request)
        return response

    def process_request(self, request):
        request.REQUEST = getattr(request, request.method, None)


class CheckStat(object):

    def __init__(self):
        """ """
        from contrib.utils import getLogger as get_logger

        self.log = get_logger(self.__class__.__name__)

    def process_request(self, request):
        """ """
        for check in getattr(settings, "TO_CHECK_STATS", []):
            value = request.META.get(check.get("key"), "")
            if re.match(check.get("pattern"), value) is not None:
                self.log.info(check.get("msg", "") % request.META)
