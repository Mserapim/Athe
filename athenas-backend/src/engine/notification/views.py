# -.- coding: utf-8 -.-
from engine.notification.models import (
    Message,
    Notification,
    TYPE_MSG_CHOICES,
    TYPE_NOTIFY_CHOICES,
    STATUS_NOTIFY_CHOICES,
)
from django import forms
from contrib import extjs
from contrib.utils import get_json_engine
from contrib.middleware import get_current_user
from contrib import decorator
from datetime import *
from contrib.utils import DateUtils, getLogger, employee_from_user
from django.db.models import Q
from rh.models import Servidor, MovimentacaoPosse
from threading import Thread

log = getLogger(__name__)
json = get_json_engine()


class ENGMessageAdmin(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Message

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "MID", "sortable": True, "dataIndex": "mid", "width": 200},
            {
                "header": "Cabeçalho",
                "sortable": True,
                "dataIndex": "header",
                "width": 150,
            },
            {
                "header": "Mensagem",
                "sortable": False,
                "dataIndex": "message",
                "width": 400,
            },
            {"header": "Tipo", "sortable": True, "dataIndex": "type", "width": 80},
            #            {"header": "Parâmetros Padrão", "sortable": False, "dataIndex": "default_params", "width": 300},
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Mensagens",
        "LIST": "Mensagens",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }

    def get_query(self, args=[]):
        """ """
        return Message.objects.exclude(mid__startswith="__MSG")


class ENGNotification(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Notification

    def get_columns_grid(self, args=[]):

        obj = []

        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Notificações",
        "LIST": "Notificações",
        "NEW": "Novo",
        "EDIT": "Editar",
        "DELETE": "Apagar",
        "FILTER": "Filter",
    }

    @decorator.login_required(type="JSON")
    def read(self, args=[]):
        result = {
            "success": False,
        }

        employee = employee_from_user(get_current_user())
        notif_id = self.request.POST.getlist("notif")

        if employee and len(notif_id) > 0:
            for notif in Notification.objects.filter(pk__in=notif_id):
                try:
                    notif.status = 8
                    notif.save()
                except Exception as e:
                    self.log.exception(e)

            result["success"] = True
        else:
            result["error"] = "Usuário ou Notificação não encontrada"

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))


class ENGNotificationCustom(extjs.ExtWidget):

    def check_chefe(self):
        chefe = False

        try:
            s = employee_from_user(self.request.user)
        except:
            chefe = False
        else:
            chefe = s.responsavel_por.exists()

        return chefe

    @decorator.login_required("JSON")
    def is_chefe(self, args=[]):
        obj = {"chefe": self.check_chefe()}

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @decorator.login_required("JSON")
    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.engine.notification.CustomView()")

    def store(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        if args[0] == "in":
            obj = self.get_store_in(args)
        elif args[0] == "out":
            obj = self.get_store_out(args)
        elif args[0] == "visualizacao":
            obj = self.get_store_visualizacao(args)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_in(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        start = int(self.request.POST.get("start", 0))
        end = start + int(self.request.POST.get("limit", 20))

        query = Notification.objects.filter(
            Q(target_id=employee_from_user(get_current_user()).pk)
            | Q(target_id=get_current_user().pk)
        ).order_by("-created_at")

        keyword = self.request.POST.get("keyword", "")
        if keyword:
            query = query.filter(
                Q(msg__header__icontains=keyword) | Q(msg__message__icontains=keyword)
            )

        obj["totalRows"] = query.count()
        for notif in query[start:end]:
            obj["result"].append(
                {
                    "codigo": notif.pk,
                    "data": DateUtils.date_to_str(notif.created_at),
                    "origem": str(notif.sender) if notif.sender else "SYS",
                    "destino": str(notif.target),
                    "assunto": str(notif.msg.header),
                    "msg": str(notif.formatMsg()),
                    "type_msg": notif.msg.type,
                    "type_notify": notif.type,
                    "status_notify": notif.status,
                }
            )
        return obj

    def get_store_out(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        query = Notification.objects.filter(
            Q(sender_id=employee_from_user(get_current_user()).pk)
            | Q(sender_id=get_current_user().pk)
        ).order_by("-created_at")
        keyword = self.request.POST.get("keyword", "")
        if keyword:
            query = query.filter(
                Q(msg__header__icontains=keyword) | Q(msg__message__icontains=keyword)
            )

        start = int(self.request.POST.get("start", 0))
        end = start + int(self.request.POST.get("limit", 20))

        obj["totalRows"] = query.count()
        for notif in query[start:end]:
            obj["result"].append(
                {
                    "codigo": notif.pk,
                    "data": DateUtils.date_to_str(notif.created_at),
                    "origem": str(notif.sender) if notif.sender else "SYS",
                    "destino": str(notif.target),
                    "assunto": str(notif.msg.header),
                    "msg": str(notif.formatMsg()),
                    "type_msg": notif.msg.type,
                    "type_notify": notif.type,
                    "status_notify": notif.status,
                }
            )
        return obj

    def get_store_visualizacao(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        return obj

    def enviar(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            try:
                mensagem = Message(
                    header=self.request.POST.get("header"),
                    message=self.request.POST.get("message"),
                )
                mensagem.save()
                Enviar(
                    mensagem=mensagem,
                    sender=employee_from_user(self.request.user),
                    servidores=self.request.POST.getlist("servidor"),
                    types=[
                        (
                            "ONTOP"
                            if self.check_chefe() is True
                            and self.request.POST.get("ontop") == "true"
                            else "SYS"
                        )
                    ],
                ).start()
            except:
                obj["success"] = False
                obj["message"] = "Erro no envio! Mensagem não pode ser criada!"
                raise
            # TODO: IMPLEMENTAR NOTIFICAÇÃO DE ERROS
            #            self.notification_err(servidor, err)
            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
        except Exception as e:
            self.log.exception(e)


class Enviar(Thread):

    def __init__(self, mensagem, sender, servidores, types=("SYS",)):
        Thread.__init__(self)
        self.mensagem = mensagem
        self.sender = sender
        self.servidores = servidores
        self.types = types

        log.debug(servidores)

    def run(self):
        self.enviar()

    def enviar(self):
        qs = []
        for servidor in self.servidores:
            log.info("send to %s", servidor)
            if servidor == "TODOS":
                for servidor in Servidor.objects.filter():
                    self.notification(servidor)
            elif servidor == "ATIVOS":
                qs.append(Q(ativo=True))
            elif servidor == "INATIVOS":
                qs.append(Q(ativo=False))
            elif servidor == "MEMBROS":
                qs.append(
                    Q(
                        type_by_possession__in=[
                            "MBR",
                            "MEL",
                            "MCM",
                            "MEC",
                            "MBR2",
                            "MEL2",
                            "MCM2",
                            "MEC2",
                        ]
                    )
                )
            elif servidor == "PROCURADORES":
                qs.append(Q(type_by_possession__in=["MBR2", "MEL2", "MCM2", "MEC2"]))
            elif servidor == "AME-DIREITO":
                qs.append(
                    Q(
                        pk__in=MovimentacaoPosse.objects.filter(
                            quadro__cargo__cargos_estrutura__estrutura_salarial__codigo="AME",
                            quadro__especialidade__nome="CIÊNCIAS JURÍDICAS",
                            ativo=True,
                        ).values("servidor")
                    )
                )
            elif servidor == "AMI-DIREITO":
                qs.append(
                    Q(
                        pk__in=MovimentacaoPosse.objects.filter(
                            quadro__cargo__cargos_estrutura__estrutura_salarial__codigo="AMI",
                            quadro__especialidade__nome="CIÊNCIAS JURÍDICAS",
                            ativo=True,
                        ).values("servidor")
                    )
                )
            elif servidor == "COMISSIONADO":
                qs.append(
                    Q(
                        pk__in=MovimentacaoPosse.objects.filter(
                            quadro__cargo__cargos_estrutura__estrutura_salarial__codigo="DAM",
                            ativo=True,
                        ).values("servidor")
                    )
                )
            else:
                self.notification(Servidor.objects.get(pk=int(servidor or 0)))
        if qs:
            q = None
            for qn in qs:
                q = qn if q is None else Q(q | qn)

            query = Servidor.objects.filter(q)
            for servidor in query:
                self.notification(servidor)

    def notification(self, servidor):
        log.info("Notificando %s", servidor.pessoa_fisica)
        Notification.notify(
            msg_or_mid=self.mensagem,
            target=servidor,
            sender=self.sender,
            types=self.types,
        )

    def notification_err(self, servidor, result, mensagem_undelivered):
        mensagem = Message(
            header="Erro no envio!",
            message='Verificar email institucional para ver relação de usuários que não receberam a mensagem "%s"'
            % mensagem_undelivered.header,
        )
        mensagem.save()
        try:
            Notification.notify(
                msg_or_mid=mensagem,
                target=servidor,
                sender=employee_from_user(self.request.user),
                types=self.types,
            )
        except Exception as e:
            self.log.exception(e)
            obj["msg"] = str(e)
            obj["result"] = False
        return obj
