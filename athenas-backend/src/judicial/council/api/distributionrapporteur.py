# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import DistributionRapporteur
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode
from contrib.nil import nil_datetime
from django.db import transaction
from judicial.api.partlawsuit import BasePartLawsuit

log = getLogger(__name__)


class CouncilDistributionRapporteur(BasePartLawsuit, Restful):

    _model = DistributionRapporteur

    def prepare(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                params = self.get_params(self.request.POST, self.force_upper)
                obj = self.Model.objects.get(pk=params.get("pk"))
                obj.prepare()
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Distribuição preparada.")

        self.renderer(rst)

    def distribute(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            with transaction.atomic():
                params = self.get_params(self.request.POST, self.force_upper)
                obj = self.Model.objects.get(pk=params.get("pk"))
                employee = obj.distribute()
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(
                employee={
                    "pk": employee.pk,
                    "name": str(employee.pessoa_fisica),
                },
                success=True,
                message="Relatoria distribuida",
            )

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            rapporteur=nil_pk(instance.rapporteur, None),
            rapporteur_unicode=nil_unicode(
                instance.rapporteur, "Não foi sorteado ainda"
            ),
            rapporteur_name=(
                instance.rapporteur.pessoa_fisica.nome
                if instance.rapporteur
                else "Não foi sorteado ainda"
            ),
            signed_at=nil_datetime(instance.signed_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            type_part=instance.type_part,
            created_at=nil_datetime(instance.created_at, None),
            cached_number=instance.cached_number,
            modified_at=nil_datetime(instance.modified_at, None),
            number=int(instance.number or 0),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            year=int(instance.year or 0),
            cache_rendered=instance.cache_rendered,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
        )

        return rst
