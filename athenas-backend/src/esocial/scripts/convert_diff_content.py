# -.- coding: utf-8 -.-
import json
import re
import os

import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from esocial.utils import format_diff_content, process_xml_diff
from contrib.middleware import set_current_user
from esocial.models import Event
from contrib.utils import getLogger


log = getLogger(__name__)


set_current_user("gustavodettenborn")


def run():
    query = Event.objects_all.filter(diff_content__isnull=False).exclude(
        diff_content=""
    )
    print(query.count())
    for event in query:
        event = event.event
        diff = event.diff_content
        # print(event, diff)

        try:
            format_diff_content(diff)
        except Exception as err:
            print(err)
            print(event.registry_employee, event)
        try:
            process_xml_diff(event.xml_diff)
        except Exception as err:
            print(err)
            print(event.registry_employee, event)


def test():
    # t = '{"dependente": [{"oids": [set(), {"1251", "2","3"}]}]}'
    t = '{"dependente": [{"oids": [set(), {"1251"}]}]}'
    print(t)
    # mfound = re.search('([\{])(\"[0-9]+\"?,?\s?)+[\}]', t)
    # print(list(eval(mfound.group(0))))
    # mfound = re.search('set\(([^)]*)\)|([\{])(\"[0-9]+\"?,?\s?)+[\}]', t)
    # print(list(eval(mfound.group(0))))

    mfound = re.finditer('set\(([^)]*)\)|([\{])("[0-9]+"?,?\s?)+[\}]', t)
    for value in mfound:
        print("value.group(0)")
        print(value.group(0))


if __name__ == "__main__":
    # test()
    run()
