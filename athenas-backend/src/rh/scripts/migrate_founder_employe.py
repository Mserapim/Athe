import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import BenefitMovement

log = getLogger(__name__)

set_current_user("athenas")


def migratedata_founder_employee():
    for benefit in BenefitMovement.objects.filter():
        if benefit.servidor.founder_employee and benefit.benefit_role:
            benefit.founder_employee = benefit.servidor.founder_employee
            benefit.save()


def run():
    migratedata_founder_employee()


if __name__ == "__main__":
    run()
