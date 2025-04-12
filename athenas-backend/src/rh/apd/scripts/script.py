# -.- coding: utf-8 -.-
import django
import os


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"


django.setup()


from rh.apd.models import PeriodicEvaluationPerformance


def run():
    for pep in PeriodicEvaluationPerformance.objects.filter(
        status=1, end_date__month__in=[5], end_date__year=2021
    )[0:10]:
        print(
            f"{pep} | days_to_bloke: {pep.days_to_bloke} | is_bloke: {pep.is_bloke} | days_to_begin: {pep.days_to_begin} | is_allowed_begin: {pep.is_allowed_begin}"
        )
        print()


if __name__ == "__main__":
    run()
