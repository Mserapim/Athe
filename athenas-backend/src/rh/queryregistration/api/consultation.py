# -*- coding: utf-8 -*-
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from rh.queryregistration.api.report import QueryReport
from rh.queryregistration.models import Consultation
from contrib.decorator import login_required
from contrib.utils import get_json_engine
from rh.queryregistration.models import TagField
import re

log = getLogger(__name__)
json = get_json_engine()


class QRConsultation(RestfulDRY):

    _model = Consultation

    full_text_index = (
        "pk__icontains",
        "title__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.queryregistration.ConsultationManage")')

    def get_icons(self, instance):
        description = instance.description if instance.description else " - "
        return (
            {"iconCls": "icon-diarias icon-information", "title": f"{description}"},
        )

    def extract_params_sql(self, sql):
        """Esse método criar os campos do formulário de acordo com as tags da consulta sql passada"""
        reg_str = "\$([^$]+)\$"
        values = re.findall(reg_str, sql)
        set_dict = dict.fromkeys(values).keys()
        params = list(set_dict)
        tags = []
        for param in params:
            temp = param.split(":")
            if len(temp) > 1:
                if temp[1] != "":
                    temp[1] = temp[1].replace("?", "")
                    tag_key = temp[0].replace(" ", "_")
                    tag = TagField.objects.filter(key_tag=tag_key).first()
                    if tag:
                        self.add_list_description(tags, temp, tag)
                else:
                    tag_key = temp[0].replace(" ", "_")
                    tag = TagField.objects.filter(key_tag=tag_key).first()
                    if tag:
                        self.add_list_empty_description(tags, temp, tag, tag_key)

            else:
                tag_key = temp[0].replace(" ", "_").replace("?", "")
                tag = TagField.objects.filter(key_tag=tag_key).first()
                if tag:
                    self.add_list(tags, temp, tag, tag_key)

        return tags

    def add_list_description(self, tags, temp, tag):
        return tags.append(
            {
                "label": temp[1].title(),
                "tag": temp[1].replace(" ", "_").lower(),
                "type": tag.type_tag,
                "rest": tag.type_rest,
                "choice": tag.choice_id,
                "length": tag.length,
                "valuefield": tag.value,
                "controller": tag.controller,
                "colums": tag.colums,
                "format": self.set_format_date(tag.type_tag),
                "name": tag.name.title(),
            }
        )

    def add_list_empty_description(self, tags, temp, tag, tag_key):
        return tags.append(
            {
                "label": temp[0].title(),
                "tag": tag_key.lower(),
                "type": tag.type_tag,
                "rest": tag.type_rest,
                "choice": tag.choice_id,
                "length": tag.length,
                "valuefield": tag.value,
                "controller": tag.controller,
                "colums": tag.colums,
                "format": self.set_format_date(tag.type_tag),
                "name": tag.name.title(),
            }
        )

    def add_list(self, tags, temp, tag, tag_key):
        return tags.append(
            {
                "label": temp[0].title().replace("?", ""),
                "tag": tag_key.lower(),
                "type": tag.type_tag,
                "rest": tag.type_rest,
                "choice": tag.choice_id,
                "length": tag.length,
                "valuefield": tag.value,
                "controller": tag.controller,
                "colums": tag.colums,
                "format": self.set_format_date(tag.type_tag),
                "name": tag.name.title(),
            }
        )

    def set_format_date(self, type):
        if type in ["datefield", "tk-datetimefield"]:
            return "Y-m-d"
        else:
            """"""

    def _extract_params_tag(self, sql):
        """Esse metódo retorna as tags da consulta sql no formato de Dict"""
        reg_str = "\$([^$]+)\$"
        tags_sql = re.findall(reg_str, sql)
        tags = {}
        for tag in tags_sql:
            temp = tag.split(":")
            if len(temp) > 1:
                tags.update({tag: temp[1].lower().replace(" ", "_").replace("?", "")})
            else:
                tags.update({tag: temp[0].lower().replace(" ", "_").replace("?", "")})

        return tags

    @login_required("JSON")
    def get_tags(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            pk = self.request.POST.get("pk")
            consultation = Consultation.objects.get(pk=pk)
            sql = consultation.sql
            tags = self.extract_params_sql(sql)

            tags_sent_by_front = self._extract_params_tag(sql)

            multichoices = [
                tag["tag"] if tag["type"] == "checkboxchoicefield" else None
                for tag in tags
            ]

            for tag in tags:
                index = tags.index(tag)
                result_name = list(tags_sent_by_front.keys())[index]
                tag_field = TagField.objects.filter(
                    name=tag.get("name").upper()
                ).first()
                tag_value = tag_field.get_cache_value(
                    employee_from_user(get_current_user()), consultation, result_name
                )
                tag["tag_value"] = tag_value if tag_value else None

            obj.update(tags=tags, multichoices=multichoices)

        except Exception as e:
            self.log.exception(e)
            obj["message"] = e
            obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update(
            {
                "icons": self.get_icons(instance),
            }
        )

        del _dict_["sql"]
        del _dict_["log_sql"]

        return _dict_
