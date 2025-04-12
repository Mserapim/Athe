# -*- coding:utf-8 -*-
import random

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import transaction

from contrib.controller import DefaultController
from contrib.helpers import err2dict
from contrib.utils import getLogger, LdapUser

from .models import PasswordChangeRequest
from .forms import UserCheckForm, ResetPasswordForm, ChangePasswordForm

log = getLogger()


class AuthBase(DefaultController):

    def __init__(self, *args, **kwargs):
        super(AuthBase, self).__init__(*args, **kwargs)

        self.set_restful("json")
        self.response["content-type"] = "text/javascript; charset=utf-8"

    def __send_verification_code(self, email, key):

        if not getattr(settings, "DEBUG", False):
            email_params = {
                "subject": "Requisição de recuperação de senha",
                "message": """
                Foi realizada uma Solicitação de recuperação de senha para o usuário associado a este email.

                Para alterar sua senha copie o código abaixo e insira-o no campo "código de verificação".

                %s

                Ministério Público do Estado do Tocantins - Departamento de Tecnologia da Informação

                """
                % key,
                "from_email": "sistemas@mpto.mp.br",
                "recipient_list": [email],
            }

            return send_mail(**email_params)
        else:
            log.info("Faking sending email to %s. key => %s" % (email, key))

    def __truncate_email(self, email):
        nose, tail = email.split("@")
        size = len(nose)

        truncate_amount = int(size / 2)
        if size > 4:
            truncate_amount += 1
        arr = list(range(size))
        nose = list(nose)

        for i in range(truncate_amount):
            index = random.choice(arr)
            arr.remove(index)
            nose[index] = "*"

        return "%s@%s" % ("".join(nose), tail)

    def recover(self, args=[]):
        response = dict(
            success=False, msg="Não foi executar recuperação de senha.", errors=[]
        )
        form = UserCheckForm(self.request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                user = User.objects.filter(username=d.get("username")).first()
                if not user:
                    raise Exception("Usuário inválido.")

                personal_email = user.servidor.pessoa_fisica.email_institucional
                if not personal_email:
                    raise Exception(
                        """É necessário um email institucional cadastrado para o procedimento de recuperação de senha.
                        Favor procurar o Departamento de GESTÃO DE PESSOAS."""
                    )

                password_change_req = PasswordChangeRequest(user=user)

                with transaction.atomic():
                    password_change_req.save()

                    self.__send_verification_code(
                        personal_email, password_change_req.key
                    )

            except Exception as e:
                log.exception(e)
                response.update(msg=str(e))
            else:
                message = (
                    "Um código de verificação foi encaminhado para o seu email institucional %s"
                    % self.__truncate_email(personal_email)
                )
                log.info(message)
                response.update(success=True, msg=message)
        else:
            response.update(
                msg="Corrija o(s) seguinte(s) problema(s)", errors=err2dict(form)
            )

        self.render(response)

    def reset(self, args=[]):
        response = dict(
            success=False, msg="Não foi executar a redefinição de senha.", errors=[]
        )
        form = ResetPasswordForm(self.request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                if d.get("new_password") != d.get("password_confirmation"):
                    raise Exception("Senhas não conferem")

                ldap_user = LdapUser()
                ldap_user.reset_password(
                    d.get("username"), d.get("key"), d.get("password_confirmation")
                )

            except Exception as e:
                log.exception(e)
                response.update(msg=str(e))
            else:
                message = "Senha restaurada com sucesso."
                log.info(message)
                response.update(success=True, msg=message)
        else:
            response.update(
                msg="Corrija o(s) seguinte(s) problema(s)", errors=err2dict(form)
            )

        self.render(response)

    def change_password(self, args=[]):
        response = dict(
            success=False, msg="Não foi executar alteração de senha.", errors=[]
        )
        form = ChangePasswordForm(self.request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                if d.get("new_password") != d.get("password_confirmation"):
                    raise Exception("Senhas não conferem")

                ldap_user = LdapUser()
                ldap_user.change_password(
                    d.get("username"),
                    d.get("current_password"),
                    d.get("password_confirmation"),
                )

            except Exception as e:
                log.exception(e)
                response.update(msg=str(e))
            else:
                message = "Senha alterada com sucesso."
                log.info(message)
                response.update(success=True, msg=message)
        else:
            response.update(
                msg="Corrija o(s) seguinte(s) problema(s)", errors=err2dict(form)
            )

        self.render(response)
