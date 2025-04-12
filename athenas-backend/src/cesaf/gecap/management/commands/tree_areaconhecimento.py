# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from cesaf.gecap.models import AreaConhecimento


class Command(BaseCommand):

    help = "Monta arvore de areas de conhecimento utilizado no software do cesaf."

    option_list = BaseCommand.option_list + ()

    def handle(self, *args, **kargs):
        self.go()

    def go(self, root=None):
        query = AreaConhecimento.objects.filter(sub_area_de=root).order_by(
            "codigo_cnpq"
        )
        num = 0
        for r in query:
            num += 1

            if r.codigo_cnpq == 0 or r.codigo_cnpq is None:
                r.codigo_cnpq = num
                r.save()

            print(r)
            self.go(r)
