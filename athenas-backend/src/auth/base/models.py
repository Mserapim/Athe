# -*- coding:utf-8 -*-
import os, hashlib

from django.db import models
from django.contrib.auth.models import User


class PasswordChangeRequest(models.Model):
    key = models.CharField(max_length=64, db_index=True)
    valid = models.BooleanField(default=True, db_index=True)
    user = models.ForeignKey(
        User,
        related_name="password_change_requests",
        null=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = hashlib.sha256(os.urandom(4096)).hexdigest()
        super(PasswordChangeRequest, self).save(*args, **kwargs)
