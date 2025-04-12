# -*- coding:utf-8 -*-
from django.db.models import (
    Q,
    When,
    Case,
    Value,
    TextField,
)
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from corregedoria.reportbuilder.pdfgenerator import PDFGenerator
from corregedoria.cirdir.models import (
    Address,
    ControlInformation,
    Debits,
    Pendency,
    Property,
    Institution,
    Irpf,
)


class EmployeePendenceIRPFReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Servidores que não anexaram a declaração do IRPF - DBVR {}".format(
            self.params.get("year_base", "")
        )

    def _query_report(self, year):
        query = Q(
            ~Q(employee__tipo="M")
            & Q(in_irpf__isnull=True)
            & Q(Q(hidden=False) & Q(year=year))
        )
        return query

    def load_csv(self):
        header = ["employee__matricula", "employee__pessoa_fisica__nome"]
        year = self.params.get("year_base", 0)

        query = self._query_report(year)

        result = ControlInformation.objects.filter(query).values(
            "employee__matricula",
            "employee__pessoa_fisica__nome",
        )

        return list(result), header

    def load(self):
        year = self.params.get("year_base", 0)
        query = self._query_report(year)

        result = ControlInformation.objects.filter(query).order_by(
            "employee__pessoa_fisica__nome"
        )

        if result.exists():
            data = [["Matr.", "Nome", "Tipo"]]
            data.extend(
                [
                    [
                        i.employee.matricula,
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.employee.tipo,
                    ]
                    for i in result
                ]
            )
            self.add_table_2(data, colWidths=(None, 80 * mm, None))
        else:
            self.add_paragraph(self.empty, self.choice_alignment("center"))

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class EmployeePendenceReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Servidores com Pendência - DBVR {}".format(
            self.params.get("year_base", "")
        )

    def load_csv(self):
        # header = ['Nome', 'Bens e Direitos', 'Dívidas e Ônus']
        header = [
            "employee__matricula",
            "employee__pessoa_fisica__nome",
            "bens_e_direitos",
            "dividas_e_onus",
        ]
        year = self.params.get("year_base", 0)

        query = Q(
            ~Q(employee__tipo="M")
            & Q(Q(property_submitted_at=None) | Q(debits_submitted_at=None))
            & Q(Q(hidden=False) & Q(year=year))
        )

        result = (
            ControlInformation.objects.filter(query)
            .annotate(
                bens_e_direitos=Case(
                    When(property_submitted_at=None, then=Value("Não submetido")),
                    default=Value("Submetido"),
                    output_field=TextField(),
                )
            )
            .annotate(
                dividas_e_onus=Case(
                    When(debits_submitted_at=None, then=Value("Não submetido")),
                    default=Value("Submetido"),
                    output_field=TextField(),
                )
            )
            .values(
                "employee__matricula",
                "employee__pessoa_fisica__nome",
                "bens_e_direitos",
                "dividas_e_onus",
            )
        )

        return list(result), header

    def load(self):
        year = self.params.get("year_base", 0)
        query = Q(
            Q(Q(property_submitted_at=None) | Q(debits_submitted_at=None))
            & Q(Q(hidden=False) & Q(year=year))
        )

        result = (
            ControlInformation.objects.exclude(employee__tipo="M")
            .filter(query)
            .order_by("employee__pessoa_fisica__nome")
        )

        # Data for table
        f_format = lambda x: "Não submetido" if x is None else "Submetido"

        # self.add_paragraph(
        #     u'<center><h2><b>Servidores com Pendência - DBVR {}</b></h2></center>'.format(year),
        #     self.choice_alignment('center')
        # )
        # self.add_spacer()

        if result.exists():
            data = [["Matr.", "Nome", "Tipo", "Bens e Direitos", "Dívidas e Ônus"]]
            data.extend(
                [
                    [
                        i.employee.matricula,
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.employee.tipo,
                        f_format(i.property_submitted_at),
                        f_format(i.debits_submitted_at),
                    ]
                    for i in result
                ]
            )
            self.add_table_2(data, colWidths=(None, 80 * mm, None, None, None))
        else:
            self.add_paragraph(self.empty, self.choice_alignment("center"))

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class EmployeeMemberPendenceReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Membros com Pendência - Bens e Direitos, Dívidas e Ônus - {}".format(
            self.params.get("year_base", "")
        )

    def load(self):
        year = self.params.get("year_base", 0)
        query = Q(
            Q(Q(property_submitted_at=None) | Q(debits_submitted_at=None))
            & Q(Q(hidden=False) & Q(year=year) & Q(employee__tipo="M"))
        )

        result = ControlInformation.objects.filter(query).order_by(
            "employee__pessoa_fisica__nome"
        )

        # Data for table
        f_format = lambda x: "Não submetido" if x is None else "Submetido"

        if result.exists():
            data = [["Matr.", "Nome", "Bens e Direitos", "Dívidas e Ônus"]]
            data.extend(
                [
                    [
                        i.employee.matricula,
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        f_format(i.property_submitted_at),
                        f_format(i.debits_submitted_at),
                    ]
                    for i in result
                ]
            )
            self.add_table_2(data, colWidths=(None, 100 * mm, None, None))
        else:
            self.add_paragraph(self.empty, self.choice_alignment("center"))

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class SubmittedAfterDeadlineReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Lista de {} que submeteram após o prazo - {}".format(
            "Membros", self.params.get("year_base", "")
        )

    def load_address(self):
        year_base = int(self.params.get("year_base", 0))
        deadlines = ControlInformation.get_default_config_date(year=year_base)

        result = ControlInformation.get_address_submitted_after_deadline(
            year=year_base,
            employee_kind="M",
            deadline=deadlines.get("close_date_address"),
        )

        summary = """<b>Item:</b> {}<br />
        <b>Prazo:</b> {}<br />
        <b>Quantidade:</b> {}"""

        self.add_paragraph(
            summary.format(
                "Endereço",
                deadlines.get("close_date_address").strftime("%d/%m/%Y"),
                result.count(),
            ),
        )

        if result.exists():
            data = [["NOME", "SUBMETIDO EM"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.address_submitted_at.strftime("%d/%m/%Y"),
                    ]
                    for i in result
                ]
            )

            self.add_table_default(data, colWidths=(120 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado", self.choice_alignment("center")
            )

    def load_property(self):
        year_base = int(self.params.get("year_base", 0))
        deadlines = ControlInformation.get_default_config_date(year=year_base)

        result = ControlInformation.get_property_submitted_after_deadline(
            year=year_base,
            employee_kind="M",
            deadline=deadlines.get("close_date_property"),
        )

        summary = """<b>Item:</b> {}<br />
        <b>Prazo:</b> {}<br />
        <b>Quantidade:</b> {}"""

        self.add_paragraph(
            summary.format(
                "Bens e Direitos",
                deadlines.get("close_date_property").strftime("%d/%m/%Y"),
                result.count(),
            ),
        )

        if result.exists():
            data = [["NOME", "SUBMETIDO EM"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.property_submitted_at.strftime("%d/%m/%Y"),
                    ]
                    for i in result
                ]
            )
            self.add_table_default(data, colWidths=(120 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado", self.choice_alignment("center")
            )

    def load_debits(self):
        year_base = int(self.params.get("year_base", 0))
        deadlines = ControlInformation.get_default_config_date(year=year_base)

        result = ControlInformation.get_debits_submitted_after_deadline(
            year=year_base,
            employee_kind="M",
            deadline=deadlines.get("close_date_debits"),
        )

        summary = """<b>Item:</b> {}<br />
        <b>Prazo:</b> {}<br />
        <b>Quantidade:</b> {}"""

        self.add_paragraph(
            summary.format(
                "Dívidas e Ônus",
                deadlines.get("close_date_debits").strftime("%d/%m/%Y"),
                result.count(),
            ),
        )

        if result.exists():
            data = [["NOME", "SUBMETIDO EM"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.debits_submitted_at.strftime("%d/%m/%Y"),
                    ]
                    for i in result
                ]
            )
            self.add_table_default(data, colWidths=(120 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado", self.choice_alignment("center")
            )

    def load_teaching_one(self):
        year_base = int(self.params.get("year_base", 0))
        deadlines = ControlInformation.get_default_config_date(year=year_base)

        result = ControlInformation.get_teaching_one_submitted_after_deadline(
            year=year_base,
            employee_kind="M",
            deadline=deadlines.get("close_date_teaching_1st_semestry"),
        )

        summary = """<b>Item:</b> {}<br />
        <b>Prazo:</b> {}<br />
        <b>Quantidade:</b> {}"""

        self.add_paragraph(
            summary.format(
                "Docência 1º Semestre",
                deadlines.get("close_date_teaching_1st_semestry").strftime("%d/%m/%Y"),
                result.count(),
            ),
        )

        if result.exists():
            data = [["NOME", "SUBMETIDO EM"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.teaching_1st_semestry_submitted_at.strftime("%d/%m/%Y"),
                    ]
                    for i in result
                ]
            )

            self.add_table_default(data, colWidths=(120 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado", self.choice_alignment("center")
            )

    def load_teaching_two(self):
        year_base = int(self.params.get("year_base", 0))
        deadlines = ControlInformation.get_default_config_date(year=year_base)

        result = ControlInformation.get_teaching_two_submitted_after_deadline(
            year=year_base,
            employee_kind="M",
            deadline=deadlines.get("close_date_teaching_2nd_semestry"),
        )

        summary = """<b>Item:</b> {}<br />
        <b>Prazo:</b> {}<br />
        <b>Quantidade:</b> {}"""

        self.add_paragraph(
            summary.format(
                "Docência 2º Semestre",
                deadlines.get("close_date_teaching_2nd_semestry").strftime("%d/%m/%Y"),
                result.count(),
            ),
        )

        if result.exists():
            data = [["NOME", "SUBMETIDO EM"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        i.teaching_2nd_semestry_submitted_at.strftime("%d/%m/%Y"),
                    ]
                    for i in result
                ]
            )

            self.add_table_default(data, colWidths=(120 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado", self.choice_alignment("center")
            )

    def load(self):
        self.load_address()
        self.load_property()
        self.load_debits()
        self.load_teaching_one()
        self.load_teaching_two()

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class MemberPendenceListReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Lista de Pendências - Ano {}".format(self.params.get("year_base", ""))

    def load_item_address(self, query=None):
        title = "Endereço"
        query = query.filter(pendency_address=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(i.pendency_address_msg, self.getStyle("Normal")),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )

    def load_item_property(self, query=None):
        title = "Bens e Direitos"
        query = query.filter(pendency_property=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(i.pendency_property_msg, self.getStyle("Normal")),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )

    def load_item_debits(self, query=None):
        title = "Dívidas e Ônus"
        query = query.filter(pendency_debits=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(i.pendency_debits_msg, self.getStyle("Normal")),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )

    def load_item_teaching1(self, query=None):
        title = "Docência 1º Semestre"
        query = query.filter(pendency_teaching_1st_semestry=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(
                            i.pendency_teaching_1st_semestry_msg,
                            self.getStyle("Normal"),
                        ),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )

    def load_item_teaching2(self, query=None):
        title = "Docência 2º Semestre"
        query = query.filter(pendency_teaching_2nd_semestry=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(
                            i.pendency_teaching_2nd_semestry_msg,
                            self.getStyle("Normal"),
                        ),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )
            self.add_paragraph("", self.choice_alignment("center"))

    def load_item_irpf(self, query=None):
        title = "IRPF"
        query = query.filter(pendency_irpf=True)

        if query.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph("{}".format(query.count()), self.getStyle("Normal")),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.employee.pessoa_fisica.nome, self.getStyle("Normal")
                        ),
                        Paragraph(i.pendency_irpf_msg, self.getStyle("Normal")),
                    ]
                    for i in query
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )

    def load(self):
        employee_kind = self.params.get("employee_kind", "M")
        year_base = int(self.params.get("year_base", 0))

        result = ControlInformation.objects.filter(
            year=year_base, employee__tipo=employee_kind
        )

        if self.params.get("address", False):
            self.load_item_address(query=result)

        if self.params.get("property", False):
            self.load_item_property(query=result)

        if self.params.get("debits", False):
            self.load_item_debits(query=result)

        if self.params.get("teaching1", False):
            self.load_item_teaching1(query=result)

        if self.params.get("teaching2", False):
            self.load_item_teaching2(query=result)

        if self.params.get("irpf", False):
            self.load_item_irpf(query=result)

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class MemberTeachingReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "MEMBROS QUE EXERCEM DOCÊNCIA - Ano {}".format(
            self.params.get("year_base", "")
        )

    def detail_schedule(self, query):
        self.add_spacer()
        for s in query:
            self.add_bullet(s.get_schedule_time)
        self.add_spacer()

    def detail_discipline(self, query, inst, period):
        teachings = query.in_teaching.filter(period=period, institution=inst.pk)
        # discipline = Discipline.objects.filter(pk__in=teachings.values_list('discipline__pk', flat=True))
        for t in teachings:
            data = [["Disciplina", "Carga H.", "Autorizado"]]
            data.extend(
                [
                    [
                        Paragraph(t.discipline.name, self.getStyle("Normal")),
                        t.work_hours,
                        Paragraph("Sim", self.getStyle("Normal")),
                    ]
                ]
            )
            self.add_invisible_table(data, colWidths=(100 * mm, None, None))
            self.detail_schedule(t.schedule.filter().order_by("day_week"))

    def detail_institution(self, query, period):
        institution = Institution.objects.filter(
            pk__in=query.in_teaching.filter(period=period).values_list("institution")
        )
        for inst in institution:
            data = [["Instituição", "Cidade"]]
            data.extend(
                [
                    [
                        Paragraph(inst.nome, self.getStyle("Normal")),
                        Paragraph(inst.county.nome, self.getStyle("Normal")),
                    ]
                ]
            )
            self.add_invisible_table(data, colWidths=(100 * mm, None))
            self.detail_discipline(query, inst, period)

    def load_teaching(self, query, period):
        self.add_spacer()
        self.add_paragraph(
            "<b>{}º SEMESTRE</b>".format(period), self.choice_alignment("center")
        )

        result = query.filter(in_teaching__period=period).distinct()

        qtd_title = "ocorrências" if result.count() > 1 else "ocorrência"
        self.add_paragraph(
            "{} {}".format(result.count(), qtd_title), self.choice_alignment("right")
        )

        count = 1
        if result.exists():
            for r in result.filter():

                self.add_paragraph(
                    "{} - {}".format(count, r.employee.pessoa_fisica.nome)
                )

                count = count + 1
                self.detail_institution(r, period)
                self.add_spacer()
        else:
            self.add_paragraph("Sem resultados", self.choice_alignment("center"))

    def load(self):
        employee_kind = self.params.get("employee_kind", "M")
        year_base = int(self.params.get("year_base", 0))

        query = ControlInformation.objects.filter(
            year=year_base, in_teaching__isnull=False
        ).distinct()

        self.load_teaching(query, 1)
        self.load_teaching(query, 2)

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class ReportBase(PDFGenerator):

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""


class PendenciesReport(ReportBase):

    @property
    def header_report_title(self):
        return "Lista de Pendências - Ano {}".format(self.params.get("year_base", ""))

    def load(self):
        year_base = int(self.params.get("year_base", 0))

        queryset = ControlInformation.objects.filter(
            year=year_base,
            hidden=False,
            employee__tipo=self.params.get("employee_type", ""),
        )

        items = self.params.get("parts", [])

        if not queryset:
            self.add_paragraph(self.empty, self.choice_alignment("center"))
        else:
            for item in items:
                self.load_item(queryset, item)

    def load_item(self, queryset, codename):
        title = {
            "address": "Endereço",
            "teaching_1st_semestry": "Docência 1º Semestre",
            "teaching_2nd_semestry": "Docência 2º Semestre",
            "debits": "Dívidas e Ônus",
            "property": "Bens e Direitos",
            "irpf": "Declaração do imposto de renda",
        }.get(codename, "Não definido")

        pendencies = Pendency.objects.filter(
            control_information__in=queryset, part=codename
        )

        if pendencies.exists():
            summary = [["Item", "Ocorrências"]]
            summary.extend(
                [
                    [
                        Paragraph(title, self.getStyle("Normal")),
                        Paragraph(
                            "{}".format(pendencies.count()), self.getStyle("Normal")
                        ),
                    ]
                ]
            )

            data = [["Nome", "Pendência"]]
            data.extend(
                [
                    [
                        Paragraph(
                            i.control_information.employee.pessoa_fisica.nome,
                            self.getStyle("Normal"),
                        ),
                        Paragraph(i.message, self.getStyle("Normal")),
                    ]
                    for i in pendencies
                ]
            )

            self.add_table_default(data, summary=summary, colWidths=(100 * mm, None))
        else:
            self.add_paragraph(
                "Não retornou resultado para {}".format(title),
                self.choice_alignment("center"),
            )


class ListAddressReport(ReportBase):

    @property
    def header_report_title(self):
        return "Listagem de Endereços - Ano {}".format(self.params.get("year_base", ""))

    def load(self):
        year_base = int(self.params.get("year_base", 0))
        information_pks = None
        information_pks = ControlInformation.objects.filter(
            year=year_base,
            hidden=False,
            employee__tipo=self.params.get("employee_type", ""),
        ).values_list("pk", flat=True)

        if not information_pks:
            self.add_paragraph(self.empty, self.choice_alignment("center"))
        else:
            address = (
                Address.objects.filter(controlinformation__in=information_pks)
                .select_related(
                    "controlinformation__employee",
                    "ref_address__municipio__comarca",
                )
                .order_by("controlinformation__employee")
            )

            if address.exists():

                def get_comarca(addr):
                    workplace = addr.controlinformation.employee.workplace_current

                    if workplace:
                        return workplace.localidade.comarca
                    else:
                        return "---"

                # summary = [["Qtd. Membros", "a", "a",  "Qtd. Endereços"]]
                summary = [["Qtd. de Registros"]]
                summary.extend(
                    [
                        [
                            Paragraph(
                                f"{information_pks.count()}", self.getStyle("Normal")
                            ),
                        ]
                    ]
                )

                # data = [["Nome", "Comarca titularidade", "Comarca da residência", "Endereço"]]
                data = [["Nome", "Comarca titularidade", "Comarca residência"]]
                data.extend(
                    [
                        [
                            Paragraph(
                                f"{addr.controlinformation.employee}",
                                self.getStyle("Normal"),
                            ),
                            Paragraph(f"{get_comarca(addr)}", self.getStyle("Normal")),
                            Paragraph(
                                f"{addr.ref_address.municipio.comarca}",
                                self.getStyle("Normal"),
                            ),
                            Paragraph(f"{addr.ref_address}", self.getStyle("Normal")),
                        ]
                        for addr in address
                    ]
                )

                self.add_table_default(
                    data,
                    summary=summary,
                    colWidths=(70 * mm, None, None, None),
                    summary_colWidths=(180 * mm),
                )
            else:
                self.add_paragraph(
                    "Não retornou resultado para Endereço",
                    self.choice_alignment("center"),
                )
