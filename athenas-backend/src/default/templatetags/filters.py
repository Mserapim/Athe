# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import DateTimeField

# from django.forms import *
from django.forms.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    DateField,
    DecimalField,
    EmailField,
    FloatField,
    IntegerField,
    RegexField,
    SlugField,
    TimeField,
    TypedChoiceField,
    URLField,
)

# from django.forms.models import *
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField

# from django.forms.widgets import *
from django.forms.widgets import Textarea
from django.template import Library, engines

# from localflavor.br.forms import *
from localflavor.br.forms import BRCNPJField, BRZipCodeField
from localflavor.br.models import BRCPFField

import static
from contrib.utils import get_json_engine, getLogger

# from engine.forms import *
from engine.models import ControllerContentType

# from ged.forms import *
# from standard.views import *

json = get_json_engine()


register = Library()


@register.filter()
def value(form, field):
    log = getLogger("filters")
    name = ""
    value = ""

    if "name" in dir(field):
        f = field.field
        name = field.name
    else:
        f = form.fields.get(field)
        name = field

    try:
        if form.instance.pk is not None:
            # if isinstance(f, ModelMultipleChoiceField) or isinstance(f, ModelMultipleChoiceFieldCustom):
            if isinstance(f, ModelMultipleChoiceField):
                value = []
                mvalue = getattr(form.instance, name, None)
                if mvalue is not None:
                    for row in mvalue.all():
                        value.append([row.pk, str(row)])
            elif isinstance(f, DateField):
                # from datetime import *
                info = getattr(form.instance, name, "")
                value = str(info.strftime("%Y-%m-%d"))
            elif isinstance(f, DateTimeField):
                # from datetime import *
                info = getattr(form.instance, name, "")
                value = str(info.strftime("%Y-%m-%d %H:%M:%S"))
            elif isinstance(f, ModelChoiceField):
                value = str(getattr(form.instance, name, "")), getattr(
                    form.instance, name + "_id", ""
                )
            else:
                value = str(getattr(form.instance, name, ""))
        else:
            try:
                value = str(form.data[field])
            except Exception:
                value = ""

        # log.debug("{0} = {1}".format(name, value))

        if value is not None:
            return value
        else:
            return ""
    except Exception as e:
        log.exception(e)
        return ""


@register.filter()
def extType(field):

    map = {
        BRCPFField: "cpffield",
        BRCNPJField: "cnpjfield",
        BRZipCodeField: "cepfield",
        # BRPhoneNumberField: "fonefield",
        CharField: "textfield",
        SlugField: "textfield",
        IPAddressField: "textfield",
        FileUploadField: "ged-fileuploadfield",
        TypedFileUploadField: "ged-typedfileuploadfield",
        ImageUploadField: "ged-imageuploadfield",
        EmailField: "textfield",
        URLField: "textfield",
        RegexField: "textfield",
        BooleanField: "checkbox",
        # NullBooleanField: "checkbox",
        DateField: "datefield",
        DateTimeField: "datetimefield",
        FloatField: "numberfield",
        DecimalField: "numberfield",
        IntegerField: "numberfield",
        TimeField: "timefield",
        ModelMultipleChoiceField: "multiselectbox",
        # ModelMultipleChoiceFieldCustom: "multiselectboxcustom",
        ModelChoiceField: "combobox",
        ChoiceField: "combobox",
        IconField: "iconfield",
        TypedChoiceField: "combobox",
    }

    log = getLogger("filters")
    log.debug(field.__class__)

    if field.__class__ in map:
        return map[field.__class__]
    elif "xtype" in dir(field):
        return field.xtype()
    else:
        return "radio"


@register.filter()
def toExtField(form, field):
    log = getLogger("filters")
    try:
        if isinstance(field, str):
            f = form.fields.get(field)
        else:
            f = field.field
            field = field.name

        xtype = extType(f)
        if "label" in dir(f):
            c = {"name": field, "label": f.label, "xtype": xtype}
        else:
            c = {"name": field, "label": "Desconhecido", "xtype": xtype}

        if "required" in dir(f):
            c["allowBlank"] = json.encode((not f.required))

        if value(form, field) != "":
            try:
                try:
                    c["value"] = json.encode(value(form, field))
                except Exception:
                    pass
            except Exception as e:
                log.exception(e)

        if c["xtype"] == "checkbox":
            try:
                log.debug(c)
                if "value" in c and c["value"] == '"True"':
                    c["checked"] = json.encode(True)
                    c.pop("value")
            except Exception:
                pass
        elif c["xtype"] == "textfield" and isinstance(f.widget, Textarea):
            c["xtype"] = "xhtmleditor"
            c["autoHeight"] = False
            c["height"] = 175
        elif c["xtype"] in ("combobox", "iconfield"):
            dataChoices = []
            for choice in f.choices:
                dataChoices.append(choice)

            log.debug(dataChoices)

            c["storeSimple"] = (
                """new Ext.data.SimpleStore({{fields: ['id', 'description'], data: {data}}})""".format(
                    data=json.encode(dataChoices)
                )
            )
        elif c["xtype"] == "multiselectbox":
            c["model"] = f.queryset.model.__name__
            c["package"] = f.queryset.model.__module__

            inf = {
                "app_label": f.queryset.model._meta.app_label,
                "name": f.queryset.model._meta.object_name.lower(),
            }

            try:
                ct = ContentType.objects.get(
                    app_label=inf["app_label"], model=inf["name"]
                )
                ctl = ControllerContentType.objects.filter(content_type=ct).order_by(
                    "id"
                )[0]
                c["controller"] = ctl.controller.controller
            except Exception:
                pass

            qset = []

            c["queryset"] = qset
        elif c["xtype"] in ["ged-typedfileuploadfield", "ged-imageuploadfield"]:
            c["types"] = f.types

        if "xtype_config" in dir(f):
            c = f.xtype_config(c)

        fd = open("{0}/js/template/toextfield.js".format(static.__path__[0]))
        buf = fd.read()
        fd.close()

        tpl = engines["django"].from_string(buf)
        buf = tpl.render(c)

        buf = buf.replace("u'", "'")

        return buf
    except Exception as e:
        log.debug("field: {0}".format(field))
        log.exception(e)
        return "/*{0}*/".format(e)
