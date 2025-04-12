import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import BenefitMovement

log = getLogger(__name__)

set_current_user("athenas")


def set_number_benefit():
    count = 0
    for benefit in BenefitMovement.objects.filter(benefit_role__isnull=False):
        benefit.save()
        count = count + 1
        print("==================================================")
        print(f"{benefit} Atualizado.")

    print(count)


def run():
    set_number_benefit()


if __name__ == "__main__":
    run()
