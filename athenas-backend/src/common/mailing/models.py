# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

PERMISSION_CHOICES = (
    ("basic", "Básico"),
    ("reviser", "Revisor"),
    ("admin", "Administrador"),
)


class Common(models.Model):
    name = models.CharField(max_length=150, blank=True)
    slug = models.SlugField(max_length=150, db_index=True, blank=True)

    def __str__(self):
        return "%s" % self.name


class MailingUser(models.Model):
    user = models.OneToOneField(
        User, related_name="mailing_user", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    permission = models.CharField(
        max_length=12, default="basic", db_index=True, choices=PERMISSION_CHOICES
    )


class Profile(Common):
    printer_name = models.CharField(max_length=100)
    users = models.ManyToManyField(MailingUser, related_name="profiles")

    common_ptr = models.OneToOneField(
        Common, parent_link=True, related_name="profile_child", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


class Group(Common):
    profile = models.ForeignKey(
        Profile, related_name="groups", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


class Treatment(Common):
    common_ptr = models.OneToOneField(
        Common,
        parent_link=True,
        related_name="treatment_child",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)


class Company(Common):
    common_ptr = models.OneToOneField(
        Common, parent_link=True, related_name="company_child", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


class Position(Common):
    common_ptr = models.OneToOneField(
        Common,
        parent_link=True,
        related_name="position_child",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)


class State(Common):
    uf = models.CharField(max_length=2, blank=True)
    common_ptr = models.OneToOneField(
        Common, parent_link=True, related_name="state_child", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s - %s" % (self.name, self.uf)


class City(Common):
    state = models.ForeignKey(
        State, related_name="cities", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s/%s" % (self.name, self.state.uf)


class Address(models.Model):
    locality = models.CharField(max_length=150, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=10, db_index=True, blank=True)
    city = models.ForeignKey(
        City, related_name="addresses", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s %s \n%s - %s" % (
            self.locality,
            self.neighborhood,
            self.code,
            self.city,
        )


class Phone(models.Model):
    fax = models.CharField(max_length=15, blank=True)
    normal = models.CharField(max_length=15, blank=True)
    mobile = models.CharField(max_length=15, blank=True)


class Contact(Common):
    groups = models.ManyToManyField(Group, related_name="contacts", blank=True)
    profile = models.ForeignKey(
        Profile, related_name="contacts", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    treatment = models.ForeignKey(
        Treatment, related_name="contacts", on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company, related_name="contacts", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    position = models.ForeignKey(
        Position, related_name="contacts", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    address = models.OneToOneField(
        Address, related_name="contact", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    phone = models.OneToOneField(
        Phone, related_name="contact", null=True, on_delete=models.CASCADE
    )
