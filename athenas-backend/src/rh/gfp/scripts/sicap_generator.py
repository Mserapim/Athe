# -*- coding: utf-8 -*-
""""""

import os
import django


os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
django.setup()


from rh.gfp.generators.sicap.protocol import SicapGenerator
from contrib.middleware import set_current_user
from contrib.utils import getLogger


log = getLogger(__name__)


set_current_user("athenas")


def run():
    SicapGenerator(
        year=2021,
        months=[1],
        feedback=lambda progress_message, progress, **kwargs: False,
        task=None,
        paymentfile=None,
    ).generate()


if __name__ == "__main__":
    run()
