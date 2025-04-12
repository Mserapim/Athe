# -*- coding: utf-8 -*-
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User

from contrib.newrest import Restful
from contrib.utils import getLogger, employee_from_user
from contrib.decorator import deprecated

from rh.profile.models import JobProfile

log = getLogger(__name__)


class AUTHUserRestful(Restful):

    _model = User

    force_upper = False

    full_text_index = (
        "username__icontains",
        "email__icontains",
        "first_name__icontains",
        "last_name__icontains",
        "servidor__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__icontains",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("auth.UserManage")')

    def _filter_eval_value(self, value):
        map_value = {"on": True, "off": False}

        return map_value.get(value, value)

    def get_params(self, *args, **kwargs):
        params = super(AUTHUserRestful, self).get_params(*args, **kwargs)

        if "is_active" in params:
            params.update(is_active=params.get("is_active", "off").lower() == "on")

        if "is_staff" in params:
            params.update(is_staff=params.get("is_staff", "off").lower() == "on")

        if "is_superuser" in params:
            params.update(
                is_superuser=params.get("is_superuser", "off").lower() == "on"
            )

        log.debug(params)

        return params

    def get_query(self, *args, **kwargs):
        return (
            super(AUTHUserRestful, self).get_query(*args, **kwargs).order_by("username")
        )

    def change_userinfo(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        self._read_special_verb()

        if not self.request.user.has_perm("auth.can_manage_username"):
            rst.update(
                message='Usuário "%s" não tem permissão para executar esta ação.'
            )
        else:
            try:
                query = self.get_query().filter(
                    username=self.request.PUT.get("oldusername")
                )
                if query.count() == 1:
                    query.update(
                        username=self.request.PUT.get("username"),
                        email=self.request.PUT.get("email"),
                    )
                    rst.update(
                        success=True, message="Informações atualizadas com sucesso."
                    )
                else:
                    rst.update(message="A requisição inválida.")
            except Exception as e:
                rst.update(message=str(e))

        self.renderer(rst)

    def toggle_active(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            self.Model.objects.filter(pk__in=self.request.PUT.getlist("pk__in")).update(
                is_active=(self.request.PUT.get("is_active", "off") == "on")
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def toggle_staff(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            self.Model.objects.filter(pk__in=self.request.PUT.getlist("pk__in")).update(
                is_staff=(self.request.PUT.get("is_active", "off") == "on")
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def toggle_superuser(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        if not self.request.user.is_superuser:
            rst.update(
                message="Pela interface só é possivel determinar que um usuário é administrador a traves de outro "
                + "usuário administrador. Caso seja o primeiro usuário administrador recorra ao shell do django."
            )
        else:
            try:
                self._read_special_verb()
                self.Model.objects.filter(
                    pk__in=self.request.PUT.getlist("pk__in")
                ).update(
                    is_superuser=(self.request.PUT.get("is_active", "off") == "on")
                )
            except Exception as e:
                rst.update(message=str(e))
            else:
                rst.update(success=True)

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def user_icon_active(self, user):
        if user.is_active:
            return {"iconCls": "icon-core icon-core-success", "title": "Usuário atívo"}
        else:
            return {"iconCls": "icon-core icon-core-blank", "title": "Usuário inatívo"}

    def user_icon_staff(self, user):
        if user.is_staff:
            return {
                "iconCls": "icon-core icon-core-users",
                "title": "Usuário da equipe",
            }
        else:
            return {
                "iconCls": "icon-core icon-core-blank",
                "title": "Usuário não é da equipe",
            }

    def user_icon_superuser(self, user):
        if user.is_superuser:
            return {
                "iconCls": "icon-core icon-core-admin",
                "title": "Usuário administrador",
            }
        else:
            return {"iconCls": "icon-core icon-core-blank", "title": "Usuário comum"}

    @deprecated
    def employee_from_user(self, user):
        return employee_from_user(user)

    def model_to_dict(self, instance):
        params = Restful.model_to_dict(self, instance)

        employee = employee_from_user(instance, False)

        """
            FIXEME: Sugiro alterar o valor da propriedade pessoa_nome para outro
                    label, e suprimir o label pessoa_nome_real
        """
        params.update(
            icons=[
                self.user_icon_active(instance),
                self.user_icon_staff(instance),
                self.user_icon_superuser(instance),
            ],
            username=instance.username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            is_active=instance.is_active,
            is_staff=instance.is_staff,
            email=instance.email,
            is_superuser=instance.is_superuser,
            servidor=employee.pk if employee else None,
            servidor_ativo=employee.ativo if employee else False,
            servidor_unicode=str(employee) if employee else None,
            servidor_matricula=employee.matricula if employee is not None else "",
            pessoa_nome=(
                employee.pessoa_fisica.nome
                if employee is not None
                else instance.username
            ),
            pessoa_nome_real=employee.pessoa_fisica.nome if employee else None,
        )

        return params

    def action_info_user_servidor(self, args=[]):
        """Action que retorna informações do usuário servidor, como lotação, ramal, cidade...
        :param args: Usuário pk
        :type args: int
        """
        obj = {
            "result": {},
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            usuario = self.Model.objects.get(pk=args[0])
            servidor = employee_from_user(usuario)
            if not servidor:
                raise Exception("Usuário não é servidor ativo")
            elif not servidor.workplace_current:
                raise Exception("Servidor não possui lotação atual")

            result = {
                "nome": servidor.pessoa_fisica.nome,
                "lotacao": servidor.workplace_current.nome,
                "membro": "Sim" if servidor.membro else "Não",
                "cidade": servidor.workplace_current.localidade.nome,
                "ramal": "",
            }
            if servidor.workplace_current.phone.all().exists():
                result.update(ramal=servidor.workplace_current.phone.all()[0].numero)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(
                {
                    "result": result,
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def cleanup(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            users = self.Model.objects.filter(pk__in=self.request.PUT.getlist("pk__in"))
            for user in users:
                path_menu = os.path.join(settings.CACHE_PATH, "menu", str(user.pk))
                if os.path.exists(path_menu):
                    shutil.rmtree(path_menu)

                JobProfile.sync_grants_for_user_all_profiles(user=user)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)
