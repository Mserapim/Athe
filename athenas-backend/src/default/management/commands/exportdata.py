# -*- coding: utf-8 -*-

import re
import codecs
import sys
import warnings

from django.core.management.base import BaseCommand
from django.db.models.query import QuerySet
from django.core import serializers

from contrib.utils import getLogger


log = getLogger(__name__)


class Command(BaseCommand):

    args = "<filtro para ser utilizado na exportação de dados.>"

    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument(dest="str_filter", default="", help="Query")

        parser.add_argument(
            "-o",
            "--outfile",
            dest="filepath",
            default=None,
            help="Arquivo de saida para a exportação, se null sai no stdout",
        )

        parser.add_argument(
            "-i",
            "--indent",
            dest="indent",
            default=0,
            help="Indentação para os dados exportados.",
        )

        parser.add_argument(
            "-n",
            "--with-natural-keys",
            dest="natural_key",
            action="store_true",
            default=False,
            help="Utilizar natural keys.",
        )

        parser.add_argument(
            "-p",
            "--use-primary-key",
            dest="use_pk",
            action="store_true",
            default=False,
            help="Dados exportados com primary key",
        )

        parser.add_argument(
            "-m",
            "--import-module",
            dest="import_module",
            help="Modulo necessário para executar o filtro",
        )

        parser.add_argument(
            "-s",
            "--set-fields",
            dest="set_fields",
            default=False,
            help="Campos a serem modificados em tempo de execução. Deve ser mostrado em formato JSON. Ex.: --set-fields=\"{'campo1': 1,'campo2': [], 'campo3': \"teste\"}",
        )

        parser.add_argument(
            "-e",
            "--exclude-fields",
            dest="exclude_fields",
            default=False,
            help="Campos a serem excluído da serialização. Deve ser mostrado em formato JSON. Ex.: --exclude-fields=\"['campo1', 'campo2', 'campo3']",
        )

        parser.add_argument(
            "-f",
            "--fields",
            dest="fields",
            default=False,
            help="Campos a serem serializados. Por padrão se não for indicado todos os fields do model será seriazlizado. Deve ser indicado no formato JSON. Ex.: --fields=\"['campo1', 'campo2', 'campo3']",
        )

    @staticmethod
    def serialize(
        query,
        indent=4,
        natural_key=True,
        use_pk=False,
        set_fields={},
        exclude_fields=[],
        fields=[],
    ):
        if isinstance(query, (list, QuerySet)) is False:
            query = [query]
        objs = query

        _fields = fields or None

        if isinstance(query, QuerySet) and not fields and query:
            obj = query.first()
            _fields = [
                (f.attname if f.remote_field is None else f.attname[:-3])
                for f in obj._meta.concrete_model._meta.local_fields
                if f.serialize
            ]
            _fields += [
                f.attname
                for f in obj._meta.concrete_model._meta.many_to_many
                if f.serialize
            ]

            for f in exclude_fields:
                f in _fields and _fields.remove(f)

            for f in obj._meta.concrete_model._meta.many_to_many:
                if f.attname in set_fields:
                    print(
                        'WARNING: The field "%s" can not be set because it is many_to_many field. This field can be excluded from serialization if you need!'
                        % f.attname
                    )
                    set_fields.pop(f.attname)

            if set_fields:
                objs = []
                for obj in query:
                    for k in set_fields:
                        if hasattr(obj, k):
                            setattr(obj, k, set_fields.get(k))
                    objs.append(obj)

        serial = serializers.serialize(
            "json",
            objs,
            indent=indent,
            use_natural_foreign_keys=natural_key,
            use_natural_primary_keys=natural_key,
            ensure_ascii=False,
            fields=_fields or None,
        )
        if use_pk is False:
            serial = re.sub('"pk": [0-9]*', '"pk": null', serial)
        return serial

    def handle(
        self,
        str_filter,
        indent,
        filepath,
        natural_key,
        use_pk,
        import_module,
        set_fields,
        exclude_fields,
        fields,
        *args,
        **kargs
    ):
        from django.conf import settings

        if import_module in getattr(settings, "INSTALLED_APPS", []):
            imports = [
                """
try:
    from %s.models import *
except:
    pass
                """
                % import_module
            ]

            str_filter = "query = %s" % str_filter
            context = {}
            indent = int(indent)
            exec("\n".join(imports + [str_filter]), context)
            rst = Command.serialize(
                query=context["query"],
                indent=indent,
                natural_key=natural_key,
                use_pk=use_pk,
                set_fields=eval(set_fields or "{}"),
                exclude_fields=eval(exclude_fields or "[]"),
                fields=eval(fields or "[]"),
            )
            if filepath:
                with codecs.open(filepath, "w", "utf-8") as fd:
                    fd.write(str(rst))  # .encode('utf-8'))
            else:
                sys.stdout.write(str(rst).encode("utf-8"))
        else:
            print("O módulo '%s' não encontra-se instalado" % import_module)
