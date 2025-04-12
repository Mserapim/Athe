# -.- coding: utf-8 -.-
import datetime
from datetime import timedelta
import time
import django
import os
import codecs

# os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'

# django.setup()


def run():
    ilru_cache = {}
    with codecs.open("/app/root/ilru_cache.csv", "r") as f_ilru_cache:
        for line in f_ilru_cache.readlines():
            line = line.split("|")
            if line[0] != "\n":
                ilru_cache.update(
                    {
                        line[0]: datetime.datetime.strptime(
                            line[1].replace("\n", ""), "%H:%M:%S.%f"
                        )
                    }
                )
    without_cache = {}
    with codecs.open("/app/root/without_cache.csv", "r") as f_without_cache:
        for line in f_without_cache.readlines():
            line = line.split("|")
            if line[0] != "\n":
                without_cache.update(
                    {
                        line[0]: datetime.datetime.strptime(
                            line[1].replace("\n", ""), "%H:%M:%S.%f"
                        )
                    }
                )
    count_r1_greater = 0
    count_r2_greater = 0
    for rs in ilru_cache.keys():
        d1 = ilru_cache.get(rs, 0)
        d2 = without_cache.get(rs, 0)
        if d1 > d2:
            count_r1_greater += 1
        else:
            count_r2_greater += 1

    print(f"count_ilru_cache_greater: {count_r1_greater}")
    print(f"count_without_cache_greater: {count_r2_greater}")


if __name__ == "__main__":
    run()
