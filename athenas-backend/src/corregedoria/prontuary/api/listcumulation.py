# -*- coding: utf-8 -*-
from datetime import datetime

import raf.api.util
from contrib.daterange import NewDateRange
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.prontuary.models import (
    Cumulation,
    DetailListCumulation,
    ListCumulation,
    Prontuary,
)
from judicial.models import ExecutionOrgan
from rh.models import ServidorLotacao

log = getLogger(__name__)


class PRONTUARYListCumulation(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = ListCumulation

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.prontuary.functionalperformance.listcumulation.Manage")'
        )

    def get_query(self):
        query = super(PRONTUARYListCumulation, self).get_query()
        return query.order_by("-date_initial", "-date_final")

    def model_to_dict(self, instance):
        _dict_ = super(PRONTUARYListCumulation, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "cumulation_date_initial": instance.date_initial.strftime("%d/%m/%Y"),
                "cumulation_date_final": (
                    instance.date_final.strftime("%d/%m/%Y")
                    if instance.date_final
                    else None
                ),
            }
        )
        return _dict_

    def normalize_cumulations(self, prontuary=None):
        analyzed = []
        for_delete = []
        dclist = []
        for dc in DetailListCumulation.objects.filter(
            listcumulation__cumulation__prontuary=prontuary
        ):
            dclist.append(dc.employeelocation)
        for c1 in (
            ListCumulation.objects.filter(cumulation__prontuary=prontuary)
            .exclude(pk__in=analyzed)
            .order_by("pk")
        ):
            analyzed.append(c1.pk)
            dr1 = NewDateRange(c1.date_initial, c1.date_final)
            for c2 in (
                ListCumulation.objects.filter(cumulation__prontuary=prontuary)
                .exclude(pk__in=analyzed)
                .order_by("pk")
            ):
                dr2 = NewDateRange(c2.date_initial, c2.date_final)
                dr3 = dr1.intersect(dr2)
                if dr3.days > 0:
                    if c1.pk not in for_delete:
                        for_delete.append(c1.pk)
                    if c2.pk not in for_delete:
                        for_delete.append(c2.pk)
                    rst = []
                    z = dr1 - dr3
                    if z.days > 0:
                        for y in z.ranges():
                            rst.append(y)
                    z = dr2 - dr3
                    if z.days > 0:
                        for y in z.ranges():
                            rst.append(y)
                    rst.append(dr3)
                    for c in rst:
                        elist = []
                        for a in dclist:
                            dra = NewDateRange(
                                a.data_vigencia_inicio, a.data_vigencia_fim
                            )
                            if c.intersect(dra).days > 0:
                                if a not in elist:
                                    elist.append(a)
                        self.save_periods(
                            prontuary=prontuary, range_dates=c, el_list=elist
                        )
            DetailListCumulation.objects.filter(
                listcumulation__pk__in=for_delete
            ).delete()
            ListCumulation.objects.filter(pk__in=for_delete).delete()

    def save_periods(self, prontuary=None, range_dates=None, el_list=[]):
        rst = 0
        if range_dates:
            cumulation = Cumulation.objects.filter(prontuary=prontuary).first()
            if cumulation is None:
                cumulation = Cumulation()
                cumulation.prontuary = prontuary
                cumulation.save()
            listcumulation = ListCumulation.objects.filter(
                cumulation=cumulation,
                date_initial=range_dates.start_date,
                date_final=range_dates.end_date,
            ).first()
            if listcumulation is None:
                if range_dates.end_date is None:
                    if range_dates.start_date <= datetime.now().date():
                        range_to_now = NewDateRange(
                            range_dates.start_date, datetime.now().date()
                        )
                        days = range_to_now.days
                    else:
                        days = 0
                listcumulation = ListCumulation()
                listcumulation.cumulation = cumulation
                listcumulation.date_initial = range_dates.start_date
                listcumulation.date_final = range_dates.end_date
                listcumulation.total_days = (
                    range_dates.days if range_dates.end_date else days
                )
                listcumulation.save()
            port = 0
            for el in el_list:
                if not DetailListCumulation.objects.filter(
                    listcumulation=listcumulation, employeelocation=el
                ).exists():
                    detaillistcumulation = DetailListCumulation()
                    detaillistcumulation.listcumulation = listcumulation
                    detaillistcumulation.employeelocation = el
                    if el.substitution_substitute.all().count() == 0:
                        port = port + 1
                    detaillistcumulation.save()
            if port > 1:
                listcumulation.mark_realcumulation()
                listcumulation.mark_activecumulation()
            rst = listcumulation.pk
        return rst

    def reload(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            prontuary = Prontuary.objects.filter(
                pk=int(params.get("prontuary", 0) or 0)
            ).first()
            if Cumulation.objects.filter(prontuary=prontuary).exists():
                prontuary.cumulation.listcumulations.all().delete()
            analyzed = []
            # TODO definir os parâmetros que efetivamente correspondem aos exercícios que serão considerados para CUMULACAO.
            query = ServidorLotacao.objects.filter(
                servidor=prontuary.employee,
                lotacao__in=ExecutionOrgan.objects.all().values_list("pk"),
            ).filter(designacao=True)
            # query = ServidorLotacao.objects.filter(servidor=prontuary.employee, lotacao__in=ExecutionOrgan.objects.all().values_list('pk')).filter(designacao=True, substitution_substitute=None)
            if prontuary.get_lastmeritoriousness is not None:
                query = query.filter(
                    data_vigencia_inicio__gt=prontuary.get_lastmeritoriousness.instancia_modelo.data_exercicio
                )
            for sl1 in query.exclude(pk__in=analyzed).order_by("data_vigencia_inicio"):
                if (
                    sl1.data_vigencia_fim
                    and sl1.data_vigencia_inicio <= sl1.data_vigencia_fim
                ) or sl1.data_vigencia_fim is None:
                    analyzed.append(sl1.pk)
                    dr1 = NewDateRange(sl1.data_vigencia_inicio, sl1.data_vigencia_fim)
                    for sl2 in query.exclude(pk__in=analyzed).order_by(
                        "data_vigencia_inicio"
                    ):
                        if (
                            sl2.data_vigencia_fim
                            and sl2.data_vigencia_inicio <= sl2.data_vigencia_fim
                        ) or sl2.data_vigencia_fim is None:
                            lists = []
                            dr2 = NewDateRange(
                                sl2.data_vigencia_inicio, sl2.data_vigencia_fim
                            )
                            dr3 = dr1.intersect(dr2)
                            if sl1.pk != sl2.pk and dr3.days > 0:
                                lists.append(sl1)
                                lists.append(sl2)
                                self.save_periods(
                                    prontuary=prontuary, range_dates=dr3, el_list=lists
                                )
            self.normalize_cumulations(prontuary=prontuary)
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Lista de exercícios simultâneos carregada com sucesso.",
            )
        return self.renderer(rst)

    def mark_realcumulation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            listcumulation = ListCumulation.objects.filter(
                pk=(
                    int(params.get("listcumulation"))
                    if params.get("listcumulation") != ""
                    else 0
                )
            ).first()
            if listcumulation:
                listcumulation.mark_realcumulation()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção/Correição marcada com sucesso.",
            )
        return self.renderer(rst)

    def mark_activecumulation(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}
        try:
            params = self.request.POST
            listcumulation = ListCumulation.objects.filter(
                pk=(
                    int(params.get("listcumulation"))
                    if params.get("listcumulation") != ""
                    else 0
                )
            ).first()
            if listcumulation:
                listcumulation.mark_activecumulation()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Inspeção/Correição marcada com sucesso.",
            )
        return self.renderer(rst)

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:
            params = self.request.POST
            listcumulation = ListCumulation.objects.filter(
                pk=int(params.get("listcumulation", 0) or 0)
            ).first()
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, content=listcumulation.rendered)
        self.renderer(rst)
