# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from contrib.newrest import Restful
from contrib.utils import getLogger

from raf.models import AutoReference, SearchByNumber


log = getLogger(__name__)


class RAFSearchProcessNumber(Restful):

    _model = SearchByNumber

    page_size = 10

    full_text_index = ("process_number",)

    def tpl_repr_lawsuit(self, *args, **kwargs):
        title = ""

        if kwargs.get("removed", False):
            title = f'<b>REMOVIDO ATRAVÉS DE SOLCITAÇÃO DE AJUSTES em: {kwargs.get("modified_at")}</b><br />'
        elif kwargs.get("title", False):
            title = f'Fonte: <b>{kwargs.get("title")}</b><br />'

        return f"""
            {title}
            Processo: <b>{kwargs.get("lawsuit")}</b><br />
            Mês/Ano: <b>{kwargs.get("month")}/{kwargs.get("year")}</b><br />
            Membro: <b>{kwargs.get("member")}</b><br />
            Pomotoria: <b>{kwargs.get("location")}</b><br />
        """

    def tpl_repr_raf(self, *args, **kwargs):
        msg_analisys = ""

        if kwargs.get("analisys", False):
            msg_analisys = f'Status: <b>{kwargs.get("analisys")}</b><br />'

        return f"""
            {msg_analisys}
            Questionário: <b>{kwargs.get("quiz")}</b><br />
            Assunto: <b>{kwargs.get("item")}</b><br />
            Movimento: <b>{kwargs.get("subitem")}</b><br />
            Data: <b>{kwargs.get("date")}</b><br />
        """

    def model_to_dict(self, instance):
        _dict_ = super(RAFSearchProcessNumber, self).model_to_dict(instance)

        _dict_.update(
            {
                "autoreference_id": 0,
                "autoreference_source_add": 0,
                "autoreference_is_adjustment": False,
            }
        )

        repr_lawsuit = {
            "lawsuit": instance.process_number_formatted,
            "month": instance.month,
            "year": instance.year,
            "member": instance.membro,
        }

        repr_raf = {"date": instance.date.strftime("%d/%m/%Y %H:%M:%S")}

        ct = ContentType.objects.filter(model=instance.contenttype).values("pk")
        autoreference = (
            AutoReference.objects.filter(content_type__in=ct, object_id=instance.pk)
            .select_related(
                "activity__item__quiz__typequiz",
                "activity__item",
                "activity__subitem",
                "activity__workerlocation__location",
            )
            .first()
        )

        if autoreference:
            _dict_.update(
                {
                    "autoreference_id": autoreference.pk,
                    "autoreference_source_add": autoreference.source_add,
                    "autoreference_is_adjustment": autoreference.is_adjustment,
                }
            )

            repr_lawsuit.update(
                {
                    "location": autoreference.activity.workerlocation.location.nome,
                    "removed": autoreference.removed,
                    "modified_at": autoreference.modified_at.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                }
            )

            repr_raf.update(
                {
                    "quiz": autoreference.activity.item.quiz.typequiz.title,
                    "item": autoreference.activity.item.title,
                    "subitem": autoreference.activity.subitem.title,
                }
            )

        data_lawsuit = None
        data_raf = None

        if instance.contenttype in ["dataeproc", "dataeext"]:
            repr_raf.update(analisys=instance.get_analisys_display().upper())

        if instance.contenttype == "dataadjustment":
            repr_raf.update(analisys=instance.get_operation_display().upper())
            repr_lawsuit.update(title="Ajustes")

        data_raf = self.tpl_repr_raf(**repr_raf)
        data_lawsuit = self.tpl_repr_lawsuit(**repr_lawsuit)

        _dict_.update(
            {
                "data_processo": data_lawsuit,
                "data_raf": data_raf,
            }
        )

        return _dict_
