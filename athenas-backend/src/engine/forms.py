# -*- coding: utf-8 -*-
from contrib.extjs import register_extractor_field, extract_choicefield
from django import forms
from engine import static

import os
import re


class IconField(forms.ChoiceField):

    def __init__(self, *args, **kargs):
        icon_dir = "%s/images/icons" % static.__path__[0]
        choices = [
            (filename, filename)
            for filename in os.listdir(icon_dir)
            if re.match(r"^.*\.(jpg|jpeg|png|gif)$", filename)
        ]
        choices.insert(0, (None, "Sem icone"))
        kargs["choices"] = choices
        forms.ChoiceField.__init__(self, *args, **kargs)


@register_extractor_field(IconField)
def extractor_iconfield(name, field, form):
    obj = {
        "xtype": "iconfield",
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "hiddenName": name,
        "dataStore": [choice for choice in field.choices],
        "triggerAction": "all",
        "mode": "local",
    }

    obj.update(value=getattr(form.instance, name, ""))

    return obj
