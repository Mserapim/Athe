# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.forms import (
    ModelChoiceField,
    ModelMultipleChoiceField,
    SelectMultiple,
    TextInput,
)

try:
    from django.db.models.fields.related import ReverseOneToOneDescriptor
except ImportError:
    from django.db.models.fields.related import (
        SingleRelatedObjectDescriptor as ReverseOneToOneDescriptor,
    )

from django.template import Template, Context
from contrib.utils import getLogger
from contrib.helpers import get_controller_for_model, get_default_controller_for_model
from standard.models import Configuration, Item
from contrib.extjs import register_extractor_field
from contrib.middleware import get_current_user
from django.conf import settings

import static

from contrib.extjs import ExtCrud
from django import forms


class STDItem(ExtCrud):
    titles = {
        "PANEL": "Item",
        "LIST": "Itens de Configurações",
        "NEW": "Novo item de configuração",
        "EDIT": "Editando um item de configuração",
        "DELETE": "Deletando um item de configuração",
    }

    class Form(forms.ModelForm):

        class Meta:
            exclude = []
            model = Item


class STDConfiguration(ExtCrud):
    titles = {
        "PANEL": "Configurações",
        "LIST": "Grupos de Configurações",
        "NEW": "Novo grupo de configuração",
        "EDIT": "Editando um grupo de configuração",
        "DELETE": "Deletando um grupo de configuração",
    }

    class Form(forms.ModelForm):

        class Meta:
            exclude = []
            model = Configuration


class AutoCompleteField(ModelChoiceField):

    def __init__(
        self,
        father=None,
        model=None,
        controller=None,
        queryAction="query",
        queryKeyword="keyword",
        display_field="description",
        value_field="pk",
        *args,
        **kargs
    ):
        self.log = getLogger(AutoCompleteField.__name__)
        if controller is not None:
            super(AutoCompleteField, self).__init__(
                queryset=model.objects,
                widget=AutoCompleteInput(
                    model=model, father=father, controller=controller
                ),
                *args,
                **kargs
            )
        else:
            super(AutoCompleteField, self).__init__(
                queryset=model.objects,
                widget=AutoCompleteInput(model=model, father=father),
                *args,
                **kargs
            )

        self.model = model
        self.father = father
        self.queryAction = queryAction
        self.queryKeyword = queryKeyword
        self.value_field = value_field
        self.display_field = display_field

        if not controller is None:
            self.controller = controller

    def xtype(self):
        return "autocomplete"

    def xtype_config(self, dict):
        dict["cls"] = "autocomplete"
        dict["tpl"] = (
            """new Ext.XTemplate('<tpl for="."><div class="search-item"><p>{description}</p></div></tpl>')"""
        )
        dict["store"] = (
            "new Ext.data.Store({{url: '/{context}/{father}/autocomplete/{model}/',{render} }})".format(
                context=settings.CONTEXT,
                father=self.father,
                model=self.model.__name__,
                render="""reader: new Ext.data.JsonReader({root: 'result',id: 'id'},[{name: 'description',mapping: 'description'},{name: 'id',mapping: 'id'}])""",
            )
        )
        if "controller" in dir(self):
            dict["controller"] = self.controller.__name__
        return dict


class AutoCompleteInput(TextInput):

    def __init__(self, *args, **kargs):
        self.log = getLogger(AutoCompleteInput.__name__)
        self.attrs = kargs.get("attrs", {})
        self.model = kargs.get("model")
        self.father = kargs.get("father")

        if "controller" in kargs:
            self.add = True
            self.controller = kargs["controller"]
        else:
            self.add = False

    def get_string_value(self, pk):
        row = self.model.objects.get(pk=pk)
        return str(row)


@register_extractor_field(AutoCompleteField)
def extractor_autocompletefield(name, field, form):
    obj = {
        "xtype": "autocompletefield",
        "hiddenName": name,
        "fieldLabel": str(field.label) if field.label is not None else str(name),
        "allowBlank": not field.required,
        "hideTrigger": True,
        "queryParam": getattr(field, "queryKeyword", "keyword"),
        "queryAction": getattr(field, "queryAction", "query"),
        "triggerAction": "all",
    }

    if hasattr(field, "father"):
        ctl = field.father
        if isinstance(ctl, str):
            obj.update(father=ctl)
        elif ctl is not None:
            obj.update(father=ctl.decode())

    if hasattr(field, "model"):
        obj.update(model=field.model._meta.object_name)

    if hasattr(form.instance, name):
        value = getattr(form.instance, name, None)
        obj.update(value=value.pk if value is not None else None)

    model = field.queryset.model
    log = getLogger()

    for attr in dir(model):
        if (
            hasattr(model, attr)
            and isinstance(getattr(model, attr), ReverseOneToOneDescriptor)
            and issubclass(getattr(model, attr).related.model, model)
        ):
            submodel = getattr(model, attr).related.model
            ctl = get_default_controller_for_model(submodel, generic=False)

            if (
                submodel.__class__ is not model.__class__
                and ctl is not None
                and ctl.controller != "ExtCrudGeneric"
            ):
                if not "subcontrollers" in obj:
                    obj["subcontrollers"] = []

                obj["subcontrollers"].append(
                    {"title": ctl.title, "controller": ctl.controller, "icon": ctl.icon}
                )

    try:
        user = get_current_user()
    except:
        log.warn(
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
                field.editLabel
                if hasattr(field, "editLabel")
                else "Visualizar registro ..."
            ),
        }

        obj.update(conf=conf)

    ctl = get_default_controller_for_model(model, generic=False)
    if ctl is not None:
        if "subcontrollers" in obj:
            obj["subcontrollers"].insert(
                0, {"title": ctl.title, "controller": ctl.controller, "icon": ctl.icon}
            )

        obj.update(
            {
                "crudController": ctl.controller,
                "queryAction": field.queryAction,
                "displayField": (
                    "description"
                    if field.display_field is None
                    else field.display_field
                ),
                "valueField": "pk" if field.value_field is None else field.value_field,
            }
        )
    else:
        obj.update(
            {
                "genericCrud": True,
                "model": {
                    "app_label": model._meta.app_label,
                    "name": model._meta.object_name.lower(),
                },
                "conf": {"canAdd": False, "canEdit": False},
                "displayField": (
                    "description"
                    if field.display_field is None
                    else field.display_field
                ),
                "valueField": "pk" if field.value_field is None else field.value_field,
            }
        )

        log.warn("Nenhum ExtCrud foi registrado para o campo %s." % (name,))

    return obj


class ExtCrudGeneric(ExtCrud):

    class Form(forms.ModelForm):

        class Meta:
            model = None

    def __init__(self, *args, **kargs):
        super(ExtCrudGeneric, self).__init__(*args, **kargs)
        qset = (
            self.request.REQUEST
        )  # self.request.POST if self.request.method == 'POST' else self.request.GET
        self.log.debug(qset)

        try:
            ct = ContentType.objects.get(
                app_label=qset.get("model_app_label", "").lower(),
                model=qset.get("model_name", "").lower(),
            )
        except Exception as e:
            self.log.info(qset)
            self.log.exception(e)
        else:
            self.Form.Meta.model = ct.model_class()
