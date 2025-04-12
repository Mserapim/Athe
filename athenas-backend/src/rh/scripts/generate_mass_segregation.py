import os
import django
from datetime import datetime


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.models import SocialSecurityEmployee

log = getLogger(__name__)


set_current_user("athenas")


def run():
    print(
        """

        Este script popula o campo mass_segregation_plan de SocialSecurityEmployee

    """
    )
    social_employees = SocialSecurityEmployee.objects.all()

    for social_employee in social_employees:
        try:
            social_employee.save()
        except Exception as e:
            print(e)

    print(f"---- Finalizado ----")


if __name__ == "__main__":
    run()
