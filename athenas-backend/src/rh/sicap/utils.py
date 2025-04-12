# -*- coding: utf-8 -*-

import calendar
import codecs
import os
import zipfile
from datetime import date, datetime
from os import unlink

from django.conf import settings
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.helpers import roundf
from contrib.utils import DateUtils, getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, FeriasAfastamento, Licenca
from rh.const import CANCELADO
from rh.gfp.models import Evento, FolhaEvento, FolhaTipo
from rh.models import (
    CargaHoraria,
    CargoQuadro,
    Documento,
    Localidade,
    Lotacao,
    MovimentacaoAposentadoria,
    MovimentacaoAproveitamento,
    MovimentacaoDesligamento,
    MovimentacaoEstabilizacao,
    MovimentacaoPessoal,
    MovimentacaoPosse,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    MovimentacaoRequisicao,
    MovimentacaoReversao,
    Servidor,
)
from rh.pensao.models import Pensao, PensaoFolhaEvento
from standard.models import Choice

log = getLogger(__name__)


class SicapUtil(object):
    """
    Classe suporte para construção de arquivos.
    """

    @classmethod
    def _months_to_unicode(cls, months=[]):
        buf = ""
        for month in months:
            if not buf:
                buf = "%s" % month
            else:
                buf += "-%s" % month
        return buf

    @classmethod
    def _file_name(cls, months=[], year=None):
        return "mpto-sicapap"

    @classmethod
    def _cache_path(cls):
        cache_path = getattr(settings, "CACHE", {}).get("sicapap", None)
        if not cache_path:
            cache_path = getattr(settings, "CACHE_PATH", None)
            if cache_path:
                cache_path = "%s/sicapap" % cache_path
        return cache_path

    @classmethod
    def directory_tmp(cls):
        directory_tmp = SicapUtil._cache_path()
        if not os.path.exists(directory_tmp):
            os.mkdir(directory_tmp)
        return directory_tmp

    def __init__(self, **kwargs):
        self.year = int(kwargs.get("year", None))
        self.months = kwargs.get("months", None)
        if not self.year or not self.months:
            raise Exception("Preencha os parâmetros mês e ano!")
        self.file_name = kwargs.get("file_name", SicapUtil._file_name())
        self.date_start, self.date_end = self.date_start_and_end()
        self.day_start = self.date_start.day
        self.month_start = self.date_start.month
        self.day_end = self.date_end.day
        self.month_end = self.date_end.month
        self.unity_employee = {}  # cpf: count

    def date_start_and_end(self):
        sorted(self.months)
        if len(self.months) > 0:
            month_begin = self.months[0]
            month_end = self.months[len(self.months) - 1]
            day_end = calendar.monthrange(self.year, month_end)[1]
            date_range = NewDateRange(
                date(self.year, month_begin, 1), date(self.year, month_end, day_end)
            )
        return date_range.first, date_range.last

    @classmethod
    def write_file(cls, text, file_name, mode="w"):
        """
        Método responsável por escrever em file_write.
        """
        try:
            file_write = codecs.open(file_name, mode, "utf-8")
            file_write.write(text)
            file_write.close()
        except Exception as err:
            log.exception(err)
            raise err

    def sign_file(self):
        return {
            "cnpj": "01786078000146",
            "directory": self.directory_tmp(),
            "month": SicapUtil._months_to_unicode(self.months),
            "year": self.year,
        }


class SicapBuilder(object):

    def __init__(self, **kwargs):
        try:
            self.sicap_util = SicapUtil(**kwargs)
            self.feedback = kwargs.get(
                "feedback", (lambda progress_message, progress, **kwargs: False)
            )
            self.builder()
        except Exception as err:
            log.exception(err)
            print(err)
            raise err

    @classmethod
    def write_file(cls, text, file_name, mode="w"):
        """
        Método responsável por escrever em file_write.
        """
        try:
            file_write = codecs.open(file_name, mode, "utf-8")
            file_write.write(text)
            file_write.close()
        except Exception as err:
            log.exception(err)
            raise err

    def builder(self):
        """
        Método responsável por organizar a construção dos arquivos.
        """
        try:
            employee_file_name = (
                "%(directory)s/%(cnpj)s_servidor_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            moves_file_name = (
                "%(directory)s/%(cnpj)s_movimentacao_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            workplace_file_name = (
                "%(directory)s/%(cnpj)s_entidade_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            job_position_file_name = (
                "%(directory)s/%(cnpj)s_cargo_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            law_file_name = (
                "%(directory)s/%(cnpj)s_lei_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            chart_file_name = (
                "%(directory)s/%(cnpj)s_quadro_efetivo_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            chart_comission_file_name = (
                "%(directory)s/%(cnpj)s_quadro_comissionado_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            sheet_type_file_name = (
                "%(directory)s/%(cnpj)s_folha_tipo_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            sheet_item_file_name = (
                "%(directory)s/%(cnpj)s_folha_item_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )
            sheet = (
                "%(directory)s/%(cnpj)s_folha_pagamento_%(month)s_%(year)s.txt"
                % self.sicap_util.sign_file()
            )

            query_filter_law = Q(
                cargo__tipo_lei_cargo__in=[
                    "EF",
                ]
            )
            query_filter_law_comission = Q(cargo__tipo_lei_cargo__in=["CM", "FC"])

            SicapServidor(
                self.sicap_util, file_name=employee_file_name, feedback=self.feedback
            ).text()
            SicapMovimentacaoPessoal(
                self.sicap_util, file_name=moves_file_name, feedback=self.feedback
            ).text()
            SicapEntidade(
                self.sicap_util, file_name=workplace_file_name, feedback=self.feedback
            ).text()
            SicapCargo(
                self.sicap_util,
                file_name=job_position_file_name,
                feedback=self.feedback,
            ).text()
            SicapLei(
                self.sicap_util,
                file_name=law_file_name,
                query_filter=(query_filter_law | query_filter_law_comission),
                feedback=self.feedback,
            ).text()
            SicapQuadro(
                self.sicap_util,
                file_name=chart_file_name,
                query_filter=query_filter_law,
                feedback=self.feedback,
            ).text()
            SicapQuadro(
                self.sicap_util,
                file_name=chart_comission_file_name,
                query_filter=query_filter_law_comission,
                feedback=self.feedback,
            ).text()
            SicapFolhaTipo(
                self.sicap_util, file_name=sheet_type_file_name, feedback=self.feedback
            ).text()
            SicapFolhaItem(
                self.sicap_util, file_name=sheet_item_file_name, feedback=self.feedback
            ).text()
            SicapFolha(self.sicap_util, file_name=sheet, feedback=self.feedback).text()
            SicapPension(
                self.sicap_util,
                file_name=moves_file_name,
                mode_write="a",
                feedback=self.feedback,
            ).text()

            self.feedback(
                "%(message_progress)s", 1, message_progress="Gerando Arquivo ZIP."
            )

            self.zip(
                entidade=workplace_file_name,
                cargo=job_position_file_name,
                lei=law_file_name,
                quadro_efetivo=chart_file_name,
                quadro_comissionado=chart_comission_file_name,
                movimentacao=moves_file_name,
                folha_tipo=sheet_type_file_name,
                folha_item=sheet_item_file_name,
                folha=sheet,
                servidor=employee_file_name,
            )

            self.feedback(
                "%(message_progress)s",
                100,
                message_progress="Geração de arquivos finalizada.",
            )
        except Exception as err:
            print(err)
            log.exception(err)
            raise err

    def zip(self, **files):
        """
        Método responsável por compactar os arquivos informados.
        """
        zip_file = zipfile.ZipFile(
            "%s/%s"
            % (
                self.sicap_util.directory_tmp(),
                "%s-%s-%s.zip"
                % (
                    self.sicap_util.file_name,
                    SicapUtil._months_to_unicode(self.sicap_util.months),
                    self.sicap_util.year,
                ),
            ),
            "w",
        )
        for key in list(files.keys()):
            try:
                zip_file.write(
                    files.get(key),
                    arcname="%s%s"
                    % ("01786078000146", files.get(key).split("01786078000146")[1]),
                )
                unlink(files.get(key))
            except Exception as err:
                log.exception(err)
                raise err
        zip_file.close()


class Sicap(object):

    verbose_name = "Gerando arquivos..."

    def __init__(self, sicap_util, **kwargs):
        self.sicap_util = sicap_util
        self.feedback = kwargs.get(
            "feedback", (lambda progress_message, progress, **kwargs: False)
        )
        self._file_name = kwargs.get("file_name", "w")
        self._mode_write = kwargs.get("mode_write", "w")

    def write_feedback(self, progress=1, message_progress=None):
        message_progress = (
            self.verbose_name if not message_progress else message_progress
        )
        self.feedback(
            "%(message_progress)s", progress, message_progress=message_progress
        )

    def write_file(self, text):
        self.sicap_util.write_file(text, self._file_name, mode=self._mode_write)

    def get_type_move(self):
        # table_05_type_move = {
        #     1: 'Nomeação/Efetivo',
        #     2: 'Contratado',
        #     3: 'Reversão',
        #     4: 'Reintegração',
        #     5: 'Readaptação',
        #     6: 'Revisão de reserva',
        #     7: 'Aproveitamento',
        #     8: 'Aposentadoria',
        #     9: 'Pensão',
        #     10: 'Nomeação/Comissionado',
        #     11: 'À disposição (Servidor Requisitado)',
        #     12: 'Cedido para outra entidade',
        #     13: 'Recondução',
        #     14: 'Estabilizado',
        #     15: 'Reserva',
        #     16: 'Desligamento',
        #     17: 'Revisão de aposentadoria',
        #     18: 'Prorrogação de contrato',
        #     19: 'Revisão de pensão',
        #     20: 'Licença',
        #     21: 'Reforma',
        #     22: 'Revisão deReforma',
        # }
        type_move = " tipo movimentação obrigatório "
        if self.is_possession_base():
            type_move = 1
            if self.instance.quadro.cargo.tipo_lei_cargo in ["CM", "FC"]:
                type_move = 10
        elif self.is_renewal():
            type_move = 13
        elif self.is_reversion():
            type_move = 3
        elif self.is_reinstatement():
            type_move = 4
        elif self.is_rehabilitation():
            type_move = 5
        elif self.is_utilization():
            type_move = 7
        elif self.is_retirement():
            type_move = 8
        elif self.is_dismissal():
            type_move = 16
        elif self.is_other_organ_removal():
            type_move = 12
        elif self.is_license() or self.is_holiday():
            type_move = 20
        elif self.is_request():
            type_move = 11
        elif self.is_stabilization():
            type_move = 14
        elif self.is_pension():
            type_move = 9
        return str(type_move)

    def is_possession(self):
        return isinstance(self.instance, MovimentacaoPosse)

    def is_possession_base(self):
        return self.is_possession() and self.instance.base_posse()

    def is_renewal(self):
        return isinstance(self.instance, MovimentacaoReconducao)

    def is_reversion(self):
        return isinstance(self.instance, MovimentacaoReversao)

    def is_reinstatement(self):
        return isinstance(self.instance, MovimentacaoReintegracao)

    def is_rehabilitation(self):
        return isinstance(self.instance, MovimentacaoReadaptacao)

    def is_utilization(self):
        return isinstance(self.instance, MovimentacaoAproveitamento)

    def is_retirement(self):
        return isinstance(self.instance, MovimentacaoAposentadoria)

    def is_dismissal(self):
        return isinstance(self.instance, MovimentacaoDesligamento)

    def is_other_organ_removal(self):
        return isinstance(self.instance, AfastamentoOutroOrgao)

    def is_license(self):
        return isinstance(self.instance, Licenca)

    def is_request(self):
        return isinstance(self.instance, MovimentacaoRequisicao)

    def is_stabilization(self):
        return isinstance(self.instance, MovimentacaoEstabilizacao)

    def is_holiday(self):
        return isinstance(self.instance, FeriasAfastamento)

    def is_pension(self):
        return isinstance(self.instance, Pensao)

    @classmethod
    def isdigit(cls, number):
        if number and not number.isdigit():
            number += " possui caractere inválido, deve ser composto apenas por dígito "
        return number

    @classmethod
    def format_number_law(cls, number, max_length=6):
        if number:
            number = cls.format_max_lenght(number=number, max_length=max_length)
        else:
            number = " número não encontrado "
        number = cls.isdigit(number)
        return number

    @classmethod
    def format_max_lenght(cls, number=None, max_length=10, fill="0"):
        if number:
            while len(number) < max_length + 1:
                number = "%s%s" % (fill, number)
            while len(number) > max_length:
                number = (
                    number[len(number) - max_length : len(number)]
                    if len(number) > max_length
                    else number
                )
        return number

    @classmethod
    def get_document_data(cls, document):
        number_document = " número da portaria é obrigatório "
        date_document = " data portaria é obrigatório "
        if document:
            number_document = "%s%s" % (
                Sicap.format_number_law(document.numero),
                document.ano,
            )
            if document.data_expedicao:
                date_document = DateUtils.date_to_str(document.data_expedicao)
        return number_document, date_document

    @classmethod
    def get_publication_data(cls, publication):
        year_publication = " sem ano de publicação "
        date_publication = " sem data de publicação "
        local_publication = " sem veículo de publicação "
        number_publication = " sem número de publicação "
        if publication:
            if publication.data_publicacao:
                date_publication = DateUtils.date_to_str(publication.data_publicacao)
                year_publication = publication.data_publicacao.year
            if publication.veiculo_publicacao:
                local_publication = publication.get_veiculo_publicacao_display()
            if publication.numero_publicacao:
                number_publication = publication.numero_publicacao
        text = date_publication, "%s %s%s" % (
            local_publication,
            number_publication,
            year_publication,
        )
        return text[:50]

    @classmethod
    def get_type_document(cls, publication):
        type_document = publication.tipo if publication and publication.tipo else None
        document_to_sicap = {
            1: 10,  # 'ATO',
            2: 2,  # 'DECRETO',
            3: 4,  # 'PORTARIA',
            5: 7,  # 'DESPACHO',
            11: 1,  # 'LEI',#1:'LEI',
            14: 3,  # 'DECRETO LEGISLATIVO',#3:'DECRETO LEGISLATIVO',
            15: 5,  # 'RESOLUÇÃO',#5:'RESOLUÇÃO',
            16: 6,  # 'CIRCULAR',#6:'CIRCULAR',
            17: 8,  # 'PROCESSO',#8:'PROCESSO',
            99: 99,  # 'OUTROS',
        }
        if not type_document:
            type_document = " não existe publicação "
        else:
            type_document = document_to_sicap.get(type_document, 99)
        return type_document

    @classmethod
    def get_number_admission(cls, possession):
        number_admission = None
        if possession and possession.publicacao_movimentacao:
            if possession.publicacao_movimentacao.numero:
                number_admission = "%s" % Sicap.format_number_law(
                    possession.publicacao_movimentacao.numero
                )
            if number_admission and possession.publicacao_movimentacao.ano:
                number_admission = "%s%s" % (
                    number_admission,
                    possession.publicacao_movimentacao.ano,
                )
        if not number_admission:
            number_admission = (
                " número de ato de admissão é obrigatório %s " % possession
            )
        return number_admission

    @classmethod
    def get_organ_cpnj(cls, administrative_unit):
        cnpj = None
        if (
            administrative_unit
            and administrative_unit.pessoa_juridica
            and administrative_unit.pessoa_juridica.cnpj
            and administrative_unit.pessoa_juridica.cnpj != "00000000000000"
        ):
            cnpj = administrative_unit.pessoa_juridica.cnpj
        return cnpj


class SicapServidor(Sicap):

    verbose_name = "Gerando Arquivo Servidor"

    def __init__(self, sicap_util, **kwargs):
        super(SicapServidor, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        query_filter = (
            Q(tipo__in=("S", "M"))
            & Q(created_at__lte=self.sicap_util.date_end)
            & Q(created_at__gte=self.sicap_util.date_start)
            & Q(modified_at__gte=self.sicap_util.date_start)
        )

        for employee in Servidor.objects.filter(query_filter).order_by(
            "pessoa_fisica__nome"
        ):
            try:
                country, locality, state = self.get_data_nationality(employee)
                (
                    pis,
                    cnh,
                    ctps,
                    ctps_series,
                    title_number,
                    title_zone,
                    title_state,
                    title_section,
                ) = self.person_documents_data(employee)
                rg, date_rg, organ_expedition = self.get_rg_data(employee)

                text += (
                    "|".join(
                        [
                            "%s" % self.get_registry(employee),
                            "%s" % self.get_name(employee),
                            "%s" % self.get_date_born(employee),
                            "%s" % self.get_gender(employee),
                            "%s" % self.get_civil_state(employee),
                            "%s" % country,
                            "%s" % locality,
                            "%s" % state,
                            "%s" % self.get_level_education(employee),
                            "%s" % self.get_cpf_employee(employee),
                            "%s" % pis,
                            "%s" % cnh,
                            "%s" % rg,
                            "%s" % date_rg,
                            "%s" % organ_expedition,
                            "%s" % ctps,
                            "%s" % ctps_series,
                            "%s" % title_number,
                            "%s" % title_zone,
                            "%s" % title_section,
                            "%s" % title_state,
                        ]
                    )
                    + "\n"
                )
            except Exception as err:
                text += " erro gerando servidor "
                log.exception(err)
        self.write_file(text)

    @classmethod
    def get_latest_possession(cls, employee, filter_possession=None):
        """
        This method returns the latest possession active or inactive.
        """
        possession = None
        if employee.posses_ativas.exists():
            possession = employee.posses_ativas
        elif employee.posses.exists():
            possession = employee.posses

        if filter_possession and possession:
            possession = possession.filter(filter_possession)

        return possession.latest("data_exercicio") if possession else possession

    @classmethod
    def get_registry(cls, employee):
        registry = " matrícula é obrigatório "
        try:
            registry = employee.matricula
        except Exception:
            pass
        return registry

    @classmethod
    def get_name(cls, employee):
        nome = " nome obrigatório "
        try:
            nome = employee.pessoa_fisica.nome
        except Exception:
            pass
        return nome

    @classmethod
    def get_date_born(cls, employee):
        date_born = " data nascimento obrigatório "
        if employee.pessoa_fisica.data_nascimento:
            date_born = DateUtils.date_to_str(employee.pessoa_fisica.data_nascimento)
        return date_born

    @classmethod
    def get_gender(cls, employee):
        return 1 if employee.pessoa_fisica.sexo == "M" else 2

    @classmethod
    def get_level_education(cls, employee):
        parser_table_sicap_02 = {
            1: 4,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 2,
            7: 2,
            8: 3,
            9: 3,
            10: 3,
            11: 3,
            12: 3,
            13: 2,
        }
        return parser_table_sicap_02.get(
            employee.pessoa_fisica.grau_instrucao, " escolaridade obrigatório "
        )

    @classmethod
    def get_civil_state(cls, employee):
        parser_table_sicap_04 = {
            1: 1,
            2: 2,
            3: 4,
            4: 3,
            5: 3,
            6: 3,
            7: 1,
        }
        return parser_table_sicap_04.get(
            employee.pessoa_fisica.estado_civil, " estado civil obrigatório "
        )

    @classmethod
    def get_data_nationality(cls, employee):
        country = " pais obrigatório "
        locality = " localidade obrigatório "
        state = " uf obrigatório "
        if employee.pessoa_fisica.municipio_naturalidade:
            if employee.pessoa_fisica.municipio_naturalidade.estado:
                if (
                    employee.pessoa_fisica.municipio_naturalidade.estado.pais
                    and employee.pessoa_fisica.municipio_naturalidade.estado.pais.nome
                ):
                    country = (
                        employee.pessoa_fisica.municipio_naturalidade.estado.pais.nome
                    )
                if employee.pessoa_fisica.municipio_naturalidade.estado.sigla:
                    state = employee.pessoa_fisica.municipio_naturalidade.estado.sigla
            if employee.pessoa_fisica.municipio_naturalidade.nome:
                locality = employee.pessoa_fisica.municipio_naturalidade.nome
        return country, locality, state

    @classmethod
    def person_documents_data(cls, employee):
        pis = ""
        cnh = ""
        ctps = ""
        ctps_series = ""
        title_number = " numero título obrigatório "
        title_zone = " titulo zona obrigatório "
        title_state = " titulo uf obrigatório "
        title_section = " titulo seção obrigatório "
        for document in Documento.objects.filter(
            naturalpersons=employee.pessoa_fisica.pk
        ):
            if document.tipo_documento == 4:
                pis = document.numero
            if document.tipo_documento == 2:
                cnh = document.numero
            if document.tipo_documento == 3:
                ctps = document.numero
                for doc_specific in document.dados_especificos.all():
                    if doc_specific.especificidade == 6 and doc_specific.valor:
                        ctps_series = doc_specific.valor
            elif document.tipo_documento == 1 and document.numero:
                title_number = document.numero
                title_state = ""
                for doc_specific in document.dados_especificos.all():
                    if doc_specific.especificidade == 1 and doc_specific.valor:
                        title_zone = doc_specific.valor
                    if doc_specific.especificidade == 2 and doc_specific.valor:
                        title_section = doc_specific.valor
                    if doc_specific.especificidade == 3 and doc_specific.valor:
                        title_state = doc_specific.valor
                    if doc_specific.especificidade == 7 and (
                        title_state is None or title_state == ""
                    ):
                        locality = Localidade.objects.filter(pk=int(doc_specific.valor))
                        title_state = (
                            locality.latest("pk").estado.sigla
                            if locality.exists()
                            else title_state
                        )

        cnh = cls.cnh_format(cnh)
        return (
            pis,
            cnh,
            ctps,
            ctps_series,
            title_number,
            title_zone,
            title_state,
            title_section,
        )

    @classmethod
    def cnh_format(cls, cnh):
        if cnh:
            # cnh = cls.format_max_lenght(number=cnh, max_length=Documento.cnh_max_len)
            cnh = cls.format_max_lenght(number=cnh, max_length=10)
            cnh = cls.isdigit(cnh)
        return cnh

    @classmethod
    def get_rg_data(cls, employee):
        rg = " rg obrigatório "
        date = " data rg obrigatório "
        organ_expedition = " orgao expedição rg obrigatório "
        if employee.pessoa_fisica.rg:
            rg = employee.pessoa_fisica.rg
        if employee.pessoa_fisica.rg_data_expedicao:
            date = DateUtils.date_to_str(employee.pessoa_fisica.rg_data_expedicao)
        if employee.pessoa_fisica.rg_orgao:
            organ_expedition = employee.pessoa_fisica.rg_orgao
        elif employee.pessoa_fisica.rg_uf and employee.pessoa_fisica.rg_uf.sigla:
            organ_expedition = employee.pessoa_fisica.rg_uf.sigla
        return rg, date, organ_expedition

    @classmethod
    def get_cpf_employee(cls, employee):
        cpf = " cpf obrigatório "
        if employee.pessoa_fisica.cpf:
            cpf = cls.format_max_lenght(
                number=employee.pessoa_fisica.cpf, max_length=11
            )
        return cpf

    @classmethod
    def type_link_payment(cls, employee, pensioner=None, date=None):
        date = datetime.now() if not date else date
        # type_13_link_payment = {
        #     1: 'Efetivo',
        #     2: 'Comissionado',
        #     3: 'Contratado',
        #     4: 'Disposição',
        #     5: 'Cedido',
        #     6: 'Aposentado',
        #     7: 'Pensionista',
        #     8: 'Requisitado',
        #     9: 'Eletivo',
        #     10: 'Estagiário',
        # }
        link = 1
        if not pensioner:
            possessions = employee.get_posses_ativas(data_inicio=date)

            if not possessions.exists():
                possessions = employee.posses

            if (
                possessions.filter(quadro__cargo__tipo_lei_cargo="EF").exists()
                and employee.moved_away()
            ):
                link = 5
            elif (
                possessions.filter(quadro__cargo__tipo_lei_cargo="EF").exists()
                and possessions.filter(quadro__cargo__tipo_lei_cargo="EL").exists()
            ):
                link = 9
            elif (
                possessions.filter(
                    quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
                ).exists()
                and not possessions.filter(quadro__cargo__tipo_lei_cargo="EF").exists()
            ):
                link = 2
                if possessions.filter(quadro__cargo__tipo_lei_cargo="AC").exists():
                    link = 8
            elif possessions.filter(quadro__cargo__tipo_lei_cargo="AC").exists():
                link = 8
            elif possessions.filter(quadro__cargo__tipo_lei_cargo="ES").exists():
                link = 10
        elif employee.settlor_pension_deth(date=date):
            link = 7
        return link

    @classmethod
    def get_type_link(cls, employee, date=None):
        type_link = " efetivo obrigatório "
        # table_11_type_link = {
        #     1: 'Efetivo',
        #     2: 'Contratado',
        #     3: 'Comissionado',
        # }
        if (
            employee.get_posses_ativas(data_inicio=date)
            .filter(quadro__cargo__tipo_lei_cargo="EF")
            .exists()
        ):
            type_link = 1
        elif (
            employee.get_posses_ativas(data_inicio=date)
            .filter(quadro__cargo__tipo_lei_cargo__in=("CM", "FC"))
            .exists()
        ):
            type_link = 0
        elif employee.posses.filter(quadro__cargo__tipo_lei_cargo="EF").exists():
            type_link = 1
        elif employee.posses.filter(
            quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
        ).exists():
            type_link = 0
        return str(type_link)

    @classmethod
    def get_number_tce(cls, possession):
        number_tce = " numero do concurso no tce obrigatorio"
        possession = possession.first_possession
        if possession.public_concurrence and possession.public_concurrence.number_tce:
            number_tce = possession.public_concurrence.number_tce
        return number_tce

    @classmethod
    def get_workplace_raw(cls, employee):
        workplace = None
        if employee.workplace_only.exists():
            workplace = employee.workplace_only.latest("data_vigencia_inicio")
        elif employee.work_assignment.exists():
            workplace = employee.work_assignment.latest("data_vigencia_inicio")
        elif employee._raw_locations(option=1).exists():
            workplace = employee._raw_locations(option=1).latest("data_vigencia_inicio")
        return workplace

    @classmethod
    def get_workplace(cls, employee):
        workplace = SicapServidor.get_workplace_raw(employee)
        if workplace:
            workplace = workplace.lotacao.sigla
        else:
            workplace = "%s não possui lotação(ou a sigla). Obrigatório." % employee
        return workplace


class SicapMovimentacaoPessoal(Sicap):

    verbose_name = "Gerando Arquivo Movimentações"

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoPessoal, self).__init__(sicap_util, **kwargs)
        self.instance = kwargs.get("instance")
        self.employee = kwargs.get("employee", None)
        if not self.employee and self.instance:
            self.employee = self.instance.servidor

    @classmethod
    def filter_move(cls, date_start, date_end, cpfs=[]):
        filter_possession = Q(
            Q(movimentacaoposse__data_exercicio__gte=date_start)
            & Q(movimentacaoposse__data_exercicio__lte=date_end)
            & ~Q(movimentacaoposse__quadro__cargo__tipo_lei_cargo="AC")
        )
        filter_dismissal = (
            Q(movimentacaodesligamento__data_desligamento__gte=date_start)
            & Q(movimentacaodesligamento__data_desligamento__lte=date_end)
            & ~Q(
                movimentacaodesligamento__movimentacao_posse__quadro__cargo__tipo_lei_cargo="AC"
            )
        )

        filter_extension = Q(
            baselicencaafastamento__afastamento__afastamentooutroorgao__prorrogacao__data_inicio__gte=date_start
        ) & Q(
            baselicencaafastamento__afastamento__afastamentooutroorgao__prorrogacao__data_inicio__lte=date_end
        )

        filter_moved_away_local = (
            (
                Q(
                    baselicencaafastamento__afastamento__afastamentooutroorgao__data_inicio__gte=date_start
                )
                & Q(
                    baselicencaafastamento__afastamento__afastamentooutroorgao__data_inicio__lte=date_end
                )
            )
            | filter_extension
        ) & ~Q(
            baselicencaafastamento__afastamento__afastamentooutroorgao__estado=CANCELADO
        )

        filter_extension = Q(
            baselicencaafastamento__licenca__prorrogacao__data_inicio__gte=date_start
        ) & Q(baselicencaafastamento__licenca__prorrogacao__data_inicio__lte=date_end)

        filter_license = (
            (
                Q(baselicencaafastamento__licenca__data_inicio__gte=date_start)
                & Q(baselicencaafastamento__licenca__data_inicio__lte=date_end)
            )
            | filter_extension
        ) & ~Q(baselicencaafastamento__licenca__estado=CANCELADO)

        filter_holiday = (
            Q(baselicencaafastamento__feriasafastamento__data_inicio__gte=date_start)
            & Q(baselicencaafastamento__feriasafastamento__data_inicio__lte=date_end)
        ) & ~Q(baselicencaafastamento__feriasafastamento__estado=CANCELADO)

        filter_period = Q(
            movimentacaorequisicao__periodo__data_inicio__gte=date_start
        ) & Q(movimentacaorequisicao__periodo__data_inicio__lte=date_end)

        filter_request = (
            Q(movimentacaorequisicao__data_inicio__gte=date_start)
            & Q(movimentacaorequisicao__data_inicio__lte=date_end)
        ) | filter_period

        filter_stabilization = Q(
            movimentacaoestabilizacao__data_vigencia__gte=date_start
        ) & Q(movimentacaoestabilizacao__data_vigencia__lte=date_end)

        filter_move = Q(servidor__tipo__in=("S", "M")) & (
            # filter_possession
            # filter_dismissal
            # filter_moved_away_local
            # filter_license
            # filter_holiday
            # filter_request
            # filter_stabilization
            filter_possession
            | filter_dismissal
            | filter_moved_away_local
            | filter_license
            | filter_holiday
            | filter_request
            | filter_stabilization
        )
        return filter_move

    def generate_header(self, publication):
        text = ""
        try:
            cpf = SicapServidor.get_cpf_employee(self.employee)
            type_move = self.get_type_move()
            type_document = Sicap.get_type_document(publication)
            number_document, date_document = Sicap.get_document_data(publication)
            date_publication, doe = Sicap.get_publication_data(publication)
            notice = ""

            if type_document == " não existe publicação ":
                type_document = "%s %s" % (type_document, self.instance)

            if number_document == " número da portaria é obrigatório ":
                number_document = "%s %s" % (number_document, self.instance)

            if date_document == " data portaria é obrigatório ":
                date_document = "%s %s" % (date_document, self.instance)

            text += "|".join(
                [
                    "%s" % cpf,
                    "%s" % type_document,
                    "%s" % number_document,
                    "%s" % date_document,
                    "%s" % type_move,
                    "%s" % self.sicap_util.unity_employee.get(cpf, 1),
                    "%s" % doe,
                    "%s" % date_publication,
                    "%s" % notice,
                ]
            )

            self.sicap_util.unity_employee.update(
                {cpf: self.sicap_util.unity_employee.get(cpf, 1) + 1}
            )
        except Exception as err:
            log.exception(err)
            text = " Err generate_header %s" % err
        return text

    def text(self):
        text = ""
        moves = MovimentacaoPessoal.objects.filter(
            self.filter_move(self.sicap_util.date_start, self.sicap_util.date_end)
        ).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )
        count = 1
        total = moves.count()
        self.write_feedback()
        kwargs = {"feedback": self.feedback}
        for instance in moves:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            print("count: %s - total: %s" % (count, total))
            # found = False
            text_cache = ""
            if hasattr(instance, "movimentacaoposse"):
                if instance.movimentacaoposse.base_posse():
                    valid = True
                    if (
                        instance.servidor.member_type_by_possession
                        and instance.servidor.posses.count() > 1
                        and instance.movimentacaoposse.quadro.cargo.tipo_lei_cargo
                        != "CM"
                    ):
                        valid = False
                    if valid:
                        kwargs.update({"instance": instance.movimentacaoposse})
                        text_cache = SicapMovimentacaoPosse(
                            self.sicap_util, **kwargs
                        ).text()
                elif hasattr(instance.movimentacaoposse, "movimentacaoreconducao"):
                    kwargs.update(
                        {"instance": instance.movimentacaoposse.movimentacaoreconducao}
                    )
                    text_cache = SicapMovimentacaoReconducao(
                        self.sicap_util, **kwargs
                    ).text()
                elif hasattr(instance.movimentacaoposse, "movimentacaoreversao"):
                    kwargs.update(
                        {"instance": instance.movimentacaoposse.movimentacaoreversao}
                    )
                    text_cache = SicapMovimentacaoReversao(
                        self.sicap_util, **kwargs
                    ).text()
                elif hasattr(instance.movimentacaoposse, "movimentacaoreintegracao"):
                    kwargs.update(
                        {
                            "instance": instance.movimentacaoposse.movimentacaoreintegracao
                        }
                    )
                    text_cache = SicapMovimentacaoReintegracao(
                        self.sicap_util, **kwargs
                    ).text()
                elif hasattr(instance.movimentacaoposse, "movimentacaoreadaptacao"):
                    kwargs.update(
                        {"instance": instance.movimentacaoposse.movimentacaoreadaptacao}
                    )
                    text_cache = SicapMovimentacaoReadaptacao(
                        self.sicap_util, **kwargs
                    ).text()
                elif hasattr(instance.movimentacaoposse, "movimentacaoaproveitamento"):
                    kwargs.update(
                        {
                            "instance": instance.movimentacaoposse.movimentacaoaproveitamento
                        }
                    )
                    text_cache = SicapMovimentacaoAproveitamento(
                        self.sicap_util, **kwargs
                    ).text()
            elif hasattr(instance, "movimentacaodesligamento"):
                if hasattr(
                    instance.movimentacaodesligamento, "movimentacaoaposentadoria"
                ):
                    kwargs.update(
                        {
                            "instance": instance.movimentacaodesligamento.movimentacaoaposentadoria
                        }
                    )
                    text_cache = SicapMovimentacaoAposentadoria(
                        self.sicap_util, **kwargs
                    ).text()
                else:
                    valid = True
                    if (
                        instance.servidor.member_type_by_possession
                        and instance.servidor.is_ativo()
                        and instance.movimentacaodesligamento.movimentacao_posse.quadro.cargo.tipo_lei_cargo
                        != "CM"
                    ):
                        valid = False
                    if valid:
                        kwargs.update({"instance": instance.movimentacaodesligamento})
                        text_cache = SicapMovimentacaoDesligamento(
                            self.sicap_util, **kwargs
                        ).text()
            elif hasattr(instance, "baselicencaafastamento"):
                if (
                    hasattr(instance.baselicencaafastamento, "licenca")
                    and not hasattr(
                        instance.baselicencaafastamento.licenca,
                        "licencaafastamentoconjuge",
                    )
                    and not hasattr(
                        instance.baselicencaafastamento.licenca, "licencaservicomilitar"
                    )
                    and not hasattr(
                        instance.baselicencaafastamento.licenca, "licencacapacitacao"
                    )
                    and not hasattr(
                        instance.baselicencaafastamento.licenca,
                        "licencamandatoclassista",
                    )
                    and not hasattr(
                        instance.baselicencaafastamento.licenca,
                        "licencaatividadepolitica",
                    )
                    and not hasattr(
                        instance.baselicencaafastamento.licenca,
                        "licencainteresseparticular",
                    )
                ):
                    kwargs.update({"instance": instance.baselicencaafastamento.licenca})
                    text_cache = SicapLicense(self.sicap_util, **kwargs).text()
                # elif hasattr(instance.baselicencaafastamento, 'feriasafastamento'):
                # kwargs.update({'instance': instance.baselicencaafastamento.feriasafastamento})
                # text_cache = SicapFeriasAfastamento(self.sicap_util, **kwargs).text()
                elif hasattr(
                    instance.baselicencaafastamento, "afastamento"
                ) and hasattr(
                    instance.baselicencaafastamento.afastamento, "afastamentooutroorgao"
                ):
                    kwargs.update(
                        {
                            "instance": instance.baselicencaafastamento.afastamento.afastamentooutroorgao
                        }
                    )
                    text_cache = SicapAfastamentoOutroOrgao(
                        self.sicap_util, **kwargs
                    ).text()
                # elif (
                #     hasattr(instance.baselicencaafastamento, 'licenca') and
                #     (
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencaafastamentoconjuge') or
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencaservicomilitar') or
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencacapacitacao') or
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencamandatoclassista') or
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencaatividadepolitica') or
                #         hasattr(instance.baselicencaafastamento.licenca, 'licencainteresseparticular')
                #     )
                # ):
                #     print instance.baselicencaafastamento.instancia_modelo
            elif hasattr(instance, "movimentacaorequisicao"):
                kwargs.update({"instance": instance.movimentacaorequisicao})
                text_cache = SicapMovimentacaoRequisicao(
                    self.sicap_util, **kwargs
                ).text()
            elif hasattr(instance, "movimentacaoestabilizacao"):
                kwargs.update({"instance": instance.movimentacaoestabilizacao})
                text_cache = SicapMovimentacaoEstabilizacao(
                    self.sicap_util, **kwargs
                ).text()
            text += text_cache
            count += 1
        # LicencaAtividadePolitica
        # LicencaInteresseParticular
        # LicencaAfastamentoConjuge
        # LicencaServicoMilitar
        # LicencaCapacitacao
        # LicencaMandatoClassista
        self.write_feedback(progress=100)
        self.write_file(text)

    def get_date_start(self, date=None):
        if date:
            date = DateUtils.date_to_str(date)
        else:
            date = " data inicio obrigatório "
        return date

    def get_date_end(self, date=None):
        if date:
            date = DateUtils.date_to_str(date)
        else:
            date = " data fim obrigatório "
        return date


class SicapMovimentacaoPosse(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoPosse, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            type_move = self.get_type_move()
            type_link = SicapServidor.get_type_link(self.employee)
            number_year_law_job_position = self.get_number_year_law_job_position()
            workplace = SicapServidor.get_workplace(self.employee)
            code_job_position = SicapQuadro.get_code_job_position(self.instance.quadro)
            date_possession = self.get_date_possession()
            date_exercise = self.get_date_exercise()

            args = [
                self.generate_header(self.instance.publicacao_movimentacao),
                workplace,
                number_year_law_job_position,
                code_job_position,
                date_possession,
                date_exercise,
            ]
            if type_move == "1":
                args.append(SicapServidor.get_number_tce(self.instance))
            elif type_move == "10":
                args.append(type_link)
                args.append("0")
            text += "|".join(args) + "\n"
        except Exception as err:
            text = " erro gerando posse "
            log.exception(err)
        return text

    def get_number_year_law_job_position(self):
        number_year_law_job_position = " número e ano do cargo obrigatório "
        number, year, date_created, local = CargoQuadro.get_data_publication_creation(
            self.instance.quadro.cargo
        )
        if number and year:
            number_year_law_job_position = "%s%s" % (
                Sicap.format_number_law(number),
                year,
            )
        return number_year_law_job_position

    def get_date_possession(self):
        date_possession = " data de posse é obrigatório "
        if self.instance.data_posse:
            date_possession = DateUtils.date_to_str(self.instance.data_posse)
        return date_possession

    def get_date_exercise(self):
        date_exercise = " data exercicio é obrigatório "
        if self.instance.data_exercicio:
            date_exercise = DateUtils.date_to_str(self.instance.data_exercicio)
        return date_exercise


class SicapMovimentacaoDesligamento(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoDesligamento, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        "%s"
                        % self.generate_header(self.instance.publicacao_movimentacao),
                        "%s"
                        % self.get_number_admission(self.instance.movimentacao_posse),
                        "%s" % self.get_type_dismissal(),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            log.exception(err)
            text += " erro gerando desligamento %s" % self.instance.servidor
        return text

    def get_type_dismissal(self):
        # table_09_type_dismissal = {
        #     1: 'Exoneração-efetivo',
        #     2: 'Exoneração-comissionado',
        #     3: 'Exoneração-estabilizado',
        #     4: 'Exoneração-estabilizado não estável',
        #     5: 'Aposentadoria',
        #     6: 'Posse em outro cargo',
        #     7: 'Falecimento',
        #     8: 'Rescisão de contrato',
        #     9: 'Demissão',
        #     10: 'Reserva-reforma',
        #     11: 'Disponibilidade',
        # }
        # TIPO_DESLIGAMENTO = {
        #     1: 'EXONERAÇÃO EFETIVO',
        #     2: 'EXONERAÇÃO COMISSIONADO',
        #     3: 'EXONERAÇÃO ESTABILIZADO',
        #     4: 'APOSENTADORIA POR INVALIDEZ',
        #     5: 'APOSENTADORIA VOLUNTÁRIA',
        #     14: 'APOSENTADORIA COMPULSÓRIA',
        #     15: 'APOSENTADORIA ESPECIAL',
        #     16: 'APOSENTADORIA POR TEMPO DE CONTRIBUIÇÃO',
        #     17: 'APOSENTADORIA POR IDADE',
        #     6: 'POSSE EM OUTRO CARGO',
        #     7: 'FALECIMENTO',
        #     8: 'RESCISÃO',
        #     9: 'DEMISSÃO',
        #     10: 'RESERVA REFORMA',
        #     11: 'DISPONIBILIDADE',
        #     12: 'PROMOÇÃO/REMOÇÃO',
        #     13: 'FIM REQUISIÇÃO/ACORDO COOPERAÇÃO',
        # }
        parser_table_sicap_9 = {
            # '1': 1,
            # '2': 2,
            # '3': 3,
            # '4': 5,
            # '5': 5,
            # '14': 5,
            # '15': 5,
            # '16': 5,
            # '17': 5,
            # '6': 6,
            # '7': 7,
            # '8': 8,
            # '9': 9,
            # '10': 10,
            # '11': 11,
            # '12': 'PROMOÇÃO/REMOÇÃO - não deve ser enviado',
            # '13': 'FIM REQUISIÇÃO/ACORDO COOPERAÇÃO - não deve ser enviado',
            1: 1,
            2: 2,
            3: 3,
            4: 5,
            5: 5,
            14: 5,
            15: 5,
            16: 5,
            17: 5,
            6: 6,
            7: 7,
            8: 8,
            9: 9,
            10: 10,
            11: 11,
            12: "PROMOÇÃO/REMOÇÃO - não deve ser enviado",
            13: "FIM REQUISIÇÃO/ACORDO COOPERAÇÃO - não deve ser enviado",
        }
        return parser_table_sicap_9.get(
            self.instance.tipo_desligamento, "tipo de desligamento obrigatório"
        )


class SicapMovimentacaoAposentadoria(SicapMovimentacaoDesligamento):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoAposentadoria, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            organ_origin = self.get_organ_origin()
            cnpj = None
            if organ_origin:
                cnpj = Sicap.get_organ_cpnj(organ_origin)
            else:
                organ_origin = " órgão origem é obrigatório "
            reversal = 0 if self.instance.reversao == 2 else 1
            first_possession = self.instance.movimentacao_posse.first_possession
            text += (
                "|".join(
                    [
                        "%s"
                        % self.generate_header(self.instance.publicacao_movimentacao),
                        "%s" % self.get_type_retirement(),
                        "%s"
                        % (cnpj if cnpj else " cnpj do órgão do cargo é obrigatório "),
                        "%s"
                        % SicapQuadro.get_job_position_chart_law_year(
                            self.instance.movimentacao_posse.quadro.cargo_quadro
                        ),  # 'numero_ano_lei_cargo',
                        "%s"
                        % SicapQuadro.get_code_job_position(
                            self.instance.movimentacao_posse.quadro.cargo_quadro
                        ),  # 'codigo_quadro_ou_cargo',
                        "%s" % reversal,
                        "%s"
                        % (
                            DateUtils.date_to_str(first_possession.data_exercicio)
                            if first_possession.data_exercicio
                            else ""
                        ),
                        # SicapServidor.get_number_tce(self.instance.movimentacao_posse)
                    ]
                )
                + "\n"
            )
        except Exception as err:
            log.exception(err)
            text += " erro gerando aposentadoria %s" % self.instance.servidor
        return text

    def get_type_retirement(self):
        parser_table_sicap_09 = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 5,
        }
        return parser_table_sicap_09.get(self.instance.tipo_aposentadoria)

    def get_job_position(self):
        job_position = None
        if (
            self.instance.movimentacao_posse.quadro
            and self.instance.movimentacao_posse.quadro.cargo
        ):
            job_position = self.instance.movimentacao_posse.quadro.cargo
        return job_position

    def get_organ_origin(self):
        organ_origin = None
        job_position = self.get_job_position()
        if job_position:
            organ_origin = job_position.unidade_administrativa
        return organ_origin


class SicapAfastamentoOutroOrgao(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapAfastamentoOutroOrgao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""

        date_start = datetime(
            int(self.sicap_util.year),
            self.sicap_util.month_start,
            self.sicap_util.day_start,
        ).date()
        date_end = datetime(
            int(self.sicap_util.year),
            self.sicap_util.month_end,
            self.sicap_util.day_end,
        ).date()

        query_filter = Q(data_inicio__gte=date_start) & Q(data_inicio__lte=date_end)

        date_start = self.get_date_start(self.instance.data_inicio)
        date_end = self.get_date_end(self.instance.data_fim)

        publication = self.instance.publicacao_movimentacao
        extensions = self.instance.prorrogacao.filter(query_filter)
        if extensions.exists():
            extension = extensions.latest("data_inicio")
            date_start = self.get_date_start(extension.data_inicio)
            date_end = self.get_date_end(extension.data_fim)
            publication = extension.publicacao if extension.publicacao else publication

        if publication:
            number_document, date_document = Sicap.get_document_data(publication)
            data_publicacao, doe = Sicap.get_publication_data(publication)

        try:
            text += (
                "|".join(
                    [
                        self.generate_header(publication),
                        self.get_number_admission(self.instance.posse),
                        self.get_target_organ_cpnj(),
                        date_start,
                        date_end,
                        self.get_charge(),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando cessao "
            log.exception(err)
        return text

    def get_target_organ_cpnj(self):
        cnpj = None
        if self.instance.orgao:
            cnpj = Sicap.get_organ_cpnj(self.instance.orgao)
            if not cnpj:
                cnpj = " cnpj do órgão destino é obrigatório %s" % (self.instance.orgao)
        return (
            cnpj
            if cnpj
            else (" cnpj do órgão destino é obrigatório %s" % (self.instance.orgao))
        )

    def get_charge(self):
        return str(self.instance.onus) if self.instance.onus else " ônus é obrigatório "


class SicapMovimentacaoRequisicao(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoRequisicao, self).__init__(sicap_util, **kwargs)

    def generate_header(self, publication):
        text = ""
        try:

            cpf = SicapServidor.get_cpf_employee(self.employee)
            type_move = self.get_type_move()

            date_start = datetime(
                int(self.sicap_util.year),
                self.sicap_util.month_start,
                self.sicap_util.day_start,
            ).date()
            date_end = datetime(
                int(self.sicap_util.year),
                self.sicap_util.month_end,
                self.sicap_util.day_end,
            ).date()

            query_filter = (
                Q(requisicao__pk=self.instance.pk)
                & Q(data_inicio__gte=date_start)
                & Q(data_inicio__lte=date_end)
            )
            periodo = self.instance.periodo.filter(query_filter)
            if periodo.exists():
                publication = periodo.latest("data_inicio").publicacao

            type_document = Sicap.get_type_document(publication)
            number_document, date_document = Sicap.get_document_data(publication)
            date_publication, doe = Sicap.get_publication_data(publication)
            notice = ""

            text += "|".join(
                [
                    "%s" % cpf,
                    "%s" % type_document,
                    "%s" % number_document,
                    "%s" % date_document,
                    "%s" % type_move,
                    "%s" % self.sicap_util.unity_employee.get(cpf, 1),
                    "%s" % doe,
                    "%s" % date_publication,
                    "%s" % notice,
                ]
            )
            self.sicap_util.unity_employee.update(
                {cpf: self.sicap_util.unity_employee.get(cpf, 1) + 1}
            )
        except Exception as err:
            log.exception(err)
            text = " Err generate_header %s" % err
        return text

    def text(self):
        text = ""
        try:
            cnpj = Sicap.get_organ_cpnj(self.instance.orgao_origem)
            text += (
                "|".join(
                    [
                        "%s"
                        % self.generate_header(self.instance.publicacao_movimentacao),
                        "%s"
                        % (cnpj if cnpj else " cnpj do órgão de origem é obrigatório "),
                        "%s" % self.get_charge(),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando requisicao "
            log.exception(err)
        return text

    def get_charge(self):
        return self.instance.onus if self.instance.onus else " ônus é obrigatório "


class SicapLicense(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapLicense, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            if self.send_to_sicap(self.get_type_license()):
                possession = SicapServidor.get_latest_possession(self.instance.servidor)
                text += (
                    "|".join(
                        [
                            self.generate_header(self.instance.publicacao_movimentacao),
                            self.get_number_admission(possession),
                            self.get_type_license(),
                            self.get_date_start(self.instance.data_inicio),
                            self.get_date_end(self.instance.data_fim),
                            "1" if self.instance.remunerado else "2",
                        ]
                    )
                    + "\n"
                )
        except Exception as err:
            text += " erro gerando licenca "
            log.exception(err)
        return text

    def send_to_sicap(self, type_license):
        not_send_to_sicap = {
            # 5: 1,  # FÉRIAS AFASTAMENTO
            9: 3,  # LicencaSaude3Dias,
            37: 3,  # LicencaSaude30Dias,
            # 10: 3,  # LicencaSaudeJuntaMedica
            11: 3,  # LicencaDoencaPessoaFamilia # observar pois deixa de ser remunerado
            12: 4,  # LicencaMaternidade
            13: 4,  # LicencaAdocao
            # 14: 5,  # LicencaAfastamentoConjuge
            # 15: 5,  # LicencaServicoMilitar
            # 16: 5,  # LicencaAtividadePolitica
            # 17: 5,  # LicencaCapacitacao
            # 18: 2,  # LicencaInteresseParticular
            # 19: 5,  # LicencaMandatoClassista
        }
        return int(type_license) not in list(not_send_to_sicap.values())

    def get_type_license(self):
        # table_10_type_license = {
        #     1: 'Férias',
        #     2: 'Licença sem vencimentos',
        #     3: 'Licença tratamento de saúde',
        #     4: 'Licença maternidade',
        #     5: 'Licença outros',
        # }
        # 8: 'LicencaSaude',
        # 9: 'LicencaSaude3Dias',
        # 37: 'LicencaSaude30Dias',
        # 10: 'LicencaSaudeJuntaMedica',
        # 11: 'LicencaDoencaPessoaFamilia',
        # 12: 'LicencaMaternidade',
        # 13: 'LicencaAdocao',
        # 14: 'LicencaAfastamentoConjuge',
        # 15: 'LicencaServicoMilitar',
        # 16: 'LicencaAtividadePolitica',
        # 17: 'LicencaCapacitacao',
        # 18: 'LicencaInteresseParticular',
        # 19: 'LicencaMandatoClassista',
        parser_table_sicap_10 = {
            # 5: 1,  # FÉRIAS AFASTAMENTO
            9: 3,  # LicencaSaude3Dias,
            37: 3,  # LicencaSaude30Dias,
            10: 3,  # LicencaSaudeJuntaMedica
            11: 3,  # LicencaDoencaPessoaFamilia # observar pois deixa de ser remunerado
            12: 4,  # LicencaMaternidade
            13: 4,  # LicencaAdocao
            # 14: 5,  # LicencaAfastamentoConjuge
            # 15: 5,  # LicencaServicoMilitar
            # 16: 2,  # LicencaAtividadePolitica
            # 17: 5,  # LicencaCapacitacao
            # 18: 2,  # LicencaInteresseParticular
            # 19: 5,  # LicencaMandatoClassista
        }
        return parser_table_sicap_10.get(self.instance.tipo, "5")


class SicapFeriasAfastamento(SicapLicense):

    def __init__(self, sicap_util, **kwargs):
        super(SicapFeriasAfastamento, self).__init__(sicap_util, **kwargs)

    def text(self):
        from rh.ferias.models import (
            PeriodoAquisitivoServidorUsufruto,
            PASU_INTERROMPIDO,
            PASU_FRUIDO,
            PASU_FRUINDO,
        )
        from rh.ferias.models import PASU_HOMOLOGADO
        from rh.models import AnotacaoFerias

        # ESTADO_PASU = {
        #     PASU_NOVO: "Inclusão solicitada",
        #     PASU_AUTORIZADO_CI: "Autorizado",
        #     PASU_HOMOLOGADO: "Homologado",  # CRIAR AFASTAMENTO
        #     PASU_ALTERADO: "Alterado",  # APAGAR AFASTAMENTO
        #     PASU_EMALTERACAO: "Alteração solicitada",
        #     PASU_INTERROMPIDO: "Interrompido",  # ALTERAR AFASTAMENTO
        #     PASU_SUSPENSO: "Suspenso",  # APAGAR AFASTAMENTO
        #     PASU_FRUINDO: "Em fruição",
        #     PASU_FRUIDO: "Usufruído",
        #     PASU_NAOAUTORIZADO: "Não autorizado",
        #     PASU_SUBSTITUTO: "Substituto"
        # }
        print(
            "------------------------------------------------------------------------------"
        )
        # print self.instance.servidor, self.instance.data_inicio, self.instance.data_fim
        pasus = PeriodoAquisitivoServidorUsufruto.objects.filter(
            periodo_aquisitivo_servidor__servidor=self.instance.servidor,
            data_inicio=self.instance.data_inicio,
            estado__in=[PASU_INTERROMPIDO, PASU_FRUIDO, PASU_FRUINDO, PASU_HOMOLOGADO],
        )

        annotation = None
        message = None
        if pasus.exists():
            pasu = pasus.latest("pk")
            annotations_scale = AnotacaoFerias.objects.filter(
                servidor=self.instance.servidor,
                # tipo_documento__in=[1, 3, 5, 12],
                resumo__icontains=pasu.pas.scale_summary_annotation(),
            ).exclude(publicacao=None)
            if not annotations_scale.exists():
                annotations_scale = AnotacaoFerias.objects.filter(
                    servidor=self.instance.servidor,
                    # tipo_documento__in=[1, 3, 5, 12],
                    resumo__icontains="Marcação/Alteração de Férias %s"
                    % pasu.pas.periodo_aquisitivo,
                ).exclude(publicacao=None)
            if not annotations_scale.exists():
                annotations_scale = AnotacaoFerias.objects.filter(
                    servidor=self.instance.servidor,
                    # tipo_documento__in=[1, 3, 5, 12],
                    resumo__icontains="Alteração de Férias %s"
                    % pasu.pas.periodo_aquisitivo,
                ).exclude(publicacao=None)
            if not annotations_scale.exists():
                annotations_scale = AnotacaoFerias.objects.filter(
                    servidor=self.instance.servidor,
                    # tipo_documento__in=[1, 3, 5, 12],
                    resumo__icontains="Escala de Férias %s"
                    % pasu.pas.periodo_aquisitivo,
                ).exclude(publicacao=None)

            annotations_mark = AnotacaoFerias.objects.filter(
                servidor=self.instance.servidor,
                # tipo_documento__in=[1, 3, 5, 12],
                resumo__icontains=pasu.pas.mark_summary_annotation(),
            ).exclude(publicacao=None)

            # print annotations_scale.count()
            if annotations_scale.exists():
                annotation = annotations_scale.latest("pk")
            if annotation and (
                not annotation.publicacao
                or not annotation.publicacao.data_publicacao
                or not annotation.publicacao.numero_publicacao
            ):
                annotation = None
            # else:
            #     print 'Não existe anotacação de escala!'

            # print annotations_mark.count()
            if not annotation and annotations_mark.exists():
                annotation = annotations_mark.latest("pk")
            # else:
            #     print 'Não existe anotacação de marcação!'

            if (
                annotation
                and annotation.publicacao
                and annotation.publicacao.data_publicacao
                and annotation.publicacao.numero_publicacao
            ):
                self.instance.publicacao_movimentacao = annotation.publicacao
            #     print annotation
            else:
                print("Anotacação não encontrada", self.instance.servidor)
                print("PASU:", pasu.pas.servidor, pasu.get_estado_display(), pasu.pas)
                message = "PASU: %s - " % pasu
        else:
            message = "Não existe pasu! %s - " % self.instance.servidor
            print("Não existe pasu!")

        text = ""
        if message:
            text += message
            text += super(SicapFeriasAfastamento, self).text()
        else:
            text += super(SicapFeriasAfastamento, self).text()

        return text


class SicapMovimentacaoEstabilizacao(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoEstabilizacao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        SicapServidor.get_workplace(self.employee),
                        SicapQuadro.get_job_position_chart_law_year(
                            self.instance.posse.quadro.cargo_quadro
                        ),
                        SicapQuadro.get_code_job_position(
                            self.instance.posse.quadro.cargo_quadro
                        ),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando estabilizacao "
            log.exception(err)
        return text


class SicapMovimentacaoPossessionBase(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoPossessionBase, self).__init__(sicap_util, **kwargs)

    def get_possession(self):
        return self.instance.posse_anterior

    def get_number_dismissal(self):
        number_dismissal = " número e ano de desligamento é obrigatório "
        if hasattr(self.get_possession(), "desligamento"):
            number_dismissal = Sicap.get_document_data(
                self.get_possession().desligamento.publicacao_movimentacao
            )[0]
        return number_dismissal

    def get_date_exercise(self):
        date_exercise = " data exercicio é obrigatório "
        if self.get_possession().data_exercicio:
            date_exercise = DateUtils.date_to_str(self.get_possession().data_exercicio)
        return date_exercise

    def get_job_position_chart(self):
        return self.get_possession().quadro.cargo_quadro

    def get_organ_origin(self):
        organ_origin = " órgão origem é obrigatório "
        if self.get_job_position_chart() and self.get_job_position_chart().cargo:
            self.get_job_position_chart().cargo.unidade_administrativa  # get_organ_origin
        return organ_origin


class SicapMovimentacaoReconducao(SicapMovimentacaoPossessionBase):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoReconducao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            cnpj = (Sicap.get_organ_cpnj(self.get_organ_origin()),)
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        self.get_number_dismissal(),
                        self.get_date_exercise(),
                        cnpj if cnpj else " cnpj do órgão do cargo é obrigatório ",
                        SicapQuadro.get_job_position_chart_law_year(
                            self.get_job_position_chart()
                        ),  # 'numero_ano_lei_cargo',
                        SicapQuadro.get_code_job_position(
                            self.get_job_position_chart()
                        ),  # 'codigo_quadro_ou_cargo',
                        # SicapServidor.get_number_tce(self.get_possession()),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando reconducao "
            log.exception(err)
        return text


class SicapMovimentacaoReintegracao(SicapMovimentacaoPossessionBase):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoReintegracao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        self.get_number_dismissal(),
                        self.get_date_exercise(),
                        SicapQuadro.get_job_position_chart_law_year(
                            self.get_job_position_chart()
                        ),  # 'numero_ano_lei_cargo',
                        SicapQuadro.get_code_job_position(
                            self.get_job_position_chart()
                        ),  # 'codigo_quadro_ou_cargo',
                        # SicapServidor.get_number_tce(self.get_possession()),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando reintegracao "
            log.exception(err)
        return text


class SicapMovimentacaoReversao(SicapMovimentacaoPossessionBase):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoReversao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        self.get_number_admission(self.get_possession()),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando reversao "
            log.exception(err)
        return text


class SicapMovimentacaoReadaptacao(SicapMovimentacaoPossessionBase):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoReadaptacao, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        self.get_number_admission(self.get_possession()),
                        SicapQuadro.get_job_position_chart_law_year(
                            self.get_job_position_chart()
                        ),  # 'numero_ano_lei_cargo',
                        SicapQuadro.get_code_job_position(
                            self.get_job_position_chart()
                        ),  # 'codigo_quadro_ou_cargo',
                        self.get_date_exercise(),
                        # SicapServidor.get_number_tce(self.get_possession()),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando readaptacao "
            log.exception(err)
        return text


class SicapMovimentacaoAproveitamento(SicapMovimentacaoPossessionBase):

    def __init__(self, sicap_util, **kwargs):
        super(SicapMovimentacaoAproveitamento, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        try:
            text += (
                "|".join(
                    [
                        self.generate_header(self.instance.publicacao_movimentacao),
                        SicapQuadro.get_job_position_chart_law_year(
                            self.get_job_position_chart()
                        ),  # 'numero_ano_lei_cargo',
                        SicapQuadro.get_code_job_position(
                            self.get_job_position_chart()
                        ),  # 'codigo_quadro_ou_cargo',
                        self.get_date_exercise(),  # EXERCIO ANTIGO OU O NOVO EXERCÍCIO
                        # SicapServidor.get_number_tce(self.get_possession()),
                    ]
                )
                + "\n"
            )
        except Exception as err:
            text += " erro gerando readaptacao "
            log.exception(err)
        return text


class SicapCargo(Sicap):

    verbose_name = "Gerando Arquivo Cargo"

    def __init__(self, sicap_util, **kwargs):
        super(SicapCargo, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        count = 1
        self.write_feedback()
        query = self.get_job_position_chart()
        total = query.count()
        for job_position_chart in query:
            len_job = len("%s" % job_position_chart)
            text_job = "%s" % job_position_chart
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            name = job_position_chart
            type_job_position = (
                3 if job_position_chart.cargo.tipo_lei_cargo == "EF" else 2
            )  # conforme tabela 1 do sicap
            text += (
                "|".join(
                    [
                        SicapQuadro.get_code_job_position(job_position_chart),
                        "%s" % text_job[0 : len_job if len_job < 80 else 80],
                        "%s" % type_job_position,
                        "1",  # regime juridico
                    ]
                )
                + "\n"
            )
        self.write_file(text)

    @classmethod
    def get_job_position_chart(cls):
        return (
            CargoQuadro.objects.filter(
                cargo__indicativo__in=["S", "M"],
                cargo__tipo_lei_cargo__in=("EF", "CM", "FC"),
            )
            .order_by("cargo__nome")
            .distinct()
        )

    @classmethod
    def get_salary(cls, cargo):
        salary = 0.0
        try:
            # referencia = cargo.get_salarios(data_inicio=datetime(2014, 9, 1).date())[0][1]
            reference = cargo.get_salarios()[0][1]
            # TODO: VERIFICAR QUAL É O DIA PARA PEGAR O SALÁRIO VIGENTE
            salary = float(reference.valor) + float(reference.gratificacao)
            # print cargo, reference, reference.valor, reference.gratificacao, salary
        except Exception as err:
            log.exception(err)
            salary = err
            # print 'Problemas com o salário.'
        return salary


class SicapLei(Sicap):

    verbose_name = "Gerando Arquivo Lei"

    def __init__(self, sicap_util, **kwargs):
        super(SicapLei, self).__init__(sicap_util, **kwargs)
        self.query_filter = kwargs.get("query_filter")

    def text(self):
        text = ""
        laws = []
        parser_table_sicap_11 = {
            "EF": 1,
            "CM": 3,
            "FC": 3,
        }
        count = 1
        self.write_feedback()
        query = (
            SicapCargo.get_job_position_chart()
            .filter(self.query_filter)
            .exclude(cargo__codigo="OMP")
        )
        total = query.count()
        for job_position_chart in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            law_year = " lei e ano da lei é obrigatório "
            date = " data da lei é obrigatório "
            local_publication = " veículo de publicação é obrigatório "
            date_publication = (
                " data publicação do veículo de publicação é obrigatório "
            )
            type_law = parser_table_sicap_11.get(
                job_position_chart.cargo.tipo_lei_cargo
            )
            if job_position_chart.publicacao_criacao:
                if job_position_chart.publicacao_criacao.numero:
                    law_year = "%s%s" % (
                        Sicap.format_number_law(
                            job_position_chart.publicacao_criacao.numero
                        ),
                        job_position_chart.publicacao_criacao.ano,
                    )
                if job_position_chart.publicacao_criacao.data_vigencia:
                    date = DateUtils.date_to_str(
                        job_position_chart.publicacao_criacao.data_vigencia
                    )
                if job_position_chart.publicacao_criacao.veiculo_publicacao:
                    local_publication = (
                        job_position_chart.publicacao_criacao.get_veiculo_publicacao_display()
                    )
                if job_position_chart.publicacao_criacao.data_publicacao:
                    date_publication = DateUtils.date_to_str(
                        job_position_chart.publicacao_criacao.data_publicacao
                    )

            # authorizing = '0' if job_position_chart.publicacao_criacao.lei_autorizativa else '2'  # 0=lei, 2=sem lei

            notice = "*"

            buf = "%s%s" % (law_year, type_law)
            if buf not in laws:
                text += (
                    "|".join(
                        [
                            "%s" % type_law,
                            "%s" % law_year,
                            "%s" % date,
                            # authorizing,
                            "%s" % local_publication,
                            "%s" % date_publication,
                            "%s" % notice,
                        ]
                    )
                    + "\n"
                )
                laws.append(buf)
        self.write_file(text)


class SicapQuadro(Sicap):

    verbose_name = "Gerando Arquivo Quadro"

    def __init__(self, sicap_util, **kwargs):
        super(SicapQuadro, self).__init__(sicap_util, **kwargs)
        self.query_filter = kwargs.get("query_filter")

    def text(self):
        text = ""
        count = 1
        self.write_feedback()
        query = (
            SicapCargo.get_job_position_chart()
            .filter(self.query_filter)
            .exclude(cargo__codigo="OMP")
        )
        total = query.count()
        for job_position_chart in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            law_year = SicapQuadro.get_job_position_chart_law_year(job_position_chart)
            code_job_position = SicapQuadro.get_code_job_position(job_position_chart)

            quantity = " cargo é obrigatório "
            if job_position_chart.quantidade_vagas:
                quantity = job_position_chart.quantidade_vagas
            salary = SicapCargo.get_salary(job_position_chart.cargo)
            level_education = "1"
            # ######MODIFICAÇÕES###
            regime = " regime é obrigatório"
            if job_position_chart.military:
                regime = "2"
            else:
                regime = "1"

            nature_job = " natureza do cargo é obrigatório"
            if job_position_chart.military:
                nature_job = "9"
            elif job_position_chart.teacher:
                nature_job = "3"
            elif job_position_chart.health:
                nature_job = "2"
            else:
                nature_job = "1"

            weekly_workday = " jornada semanal é obrigatório"
            if job_position_chart.carga_horaria:
                weekly_workday = job_position_chart.carga_horaria

            # ####FIM#####

            # workload = ' carga horaria é obrigatório '
            # if job_position_chart.carga_horaria:
            #     workload = unicode(job_position_chart.carga_horaria)
            # type_workload = ' tipo carga horária é obrigatório '
            # if job_position_chart.tipo_carga_horaria:
            #     type_workload = unicode(job_position_chart.tipo_carga_horaria)

            text += (
                "|".join(
                    [
                        "%s" % law_year,
                        "%s" % code_job_position,
                        "%s" % quantity,
                        "%s" % salary,
                        "%s" % level_education,
                        "%s" % regime,
                        "%s" % nature_job,
                        "%s" % weekly_workday,
                        # workload,
                        # type_workload
                    ]
                )
                + "\n"
            )
        self.write_file(text)

    @classmethod
    def get_job_position_chart_law_year(cls, job_position_chart):
        law_year = " lei e ano do cargo em quadro é obrigatório "
        if (
            job_position_chart
            and job_position_chart.publicacao_criacao.numero
            and job_position_chart.publicacao_criacao.ano
        ):
            law_year = "%s%s" % (
                Sicap.format_number_law(job_position_chart.publicacao_criacao.numero),
                job_position_chart.publicacao_criacao.ano,
            )
        return law_year

    @classmethod
    def get_code_job_position(cls, job_position_chart):
        code_job_position = " cargo em cargo em quadro é obrigatório "
        if (
            job_position_chart
            and job_position_chart.cargo
            and job_position_chart.cargo.codigo
        ):
            code_job_position = job_position_chart.cargo.codigo
            if (
                job_position_chart.especialidade
                and job_position_chart.especialidade.sigla
            ):
                code_job_position = "%s-%s" % (
                    code_job_position,
                    job_position_chart.especialidade.sigla,
                )
        return code_job_position.rjust(10, "0")


class SicapEntidade(Sicap):

    verbose_name = "Gerando Arquivo Lotação"

    def __init__(self, sicap_util, **kwargs):
        super(SicapEntidade, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        count = 1
        self.write_feedback()
        query = Lotacao.objects.filter(organograma=True)
        total = query.count()
        for workplace in query:
            len_work = len("%s" % workplace)
            text_work = "%s" % workplace
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            text += (
                "|".join(
                    [
                        self.get_initials(workplace),
                        "1",
                        "%s" % text_work[0 : len_work if len_work < 49 else 49],
                    ]
                )
                + "\n"
            )
        self.write_file(text)

    @classmethod
    def get_initials(cls, workplace):
        if workplace and workplace.sigla:
            workplace = workplace.sigla
        else:
            workplace = "%s não possui lotação(ou a sigla). Obrigatório." % workplace
        return workplace


class SicapFolhaBase(Sicap):

    def __init__(self, sicap_util, **kwargs):
        super(SicapFolhaBase, self).__init__(sicap_util, **kwargs)

    def query(self):
        query = FolhaEvento.objects.filter(
            ~Q(evento__genre_event__config_transparency=None)
            & Q(folha__periodo__mes__gte=self.sicap_util.month_start)
            & Q(
                folha__periodo__mes__lte=(
                    13 if self.sicap_util.month_end == 12 else self.sicap_util.month_end
                )
            )
            & Q(folha__periodo__ano=self.sicap_util.year)
        ).order_by("servidor", "folha__periodo__mes")
        if self.sicap_util.months:
            query = query.filter(folha__periodo__mes__in=self.sicap_util.months)
        return query


class SicapFolhaTipo(SicapFolhaBase):

    verbose_name = "Gerando Arquivo Folha Tipo"

    def __init__(self, sicap_util, **kwargs):
        super(SicapFolhaTipo, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        count = 1
        self.write_feedback()
        query = FolhaTipo.objects.filter(
            numero__in=self.query().values("folha__tipo_folha__numero").distinct()
        )
        total = query.count()
        for sheet in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            text += (
                "|".join(
                    [
                        "%s" % sheet.numero,
                        "%s" % sheet,
                    ]
                )
                + "\n"
            )
        self.write_file(text)


class SicapFolhaItem(SicapFolhaBase):

    verbose_name = "Gerando Arquivo Folha Item"

    def __init__(self, sicap_util, **kwargs):
        super(SicapFolhaItem, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        # events = []
        count = 1
        self.write_feedback()
        query = Evento.objects.filter(pk__in=self.query().values("evento").distinct())
        total = query.count()
        for event in query:
            nature_of_event = ""
            if not event.nature_of_event:
                log.debug(event)
            else:
                nature_of_event = event.nature_of_event.code
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            text += (
                "|".join(
                    [
                        "%s" % event.numero,
                        "%s" % self.get_type_event(event),
                        "%s" % nature_of_event,
                        "%s" % event,
                        "%s" % self.get_nature_advantage(event),
                        "%s" % SicapFolhaItem.get_nature_discount(event),
                        "%s" % self.get_nature_description(event),
                        "%s" % self.is_rpps(event),
                        "%s" % self.is_rgps(event),
                        # normalize('NFKD', unicode(event)).encode("ascii", "ignore"),
                    ]
                )
                + "\n"
            )
        self.write_file(text)

    def get_type_event(self, event):
        type_event = {
            "P": 1,  # VANTAGEM
            "D": 2,  # DESCONTO
        }
        return type_event.get(event.tipo)

    def is_rpps(self, event):
        rpps = "2"
        if event.carater == 8:
            if event.genre_event.genre_number in [
                900,
                901,
                902,
                905,
                906,
                908,
                909,
                912,
                913,
                915,
                916,
                917,
                918,
            ]:
                rpps = str(1)

        return rpps

    def is_rgps(self, event):
        rpps = "2"
        if event.carater == 8:
            if event.genre_event.genre_number in [910, 911]:
                rpps = str(1)

        return rpps

    def get_nature_description(self, event):
        if (
            self.get_nature_advantage(event) == "3"
            or SicapFolhaItem.get_nature_discount(event) == "4"
        ):
            return (
                Choice.objects.filter(
                    app_label="gfp", name="EVENT_CHARACTER", value=event.carater
                )
                .last()
                .label
            )
        return ""

    def get_nature_advantage(self, event):
        nature_advantage = event.carater
        if event.carater is not [1, 2]:
            nature_advantage = str(3)
        return nature_advantage

    @classmethod
    def get_nature_discount(cls, event):
        nature_discount = "4"
        # event_igeprev = ['900', '902', '905', '901', '906']
        # event_irrf = ['991', '992', '999']
        event_roof = ["498", "499"]
        if event.carater == 8:
            nature_discount = str(1)
        elif event.carater == 4:
            nature_discount = str(2)
        elif event.genre_event.genre_number in event_roof:
            nature_discount = str(3)
        return nature_discount


class SicapFolha(SicapFolhaBase):

    verbose_name = "Gerando Arquivo Folha"

    def __init__(self, sicap_util, **kwargs):
        super(SicapFolha, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        sheets = []
        employee_array = []
        registry = None
        count = 1
        self.write_feedback()
        query = self.query()
        total = query.count()
        for sheet_event in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            job_position = self.job_position(sheet_event)
            if not job_position:
                job_position = "******"
            job_commission = self.job_commission(sheet_event)
            if not job_commission:
                job_commission = "******"
            job_function = self.job_function(sheet_event)
            if not job_function:
                job_function = "******"

            possession = SicapServidor.get_latest_possession(sheet_event.servidor)
            exercise_date = DateUtils.date_to_str(
                possession.first_possession.data_exercicio
            )
            off_date = ""
            if sheet_event.servidor.data_desligamento:
                off_date = DateUtils.date_to_str(sheet_event.servidor.data_desligamento)

            sheet_employee = {
                "type_sheet": self.get_type_sheet_new(sheet_event),
                "item_sheet": self.get_item_sheet(sheet_event),
                "registry": str(sheet_event.servidor.matricula),
                "cpf": str(sheet_event.servidor.pessoa_fisica.cpf),
                "name": sheet_event.servidor.pessoa_fisica,
                "birth_date": DateUtils.date_to_str(
                    sheet_event.servidor.pessoa_fisica.data_nascimento
                ),
                "type_link_payment": SicapServidor.type_link_payment(
                    sheet_event.servidor
                ),
                "exercise_date": exercise_date,
                "off_date": off_date,
                "situation_employee": self.get_active(sheet_event.servidor),
                "nature_socialsecurity": self.get_nature_socialsecurity(
                    sheet_event.servidor
                ),
                "socialsecurity": self.get_socialsecurity(sheet_event.servidor),
                "workload": self.get_workload(sheet_event.servidor),
                "amount": roundf(str(sheet_event.valor)),
                "aliquot_socialsecurity": self.get_aliquot_socialsecurity(sheet_event),
                "aliquot_socialsecurity_employer": self.get_aliquot_socialsecurity_employer(
                    sheet_event
                ),
                "month": (
                    str(12)
                    if sheet_event.folha.periodo.mes == 13
                    else str(sheet_event.folha.periodo.mes)
                ),
                "year": str(sheet_event.folha.periodo.ano),
                "job_position": job_position,
                "job_function": job_function,
                "commission": job_commission,
                "city": self.get_city(sheet_event.servidor),
                "workplace_organ": self.get_workplace_not_none(sheet_event.servidor),
                "complement": "*",
                "obs": "*",
            }

            if sheet_event.servidor.matricula != registry:
                sheets += employee_array
                registry = sheet_event.servidor.matricula
                employee_array = []

            if not self.search_occurrence(employee_array, sheet_employee):
                employee_array.append(sheet_employee)

            count += 1

            print("count: %s - total: %s" % (count, total))

            if count > total:
                sheets += employee_array

        try:
            count = 1
            total = len(sheets)
            self.write_feedback(message_progress="Escrevendo Arquivo Folha")
            with codecs.open(self._file_name, "a", "utf-8") as fd:
                for sheet in sheets:
                    self.write_feedback(
                        progress=((100.0 * float(count)) / float(total)),
                        message_progress="Escrevendo Arquivo Folha",
                    )
                    print(
                        "Escrevendo Arquivo Folha - %s"
                        % ((100.0 * float(count)) / float(total))
                    )
                    count += 1
                    text = (
                        "|".join(
                            [
                                "%s" % sheet.get("type_sheet"),
                                "%s" % sheet.get("item_sheet"),
                                "%s" % sheet.get("registry"),
                                "%s" % sheet.get("cpf"),
                                "%s" % sheet.get("name"),
                                "%s" % sheet.get("birth_date"),
                                "%s" % sheet.get("type_link_payment"),
                                "%s" % sheet.get("exercise_date"),
                                "%s" % sheet.get("off_date"),
                                "%s" % sheet.get("situation_employee"),
                                "%s" % sheet.get("nature_socialsecurity"),
                                "%s" % sheet.get("socialsecurity"),
                                "%s" % sheet.get("workload"),
                                "",
                                "%s" % sheet.get("amount"),
                                "%s" % sheet.get("aliquot_socialsecurity"),
                                "%s" % sheet.get("aliquot_socialsecurity_employer"),
                                "%s" % sheet.get("month"),
                                "%s" % sheet.get("year"),
                                "%s" % sheet.get("job_position"),
                                "%s" % sheet.get("job_function"),
                                "%s" % sheet.get("commission"),
                                "%s" % sheet.get("city"),
                                "%s" % sheet.get("workplace_organ"),
                                "%s" % sheet.get("complement"),
                                "%s" % sheet.get("obs"),
                            ]
                        )
                        + "\n"
                    )
                    fd.write(text)
        except Exception as err:
            print(err)
            log.exception(err)
            raise err

    def get_type_sheet_new(self, sheet_event):
        if sheet_event.folha.tipo_folha.numero == "0001":
            return str(1)
        elif sheet_event.folha.tipo_folha.numero == "0021":
            return str(4)
        elif sheet_event.folha.tipo_folha.numero == "0003":
            return str(5)
        else:
            return str(12)

    def get_aliquot_socialsecurity(self, sheet_event):
        aliquot_socialsecurity = ""
        aliquot = SicapFolhaItem.get_nature_discount(sheet_event.evento)
        if int(aliquot) in [1, 2]:
            if sheet_event.pct:
                aliquot_socialsecurity = roundf(sheet_event.pct)
            if not aliquot_socialsecurity:
                aliquot_socialsecurity = "0"
        return aliquot_socialsecurity

    def get_aliquot_socialsecurity_employer(self, sheet_event):
        socialsecurity = self.get_socialsecurity(sheet_event.servidor)
        if socialsecurity == 1:
            aliquot_socialsecurity = (
                sheet_event.patronal * 100
            ) / sheet_event.valor_base
            aliquot_socialsecurity = (
                0 if aliquot_socialsecurity < 0 else aliquot_socialsecurity
            )
            return roundf(aliquot_socialsecurity)
        else:
            return ""

    def get_type_sheet(self, sheet_event):
        return str(sheet_event.folha.tipo_folha.numero)

    def get_item_sheet(self, sheet_event):
        return str(sheet_event.evento.numero)

    def get_workplace_not_none(self, employee):
        workplace = SicapServidor.get_workplace_raw(employee)
        if workplace:
            code = workplace.lotacao.sigla
        else:
            code = str(Lotacao.objects.get(sigla="PGJ-TO").sigla)
        return code

    def job_position(self, sheet_event):
        job_position = sheet_event.contracheque.cargo_efetivo
        if job_position:
            job_position = job_position
        return job_position

    def job_commission(self, sheet_event):
        job_position = sheet_event.contracheque.cargo_comissao
        if job_position:
            job_position = job_position
        return job_position

    def job_function(self, sheet_event):
        job_position = sheet_event.contracheque.cargo_comissao
        if job_position and job_position.tipo_lei_cargo == "FC":
            job_position = job_position
        else:
            job_position = None
        return job_position

    def get_city(self, employee):
        # ibge = 'não encontrou cidade de lotação'
        ibge = str(1721000)  # 1721000 = Palmas-TO
        workplace = SicapServidor.get_workplace_raw(employee)
        if workplace:
            ibge = str(workplace.lotacao.localidade.ibge)
        return ibge

    def get_active(self, employee):
        return str(1) if employee.ativo else str(2)

    def get_nature_socialsecurity(self, employee):
        # TODO Verificar se não é necessário pegar o regime vigente para a data de interesse
        return str(2) if employee.regime_social_security == 3 else str(1)

    def get_socialsecurity(self, employee):
        # TODO Verificar se não é necessário pegar o regime vigente para a data de interesse
        return str(2) if employee.regime_social_security == 1 else str(1)

    def get_workload(self, employee):
        workload = 35
        workloads = CargaHoraria.objects.filter(servidor=employee, data_fim=None)
        if workloads.exists():
            workload = int(workloads.last().quantidade)
        if not employee.ativo:
            workload = 0
        return str(workload)

    def search_occurrence(self, sheets, sheet_employee):
        for sheet in sheets:
            if (
                sheet.get("registry") == sheet_employee.get("registry")
                and sheet.get("month") == sheet_employee.get("month")
                and sheet.get("year") == sheet_employee.get("year")
                and sheet.get("type_sheet") == sheet_employee.get("type_sheet")
                and sheet.get("item_sheet") == sheet_employee.get("item_sheet")
            ):
                sheet.update(
                    {
                        "registry": sheet.get("registry"),
                        "cpf": sheet.get("cpf"),
                        "month": sheet.get("month"),
                        "year": sheet.get("year"),
                        "type_sheet": sheet.get("type_sheet"),
                        "item_sheet": sheet.get("item_sheet"),
                        "amount": roundf(
                            str(
                                float(sheet.get("amount"))
                                + float(sheet_employee.get("amount"))
                            )
                        ),
                    }
                )
                return True
        return False


class SicapPensaoFolha(SicapFolha):

    def __init__(self, sicap_util, **kwargs):
        super(SicapPensaoFolha, self).__init__(sicap_util, **kwargs)

    def query(self):
        return PensaoFolhaEvento.objects.filter(
            ~Q(pensao__pensaomorte=None)
            & Q(folha__periodo__mes__gte=self.sicap_util.month_start)
            & Q(
                folha__periodo__mes__lte=(
                    13 if self.sicap_util.month_end == 12 else self.sicap_util.month_end
                )
            )
            & Q(folha__periodo__ano=self.sicap_util.year)
        ).order_by("pensao__servidor", "folha__periodo__mes")

    def text(self):
        text = ""
        sheets = []
        employee_array = []
        registry = None
        total = self.query().count()
        count = 1

        self.write_feedback()
        query = self.query()
        total = query.values("evento").distinct().count()
        for pension_sheet_event in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            job_position = "******"
            commission = "******"

            sheet_employee = {
                "registry": str(pension_sheet_event.pensao.servidor.matricula),
                "cpf": str(pension_sheet_event.pensao.pensionista.cpf),
                "name": pension_sheet_event.pensao.pensionista,
                "type_link_payment": str(
                    SicapServidor.type_link_payment(pension_sheet_event.pensao.servidor)
                ),
                "type_sheet": self.get_type_sheet(pension_sheet_event),
                "item_sheet": self.get_item_sheet(pension_sheet_event),
                "month": (
                    str(12)
                    if pension_sheet_event.folha.periodo.mes == 13
                    else str(pension_sheet_event.folha.periodo.mes)
                ),
                "year": str(pension_sheet_event.folha.periodo.ano),
                "job_position": job_position,
                "commission": commission,
                "amount": roundf(str(pension_sheet_event.valor)),
                "complement": "*",
            }

            if pension_sheet_event.pensao.pensionista.cpf != registry:
                sheets += employee_array
                registry = pension_sheet_event.pensao.pensionista.cpf
                employee_array = []

            if not self.search_occurrence(employee_array, sheet_employee):
                employee_array.append(sheet_employee)

            count += 1

            print("count: %s - total: %s" % (count, total))

            if count > total:
                sheets += employee_array

        for sheet in sheets:
            text += (
                "|".join(
                    [
                        "%s" % sheet.get("registry"),
                        "%s" % sheet.get("cpf"),
                        "%s" % sheet.get("name"),
                        "%s" % sheet.get("type_link_payment"),
                        "%s" % sheet.get("type_sheet"),
                        "%s" % sheet.get("item_sheet"),
                        "%s" % sheet.get("month"),
                        "%s" % sheet.get("year"),
                        "%s" % sheet.get("job_position"),
                        "%s" % sheet.get("commission"),
                        "%s" % sheet.get("amount"),
                        "%s" % sheet.get("complement"),
                    ]
                )
                + "\n"
            )
        return text


class SicapPension(SicapMovimentacaoPessoal):

    def __init__(self, sicap_util, **kwargs):
        super(SicapPension, self).__init__(sicap_util, **kwargs)

    def text(self):
        text = ""
        pensions = Pensao.objects.filter(
            ~Q(pensaomorte=None)
            & Q(data_inicio__gte=self.sicap_util.date_start)
            & Q(data_inicio__lte=self.sicap_util.date_end)
        )
        for pension in pensions:
            self.employee = pension.servidor
            self.instance = pension
            possession = SicapServidor.get_latest_possession(self.employee)
            try:
                text += (
                    "|".join(
                        [
                            "%s" % self.generate_header(self.instance.publicacao),
                            # SicapQuadro.get_code_job_position(possession.quadro.cargo_quadro if possession else None),  # self.instance.movimentacao_posse.quadro 'codigo_quadro_ou_cargo',  # Código do quadro instituido pelo quadro de pessoal efetivo do órgão de origem (do cargo exercido antes da pensão)
                            "%s"
                            % self.get_organ_origin(
                                possession
                            ),  # CNPJ do órgão de origem
                            # self.instance.movimentacao_posse.quadro 'numero_ano_lei_cargo',  # Número e ano da lei atorizativa que institui o quadro de pessoal efetivo do órgão de origem (do cargo exercido antes da pensão)
                            "%s"
                            % SicapQuadro.get_job_position_chart_law_year(
                                possession.quadro.cargo_quadro if possession else None
                            ),
                            # self.instance.movimentacao_posse.quadro 'codigo_quadro_ou_cargo',  # Código do quadro instituido pelo quadro de pessoal efetivo do órgão de origem (do cargo exercido antes da pensão)
                            "%s"
                            % SicapQuadro.get_code_job_position(
                                possession.quadro.cargo_quadro if possession else None
                            ),
                            # self.get_cpf_beneficiary(),  # Número do CPF do beneficiário
                            # self.get_name_beneficiary(),  # Nome do beneficiário
                            # self.get_type_beneficiary(),  # Código do tipo de benefício
                            # self.get_date_start_beneficiary(),  # Data de ínicio do benefício
                            # self.get_date_end_beneficiary(),  # Data de fim do benefício
                            # self.get_degree_kinship_beneficiary(),  # Código do grau de parentesco
                            # self.get_percentage_benefit(),  # Porcentagem do beneficio
                            # self.get_responsible_benefit(),  # Nome do responsável pelo beneficiário
                        ]
                    )
                    + "\n"
                )
            except Exception as err:
                log.exception(err)
                text += " erro gerando %s " % err
        self.write_file(text)

    def get_organ_origin(self, possession):
        return self.get_organ_cpnj(
            possession.quadro.cargo.unidade_administrativa if possession else possession
        )

    def get_cpf_beneficiary(self):
        cpf = " Número do CPF do beneficiário obrigatório "
        if self.instance.pensionista.cpf:
            cpf = str(self.instance.pensionista.cpf)
        return cpf

    def get_name_beneficiary(self):
        name = " Nome do beneficiário obrigatório "
        if self.instance.pensionista.nome:
            name = self.instance.pensionista.nome
        return name

    def get_type_beneficiary(self):
        # table_07_benefit = {
        #     1: ' Vitalícia',
        #     2: ' Temporária',
        # }
        return "2"

    def get_date_start_beneficiary(self):
        return self.get_date_start(self.instance.data_inicio)

    def get_date_end_beneficiary(self):
        return self.get_date_end(self.instance.data_fim)

    def get_degree_kinship_beneficiary(self):
        return self.instance.degree_kinship

    def get_percentage_benefit(self):
        percentage = " Porcentagem do beneficio obrigatório "
        # (1, 'VALOR FIXO'),
        # (2, 'PERCENTUAL'),
        # (3, 'SALÁRIO MÍNIMO')
        if self.instance.tipo in (1, 3):
            percentage = "100"
        else:
            percentage = str(self.instance.valor / 100)
        return percentage

    def get_responsible_benefit(self):
        name = " Nome do responsável pelo beneficiário obrigatório "
        if self.instance.representante_legal.nome:
            name = self.instance.representante_legal.nome
        return name
