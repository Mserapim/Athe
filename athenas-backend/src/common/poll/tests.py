# -*- coding:utf-8 -*-
import random
from django.contrib import auth
from django.utils import unittest
from django.test.client import Client
from .models import Poll

VOTERS_AMOUNT = auth.models.User.objects.all().count()


class PollTest(unittest.TestCase):

    def setUp(self):
        self.poll = Poll.objects.filter(active=True).latest("id")
        self.choices = self.poll.choices.filter(active=True, meta=False).values("id")
        self.users = auth.models.User.objects.all()[16:VOTERS_AMOUNT]

    def test_votes(self):
        for user in self.users:
            votes = []
            for i in range(self.poll.max_of_choices):
                votes.append(str(random.choice(self.choices)["id"]))
            print(
                "========================================================================="
            )
            client = Client()
            client.login(username=user.username, password="123")
            # self.assertEqual(logged, True)
            params = {"poll": self.poll.id, "votes": ",".join(votes), "password": "123"}
            print("Voting %s" % params)
            response = client.post("/SafePolls/vote/json/", params)
            print("Response: %s" % response)
            # self.assertEqual(response, )
