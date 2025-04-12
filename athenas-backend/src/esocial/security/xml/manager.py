# -.- coding: utf-8 -.-
import codecs
import copy
import os

from lxml import etree
from signxml import XMLSigner, methods

from contrib.utils import getLogger
from esocial.security import CERTIFICATE_X509_FILE, PRIVATE_KEY
from esocial.security.xml.const import (
    ESOCIAL_TAG,
    IDE_EMPLOYER_NR_INSC,
    IDE_EMPLOYER_TP_INSC,
    IDE_TRANSMITTER_NR_INSC,
    IDE_TRANSMITTER_TP_INSC,
    SEND_EVENT_BATCH_TAG,
    XML_TO_SEND_TEMPLATE,
)

log = getLogger(__name__)


def _load_data_xml(data, encoding=bytes, to_string=True):
    if (
        not isinstance(data, etree._ElementTree)
        and not isinstance(data, etree._Element)
        and os.path.exists(data)
    ):
        data = etree.parse(data)

    if isinstance(data, etree._ElementTree) or isinstance(data, etree._Element):
        if to_string:
            data = element_to_string(data)
        if encoding:
            data = encoding(data, "utf-8")
    return data


def _load_data_to_string(data):
    return _load_data_xml(data).decode("utf-8")


def _load_data_file(file_path):
    data = ""
    with codecs.open(file_path, "rb") as binary_file:
        data = binary_file.read()
    return data


def _write_data_xml(
    data,
    file_path,
    mode="wb",
    xml_declaration=True,
    encoding="utf-8",
    pretty_print=True,
    to_string=False,
    method="xml",
):
    if isinstance(data, etree._Element):
        data = data.getroottree()
    data.write(
        file_path,
        pretty_print=pretty_print,
        xml_declaration=xml_declaration,
        encoding=encoding,
    )


def element_to_string(data, pretty_print=True, method="xml"):
    return etree.tostring(data, pretty_print=pretty_print, method=method).decode()


def remove_xml_encoding(xml_data):
    return xml_data.replace("<?xml version='1.0' encoding='UTF-8'?>", "")


def data_xml_append_xml_signature(xml_data, xml_signature_template):
    if isinstance(xml_signature_template, etree._ElementTree):
        xml_signature_template = xml_signature_template.getroot()
    if isinstance(xml_data, str):
        xml_data = _load_data_xml(xml_data, encoding="utf-8", to_string=False)
    if isinstance(xml_data, etree._ElementTree):
        xml_data = xml_data.getroot()
    xml_data.append(xml_signature_template)
    return xml_data


def load_from_path(file_path):
    content = ""
    with codecs.open(file_path, "r") as file:
        content = file.read()
    return content


def _signer_process(xml_or_file_path, file_path=""):

    tmp_xml_signed = xml_doc = None
    if isinstance(xml_or_file_path, str) and os.path.exists(xml_or_file_path):
        xml_doc = _load_data_xml(xml_or_file_path, encoding="utf-8", to_string=False)
    elif isinstance(xml_or_file_path, etree._Element):
        xml_doc = etree.ElementTree(xml_or_file_path)
    elif isinstance(xml_or_file_path, etree._ElementTree):
        xml_doc = xml_or_file_path

    if not os.path.exists(CERTIFICATE_X509_FILE) or not os.path.exists(PRIVATE_KEY):
        return '<?xml version="1.0" encoding="UTF-8"?>assinatura nao encontrada'

    cert_str = load_from_path(CERTIFICATE_X509_FILE)
    key_str = load_from_path(PRIVATE_KEY)
    root = xml_doc.getroot()
    tmp_xml_signed = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
    ).sign(root, key=key_str, cert=cert_str)
    if file_path:
        _write_data_xml(tmp_xml_signed, file_path, pretty_print=True)

    return tmp_xml_signed


class XmlTemplate(object):
    """
    Classe para gerar xml a partir de uma estrutura definida em dict:

    estrutura = {
        1: {
            'id': 1,
            'father': 0,
            'tag': 'name',
            'group': False,
            'has_value': True, # para evaluar
            'value': '',
            'attributes': [{'tag': 'name', 'value': ''}]
        },
    }

    De acordo com informações passadas no momento da instância, o método
    dump retorna o xml de duas formas etree.Element ou str.
    """

    TEMPLATE = {}

    def __init__(self, **kwargs):
        self._events = kwargs.get("events", [])
        self._generate_document_by_template()
        self._configure(**kwargs)

    def _configure(self, **kwargs):
        """Este método configura os campos padrão com valores passados no momento da instância."""
        self._document.get(IDE_EMPLOYER_TP_INSC).update(
            {"value": kwargs.get("ide_employer_tp_insc", "")}
        )
        self._document.get(IDE_EMPLOYER_NR_INSC).update(
            {"value": kwargs.get("ide_employer_nr_insc", "")}
        )
        self._document.get(IDE_TRANSMITTER_TP_INSC).update(
            {"value": kwargs.get("ide_transmitter_tp_insc", "")}
        )
        self._document.get(IDE_TRANSMITTER_NR_INSC).update(
            {"value": kwargs.get("ide_transmitter_nr_insc", "")}
        )
        self._document.get(ESOCIAL_TAG).update(
            {"attributes": [{"tag": "xmlns", "value": kwargs.get("xmlns", "")}]}
        )
        self._document.get(SEND_EVENT_BATCH_TAG).update(
            {"attributes": [{"tag": "grupo", "value": kwargs.get("grupo", "")}]}
        )

    def _generate_document_by_template(self):
        """Este método gera um dicionário de eventos que estão em self._events.

        Returns:
            events (dict): dicionário de eventos."""
        self._document = copy.deepcopy(self.TEMPLATE)

        count = 11
        for event in self._events:
            event = event.event
            self._document.update(
                {
                    count: {
                        "id": count,
                        "father": 10,
                        "tag": "evento",
                        "group": False,
                        "many": [],
                        "has_value": "xml",
                        "value": event.xml_signed,
                        "attributes": [{"tag": "Id", "value": event.identifier}],
                    }
                }
            )
            count += 1

    def dump(self, format_dump="element"):
        """
        :py:function:: dump(self, format_dump='element')

        Método que solicita processamento do xml padronizado para ESOCIAL.
        Retorna em formato etree.Element ou str.

        This method processes xml for ESOCIAL.
        It returns according to param format_dump 'element'(tree.Element) or 'string'(str).

        :param str format_dump: 'element' default or 'string'
        :return: etree.Element or str
        :rtype: etree.Element or str
        """
        element = self._dump_etree_element(self._document)
        return (
            etree.tostring(element, encoding="utf-8", pretty_print=True)
            if format_dump == "string"
            else element
        )

    def _dump_etree_element(self, xml_tree=None, field=1):
        """
        :py:function:: _dump_etree_element(self, xml_tree=None, field=1)

        Método que gerencia a criação dos elementos do xml baseado na estrutura.

        This method manages the creation of the xml's element based on structure.

        :param etree.Element xml_tree: xml_tree
        :return: xml_tree
        :rtype: etree.Element
        """
        if field == 1:
            xml_tree = self.create_group_xml(xml_tree, self._document.get(field))
        children = self._children_of_sorted(self._document.get(field))
        keys = list(children)
        keys.sort()
        for key in keys:
            if children.get(key).get("group", False) is True:
                xml_tree_new = self.create_group_xml(xml_tree, children.get(key))
                self._dump_etree_element(xml_tree_new, key)
            else:
                self._create_element_xml(xml_tree, children.get(key))
        return xml_tree

    def _children_of_sorted(self, father):
        """
        :py:function:: _children_of_sorted(self, father)

        Este método ordena os filhos de um campo a partir das chaves.

        This method sorts children of the father parameter using key identity.

        :param dict father:
        :return: children
        :rtype: dict
        """
        children = self._children_of(father)
        return {int(key): children.get(key) for key in children}

    def _children_of(self, field):
        """
        :py:function:: _children_of(self, field)

        Este método encontra os filhos de um campo a partir do field.

        This method finds the children of the field parameter.

        :param dict field:
        :return: children
        :rtype: dict
        """
        children = {}
        for key in self._document.keys():
            if self._document.get(key).get("father") == field.get("id"):
                children.update({key: self._document.get(key)})
        return children

    def create_group_xml(self, xml_tree, field):
        """
        :py:function:: create_group_xml(self, xml_tree, field)

        Este método cria o elemento xml para o elemento tipo grupo.

        This method creates the xml element for group type.

        :param etree.Element xml_tree: xml_tree
        :param str field: name of the field to evaluate
        :return: element
        :rtype: etree.Element
        """
        element = None
        if field and not field.get("father"):
            root = etree.Element(field.get("tag"), **self._attributes(field))
            element = etree.ElementTree(root)
        elif field:
            if hasattr(xml_tree, "getroot"):
                xml_tree = xml_tree.getroot()
            element = self._create_sub_element(xml_tree, field)
        else:
            raise Exception("field not defined")
        return element

    def _create_element_xml(self, xml_tree, field):
        """
        :py:function:: _create_element_xml(self, xml_tree, field)

        Este método cria o elemento xml para o tipo elemento.

        This method creates the xml element for element type.

        :param etree.Element xml_tree: xml_tree
        :param str field: name of the field to evaluate
        :return: element
        :rtype: etree.Element
        """
        has_value = field.get("has_value", False)
        if isinstance(xml_tree, etree._ElementTree) and hasattr(xml_tree, "getroot"):
            xml_tree = xml_tree.getroot()
        self._create_sub_element(xml_tree, field, has_value=has_value)

    def _create_sub_element(self, xml_tree, field, has_value=False):
        """
        :py:function:: _create_sub_element(self, xml_tree, field, has_value=False)

        Este método cria o elemento xml.

        This method creates the xml element.

        :param etree.Element xml_tree: xml_tree
        :param str field: name of the field to evaluate
        :return: element
        :rtype: etree.Element
        """
        element = etree.SubElement(
            xml_tree, field.get("tag"), **self._attributes(field)
        )
        if has_value:
            self._set_value(element, field.get("value", ""))
        return element

    def _set_value(self, element, value):
        try:
            if isinstance(value, etree._ElementTree):
                element.append(value.getroot())
            elif isinstance(value, etree._Element):
                element.append(value)
            else:
                element.text = value
        except Exception as err:
            print(element.tag)
            print(err)
            print(type(value))
            print(value)

    def _attributes(self, field):
        """
        :py:function:: _attributes(self, field)

        Este método encontra os atributos do field.
        Evalua e os retorna.

        This method gets the attributes of the field parameter.
        Evaluate its values. Then returns.

        :param dict field:
        :return: attributes
        :rtype: dict
        """
        return {
            attr.get("tag"): attr.get("value") for attr in field.get("attributes", [])
        }


class XmlToSendTemplate(XmlTemplate):
    """
    Classe para gerar xml que contém informações de assinatura digital.
    Padrão exigido ESOCIAL.

    De acordo com informações passadas no momento da instância, o método
    dump retorna o xml de duas formas etree.Element ou str.
    """

    TEMPLATE = XML_TO_SEND_TEMPLATE
