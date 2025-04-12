# -*- coding:utf-8 -*-

from contrib.utils import getLogger
from django.core.cache import cache
import uuid

log = getLogger()


def get_cache(key, group_key=None):
    # log.debug('GET_CACHE: %s/%s' % (key, group_key))
    if not group_key:
        return None
    else:
        cached = cache.get(group_key)
        if cached:
            return cached.get(key, None)
        else:
            return None


def set_cache(key, value, group_key=None):
    if group_key:
        cached = cache.get(group_key)
        if not cached:
            cached = {}
        cached[key] = value
        cache.set(group_key, cached)
        # log.debug('SET_CACHE: %s/%s >> %s' % (key, group_key, value))


def delete_cache(group_key):
    # log.debug('DELETE_CACHE: %s' % group_key)
    cache.delete(group_key)


def make_group_key():
    return uuid.uuid4().hex
