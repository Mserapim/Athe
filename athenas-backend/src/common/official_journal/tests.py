# -*- coding:utf-8 -*-

import unittest
from pprint import pprint

from contrib import mongo
from contrib.middleware import set_current_user

from common.official_journal.models import Journal


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        set_current_user("tonyreis")


class JournalToMongoTestCase(BaseTestCase):

    def test_model_mapping(self):
        journal = Journal.objects.last()

        fields = ["id", "UID", "name", "created_at", "published_date", "text"]

        custom_fields = [{"name": "download_url", "function": "file_url"}]

        client = mongo.connect()
        mapper = (
            mongo.ODM(fields=fields + ["code", "suplements"])
            .use(client)
            .db("fulltextIndex")
            .to("officialJournals")
            .custom_fields(custom_fields)
            .rel(
                "suplements",
                fields=fields,
                custom_fields=custom_fields,
                query_params=Journal.published(),
            )
        )

        pprint(mapper.save(journal), indent=4)
