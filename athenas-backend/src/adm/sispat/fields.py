# -*- coding: utf-8 -*-
import json

import pymssql
from contrib.controller import DefaultController
from contrib.extjs import register_extractor_field
from contrib.utils import getLogger
from django.conf import settings
from django.forms import Field
from django.template.defaultfilters import slugify

log = getLogger(__name__)


class MSSQLAutocompleteController(DefaultController):

    def query(self, args=[]):
        obj = {}
        slug = args[0]

        cur = MSSQLAutocompleteField.get_connection(slug).cursor()
        sqlcommand = MSSQLAutocompleteField.get_sql_command(slug)
        sqlcommand = sqlcommand % {"query": self.request.REQUEST.get("query")}
        cur.execute(sqlcommand)

        obj.update(
            collection=[
                {"pk": pk, "description": description.decode("iso-8859-1")}
                for pk, description in cur.fetchall()
            ]
        )
        obj.update(count=len(obj.get("collection", [])))

        self.response.write(json.dumps(obj))


class MSSQLAutocompleteField(Field):
    """
    slug: sqlcommand
    """

    __sqls = {}

    class SQLCommandAlreadyRegistred(Exception):

        def __init__(self):
            """ """
            self.message = "Comando com este slug já esta registrado"

    @classmethod
    def get_connection(class_, slug):
        db_conf = getattr(settings, "MSSQL_DATABASE", {})
        conf = class_.__sqls.get(slug, {})
        connector_name = conf.get("connector", "undefined")

        return pymssql.connect(**db_conf.get(connector_name, {}))

    @classmethod
    def get_sql_command(class_, slug):
        conf = class_.__sqls.get(slug, {})
        return conf.get("command", "")

    @classmethod
    def register(class_, slug, sqlcommand, connector="default"):
        """ """
        if slugify(slug) not in list(class_.__sqls.keys()):
            class_.__sqls.update(
                {slugify(slug): {"command": sqlcommand, "connector": connector}}
            )
        else:
            raise class_.SQLCommandAlreadyRegistred()

    def __init__(self, slug, *args, **kargs):
        """ """
        Field.__init__(self, *args, **kargs)
        self.slug = slug


@register_extractor_field(MSSQLAutocompleteField)
def extract_mssql_autocomplete_field(name, field, form):
    obj = {
        "xtype": "mssql-autocompletefield",
        "hiddenName": name,
        "fieldLabel": name if field.label is None else field.label,
        "dataUrl": "%(context)s/MSSQLAutocompleteController/query/%(slug)s"
        % {
            "context": (
                ""
                if hasattr(settings, "CONTEXT") is False
                else "/" + getattr(settings, "CONTEXT")
            ),
            "slug": field.slug,
        },
        "displayField": "description",
        "valueField": "pk",
    }

    return obj
