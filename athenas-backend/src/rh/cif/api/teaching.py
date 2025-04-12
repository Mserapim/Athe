# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_new_display, nil_pk, nil_new_unicode

# from rh.models import *
from contrib.utils import DateUtils, getLogger
from rh.cif.models import ControlInformationMember, ReferencePeriod, Teaching

# from django.core.exceptions import *


log = getLogger(__name__)


class CifTeaching(Restful):

    _model = Teaching

    full_text_index = (
        "discipline__name__icontains",
        "educational_institution__razao_social__icontains",
        "educational_institution__nome__icontains",
        "educational_institution__county__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.teaching.Manage")')

    def validate(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            teac = Teaching.objects.get(pk=self.request.POST.get("oId"))
            if not teac.schedule.exists():
                raise Exception("Preecha o campo Horários")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def confirm_not_teaching(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            control_information = ControlInformationMember.objects.get(
                pk=self.request.POST.get("pk_member")
            )
            active_period = ReferencePeriod.objects.get(
                main_period=False, status_period=1
            )
            teac = Teaching.objects.filter(
                member=control_information, refperiod_teaching=active_period
            ).first()
            if teac:
                teac.status = 2
                teac.save()
            else:
                teac = Teaching(
                    member=control_information,
                    status=2,
                    refperiod_teaching=active_period,
                )
                teac.save()

        except ReferencePeriod.MultipleObjectsReturned:
            rst.update(
                message="Há mais de um Período de Referência ativo. Entre em contato com a Corregedoria sobre o problema!"
            )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def confirm_action(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            teaching = self._model.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            )
            for teac in teaching:
                teac.status = 2
                teac.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        # log.info(params)

        if "authorization" in params:
            params.update(
                authorization=params.get("authorization", "off").lower() == "on"
            )

        if "refperiod_teaching" in params:
            if params.get("refperiod_teaching") != "":
                field = getattr(self.Model, "refperiod_teaching")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        refperiod_teaching=query.get(
                            pk=params.get("refperiod_teaching")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Período de Referência!")
                # params.update(refperiod_teaching=None)

        if "member" in params:
            if params.get("member") != "":
                field = getattr(self.Model, "member")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(member=query.get(pk=params.get("member")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                log.info("erro")
                # cif = ControlInformationMember.objects.get(employee__servidor=self.request.user.servidor, status=1)
                # params.update(member=cif)

        if "educational_institution" in params:
            if params.get("educational_institution") != "":
                field = getattr(self.Model, "educational_institution")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        educational_institution=query.get(
                            pk=params.get("educational_institution")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Instituição de Ensino!")
                # params.update(educational_institution=None)

        if "discipline" in params:
            if params.get("discipline") != "":
                field = getattr(self.Model, "discipline")
                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(discipline=query.get(pk=params.get("discipline")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Disciplina!")
                # params.update(discipline=None)

        if "file_document" in params:
            if params.get("file_document") != "":
                field = getattr(self.Model, "file_document")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        file_document=query.get(pk=params.get("file_document"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(file_document=None)

        if "work_hours" in params:
            if params.get("work_hours") != "":
                params.update(work_hours=params.get("work_hours"))
            else:
                raise Exception("Preencha o campo Carga Horária!")
                # params.update(work_hours=None)

        if "start_date" in params:
            if params.get("start_date") != "":
                params.update(
                    start_date=DateUtils.str_to_date(params.get("start_date"))
                )
            else:
                raise Exception("Preencha o campo Data Início Docência!")
                # params.update(start_date=None)

        if "end_date" in params:
            if params.get("end_date") != "":
                params.update(end_date=DateUtils.str_to_date(params.get("end_date")))
            else:
                raise Exception("Preencha o campo Data Fim Docência!")
                # params.update(end_date=None)

        params.update(status=2)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        if instance.validade_excercises_teaching():
            rst.update(
                icons=instance.icons,
                authorization=nil_new_unicode(instance.authorization, ""),
                status=instance.status,
                status_display=nil_new_display(instance, "status", ""),
                status_pendency=nil_new_unicode(instance.status_pendency, ""),
                status_pendency_display=nil_new_display(
                    instance, "status_pendency", ""
                ),
                schedules=instance.get_schedules(),
                discipline=nil_pk(instance.discipline, None),
                discipline_unicode=nil_new_unicode(instance.discipline, ""),
                modified_by=nil_pk(instance.modified_by, None),
                modified_by_unicode=("%s" % instance.modified_by),
                end_date=nil_date(instance.end_date, None),
                created_at=nil_datetime(instance.created_at, None),
                modified_at=nil_datetime(instance.modified_at, None),
                created_by=nil_pk(instance.created_by, None),
                created_by_unicode=("%s" % instance.created_by),
                educational_institution=nil_pk(instance.educational_institution, None),
                educational_institution_unicode=nil_new_unicode(
                    instance.educational_institution, ""
                ),
                member=nil_pk(instance.member, None),
                member_unicode=nil_new_unicode(instance.member, ""),
                work_hours=int(instance.work_hours or 0),
                file_document=nil_pk(instance.file_document, None),
                file_document_unicode=nil_new_unicode(instance.file_document, ""),
                start_date=nil_date(instance.start_date, None),
                refperiod_teaching=nil_pk(instance.refperiod_teaching, None),
                refperiod_teaching_unicode=nil_new_unicode(
                    instance.refperiod_teaching, ""
                ),
                refperiod_status=nil_new_unicode(
                    instance.refperiod_teaching.status_period, ""
                ),
                modality=nil_new_unicode(instance.modality, ""),
                modality_display=nil_new_display(instance, "modality", ""),
            )
        else:
            rst.update(
                icons=instance.icons,
                authorization=nil_new_unicode(instance.authorization, ""),
                status=instance.status,
                status_display=nil_new_display(instance, "status", ""),
                status_pendency=nil_new_unicode(instance.status_pendency, ""),
                status_pendency_display=nil_new_display(
                    instance, "status_pendency", ""
                ),
                discipline=nil_pk(instance.discipline, None),
                discipline_unicode=nil_new_unicode(instance.text_not_teaching, ""),
                schedules=nil_new_unicode(instance.text_not_teaching, ""),
                modified_by=nil_pk(instance.modified_by, None),
                modified_by_unicode=("%s" % instance.modified_by),
                end_date=nil_date(instance.end_date, None),
                created_at=nil_datetime(instance.created_at, None),
                modified_at=nil_datetime(instance.modified_at, None),
                created_by=nil_pk(instance.created_by, None),
                created_by_unicode=("%s" % instance.created_by),
                educational_institution=nil_pk(instance.educational_institution, None),
                educational_institution_unicode=nil_new_unicode(
                    instance.text_not_teaching, ""
                ),
                member=nil_pk(instance.member, None),
                member_unicode=nil_new_unicode(instance.member, ""),
                work_hours=int(instance.work_hours or 0),
                file_document=nil_pk(instance.file_document, None),
                file_document_unicode=nil_new_unicode(instance.file_document, ""),
                start_date=nil_date(instance.start_date, None),
                refperiod_teaching=nil_pk(instance.refperiod_teaching, None),
                refperiod_teaching_unicode=nil_new_unicode(
                    instance.refperiod_teaching, ""
                ),
                refperiod_status=nil_new_unicode(
                    instance.refperiod_teaching.status_period, ""
                ),
                modality=nil_new_unicode(instance.modality, ""),
                modality_display=nil_new_display(instance, "modality", ""),
            )

        return rst
