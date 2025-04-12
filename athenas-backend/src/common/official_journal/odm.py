# -*- coding:utf-8 -*-
# Create your the model document mappers here

import datetime
from django.db.models import Q
from contrib import mongo


class JournalODM(object):

    base_fields = ["id", "UID", "name", "created_at", "published_date", "text"]

    journal_fields = base_fields + ["extra", "code", "suplements"]

    custom_fields = [
        {"name": "fullname", "property": "fullname"},
        {"name": "year", "property": "year"},
        {"name": "month", "property": "month"},
        {"name": "hash", "property": "file_hash"},
        {"name": "download_url", "property": "file_url"},
    ]

    @property
    def mapper(self):
        date = datetime.datetime.now()
        odm = (
            mongo.ODM()
            .use(mongo.connect())
            .db("fulltextIndex")
            .to("officialJournals")
            .fields(self.journal_fields)
            .custom_fields(self.custom_fields)
            .rel(
                "suplements",
                fields=self.base_fields,
                custom_fields=self.custom_fields,
                query_params=Q(published_date__lte=date),
            )
        )
        return odm
