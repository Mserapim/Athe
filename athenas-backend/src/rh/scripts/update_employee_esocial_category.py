import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import Servidor

log = getLogger(__name__)

set_current_user("athenas")


def set_category_esocial():
    count = 0
    for employee in Servidor.objects.filter(user__isnull=False):
        employee.save()
        count = count + 1
        print("==================================================")
        print(f"{employee} Atualizado.")

    print(count)


def run():
    set_category_esocial()


if __name__ == "__main__":
    run()
