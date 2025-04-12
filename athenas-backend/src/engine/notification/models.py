# -.- coding: utf-8 -.-
import os
import string
import sys
import re

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields as generic
from django.core import mail
import datetime
from contrib.decorator import to_search
from urllib.parse import urlencode
from unicodedata import normalize
import urllib.request
from contrib.utils import getLogger


lof = getLogger(__name__)

RESPOSTAS_SMS = {
    "000": "000 - Mensagem enviada com sucesso!",
    "010": "010 - Mensagem sem conteudo.",
    "011": "011 - Mensagem invalida.",
    "012": "012 - Destinatario vazio.",
    "013": "013 - Destinatario invalido.",
    "014": "014 - Destinatario vazio",
    "080": "080 - ID ja usado.",
    "900": "900 - Erro de autenticacao na conta.",
    "990": "990 - Creditos insuficientes.",
    "999": "999 - Erro desconhecido.",
}


log = getLogger("Notification:Model")

TYPE_MSG_CHOICES = {"INFO": "Information", "WARNING": "Caution", "ERROR": "Error"}

TYPE_NOTIFY_CHOICES = {
    "SYS": "System",
    "EMAIL": "Email",
    "SMS": "SMS",
    "ONTOP": "On top",
}

STATUS_NOTIFY_CHOICES = {
    1: "not send",
    2: "send",
    4: "send error",
    8: "received",
    16: "abandoned",
}


class MessageManager(models.Manager):
    # def get_queryset(self):
    #     return super(MessageManager, self).get_queryset().exclude(mid__startswith='__')

    def get_by_natural_key(self, mid):
        return self.get(mid=mid)


@to_search(
    [
        {"name": "mid", "type": "text"},
        {"name": "header", "type": "text"},
        {"name": "message", "type": "text"},
        {"name": "type", "type": "choices"},
    ]
)
class Message(models.Model):
    """
    Classe que encapsula a mensagem.

    @mid -> atributo (OPCIONAL) único para identificar uma mensagem, que pode ser usado para capturar uma mensagem específica
    @header -> (OPCIONAL) cabeçalho da mensagem
    @message -> corpo da mensagem que pode ser formatada com parametros. sintaxe do formato: %(nome_do_parametro)tipo tipo=[s|d|i|f]
        Ex1.: message: "Você deve marcar os %(dias)d dias restantes do período - %(pa)s - até o dia %(data_fim)s."
             Este exemplo possui 3 parametros na mensagem: dias-> inteiro(d), pa-:string(s) e data_fim->string(s)
        Ex2.: message: "Você foi avaliado, na primeira etapa do estágio probatório, com nota média de %(nota)f."
             Este exemplo possui 1 parametro na mensagem: nota-> float(f)
    @type -> tipo de mensagem (INFO, WARNING, ERROR) padrão: INFO
    @default_params -> dicionario(DICT) com TODOS os parametros usado no corpo da mensagem, que será o valor padrão
        para o caso de não ser indicado na chamada do método @@formated(parametros={})
    """

    class Meta:
        db_table = "eng_message"

    objects = MessageManager()
    mid = models.CharField(
        max_length=30,
        blank=True,
        null=False,
        verbose_name="MID",
        unique=True,
        help_text="",
    )
    header = models.CharField(
        max_length=120, blank=True, verbose_name="Header", help_text="", default=""
    )
    message = models.TextField(verbose_name="Message", help_text="", default="")
    type = models.CharField(
        max_length=10,
        choices=list(TYPE_MSG_CHOICES.items()),
        verbose_name="Type of Message",
        default="INFO",
        help_text="",
    )
    default_params = models.CharField(
        max_length=400,
        blank=True,
        default="{}",
        verbose_name="Default Params",
        help_text="",
    )

    def natural_key(self):
        return (self.mid,)

    def save(self, force_insert=False, force_update=False):
        from contrib.utils import getLogger

        log = getLogger("Message:Model")
        """
        Essa sobrescrita verifica se o @default_params é do tipo DICT, pois caso seja faz uma mesclagem dos valores
        passados para ele com dicionario retornado pala propriedade params, fazendo com que o @default_params tenha todos os
        parametros necessários na mensagem
        """
        try:
            self.default_params = self.params
            self.mid = self.mid or "__MSG" + datetime.datetime.now().strftime("%s%f")
            super(Message, self).save(force_insert, force_update)
        except Exception as e:
            log.exception(e)
            raise

    def __str__(self):
        return "[%s] %s: %s" % (self.type, self.header, self.message)

    def _get_msg(self):
        return "%s" % self

    msg = property(_get_msg)

    def _get_params(self):
        """
        Retorna um dicionário com o nome dos parametros encotrados na mensagem,
        cada um com um valor PADRÃO para o tipo indicado na mensagem.
        OBS.: Este método é acessado pela propriedade @params (obj.params)
        RETORNO: dicionário(DICT) com os parametros constantes na mensagem
        """
        params = {}
        default_type = {"s": "", "d": 0, "i": 0, "f": 0.0}
        for param in re.findall(r"\%\(\w*\)[sdif]", self.message):
            params[param[2:-2]] = default_type[param[-1:]]
        return params

    params = property(_get_params)

    def formated(self, params={}):
        """
        Este método formata a mensagem com os paramentros passados em @params e caso haja algum
        parametro na mensagem que não esteja em params será usado o parametro padrão em definido em @defaul_params
        RETORNO: string do corpo da mensagem formatada com os paramentros passados, caso haja.
        """
        try:
            _params = {}
            if self.default_params.__class__.__name__ in [
                "str",
            ]:
                _params = eval(self.default_params)
        except Exception as e:
            log.exception("ERROR MESSAGE: %s" % e)
            return self.message
        else:
            for param in _params:
                if param in params:
                    _params[param] = params[param]
            try:
                rst = self.message % (_params)
            except ValueError as e:
                log.exception(e)
                rst = "Ocorreu um erro traduzindo a mensagem."
            except Exception as e:
                log.exception(e)
                rst = "Ocorreu um erro traduzindo a mensagem."

            return rst


class Notification(models.Model):
    """
    Classe de notificação.

    Essa classe notifica um target(GENÉRICO) com um objeto Message.
    @msg -> objeto do tipo Message
    @sender -> um objeto qualquer(OPCIONAL) que tem a responsabilidade pela notificação
    @target -> o objeto que está sendo notificado. Ex.: Servidor, PessoaFisica, Pessoa
        OBS.: para acessar as notificações diretamente do objeto notificado a classe do objeto notificado
              pode declarar um GenericRelated (não modifica a estrutura, é apenas lógico)
              Ex.: Para acessar as notificações a partir do servidor que as recebeu:
                   no model: class Servidor
                                ...
                                notificacoes = generic.GenericRelation(Notification, content_type_field='target_ct', object_id_field='target_id')
                    onde @notificacoes é o nome dado ao query set das notificacoes enviadas para o servidor
    @type -> tipo de notificação (SYS: sistema, *SMS: mensagem, *EMAIL: email, outros)
    @status -> status
    @params -> parametros a serem usados para formatar a mensagem, DEVE SER um dicionario ({'parama':1, 'paramb': 'teste'}).
    """

    class Meta:
        db_table = "eng_notification"
        ordering = ("-created_at",)

    msg = models.ForeignKey(
        Message,
        verbose_name="Message",
        help_text="",
        related_name="notifications",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    sender_ct = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        related_name="notifications_send",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    sender_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    sender = generic.GenericForeignKey("sender_ct", "sender_id")
    target_ct = models.ForeignKey(
        ContentType, related_name="notifications_receive", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    target_id = models.PositiveIntegerField(db_index=True)
    target = generic.GenericForeignKey("target_ct", "target_id")
    type = models.CharField(
        max_length=10,
        choices=list(TYPE_NOTIFY_CHOICES.items()),
        verbose_name="Type of Notification",
        default="SYS",
    )
    status = models.PositiveSmallIntegerField(
        choices=list(STATUS_NOTIFY_CHOICES.items()),
        verbose_name="Status of Notification",
        default=2,
    )
    params = models.TextField(verbose_name="Params")
    created_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "[%s] %s -> %s" % (self.type, self.msg, self.target)

    def formatMsg(self):
        """
        Retorna a mensagem formatada para os parâmetros passado na criação da notificação. Caso falte algum parametro
        este receberá o valor default para o parametro que fica armazenado com a mensagem no atributo @default_params.
        Ex.:
            self.msg.message: 'A mensagem número %(id)s será enviada em %(data)s',
            self.params: {id: 3, data: '23-02-2010'}
            self.formatMsg= 'A mensagem número 3 será enviada em 23-02-2010'
        """
        return "%s" % self.msg.formated(eval(self.params))

    @classmethod
    def notify(cls, msg_or_mid, target, sender=None, types=["SYS"], **kargs):
        """
        Envia uma notificação de cada tipo de notificação(SYS, EMAIL, SMS) solicitada para um servidor específico
                Params:
                @msg_or_mid -> objeto Message com a mensagem a ser enviada ou uma string com um @mid de mensagem existente
                @target -> objeto Generico a ser notificado. Ex.: Servidor, PessoaFisica, etc...
                @sender -> objeto que esta disparando a notificação (opcional)
                        Ex.: ao se criar/liberar a folha de pagamento de julho de 2010 os servidores seriam notificados,
                        neste caso, o sender é o objeto da folha de pagamento em questão e o target seria um servidor a ser
                        notificado
                @types -> tipo de notificação
                        SYS: sistema - OK
                        SMS: mensagem de texto via celular - NÃO IMPLEMENTADO
                        EMAIL: email - NÃO IMPLEMENTADO
                @kargs -> parametros que vai ser usado para formatar a mensagem, deve ser passado como tipo simples
                            e deve ter o mesmo nome do parametro da mensagem
                        Ex.: msg: "Faltam %(dias)d para o inicío de duas férias referente ao período %(pas)s"
                             kargs: dias=10, pas="2010/2011"
        """
        params = result = {}
        try:
            if isinstance(msg_or_mid, Message):
                msg = msg_or_mid
            else:
                msg = Message.objects.get(mid=msg_or_mid)
        except Message.DoesNotExist:
            log.debug("A template %s não existe na base de dados!" % msg_or_mid)
        except Exception:
            log.debug("Mensagem nao enviada: %s" % msg_or_mid)
        else:
            for k in kargs:
                params[k] = "%s" % kargs[k]
            for type in types:
                n = cls()
                n.msg = msg
                n.target = target
                if sender:
                    n.sender = sender
                n.type = type
                n.status = 2
                n.params = str(params) if params else "{}"
                if type == "EMAIL":
                    result[type] = n.sendEmail()
                elif type == "SMS":
                    result[type] = n.sendSMS()
                else:
                    result[type] = n.sendSYS()
        return result

    @classmethod
    def notify_all(cls, msg, targets, sender=None, types=["SYS"], **kargs):
        """
        Envia uma notificação de cada tipo de notificação(SYS, EMAIL, SMS) solicitada para um servidor específico
                Params:
                @msg_or_mid -> objeto Message com a mensagem a ser enviada ou uma string com um @mid de mensagem existente
                @target -> objeto Generico a ser notificado. Ex.: Servidor, PessoaFisica, etc...
                @sender -> objeto que esta disparando a notificação (opcional)
                        Ex.: ao se criar/liberar a folha de pagamento de julho de 2010 os servidores seriam notificados,
                        neste caso, o sender é o objeto da folha de pagamento em questão e o target seria um servidor a ser
                        notificado
                @types -> tipo de notificação
                        SYS: sistema - OK
                        SMS: mensagem de texto via celular - NÃO IMPLEMENTADO
                        EMAIL: email - NÃO IMPLEMENTADO
                @kargs -> parametros que vai ser usado para formatar a mensagem, deve ser passado como tipo simples
                            e deve ter o mesmo nome do parametro da mensagem
                        Ex.: msg: "Faltam %(dias)d para o inicío de duas férias referente ao período %(pas)s"
                             kargs: dias=10, pas="2010/2011"
        """
        result = []
        targets = targets if isinstance(targets, (tuple, list)) else [targets]
        for target in targets:
            res = {}
            res["target"] = "%s" % target
            res["result"] = cls.notify(msg, target, sender, types, **kargs)
            result.append(res)
        return result

    def sendSYS(self):
        self.save()

    def sendEmail(self):
        try:
            msg = mail.EmailMessage(
                "[%(type)s] %(title)s"
                % {"type": self.msg.get_type_display(), "title": self.msg.header},
                self.formatMsg(),
                "athenas@mpto.mp.br",
                [self.target.user.email],
            )
            msg.content_subtype = "html"
            msg.send()
        except Exception as e:
            log.exception(e)

    def sendSMS(self):
        self.save()
        nsms = NotifSMS()
        nsms.send(self, self.target.numero_sms)


class NotifSMS(models.Model):

    class Meta:
        db_table = "eng_notification_sms"

    notification = models.ForeignKey(
        Notification, related_name="sms_notifications", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    sms_number = models.CharField(
        max_length=12, blank=True, verbose_name="SMS Number", help_text=""
    )
    sms_status = models.CharField(
        max_length=3, blank=True, verbose_name="SMS Status", help_text=""
    )

    def send(self, notif, number):
        self.notification = notif
        if not notif.pk:
            notif.save()
        # Aqui voce deve preencher os dados da mensagem
        # Lembre que o celular deve estar internacionalizado (ex: 555184220483)
        msg = ""

        self.sms_number = number

        # Aqui voce deve preencher os dados de autenticacao de sua conta
        account = "mptocantins"
        code = "Xpv2mIQgFb"
        log.debug(self.notification.formatMsg())
        # Prepara a mensagem com URL Encode
        msgUrl = urlencode(
            {
                "msg": normalize("NFKD", self.notification.formatMsg()).encode(
                    "ascii", "ignore"
                )
            }
        )

        # Tenta abrir a URL indicada
        log.debug("Notificando via SMS...")
        try:
            url = (
                "http://system.human.com.br/GatewayIntegration/msgSms.do?dispatch=send&account=%s&code=%s&id=%d&to=55%s&%s"
                % (account, code, self.notification.id, self.sms_number, msgUrl)
            )
            log.debug(url)
            conexao = urllib.request.urlopen(url)
            log.debug("Notificando via SMS...(conectado)")
            conteudo = conexao.read()
            log.debug("Notificando via SMS...(recebendo resposta)")
            log.debug(conteudo)
        except Exception as e:
            log.debug(e)
        else:
            # Retira o trecho que sera verificado
            codigo = conteudo[0:3]
            # Retorna resposta para o usuario
            self.sms_status = codigo
            self.save()
            log.debug("Notificando via SMS...(salvando notif)")
        finally:
            conexao.close()
            log.debug("Notificando via SMS...(fechando conexao)")
        log.debug("Notificando via %s" % self.__class__.__name__)


class NotifEmail(models.Model):
    class Meta:
        db_table = "eng_notification_email"

    sms_number = models.CharField(
        max_length=150, blank=True, verbose_name="Email", help_text=""
    )

    def send(self):
        log.debug("Notificando via %s" % self.__class__.__name__)
