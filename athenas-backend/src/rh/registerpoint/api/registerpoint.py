# -*- coding: utf-8 -*-
from contrib.controller import DefaultController
from contrib.utils import getLogger, get_json_engine
from rh.registerpoint.models import MarkPoint
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
from rh.registerpoint.utils import markpoint
from datetime import datetime
from standard.models import ConfigPoint
import ipaddress
import pytz

log = getLogger(__name__)
json = get_json_engine()


class RHRegisterPoint(DefaultController):

    def check_permission(self, user, action, app_label, object_name):
        perm = "%(app_label)s.%(action)s_%(object_name)s" % vars()
        perm = perm.lower()

        log.info("check %s permission for %s" % (perm, user))
        if user.has_perm(perm) is True:
            log.info("user %s has permission %s" % (user, perm))
            return True
        else:
            log.warn("permission %s dained for %s" % (perm, user))
            return False

    def _check_ipaddress(self, ip):
        for config in ConfigPoint.objects.filter():
            if ipaddress.ip_address(ip) in ipaddress.ip_network(config.network, False):
                return True
        return False

    def _get_ipaddress(self):
        ip = None
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip

    def validate_ip_address(self, ip):
        if not self._check_ipaddress(ip):
            raise Exception(f"{ip} - IP inválido para registro de ponto.")
        return True

    @login_required("JSON")
    def register_point(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            can = self.check_permission(
                self.request.user,
                "add",
                MarkPoint._meta.app_label,
                MarkPoint._meta.object_name,
            )
            if can is False:
                obj.update(
                    message="Você não tem permissão para bater ponto %s."
                    % MarkPoint._meta.object_name
                )
            else:
                employee = employee_from_user(get_current_user())
                marks = MarkPoint.objects.filter(
                    day=datetime.today().date(), employee=employee
                ).count()
                ip = self._get_ipaddress()
                self.validate_ip_address(ip)
                vreturn1, vreturn2 = markpoint.register(employee)
                # vreturn1,vreturn2 = ['S',"PONTO REGISTRADO COM SUCESSSO"]
                if vreturn1 == "S":
                    if marks < 4:
                        instance = MarkPoint(
                            mark=datetime.now(pytz.timezone("America/Cuiaba")).time(),
                            employee=employee_from_user(get_current_user()),
                            day=datetime.now(pytz.timezone("America/Cuiaba")).date(),
                            ip=ip,
                        )
                        instance.save()
                        obj.update(
                            success=True,
                            message=vreturn2,
                            mark=MarkPoint.objects.filter(
                                day=datetime.today().date(), employee=employee
                            ).count()
                            % 2,
                        )
                    else:
                        obj.update(
                            success=False,
                            message="JÁ FORAM REGISTRADAS 4 BATIDAS NO DIA.",
                            mark=marks % 2,
                        )
                else:
                    obj.update(success=False, message=vreturn2, mark=marks % 2)
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e), mark=marks % 2)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def get_mark(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda!"}
        try:
            marks = MarkPoint.objects.filter(
                day=datetime.today().date(),
                employee=employee_from_user(get_current_user()),
            ).count()

            obj.update(success=True, message="Consultar marcações.", mark=marks % 2)
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
