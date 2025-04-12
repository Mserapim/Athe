# -*- coding: utf-8 -*-


class Singleton(object):

    _instance = None

    def __new__(self, *args, **kargs):
        if Singleton._instance is None:
            Singleton._instance = object.__new__(self, *args, **kargs)

        return Singleton._instance

    @classmethod
    def get_instance(cls, *args, **kargs):
        return cls(*args, **kargs)
