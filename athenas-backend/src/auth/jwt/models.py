# -*- coding: utf-8 -*-
import os
import jwt
import hashlib

from django.db import models
from django.conf import settings
from django.contrib.auth import login
from contrib.utils import getLogger


log = getLogger(__name__)


class Voucher(models.Model):
    user = models.ForeignKey(
        "auth.User", related_name="have_jwt_vouchers", on_delete=models.CASCADE
    )
    voucher_type = models.SmallIntegerField(
        choices=((1, "Descartavel"), (2, "Permanente"), (100, "Invalidada"))
    )
    token = models.CharField(max_length=32, blank=True)

    @classmethod
    def use(klass, request):
        token = request.META.get("HTTP_AUTHORIZATION", None)
        if token:
            token_type, token_value = token.split(" ")
            if token_type == "JWT":
                data = jwt.decode(
                    token_value,
                    getattr(settings, "SECRET_KEY", "secr3t"),
                    algorithms=["HS256"],
                )
                vouche = klass.objects.get(**data)
                vouche.__use(request)
            else:
                pass
        else:
            pass

    def __use(self, request):
        if self.voucher_type != 100:
            user = self.user
            user.backend = "jwt-authorization"
            login(request, user)
            request.voucher = self

        if self.voucher_type == 1:
            self.voucher_type = 100
            self.save()

    @property
    def jwt(self):
        data = {"pk": self.pk, "token": self.token}

        return jwt.encode(
            data, getattr(settings, "SECRET_KEY", "secr3t"), algorithm="HS256"
        )

    @property
    def is_active(self):
        return self.voucher_type != 100

    def save(self, *args, **kwags):
        if not self.pk:
            self.token = hashlib.new("md5", os.urandom(8192)).hexdigest()

        super(Voucher, self).save(*args, **kwags)


class DisposableVoucherManager(models.Manager):

    def get_queryset(self):
        return (
            super(DisposableVoucherManager, self).get_queryset().filter(voucher_type=1)
        )

    def create(self, **kwargs):
        kwargs.update(voucher_type=1)
        return super(DisposableVoucherManager, self).create(**kwargs)


class DisposableVoucher(Voucher):

    objects = DisposableVoucherManager()

    class Meta:
        proxy = True


class VoucherLog(models.Model):
    voucher = models.ForeignKey(Voucher, related_name="logs", on_delete=models.CASCADE)
