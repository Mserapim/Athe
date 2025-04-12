import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from rh.pvf.const import INTERNS_RECESS
from rh.dayoff.const import ACQP_PROGRESS
from datetime import datetime, timedelta
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.dayoff.models import AcquisitionPeriod

log = getLogger(__name__)

set_current_user("athenas")


def update_acq_period_intern_recess():
    count = 0
    for acq_period in AcquisitionPeriod.objects.filter(
        employee__ativo=True,
        status=ACQP_PROGRESS,
        days_not_booked_cache__gt=0,
        group_period__configuration__sub_type_of_usufruct__in=[INTERNS_RECESS],
    ):
        if acq_period.end_date_fruition and acq_period.start_date_fruition:
            diffs = acq_period.end_date_fruition - acq_period.start_date_fruition
            qtd_months = diffs.days // 30
            if qtd_months < 4:
                count = count + 1
                new_end_date = acq_period.end_date_fruition + timedelta(days=30)
                if new_end_date < acq_period.employee.termination_date:
                    acq_period.end_date_fruition = new_end_date
                    acq_period.save()
                    print("==================================================")
                    print(f"{acq_period} Atualizado.")
                else:
                    acq_period.end_date_fruition = (
                        acq_period.employee.termination_date - timedelta(days=1)
                    )
                    acq_period.save()
                    print("==================================================")
                    print(f"{acq_period} Atualizado.")
        else:
            print("==================================================")
            print(f"{acq_period} sem end_date_fruition")

    print(count)


def run():
    update_acq_period_intern_recess()


if __name__ == "__main__":
    run()
