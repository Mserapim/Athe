# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_new_display, nil_pk, nil_new_unicode
from contrib.utils import getLogger
from rh.cif.models import ControlInformationMember, Property

log = getLogger(__name__)


class CifProperty(Restful):

    _model = Property

    full_text_index = ("description__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("cif.property.Manage")')

    def confirm_action(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            props = self._model.objects.filter(pk__in=self.request.POST.getlist("pks"))
            for prop in props:
                prop.refperiod_property = prop.member.referenceperiod
                prop.status = 2
                prop.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def confirm_not_property(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            control_information = ControlInformationMember.objects.get(
                pk=self.request.POST.get("pk_member")
            )
            if Property.objects.filter(
                member=control_information, country=None
            ).exists():
                raise Exception("Você já informou que não possui bens ou valores!")
            else:
                prop = Property(
                    member=control_information,
                    status=2,
                    current_value=0,
                    refperiod_property=control_information.referenceperiod,
                )
                prop.save()

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
                log.info("error")
                # cif = ControlInformationMember.objects.get(employee__servidor=self.request.user.servidor, status=1)
                # params.update(member=cif)

        if "code" in params:
            if params.get("code") != "":
                field = getattr(self.Model, "code")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(code=query.get(pk=params.get("code")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("O campo Código deve ser informado.")

        if "country" in params:
            if params.get("country") != "":
                field = getattr(self.Model, "country")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(country=query.get(pk=params.get("country")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("O campo País deve ser informado.")

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

        if "refperiod_property" in params:
            if params.get("refperiod_property") != "":
                field = getattr(self.Model, "refperiod_property")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        refperiod_property=query.get(
                            pk=params.get("refperiod_property")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Período de Referência!")
                # params.update(refperiod_property=None)

        if "description" in params:
            if params.get("description") != "" and len(params.get("description")) > 15:
                params.update(description=params.get("description"))
            else:
                raise Exception(
                    "O campo Descrição deve conter no mínimo 15 caracteres!"
                )

        params.update(status=2)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            icons=instance.icons,
            status=instance.status,
            status_display=nil_new_display(instance, "status", ""),
            kind=nil_new_unicode(instance.kind, ""),
            kind_display=nil_new_display(instance, "kind", ""),
            status_pendency=nil_new_unicode(instance.status_pendency, ""),
            status_pendency_display=nil_new_display(instance, "status_pendency", ""),
            code=nil_pk(instance.code, None),
            code_unicode=nil_new_unicode(instance.code, ""),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            description=(
                "%s" % instance.description
                if instance.validade_exists_property()
                else "%s" % instance.text_not_property
            ),
            country=nil_pk(instance.country, None),
            country_unicode=nil_new_unicode(instance.country, ""),
            created_at=nil_datetime(instance.created_at, None),
            modified_at=nil_datetime(instance.modified_at, None),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=str(instance.created_by) or None,
            member=nil_pk(instance.member, None),
            member_unicode=nil_new_unicode(instance.member, ""),
            file_document=nil_pk(instance.file_document, None),
            file_document_unicode=nil_new_unicode(instance.file_document, ""),
            current_value=float(instance.current_value or 0),
            last_value=float(instance.last_value or 0),
            refperiod_property=nil_pk(instance.refperiod_property, None),
            refperiod_property_unicode=nil_new_unicode(instance.refperiod_property, ""),
        )

        return rst
