# -*- coding: utf-8 -*-
from unittest import TestCase
from contrib.middleware import set_current_user, get_current_user
from django.contrib.auth.models import User


class CurrentUserTestCase(TestCase):

    def setUp(self):
        self._user = User.objects.get(pk=1)

    def test_set_current_user_from_username(self):
        set_current_user(self._user.username)
        self.assertEqual(self._user, get_current_user())

    def test_set_current_user_from_id(self):
        set_current_user(self._user.pk)
        self.assertEqual(self._user, get_current_user())

    def test_set_current_user_from_user(self):
        set_current_user(self._user)
        self.assertEqual(self._user, get_current_user())
