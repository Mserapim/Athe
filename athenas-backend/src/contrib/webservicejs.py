# -.- coding: utf-8 -.-
import xmlrpc.client
from django.conf import settings
from contrib.controller import DefaultController
from xml.dom import minidom
from django.core.servers.basehttp import FileWrapper

import mimetypes
import SOAPpy
import random
import os

JASPER_SERVER = getattr(settings, "JASPER_SERVER", None)
TRAC = getattr(settings, "TRAC", None)


class WSJasper(DefaultController):
    """
    Procedimentos para geraçãoo de relatórios
    Formato Recebido: url para a geração de relatório codificada em base64
    e tipo de pdf como parâmetros elegantes e os parâmetros para o relatório
    serão passados por post contendo o prefixo PARAM_ antes do nome de cada
    parâmetro
    """

    webservices_wsdl_file = (
        "http://{server}:{port}/jasperserver/services/repository?wsdl".format(
            server=JASPER_SERVER["host"], port=JASPER_SERVER["port"]
        )
    )

    namespace = "http://www.jaspersoft.com/namespaces/django"

    def html_unescape(self, text):
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '"')
        text = text.replace("&#39;", "'")
        text = text.replace("&gt;", ">")
        text = text.replace("&lt;", "<")

        return text

    def get_receptor(self):
        if "format" in self.request.GET:
            receptor = self.request.GET
        else:
            receptor = self.request.POST
        return receptor

    def run_report(self, args=[]):

        receptor = self.get_receptor()

        report_type = receptor["format"]
        url_report = receptor["uri"]

        # organiza os parâmetros ou filtros necessários para a geração do relatório
        rel_param = ""
        for key, value in list(receptor.items()):
            if not key.find("PARAM_") == -1:
                rel_param += (
                    "&lt;parameter name=&quot;"
                    + key[6:]
                    + "&quot;&gt;"
                    + value
                    + "&lt;/parameter&gt;\n"
                )

        request_report = """&lt;request operationName=&quot;runReport&quot;&gt;
                        &lt;argument name=&quot;RUN_OUTPUT_FORMAT&quot;&gt;%s&lt;/argument&gt;
                        &lt;resourceDescriptor name=&quot;%s&quot; wsType=&quot;reportUnit&quot; uriString=&quot;%s&quot; isNew=&quot;false&quot;&gt;
                        &lt;label&gt;&lt;/label&gt;
                        %s
                        &lt;/resourceDescriptor&gt;&lt;/request&gt;""" % (
            report_type,
            url_report,
            url_report,
            rel_param,
        )

        soap_envelope_header = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:ns4="http://www.jaspersoft.com/namespaces/php"
 SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<SOAP-ENV:Body>
<ns4:runReport>
<request xsi:type="xsd:string">"""
        soap_envelope_foot = """
</request></ns4:runReport>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

        request_envelope = "%s%s%s" % (
            soap_envelope_header,
            request_report,
            soap_envelope_foot,
        )
        soapAddress = SOAPpy.SOAPAddress(
            "http://{user}:{password}@{host}:{port}/jasperserver/services/repository?wsdl".format(
                user=JASPER_SERVER["user"],
                password=JASPER_SERVER["password"],
                host=JASPER_SERVER["host"],
                port=JASPER_SERVER["port"],
            )
        )
        httpTransport = SOAPpy.HTTPTransport()
        try:

            resp = httpTransport.call(soapAddress, request_envelope, None)

            lines = resp[0].split("\r\n")

            #            Verifica a resposta xml do jasperserver que mostra se o relatório foi gerado
            self.log.debug("Numero de linhas {0}".format(len(lines)))
            if len(lines) >= 6:
                xml_response = lines[6]
                dom_response = minidom.parseString(xml_response)
                node = dom_response.documentElement

                server_response = node.getElementsByTagName("runReportReturn")[
                    0
                ].lastChild.toxml()
                server_response = self.html_unescape(server_response)
                DOMResponse = minidom.parseString(server_response)

                if (
                    DOMResponse.getElementsByTagName("returnCode")[0].lastChild.data
                    == "0"
                ):
                    #                Procura a posicao do relatório
                    position = -1
                    count = 0

                    for item in lines:
                        if not item.find("<report>") == -1:
                            position = count
                        count += 1

                    #                Escreve o relatório em um arquivo temporário
                    report_response = lines[position + 2 : -2]
                    report_buffer = ""

                    for line in report_response:
                        report_buffer += line

                    random_key = random.randrange(1000, 9999)
                    generate_file = "tmp_" + str(random_key) + "." + report_type.lower()

                    filename = "/tmp/" + generate_file

                    fd = open(filename, "wb")
                    fd.write(report_buffer)
                    fd.close()

                    try:
                        file_download_wrapper = FileWrapper(file(filename))
                        mimetype = mimetypes.guess_type(filename)
                        self.response["Content-Type"] = mimetype[0]
                        self.response["Content-Length"] = os.path.getsize(filename)
                        self.response["Content-Disposition"] = (
                            "attachment; filename=" + generate_file
                        )

                        for buf in file_download_wrapper:
                            self.response.write(buf)

                        if os.path.isfile(filename):
                            os.remove(filename)

                    except Exception as e:
                        self.log.exception(
                            "Erro no processo de download ou remoção do relatório (stream do arquivo) gerado - {0}.".format(
                                e
                            )
                        )
            else:
                self.log.debug(lines)
        except Exception as e:
            self.log.exception(
                "Erro no processo de consumo de fato do relatório do jasperserver - {0}.".format(
                    e
                )
            )


class WSTrac(object):

    def __init__(self):
        self.server = xmlrpc.client.ServerProxy(
            "http://{user}:{password}@{host}:{port}/{context}/login/xmlrpc".format(
                user=TRAC["user"],
                password=TRAC["password"],
                host=TRAC["host"],
                port=int(TRAC["port"]),
                context=TRAC["context"],
            )
        )

    def all_milestones(self):
        return self.server.ticket.milestone.getAll()

    def all_versions(self):
        return self.server.ticket.version.getAll()

    def create_ticket(self, dict, user):
        res = self.server.ticket.create(
            dict["title"],
            "{0}\n\nReportado pelo usuario '''{1}''' com id '''{2}'''.\n{3} {4} <{5}>".format(
                dict["description"],
                user.username,
                user.pk,
                user.first_name,
                user.last_name,
                user.email,
            ),
            {
                "milestone": dict["milestone"],
                "type": "task",
                "priority": "minor",
                "component": "catalog",
                "version": dict["version"],
            },
        )

        return (res > 0), res

    def list_method(self):
        obj = []

        for method in self.server.system.listMethods():
            obj.append(method)

        return obj
