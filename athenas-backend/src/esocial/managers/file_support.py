# -*- coding: utf-8 -*-
import codecs
import errno
import fnmatch
import importlib
import json
import os
import re
from string import Template

from django.conf import settings

from contrib.utils import getLogger
from esocial.const import (
    OCCURRENCE_CHOICE,
    OCCURRENCE_MANDATORY,
    OCCURRENCE_NOT_MANDATORY,
)
from esocial.utils import esocial_environment

log = getLogger(__name__)

DIRECTORY_DATA = "%s/esocial/data/generated" % settings.BASE_DIR
DIRECTORY_DATA_CSV = "%s/csv" % DIRECTORY_DATA
DIRECTORY_DATA_JSON = "%s/json" % DIRECTORY_DATA
DIRECTORY_DATA_MODELS_GENERATED = "%s/models" % DIRECTORY_DATA
DIRECTORY_EXTRACTORS = "%s/extractors" % DIRECTORY_DATA

DIRECTORY_CERTS = "%s/esocial/security/store" % settings.UPLOAD_STORE_DIR

NAME_INDEX = 1
LINE_INDEX = 0
FATHER_NAME_INDEX = 2
TYPE_XML_INDEX = 3
TYPE_DESC_INDEX = 4
OCCURRENCE_INDEX = 5
LENGTH_INDEX = 6
DECIMAL_INDEX = 7
DESCRIPTION_INDEX = 8


_TEMPLATES = {
    "json_model": Template(
        """
    "$field_key_value": {
        "line": "$line",
        "name": "$name",
        "name_key_value": "$name_key_value",
        "name_full_key": "$name_full_key",
        "father": "$father",
        "father_key_value": "$father_key_value",
        "django_id": "$django_id",
        "xml_type": "$xml_type",
        "type_desc": "$type_desc",
        "occurrence": "$occurrence",
        "length": "$length",
        "decimal": "$decimal",
        "description": "$description",
        "foreign_key": "$foreign_key",
        "model": "$model",
        "many_to_many": "$many_to_many",
        "django_field_name": "$django_field_name",
        "type_of_action": "$type_of_action"
    } """
    ),
    "extractor": Template(
        '''
# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.extractors.base import Extractor


log = getLogger(__name__)


class $klassName(Extractor):

    def __init__(self, *args, **kwargs):
        self.clear = kwargs.get('clear', False)
        super($klassName, self).__init__(*args, **kwargs)

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        pass
$methods'''
    ),
    "extractor_method": Template(
        """
    def $method(self):
        return ''
"""
    ),
}


def directory_data_generate_xml():
    return f"{settings.UPLOAD_STORE_DIR}/esocial/xml{esocial_environment()}"


def camel_to_snake(name):
    name = _lower_esocial(name)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _lower_esocial(name):
    if name.find("eSocial") > -1:
        name = name.replace("eSocial", "esocial")
    return name


def _load_json_model(acronym):
    """
    :py:function:: _load_json_model(acronym)

    This method loads a json file of the event model based on the acronym paremeter. Then returns.

    :return: json_model
    :rtype: dict
    """
    json_model = {}
    try:
        with open(
            "%s/%s.json" % (DIRECTORY_DATA_JSON, acronym.lower()), "r"
        ) as register:
            json_model = json.load(register)
    except Exception as err:
        log.info("Json model não encontrado para %s" % acronym)
        log.exception(err)
        print("Json model não encontrado para %s" % acronym)
        print(err)

    return json_model


def _json_model_key_by_line(json_model):
    """
    :py:function:: _json_model_key_by_line(json_model)

    This method creates a new json_model using the line as key.

    Este método cria um novo json_model utilizando a linha como key.

    :param dict json_model: json_model
    :return: json_model
    :rtype: dict
    """
    line_to_elem = {}
    for elem in json_model:
        line_to_elem.update(
            {int(json_model.get(elem).get("line")): json_model.get(elem)}
        )
    return line_to_elem


def json_rewrite_key(acronyms=[]):
    """
    :py:function:: json_rewrite_key()

    This method modifies the json_model by rewriting its keys.

    Este método modica o json_model reescrevendo suas keys.

    """
    for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_JSON):
        for filename in fnmatch.filter(filenames, "*.json"):
            acronym = filename.replace(".json", "").replace("-", "").lower()
            filename = "%s/%s" % (root, filename)
            if acronym and acronym in acronyms:
                json_model = _load_json_model(acronym)
                json_model_by_line = _json_model_key_by_line(json_model)

                template = _TEMPLATES.get("json_model")

                buff = "{"
                for key in list(json_model_by_line):
                    field = json_model_by_line.get(key)
                    name = _define_name(json_model, field)
                    father_key_value = ""
                    if field.get("name") != "eSocial":
                        name_splitted = name.split("-")
                        father_key_value = name_splitted[0 : (len(name_splitted) - 1)]
                        father_key_value = "-".join(father_key_value)
                    if len(buff) > 1:
                        buff += ","
                    buff += template.substitute(
                        field_key_value=name,
                        line=field.get("line"),
                        name=field.get("name"),
                        name_key_value=field.get("name_key_value"),
                        name_full_key=name,
                        father=field.get("father"),
                        father_key_value=father_key_value,
                        django_id=field.get("django_id"),
                        xml_type=field.get("xml_type"),
                        type_desc=field.get("type_desc"),
                        occurrence=field.get("occurrence"),
                        length=field.get("length"),
                        decimal=field.get("decimal"),
                        description=field.get("description"),
                        foreign_key=field.get("foreign_key"),
                        model=field.get("model"),
                        many_to_many=field.get("many_to_many"),
                        django_field_name=camel_to_snake(
                            field.get("django_field_name")
                        ),
                        type_of_action=field.get("type_of_action"),
                    )
                buff += "\n}"

                with open(filename, "w") as json_rewrite:
                    json_rewrite.write(buff)


def _define_name(json_model, field):
    """
    :py:function:: _define_name(json_model, field)

    This method sets the new name using the path to the field.

    Este método define o novo nome utilizando caminho até o campo.

    :param dict json_model: json_model
    :param dict field: field
    :return: path_name
    :rtype: str
    """
    father = field
    father = search_father_of_field_by_position(
        json_model, father.get("father"), father.get("line")
    )
    path_name = []
    if father and father.get("name"):
        while father.get("name") != "eSocial":
            father = search_father_of_field_by_position(
                json_model, father.get("father"), father.get("line")
            )
            path_name.append(father.get("name"))
        path_name.reverse()
        path_name.append(field.get("father"))
        path_name.append(field.get("name"))
    else:
        path_name.append(field.get("name"))
    path_name = "-".join(path_name)
    return path_name


def json_rewrite_django_field_name(acronyms=[]):
    """
    :py:function:: json_rewrite_django_field_name()

    This method modifies the json_model by rewriting the django_field_name when the is a duplicated.

    Este método modica o json_model reescrevendo o django_field_name quando existir um duplicado.

    """
    for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_JSON):
        for filename in fnmatch.filter(filenames, "*.json"):
            acronym = filename.replace(".json", "").replace("-", "").lower()
            filename = "%s/%s" % (root, filename)
            if acronym and acronym in acronyms:
                json_model = _load_json_model(acronym)

                _change_repeated_django_field_name(json_model)

                template = _TEMPLATES.get("json_model")
                json_model = _json_model_key_by_line(json_model)
                buff = "{"
                for key in list(json_model):
                    if len(buff) > 1:
                        buff += ","
                    buff += template.substitute(
                        field_key_value=json_model.get(key).get("name_full_key"),
                        line=json_model.get(key).get("line"),
                        name=json_model.get(key).get("name"),
                        name_key_value=json_model.get(key).get("name_key_value"),
                        name_full_key=json_model.get(key).get("name_full_key"),
                        father=json_model.get(key).get("father"),
                        father_key_value=json_model.get(key).get("father_key_value"),
                        django_id=json_model.get(key).get("django_id"),
                        xml_type=json_model.get(key).get("xml_type"),
                        type_desc=json_model.get(key).get("type_desc"),
                        occurrence=json_model.get(key).get("occurrence"),
                        length=json_model.get(key).get("length"),
                        decimal=json_model.get(key).get("decimal"),
                        description=json_model.get(key).get("description"),
                        foreign_key=json_model.get(key).get("foreign_key"),
                        model=json_model.get(key).get("model"),
                        many_to_many=json_model.get(key).get("many_to_many"),
                        django_field_name=camel_to_snake(
                            json_model.get(key).get("django_field_name")
                        ),
                        type_of_action=json_model.get(key).get("type_of_action"),
                    )
                buff += "\n}"

                with open(filename, "w") as json_rewrite:
                    json_rewrite.write(buff)


def _change_repeated_django_field_name(json_model):
    """
    :py:function:: _change_repeated_django_field_name(json_model)

    This method modifies the django_field_name when it encounters a duplicated.

    Este método modifica o django_field_name quando encontra um duplicado.

    :param dict json_model: json_model
    :param dict field: field
    :return: json_model
    :rtype: dict
    """
    json_model_by_line = _json_model_key_by_line(json_model)
    keys = list(json_model_by_line)
    keys.sort(reverse=True)

    for key in keys:
        key = json_model_by_line.get(key).get("name_full_key")
        new_name = []
        level = 1
        count = 0
        if json_model.get(key).get("xml_type") not in ["G", "CG"]:
            while _find_repeated_django_field_name(json_model, json_model.get(key)):
                father = _next_father_level(json_model, json_model.get(key), level)
                new_name.append(father.get("name"))
                if json_model.get(key).get("django_field_name") and count > 0:
                    new_name.append(json_model.get(key).get("django_field_name"))
                else:
                    new_name.append(json_model.get(key).get("name"))
                new_name = "_".join(new_name)
                json_model.get(key).update(
                    {"django_field_name": camel_to_snake(new_name)}
                )
                new_name = []
                level += 1
                count += 1


def _find_repeated_django_field_name(json_model, field):
    repeated = False
    for key in json_model:
        if (
            field.get("name") == json_model.get(key).get("name")
            and field.get("django_field_name")
            == json_model.get(key).get("django_field_name")
            and field.get("type_of_action") == json_model.get(key).get("type_of_action")
            and field.get("line") != json_model.get(key).get("line")
        ):
            repeated = True
    return repeated


def _next_father_level(json_model, field, level=1):
    father = field
    count = 1
    while count <= level and father:
        father = search_father_of_field_by_name(
            json_model, father.get("father_key_value")
        )
        count += 1
    return father


def _csv_adjust(recreate=True):
    """
    :py:function:: _csv_adjust(recreate=True)

    This method adjusts the csv.

    Este método ajusta o csv baseando-se no csv.

    :param bool recreate: recreate
    """
    for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_CSV):
        for filename in fnmatch.filter(filenames, "*.csv"):
            csv = filename.replace(".csv", "").replace("-", "").lower()
            if not os.path.isfile(csv) or recreate:
                filename = "%s/%s" % (root, filename)
                lines = []
                with codecs.open(filename, "r") as csv_file:
                    lines = csv_file.readlines()

                buff = ""
                count = 1
                for line in lines:
                    line_array = line.split("|")
                    change_index = 1 if len(line_array) == 10 else 0

                    line_array[change_index] = "%s" % count
                    line_array[NAME_INDEX + change_index] = line_array[
                        NAME_INDEX + change_index
                    ].replace(" ", "")
                    line_array[LINE_INDEX + change_index] = line_array[
                        LINE_INDEX + change_index
                    ].replace(" ", "")
                    line_array[FATHER_NAME_INDEX + change_index] = line_array[
                        FATHER_NAME_INDEX + change_index
                    ].replace(" ", "")
                    line_array[TYPE_XML_INDEX + change_index] = (
                        line_array[TYPE_XML_INDEX + change_index]
                        .replace(" ", "")
                        .replace("-", "")
                    )
                    line_array[TYPE_DESC_INDEX + change_index] = line_array[
                        TYPE_DESC_INDEX + change_index
                    ].replace(" ", "")
                    line_array[OCCURRENCE_INDEX + change_index] = line_array[
                        OCCURRENCE_INDEX + change_index
                    ].replace(" ", "")
                    line_array[LENGTH_INDEX + change_index] = line_array[
                        LENGTH_INDEX + change_index
                    ].replace(" ", "")
                    if len(line_array) - 1 >= (DECIMAL_INDEX + change_index):
                        line_array[DECIMAL_INDEX + change_index] = line_array[
                            DECIMAL_INDEX + change_index
                        ].replace(" ", "")

                    new_line = (
                        ("|".join(line_array[change_index : len(line_array)]))
                        .replace("\n", "")
                        .replace('"', "")
                    )
                    buff += new_line + "\n"
                    count += 1
                with codecs.open(filename, "w") as csv_file:
                    csv_file.write(buff)


def csv_to_json(recreate=True, acronyms=[]):
    """
    :py:function:: csv_to_json(recreate=True)

    This method creates the json_mdoel file based on the csv conf.

    Este método cria o json_model baseando-se no csv.

    :param bool recreate: recreate
    """

    _csv_adjust(recreate=recreate)

    for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_CSV):
        for filename in fnmatch.filter(filenames, "*.csv"):
            event_name = filename.replace(".csv", ".json").replace("-", "").lower()
            event_file_name = "%s/%s" % (DIRECTORY_DATA_JSON, event_name)
            if event_name.replace(".json", "") in acronyms:
                filename = "%s/%s" % (root, filename)
                buff = "{"
                template = _TEMPLATES.get("json_model")
                father_key_value_array = {}

                fields_relation = _fields_relation(event_name.replace(".json", ""))

                with open(filename, "r") as event:
                    fields = []
                    django_fields = []
                    type_of_action = ""
                    count = 0
                    for line in event.readlines():
                        count += 1
                        line = line.replace(" ", "")
                        line = line.replace("\t", "")
                        line_array = line.split("|")
                        change_index = 1 if len(line_array) == 10 else 0
                        if len(buff) > 1:
                            buff += ","
                        name = line_array[NAME_INDEX + change_index].replace(" ", "")
                        line = line_array[LINE_INDEX + change_index].replace(" ", "")
                        name_key_value = "%s-%s" % (line, name)
                        father_name = line_array[
                            FATHER_NAME_INDEX + change_index
                        ].replace(" ", "")
                        father_key_value = search_father_of_field_by_position(
                            father_key_value_array, father_name, line
                        )
                        if father_key_value:
                            father_value_key = "%s-%s" % (
                                father_key_value.get("name"),
                                father_key_value.get("line"),
                            )
                            father_key_value = "%s-%s" % (
                                father_key_value.get("line"),
                                father_key_value.get("name"),
                            )
                        else:
                            father_value_key = father_name
                            father_key_value = father_name
                        django_id = ""
                        if name in fields:
                            django_id = (
                                "%s-%s" % ("%s-%s" % (name, line), father_value_key)
                            ).replace("-", "")

                        type_xml = line_array[TYPE_XML_INDEX + change_index].replace(
                            " ", ""
                        )

                        if type_xml == "G" and name in [
                            "inclusao",
                            "alteracao",
                            "exclusao",
                        ]:
                            type_of_action = name

                        if type_xml in ["G", "CG"] and name not in fields_relation:
                            django_field_name = ""
                        elif name == "Id":
                            django_field_name = "identifier"
                        elif name in fields_relation:
                            django_field_name = name
                        elif father_name and father_name != "eSocial":
                            django_field_name = "%s_%s" % (father_name, name)
                        else:
                            django_field_name = name

                        if django_field_name:
                            django_fields.append(django_field_name)

                        foreign_key = fields_relation.get(name, {}).get(
                            "foreign_key", False
                        )
                        many_to_many = fields_relation.get(name, {}).get(
                            "many_to_many", False
                        )
                        model = fields_relation.get(name, {}).get("refer_class", "")
                        buff_line = template.substitute(
                            field_key_value=("%s-%s" % (line, name)),
                            line=line,
                            name=name,
                            name_key_value=name_key_value,
                            name_full_key=("%s-%s" % (line, name)),
                            father=father_name,
                            father_key_value=father_key_value,
                            django_id=django_id,
                            xml_type=type_xml,
                            type_desc=line_array[
                                TYPE_DESC_INDEX + change_index
                            ].replace(" ", ""),
                            occurrence=line_array[
                                OCCURRENCE_INDEX + change_index
                            ].replace(" ", ""),
                            length=line_array[LENGTH_INDEX + change_index].replace(
                                " ", ""
                            ),
                            decimal=line_array[DECIMAL_INDEX + change_index].replace(
                                " ", ""
                            ),
                            description=line_array[DESCRIPTION_INDEX + change_index]
                            .replace("\n", "")
                            .replace('"', ""),
                            foreign_key=foreign_key,
                            model=model,
                            many_to_many=many_to_many,
                            django_field_name=camel_to_snake(django_field_name),
                            type_of_action=type_of_action,
                        )
                        buff += buff_line
                        if type_xml in ("G", "CG"):
                            father_key_value_array.update(
                                {"%s-%s" % (line, name): {"name": name, "line": line}}
                            )

                        fields.append(name)
                line = int(line)
                buff = _append_xmlns_field(template, buff, line)
                buff += "\n}"
                with open(event_file_name, "w") as event_file:
                    event_file.write(buff)
    json_rewrite_key(acronyms=acronyms)
    json_rewrite_django_field_name(acronyms=acronyms)
    return True


def _append_xmlns_field(template, buff, length):
    """
    :py:function:: _append_xmlns_field(template, buff, length)

    This method appends the xmlns field to the buffer.

    Este método acrescenta o campo xmlns ao buffer.

    :param Template template: template
    :param str buff: buff
    :return: buff
    :rtype: str
    """
    line_number = length + 1
    buff += ","
    buff += template.substitute(
        field_key_value="eSocial-xmlns",
        line=line_number,
        name="xmlns",
        name_key_value=str(line_number) + "-xmlns",
        name_full_key=str(line_number) + "-xmlns",
        father="eSocial",
        father_key_value="eSocial",
        django_id="",
        xml_type="A",
        type_desc="C",
        occurrence="1-1",
        length="256",
        decimal="-",
        description="",
        foreign_key="False",
        model="",
        many_to_many="False",
        django_field_name="xmlns",
        type_of_action="",
    )
    return buff


def _fields_relation(acronym=""):
    return {
        "ideEmpregador": {
            "refer_class": "IdeEmployer",
            "django_field": "models.ForeignKey",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "foreign_key": True,
        },
        "dependente": {
            "refer_class": "Dependent",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "horarioIntervalo": {
            "refer_class": "WorkHourInterval",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "infoCRContrib": {
            "refer_class": "InfoCRContrib",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "ideProcessoSIND": {
            "refer_class": "IdeProcesso",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "ideProcessoCP": {
            "refer_class": "IdeProcesso",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "ideProcessoIRRF": {
            "refer_class": "IdeProcesso",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "ideProcessoFGTS": {
            "refer_class": "IdeProcesso",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "procJudTrab": {
            "refer_class": "IdeProcesso",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "procJudTerceiro": {
            "refer_class": "ProcJudTerceiro",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='register_%s'" % acronym.replace("-", ""),
            "many_to_many": True,
        },
        "infoSusp": {
            "refer_class": "InfoSuspensao",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='events'",
            "many_to_many": True,
        },
        "infoAtestado": {
            "refer_class": "HealthCertificate",
            "django_field": "models.ManyToManyField",
            "related_name": "related_name='events'",
            "many_to_many": True,
        },
    }


def _fields_pre_conf():
    return {
        "Id": {
            "django_field": "models.PositiveIntegerField",
            "choices": "",
            "default": "",
        },
        "tpAmb": {
            "django_field": "models.PositiveIntegerField",
            "choices": "choices=Choice.get_choices_for('esocial', 'TYPE_ENV')",
            "default": "default=3",
        },
        "procEmi": {
            "django_field": "models.PositiveIntegerField",
            "choices": "",
            "default": "default=1",
        },
        "verProc": {
            "django_field": "models.CharField",
            "choices": "",
            "default": "",
            "max_length": "20",
        },
        "indRetif": {
            "django_field": "models.PositiveIntegerField",
            "choices": "choices=Choice.get_choices_for('esocial', 'INDICATIVE_TYPE_INFORMATION')",
            "default": "default=1",
        },
        "indApuracao": {
            "django_field": "models.PositiveIntegerField",
            "choices": "choices=Choice.get_choices_for('esocial', 'INDICATIVE_ASCERTAINMENT_PERIOD')",
            "default": "default=1",
        },
        "perApur": {
            "django_field": "models.CharField",
            "choices": "",
            "default": "",
            "max_length": "7",
        },
        "nrRecibo": {
            "django_field": "models.CharField",
            "choices": "",
            "default": "",
            "max_length": "40",
        },
    }


def _static_fields():
    return ["XML_SCHEMA_NAME", "XMLNS", "GROUP", "NAME", "ACTION_PERM"]


def _get_register_model_template():
    return Template(
        """# -*- coding: utf-8 -*-
from django.db import models
from esocial.models import Register
from esocial.const import ACTION


class $register_model_name(Register):
    class Meta:
        app_label = 'esocial'
$fields
"""
    )


def _get_event_field_template():
    return Template(
        """
    $xml_schema_name
    $xmlns
    $group
    $name
    $action_perm"""
    )


def _get_register_field_template():
    return Template(
        """
    $name = $django_field($refer_class$related_name$max_digits$decimal_places$max_length$null$blank$choices$default)"""
    )


def create_django_model_by_json_model(recreate=True, acronyms=[]):
    """
    :py:function:: create_django_model_by_json_model(recreate=True)

    This method creates the django model based on the json file conf.

    """
    for root, dirnames, filenames in os.walk("%s" % DIRECTORY_DATA_JSON):
        for filename in fnmatch.filter(filenames, "*.json"):
            acronym = filename
            acronym = acronym.replace(".json", "").replace("-", "")
            register_model_name = acronym
            register_model_file_name = "%s/%s.py" % (
                DIRECTORY_DATA_MODELS_GENERATED,
                register_model_name,
            )

            acronym_lower = acronym.lower()
            if acronym in acronyms:
                json_model = _load_json_model(acronym)
                json_model_by_line = _json_model_key_by_line(json_model)
                register_field_template = _get_register_field_template()
                static_fields_conf = _read_model_static_fields(acronym)

                register_fields_buff = _get_event_field_template().substitute(
                    xml_schema_name="XML_SCHEMA_NAME = '%s'"
                    % static_fields_conf.get(acronym_lower, {}).get("XML_SCHEMA_NAME"),
                    xmlns="XMLNS = '%s'"
                    % static_fields_conf.get(acronym_lower, {}).get("XMLNS"),
                    group="GROUP = %s"
                    % static_fields_conf.get(acronym_lower, {}).get("GROUP"),
                    name="NAME = '%s'"
                    % static_fields_conf.get(acronym_lower, {}).get("NAME"),
                    action_perm="ACTION_PERM = ACTION",
                )

                not_include = _not_include_model()
                fields_relation = _fields_relation(acronym.replace("-", ""))

                relateds = []
                for key in list(json_model_by_line):
                    django_id = ""
                    field = json_model_by_line.get(key)
                    name = field.get("name")
                    django_field_name = field.get("django_field_name")
                    father_name = field.get("father_key_value")
                    father_of_field = search_father_of_field_by_name(
                        json_model, father_name
                    )
                    to_include = True
                    django_field = "models.CharField"
                    type_xml = field.get("xml_type", "")
                    refer_class = field.get("model", "")
                    related_name = ""
                    max_length = ""
                    max_digits = ""
                    decimal_places = ""
                    null_op = ""
                    blank_op = ""
                    flag_as_group = False
                    choices = ""
                    default = ""
                    if type_xml in ("G", "CG"):
                        flag_as_group = True
                        django_field = fields_relation.get(name, {}).get(
                            "django_field", ""
                        )
                        related_name = fields_relation.get(name, {}).get(
                            "related_name", ""
                        )
                        if related_name:
                            if related_name in relateds and django_field_name:
                                related_name = related_name.split("'")
                                related_name = "related_name='%s_%s'" % (
                                    django_field_name,
                                    related_name[1],
                                )
                            relateds.append(related_name)
                    elif field.get("type_desc") == "N":
                        django_field = "models.PositiveIntegerField"
                        if field.get("decimal").replace("-", ""):
                            django_field = "models.DecimalField"
                            fld_len = field.get("length", "1").split("-")
                            fld_len = fld_len[len(fld_len) - 1]
                            max_digits = "max_digits=%s" % int(fld_len)
                            decimal_places = "decimal_places=%s" % int(
                                field.get("decimal").replace("-", "")
                            )
                    elif field.get("type_desc") == "C":
                        fld_len = field.get("length", "1").split("-")
                        fld_len = fld_len[len(fld_len) - 1]
                        max_length = "max_length=%s" % int(fld_len)
                    elif field.get("type_desc") == "D":
                        django_field = "models.DateField"

                    if name in list(_fields_pre_conf()):
                        django_field = (
                            _fields_pre_conf().get(name).get("django_field", "")
                        )
                        choices = _fields_pre_conf().get(name).get("choices", "")
                        default = _fields_pre_conf().get(name).get("default", "")
                        max_length = _fields_pre_conf().get(name).get("max_length", "")

                    if name in _static_fields():
                        django_field = static_fields_conf

                    occurrence = _define_occurrence(field.get("occurrence"))
                    father_occurrence = _check_fathers_occurrence(json_model, field)

                    if (
                        OCCURRENCE_NOT_MANDATORY in [father_occurrence, occurrence]
                        and not refer_class
                    ):
                        null_op = "null=True"
                        blank_op = "blank=True"

                    mandatory_to_comment = name in list(_fields_pre_conf())

                    field_nt = not_include.get(name, {})
                    if len(field_nt) > 0 and (
                        father_of_field.get("name") == field_nt.get("father", "")
                        or field_nt.get("father", "") == ""
                    ):
                        mandatory_to_comment = True

                    if (father_name not in list(fields_relation)) or name:
                        commented = ""
                        if (
                            (flag_as_group and not refer_class)
                            or mandatory_to_comment
                            or not django_field_name
                        ):
                            commented = "# "
                        elif _search_field_with_action_inclusion(json_model, field):
                            commented = "# "
                        elif _check_fathers_relation(json_model, field):
                            commented = "# "
                            to_include = False

                        name_defined = django_id if django_id else name
                        name = "%s%s" % (
                            commented,
                            (
                                str(django_field_name)
                                if django_field_name
                                else name_defined
                            ),
                        )

                        if (not flag_as_group or refer_class) and not commented:
                            if refer_class and related_name:
                                related_name = ", %s" % related_name
                            if max_digits and decimal_places:
                                decimal_places = ", %s" % decimal_places
                            if null_op and (
                                refer_class
                                or related_name
                                or max_length
                                or max_digits
                                or decimal_places
                            ):
                                null_op = ", %s" % null_op
                            if blank_op and (
                                refer_class
                                or related_name
                                or max_length
                                or max_digits
                                or decimal_places
                                or null_op
                            ):
                                blank_op = ", %s" % blank_op
                            if choices and (
                                max_length
                                or max_digits
                                or decimal_places
                                or null_op
                                or blank_op
                            ):
                                choices = ", %s" % choices
                            if default and (
                                max_length
                                or max_digits
                                or decimal_places
                                or null_op
                                or blank_op
                                or choices
                            ):
                                default = ", %s" % default
                        else:
                            to_include = False

                        if to_include:
                            register_fields_buff += register_field_template.substitute(
                                name=name,
                                django_field=django_field,
                                refer_class=(
                                    ("'%s'" % refer_class) if refer_class else ""
                                ),
                                related_name=related_name,
                                max_digits=max_digits,
                                decimal_places=decimal_places,
                                max_length=max_length,
                                null=null_op,
                                blank=blank_op,
                                choices=choices,
                                default=default,
                            )
                register_class_buff = _get_register_model_template().substitute(
                    register_model_name=register_model_name.upper(),
                    fields=register_fields_buff,
                )
                with codecs.open(
                    register_model_file_name, "w", encoding="utf-8"
                ) as register_file:
                    register_file.write(register_class_buff)
    return True


def search_father_of_field_by_position(
    father_key_value_array, father_key, position, verbose=0
):
    """
    :py:function:: search_father_of_field_by_position(father_key_value_array, father_key, position)

    This method search father of the field.

    :return: json_model
    :rtype: dict
    """
    father = {}
    father_key_value_array = _json_model_key_by_line(father_key_value_array)
    keys = list(father_key_value_array)
    for key in keys:
        if int(key) > int(position):
            break

        if father_key_value_array.get(key).get("name") == father_key:
            if not father:
                father = father_key_value_array.get(key)

            if int(father.get("line")) > int(position):
                father_value = int(father.get("line")) - int(position)
            else:
                father_value = int(position) - int(father.get("line"))

            if int(father_key_value_array.get(key).get("line")) > int(position):
                test_value = int(father_key_value_array.get(key).get("line")) - int(
                    position
                )
            else:
                test_value = int(position) - int(
                    father_key_value_array.get(key).get("line")
                )

            if father_value > test_value:
                father = father_key_value_array.get(key)
    return father


def search_father_of_field_by_name(json_model, to_find):
    """
    :py:function:: search_father_of_field_by_name(json_model, to_find)

    This method search father of the field.

    :return: json_model
    :rtype: dict
    """
    father = json_model.get(to_find, {})
    return father


def _check_fathers_occurrence(
    json_model, field, father_occurrence=OCCURRENCE_NOT_MANDATORY
):
    if field.get("father_key_value") != "eSocial":
        father = search_father_of_field_by_name(
            json_model, field.get("father_key_value")
        )
        if father.get("name") in ["inclusao", "alteracao", "exclusao"]:
            father_occurrence = OCCURRENCE_MANDATORY
        else:
            father_occurrence = _define_occurrence(father.get("occurrence", ""))
        if father_occurrence != OCCURRENCE_NOT_MANDATORY and father != {}:
            father_occurrence = _check_fathers_occurrence(
                json_model, father, father_occurrence
            )
    return father_occurrence


def _check_fathers_relation(json_model, field):
    """
    :py:function:: _check_fathers_relation(json_model, field)

    This method checks whether the path to the field has foreign_key or many_to_many.

    Este método verifica se o caminho até o field possui foreign_key ou many_to_many.

    :param dict json_model: json_model
    :param dict field: field
    :return: bool
    :rtype: bool
    """
    field = search_father_of_field_by_name(json_model, field.get("father_key_value"))
    while field and field.get("name_full_key") != "eSocial":
        if eval(field.get("foreign_key")) or eval(field.get("many_to_many")):
            return True
        field = search_father_of_field_by_name(
            json_model, field.get("father_key_value")
        )
    return False


def _define_occurrence(occurrence):
    return OCCURRENCE_CHOICE.get(
        occurrence.replace(" ", "").split("-")[0], OCCURRENCE_MANDATORY
    )


def create_dir_batch(batch):
    try:
        dir_year, dir_month = define_dir_event(
            batch.created_at.month, batch.created_at.year
        )
        dir_batch = "%s/%s" % (dir_month, batch.pk)
        if not os.path.exists(dir_year):
            os.makedirs(dir_year)
        if not os.path.exists(dir_month):
            os.makedirs(dir_month)
        if not os.path.exists(dir_batch):
            os.makedirs(dir_batch)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise err
    return dir_batch


def get_register_model(search):
    search = search.lower()
    register_modules = importlib.import_module("esocial.models")
    register_model = getattr(register_modules, search.upper(), None)
    return register_model


def directory_certs():
    if not os.path.exists(DIRECTORY_CERTS):
        os.makedirs(DIRECTORY_CERTS)
    return DIRECTORY_CERTS


def _read_model_static_fields(acronym):
    _model = get_register_model(acronym)
    return {
        acronym: {
            "XML_SCHEMA_NAME": getattr(_model, "XML_SCHEMA_NAME", ""),
            "NAME": getattr(_model, "NAME", ""),
            "XMLNS": getattr(_model, "XMLNS", ""),
            "GROUP": getattr(_model, "GROUP", "1"),
            "ACTION_PERM": getattr(_model, "ACTION_PERM", "ACTION"),
        }
    }


def _search_field_with_action_inclusion(json_model, field):
    to_comment = False
    name_full_key = field.get("name_full_key")
    if name_full_key.find("alteracao") > -1 or name_full_key.find("exclusao") > -1:
        name_full_key = name_full_key.replace("alteracao", "inclusao").replace(
            "exclusao", "inclusao"
        )
        to_comment = len(json_model.get(name_full_key, {})) > 0
    return to_comment


def _not_include_model():
    return {
        "ideEmpregador": {"father": ""},
        "tpInsc": {"father": "ideEmpregador"},
        "nrInsc": {"father": "ideEmpregador"},
        "xmlns": {"father": ""},
    }


def define_dir_year(year):
    return "%s/%s" % (directory_data_generate_xml(), year)


def define_dir_month(register):
    return "%s/%s" % (define_dir_year(register), register.competence_month)


def define_dir_event(month, year):
    dir_year = define_dir_year(year)
    dir_month = "%s/%s" % (dir_year, month)
    return dir_year, dir_month


def create_dir_event(event):
    dir_event = None
    if not event.INTERNAL:
        try:
            dir_year, dir_month = define_dir_event(
                event.competence_month, event.competence_year
            )
            dir_event = "%s/%s" % (dir_month, event.acronym)
            if not os.path.exists(dir_year):
                os.makedirs(dir_year)
            if not os.path.exists(dir_month):
                os.makedirs(dir_month)
            if not os.path.exists(dir_event):
                os.makedirs(dir_event)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    return dir_event
