# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.contrib.auth import models as auth_model
from contrib.router import __router_extract_dictionary__ as router_extract_dictionary
from contrib.utils import getLogger, DateUtils
from contrib.decorator import to_search
from django.conf import settings
from contrib.utils import get_json_engine
from datetime import date, datetime
from decimal import Decimal

CONTEXT = settings.CONTEXT
json = get_json_engine()


CHOICE_LEVEL = (
    (0, "CHECK_ACCESS"),
    (1, "ADD"),
    (2, "UPDATE"),
    (3, "PROFILE_CHANGEPASSWORD"),
    (4, "DELETE"),
    (5, "PROFILE_CHANGEINFORMATION"),
    (8, "AUDIT_VIEW"),
    (16, "AUDIT_UPDATE"),
    (32, "AUTENTICATE_LOGIN"),
    (64, "AUTENTICATE_LOGOUT"),
    ############### PROTOCOLO ###############
    (65, "PROTOCOLO_EDOCBOX_DELETE"),
    (66, "PROTOCOLO_EDOCBOX_RECEBER"),
    (67, "PROTOCOLO_EDOCBOX_NEW_COMMIT"),
    (68, "PROTOCOLO_EDOCBOX_NEW_COMMIT_MOV"),
    (69, "PROTOCOLO_EDOCBOX_NEW_COMMIT_IMPRIMIR"),
    (70, "PROTOCOLO_EDOCBOX_INSERIR_MOVIMENTACAO"),
    (72, "PROTOCOLO_EDOCBOX_MARCAR_NAO_RECEBIDO"),
    ############### RH ###############
    (71, "RH_SERVIDOR_ESPECIALIZADO"),
    (96, "RH_FRS_CONFIGURACAO"),
    (97, "RH_FRS_PA_CREATE"),
    (98, "RH_FRS_PAS_CREATE"),
    (99, "RH_FRS_GERENCIAMENTO"),
    (100, "RH_FRS_MARCACAO"),
    (101, "RH_FRS_AUTORIZACAO"),
    (128, "RH_CONFIGURATION_COMMIT"),
    ############### GFP ###############
    (256, "GFP_LANCADOR_RECALC"),
    (512, "GFP_LANCADOR_EVENT_INFORMATION"),
    (1024, "GFP_LANCADOR_EVENT_ADD"),
    (2048, "GFP_LANCADOR_EVENT_DELETE"),
    ############# CONSURSO ##############
    (130, "CONCURSO_HOMOLOGAR_INSCRICAO"),
    (131, "CONCURSO_DEFERIR_RECURSO"),
    ############### GECAP ###############
    (2049, "GECAP_CREATE_CAPACITACAO_INVESTIMENTO"),
    (2050, "GECAP_UPDATE_CAPACITACAO_INVESTIMENTO"),
    (2051, "GECAP_DELETE_CAPACITACAO_INVESTIMENTO"),
    (2052, "GECAP_CREATE_INSCRICAO"),
    (2053, "GECAP_UPDATE_INSCRICAO"),
    (2054, "GECAP_DELETE_INSCRICAO"),
    (2055, "GECAP_CREATE_INSCRICAO_INVESTIMENTO"),
    (2056, "GECAP_UPDATE_INSCRICAO_INVESTIMENTO"),
    (2057, "GECAP_DELETE_INSCRICAO_INVESTIMENTO"),
    (2058, "GECAP_INSCRICAO_HOMOLOGACAO"),
    (2059, "GECAP_INSCRICAO_CERTIFICADO"),
    (2060, "GECAP_COPY_INSCRICAO_INVESTIMENTO"),
    ################# WEB CMS ##################
    (2000, "CMS_CREATE_AREA"),
    (2001, "CMS_UPDATE_AREA"),
    (2002, "CMS_DELETE_AREA"),
    (2003, "CMS_CREATE_LINK"),
    (2004, "CMS_UPDATE_LINK"),
    (2005, "CMS_DELETE_LINK"),
    (2006, "CMS_CREATE_POST"),
    (2007, "CMS_UPDATE_POST"),
    (2008, "CMS_DELETE_POST"),
    (2009, "CMS_CREATE_FILE"),
    (2010, "CMS_UPDATE_FILE"),
    (2011, "CMS_DELETE_FILE"),
    (2012, "CMS_CREATE_IMAGE"),
    (2013, "CMS_UPDATE_IMAGE"),
    (2014, "CMS_DELETE_IMAGE"),
    (2015, "CMS_CREATE_AUDIO"),
    (2016, "CMS_UPDATE_AUDIO"),
    (2017, "CMS_DELETE_AUDIO"),
    (2018, "CMS_CREATE_VIDEO"),
    (2019, "CMS_UPDATE_VIDEO"),
    (2020, "CMS_DELETE_VIDEO"),
    (2021, "CMS_CREATE_PUBLICATION"),
    (2022, "CMS_DELETE_PUBLICATION"),
    # (2023, 'CMS_CREATE_CATEGORY'),
    # (2024, 'CMS_UPDATE_CATEGORY'),
    # (2025, 'CMS_DELETE_CATEGORY'),
    # (2026, 'CMS_CATEGORIZE'),
    # (2027, 'CMS_UNCATEGORIZE'),
    (2028, "CMS_RELATE_USER"),
    (2029, "CMS_UNRELATE_USER"),
    (2030, "CMS_RELATE_FILE"),
    (2031, "CMS_RELATE_IMAGE"),
    (2032, "CMS_RELATE_AUDIO"),
    (2033, "CMS_RELATE_VIDEO"),
    (2034, "CMS_CREATE_POLL"),
    (2035, "CMS_UPDATE_POLL"),
    (2036, "CMS_DELETE_POLL"),
    (2037, "CMS_CREATE_CHOICE"),
    (2038, "CMS_UPDATE_CHOICE"),
    (2039, "CMS_DELETE_CHOICE"),
    (2040, "CMS_VOTE_POLL"),
    (2041, "CMS_CREATE_PROSECUTOR_ACTION_STATUS"),
    (2042, "CMS_UPDATE_PROSECUTOR_ACTION_STATUS"),
    (2043, "CMS_DELETE_PROSECUTOR_ACTION_STATUS"),
    (2044, "CMS_CREATE_PROSECUTOR_ACTION"),
    (2045, "CMS_UPDATE_PROSECUTOR_ACTION"),
    (2046, "CMS_DELETE_PROSECUTOR_ACTION"),
    ################# COMMON SAFE POLL ##################
    (3001, "COMMON_SAFE_POLL_CREATE"),
    (3002, "COMMON_SAFE_POLL_UPDATE"),
    (3003, "COMMON_SAFE_POLL_DELETE"),
    (3004, "COMMON_SAFE_POLL_CHOCIE_CREATE"),
    (3005, "COMMON_SAFE_POLL_CHOCIE_UPDATE"),
    (3006, "COMMON_SAFE_POLL_CHOCIE_DELETE"),
    (3007, "COMMON_SAFE_POLL_PUBLICATION"),
    (3008, "COMMON_SAFE_POLL_VOTE"),
    (3009, "COMMON_SAFE_POLL_COUNT"),
    (3010, "COMMON_SAFE_POLL_BLOCK_USER"),
    (3011, "COMMON_SAFE_POLL_REMOVE_BLOCKED_USER"),
)

CHOICE_STATUS = (
    (0, "FAILED"),
    (1, "SUCCESS"),
    (2, "WARNING"),
)


@to_search(
    [
        {"name": "user__username", "type": "text"},
        {"name": "dt", "type": "date"},
        {"name": "level", "type": "choices"},
        {"name": "controller", "type": "text"},
        {"name": "action", "type": "text"},
    ]
)
class LineLog(models.Model):
    user = models.ForeignKey(
        auth_model.User, blank=True, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    dt = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.IntegerField(choices=CHOICE_LEVEL, null=True, db_index=True)
    controller = models.CharField(max_length=200, null=True, db_index=True)
    action = models.CharField(max_length=200, null=True, db_index=True)
    status = models.IntegerField(choices=CHOICE_STATUS, null=True)
    json_description = models.TextField(null=True)
    host_address = models.CharField(max_length=100, null=True)
    host_name = models.CharField(max_length=250, null=True)

    class Meta:
        ordering = ("-dt",)

    def __init__(self, *args, **kw):
        log = getLogger("LineLog")
        request = None
        if "request" in kw:
            request = kw["request"]
            del kw["request"]

        super(LineLog, self).__init__(*args, **kw)
        request is not None and self.read_request(request)

    @staticmethod
    def prepare_json(obj):
        log = getLogger("LineLog")
        nobj = None

        if isinstance(obj, (list, tuple)):
            nobj = []
            for value in obj:
                if isinstance(value, (tuple, list, dict)):
                    nobj.append(LineLog.prepare_json(value))
                elif isinstance(value, datetime):
                    nobj.append(DateUtils.datetime_to_str(value))
                elif isinstance(value, date):
                    nobj.append(DateUtils.date_to_str(value))
                elif isinstance(value, Decimal):
                    nobj.append("%s" % value)
                else:
                    nobj.append(value)
        elif isinstance(obj, dict):
            nobj = {}
            for key, value in list(obj.items()):
                if isinstance(value, (tuple, list, dict)):
                    nobj.update({key: LineLog.prepare_json(value)})
                elif isinstance(value, datetime):
                    nobj.update({key: DateUtils.datetime_to_str(value)})
                elif isinstance(value, date):
                    nobj.update({key: DateUtils.date_to_str(value)})
                elif isinstance(value, Decimal):
                    nobj.update({key: "%s" % value})
                else:
                    nobj.update({key: value})

        return nobj

    @transaction.atomic
    def save(self, force_insert=False, force_update=False):
        log = getLogger("LineLog")

        try:
            self.json_description = json.encode(
                LineLog.prepare_json(self.json_description)
            )
        except Exception as e:
            self.json_description = "__BUG__"
            log.exception(e)

        try:
            super(LineLog, self).save(force_insert, force_update)
        except Exception as e:
            log.exception(e)
        except TypeError as e:
            pass

    #            raise e

    def read_request(self, request):
        log = getLogger("LineLog")
        url_path = ""

        log.debug("path is %s" % request.path)

        try:
            if request.path.index("/{0}/".format(CONTEXT)) == 0:
                url_path = request.path
            elif request.path[0] == "/":
                url_path = "/{0}{1}".format(CONTEXT, request.path)
            else:
                url_path = "/{0}/{1}".format(CONTEXT, request.path)
        except:
            if request.path[0] == "/":
                url_path = "/{0}{1}".format(CONTEXT, request.path)
            else:
                url_path = "/{0}/{1}".format(CONTEXT, request.path)

        try:
            dic = router_extract_dictionary(url_path[len("/{0}/".format(CONTEXT)) :])

            self.action = dic["action"]
            self.controller = dic["controller"]
            self.host_address = request.META["REMOTE_ADDR"]

            try:
                self.host_name = request.META["REMOTE_HOST"]
            except:
                self.host_name = ""

            self.json_description = {
                "get": dict(request.GET),
                "post": dict(request.POST),
            }

            if "passwd" in self.json_description["get"]:
                self.json_description["get"]["passwd"] = "***"
            if "passwd" in self.json_description["post"]:
                self.json_description["post"]["passwd"] = "***"

            self.user = request.user if request.user.is_authenticated else None

        except Exception as e:
            log.exception(e)


#    def __unicode__(self):
#        return u"{user} no momento {mt} solicitou {level}, no {controller} com a {action} e obteve {status}".format(
#            user = unicode(self.user),
#            mt = self.dt.strftime(""),
#            level = self.get_level_display(),
#            status = self.get_status_display(),
#            controller = self.controller,
#            action = self.action
#        )
