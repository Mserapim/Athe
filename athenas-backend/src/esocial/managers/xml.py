# -*- coding: utf-8 -*-
import copy
import os
import re
from io import StringIO

from django.conf import settings
from lxml import etree

from contrib.utils import DateUtils, getLogger
from esocial.const import ACTION, OCCURRENCE_MANDATORY
from esocial.managers.file_support import (
    _check_fathers_occurrence,
    _define_occurrence,
    search_father_of_field_by_name,
)
from esocial.security.xml.manager import _load_data_file

log = getLogger(__name__)


"""

    json_model - json - é um modelo contendo as configurações do evento;

"""


PRINT_VERBOSE = False


def _print_verbose(message, verbose=False):
    if verbose:
        print(message)


def _validation_xml_schema(xml_schema, xml_or_path, assert_test=False):
    """
    :py:function:: _validation_xml_schema(xml_schema, xml_or_path, assert_test=False)

    Este método valida um xml através do schema informado.

    :param str xml_schema: schema of xml to validate
    :param str,etree._Element,etree._ElementTree, xml_or_path: etree._Element or path
    :param bool assert_test: default False
    :return: xml_tree
    :rtype: etree.Element
    """
    path_schema_location = (
        "%s/esocial/data/schema/xmldsig-core-schema.xsd" % settings.BASE_DIR
    )
    valid = False
    # TODO: CARREGAR O XML DO ARQUIVO, COM A TAG
    xmlschema = None
    try:
        if not xml_schema:
            raise Exception("Schema não informado")
        path_schema_location = "%s/esocial/data/schema/" % settings.BASE_DIR
        schema = StringIO(xml_schema)
        xmlschema_doc = etree.parse(schema)
        import_location = xmlschema_doc.getroot().find("{*}import")
        include_location = xmlschema_doc.getroot().find("{*}include")
        if import_location is not None:
            import_location.set(
                "schemaLocation",
                path_schema_location + import_location.get("schemaLocation"),
            )
        if include_location is not None:
            include_location.set(
                "schemaLocation",
                path_schema_location + include_location.get("schemaLocation"),
            )
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml_doc = None
        if isinstance(xml_or_path, str) and os.path.exists(xml_or_path):
            xml = StringIO(_load_data_file(xml_or_path))
            xml_doc = etree.parse(xml)
        elif isinstance(xml_or_path, etree._Element):
            xml_doc = etree.ElementTree(xml_or_path)
        elif isinstance(xml_or_path, etree._ElementTree):
            xml_doc = xml_or_path
        else:
            log.info("XML Valid: False > invalid type %s" % type(xml_or_path))
            _print_verbose(
                "XML Valid: False > invalid type %s" % type(xml_or_path),
                verbose=PRINT_VERBOSE,
            )

        if xml_doc:
            valid = (xmlschema.validate(xml_doc) and True) or False
    except IOError:
        log.info("Invalid File")
        _print_verbose("Invalid File", verbose=PRINT_VERBOSE)
    except etree.XMLSyntaxError as err:
        log.info("XML Syntax Error, see error_syntax.log")
        _print_verbose("XML Syntax Error, see error_syntax.log", verbose=PRINT_VERBOSE)
        with open("error_syntax.log", "w+") as error_log_file:
            error_log_file.write(
                "---------------------------- %s ----------------------------"
                % xml_or_path
            )
            error_log_file.write(str(err.error_log))
    except Exception as e:
        message = ">>>>>>>>>>>> Unknown error, exiting.<<<<<<<<<<<<<<"
        _print_verbose(e, verbose=PRINT_VERBOSE)
        _print_verbose(message, verbose=PRINT_VERBOSE)
        log.info(message)
        log.exception(e)

    if assert_test and xmlschema:
        xmlschema.assertValid(xml_doc)

    return valid


def generate_xml_with_value(event, file_path=None):
    """
    :py:function:: generate_xml_with_value(event, file_path=None)

    Este método gerencia o processo de criação do xml baseado num modelo definido em json_model
    de cada evento.
    Evalua os campos do modelo do django.
    Escreve o xml criado.

    This method manages the process that creates xml based on the json_model of the event.
    Evaluate fields from django model.
    Writes the xml file created.

    :param Event event:
    :param str file_path:
    :return: xml_tree
    :rtype: etree.Element
    """
    xml_tree = None
    if event.json_model:

        xml_tree = evaluate_by_action(
            event, event, field=root_element_name(event.json_model)
        )

        if xml_tree:
            remove_not_mandatory_group(event.json_model, xml_tree)
            xml_tree.write(
                file_path or event.file_path, encoding="utf-8", pretty_print=True
            )

    return xml_tree


def root_element_name(json_model):
    """
    :py:function:: root_element_name(json_model)

    Este método encontra o elemento root do json_model e o retorna.

    This method finds the root element then return its name from json_model.

    :param dict json_model:
    :return: root_element_name
    :rtype: str
    """
    return "eSocial"


def evaluate_by_action(event, instance, xml_tree=None, field="eSocial"):
    """
    :py:function:: evaluate_by_action(event, instance, xml_tree=None, field='eSocial')

    Este método evalua o registro a partir do json_model do evento. O json_model
    é definido pela ação do evento identificado pelo campo json_model_by_action.

    This method evaluate the event by the json_model. The json_model is
    defined by the action of the event given by the json_model_by_action property.

    :param Event event:
    :param Event instance:
    :param etree.Element xml_tree: xml_tree
    :param str field: name of the field to evaluate
    :return: etree.Element
    :rtype: xml_tree
    """
    json_model = event.json_model_by_action
    if field == "eSocial":
        xml_tree = create_group_xml(
            event, event, json_model, json_model.get(field), xml_tree
        )
    children = children_of_sorted(json_model, field)
    keys = list(children)
    keys.sort()
    for key in keys:
        _evaluate(event, instance, xml_tree, children.get(key))
    return xml_tree


def evaluate_many_to_many(event, instance, xml_tree=None, field=None):
    """
    :py:function:: evaluate_many_to_many(event, instance, xml_tree=None, field=None)

    Este método evalua o registro a partir do json_model do evento. O json_model
    é definido pela ação do evento identificado pelo campo json_model_by_action.

    This method evaluate the event by the json_model. The json_model is
    defined by the action of the event given by the json_model_by_action property.

    :param Event event:
    :param Event instance:
    :param etree.Element xml_tree: xml_tree
    :param str field: name of the field to evaluate
    :return: etree.Element
    :rtype: xml_tree
    """
    json_model = event.json_model_by_action
    field_inst = json_model.get(field)
    django_field = extract_django_field(
        event, instance, field_inst, field_inst.get("django_field_name")
    )
    queryset = extract_django_field_queryset(instance, django_field.name)
    for obj in queryset.filter():
        children = children_of_sorted(json_model, field)
        keys = list(children)
        keys.sort()
        create_group_xml(event, obj, json_model, field_inst, xml_tree)
        for key in keys:
            _evaluate(event, obj, xml_tree, children.get(key))
    return xml_tree


def _evaluate(event, instance, xml_tree=None, field=None):
    json_model = event.json_model_by_action
    if field.get("xml_type") in ("G", "CG"):
        if eval(field.get("many_to_many")):
            evaluate_many_to_many(event, instance, xml_tree, field.get("name_full_key"))
        else:
            create_group_xml(event, instance, json_model, field, xml_tree)
            evaluate_by_action(event, instance, xml_tree, field.get("name_full_key"))
    elif field.get("xml_type") == "E":
        create_element_xml(event, instance, json_model, field, xml_tree)
    elif field.get("xml_type") == "A":
        pass
    else:
        print("%s not evaluated" % field.get("name"))


def extract_instance(event, name_full_key):
    return event


def create_group_xml(event, instance, json_model, field, xml_tree):
    """
    :py:function:: create_group_xml(event, instance, json_model, field, xml_tree)

    Este método cria o elemento xml para o elemento tipo grupo.

    This method creates the xml element for group type.

    :param Event event:
    :param * instance: qualquer objeto para extração, pode ser Event, IdeProcesso, Dependent
    :param etree.Element xml_tree: xml_tree
    :param dict json_model:
    :param str field: name of the field to evaluate
    :return: etree.Element
    :rtype: xml_tree
    """
    element_tree = None
    if field and not field.get("father_key_value"):
        root = etree.Element(
            field.get("name"), **attributes(event, instance, json_model, field)
        )
        element_tree = etree.ElementTree(root)
    elif field:
        father = _xml_search_father(field.get("father"), xml_tree)
        element_tree = etree.SubElement(
            father, field.get("name"), **attributes(event, instance, json_model, field)
        )
    else:
        print("field not defined", field)
    return element_tree


def create_element_xml(event, instance, json_model, field, xml_tree):
    """
    :py:function:: create_element_xml(event, instance, json_model, field, xml_tree)

    Este método cria o elemento xml para o tipo elemento.

    This method creates the xml element for element type.

    :param Event event:
    :param Event instance:
    :param dict json_model:
    :param str field: name of the field to evaluate
    :param etree.Element xml_tree: xml_tree
    :return: etree.Element
    :rtype: xml_tree
    """
    element = None
    value = evaluate_field(event, instance, field)
    father = _xml_search_father(field.get("father"), xml_tree)
    if value is not None or (
        _field_mandatory(field) and _father_mandatory(json_model, field)
    ):
        element = etree.SubElement(
            father, field.get("name"), **attributes(event, instance, json_model, field)
        )
        element.text = "{}".format(value)
    return element


def json_model_by_action(json_model, action, not_exclude=[]):
    """
    :py:function:: json_model_by_action(json_model, action)

    Este método identifica qual é a ação passada e então pega todos seus filhos.

    This method identifies which action is passed then gets all fields from that.

    :param dict json_model:
    :param int action:
    :param list not_exclude: lista de ações que não serão excluídas
    :return: json_model_new: new json_model
    :rtype: dict
    """
    action_copy = copy.copy(ACTION)
    to_exclude = {}
    if action in list(action_copy):
        action_copy.pop(action)
    for act in list(action_copy.values()):
        if act not in not_exclude:
            field = None
            for key in list(json_model):
                if json_model.get(key).get("name") == act:
                    field = json_model.get(key)
            if field:
                to_exclude = get_excluded_from_action(json_model, field, to_exclude)
            json_model_new = exclude_elements(json_model, to_exclude)
    return json_model_new


def get_excluded_from_action(json_model, field, to_exclude={}):
    """
    :py:function:: get_excluded_from_action(json_model, field, to_exclude={})

    Este método identifica quais campos devem ser excluídos.

    This method identifies which fields may have to exclude.

    :param dict json_model:
    :param dict field:
    :param dict to_exclude:
    :return: to_exclude:
    :rtype: dict
    """
    to_exclude.update({field.get("name_full_key"): field})
    children = children_of(json_model, field.get("name_full_key"))
    keys = list(children)
    for key in keys:
        if json_model.get(key).get("xml_type") in ("G", "CG"):
            get_excluded_from_action(json_model, json_model.get(key), to_exclude)
        elif field.get("name_full_key") in (
            key,
            json_model.get(key).get("father_key_value"),
        ):
            to_exclude.update({key: json_model.get(key)})
    return to_exclude


def exclude_elements(json_model, to_exclude=[]):
    """
    :py:function:: exclude_elements(json_model, to_exclude=[])

    Este método exclue os campos que não fazem parte da ação do json_model.

    This method excludes fields that doesn't be part of action from json_model.
    Then returns the json_model_new.

    :param dict json_model:
    :param list to_exclude:
    :return: json_model_new: new json_model
    :rtype: dict
    """
    json_model_new = {}
    for key in list(json_model):
        if key not in to_exclude:
            json_model_new.update({key: json_model.get(key)})
    return json_model_new


def children_of(json_model, field_name_full_key):
    """
    :py:function:: children_of(json_model, field_name_full_key)

    Este método encontra os filhos de um campo a partir do field_name_full_key.

    This method finds the children of the field_name_full_key parameter.

    :param dict json_model:
    :param dict field_name_full_key:
    :return: children
    :rtype: dict
    """
    keys = list(json_model)
    children = {}
    for key in keys:
        if json_model.get(key).get("father_key_value") == field_name_full_key:
            children.update({key: json_model.get(key)})
    return children


def children_of_sorted(json_model, field_name_full_key):
    """
    :py:function:: children_of_sorted(json_model, field_name_full_key)

    Este método ordena os filhos de um campo a partir das chaves.

    This method sorts children of the field_name_full_key parameter using key identity.

    :param dict json_model:
    :param dict field_name_full_key:
    :return: children
    :rtype: dict
    """
    children = children_of(json_model, field_name_full_key)
    return {int(children.get(key).get("line")): children.get(key) for key in children}


def attribute_of_field(field, json_model):
    """
    :py:function:: attribute_of_field(field, json_model)

    Este método encontra apenas atributos do field.

    This method gets only the attributes of the field parameter.

    :param dict field:
    :param dict json_model:
    :return: attributes
    :rtype: dict
    """
    attributes = {}
    for key in json_model:
        fld = json_model.get(key)
        if (
            fld.get("xml_type") == "A"
            and field
            and fld.get("father_key_value") == field.get("name_full_key")
        ):
            attributes.update({key: fld})
    return attributes


def attributes(event, instance, json_model, field):
    """
    :py:function:: attributes(event, instance, json_model, field)

    Este método encontra os atributos do field.
    Evalua e os retorna.

    This method gets the attributes of the field parameter.
    Evaluate its values. Then returns.

    :param Event event:
    :param * instance: qualquer objeto para extração, pode ser Event, IdeProcesso, Dependent
    :param dict json_model:
    :param dict field:
    :return: attributes
    :rtype: dict
    """
    attributes = attribute_of_field(field, json_model)
    return {
        attributes.get(key).get("name"): evaluate_field(
            event, instance, attributes.get(key)
        )
        for key in list(attributes)
    }


def evaluate_field(event, instance, field):
    """
    :py:function:: evaluate_field(event, instance, field)

    Este método evalua field. Chama a validação com o método @validate como primeiro passo.

    This method evaluates the field parameter. Calls the validation with validate method as a first pass.

    :param Event event:
    :param * instance: qualquer objeto para extração, pode ser Event, IdeProcesso, Dependent
    :param dict field:
    :return: attributes
    :rtype: dict
    """
    validate()
    return evaluate(event, instance, field)


def validate():
    pass


def evaluate(event, instance, field):
    """
        :py:function:: evaluate(event, instance, field)

        Este método evalua field. Chama a @extract_field.

        This method evaluates the field parameter. Calls @extract_field.

    :param Event event:
    :param Event instance:
    :param dict field:
    :return: value
    :rtype: (str, float, int, bool) raw type found
    """
    value = extract_field(event, instance, field)
    if value is None and (
        _field_mandatory(field) and _father_mandatory(event.json_model_by_action, field)
    ):
        value = "-------------value-not-found-on-model-----------------"
    return value


def extract_field(event, instance, field):
    """
    :py:function:: extract_field(event, instance, field)

    Este método extrai o field de @extract_django_field quando for grupo ou @_get_value.

    This method evaluates the field parameter. Calls @extract_django_field when field is group element,
    otherwise calls @_get_value

    :param Event event:
    :param Event instance:
    :param dict field:
    :return: value
    :rtype: (str, float, int, bool) raw type found
    """
    value = None
    check_name = field.get("django_id", False)
    if not check_name and hasattr(instance, field.get("django_field_name")):
        check_name = field.get("django_field_name", False)

    if not check_name:
        father_of = search_father_of_field_by_name(
            event.json_model_by_action, field.get("father_key_value")
        )
        foreign_key = True
        if (
            father_of.get("foreign_key") == "False"
            or father_of.get("foreign_key", False) is False
        ):
            foreign_key = False
        if foreign_key:
            instance = getattr(event, father_of.get("django_field_name"))
        check_name = (
            field.get("django_field_name")
            if hasattr(instance, field.get("django_field_name"))
            else False
        )

    if check_name:
        value = _get_value(
            event, instance, extract_django_field(event, instance, field, check_name)
        )
    return value


def extract_django_field(event, instance, field, check_name=None):
    django_field = None
    fields = [fld for fld in instance._meta.fields]
    fields += [fld for fld in instance._meta.many_to_many]
    for fld in fields:
        if check_name == fld.attname:
            django_field = fld
            break
    if not django_field:
        for fld in fields:
            if (
                field.get("django_field_name") == fld.attname
                or field.get("django_id") == fld.attname
            ):
                django_field = fld
                break
    if not django_field:
        print("field %s %s" % (field.get("name"), field.get("name_full_key")))
        print("instance %s" % instance)
        print("check_name %s" % check_name)
        print("not exist django field %s" % fld)
        log.warn(
            "not exist django field %s %s"
            % (field.get("name"), field.get("name_full_key"))
        )
        log.warn("not exist django field %s" % fld)
        log.warn("instance %s" % instance)
        log.warn("check_name %s" % check_name)
    return django_field


def extract_django_field_queryset(instance, field_name):
    return getattr(instance, field_name)


def _get_value(event, instance, field_django):
    value = "------------------------------"
    try:
        _type = field_django.get_internal_type()
    except Exception as err:
        print(err)
        print("event %s" % event)
        print("instance %s" % instance)
        print("field_django %s" % field_django)
        raise err

    if _type == "DecimalField":
        value = (
            float(getattr(instance, field_django.name))
            if getattr(instance, field_django.name) is not None
            else None
        )
    elif _type == "DateTimeField":
        value = (
            DateUtils.datetime_to_str(getattr(instance, field_django.name))
            if getattr(instance, field_django.name)
            else None
        )
    elif _type == "DateField":
        value = (
            DateUtils.date_to_str(getattr(instance, field_django.name), "%Y-%m-%d")
            if getattr(instance, field_django.name)
            else None
        )
    elif _type in ("ForeignKey", "OneToOneField"):
        value = getattr(instance, field_django.attname) or None
    elif _type in (
        "BigIntegerField",
        "IntegerField",
        "PositiveIntegerField",
        "PositiveSmallIntegerField",
        "SmallIntegerField",
    ):
        value = (
            int(getattr(instance, field_django.attname))
            if getattr(instance, field_django.attname) is not None
            else None
        )
    else:
        value = getattr(instance, field_django.name)
    return value


def _field_mandatory(field):
    mandatory = OCCURRENCE_MANDATORY == _define_occurrence(field.get("occurrence"))
    return mandatory


def _father_mandatory(json_model, field):
    mandatory = OCCURRENCE_MANDATORY == _check_fathers_occurrence(json_model, field)
    return mandatory


def json_config_by_element(element, json_model):
    xml_tree = element.getroottree()
    path = xml_tree.getelementpath(element)
    dtree = path.split("/")
    tag = dtree[-1]
    father_tag = ""
    if len(dtree) > 1:
        father_tag = dtree[-2]
    key_json = None
    for k in list(json_model):
        r = re.match("^[0-9]+-%s$" % tag, k)
        if r:
            if r and (not father_tag or father_tag == json_model[r.group()]["father"]):
                key_json = r.group()
                break
    return json_model[key_json] if key_json else {}


def deep_remove_group(father, deep=0):
    for child in father.getchildren():
        deep_remove_group(child, deep + 1)
        if not child.getchildren() and child.text is None:
            father.remove(child)


def remove_not_mandatory_group(json_model, xml_tree):
    deep_remove_group(xml_tree.getroot())


def _xml_search_father(tag_name, xml_tree):
    found = None
    for element in xml_tree.getiterator():
        if element.tag == tag_name:
            found = element
    return found
