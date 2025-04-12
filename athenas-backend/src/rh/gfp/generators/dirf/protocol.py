# -*- coding: utf-8 -*-

from django.db.models import FloatField, Max, Sum

from contrib.helpers import clear_to_ascii as tira_acentos
from contrib.protofile import GroupRecords, Protocol, Record
from contrib.utils import getLogger
from rh.gfp.dirf.models import (
    INFORMATION_TAGS,
    Declaracao,
    DirfSummary,
    NaturezaRendimento,
)
from rh.gfp.generators.dirf.layouts import DIRF
from rh.gfp.models import RRA
from rh.gfp.models import Servidor as Employee
from rh.models import Dependente as Dependent
from rh.models import UnidadeAdministrativa
from standard.models import Choice, Configuration

__name__ = "RFB - DIRF"

log = getLogger(__name__)


class RecordDirf(Record):
    _protocol = DIRF
    _separator = "|"
    _separator_on_end_line = "|"


class GroupRecordsInf(GroupRecords):
    def __init__(self, cls, **kargs):
        self.json_config = {}
        super(GroupRecordsInf, self).__init__(cls, None, None, **kargs)

    def formated_inf(self, cpf):
        if cpf not in self.json_config:
            return ""
        formated_text = "<pre>"
        for key in self.json_config[cpf]:
            formated_text += "%s:<br />" % tira_acentos(key)
            for info in self.json_config[cpf][key]:
                formated_text += " - %s<br />" % tira_acentos(info)
            formated_text += "<br />"
        formated_text += "</pre>"
        return formated_text

    def add(self, cpf, key, info, **kargs):
        if cpf not in self.json_config:
            self.json_config[cpf] = {}
        if key not in self.json_config[cpf]:
            self.json_config[cpf][key] = []
        self.json_config[cpf][key].append(info)
        rec = self.get("cpf", cpf)
        if not rec:
            rec = super(GroupRecordsInf, self).add(
                "INF", cpf=cpf, informacoes_complementares=self.formated_inf(cpf)
            )
        else:
            rec.update_value("informacoes_complementares", self.formated_inf(cpf))

        return rec


class File(Protocol):
    """ """

    def __init__(self, dialect, receipt_number="", persons=[]):
        super(File, self).__init__()
        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.cfg = Configuration.objects.get(application="gfp")
        self.email = self.cfg.get("email_gfp")
        self.uadm = UnidadeAdministrativa.objects.get(pk=self.cfg.get("orgao"))
        self.dialect = dialect
        self.persons = persons

        self.receipt_number = receipt_number
        self.regs = []

        self.main_group = GroupRecords(
            RecordDirf,
            "DIRF",
            "FIMDIRF",
            **{
                "ano_referencia": self.dialect.reference_year,
                "ano_calendario": self.dialect.calendar_year,
                "indicador_retificadora": "S" if self.receipt_number else "N",
                "numero_recibo": self.receipt_number or None,
                "identificador_layout": self.dialect.identificador_layout,
            },
        )

        self.employee_manager = Employee.objects.get(
            pk=int(self.cfg.get("responsavel_gfp"))
        )
        self.master_manager = Employee.objects.get(
            pk=int(self.cfg.get("responsavel_orgao"))
        )

        self.main_group.add(
            "RESPO",
            **{
                "cpf": int(self.employee_manager.pessoa_fisica.cpf or 0),
                "nome": tira_acentos(self.employee_manager.pessoa_fisica.nome).strip(),
                "ddd": self.cfg.get("telefone_responsavel_gfp")[0:2],
                "telefone": self.cfg.get("telefone_responsavel_gfp")[2:],
                "ramal": self.cfg.get("telefone_responsavel_gfp")[-4:],
                "fax": self.cfg.get("fax_gfp")[2:],
                "email": self.cfg.get("email_gfp"),
            },
        )

        self.decpj_group = GroupRecords(
            RecordDirf,
            "DECPJ",
            None,
            **{
                "cnpj": int(self.uadm.pessoa_juridica.cnpj or 0),
                "nome_empresarial": tira_acentos(
                    self.uadm.pessoa_juridica.razao_social
                ),
                "cpf_responsavel": int(self.master_manager.pessoa_fisica.cpf or 0),
            },
        )

        self.rra_groups = {}  # GroupRecords(RecordDirf, 'RRA', None, **config_rra)
        for rra in RRA.objects.filter():
            query_rra = rra.employeers.filter(
                entries__folha__periodo__ano=self.dialect.calendar_year
            )
            if persons:
                query_rra = query_rra.filter(employee__pessoa_fisica__pk__in=persons)
            if query_rra.exists():
                process = rra.process or ""
                process = (
                    process.replace(".", "").replace("-", "").replace("/", "").strip()
                )
                self.rra_groups[rra] = GroupRecords(
                    RecordDirf, "RRA", None, **{"numero_processo": process}
                )

        self.inf_group = GroupRecordsInf(RecordDirf)

    def _update_demonstrative(
        self, demonstrative, identifier, values, rra=None, pensioner=None
    ):
        if not demonstrative:
            return None

        if identifier == "INF":
            demonstrative.informacao_complementar = values

        elif demonstrative.natureza.codigo in ("0561", "3208", "0916", "0588"):
            if identifier == "BPFDEC-RTRT":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.rendimento = total_value
                demonstrative.decimoterceiro += round((values.get("m13") or 0), 2)
            elif identifier == "BPFDEC-RTPO":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.previdencia_oficial = total_value
                demonstrative.decimoterceiro -= round((values.get("m13") or 0), 2)
            elif identifier == "BPFDEC-RIMOG":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.rendimento_molestia = total_value
            elif identifier == "BPFDEC-RTIRF":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.imposto_retido = total_value
                demonstrative.decimoterceiro -= round((values.get("m13") or 0), 2)
                demonstrative.decimoterceiro_imposto = values.get("m13") or 0
            elif identifier == "BPFDEC-RIDAC":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.ajuda_custo = total_value
            elif identifier == "BPFDEC-RIIRP":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.idenizacao = total_value
            elif identifier == "BPFDEC-RIAP":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.outros += round(total_value, 2)
            elif identifier == "BPFDEC-RIO":
                demonstrative.outros += round(
                    float(values.get("valor_pago_ano") or 0), 2
                )
                if demonstrative.outros_descricao and values.get(
                    "descricao_rendimentos"
                ):
                    demonstrative.outros_descricao += ", "
                demonstrative.outros_descricao += (
                    values.get("descricao_rendimentos") or ""
                )
            elif identifier == "BPFDEC-RTPA":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.pensao_alimenticia += round((total_value), 2)
                demonstrative.decimoterceiro -= round((values.get("m13") or 0), 2)
            elif identifier == "BPFDEC-RTDP":
                demonstrative.decimoterceiro -= round((values.get("m13") or 0), 2)

        elif demonstrative.natureza.codigo in ("1889",):
            if identifier == "BPFRRA-RTRT":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.rendimento = total_value
            elif identifier == "BPFRRA-RTPO":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.previdencia_oficial = total_value
            elif identifier == "BPFRRA-RIMOG":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.rendimento_molestia = total_value
            elif identifier == "BPFRRA-RTIRF":
                total_value = 0
                for x in range(1, 14):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.imposto_retido = total_value
            elif identifier == "BPFRRA-RTPA":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.pensao_alimenticia += round(total_value, 2)
            elif identifier == "BPFRRA-QTMESES":
                total_value = 0
                for x in range(1, 13):
                    total_value += values.get("m%02d" % x) or 0
                demonstrative.qnt_meses = total_value

    def _clear_negatives(self, values, include_13=False):
        month = loop = 1
        negative = 0
        months = 12 if not include_13 else 13
        while loop == 1 or (loop == 2 and negative != 0):
            idx = "m%02d" % month
            values[idx] += negative
            negative = 0
            if values[idx] < 0:
                negative = values[idx]
                values[idx] = 0

            month += 1
            if month > months:
                month = 1
                loop += 1

        # Evaluate month = 13
        if values["m13"] < 0 and not include_13:
            values["m13"] = 0

        return values

    def _add_records_default(
        self,
        person,
        group,
        identifier,
        rra=None,
        pensioner=None,
        layout="VALUES",
        total_months=13,
        demonstrative=None,
    ):
        # print 'IDENTIFIER: %s' % identifier
        choice = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label=identifier
        ).value
        q_summary = person.dirf_summaries.filter(
            calendar_year=self.dialect.calendar_year,
            identifier=choice,
            rra=rra,
            pensioner=pensioner,
        )
        information_tag = ", ".join(
            [
                tira_acentos(ds.info)
                for ds in q_summary.order_by("info").distinct("info")
            ]
        )
        if q_summary:
            values = q_summary.aggregate(
                m01=Sum("value_01", output_field=FloatField()),
                m02=Sum("value_02", output_field=FloatField()),
                m03=Sum("value_03", output_field=FloatField()),
                m04=Sum("value_04", output_field=FloatField()),
                m05=Sum("value_05", output_field=FloatField()),
                m06=Sum("value_06", output_field=FloatField()),
                m07=Sum("value_07", output_field=FloatField()),
                m08=Sum("value_08", output_field=FloatField()),
                m09=Sum("value_09", output_field=FloatField()),
                m10=Sum("value_10", output_field=FloatField()),
                m11=Sum("value_11", output_field=FloatField()),
                m12=Sum("value_12", output_field=FloatField()),
                m13=Sum("value_13", output_field=FloatField()),
            )
            identifier_record = identifier.split("-")[-1]
            values = self._clear_negatives(values)
            total_value = sum(values.values())
            # log.debug('ADR (%s) %s %s RRA: %s Pensioner: %s %s'
            #   % (q_summary.count(), layout, identifier, rra, pensioner, values))
            if total_value > 0:
                group.add(layout, identificador_registro=identifier_record, **values)
                self._update_demonstrative(
                    demonstrative, identifier, values, rra=rra, pensioner=pensioner
                )
                if INFORMATION_TAGS.get(identifier, None) and information_tag:
                    rec = self.inf_group.add(
                        person.pessoafisica.cpf,
                        INFORMATION_TAGS.get(identifier, None),
                        "%s: RS %6.2f" % (information_tag, total_value),
                    )
                    self._update_demonstrative(
                        demonstrative, "INF", rec.get("informacoes_complementares")
                    )

        return [ds.pk for ds in q_summary]

    def _add_records_bpfrra_qtmeses(
        self,
        person,
        group,
        identifier,
        rra=None,
        pensioner=None,
        layout="QTMESES",
        demonstrative=None,
    ):
        return self._add_records_default(
            person,
            group,
            identifier,
            rra=rra,
            pensioner=pensioner,
            layout=layout,
            demonstrative=demonstrative,
        )

    def _add_records_bpfdec_rtpa(
        self,
        person,
        group,
        identifier,
        rra=None,
        pensioner=None,
        layout="VALUES",
        demonstrative=None,
    ):
        choice = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label="BPFDEC-RTPA"
        )
        q_summary = person.dirf_summaries.filter(
            calendar_year=self.dialect.calendar_year, identifier=choice.value, rra=rra
        ).order_by("pensioner__cpf", "pensioner__data_nascimento")
        for ds in q_summary:
            if q_summary:
                dependent = Dependent.objects.filter(
                    servidor__pessoa_fisica=person, pessoa_fisica=ds.pensioner
                ).last()
                TIPO_DEPENDENTE_TABLE = {
                    1: 3,
                    2: 3,
                    3: 4,
                    4: 4,
                    5: 8,
                    6: 10,
                    7: 10,
                    8: 10,
                    9: 10,
                    10: 4,
                    11: 4,
                }
                config_infpa = {
                    "cpf_alimentando": ds.pensioner.cpf,
                    "data_nascimento": (
                        ds.pensioner.data_nascimento.strftime("%Y%m%d")
                        if ds.pensioner.data_nascimento
                        else ""
                    ),
                    "nome": tira_acentos(ds.pensioner.nome),
                    "relacao_dependencia": (
                        TIPO_DEPENDENTE_TABLE.get(dependent.tipo, 10)
                        if dependent
                        else 10
                    ),
                }
                group.add("INFPA", **config_infpa)
                self._add_records_default(
                    person,
                    group,
                    "BPFDEC-RTPA",
                    rra=rra,
                    pensioner=ds.pensioner,
                    demonstrative=demonstrative,
                )

        return [ds.pk for ds in q_summary]

    def _add_records_bpfrra_rtpa(
        self,
        person,
        group,
        identifier,
        rra=None,
        pensioner=None,
        layout="VALUES",
        demonstrative=None,
    ):
        return self._add_records_bpfdec_rtpa(
            person,
            group,
            identifier,
            rra=rra,
            pensioner=pensioner,
            layout=layout,
            demonstrative=demonstrative,
        )

    def _add_records_bpfdec_rio(
        self,
        person,
        group,
        identifier,
        rra=None,
        pensioner=None,
        layout="VALUES",
        demonstrative=None,
    ):
        # print 'IDENTIFIER: %s' % identifier
        choice = Choice.objects.get(
            app_label="dirf", name="IDENTIFIERS_DIRF", label=identifier
        ).value
        q_summary = person.dirf_summaries.filter(
            calendar_year=self.dialect.calendar_year,
            identifier=choice,
            rra=rra,
            pensioner=pensioner,
        )
        total_rio = 0
        description = ""
        rec = None
        if q_summary:
            for rio in q_summary:
                total_rio_inf = 0
                for x in range(1, 14):
                    total_rio_inf += getattr(rio, "value_%02d" % x)

                if total_rio_inf > 0:
                    total_rio += total_rio_inf
                    description += ("%s, " % tira_acentos(rio.info)) if rio.info else ""
                    info = "%s: RS %6.2f" % (tira_acentos(rio.info), total_rio_inf)
                    rec = self.inf_group.add(
                        person.pessoafisica.cpf,
                        INFORMATION_TAGS.get(identifier, None),
                        info,
                    )

            if description[-2:] == ", ":
                description = description[:-2]

            if total_rio > 0:
                values = {
                    "valor_pago_ano": total_rio,
                    "descricao_rendimentos": description,
                }
                group.add("RIO", **values)
                self._update_demonstrative(demonstrative, identifier, values)

        if rec:
            self._update_demonstrative(
                demonstrative, "INF", rec.get("informacoes_complementares")
            )

        return [ds.pk for ds in q_summary]

    def get_records(self):

        if self.regs:
            return self.regs

        q_sumaries_naturalperson = DirfSummary.objects.filter(
            calendar_year=self.dialect.calendar_year
        ).filter(person__pessoajuridica=None)

        if self.persons:
            q_sumaries_naturalperson = q_sumaries_naturalperson.filter(
                person__pk__in=self.persons
            )

        q_sumaries_legalperson = DirfSummary.objects.filter(
            calendar_year=self.dialect.calendar_year
        ).filter(person__pessoafisica=None)

        code = None

        declaration, created = Declaracao.objects.get_or_create(
            ano_base=self.dialect.calendar_year,
            defaults={"rectified_receipt": self.receipt_number},
        )
        if declaration.rectified_receipt != self.receipt_number:
            declaration.rectified_receipt = self.receipt_number
            declaration.save()

        for nr in NaturezaRendimento.objects.order_by("codigo"):

            q_sumaries_naturalperson_code = q_sumaries_naturalperson.filter(code=nr)
            q_sumaries_legalperson_code = q_sumaries_legalperson.filter(code=nr)
            if q_sumaries_naturalperson_code or q_sumaries_legalperson_code:

                #  BPFDEC Records -----------------------------------------------------------------------------------
                evaluated_summaries = []
                for obj in q_sumaries_naturalperson_code.order_by(
                    "person__pessoafisica__cpf"
                ):
                    if obj.pk not in evaluated_summaries:
                        layout = obj.choice.label.split("-")[0]

                        person = obj.person
                        # log.debug('GRDIRF %s' % person.pessoafisica.cpf,)
                        # log.debug('GRDIRF %-50s: %s' % (tira_acentos(person.nome), obj.rra))

                        demonstrative = None
                        if nr.codigo in ["0561", "1889", "3208", "0916", "0588"]:
                            demonstrative, created = (
                                declaration.demonstrativos.get_or_create(
                                    pessoa_fisica=person.pessoafisica,
                                    natureza=nr,
                                    rra=obj.rra,
                                    defaults={"responsavel": self.employee_manager},
                                )
                            )
                            demonstrative.clear()

                        group = (
                            self.decpj_group
                            if not obj.rra
                            else self.rra_groups[obj.rra]
                        )

                        # Adicionando o registro IDREC caso não exista ainda para o código atual
                        if (nr.codigo != code) or (obj.rra and len(group.records) == 0):
                            code = nr.codigo
                            group.add("IDREC", codigo_receira=code)

                        disease_date = (
                            person.pessoafisica.servidor_set.aggregate(
                                date=Max("molestia__data_laudo")
                            ).get("date")
                            or ""
                        )

                        bpfdec_rtpa_choice_id = Choice.objects.get(
                            app_label="dirf",
                            name="IDENTIFIERS_DIRF",
                            label="BPFDEC-RTPA",
                        ).value
                        person_has_bpfdec_rtpa = person.dirf_summaries.filter(
                            calendar_year=self.dialect.calendar_year,
                            identifier=bpfdec_rtpa_choice_id,
                        ).exists()
                        idicador_ident_alim = "S" if person_has_bpfdec_rtpa else "N"

                        group.add(
                            layout,
                            cpf=person.pessoafisica.cpf,
                            nome=tira_acentos(person.nome),
                            data_laudo_molestia=(
                                disease_date.strftime("%Y%m%d")
                                if disease_date and obj.rra
                                else ""
                            ),
                            natureza_rra=tira_acentos(obj.rra.title if obj.rra else ""),
                            indicador_identificacao_alimentando=idicador_ident_alim,
                            # data_laudo_molestia=disease_date.strftime('%Y%m%d') if disease_date else '',
                        )

                        records = q_sumaries_naturalperson_code.filter(
                            rra=obj.rra, person=person
                        ).order_by("person__pessoafisica__cpf")
                        for ds in records:
                            if ds.pk not in evaluated_summaries:
                                method_name = f"_add_records_{ds.choice.label.lower().replace('-', '_')}"
                                _add_record_method = getattr(
                                    self, method_name, self._add_records_default
                                )
                                evaluated_summaries += _add_record_method(
                                    person,
                                    group,
                                    ds.choice.label,
                                    rra=ds.rra,
                                    pensioner=ds.pensioner,
                                    demonstrative=demonstrative,
                                )

                        if demonstrative:
                            demonstrative.save()

                #  BPJDEC Records --------------------------------------------------------------------------------
                # log.debug('GRDIRF >> PJ Records')
                # evaluated_summaries = []
                # for obj in q_sumaries_legalperson_code.order_by('person__pessoajuridica__cnpj'):
                #     if obj.pk not in evaluated_summaries:
                #         layout = obj.choice.label.split('-')[0]

                #         group = self.decpj_group

                #         # Adicionando o registro IDREC caso não exista ainda para o código atual
                #         if nr.codigo != code:
                #             code = nr.codigo
                #             group.add('IDREC', codigo_receira=code)
                #             log.debug('GRDIRF >>>>>>>> PJ %s' % nr)

                #         person = obj.person
                #         # log.debug('GRDIRF %s' % person.pessoajuridica.cnpj,)
                #         # log.debug('GRDIRF %-50s' % tira_acentos(person.nome))
                #         self.decpj_group.add(
                #             layout,
                #             cnpj=person.pessoajuridica.cnpj,
                #             nome_empresarial=tira_acentos(person.nome),
                #         )

                #         for ds in q_sumaries_legalperson_code.filter(rra=None, person=person).order_by('identifier'):
                #             if ds not in evaluated_summaries:
                #                 _add_record_method = getattr(self, '_add_records_%s' % ds.choice.label.lower().replace(
                #                     '-', '_'), self._add_records_default)
                #                 evaluated_summaries += _add_record_method(person,
                #                                                           group,
                #                                                           ds.choice.label,
                #                                                           pensioner=ds.pensioner)

                #  RRA Records ---------------------------------------------------------------------------
                #  END BPFDEC Records ------------------------------------------------------------------------------

        self.main_group.records += self.decpj_group.get_records()
        for rra in self.rra_groups:
            rra_records = self.rra_groups[rra].get_records()
            if len(rra_records) > 1:
                self.main_group.records += rra_records

        ordering_info_temp = self.inf_group.get_records()
        ordering_info = sorted(ordering_info_temp, key=lambda x: x[2])
        self.main_group.records += ordering_info

        self.regs = self.main_group.get_records()

        return self.regs
        # ----------------------------------------------------------------------
