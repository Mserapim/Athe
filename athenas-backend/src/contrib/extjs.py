# -*- coding: utf-8 -*-
import codecs
import datetime
import hashlib
import os
import re
import shutil
import threading
import time
import uuid
from functools import partial
from threading import Thread

from django import forms, template
from django.conf import settings
from django.db.models import BooleanField, CharField, Model
from django.db.models.query_utils import Q
from django.http import QueryDict
from localflavor.br import forms as brforms

import static
from auditoria.models import LineLog
from contrib import controller
from contrib.decorator import login_required
from contrib.helpers import get_default_controller_for_model
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, get_json_engine, getLogger

log = getLogger(__name__)


def timeout(timeout, method, args):
    log = getLogger(__name__)
    log.info([timeout, method, args])

    def _call(*args):
        time.sleep(timeout)
        method(*args)

    t = threading.Thread(target=_call, args=args)
    t.setDaemon(True)
    t.start()


def clean_format(self, value):
    """
    Remove formatção de texto.
    """
    value = self._clean(value)
    return re.sub(r"[-|\/|\.]", "", value)


def direct_clean_format(self, value):
    """ """
    return re.sub(r"[-|\/|\.]", "", value) if value else ""


brforms.BRCPFField._clean = brforms.BRCPFField.clean
brforms.BRCPFField.clean = clean_format
brforms.BRCNPJField._clean = brforms.BRCNPJField.clean
brforms.BRCNPJField.clean = clean_format
# brforms.BRPhoneNumberField._clean = brforms.BRPhoneNumberField.clean
# brforms.BRPhoneNumberField.clean  = clean_format

brforms.BRZipCodeField.clean = direct_clean_format

json = get_json_engine()

register_log = getLogger("register")

EXTJS_FIELDS_TRANSLATION = {}


def register_extractor_field(cls):
    def decorator(extractor):
        if cls not in EXTJS_FIELDS_TRANSLATION:
            EXTJS_FIELDS_TRANSLATION[cls] = extractor
        return extractor

    return decorator


def register_field(extractor):
    def decorator(cls):
        if cls not in EXTJS_FIELDS_TRANSLATION:
            EXTJS_FIELDS_TRANSLATION[cls] = extractor
        return cls

    return decorator


def extract_unknowfield(name, field, form):
    obj = {
        "xtype": "radio",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
    }

    register_log.info(
        "for %s input class not registred %s" % (name, str(field.__class__))
    )

    if isinstance(field.widget, forms.Textarea):
        obj.update(xtype="textarea")

    return obj


@register_extractor_field(forms.EmailField)
@register_extractor_field(forms.CharField)
def extract_charfield(name, field, form):
    obj = {
        "xtype": "textfield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
    }

    obj.update(value=getattr(form.instance, name, ""))

    if isinstance(field.widget, forms.Textarea):
        obj.update(xtype="ckeditor")
    elif isinstance(field.widget, forms.PasswordInput):
        obj.update({"value": "", "xtype": "passwordfield", "inputType": "password"})

    return obj


@register_extractor_field(forms.RegexField)
def extract_regexpfield(name, field, form):
    obj = extract_charfield(name, field, form)

    obj.update(
        {
            "regexp": field.regexp,
            "regexpText": getattr(field, "error_message", {}).get(
                "invalid", "Verfique o preenchimento do campo"
            ),
        }
    )

    return obj


@register_extractor_field(brforms.BRZipCodeField)
def extract_cepfield(name, field, form):
    obj = extract_charfield(name, field, form)
    obj.update(xtype="cepfield")

    return obj


@register_extractor_field(brforms.BRCPFField)
def extract_cpffield(name, field, form):
    obj = extract_charfield(name, field, form)
    obj.update(xtype="cpffield")

    return obj


@register_extractor_field(brforms.BRCNPJField)
def extract_cnpjfield(name, field, form):
    obj = extract_charfield(name, field, form)
    obj.update(xtype="cnpjfield")

    return obj


# @register_extractor_field(brforms.BRPhoneNumberField)
# def extract_phonenumberfield(name, field, form):
#     obj = extract_charfield(name, field, form)
#     obj.update(xtype = 'fonefield')

#     return obj


@register_extractor_field(forms.DateTimeField)
def extract_datetimefield(name, field, form):
    obj = {
        "xtype": "ndatetimefield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
    }

    dtf = DateUtils.default_datetime_format()
    obj.update(format=dtf.replace("%", ""))

    if hasattr(form.instance, name):
        value = getattr(form.instance, name, None)
        obj.update(
            value=DateUtils.datetime_to_str(value) if value is not None else None
        )

    return obj


@register_extractor_field(forms.DateField)
def extract_datefield(name, field, form):
    obj = {
        "xtype": "datefield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
    }

    dtf = DateUtils.default_date_format()
    obj.update(format=dtf.replace("%", ""))

    if hasattr(form.instance, name):
        value = getattr(form.instance, name, None)
        obj.update(value=DateUtils.date_to_str(value) if value is not None else None)

    return obj


@register_extractor_field(forms.ChoiceField)
@register_extractor_field(forms.TypedChoiceField)
def extract_choicefield(name, field, form):
    obj = {
        "xtype": "combo",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "hiddenName": name,
        "resizable": True,
        "store": [],
        "triggerAction": "all",
    }

    obj["store"] = [choice for choice in field.choices]
    obj.update(value=getattr(form.instance, name, ""))

    return obj


@register_extractor_field(forms.ModelChoiceField)
def extract_modelchoicefield(name, field, form):
    obj = {
        "xtype": "modelchoicefield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "hiddenName": name,
        "triggerAction": "all",
    }

    model = field.queryset.model
    if field.queryset.all().count() > 10:
        register_log.warn(
            "ModelChoiceField problem, field (%s) has many options to choose, we recommend using AutocompleteField."
            % name
        )

    store = [(row.pk, str(row)) for row in field.queryset.all()]
    obj.update(store=store)

    if hasattr(form.instance, name):
        e = getattr(form.instance, name)
        obj.update(value=e.pk if e is not None else None)

    return obj


@register_extractor_field(forms.ModelMultipleChoiceField)
def extract_modelmultichoicefield(name, field, form):
    obj = {
        "xtype": "multiselectbox",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "hiddenName": name,
        "name": name,
    }

    model = field.queryset.model

    obj.update(
        model={"name": str(model._meta.object_name), "pkg": str(model._meta.app_label)}
    )

    try:
        user = get_current_user()
    except Exception:
        register_log.warn(
            "Por favor ative o middleware contrib.middleware.ThreadLocals em seu settings.py"
        )
    else:
        can_add = "%s.add_%s" % (model._meta.app_label, model._meta.object_name.lower())
        can_edit = "%s.change_%s" % (
            model._meta.app_label,
            model._meta.object_name.lower(),
        )

        conf = {
            "canAdd": user.has_perm(can_add) or user.is_superuser,
            "canEdit": user.has_perm(can_edit) or user.is_superuser,
            "addLabel": field.addLabel if hasattr(field, "addLabel") else "Criar ...",
            "editLabel": (
                field.editLabel if hasattr(field, "editLabel") else "Modificar ..."
            ),
        }

        obj.update(conf=conf)

    ctl = get_default_controller_for_model(model, generic=False)
    if ctl is None:
        register_log.warn(
            "Não foi prossivel encontrar um controller para o modelo %s, se existir favor registrar."
            % model._meta.object_name
        )

        conf = {"canAdd": False, "canEdit": False}

        obj.update(conf=conf)

    else:
        obj.update(controller=ctl.controller)
        obj.update(displayField="description")
        obj.update(valueField="pk")

    if hasattr(form.instance, name):
        values = getattr(form.instance, name)
        obj.update(value=[(value.pk, str(value)) for value in values.all()])

    return obj


@register_extractor_field(forms.IntegerField)
def extract_numberfield(name, field, form):
    obj = {
        "xtype": "numberfield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
        "allowDecimals": False,
    }

    if hasattr(field, "min_value") and field.min_value is not None:
        obj.update(minValue=field.min_value)
    if hasattr(field, "max_value") and field.max_value is not None:
        obj.update(maxValue=field.max_value)

    obj.update(value=getattr(form.instance, name, ""))

    return obj


@register_extractor_field(forms.BooleanField)
def extract_booleanfield(name, field, form):
    obj = {
        "xtype": "checkbox",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
        "checked": getattr(form.instance, name, False),
    }

    return obj


@register_extractor_field(forms.DecimalField)
def extract_decimalfield(name, field, form):
    obj = {
        "xtype": "numberfield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "name": name,
        "allowDecimals": True,
    }

    obj.update(decimalPrecision=getattr(field, "decimal_places", 2))
    obj.update(
        maxLength=1
        + getattr(field, "max_digits", 0)
        + getattr(field, "decimal_places", 0)
    )

    if hasattr(field, "min_value") and field.min_value is not None:
        obj.update(minValue=field.min_value)
    if hasattr(field, "max_value") and field.max_value is not None:
        obj.update(maxValue=field.max_value)

    obj.update(value=str(getattr(form.instance, name, "")))

    return obj


class ExtWidget(controller.DefaultController):
    """
    Controller Widget básico baseado na ExtJS.
    """

    titles = {}

    def json(self, args=[]):
        """
        Responde com um JSON com a nova instância do Widget.
        :param args Argumentos repassados pela URL.
        """
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new Ext.pgj.widget.ExtWidget()")

    def get_title(self, args=[]):
        """
        Responde com um JSON com o título solicitado.
        :param args Argumentos repassados pela URL. É necessário passar um
        argumento com o valor da key.
        """
        key = args[0]
        obj = {}

        if key in self.titles:
            obj["title"] = self.titles[key]
        else:
            obj["title"] = "NOT_DEFINED"

        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def autocomplete(self, args=[]):
        """
        Responde com um JSON com o filtro do autocomplete desejado..
        :param args Argumentos repassados pela URL. É necessário passar um
        argumentos com o nome do modelo.
        """
        obj = {"result": []}

        buf = """
{% for app in apps %}try:
    from {{ app }}.models import *
except:
    self.log.warn("Nao foi importado '{{ app }}.models'")

{% endfor %}
mdl = {{ model }}"""

        tpl = template.engines["django"].from_string(buf)

        try:
            exec(tpl.render({"apps": settings.INSTALLED_APPS, "model": args[0]}))
        except Exception as e:
            self.log.exception(e)

        qs = []
        if "pk" in self.request.POST:
            qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
        else:
            for field in [f.name for f in mdl._meta.get_fields()]:
                if isinstance(getattr(mdl, field, None), CharField):
                    qs.append(Q(**{"%s__icontains": self.request.POST.get("query")}))

        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        if q is not None:
            for row in mdl.objects.filter(q):
                obj["result"].append(
                    {"pk": row.id, "id": row.id, "description": str(row)}
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class AbstractExtFormController(ExtWidget):

    @login_required(type="JSON")
    def action_form(self, args=[]):
        obj = {
            "xtype": "panel",
            "border": False,
            "autoHeight": True,
            "style": "padding:0.5em",
        }

        if (
            isinstance(self.Form, (forms.ModelForm, forms.models.ModelFormMetaclass))
            is True
        ):
            if args[0] == "NEW":
                form = self.Form()
            else:
                instance = self.Form.Meta.model.objects.get(pk=int(args[1]))
                form = self.Form(instance=instance)
        else:
            form = self.Form()
            form.instance = None

        if hasattr(self, "tabs_conf"):
            del obj["style"]
            obj.update(xtype="tabpanel")
            obj.update(activeTab=0)
            obj.update(items=self.__extract_tabform__(form))
        else:
            obj.update(layout="form")
            obj.update(defaults={"width": 375})
            obj.update(labelWidth=115)
            obj.update(items=self.__extract_form__(form))

        self.response["content-type"] = "text/javascript"
        import json

        self.response.write(json.dumps(obj, indent=4))

    def __extract_form__(self, form):
        items = []

        for name in form.fields:
            try:
                field = form.fields.get(name)
            except Exception:
                pass
            else:
                if field is not None:
                    items.append(self.__translate_field__(name, field, form))
                else:
                    self.log.info("Can't not found field with name %s" % name)

        return items

    def __extract_tabform__(self, form):
        items = []

        for tab in self.tabs_conf:
            panel = {
                "xtype": "panel",
                "layout": "form",
                "title": tab.get("title", "undefined"),
                "items": [],
                "labelWidth": 115,
                "autoHeight": True,
                "style": "padding:0.5em",
                "defaults": {"width": 375},
            }

            for name in tab.get("field", []):
                try:
                    field = form.fields.get(name)
                except Exception:
                    pass
                else:
                    if field is not None:
                        panel["items"].append(
                            self.__translate_field__(name, field, form)
                        )
                    else:
                        self.log.info("Can't not found field with name %s" % name)

            items.append(panel)

        return items

    def __translate_field__(self, name, field, form):
        handler = (
            extract_unknowfield
            if field.__class__ not in EXTJS_FIELDS_TRANSLATION
            else EXTJS_FIELDS_TRANSLATION[field.__class__]
        )
        return handler(name, field, form)


class ExtCrud(AbstractExtFormController):
    """
    Widget Crud baseado na ExtJS.
    """

    class Form(forms.ModelForm):
        class Meta:
            model = None

    titles = {
        "PANEL": "NOT_DEFINED_IN_CONTROLLER",
        "LIST": "NOT_DEFINED_IN_CONTROLLER",
        "INSERT": "NOT_DEFINED_IN_CONTROLLER",
        "UPDATE": "NOT_DEFINED_IN_CONTROLLER",
        "DELETE": "NOT_DEFINED_IN_CONTROLLER",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get(self, args=[]):
        code = {"result": []}

        try:
            obj = self.Form.Meta.model.objects.get(pk=int(self.request.POST["pk"]))

            code["result"].append({"pk": obj.pk, "id": obj.pk, "description": str(obj)})
        except Exception:
            pass

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(code))

    @login_required(type="JSON")
    def json(self, args=[]):
        """
        Responde com um JSON com a nova instância do Widget.
        :param args Argumentos repassados pela URL. É necessário passar um
        argumentos com o nome do controller.
        """
        self.log.info(self)
        searchable = hasattr(self.Form.Meta.model, "to_search")

        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'new toolkit.widget.ExtCrud("'
            + args[0]
            + '", '
            + json.encode(searchable)
            + ")"
        )

    def is_searchable(self, fieldname):
        model = self.Form.Meta.model
        flag = False

        if hasattr(model, "to_search") and fieldname is not None:
            for field in model.to_search:
                ts_name = field["name"].split("__")[0]
                if ts_name == fieldname:
                    flag = True
                    break

        return flag

    def _apply_to_search_for_columns_grid(self, columns):
        ncolumns = []

        for column in columns:
            if self.is_searchable(column.get("dataIndex", None)):
                column.update(toSearch=True)
            ncolumns.append(column)

        return ncolumns

    @login_required(type="JSON")
    def get_columns_grid(self, args=[]):
        """
        Responde com um JSON com um array de colunas para Grid.
        :param args Argumentos repassados pela URL. Não é necessário repassar
        argumentos.
        """
        model = self.Form.Meta.model

        obj = []

        conf = {
            "header": "Chave",
            "sortable": True,
            "dataIndex": "id",
            "toSearch": self.is_searchable("id"),
        }

        obj.append(conf)

        for f in [field.name for field in model._meta.get_fields()]:
            try:
                if f not in ["pk", "id"]:
                    ff = model._meta.get_field(f)
                    if f[len(f) - 3 :] == "_id":
                        f = f[0 : len(f) - 3]

                    conf = {
                        "sortable": True,
                        "dataIndex": ff.name,
                        "toSearch": self.is_searchable(ff.name),
                    }

                    if isinstance(
                        ff.verbose_name, str
                    ):  # or isinstance(ff.verbose_name, unicode):
                        conf["header"] = ff.verbose_name
                    # else:
                    #     conf["header"] = unicode(ff.verbose_name)

                    obj.append(conf)
            except Exception:
                pass

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_fields_filter(self, args=[]):
        obj = []
        model = self.Form.Meta.model

        from django.db.models.fields.related import RelatedField
        from django.db.models.fields import AutoField

        for fieldName in [f.name for f in model._meta.get_fields()]:
            try:
                field = model._meta.get_field(fieldName)
                if not isinstance(field, RelatedField) and not isinstance(
                    field, AutoField
                ):
                    item = {
                        "field": fieldName,
                        "handler": str(field.verbose_name),
                        "type": self.__field_to_type(field),
                    }

                    if len(field.choices) > 0:
                        item["type"] = "choices"
                        item["choices"] = field.choices

                    obj.append(item)
                elif isinstance(field, RelatedField):
                    if getattr(model, "filterInformation", False):
                        for info in model.filterInformation:
                            if info.field_real == fieldName:
                                obj.append(
                                    {
                                        "field": info.field_virtual,
                                        "handler": info.handle == ""
                                        and str(field.verbose_name)
                                        or info.handle,
                                        "type": info.type,
                                    }
                                )
            except Exception as e:
                self.log.exception(e)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode({"result": obj}))

    @login_required(type="JSON")
    def get_field_list(self, args=[]):
        """
        Responde com um JSON com um array de colunas para Store.
        :param args Argumentos repassados pela URL. Não é necessário repassar
        argumentos.
        """
        fields = list(self.get_fields().keys())

        obj = [{"name": "id", "type": "int"}, {"name": "__description__"}]

        for field in fields:
            if field != "id":
                if field[len(field) - 3 :] == "_id":
                    field = field[0 : len(field) - 3]
                obj.append(
                    {
                        "name": field,
                    }
                )

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def translate_to_query(self, info):
        try:
            field_info = self.Form.Meta.model._meta.get_field_by_name(info["field"])

            if isinstance(field_info[0], BooleanField):
                return "{0}{1} = {2}".format(
                    str(info["field"]),
                    str(info["test"]),
                    True if info["keyword"] == "true" else False,
                )
            else:
                return "{0}{1} = '{2}'".format(
                    str(info["field"]), str(info["test"]), str(info["keyword"])
                )
        except Exception:
            return "{0}{1} = '{2}'".format(
                str(info["field"]), str(info["test"]), str(info["keyword"])
            )

    def detect_type_keyword(self):
        value = self.request.POST["keyword"]

        if re.match(r"^(-|)(\d+|(\d*(\.|,)\d+|\d+(\.|,)\d*))$", value):
            return "number"
        elif re.match(r"^\d{1,2}\/\d{1,2}\/\d{1,4}$", value):
            return "date"
        elif re.match(r"^\d{1,2}\/\d{1,2}\/\d{1,4} \d{1,2}:\d{1,2}$", value):
            return "date_time"
        else:
            return "text"

    def get_querys_for_type(self, type, keyword):
        try:
            if type == "text":
                return self.get_querys_for_text(keyword)
            elif type == "number":
                q1 = self.get_querys_for_number(keyword)
                q2 = self.get_querys_for_text(keyword)
                if q1 is not None:
                    return Q(q1 | q2)
                else:
                    return q2
            elif type == "date":
                return self.get_querys_for_date(keyword)
            elif type == "date_time":
                return self.get_querys_for_datetime(keyword)
        except Exception as e:
            self.log.exception(e)
            return None

    def get_fields_in_search(self):
        obj = []
        model = self.Form.Meta.model

        try:
            if "toSearch" in self.request.POST:
                for ts in model.to_search:
                    flag = False
                    for uts in self.request.POST.getlist("toSearch"):
                        if ts["name"].split("__")[0] == uts:
                            flag = True
                            break
                    if flag:
                        obj.append(ts)
            else:
                obj = model.to_search
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_querys_for_text(self, keyword):
        model = self.Form.Meta.model
        qs = []
        q = None

        for ts in self.get_fields_in_search():
            param = None

            if ts["type"] == "text":
                param = {ts["name"] + "__icontains": keyword}
            elif ts["type"] == "choices":
                field = model._meta.get_field(ts["name"])
                if field.choices is not None:
                    choices = [
                        choice[0]
                        for choice in field.choices
                        if re.match("^.*" + keyword.upper() + ".*$", choice[1].upper())
                    ]
                    param = {ts["name"] + "__in": choices}
            elif ts["type"] == "boolean":

                if (
                    "true" in ts and keyword.lower() == ts["true"]
                ) or keyword.lower() == "sim":
                    param = {ts["name"]: True}
                elif (
                    "false" in ts and keyword.lower() == ts["false"]
                ) or keyword.lower() == "não":
                    param = {ts["name"]: False}

            if param is not None:
                qs.append(Q(**param))

        for qN in qs:
            q = qN if q is None else Q(q | qN)

        return q

    def get_querys_for_number(self, keyword):
        qs = []

        try:
            if re.match(r"^\d+$", keyword):
                number = int(keyword)
            else:
                number = float(keyword)

            q = None

            for ts in self.get_fields_in_search():
                param = None

                if ts["type"] == "number":
                    param = {ts["name"]: number}

                if param is not None:
                    qs.append(Q(**param))

        except Exception:
            pass

        for qN in qs:
            q = qN if q is None else Q(q | qN)

        return q

    def get_querys_for_date(self, keyword):
        import time
        from datetime import date

        qs = []

        try:

            dt = date.fromtimestamp(time.mktime(time.strptime(keyword, "%d/%m/%Y")))
            q = None

            for ts in self.get_fields_in_search():
                param = None

                if ts["type"] == "date":
                    param = {ts["name"]: dt}

                if param is not None:
                    qs.append(Q(**param))

        except Exception as e:
            self.log.exception(e)

        for qN in qs:
            q = qN if q is None else Q(q | qN)

        return q

    def get_querys_for_datetime(self, keyword):
        import time
        from datetime import datetime

        qs = []

        try:

            dt = datetime.fromtimestamp(
                time.mktime(time.strptime(keyword, "%d/%m/%Y %H:%M"))
            )
            q = None

            for ts in self.get_fields_in_search():
                param = None

                if ts["type"] == "date_time":
                    param = {ts["name"]: dt}

                if param is not None:
                    qs.append(Q(**param))

        except Exception:
            pass

        for qN in qs:
            q = qN if q is None else Q(q | qN)

        return q

    def get_query(self):
        log.info("#EXTCRUD: %s" % self.__class__.__name__)
        filter = {}
        for k in self.request.POST:
            if re.match("^___", k):
                filter[re.sub("^___", "", k)] = self.request.POST.get(k)

        return self.Form.Meta.model.objects.filter(**filter)

    def get_query_filtred(self, paginator=True):
        try:
            pk = int(self.request.GET.get("pk") or 0)
        except ValueError:
            pk = 0

        query = self.get_query() if pk == 0 else self.get_query().filter(pk=pk)

        if "keyword" in self.request.POST and self.request.POST["keyword"] != "":
            type = self.detect_type_keyword()

            q = self.get_querys_for_type(type, self.request.POST["keyword"])

            if q is not None:
                query = query.filter(q) if q is not None else query
            else:
                query = query.filter(pk=-1)
        else:
            self.log.warn("Keyword not defined!")

        if "sort" in self.request.POST and "dir" in self.request.POST:
            if self.request.POST["dir"] == "DESC":
                sort = "-" + self.request.POST["sort"]
            else:
                sort = self.request.POST["sort"]
            query = query.order_by(sort)

        if paginator:
            pageInfo = self.get_page_info()

            return query.all()[
                pageInfo["start"] : pageInfo["start"] + pageInfo["limit"]
            ]
        else:
            return query

    def get_page_info(self):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        try:
            start = int(self.request.POST["start"])
            limit = int(self.request.POST["limit"])
        except Exception:
            start = 0
            limit = 50

        return {"start": start, "limit": limit}

    def get_total_rows(self):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        model = self.Form.Meta.model
        count = 0

        if "keyword" in self.request.POST:
            count = self.get_query_filtred(paginator=False).count()
        else:
            count = self.get_query().count()

        return count

    def __field_to_type(self, field):
        convention_types = {
            "text": ["CharField", "TextField", "SlugField"],
            "number": [
                "FloatField",
                "DecimalField",
                "SmallIntegerField",
                "PositiveSmallIntegerField",
                "PositiveIntegerField",
                "IntegerField",
            ],
            "boolean": ["BooleanField", "NullBooleanField"],
            "date": ["DateField", "DateTimeField", "TimeField"],
            "ip": ["IPAdressField"],
            "file": ["FilePathField", "FileField", "ImageField"],
        }

        type = None
        flag = False
        className = field.__class__.__name__

        for type in convention_types:
            if className in convention_types[type]:
                flag = True
                break
        if flag:
            return type
        else:
            return ""

    # Sobrescreva esse metodo no controller para adicionar ao dicionario de resultado os campos a
    # serem adicionados (Ex.: properties, functions ,etc)
    def get_fields(self):
        log.info("#EXTCRUD: %s" % self.__class__.__name__)
        return self.Form.Meta.model().__dict__

    def get_instance_controller(self, instance):
        for attr in instance._meta.get_fields():
            if isinstance(attr.model, self.Form.Meta.model):
                submodel = attr.model
                ctl = get_default_controller_for_model(submodel)
                if ctl is not None:
                    return ctl.controller
        return None

    def read_model_instance(self, instance):
        rst = {
            "pk": instance.pk,
            "__description__": str(instance),
            "description": str(instance),
            "controller": self.get_instance_controller(instance),
        }

        for field in list(self.get_fields().keys()):
            if field[-3:] == "_id":
                field = field[:-3]

            funcname = "get_%s_display" % field
            func = getattr(instance, funcname, None)
            value = getattr(instance, field)

            if func is not None:
                """get_FIELD_display of the django."""
                rst.update({field: func()})
            elif isinstance(value, datetime.datetime):
                """get formated date and time value."""
                rst.update({field: DateUtils.datetime_to_str(value)})
            elif isinstance(value, datetime.date):
                """get formated date value."""
                rst.update({field: DateUtils.date_to_str(value)})
            elif isinstance(value, bool):
                """get boolean value."""
                rst.update({field: value and "Sim" or "Não"})
            elif value is None:
                """get empty value."""
                rst.update({field: ""})
            elif isinstance(value, Model):
                """get model value."""
                rst.update({field: str(value), "%s__pk" % field: value.pk})
            else:
                """get unicode value of field."""
                rst.update({field: str(value)})

        return rst

    @login_required(type="JSON")
    def query(self, args=[]):
        """
        Metodo responsável por aplicar paginação no QuerySet retornado pelo metodo
        get_query_filtred e retorna um QuerySet.
        :return Retorna um QuerySet páginado de acordo com parametros repassado
        por POST.
        """
        result = {
            "result": [],
            "totalRows": self.get_total_rows(),
        }

        query = self.get_query_filtred()
        result.update(result=[self.read_model_instance(row) for row in query])

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(result))

    @login_required(type="JSON")
    def action_list(self, args=[]):

        conf = {"unique_id": args[0], "title": self.titles["LIST"]}

        tpl = self.load_static_template(
            filename=static.__path__[0] + "/html/action_list.html"
        )

        obj = {
            "html": tpl.render(conf),
            "num_row": 10,
            "last": 0,
            "active": 0,
        }

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def validate(self, args=[]):
        try:
            if args[0] == "NEW":
                frm = self.Form(self.request.POST)
            else:
                inst = self.Form.Meta.model.objects.get(pk=int(args[1]))
                frm = self.Form(self.request.POST, instance=inst)
        except Exception:
            frm = self.Form(self.request.POST)

        obj = {"result": False, "html": ""}

        if frm.is_valid():
            obj["result"] = True
        else:
            obj["errors"] = []
            for field in frm.errors:
                obj["errors"].append(
                    {"field": field, "description": str(frm.errors[field].as_text())}
                )

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def commit(self, args=[]):

        autorization = self.request.user.is_superuser
        model = self.Form.Meta.model

        actions_translate = {"NEW": "add", "EDIT": "change", "DELETE": "delete"}

        action_translate_number = {"NEW": 1, "EDIT": 2, "DELETE": 4}

        if not autorization:
            perm = "{package}.{action}_{model}".format(
                package=model._meta.app_label,
                model=model.__name__.lower(),
                action=actions_translate[args[0]],
            )
            autorization = self.request.user.has_perm(perm)

            self.log.info(
                "%s %s realizar %s"
                % (self.request.user, "pode" if autorization else "não pode", perm)
            )

        if autorization and self.request.user.is_active:

            linelog = LineLog()
            linelog.user = self.request.user
            linelog.level = action_translate_number[args[0]]
            linelog.read_request(self.request)
            linelog.status = 0

            if len(args) == 3:
                validate = bool(args[2] != 1)
            else:
                validate = True

            try:
                if args[0] == "NEW":
                    frm = self.Form(self.request.POST)
                else:
                    inst = self.Form.Meta.model.objects.get(pk=int(args[1]))
                    frm = self.Form(self.request.POST, instance=inst)

                obj = {
                    "result": False,
                    "html": "",
                    "validate": validate,
                }

                if frm.is_valid() or validate:
                    if args[0] == "NEW":
                        inst = self.Form.Meta.model()
                        frm = self.Form(self.request.POST, instance=inst)

                        try:
                            linelog.status = 1

                            linelog.json_description = {
                                "action": "NEW",
                                "new": {},
                                "post": dict(self.request.POST),
                                "get": dict(self.request.GET),
                            }

                            for field in inst._meta.fields:
                                linelog.json_description["new"][field.name] = (
                                    field.value_from_object(inst)
                                )

                            frm.save()
                            obj["cid"] = inst.pk
                            obj["cvalue"] = str(inst)
                            obj["result"] = True
                        except Exception as exception:
                            linelog.status = 0
                            linelog.json_description["message"] = str(exception)
                            obj["exception"] = "toolkit.exception.CrudSave"
                            obj["messageException"] = str(exception)
                    elif args[0] == "EDIT":
                        inst = self.Form.Meta.model.objects.get(pk=int(args[1]))

                        old = {}
                        for field in inst._meta.fields:
                            old[field.name] = field.value_from_object(inst)

                        frm = self.Form(self.request.POST, instance=inst)
                        try:
                            new = {}
                            for field in inst._meta.fields:
                                new[field.name] = field.value_from_object(inst)

                            linelog.json_description = {
                                "action": "EDIT",
                                "new": new,
                                "old": old,
                            }

                            frm.save()
                            obj["cid"] = inst.pk
                            obj["cvalue"] = str(inst)
                            linelog.status = 1

                            obj["result"] = True
                        except Exception as exception:
                            linelog.json_description["error"] = {
                                "type": exception.__class__.__name__,
                                "message": str(exception),
                            }
                            obj["exception"] = "toolkit.exception.CrudSave"
                            obj["messageException"] = str(exception)
                    elif args[0] == "DELETE":
                        inst = self.Form.Meta.model.objects.get(pk=int(args[1]))

                        old = {}
                        for field in inst._meta.fields:
                            old[field.name] = field.value_from_object(inst)

                        frm = self.Form(self.request.POST, instance=inst)

                        try:
                            linelog.json_description = {"action": "DELETE", "old": old}

                            inst.delete()
                            linelog.status = 1

                            obj["result"] = True
                        except Exception as exception:
                            linelog.json_description["error"] = {
                                "type": exception.__class__.__name__,
                                "message": str(exception),
                            }
                            obj["exception"] = "toolkit.exception.CrudDelete"
                            obj["messageException"] = str(exception)
            except Exception:
                obj = {
                    "result": False,
                    "exception": "toolkit.exception.Bug",
                    "messageException": "Ocorreu um erro processando a operação. Contacte a equipe de desenvolvimento para reportar o erro.",
                }

            try:
                linelog.save()
            except Exception as e:
                self.log.exception(e)
        else:
            obj = {"result": False, "exception": "toolkit.exception.Permission"}

            linelog = LineLog()
            linelog.user = self.request.user
            linelog.level = 0
            linelog.status = 0
            linelog.read_request(self.request)

            try:
                linelog.save()
            except Exception as e:
                self.log.exception(e)

            if not self.request.user.is_active:
                obj["messageException"] = (
                    "O usuário não está ativo, devido a isto não é possível alterar dados."
                )
            else:
                obj["messageException"] = "Você não tem permissão para esta ação."

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_filters(self, args=[]):
        buf = """new toolkit.plugins.GridFilters({filters: [{% for field in fields %}{ dataIndex: '{{ field.name }}', type: '{{ field.type }}'}{% if not forloop.last %},{% endif %}{% endfor %}})"""
        tpl = template.engines["django"].from_string(buf)

        meta = self.Form.Meta.model._meta
        fields = []
        for field in [f.name for f in meta.get_fields()]:
            try:
                fields.append({"name": field, "type": "string"})
            except Exception:
                pass

        self.response["content-type"] = "text/javascript"
        self.response.write(tpl.render({"fields": fields}))


class ExtConfigurableButtonsCrud(ExtCrud):

    MODE = {
        "crud": {"insert": True, "edit": True, "delete": True, "view": False},
        "view": {"insert": False, "edit": False, "delete": False, "view": True},
        "editor": {"insert": False, "edit": True, "delete": False, "view": False},
    }

    mode = MODE["crud"]

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"

        searchable = hasattr(self.Form.Meta.model, "to_search")

        self.response.write(
            "new toolkit.widget.ExtConfigurableButtonsCrud('%s', %s)"
            % (args[0], json.encode(searchable))
        )

    def buttons(self, args=[]):
        obj = self.mode
        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))


class ExtViewOnlyCrud(ExtConfigurableButtonsCrud):
    mode = ExtConfigurableButtonsCrud.MODE["view"]


class ExtEditorCrud(ExtConfigurableButtonsCrud):
    mode = ExtConfigurableButtonsCrud.MODE["editor"]


class ReportBuild(object):
    """
    Nome do datasouce do JASPER
    """

    datasource = settings.JASPER_DATASOURCE

    """
    Fonte do relatório
    """
    report_src = ""

    """
    Nome do arquivo que será gerado.
    """
    filename = "not_implemented.pdf"

    """
    Parâmetros default
    """
    params = [
        """
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "",
        }
        """
    ]

    """
    Formulario para ser utilziado como filtro.
    """

    class Form(forms.Form):
        pass

    class Command(Thread):
        def __init__(self, session, command, log, xmlfile):
            Thread.__init__(self)

            self.session = session
            self.command = command
            self.log = log
            self.xmlfile = xmlfile

        def run(self):
            try:
                self.session.status = os.system(self.command)
                self.session.store()
            except Exception as e:
                self.log.exception(e)
            finally:
                if os.path.exists(self.xmlfile):
                    os.unlink(self.xmlfile)

    class Session:

        TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        class Status:
            SUCCESS = 0
            JASPER_NOT_FOUND = 1
            NOT_FOUND_DB = 2
            UKNOW_ERROR = 3
            DB_NOT_CONECTED = 4
            SRC_NOT_CONECTED = 5
            OPENED = 6
            WAITING = 7
            UKNOW = 8
            NOT_FOUND = 9
            SESSION_EXPIRED = 10
            SESSION_NOT_FOUND = 11
            STARTED = 12
            JAR_NOT_FOUND = 256
            COMMAND_NOT_FOUND = 32512

        def __init__(self, **kargs):
            self.sid = (
                "sid" in kargs
                and kargs["sid"]
                or hashlib.new("md5", os.urandom(64)).hexdigest()
            )
            self.expire_date = (
                "expire_date" in kargs
                and kargs["expire_date"]
                or datetime.datetime.now() + datetime.timedelta(seconds=320)
            )

            if "status" in kargs:
                self.status = kargs["status"]
            else:
                self.status = self.Status.OPENED

            self.report = "report" in kargs and kargs["report"] or ""
            self.log = getLogger("ReportBuild.Session")

        def __str__(self):
            obj = {"sid": self.sid, "expire_date": str(self.expire_date)}

            return json.encode(obj)

        # def __unicode__(self):
        #     return unicode(self.__str__())

        @classmethod
        def get_xml_filepath(cls, sid=None):
            return os.path.join(
                getattr(settings, "JASPER_TMP", "/tmp"), "-".join(["xml", sid])
            )

        @classmethod
        def get_rb_filepath(cls, sid=None):
            return os.path.join(
                getattr(settings, "JASPER_TMP", "/tmp"), "-".join(["rb", sid])
            )

        @classmethod
        def get_sid_filepath(cls, sid=None):
            return os.path.join(
                getattr(settings, "JASPER_TMP", "/tmp"), "-".join(["sid", sid])
            )

        @classmethod
        def load(cls, sid):
            """ """
            f = open(cls.get_sid_filepath(sid), "r")
            buf = f.read()
            obj = json.decode(buf)
            f.close()

            tm = time.strptime(obj["expire_date"], cls.TIME_FORMAT)

            rb = ReportBuild.Session(
                sid=obj["sid"],
                expire_date=datetime.datetime(
                    year=tm.tm_year,
                    month=tm.tm_mon,
                    day=tm.tm_mday,
                    hour=tm.tm_hour,
                    minute=tm.tm_min,
                    second=tm.tm_sec,
                ),
                status=obj["status"],
                report=obj["report"],
            )

            return rb

        def destroy(self):
            log = getLogger(__name__)
            xmlfile = self.get_xml_filepath(self.sid)
            rbfile = self.get_rb_filepath(self.sid)
            sidfile = self.get_sid_filepath(self.sid)
            log = self.log

            def handler(filepath):
                log.debug(filepath)
                try:
                    os.path.exists(filepath) and os.unlink(filepath)
                except Exception as e:
                    log.exception(e)

            timeout(5, handler, [xmlfile])
            timeout(10, handler, [sidfile])
            timeout(15, handler, [rbfile])

        def store(self):
            """ """
            try:
                f = open(self.get_sid_filepath(self.sid), "w+")
                f.write(
                    json.encode(
                        {
                            "sid": self.sid,
                            "expire_date": self.expire_date.strftime(self.TIME_FORMAT),
                            "status": self.status,
                            "report": self.report,
                        }
                    )
                )
                f.close()
            except Exception as e:
                self.log.exception(e)

    def __init__(self, *args, **kargs):
        self.add_fields = {}

    def get_generated_filename(self):
        return self.filename

    @login_required(type="JSON")
    def create_session(self, args=[]):
        """
        Cria a sessão para iniciar o processo de construção do relatório
        """
        session = self.Session()
        session.store()

        self.response["content-type"] = "text/javascript"
        self.response.write(session)

    def is_expired(self, session):
        return datetime.datetime.now() > session.expire_date

    def _get_session(self, sid):
        session = self.Session.load(sid)

        if self.is_expired(session):
            session.status = session.Status.SESSION_EXPIRED

        return session

    @login_required(type="JSON")
    def get_status_session(self, args=[]):
        """
        Checa o status da sessão de geração de relatório.
        """
        obj = {"status": self.Session.Status.UKNOW, "message": ""}

        try:
            session = self._get_session(self.request.POST["sid"])
            obj["status"] = session.status
        except Exception as e:
            obj["message"] = "Não consegui resgatar a sessão."
            obj["status"] = self.Session.Status.SESSION_NOT_FOUND
            obj["e"] = str(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="BUFFER")
    def download(self, args=[]):
        session = self._get_session(args[0])

        self.response["Content-Type"] = "application/pdf"
        self.response["Content-Length"] = os.path.getsize(session.report)
        self.response["Content-Disposition"] = (
            "attachment; filename=" + self.get_generated_filename()
        )

        with open(session.report, "r") as fd:
            for chunk in iter(partial(fd.read, 8192), b""):
                self.response.write(chunk)

        session.destroy()

    @login_required(type="JSON")
    def run_report(self, args=[]):
        """
        Inicia a geração do relatório, necessita de um sessão aberta.
        """
        obj = {"status": self.Session.Status.UKNOW, "message": ""}

        try:
            session = self._get_session(args[0])

            tmpfile = session.get_rb_filepath(session.sid)
            xmlfile = session.get_xml_filepath(session.sid)

            buffer = "<parametros>\n"
            parametros = []
            for par in self.params:
                buffer += "\t<item><nome>{0}</nome><tipo>{1}</tipo><valor>{2}</valor></item>\n".format(
                    par["nome"],
                    par["tipo"],
                    par["valor"],
                )
                parametros.append(par["nome"])

            for name in self.request.POST:
                if (
                    name in self.Form.__dict__["base_fields"]
                    and (name not in parametros)
                    and (name not in self.add_fields)
                ):
                    field = (
                        self.Form.__dict__["base_fields"][name]
                        if name in self.Form.__dict__["base_fields"]
                        else name
                    )

                    if len(self.request.POST.getlist(name)) == 1 and not isinstance(
                        field, forms.ModelMultipleChoiceField
                    ):
                        buffer += "\t<item><nome>{0}</nome><valor>{1}</valor><tipo/></item>\n".format(
                            name,
                            self.request.POST[name],
                        )
                    else:
                        if name in self.request.POST:
                            self.log.debug("POST: %s" % self.request.POST)
                            self.log.debug(
                                "REPORT %s: %s > QueryDict: %s"
                                % (
                                    name,
                                    self.request.POST[name],
                                    isinstance(self.request.POST[name], QueryDict),
                                )
                            )

                        buffer += '\t<itemset nome="{0}">\n'.format(name)
                        list_ = self.request.POST.getlist(name)
                        for item in list_:
                            buffer += "\t\t<item><valor>{0}</valor></item>\n".format(
                                item,
                            )
                        buffer += "\t</itemset>\n"

            for name in self.add_fields:

                if not isinstance(self.add_fields.get(name, None), list):
                    buffer += "\t<item><nome>{0}</nome><valor>{1}</valor><tipo/></item>\n".format(
                        name,
                        self.add_fields[name],
                    )
                else:
                    buffer += '\t<itemset nome="{0}">\n'.format(name)
                    for item in self.add_fields[name]:
                        buffer += "\t\t<item><valor>{0}</valor></item>\n".format(
                            item,
                        )
                    buffer += "\t</itemset>\n"
            buffer += "</parametros>"

            xml = codecs.open(xmlfile, "w+", "utf-8")
            xml.write(buffer)
            xml.close()

            session.report = tmpfile
            command = (
                "%(java_home)s/bin/java %(java_options)s -Duser.dir=%(jasper_home)s -jar '%(jasper_builder)s' '%(datasource)s' '%(report)s.jasper' '%(output)s' '%(xml_parametro)s'"
                % {
                    "java_home": getattr(settings, "JAVA_HOME"),
                    "java_options": getattr(settings, "JAVA_OPTIONS", ""),
                    "jasper_home": getattr(settings, "JASPER_HOME"),
                    "jasper_builder": getattr(settings, "JASPER_BUILDER"),
                    "datasource": self.datasource,
                    "report": self.report_src,
                    "output": tmpfile,
                    "xml_parametro": xmlfile,
                }
            )
            session.status = session.Status.STARTED
            session.store()
            obj["status"] = session.status

            self.log.debug(command)

            cmd = self.Command(
                session=session, command=command, log=self.log, xmlfile=xmlfile
            )
            cmd.start()

        except Exception as e:
            obj["message"] = "Não consegui resgatar a sessão."
            obj["e"] = str(e)
            self.log.exception(e)

        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def destroy_session(self, args=[]):
        """
        Destroi a sessão de geração de relatórios, geralmente invocada
        quando o status de sucesso ou de insucesso ocorrer.
        """


class ExtReportBuild(AbstractExtFormController, ReportBuild):

    def fix_date_and_datetime(self, qdict):
        qd = QueryDict("", mutable=True)

        for key in list(qdict.keys()):
            for value in qdict.getlist(key):
                treated = value
                try:
                    if isinstance(self.Form.base_fields[key], forms.DateField):
                        treated = DateUtils.str_to_date(value).strftime("%Y-%m-%d")
                    elif isinstance(self.Form.base_fields[key], forms.DateTimeField):
                        treated = DateUtils.str_to_date(value).strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    else:
                        self.log.info("%s not is DateField or DateTimeField", key)
                except Exception:
                    log.warn("key %s not in form of %s", key, self.__class__)
                finally:
                    log.debug("%s <- %s", key, treated)
                    qd.update({key: treated})

        return qd

    def __init__(self, *args, **kargs):
        AbstractExtFormController.__init__(self, *args, **kargs)
        ReportBuild.__init__(self)

        # FIXME: Esta sendo removido desta forma devida a dificuldade de se resolver o formato no lado do gerador de relatórios
        self.request.POST = self.fix_date_and_datetime(self.request.POST)
        self.request.GET = self.fix_date_and_datetime(self.request.GET)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            """new toolkit.widget.ExtReportBuild("{0}", "{1}")""".format(
                args[0], self.report_src
            )
        )


class ExtFileBuild(AbstractExtFormController):

    titles = {"TITLE": "Exportar arquivo", "SUB_TITLE": "Exportar arquivo do modelo"}

    mimetype = "text/plain"
    generate_file = "default.txt"
    encoding_out = "utf-8"
    _tmp_dir = "tmp"

    def __init__(self, *args, **kargs):
        log.debug("INIT ExtFileBuild")
        super(ExtFileBuild, self).__init__(*args, **kargs)
        self.uuid = uuid.uuid1().hex

    class Form(forms.Form):
        pass

    def get_generate_filename(self):
        return self.generate_file

    @property
    def generated_filename(self):
        return self.generate_file

    def builder_buffer(self):
        return "Método builder não foi implementado"

    def len_buffer(self, buffer):
        return len(buffer)

    @login_required(type="BUFFER")
    def builder(self, args=[]):
        buffer = self.builder_buffer()

        self.response["Content-Type"] = self.mimetype
        self.response["Content-Length"] = self.len_buffer(buffer)
        # self.response['Content-Length']      = len(buffer)
        self.response["Content-Disposition"] = (
            "attachment; filename=" + self.get_generate_filename()
        )

        self.response.write(buffer)

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            """new toolkit.widget.ExtFileBuild("{0}")""".format(args[0])
        )

    @property
    def tmp_dir(self):
        return os.path.join(settings.UPLOAD_STORE_DIR, self._tmp_dir, self.uuid)

    def create_file(self, file_path, objs=[], xml=False):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        if xml:
            objs.write(file_path, encoding=self.encoding_out, xml_declaration=True)
        else:
            with codecs.open(file_path, "w", self.encoding_out) as fd:
                try:
                    iter(objs)
                except TypeError:
                    fd.write(str(objs))
                else:
                    fd.writelines(objs)

        return file_path

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def clear_tmpdir(self):
        shutil.rmtree(self.tmp_dir)
