# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from rh.pvf.models import ShiftManager
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user, getLogger
from rh.models import Lotacao
from rh.pvf.const import (
    TYPE_SHIFT_DTI,
    TYPE_SHIFT_WEEKEND,
    TYPE_SHIFT_ELECTORAL,
    TYPE_SHIFT_RECESS,
)
from django.db import transaction
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from rh.pvf.utils.custom_exception import LinkException
import json


log = getLogger(__name__)


class PVFShiftmanager(RestfulDRY):

    _model = ShiftManager

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__iexact",
        "workplace__nome__icontains",
    )

    def get_employee(self):
        return employee_from_user(get_current_user())

    def check_duty_link(self, instance):
        return instance.server_duty.exists()

    def linkException(self, instance):
        if self.check_duty_link(instance):
            raise LinkException(
                f"""Não é possível remover/editar a solicitação, 
                pois a mesma está vinculada a solicitação nº {instance.server_duty.get().pk}.
            """
            )
        else:
            return True

    def get_query(self):
        query = super(PVFShiftmanager, self).get_query()
        return query.filter(owner=self.get_employee())

    def model_to_dict(self, instance):
        _dict_ = super(PVFShiftmanager, self).model_to_dict(instance)
        _dict_.update({"icons": instance.icons})
        return _dict_

    def get_permissions(self):
        permissons = []
        workplaces = Lotacao.objects.filter(responsavel=self.get_employee())
        for workplace in workplaces:
            if workplace.gestor_plantao_dti:
                permissons.append([TYPE_SHIFT_DTI, "DTI"])
            if workplace.gestor_plantao_final_semana:
                permissons.append([TYPE_SHIFT_WEEKEND, "Final de Semana"])
            if workplace.gestor_plantao_recesso:
                permissons.append([TYPE_SHIFT_RECESS, "Recesso"])
            if workplace.gestor_plantao_eleitoral:
                permissons.append([TYPE_SHIFT_ELECTORAL, "Eleitoral"])
        permissons_unique = [list(per) for per in set(tuple(per) for per in permissons)]
        return permissons_unique

    def do_delete_single(self, pk):
        """Remove uma instância.

        :param pk: Chave primária de uma instância.
        :type pk: Integer
        """
        rst = {"success": False}

        try:
            inst = self.get_instance_model(pk)
            related_pk = (
                inst.server_duty.first().pk if self.check_duty_link(inst) else None
            )
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado para remoção.")
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            try:
                inst.delete()
            except ProtectedError:
                rst.update(
                    message=f"Não é possível remover/editar a solicitação, pois a mesma está vinculada a solicitação nº {related_pk}."
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update({"message": "Removido com sucesso!", "success": True})

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
                self.linkException(inst)
                if self.use_full_clean:
                    inst.full_clean()
                inst.save()
                self.fill_instance_m2m(inst, params)
            except LinkException as e:
                rst.update(message=str(e))
                log.exception(e)
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

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.pvf.shiftmanager.Manage",{permissions:"%s",})'
            % (self.get_permissions())
        )


class PVFShiftmanagerResume(RestfulDRY):

    _model = ShiftManager

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__iexact",
        "workplace__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.shiftmanager.ManageResume")')
