# -*- coding: utf-8 -*-
import time

from django.core.management.base import BaseCommand
from common.clinical.models import Prescription
from common.clinical import tasks
from django.contrib.auth.models import User
from contrib.middleware import set_current_user
from contrib.utils import getLogger

log = getLogger("db")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--build-pendent",
            "-b",
            help="Build all prescriptions in available status",
            dest="build_pendent",
            action="store_true",
        )

        parser.add_argument(
            "--dispatch-pendent",
            "-d",
            help="Dispatch all prescriptions in manufactured status",
            dest="dispatch_pendent",
            action="store_true",
        )

    def _build_all_pendent(self):
        for prescription in Prescription.objects.filter(delivery_state=2):
            print("Building %s ..." % prescription.cache_number)
            tasks.manufacture_prescription.delay(prescription.pk)

    def _dispatch_all_pendent(self):
        for prescription in Prescription.objects.filter(delivery_state=3):
            print("Dispatch %s ..." % prescription.cache_number)
            tasks.delivery_prescription.delay(prescription.pk)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, build_pendent=False, dispatch_pendent=False, *args, **kwargs):
        if build_pendent:
            self.set_user_to_job("job_clinicalctl__build_all_pendent")
            self._build_all_pendent()

        if dispatch_pendent:
            self.set_user_to_job("job_clinicalctl__dispatch_all_pendent")
            self._dispatch_all_pendent()
