from django.core.exceptions import ValidationError

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user, DateUtils
from contrib.middleware import get_current_user
from contrib.decorator import login_required

from rh.pvf.models import (
    PortalRequestProgression,
    PortalRequestProgressionH,
    PRProgressionHDocument,
)
from rh.gfp.models import MovimentacaoProgressao, HorizontalProgressionConfig
from rh.models import Publicacao as Publication

from rh.pvf.const import (
    STS_REJECTED,
    STS_EFFECTIVE,
    STS_CANCELED_DGP,
    STS_CANCELED_APPLICANT,
    REQUEST_STEP_STAND,
    STS_STAND_BY,
)

log = getLogger(__name__)


class PVFRequestProgression(RestfulDRY):
    _model = PortalRequestProgression

    full_text_index = ("title__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.progression.Manage")')


class PVFRequestProgressionH(RestfulDRY):
    _model = PortalRequestProgressionH

    full_text_index = ("title__icontains",)

    def get_request_progress_h(self):
        return (
            PortalRequestProgressionH.objects.filter(
                employee=employee_from_user(get_current_user()),
            )
            .exclude(
                status__in=[
                    STS_REJECTED,
                    STS_EFFECTIVE,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )
            .exists()
        )

    def get_request_progress_v(self):
        return (
            PortalRequestProgression.objects.filter(
                employee=employee_from_user(get_current_user()),
            )
            .exclude(
                status__in=[
                    STS_REJECTED,
                    STS_EFFECTIVE,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )
            .exists()
        )

    @login_required("JSON")
    def save(self, args=[]):
        message = "Não foi processado nada ainda!"
        rst = {"success": False, "message": message}
        if self.get_request_progress_h():
            raise Exception(
                "Já existe uma solicitação de Progressão Horizontal em andamento."
            )
        if self.get_request_progress_v():
            raise Exception(
                "Já existe uma solicitação de Progressão Vertical em andamento."
            )

        try:
            progression = MovimentacaoProgressao.objects.get(
                pk=int(self.request.POST.get("progression"))
            )
            config = HorizontalProgressionConfig.objects.get(
                pk=int(self.request.POST.get("config"))
            )

            instance = self.Model.create(progression, config)
            message = "Registro Criado com Sucesso"

            rst.update(
                {
                    "success": True,
                    "message": message,
                    "pk": instance.pk,
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)

                rst = self.save()
                if rst["success"] == False:
                    raise Exception(rst["message"])
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
                    rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Dados persistido com sucesso.",
                        "instance": self.model_to_dict(inst),
                    }
                )

        return rst

    def model_to_dict(self, instance):
        """Cria um dicionário com atributos de uma instância.

        :param instance: Instância de Model.

        :returns: Dicionário com indices pk e unicode da instância.

        Este método deve ser sobrescrito para adicionar os demais atributos de uma determinada instância.
        Os valores dos atributos devem ser convertidos neste método para um formato serializável se necessário.
        """
        # Se a instance produzida no getquery for um dicionario
        # Pode acontecer quando o getquery foi sobrescrito para um aggregate

        progression = getattr(instance, "progression")
        prph = PortalRequestProgressionH.objects.filter(
            progression=progression,
            step_current__in=[REQUEST_STEP_STAND],
            status__in=[STS_STAND_BY],
        )
        if prph:
            instance = prph.first()

        if isinstance(instance, dict):
            return instance

        params = {
            "pk": instance.pk,
            "unicode": str(instance),
            "icons": self.get_icons(instance),
        }
        meta = instance._meta

        for f in meta.fields:
            if f.name in self._fields:
                _type = f.get_internal_type()
                if _type == "DecimalField":
                    params[f.name] = (
                        float(getattr(instance, f.name))
                        if getattr(instance, f.name) is not None
                        else ""
                    )
                elif _type == "DateTimeField":
                    params[f.name] = (
                        DateUtils.datetime_to_str(getattr(instance, f.name))
                        if getattr(instance, f.name)
                        else ""
                    )
                elif _type == "DateField":
                    params[f.name] = (
                        DateUtils.date_to_str(getattr(instance, f.name))
                        if getattr(instance, f.name)
                        else ""
                    )
                elif _type in ["ForeignKey", "OneToOneField"]:
                    params[f.name] = getattr(instance, f.attname) or ""
                elif _type in (
                    "BigIntegerField",
                    "IntegerField",
                    "PositiveIntegerField",
                    "PositiveSmallIntegerField",
                    "SmallIntegerField",
                ):
                    params[f.name] = (
                        int(getattr(instance, f.attname))
                        if getattr(instance, f.attname) is not None
                        else None
                    )
                elif _type == "UUIDField":
                    params[f.name] = str(getattr(instance, f.name)) or ""
                else:
                    params[f.name] = getattr(instance, f.name)
                if f.choices:
                    params["%s_display" % f.name] = (
                        getattr(instance, "get_%s_display" % f.name)() or ""
                    )
                if f.remote_field:
                    if not instance:
                        params["%s_unicode" % f.name] = str(
                            getattr(instance, f.name) or ""
                        )

        return params

    @login_required("JSON")
    def send(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            pk = self.request.POST.get("pk")
            instance = PortalRequestProgressionH.objects.get(pk=pk)

            if "publication" in self.request.POST:
                publication = Publication.objects.get(
                    pk=self.request.POST.get("publication")
                )
                instance.register_publication(publication)
                rst.update(
                    {
                        "success": True,
                        "message": "Publicação registrada com sucesso",
                    }
                )
            else:
                instance.resend_request()
                rst.update(
                    {
                        "success": True,
                        "message": "Registro enviado com sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.progression_h.Manage")')


class PVFProgressionHDocument(RestfulDRY):

    _model = PRProgressionHDocument

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.progression_h.document.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            custom_approver_current=instance.get_doc_origin_display(
                instance.doc_origin
            ),
        )

        return rst
