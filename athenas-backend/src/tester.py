#!/usr/bin/env python
# -*- coding:utf-8 -*-

import django
import os, argparse, importlib, unittest

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

parser = argparse.ArgumentParser(
    description="Running tests for non django app but with some django dependencies like settings.py module"
)
parser.add_argument(
    "module",
    type=str,
    help="Test module to run, in the python import path format. Example: myapp_or_package.the_test_module",
)
parser.add_argument(
    "-t",
    "--test-cases",
    type=str,
    nargs="+",
    help="Inform which test cases you want to run Example: myapp_or_package.the_test_module -t Test1 Test2...N ",
)

args = parser.parse_args()

test_suite = None
if args.test_cases:
    names = ["%s.%s" % (args.module, test_case) for test_case in args.test_cases]
    test_suite = unittest.defaultTestLoader.loadTestsFromNames(names)
else:
    module = importlib.import_module(args.module)
    test_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
unittest.TextTestRunner().run(test_suite)
