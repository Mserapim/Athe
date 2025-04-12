from auth.base.forms import ChangePasswordForm
import os
import json

from contrib.decorator import is_public, login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, get_json_engine
from contrib.helpers import err2dict

from rh.employeeaccesscontrol.models import EACEmployee
from rh.gfp.models import Servidor

from rh.servidor.atualizar_infos import AtualizarInfosServidor

log = getLogger(__name__)
json_engine = get_json_engine()


class AUTHEmployeeRestful(RestfulDRY):

    _model = EACEmployee

    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "matricula__icontains",
        "user__username__icontains",
    )

    def atualizar_infos_usuario_mastiff(self, *args):
        obj = {
            "success": True,
            "message": "Conferência de informações do usuário com Mastiff realizada com sucesso.",
        }

        try:
            matricula = self.request.POST.get("matricula")
            servidor = Servidor.objects.get(matricula=matricula)
            AtualizarInfosServidor().atualizar_username(servidor)
        except:
            obj["success"] = False
            obj["message"] = "Erro ao atualizar informações do usuário."

        self.response.write(json_engine.encode(obj))

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)
        _dict_.update(
            {
                "social_name": instance.pessoa_fisica.social_name or "",
            }
        )
        _dict_.update({"email": instance.pessoa_fisica.email_institucional or ""}),
        if instance.user:
            _dict_.update({"is_staff": instance.user.is_staff or ""}),
            _dict_.update({"is_active": instance.user.is_active or ""}),
            _dict_.update({"is_superuser": instance.user.is_superuser or ""}),
            _dict_.update({"username": instance.user.username or ""}),
            _dict_.update({"user_pk": instance.user.pk or ""}),
            _dict_.update(
                {
                    "email_pessoal_verificado": instance.pessoa_fisica.email_pessoal_verificado
                    or ""
                }
            ),

        return _dict_

    @login_required(type="JSON")
    def create_or_update_username(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            valores = {}
            employee_id = self.request.POST.get("employee_id")
            is_staff = self.request.POST.get("is_staff")
            is_active = self.request.POST.get("is_active")
            is_superuser = self.request.POST.get("is_superuser")
            username = self.request.POST.get("username")

            valores = {
                "employee_id": employee_id,
                "is_staff": True if is_staff else False,
                "is_active": True if is_active else False,
                "is_superuser": True if is_superuser else False,
                "username": username,
            }
            instance = self._model.objects.get(pk=employee_id)
            instance.save(valores)

        except Exception as e:
            rst.update(message=f"{e}")

        else:
            rst.update(
                success=True,
                message=f"O usuário:<br> <b> {username} </b><br>foi criado com sucesso.",
            )

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employeeaccesscontrol.authemployee.Manage")'
        )

    @login_required(type="JSON")
    def create_user_by_admin(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            instance = self._model.objects.get(pk=self.request.POST.get("employee"))
            username = instance.user.username if instance.user else None

            if not username:
                instance.create_user_by_admin()
            else:
                raise Exception("O servidor informado já possui um usuário cadastrado.")

        except self._model.DoesNotExist:
            rst.update(
                message="O servidor informado não foi emcontrado na base de dados."
            )

        except Exception as e:
            rst.update(message=f"{e}")

        else:
            rst.update(
                success=True,
                message=f"O usuário do(a) servidor(a):<br> <b> {instance} </b><br>foi criado com sucesso.",
            )

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    @login_required(type="JSON")
    def create_user_ldap(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            instance = self._model.objects.get(pk=self.request.POST.get("employee"))
            username = instance.user.username if instance.user else None
            if username:
                instance.create_user_ldap()
            else:
                raise Exception(
                    "O servidor informado não possui um usuário cadastrado."
                )

        except self._model.DoesNotExist:
            rst.update(
                message="O servidor informado não foi emcontrado na base de dados."
            )

        except Exception as e:
            rst.update(message=f"{e}")

        else:
            rst.update(
                success=True,
                message=f"O servidor(a):<br> <b> {instance} </b><br>foi criado com sucesso.",
            )

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    @login_required(type="JSON")
    def reset_user_password(self, args=[]):

        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            instance = self._model.objects.get(pk=self.request.POST.get("employee"))
            username = instance.user.username if instance.user else None
            if username:
                instance.reset_user_password()
            else:
                raise Exception(
                    "O servidor informado não possui um usuário cadastrado."
                )

        except self._model.DoesNotExist:
            rst.update(
                message="O servidor informado não foi emcontrado na base de dados."
            )

        except Exception as e:
            rst.update(message=f"{e}")

        else:
            rst.update(
                success=True,
                message=f"A senha do(a) servidor(a):<br> <b> {instance} </b><br>foi resetada com sucesso.",
            )

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)

    @is_public()
    def change_password(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        body = self.request.body
        form = ChangePasswordForm(json.loads(body.decode()))

        if form.is_valid():
            data = form.cleaned_data

            try:
                if data.get("new_password") != data.get("password_confirmation"):
                    raise Exception("Senhas não conferem")

                if not isinstance(data.get("username"), str) and not isinstance(
                    data.get("current_password"), str
                ):
                    raise Exception(
                        "Credenciais inválidas. Insira corretamente o usuário e senha atuais."
                    )

                employee = self._model.objects.get(
                    user__is_active=True, user__username=data.get("username")
                )

                employee.change_password(
                    data.get("current_password"), data.get("password_confirmation")
                )

            except self._model.DoesNotExist as e:
                log.exception(e)
                rst.update(message="Usuário não encontrado na base de dados.")
            except Exception as e:
                log.exception(e)
                rst.update(message=str(e))
            else:
                message = "Senha alterada com sucesso."
                log.info(message)
                rst.update(success=True, message=message)
        else:
            rst.update(
                msg="Corrija o(s) seguinte(s) problema(s)", errors=err2dict(form)
            )

        renderer = self.get_renderer(self.request.META.get("HTTP_ACCEPT", "text/json"))
        renderer(rst)
