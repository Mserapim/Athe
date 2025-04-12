#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
from threading import Thread
from django.db.models import Q
from web.models import *
from contrib.utils import getLogger

log = getLogger("Search")


class Term(Thread):
    __total = 0
    __length = 100
    __results = []

    def __init__(self, conditions={}):
        Thread.__init__(self)
        conditions["active"] = True
        conditions["published_date__isnull"] = False
        self.__conditions = conditions

    def run(self):
        today = datetime.date.today()
        dynanmic = Q(publication_start__lte=today, publication_end__gte=today)
        static = Q(published=True)
        qs = Post.objects.filter(static | dynanmic, **self.__conditions).order_by(
            "-published_date"
        )
        Term.add_result(qs)

    @classmethod
    def get_total(self, reset=True):
        total = self.__total
        if reset:
            self.__total = 0
        return total

    @classmethod
    def add_result(self, qs):
        self.__total += qs.count()

        current_total = 0
        for item in self.__results:
            current_total += len(item)

        limit = 0
        if current_total < self.__length:
            limit = self.__length - current_total
            self.__results.append(
                qs.values("id", "title", "abstract", "slug", "published_date")[0:limit]
            )

    @classmethod
    def get_results(self):
        return self.__reduce(self.__results)

    @classmethod
    def __clear_results(self):
        self.__results = []

    @classmethod
    def __reduce(self, rs):
        reduced = []
        for qs in rs:
            for item in qs:
                if item not in reduced:
                    reduced.append(item)
        self.__clear_results()
        return reduced


class Engine(object):
    __tasks = []
    __kind_search = ["title", "tags__name"]

    def __init__(self, kind_search=None, overwrite=False):
        if kind_search:
            if isinstance(kind_search, str):
                kind_search = [kind_search]
            self.__kind_search = (
                self.__kind_search + kind_search if not overwrite else kind_search
            )

    def run(self, pars={}):
        self.time_start = datetime.datetime.now()

        terms = pars["terms"]
        del pars["terms"]

        terms = terms.split(" ")
        if len(terms) > 1:
            terms = [" ".join(terms)] + terms

        for term in terms:
            for kind in self.__kind_search:
                kw = {"%s__icontains" % kind: term}
                kw.update(pars)
                args = [Q(**kw)]
                if "areas__parent__slug" not in pars:
                    args.insert(0, ~Q(areas__parent__slug="intranet"))
                task = Term(kw)
                self.__tasks.append(task)
                task.start()

        while not self.__all_works_is_done():
            pass

        self.time_end = datetime.datetime.now()

        return Term.get_results()

    def __all_works_is_done(self):
        for t in self.__tasks:
            if t.is_alive():
                return False
        return True
