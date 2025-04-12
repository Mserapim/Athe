# -*- coding: utf-8 -*-
import uuid
import json

from decimal import Decimal
from django.http import QueryDict
from django.core.exceptions import FieldDoesNotExist, ValidationError

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, get_json_engine
from contrib.utils import DateUtils

from rh.pvf.models import PointJustification, PortalRequest
from standard.models import JustificationItem

from django.db.models import ProtectedError
from contrib.decorator import login_required

log = getLogger(__name__)
json_engine = get_json_engine()


class PVFPointJustification(RestfulDRY):

    _model = PointJustification

    def get_config_justification(self, *args):
        import json

        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            if args[0][0] != "undefined":
                type_by_possession = PortalRequest.objects.get(
                    pk=args[0][0]
                ).employee.type_by_possession
                items = self.get_data_type_by_possession_access(type_by_possession)
                values = JustificationItem.objects.filter(value__in=items).values_list(
                    "value", "name"
                )
            else:
                values = JustificationItem.objects.all().values_list("value", "name")

            # values = Choice.objects.filter(app_label='pvf',name='TYPE_OF_REASON',active=True).values_list('value','label')
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(values),
                collection=[
                    {"pk": int(value[0]), "description": value[1]} for value in values
                ],
            )
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_data_type_by_possession_access(self, type_by_possession):
        items = []
        types_in_justif_item = []
        for item in JustificationItem.objects.all():
            types_in_justif_item = (
                item.type_by_possession.split(",") if item.type_by_possession else None
            )
            if types_in_justif_item and type_by_possession in types_in_justif_item:
                items.append(item.value)
        return items

    def get_params(self, querydict=None, check_case=False):
        """Recebe os parâmetros do browser como uma QueryDict e converte para um dicionário.

        :param querydict: QueryDict.

        :param check_case: Define se verifica o atributo 'force_upper' para conversão em uppercase.

        Este método deve ser sobrescrito para converter os parâmetros para um formato serializável se necessário.
        """

        # params = super(RestfulDRY, self).get_params(querydict, check_case)

        _dict_ = {}
        opts = self._model._meta

        querydict = (
            querydict
            if querydict is not None
            else getattr(self.request, self.request.method, QueryDict("", False))
        )

        keys = (
            set(querydict.keys())
            .union(self.force_persist_boolean_fields)
            .union(self.force_persist_clear_m2m)
            .difference(self.exclude_fields)
        )

        # log.debug('KEYS: %s' % keys)

        for key in keys:
            value = querydict.getlist(key) if key in querydict else []
            if len(value) <= 1:
                value = querydict.get(key) if key in querydict else None

            value = self._force_case(value) if check_case and value else value

            try:
                field = opts.get_field(key)
                model = getattr(field, "model", None)
                direct = not field.auto_created or field.concrete
                m2m = getattr(field, "many_to_many", None)

                _type = field.get_internal_type() if not m2m else "ManyToManyField"
                # log.debug('1 KEY: %s VALUE: %s TYPE: %s/%s' % (key, value, _type, type(value)))
                if _type in ["ForeignKey", "OneToOneField"]:
                    if not value:
                        value = None
                    else:
                        value = field.remote_field.model.objects.get(pk=value)
                elif _type == "DateTimeField":
                    value = DateUtils.str_to_datetime(value) if value else None
                elif _type == "DateField":
                    value = DateUtils.str_to_date(value) if value else None
                elif _type == "ManyToManyField":
                    value = querydict.getlist(key)
                elif _type in [
                    "IntegerField",
                    "BigIntegerField",
                    "PositiveIntegerField",
                    "PositiveSmallIntegerField",
                    "SmallIntegerField",
                ]:
                    value = int(value) if value not in ("", None) else None
                elif _type == "DecimalField":
                    if value == "00:00":
                        value = ""
                    value = (
                        Decimal(value.replace(":", "."))
                        if value not in ("", None)
                        else None
                    )
                elif _type == "BooleanField":
                    if value in ("", "off", "OFF", None, 0, False, "FALSE"):
                        value = False
                    elif value.lower() in ("on", "true"):
                        value = True
                elif _type == "UUIDField":
                    value = uuid.UUID(value) if value else None
                else:
                    log.debug("OTHER KEY: %s VALUE: %s" % (key, value))
                # log.debug('2 KEY: %s VALUE: %s TYPE: %s' % (key, value, type(value)))

            except FieldDoesNotExist:
                log.warn("Field %s do not exist in model %s" % (key, self._model))
            except Exception as e:
                log.exception(str(e))
                raise e

            _dict_.update({key: value})

        if self.force_persist_clear_m2m:
            # Deixando como [] os m2m que não vieram no request
            for field in opts.many_to_many:
                fname = field.name
                if fname in self.force_persist_clear_m2m and fname not in _dict_:
                    _dict_[fname] = []

        return _dict_

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

                if self.use_full_clean:
                    inst.full_clean()

                inst.save({"modulo": params["modulo"]})
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

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            log.debug(
                "COUNT UPDATE FOR %s [%s,]: %s"
                % (self.Model.__name__, pk, self.Model.objects.filter(pk=pk).count())
            )
            params = self.get_params(self.request.PUT, check_case=True)
            log.debug("PUT GETPARAMS....")
            log.debug(json.dumps(params, default=str))
            inst = self.Model.objects.get(pk=pk)
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o item que deseja atualizar. pk: %s model: %s ctr: %s"
                % (pk, self.Model.__name__, self.__class__.__name__)
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            if self.can_update_fields_values is not None:
                params = {
                    k: v
                    for k, v in list(params.items())
                    if k in self.can_update_fields_values
                }

            self.fill_instance_values(inst, params)

            try:
                if self.use_full_clean:
                    inst.full_clean()

                inst.save({"modulo": params["modulo"]})
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

    @login_required("JSON")
    def cancelar_justificativa(self, *args):
        obj = {
            "success": True,
            "message": "Nada Feito ainda ",
        }

        params = self.get_params(self.request.POST, check_case=True)

        modulo = int(params.get("modulo"))
        num_selecao = int(params.get("num_selecao"))

        if num_selecao == 1:
            selecionados = [int(params.get("selecionados"))]
        else:
            selecionados = [int(s) for s in params.get("selecionados")]

        try:
            for justificativa in PointJustification.objects.filter(pk__in=selecionados):
                justificativa.delete({"modulo": modulo})
            obj["message"] = "Justificativa Cancelada! "
        except Exception as e:
            obj["success"] = False
            obj["message"] = e.args

        return self.response.write(json_engine.encode(obj))

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)
        reason_type = JustificationItem.objects.filter(
            value=instance.reason_type
        ).first()
        _dict_.update(
            {
                "number_hours_str": instance.number_hours,
                "number_hours": instance.number_hours,
                "is_update": instance.is_update,
                "days": instance.get_days,
                "hours": int(instance.number_hours.split(":")[0]),
                "minutes": (
                    int(instance.number_hours.split(":")[1])
                    if len(instance.number_hours.split(":")) > 1
                    else 0
                ),
                "reason_type_str": reason_type.name if reason_type else "",
            }
        )
        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.pvf.sendpointsheet.PointJustificationManage")'
        )
