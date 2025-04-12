# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from django.db import transaction
from django.db.models import Q, Sum
from planejamento.contrato.models import (
    Minute,
    MinuteItem,
    MinuteItemComplementaryDescription,
    MinuteItemAction,
)
from standard.models import Choice
import json
import csv
from collections import namedtuple
import locale
import codecs

log = getLogger(__name__)


class PHMMinuteItem(RestfulDRY):

    _model = MinuteItem

    force_upper = False

    force_orm_single = True

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("line__icontains", "group__icontains", "description__icontains")

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    force_persist_boolean_fields = [
        "generate_agreement",
    ]

    def get_query(self):
        query = super(PHMMinuteItem, self).get_query()
        query = query.extra(select={"_group": 'CAST("group" AS INTEGER)'}).order_by(
            "_group", "id"
        )
        if "keyword" in self.request.REQUEST:
            keyword = self.request.REQUEST.get("keyword")
            query = query.filter(
                Q(description__icontains=keyword) | Q(group__icontains=keyword)
            )

        return query

    def total_value_display(self, *args):
        obj = {}
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        item = self._model.objects.get(pk=self.request.POST.get("pk"))
        obj["total_value_display"] = str(
            locale.currency(item.total_value, grouping=True, symbol=None)
        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_item_values(self, *args):
        obj = {"success": False, "item_balance": "", "item_description": ""}
        try:
            item = self._model.objects.get(pk=self.request.POST.get("pk"))
            item.update_item_balance()
            if len(item.description_without_tags) > 400:
                _description = item.description_without_tags[:400] + " ..."
            else:
                _description = item.description_without_tags
            obj.update(
                success=True,
                item_description=_description,
                item_balance=str(round(item.item_balance, 2)),
            )

        except MinuteItem.DoesNotExist:
            obj.update(success=False, message="Não foi possível localizar o item")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def set_complementary_description(self, minute_item, row):
        """
        Inseri todas as características extras de um item
        """
        i = 1
        while hasattr(row, "caracteristica" + str(i)) and hasattr(
            row, "descricao" + str(i)
        ):
            characteristic = row.__getattribute__("caracteristica" + str(i))
            description = row.__getattribute__("descricao" + str(i))
            if len(characteristic) > 0 or len(description) > 0:
                try:
                    MinuteItemComplementaryDescription.objects.create(
                        minuteitem=minute_item,
                        characteristic=characteristic,
                        description=description,
                    )
                except Exception as e:
                    raise e
            i += 1

    def import_items(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        csv_file = self.request.FILES.get("file")
        minute_id = self.request.POST.get("minute")

        if csv_file and minute_id:
            if not csv_file.name.endswith(".csv"):
                obj.update(
                    success=False,
                    message="O arquivo informado não possui extensão .csv",
                )
            else:
                try:
                    with transaction.atomic():
                        minute = Minute.objects.get(pk=minute_id)
                        with open(csv_file.temporary_file_path()):
                            f_csv = csv.reader(
                                codecs.iterdecode(csv_file, "utf-8"), delimiter=";"
                            )
                            headings = next(f_csv)
                            Row = namedtuple("Row", headings)
                            for r in f_csv:
                                row = Row(*r)
                                if (
                                    row.ata == ""
                                    or row.descricao_grupo == ""
                                    or row.grupo_item == ""
                                    or row.descricao == ""
                                    or row.unidade_medida == ""
                                    or row.quantidade == ""
                                    or row.valor_unitario == ""
                                    or row.gera_contrato == ""
                                ):
                                    obj.update(
                                        success=False,
                                        message="Verifique se os campos obrigatórios estão preenchidos.",
                                    )
                                    transaction.set_rollback(True)

                                if not row.ata == minute.number:
                                    obj.update(
                                        success=False,
                                        message="O arquivo possui item de outra ata.",
                                    )
                                    transaction.set_rollback(True)
                                else:
                                    if row.grupo_item.isdigit():
                                        if row.linha:
                                            if row.linha.isdigit():
                                                _line = row.linha
                                            else:
                                                obj.update(
                                                    success=False,
                                                    message="Verifique se o campo linha é numérico.",
                                                )
                                                transaction.set_rollback(True)

                                            if not MinuteItem.objects.filter(
                                                minute=minute_id,
                                                group=row.grupo_item,
                                                quantity=None,
                                                unitary_value=None,
                                            ).exists():

                                                minuteitem_group = (
                                                    MinuteItem.objects.create(
                                                        minute=minute,
                                                        line=row.grupo_item,
                                                        description=row.descricao_grupo,
                                                        status=5,
                                                    )
                                                )
                                                _parent = minuteitem_group
                                            else:
                                                item = MinuteItem.objects.get(
                                                    minute=minute_id,
                                                    group=row.grupo_item,
                                                    quantity=None,
                                                    unitary_value=None,
                                                )
                                                if (
                                                    not item.quantity
                                                    and not item.unitary_value
                                                ):
                                                    _parent = item
                                                else:
                                                    _parent = None
                                        else:
                                            _line = row.grupo_item
                                            _parent = None
                                    else:
                                        obj.update(
                                            success=False,
                                            message="Verifique se o campo group_item é numérico.",
                                        )
                                        transaction.set_rollback(True)

                                    if row.unidade_medida:
                                        _unit_measure = row.unidade_medida.upper()
                                        try:
                                            _unit_measure = Choice.objects.get(
                                                name="MINUTE_ITEM_UNIT_MEASURE",
                                                label=_unit_measure,
                                            ).value
                                        except Choice.DoesNotExist:
                                            if row.linha:
                                                message = "O item {}.{} não possui uma unidade de medida válida.".format(
                                                    row.grupo_item, row.linha
                                                )
                                            else:
                                                message = "O item {} não possui uma unidade de medida válida.".format(
                                                    row.grupo_item
                                                )

                                            obj.update(success=False, message=message)
                                            transaction.set_rollback(True)

                                    if row.quantidade:
                                        _quantity = float(
                                            row.quantidade.replace(",", ".")
                                        )

                                    if row.valor_unitario:
                                        _unitary_value = float(
                                            row.valor_unitario.replace(",", ".")
                                        )

                                    if _quantity and _unitary_value:
                                        _total_value = round(_quantity, 2) * round(
                                            _unitary_value, 2
                                        )

                                    if (
                                        row.gera_contrato == "S"
                                        or row.gera_contrato == "s"
                                    ):
                                        _generate_agreement = True
                                    else:
                                        _generate_agreement = False

                                    minute_item = MinuteItem.objects.create(
                                        minute_id=minute.id,
                                        description=" ".join(row.descricao.split()),
                                        brand=row.marca_modelo,
                                        unit_measure=_unit_measure,
                                        quantity=_quantity,
                                        unitary_value=_unitary_value,
                                        total_value=_total_value,
                                        parent=_parent,
                                        line=_line,
                                        item_balance=row.quantidade,
                                        generate_agreement=_generate_agreement,
                                        status=5,
                                    )

                                    self.set_complementary_description(minute_item, row)

                                    obj.update(
                                        success=True,
                                        message="Arquivo importado com sucesso!",
                                    )

                except Exception as e:
                    log.exception(e)
                    obj.update(
                        success=False,
                        message="O aquivo de importação possui um erro. A importação não foi realizada.",
                    )

        else:
            obj.update(
                success=False, message="Informe um arquivo para a importação dos itens."
            )

        self.response["content-type"] = "text/html"
        self.response.write(json.dumps(obj))

    def validate_items(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        minute = self.request.POST.get("minute")
        try:
            minuteitems = MinuteItem.objects.filter(minute=minute, status=5)
            minuteitems.update(status=1)
            obj = {
                "success": True,
                "message": "Validação de itens realizada com sucesso",
            }
        except Exception as e:
            log.debug(e)
            obj = {
                "success": False,
                "message": "Ocorreram erros ao realizar a validação.",
            }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def invalidate_items(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        minute_id = self.request.POST.get("minute")
        try:
            minuteitems_invalid = MinuteItem.objects.filter(minute=minute_id, status=5)
            minuteitems_invalid.filter(parent__isnull=False).delete()
            minuteitems_invalid.delete()

            minute = Minute.objects.get(id=minute_id)
            minuteitems = minute.minuteitems.all()

            if minuteitems:
                total_amount = 0
                for i in minuteitems:
                    total_item = 0
                    if i.quantity and i.unitary_value:
                        if i.status in [2, 3]:
                            _quantity = i.minutesolicitationitems.aggregate(
                                Sum("quantity")
                            ).get("quantity__sum")
                            if _quantity:
                                total_item = round(_quantity, 2) * round(
                                    i.unitary_value, 2
                                )
                        else:
                            total_item = round(i.quantity, 2) * round(
                                i.unitary_value, 2
                            )
                    total_amount = round(total_amount, 2) + round(total_item, 2)
            else:
                total_amount = 0

            minute.total_amount = total_amount
            minute.save()

            obj = {
                "success": True,
                "message": "Importação de itens desfeita com sucesso",
            }
        except Exception as e:
            log.debug(e)
            obj = {
                "success": False,
                "message": "Ocorreram erros ao desfazer importação.",
            }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_total_value_imported(self, *args):
        obj = {"success": False, "textValue": "Total: Não disponível"}

        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        minute_id = self.request.POST.get("minute")
        minuteitems = MinuteItem.objects.filter(minute=minute_id, status=5)
        if minuteitems:
            total_value = 0
            for i in minuteitems:
                if i.quantity and i.unitary_value:
                    total_value += round(i.quantity, 2) * round(i.unitary_value, 2)

            obj.update(
                success=True,
                textValue="Total: R$ {}".format(
                    str(locale.currency(total_value, grouping=True, symbol=None))
                ),
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteItem, self).model_to_dict(instance)

        _dict_.update({"description_without_tags": instance.description_without_tags})

        return _dict_


class PHMMinuteItemComplementaryDescription(RestfulDRY):

    _model = MinuteItemComplementaryDescription

    force_upper = False


class PHMMinuteItemAction(RestfulDRY):

    _model = MinuteItemAction

    full_text_index = (
        "user__username__icontains",
        "date__icontains",
        "observation__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super(PHMMinuteItemAction, self).model_to_dict(instance)

        _dict_.update({"actions_list": instance.actions_list()})

        return _dict_

    def get_actions_list(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            obj.update(actions_list=MinuteItemAction.actions_list())
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
