# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from raf.models import AutoReference, DataEProc
from judicial.models import LegalClassification
import raf.api.util as util

log = getLogger(__name__)


class RAFAutoReference(RestfulDRY):

    _model = AutoReference

    full_text_index = ("process_number__icontains",)

    def model_to_dict(self, instance):
        _dict_ = super(RAFAutoReference, self).model_to_dict(instance)

        _dict_.update(
            {
                "autoreference_id": instance.pk,
                "process_number": instance.process_number_formatted,
            }
        )

        return _dict_

    def get_dataeproc(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            autoreference = self.get_query().get(id=params.get("autoreference"))
            data = []
            dataeproc = autoreference.content_object
            if dataeproc:
                data.append(
                    {
                        "processo": (
                            dataeproc.processo_formatted
                            if dataeproc.processo != "None"
                            else ""
                        ),
                        "classe": (
                            LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codclasse
                                    if dataeproc.codclasse != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalclass",
                            )
                            .values("path_cache")
                            .first()["path_cache"]
                            if LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codclasse
                                    if dataeproc.codclasse != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalclass",
                            ).first()
                            else ""
                        ),
                        "assuntoprincipal": (
                            LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codassuntoprincipal
                                    if dataeproc.codassuntoprincipal != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalmatter",
                            )
                            .values("path_cache")
                            .first()["path_cache"]
                            if LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codassuntoprincipal
                                    if dataeproc.codassuntoprincipal != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalmatter",
                            ).first()
                            else ""
                        ),
                        "movimento": (
                            LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codmovimento
                                    if dataeproc.codmovimento != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalmoviment",
                            )
                            .values("path_cache")
                            .first()["path_cache"]
                            if LegalClassification.objects.filter(
                                cnmp_code=int(
                                    dataeproc.codmovimento
                                    if dataeproc.codmovimento != "None"
                                    else "0"
                                ),
                                taxonomy_type="legalmoviment",
                            ).first()
                            else ""
                        ),
                        "datamovimento": (
                            dataeproc.datamovimento
                            if dataeproc.datamovimento != "None"
                            else ""
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("autoreference")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def get_dataeext(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            autoreference = self.get_query().get(id=params.get("autoreference"))
            data = []
            dataeext = autoreference.content_object
            if dataeext:
                data.append(
                    {
                        "processo": (
                            dataeext.proccess_number if dataeext.proccess_number else ""
                        ),
                        "classe": (
                            dataeext.legalclass.path_cache
                            if dataeext.legalclass
                            else ""
                        ),
                        "assuntoprincipal": (
                            dataeext.legalmatter.path_cache
                            if dataeext.legalmatter
                            else ""
                        ),
                        "movimento": (
                            dataeext.legalmovement.path_cache
                            if dataeext.legalmovement
                            else ""
                        ),
                        "datamovimento": (
                            dataeext.date_movement.strftime("%d/%m/%y %H:%M:%S")
                            if dataeext.date_movement
                            else ""
                        ),
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("autoreference")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def get_attendance(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            autoreference = self.get_query().get(id=params.get("autoreference"))
            data = []
            step = autoreference.content_object
            if step:
                data.append(
                    {
                        "attendance_redered": step.attendance.rendered,
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("autoreference")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def get_dataadjustment(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            autoreference = self.get_query().get(id=params.get("autoreference"))
            data = []
            dataadjustment = autoreference.content_object
            if dataadjustment:
                data.append(
                    {
                        "dataadjustment_rendered": dataadjustment.rendered,
                    }
                )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("autoreference")).count(),
                collection=data,
            )
        return self.renderer(rst)
