# -*- coding: utf-8 -*-

from contrib.newrest import Restful
from contrib.nil import nil_datetime, nil_new_display, nil_pk, nil_new_unicode
from contrib.utils import DateUtils, getLogger
from rh.cif.models import ControlInformationMember, DebtsEncumbrances

log = getLogger(__name__)


class CifDebtsEncumbrances(Restful):

    _model = DebtsEncumbrances

    full_text_index = ("discipline__name__icontains",)

    def confirm_action(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            debts = self._model.objects.filter(pk__in=self.request.POST.getlist("pks"))
            for debt in debts:
                debt.refperiod_debts = debt.member.referenceperiod
                debt.status = 2
                debt.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def confirm_not_debts(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            control_information = ControlInformationMember.objects.get(
                pk=self.request.POST.get("pk_member")
            )

            if DebtsEncumbrances.objects.filter(
                member=control_information, code=None
            ).exists():
                raise Exception("Você já informou que não possui dívidas e ônus reais!")
            else:
                prop = DebtsEncumbrances(
                    member=control_information,
                    status=2,
                    current_value=0,
                    refperiod_debts=control_information.referenceperiod,
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
                raise Exception("O campo Código deve ser preenchido.")

        if "modified_by" in params:
            if params.get("modified_by") != "":
                field = getattr(self.Model, "modified_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(modified_by=query.get(pk=params.get("modified_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(modified_by=None)

        if "created_at" in params:
            if params.get("created_at") != "":
                params.update(
                    created_at=DateUtils.str_to_datetime(params.get("created_at"))
                )
            else:
                params.update(created_at=None)

        if "modified_at" in params:
            if params.get("modified_at") != "":
                params.update(
                    modified_at=DateUtils.str_to_datetime(params.get("modified_at"))
                )
            else:
                params.update(modified_at=None)

        if "created_by" in params:
            if params.get("created_by") != "":
                field = getattr(self.Model, "created_by")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(created_by=query.get(pk=params.get("created_by")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(created_by=None)

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
                params.update(member=None)

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

        if "refperiod_debts" in params:
            if params.get("refperiod_debts") != "":
                field = getattr(self.Model, "refperiod_debts")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        refperiod_debts=query.get(pk=params.get("refperiod_debts"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                raise Exception("Preencha o campo Período de Referência!")
                # params.update(refperiod_debts=None)

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
            kind=str(instance.kind),
            kind_display=nil_new_display(instance, "kind", ""),
            code=nil_pk(instance.code, None),
            code_unicode=nil_new_unicode(instance.code, ""),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=str(instance.modified_by) or None,
            # description=instance.description,
            description=(
                "%s" % instance.description
                if instance.validade_exists_debts()
                else "%s" % instance.text_not_debts
            ),
            status_pendency=nil_new_unicode(instance.status_pendency, ""),
            status_pendency_display=nil_new_display(instance, "status_pendency", ""),
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
            refperiod_debts=nil_pk(instance.refperiod_debts, None),
            refperiod_debts_unicode=nil_new_unicode(instance.refperiod_debts, ""),
        )

        return rst
