# -*- coding: utf-8 -*-

import json
import re

from django.db import transaction

from contrib.controller import DefaultController
from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_new_display, nil_pk, nil_new_unicode
from contrib.utils import DateUtils, getLogger
from rh.cif.models import (
    AddressCif,
    ControlInformationMember,
    Property,
    ReferencePeriod,
    Teaching,
)
from standard.models import Configuration

log = getLogger(__name__)


class CifReferencePeriod(Restful):

    _model = ReferencePeriod

    full_text_index = (
        "exercise__icontains",
        "exercise_year__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.ManageConfiguration")')
        # self.response.write('Ext._create("cif.referenceperiod.Manage")')

    def copy_referenceperiod(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            with transaction.atomic():
                previous_referenceperiod = ReferencePeriod.objects.get(
                    pk=int(self.request.POST.get("previous_referenceperiod"))
                )
                old_controlinformation = ControlInformationMember.objects.filter(
                    referenceperiod=previous_referenceperiod
                )
                # Cria um novo periodo de referencia
                new_referenceperiod = ReferencePeriod(
                    previous_referenceperiod=previous_referenceperiod,
                    exercise=self.request.POST.get("exercise"),
                    start_date=DateUtils.str_to_date(
                        self.request.POST.get("start_date")
                    ),
                    end_date=DateUtils.str_to_date(self.request.POST.get("end_date")),
                )
                new_referenceperiod.save()
                # Cria um novo controle de informacoes referentes a um novo periodo para cada membro
                for old_information in old_controlinformation.all():
                    new_controlinformation = ControlInformationMember(
                        previous_controlinformation=old_information,
                        employee=old_information.employee,
                        referenceperiod=new_referenceperiod,
                    )
                    new_controlinformation.save()

                    # Copia atividades de docencia de um controle anteiror para o novo controle
                    if old_information.teaching.exists():
                        for old_teaching in old_information.teaching.all():
                            new_teaching = Teaching(
                                member=new_controlinformation,
                                educational_institution=old_teaching.educational_institution,
                                discipline=old_teaching.discipline,
                                work_hours=old_teaching.work_hours,
                                start_date=old_teaching.start_date,
                                end_date=old_teaching.end_date,
                            )
                            new_teaching.save()
                            if old_teaching.schedule.exists():
                                for sc in old_teaching.schedule.all():
                                    new_teaching.schedule.add(sc)
                            new_teaching.save()

                    # Copia endereços de um controle anteiror para o novo controle
                    if old_information.address.exists():
                        for old_address in old_information.address.all():
                            new_address = AddressCif(
                                previus_addres=old_address,
                                member=new_controlinformation,
                                start_date=old_address.start_date,
                                end_date=old_address.end_date,
                                type_residence=old_address.type_residence,
                                # municipio=old_address.municipio,
                                # logradouro=old_address.logradouro,
                                # tipo_logradouro=old_address.tipo_logradouro,
                                # numero=old_address.numero,
                                # complemento=old_address.complemento,
                                # bairro=old_address.bairro,
                                # cep=old_address.cep,
                                # tipo_endereco=old_address.tipo_endereco,
                            )
                            new_address.save()

                    # # Copia bens e valores para o novo controle
                    if old_information.property.exists():
                        for old_property in old_information.property.all():
                            new_property = Property(
                                member=new_controlinformation,
                                code=old_property.code,
                                country=old_property.country,
                                description=old_property.description,
                                current_value=old_property.current_value,
                                last_value=old_property.current_value,
                            )
                            new_property.save()

                    old_information.status = 2
                    old_information.save()
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
                message="Dados persistidos com sucesso!",
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "main_period" in params:
            params.update(main_period=params.get("main_period", "off").lower() == "on")

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                params.update(end_date=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                params.update(start_date=None)

        if "previous_referenceperiod" in params:
            if params.get("previous_referenceperiod") != "":
                field = getattr(self.Model, "previous_referenceperiod")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        previous_referenceperiod=query.get(
                            pk=params.get("previous_referenceperiod")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(previous_referenceperiod=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            modified_by=nil_pk(instance.modified_by, None),
            main_period=nil_new_unicode(instance.main_period, ""),
            modified_by_unicode=str(instance.modified_by) or None,
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            end_date=nil_date(instance.end_date, None),
            created_at=nil_datetime(instance.created_at, None),
            exercise_year=int(instance.exercise_year or 0),
            modified_at=nil_datetime(instance.modified_at, None),
            start_date=nil_date(instance.start_date, None),
            previous_referenceperiod=nil_pk(instance.previous_referenceperiod, None),
            previous_referenceperiod_unicode=nil_new_unicode(
                instance.previous_referenceperiod, ""
            ),
            exercise=nil_new_unicode(instance.exercise, ""),
            status_period=nil_new_unicode(instance.status_period, ""),
            status_period_display=nil_new_display(instance, "status_period", ""),
        )

        return rst


class CifConfiguration(DefaultController):
    def eval_value(self, value):
        if re.match(r"^\[.*\]$", value):
            return eval(value)
        else:
            return value

    def read(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("cif")
            log.info(cfg)
            rst.update(
                config={
                    item.key: self.eval_value(item.value)
                    for item in list(cfg.items.filter())
                }
            )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def write(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        cfg = Configuration.get_or_create("cif")

        cfg.set(self.request.POST.get("property"), self.request.POST.get("value"))

        self.response.write(json.dumps(rst))

    def save(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}
        try:
            cfg = Configuration.get_or_create("cif")
            for attr in self.request.POST:
                cfg.set(attr, self.request.POST.get(attr))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def json(self, args=[]):
        self.response.write('Ext._create("cif.referenceperiod.ConfigurationManage")')
