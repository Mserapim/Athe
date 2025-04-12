# -*- coding: utf-8 -*-
import os
import re

from django.core.management import call_command
from contrib.utils import getLogger
from contrib.middleware import set_current_user

log = getLogger(__name__)


class Config:
    pass


def setUp():
    log.info("SetUp")
    # Config.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    # Config.FIXTURE_DIR = os.path.join(Config.TEST_DIR, 'fixtures')

    # log.info('Loading fixtures from "%s" ...', Config.FIXTURE_DIR)
    # fixtures = []
    # for filename in os.listdir(Config.FIXTURE_DIR):
    #     fixtures.append(filename)

    # for filename in sorted(fixtures):
    #     filepath = os.path.join(Config.FIXTURE_DIR, filename)
    #     call_command('loaddata', filepath)

    # log.info('done')
    # set_current_user('athenas')


def tearDown():
    log.info("Droping data...")
    log.info("done")
