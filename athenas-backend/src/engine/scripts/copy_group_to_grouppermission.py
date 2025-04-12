import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
import django

django.setup()

from django.contrib.auth.models import Group
from engine.models import GroupPermission


def execute():
    """
    Copia todos os registros da tabela Group para a tabela GroupPermission
    """
    groups = Group.objects.all()
    for group in groups:
        print("Grupo: " + group.name)
        group_permission = GroupPermission()
        for field in group.__dict__.keys():
            group_permission.__dict__[field] = group.__dict__[field]
        group_permission.save()
