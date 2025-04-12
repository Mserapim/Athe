# -*- coding: utf-8 -*-
from contrib.utils import getLogger

log = getLogger(__name__)


def defaultfield(field, _type="string"):
    form = {
        "name": field.name,
        "fieldLabel": str(field.verbose_name),
        "xtype": "textfield",
        "allowBlank": field.blank,
    }

    fields = [{"name": field.name, "type": _type}]

    if field.choices:
        form.update(
            xtype="combo",
            hiddenName=field.name,
            triggerAction="all",
            mode="local",
            store=[choice for choice in field.choices],
            lazyRender=True,
        )

        fields.append({"name": "_".join([field.name, "display"]), "type": "string"})

    return {"form": form, "field": fields}


def replace_first_field(conf, key, value):
    data = conf.get(key, [])
    data = [value] + (data[1:] if len(data) > 1 else [])
    conf.update({key: data})


def charfield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    if form.get("xtype", "") != "combo":
        form.update(maxLength=field.max_length)

    return conf


def integerfield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    if form.get("xtype", "") != "combo":
        form.update(xtype="numberfield", allowDecimals=False)

    replace_first_field(
        conf, "field", {"name": field.name, "type": "int", "useNull": True}
    )

    return conf


def numberfield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    if form.get("xtype", "") != "combo":
        form.update(xtype="numberfield", allowDecimals=True, decimalPrecision=2)

    replace_first_field(
        conf, "field", {"name": field.name, "type": "float", "useNull": True}
    )

    return conf


def booleanfield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    form.update(boxLabel=form.get("fieldLabel"), xtype="checkbox", fieldLabel="")

    replace_first_field(conf, "field", {"name": field.name, "type": "bool"})

    return conf


def datefield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    form.update(xtype="datefield")

    replace_first_field(
        conf, "field", {"name": field.name, "type": "date", "dateFormat": "d/m/Y"}
    )

    return conf


def datetimefield(field):
    conf = defaultfield(field)

    form = conf.get("form")
    form.update(xtype="tk-datetimefield")

    replace_first_field(
        conf, "field", {"name": field.name, "type": "date", "dateFormat": "d/m/Y H:i"}
    )

    return conf


def foreignfield(field):
    conf = defaultfield(field)
    model = field.related_model

    form = conf.get("form")
    form.update(
        xtype="rest-autocompletefield",
        rest=".".join([model._meta.app_label, "%sRestful" % model._meta.model_name]),
    )

    conf.update(
        field=[
            {"name": field.name, "type": "int", "useNull": True},
            {"name": "_".join([field.name, "unicode"]), "type": "string"},
        ]
    )

    return conf
