# -*- coding:utf-8 -*-
import datetime
from contrib.extjs import ExtWidget
from contrib.controller import ContentType
from contrib.decorator import login_required, validate
from contrib.br import br_number, br_money, br_abbreviated_month

from bi.db import SimpleDB
from bi.forms import ReportForm


class BI(ExtWidget):

    __regions = []
    __indexes = {}

    def __init__(self, *a, **k):
        super(ExtWidget, self).__init__(*a, **k)

        if not self.__regions:
            with SimpleDB() as conn:
                self.__regions = conn.query(
                    """
                    select c.com_numero pgj_id, rc.id athenas_id, rc.nome name
                    from PGJ.COMARCA c
                    left join rh_comarca rc on c.COM_NOME = rc.NOME
                    where c.CIR_NUMERO is not null
                    order by c.com_nome
                """
                )
            self.__indexes = dict(
                [
                    (
                        int(item["athenas_id"]),
                        dict(id=int(item["pgj_id"]), name=item["name"]),
                    )
                    for item in self.__regions
                ]
            )

    @ContentType("text/javascript")
    @login_required(type="JSON")
    def json(self, args=[]):
        self.render("toolkit.bi.regions = new toolkit.bi.Regions()")

    @ContentType("text/javascript")
    @login_required(type="JSON")
    def regions(self, args=[]):
        self.render(dict(total=len(self.__regions), list=self.__regions))

    @ContentType("text/javascript")
    @login_required(type="JSON")
    @validate(ReportForm)
    def simple_report(self, args=[]):
        date = datetime.date.today()
        data = getattr(self.request, "data", self.request.REQUEST)

        region = data.get("region")
        region2 = data.get("region2", region)

        month2 = data.get("month2", date.strftime("%m"))
        year2 = data.get("year2", date.year)

        month = int(month2) - 1 if (int(month2) - 1) > 0 else 12
        month = data.get("month", "0%s" % month if month < 10 else month)
        year = data.get("year", year2 - 1)

        func_pars = {
            self.__indexes[region]["name"]: [
                [region, month, year],
                [region, month2, year2],
            ]
        }
        if region2 and region2 != region:
            func_pars[self.__indexes[region2]["name"]] = [
                [region2, month, year],
                [region2, month2, year2],
            ]

        reports = []
        for _region, pars in list(func_pars.items()):
            supplies = {"name": "Suprimentos", "periods": []}
            heritage = {"name": "Patrimônio", "periods": []}
            payroll = {"name": "Folha de Pagamento", "periods": []}
            # lawsuit = {'name': 'Processos Entregues', 'periods': []}
            prosecutors = {"name": "Quantidade de Membros", "periods": []}
            employees = {"name": "Quantidade de Servidores", "periods": []}

            works = [
                (self.__supplies, br_money, supplies),
                (self.__heritage, br_money, heritage),
                (self.__payroll, br_money, payroll),
                # (self.__lawsuit, br_number, lawsuit),
                (self.__prosecutors, br_number, prosecutors),
                (self.__employees, br_number, employees),
            ]

            for p in pars:
                period = "%s %s" % (br_abbreviated_month(p[1]), p[2])

                for func, normalizer, container in works:
                    value, human_value, result = 0, 0, func(*p)
                    if result:
                        value = result[0].get("total", "0")
                        human_value = normalizer(value)
                        container["periods"].append(
                            {
                                "value": value,
                                "human_value": human_value,
                                "period": period,
                            }
                        )

            # reports.append({'region':_region, 'data': [supplies, heritage, payroll, lawsuit, prosecutors, employees]})
            reports.append(
                {
                    "region": region,
                    "data": [supplies, heritage, payroll, prosecutors, employees],
                }
            )

        self.render({"success": True, "reports": reports})

    @ContentType("text/javascript")
    @login_required(type="JSON")
    @validate(ReportForm)
    def detailed_report(self, args=[]):
        pass

    @login_required(type="JSON")
    def __supplies(self, region, month, year, full=False):
        sql = (
            ""
            if full
            else "SELECT sum(valor_total) as total from BI_ALMOXARIFADO(%s,%s,%s);"
        )
        sql = sql % (region, month, year)
        return self.__run_query("almoxarifado", sql)

    @login_required(type="JSON")
    def __heritage(self, region, month, year, full=False):
        sql = "" if full else "SELECT sum(total) as total from BI_PATRIMONIO(%s,%s,%s);"
        sql = sql % (region, month, year)
        return self.__run_query("patrimonio", sql)

    @login_required(type="JSON")
    def __payroll(self, region, month, year, full=False):
        sql = (
            ""
            if full
            else """
            select nvl(valor_servidores+valor_membros+valor_estagiarios, 0) as total
            from (select * from table (Bi_Rh_Gfp (%s,%s,%s)))
        """
        )
        sql = sql % (region, month, year)
        return self.__run_query("default", sql)

    @login_required(type="JSON")
    def __lawsuit(self, region, month, year, full=False):
        region = self.__indexes[region]["id"]
        sql = (
            ""
            if full
            else """select entregues as total from table (Bi_Raf(%s, '%s-%s-01'))"""
        )

        sql = sql % (region, year, month)
        return self.__run_query("default", sql)

    @login_required(type="JSON")
    def __prosecutors(self, region, month, year, full=False):
        sql = (
            ""
            if full
            else """select membros as total from table (Bi_Rh_Gfp (%s,%s,%s))"""
        )

        sql = sql % (region, month, year)
        return self.__run_query("default", sql)

    @login_required(type="JSON")
    def __employees(self, region, month, year, full=False):
        sql = (
            ""
            if full
            else """select servidores as total from table (Bi_Rh_Gfp (%s,%s,%s))"""
        )

        sql = sql % (region, month, year)
        return self.__run_query("default", sql)

    @login_required(type="JSON")
    def __run_query(self, name, sql):
        rs = []
        with SimpleDB(name) as conn:
            rs = conn.query(sql)
        return rs
