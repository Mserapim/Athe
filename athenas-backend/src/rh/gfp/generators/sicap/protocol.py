# -*- coding: utf-8 -*-
import calendar
import codecs
import functools
import os
import re
import zipfile
from datetime import date, datetime
from os import unlink

from django.conf import settings
from django.db.models import Count, F, Q

from contrib.daterange import NewDateRange
from contrib.protofile import Protocol, Record
from contrib.utils import getLogger
from ged.models import Arquivo as File
from rh.afastamento.models import (
    AfastamentoDisponibilidade,
    AfastamentoOutroOrgao,
    BaseLicencaAfastamento,
)
from rh.const import CANCELADO, TYPE_BY_POSSESSION_BENEFICIARY
from rh.gfp.generators.sicap.layouts import SICAP
from rh.gfp.models import Evento, FatorFap, FatorRat, FolhaEvento
from rh.models import (
    CargaHoraria,
    CargoQuadro,
    Documento,
    Localidade,
    Lotacao,
    MovimentacaoAposentadoria,
    MovimentacaoAproveitamento,
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    MovimentacaoReadaptacao,
    MovimentacaoReconducao,
    MovimentacaoReintegracao,
    Publicacao,
    PublicConcurrence,
    RequestMove,
    Servidor,
    SocialSecurity,
    UnidadeAdministrativa,
)

__name__ = "SICAP"
__hid__ = "001"

log = getLogger(__name__)


def my_cmp(first, second):
    rs = 1
    if type(first) == str or type(second) == str:
        rs = -1
    elif first < second:
        rs = -1
    return rs


class SicapGenerator(object):

    def __init__(self, **kwargs):
        try:
            self.sicap_helper = SicapHelper(**kwargs)
        except Exception as err:
            self.sicap_helper = kwargs.get("sicap_helper", None)
            if not self.sicap_helper:
                log.exception(err)
                print(err)
                raise err
        finally:
            self.feedback = kwargs.get(
                "feedback", lambda progress_message, progress, **kwargs: False
            )
            self.task = kwargs.get("task", None)
            self.sicap_helper.paymentfile = kwargs.get("paymentfile", None)

    def generate(self):
        """
        Este método gera os arquivos de protocolo SICAP.
        O geração deve ocorrer de forma pré definida, poís algumas classes depedem de valores preenchidas por outras.
        Ex. A classe que gera o arquivo de Desligamento preenche a lista de Servidores (employees) e Admissões (admissions)
        presentes na classe SicapHelper, que irá ser utilizado pela classe que gera o arquivo de Admissão e gera o
        arquivo de Servidores.
        """
        try:

            print("DispatchFile")
            dispatch_file_name = (
                "%(directory)s/InfoRemessa.xml" % self.sicap_helper.sign_file()
            )
            DispatchFile(
                self.sicap_helper,
                file_name=dispatch_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("SocialSecurityGathering")
            socialsecurity_gathering_file_name = (
                "%(directory)s/RecolhimentoPrevidenciario.xml"
                % self.sicap_helper.sign_file()
            )
            SocialSecurityGatheringFile(
                self.sicap_helper,
                file_name=socialsecurity_gathering_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("AdministrativeUnitFile")
            administrative_unit_file_name = (
                "%(directory)s/UnidadeAdministrativa.xml"
                % self.sicap_helper.sign_file()
            )
            AdministrativeUnitFile(
                self.sicap_helper,
                file_name=administrative_unit_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("SocialSecurityDemonstrativeFile")
            socialsecurity_demonstrative_file_name = (
                "%(directory)s/DemonstrativoPrevidenciario.xml"
                % self.sicap_helper.sign_file()
            )
            SocialSecurityDemonstrativeFile(
                self.sicap_helper,
                file_name=socialsecurity_demonstrative_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("ReadaptationFile")
            readaptation_file_name = (
                "%(directory)s/Readaptacao.xml" % self.sicap_helper.sign_file()
            )
            ReadaptationFile(
                self.sicap_helper,
                file_name=readaptation_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("ReappointmentFile")
            reappointment_file_name = (
                "%(directory)s/Reconducao.xml" % self.sicap_helper.sign_file()
            )
            ReappointmentFile(
                self.sicap_helper,
                file_name=reappointment_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("ReintegrationFile")
            reintegration_file_name = (
                "%(directory)s/Reintegracao.xml" % self.sicap_helper.sign_file()
            )
            ReintegrationFile(
                self.sicap_helper,
                file_name=reintegration_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("RetirementFile")
            retirement_file_name = (
                "%(directory)s/Aposentadoria.xml" % self.sicap_helper.sign_file()
            )
            RetirementFile(
                self.sicap_helper,
                file_name=retirement_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("LicenseFile")
            licence_file_name = (
                "%(directory)s/Licenca.xml" % self.sicap_helper.sign_file()
            )
            LicenseFile(
                self.sicap_helper,
                file_name=licence_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("FunctionFile")
            function_file_name = (
                "%(directory)s/Funcao.xml" % self.sicap_helper.sign_file()
            )
            FunctionFile(
                self.sicap_helper,
                file_name=function_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("AssignmentFile")
            assignment_file_name = (
                "%(directory)s/Cessao.xml" % self.sicap_helper.sign_file()
            )
            AssignmentFile(
                self.sicap_helper,
                file_name=assignment_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("AvailabilityFile")
            availability_file_name = (
                "%(directory)s/Disponibilidade.xml" % self.sicap_helper.sign_file()
            )
            AvailabilityFile(
                self.sicap_helper,
                file_name=availability_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("UtilizationFile")
            utilization_file_name = (
                "%(directory)s/Aproveitamento.xml" % self.sicap_helper.sign_file()
            )
            UtilizationFile(
                self.sicap_helper,
                file_name=utilization_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("SheetItemFile")
            sheet_item_file_name = (
                "%(directory)s/FolhaItem.xml" % self.sicap_helper.sign_file()
            )
            SheetItemFile(
                self.sicap_helper,
                file_name=sheet_item_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("SheetFile")
            sheet_file_name = (
                "%(directory)s/FolhaPagamento.xml" % self.sicap_helper.sign_file()
            )
            SheetFile(
                self.sicap_helper,
                file_name=sheet_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("DismissalFile")
            dismissal_file_name = (
                "%(directory)s/Desligamento.xml" % self.sicap_helper.sign_file()
            )
            DismissalFile(
                self.sicap_helper,
                file_name=dismissal_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("AdmissionFile")
            admission_file_name = (
                "%(directory)s/Admissao.xml" % self.sicap_helper.sign_file()
            )
            AdmissionFile(
                self.sicap_helper,
                file_name=admission_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("JobPositionFile")
            job_position_file_name = (
                "%(directory)s/Cargo.xml" % self.sicap_helper.sign_file()
            )
            JobPositionFile(
                self.sicap_helper,
                file_name=job_position_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("PublicConcurrenceFile")
            public_concurrence_file_name = (
                "%(directory)s/Edital.xml" % self.sicap_helper.sign_file()
            )
            PublicConcurrenceFile(
                self.sicap_helper,
                file_name=public_concurrence_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("LawFile")
            law_file_name = "%(directory)s/Lei.xml" % self.sicap_helper.sign_file()
            LawFile(
                self.sicap_helper,
                file_name=law_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("ActFile")
            act_file_name = "%(directory)s/Ato.xml" % self.sicap_helper.sign_file()
            ActFile(
                self.sicap_helper,
                file_name=act_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("EmployeeFile")
            employee_file_name = (
                "%(directory)s/Servidor.xml" % self.sicap_helper.sign_file()
            )
            EmployeeFile(
                self.sicap_helper,
                file_name=employee_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            print("WorkplaceFile")
            workplace_file_name = (
                "%(directory)s/Lotacao.xml" % self.sicap_helper.sign_file()
            )
            WorkplaceFile(
                self.sicap_helper,
                file_name=workplace_file_name,
                feedback=self.feedback,
                task=self.task,
            ).build()

            self.feedback(
                "%(message_progress)s", 1, message_progress="Gerando Arquivo ZIP."
            )
            self.zip(
                dispatch=dispatch_file_name,
                administrative_unit=administrative_unit_file_name,
                act=act_file_name,
                job_position=job_position_file_name,
                workplace=workplace_file_name,
                employee=employee_file_name,
                admission=admission_file_name,
                dismissal=dismissal_file_name,
                readaptation=readaptation_file_name,
                reappointment=reappointment_file_name,
                reintegration=reintegration_file_name,
                retirement=retirement_file_name,
                license=licence_file_name,
                function=function_file_name,
                assignment=assignment_file_name,
                availability=availability_file_name,
                utilization=utilization_file_name,
                sheet_item=sheet_item_file_name,
                sheet=sheet_file_name,
                public_concurrence=public_concurrence_file_name,
                law=law_file_name,
                socialsecurity_demonstrative=socialsecurity_demonstrative_file_name,
                socialsecurity_gathering=socialsecurity_gathering_file_name,
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
                self.sicap_helper.directory_tmp(),
                "%s-%s-%s.zip"
                % (
                    self.sicap_helper.file_name,
                    SicapHelper._months_to_unicode(self.sicap_helper.months),
                    self.sicap_helper.year,
                ),
            ),
            "w",
        )
        for key in list(files.keys()):
            try:
                print(files.get(key))
                zip_file.write(
                    files.get(key),
                    arcname="%s"
                    % (
                        files.get(key).split(
                            "%(directory)s" % self.sicap_helper.sign_file()
                        )[1]
                    ),
                )
                unlink(files.get(key))
            except Exception as err:
                log.exception(err)
                raise err
        zip_file.close()


class SicapHelper(object):
    """
    Classe suporte para construção de arquivos.
    Os métodos add_act, add_admission, add_employee, add_possession, add_workplace, add_jobposition, add_laws
    são para adicionar os pks dos objetos que estão sendo mencionados em qualquer um dos arquivos.
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
        directory_tmp = SicapHelper._cache_path()
        if not os.path.exists(directory_tmp):
            os.mkdir(directory_tmp)
        return directory_tmp

    def __init__(self, **kwargs):
        self.year = int(kwargs.get("year", None))
        self.months = kwargs.get("months", None)
        if not self.year or not self.months:
            raise Exception("Preencha os parâmetros mês e ano!")
        self.file_name = kwargs.get("file_name", SicapHelper._file_name())
        self.date_start, self.date_end = self.date_start_and_end()
        self.day_start = self.date_start.day
        self.month_start = self.date_start.month
        self.day_end = self.date_end.day
        self.month_end = self.date_end.month
        self.unity_employee = {}  # cpf: count
        self._acts = []
        self._fires = []
        self._employees = []
        self._possessions = []
        self._workplaces = []
        self._job_positions = []
        self._laws = []

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
            "directory": self.directory_tmp(),
        }

    def add_act(self, pk):
        """
        Este método adiciona os pks de atos presentes nos arquivos gerados do período.
        """
        self._acts.append(pk)

    def get_acts(self):
        return list(dict.fromkeys(self._acts))

    def add_employee(self, pk):
        """
        Este método adiciona os pks de servidores presentes nos arquivos gerados do período.
        """
        self._employees.append(pk)

    def get_employees(self):
        return list(dict.fromkeys(self._employees))

    def get_possessions(self):
        return self._possessions

    def add_possession(self, possession):
        """
        Este método adiciona os pks de posses presentes nos arquivos gerados do período.
        """
        if isinstance(possession, MovimentacaoPosse):
            self._possessions.append(possession.pk)
            if hasattr(possession, "desligamento") and possession.desligamento:
                self.add_fires(possession.desligamento)

    def add_fires(self, desligamento):
        """
        Este método adiciona os pks de posses presentes nos arquivos gerados do período.
        """
        if desligamento.data_desligamento <= self.date_end:
            self._fires.append(desligamento.pk)

    def get_workplaces(self):
        return list(dict.fromkeys(self._workplaces))

    def add_workplace(self, pk):
        """
        Este método adiciona os pks de lotações presentes nos arquivos gerados do período.
        """
        self._workplaces.append(pk)

    def add_job_position(self, pk):
        """
        Este método adiciona os pks de cargos presentes nos arquivos gerados do período.
        """
        self._job_positions.append(pk)

    def get_job_positions(self):
        return list(dict.fromkeys(self._job_positions))

    def add_law(self, pk):
        """
        Este método adiciona os pks de leis presentes nos arquivos gerados do período.
        """
        self._laws.append(pk)

    def get_laws(self):
        return list(dict.fromkeys(self._laws))


class BaseSicapFile(Protocol):
    """
    Esta classe é a base para todas as outras classes de protocolo.
    Todas as classes que herdam dessa precisam de um 'verbose_name', que informa ao usuário qual arquivo está sendo processado,
    além de informações e erros.
    """

    def __init__(self, sicap_helper, **kwargs):
        super(BaseSicapFile, self).__init__()
        self.regs = []
        self.global_marker = "Sicap"
        self.feedback = kwargs.get(
            "feedback", (lambda progress_message, progress, **kwargs: False)
        )
        self._file_name = kwargs.get("file_name", "w")
        self._mode_write = kwargs.get("mode_write", "w")
        self.sicap_helper = sicap_helper
        self.task = kwargs.get("task", None)

    def get_records(self):
        """
        Este método retorna os registros a ser gravado no arquivo e gera caso não exista.
        """
        if not self.regs:
            self.make_records()

        return self.regs

    def write_feedback(self, progress=1, message_progress=None):
        message_progress = (
            f"Gerando Arquivo de {self.verbose_name}"
            if not message_progress
            else message_progress
        )
        self.feedback(
            "%(message_progress)s", progress, message_progress=message_progress
        )

    def write_file(self, text):
        """
        Este método cria o cabecalho e dados XML a ser gravados nos arquivos.
        """
        markup = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        self.sicap_helper.write_file(
            markup
            + "<"
            + self.global_marker
            + ">\n"
            + str(text)
            + "</"
            + self.global_marker
            + ">",
            self._file_name,
            mode=self._mode_write,
        )

    def record_add(self, record, instance, custom_msg=None):
        """
        Este método valida o registro de acordo com o layout especificado, notifica o usuário sobre os erros ocorridos
        @return boolean True se o registro é todo válido, False se houver algum erro.
        """
        errors = record.validate()
        if errors:
            print(f"errors: {errors}")
            if custom_msg:
                self.errors_notify(instance, errors, custom_msg=custom_msg)
            else:
                self.errors_notify(instance, errors)
            return False
        else:
            self.regs.append(record)
            return True

    def errors_notify(self, instance, errors, custom_msg=None):
        """
        Este método apenas notifica o usuários sobre erros de forma amigável e legível.
        Utiliza as Tasks para notificar.
        """
        try:
            if errors:
                if self.task:
                    pk = "(%s)" % instance.pk if hasattr(instance, "pk") else ""
                    msg = (
                        f"{self.verbose_name} - {instance} {pk} - Erro(s):\n"
                        if not custom_msg
                        else custom_msg
                    )
                    for err in errors:
                        msg += f"{err}\n"
                    self.task.info(msg=f"{msg}", type_of=3)
                else:
                    print(
                        instance.pk if hasattr(instance, "pk") else "", instance, errors
                    )
        except Exception as err:
            log.exception(err)
            raise err

    @classmethod
    def format_number_law(cls, number, max_length=6):
        if number:
            number = cls.format_max_lenght(number=number, max_length=max_length)
            if cls.isdigit(number) and int(number) == 0:
                # Caso o numero do ato seja 0 deve-se colocar 999999 conforme ato do tce
                number = "999999"
        else:
            number = ""
        number = cls.isdigit(number)
        return number

    @classmethod
    def publication_is_valid(cls, publication):
        """
        Este método verifica se a publicação possui numero e ano preenchidos de forma correta.
        @return boolean True se a publicação é válida, False se não.
        """
        valid = False
        if (
            publication
            and publication.numero
            and publication.ano
            and BaseSicapFile.format_number_law(publication.numero)
        ):
            if publication.numero.isdecimal():
                valid = True
        return valid

    @classmethod
    def isdigit(cls, number):
        if number and not number.isdigit():
            number = False
        return number

    @classmethod
    def only_digit(cls, number):
        """
        Este método remove caracteres que não forem numeros.
        """
        import re

        return re.sub("[^0-9]", "", number)

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

    def build(self):
        self.get_records()
        text = ""
        for r in self.regs:
            text += str(r)
        self.write_feedback(progress=100)
        self.write_file(text)


class BaseSicapRecord(Record):
    """
    Este classe é a base para todas as outras que formatam os registros de acordo com o layout.
    Toda classe que é herdada deve devinir uma constante '_marker' que é o nome da tag global do arquivo XML
    """

    def __str__(self):
        """
        Este metodo retorna o registro formatado para o formato XML.
        """
        linha = ""

        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                pass
            else:
                # log.debug('KEY: %s' % k)
                if Record.is_empty(self.info[k]) and self.is_required(k):
                    line = self.__class__.get_required_value(
                        label=self._protocol[self.layout][k]["label"],
                        required=self._protocol[self.layout][k].get("required", 0),
                    )
                else:
                    line = self.prepare(k)
                try:
                    if not Record.is_empty(self.info[k]):
                        _open_separator = (
                            "<" + self._protocol[self.layout][k]["label"] + ">"
                        )
                        _close_separator = (
                            "</" + self._protocol[self.layout][k]["label"] + ">\n"
                        )
                        _marker_open = "<" + self._marker + ">"
                        _marker_close = "</" + self._marker + ">\n"
                        if linha:
                            linha += (
                                _open_separator + line + _close_separator
                                if not isinstance(line, str)
                                else _open_separator + str(line) + _close_separator
                            )
                        else:
                            linha += _marker_open + "\n"
                            linha += (
                                _open_separator + line + _close_separator
                                if not isinstance(line, str)
                                else _open_separator + str(line) + _close_separator
                            )
                except Exception as e:
                    log.exception(e)

        return linha + _marker_close

    def validate(self):
        error = []
        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                pass
            else:
                if type(self.info[k]) == dict:
                    if self.info[k].get("error", False):
                        error.append(self.info[k]["error"])
                elif Record.is_empty(self.info[k]) and self.is_required(k):
                    verbose = (
                        self._protocol[self.layout][k].get("verbose")
                        if self._protocol[self.layout][k].get("verbose")
                        else ""
                    )
                    if verbose:
                        error.append(
                            "%s | %s - Preenchimento obrigatório"
                            % (self._protocol[self.layout][k]["label"], verbose)
                        )
                    else:
                        error.append(
                            "%s - Preenchimento obrigatório"
                            % self._protocol[self.layout][k]["label"]
                        )
                else:
                    try:
                        line = self.prepare(k)
                    except ValueError:
                        error.append(
                            f'{self._protocol[self.layout][k]["label"]}: {self.info[k]} - Erro de preenchimento, verificar layout'
                        )
                    except Exception as err:
                        error.append(
                            f'{self._protocol[self.layout][k]["label"]}: {self.info[k]}.'
                        )
                        print(err)
        return error


class DispatchRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "InfoRemessa"


class DispatchFile(BaseSicapFile):

    verbose_name = "Remessa"

    def make_records(self):

        organ = AdministrativeUnitFile.get_administrative_unit()
        self.write_feedback()
        self.write_feedback(progress=((100.0 * float(1)) / float(1)))

        record = DispatchRecord(
            "dispatch",
            idUnidadeGestora=organ.pessoa_juridica.cnpj,
            exercicio=self.sicap_helper.date_start.year,
            remessa=self.sicap_helper.date_start.month,
            data=datetime.now().strftime("%Y-%m-%d"),
        )
        self.record_add(record, organ)

        return self.regs


class AdministrativeUnitFile(BaseSicapFile):

    verbose_name = "Unidades Administrativas"

    def make_records(self):

        organ = self.get_administrative_unit()

        self.write_feedback()
        self.write_feedback(progress=((100.0 * float(1)) / float(1)))

        self.regs.append(
            AdministrativeUnitRecord(
                "administrative_unit",
                codigoUnidadeAdministrativa=organ.pk,
                sigla=organ.sigla,
                nome=organ.nome,
                cnpj=organ.pessoa_juridica.cnpj,
            )
        )

        return self.regs

    @classmethod
    def get_administrative_unit(cls):
        return UnidadeAdministrativa.objects.filter(main=True, ativo=True).first()

    @classmethod
    def get_administravite_unit_by_choice(cls, choice):
        return UnidadeAdministrativa.objects.filter(veiculo_publicacao=choice).last()


class ActFile(BaseSicapFile):

    verbose_name = "Atos"

    def make_records(self):

        if self.regs:
            return self.regs

        query = self.get_query()
        count = 1
        total = query.count()
        self.write_feedback()

        for publication in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            law_year = ""
            local_publication = ""
            date_publication = ""
            if BaseSicapFile.publication_is_valid(publication):
                law_year = "%s%s" % (
                    BaseSicapFile.format_number_law(publication.numero),
                    publication.ano,
                )
            if publication.veiculo_publicacao:
                local_publication = publication.get_veiculo_publicacao_display()
            if publication.data_publicacao:
                date_publication = publication.data_publicacao.strftime("%Y-%m-%d")
            type_act = self.parse_act_type(publication.tipo)
            publication_organ = (
                AdministrativeUnitFile.get_administravite_unit_by_choice(
                    publication.veiculo_publicacao
                )
            )
            publication_organ = (
                publication_organ.pessoa_juridica.cnpj
                if publication_organ and publication_organ.pessoa_juridica
                else ""
            )
            record = ActRecord(
                "act",
                numeroAto=law_year,
                cnpjUgPublicacao=publication_organ,
                veiculoPublicacao=local_publication,
                dataPublicacao=date_publication,
                tipoAto=type_act,
            )
            if not self.on_list(record):
                self.record_add(record, publication)

        return self.regs

    def on_list(self, record):
        """
        Verifica se já existe o ato dentro de self.regs
        """
        for reg in self.regs:
            if reg.get("numeroAto") == record.get("numeroAto") and reg.get(
                "tipoAto"
            ) == record.get("tipoAto"):
                return True
        return False

    def get_query(self, filter_=None):
        return Publicacao.objects.filter(pk__in=self.sicap_helper.get_acts())

    @classmethod
    def parse_act_type(cls, value):

        parser_act_type = {
            1: 10,  # Ato
            2: 2,  # Decreto
            3: 4,  # Portaria
            5: 7,  # Despacho
            11: 1,  # Lei
            14: 3,  # Decreto Legislativo
            15: 5,  # Resolução
            16: 6,  # Circular
            17: 8,  # Processo
        }

        return parser_act_type.get(value, 99)


class LawFile(BaseSicapFile):
    """
    Gerador de de arquivos de Leis
    """

    verbose_name = "Lei"

    def make_records(self):

        query = self.get_query()
        total = query.count()
        count = 1

        for publication in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            law_year = ""
            local_publication = ""
            date_publication = ""
            type_act = ""
            if BaseSicapFile.publication_is_valid(publication):
                law_year = "%s%s" % (
                    BaseSicapFile.format_number_law(publication.numero),
                    publication.ano,
                )
                type_act = ActFile.parse_act_type(publication.tipo)

            if publication.veiculo_publicacao:
                local_publication = publication.get_veiculo_publicacao_display()
            if publication.data_publicacao:
                date_publication = publication.data_publicacao.strftime("%Y-%m-%d")
            record = LawRecord(
                "law",
                numeroLei=law_year,
                numeroAto=law_year,
                tipoAto=type_act,
                dataPublicacao=date_publication,
                veiculoPublicacao=local_publication,
                ementa=(
                    re.sub("[\W_]+", "", publication.document)
                    if publication.document
                    else " "
                ),
            )
            if not self.on_list(record):
                if self.record_add(record, publication):
                    self.sicap_helper.add_act(publication.pk)

    def on_list(self, record):
        for reg in self.regs:
            if reg.get("numeroLei") == record.get("numeroLei"):
                return True
        return False

    def get_query(self):
        return Publicacao.objects.filter(pk__in=self.sicap_helper.get_laws())


class JobPositionFile(BaseSicapFile):

    verbose_name = "Cargos"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for job_position_chart in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            law_year = JobPositionFile.get_job_position_chart_law_year(
                job_position_chart
            )
            bond_type = self.parser_table_sicap(job_position_chart.cargo.tipo_lei_cargo)
            scholarity = self.parser_scholarity(job_position_chart.nivel_escolaridade)
            salary_initial = self.get_salary_initial(job_position_chart.cargo)
            salary_final = (
                self.get_salary_final(job_position_chart.cargo)
                if job_position_chart.cargo.tipo_lei_cargo == "EF"
                else salary_initial
            )
            quantity = self.get_jobs_quantity(job_position_chart)
            nature_job = self.get_nature_job(job_position_chart)
            weekly_workday = self.get_workload(job_position_chart)
            classe = self.get_class(job_position_chart)
            code_tce = (
                job_position_chart.cargo.code_tce
                if job_position_chart.cargo.code_tce
                else ""
            )

            if job_position_chart.cargo.tipo_lei_cargo == "AC":
                code_tce = 11937  # cargo tce para requisitados
                law_year = ""

            record = JobPositionRecord(
                "job_position",
                codigoCargo=(
                    job_position_chart.cargo.pk if job_position_chart.cargo else ""
                ),
                numeroLei=law_year,
                numeroAto=law_year,
                nomeCargo="%s" % job_position_chart,
                atribuicaoCargo="%s" % "não existente",
                idCargoNome=code_tce,
                regimeJuridico=1,
                vinculoCargo=bond_type,
                jornadaSemanal=weekly_workday,
                quantidadeVagas=quantity,
                natureza=nature_job,
                vencimentoInicial=salary_initial,
                vencimentoFinal=salary_final,
                escolaridade=scholarity,
                classe=classe,
            )
            if self.record_add(record, job_position_chart.cargo):
                if job_position_chart.publicacao_criacao and law_year:
                    self.sicap_helper.add_act(job_position_chart.publicacao_criacao.pk)
                    self.sicap_helper.add_law(job_position_chart.publicacao_criacao.pk)
        req_job = self.get_requested_job_position()
        self.record_add(
            JobPositionRecord(
                "job_position",
                codigoCargo=req_job.pk,
                nomeCargo="%s" % req_job.nome,
                atribuicaoCargo="%s" % "não existente",
                idCargoNome=11937,
                regimeJuridico=1,
                vinculoCargo=req_job.vinculo,
                jornadaSemanal=weekly_workday,
                quantidadeVagas=1,
                natureza=req_job.natureza,
                escolaridade=req_job.escolaridade,
                classe=req_job.classe,
            ),
            req_job,
        )

    def get_query(self):
        return JobPositionFile.get_job_position_chart(self.sicap_helper)

    def get_jobs_quantity(self, job):
        return job.quantidade_vagas if job.quantidade_vagas else ""

    def get_workload(self, job):
        return (
            self.parser_workload_sicap(job.carga_horaria) if job.carga_horaria else ""
        )

    def get_nature_job(self, job):
        nature_job = 1
        if job.military:
            nature_job = "9"
        elif job.teacher:
            nature_job = "3"
        elif job.health:
            nature_job = "2"

        return nature_job

    def get_class(self, job):
        if job.military:
            return "2"
        else:
            return "1"

    def parser_table_sicap(self, type):
        # Tipo do cargo
        parser_table_sicap = {"EF": 1, "CM": 3, "FC": 3, "AC": 1}

        return parser_table_sicap.get(type, "")

    def parser_scholarity(self, type):
        parser_scholarity = {1: 3, 2: 4, 3: 5, 4: 2}

        return parser_scholarity.get(type, 1)

    def parser_workload_sicap(self, workload):
        parser_workload_sicap = {20: 1, 30: 2, 35: 3, 40: 4, 60: 5, 88: 6, 99: 9}
        return parser_workload_sicap.get(workload, 3)

    def get_salary_initial(self, cargo):
        salary = 0.0
        percentage = 0.0
        try:
            if cargo.tipo_lei_cargo != "AC":
                reference = cargo.get_salarios()[0][1]
                salary = float(reference.valor) + float(reference.gratificacao)
                if (
                    not reference.valor
                    and not reference.gratificacao
                    and reference.gratificacao_membro
                ):
                    if reference.gratificacao_membro > percentage:
                        percentage = reference.gratificacao_membro
        except Exception as err:
            log.exception(err)
            return {"error": "Não foi encontrado salário inicial para o cargo"}
        return salary if salary > 0 else (percentage if percentage > 0 else "")

    def get_salary_final(self, cargo):
        salary = 0.0
        percentage = 0.0
        try:
            if cargo.tipo_lei_cargo != "AC":
                for sl in cargo.get_salarios():
                    reference = float(sl[1].valor) + float(sl[1].gratificacao)
                    if reference > salary:
                        salary = reference
                    if (
                        not sl[1].valor
                        and not sl[1].gratificacao
                        and sl[1].gratificacao_membro
                    ):
                        if sl[1].gratificacao_membro > percentage:
                            percentage = sl[1].gratificacao_membro

        except Exception as err:
            log.exception(err)
            return {"error": "Não foi encontrado salário final para o cargo"}
        return salary if salary > 0 else (percentage if percentage > 0 else "")

    @classmethod
    def get_job_position_chart(cls, sicap_helper=None):
        if sicap_helper:
            pks = sicap_helper.get_job_positions()
        else:
            pks = []
        _filter = Q(
            Q(quantidade_vagas__gt=0)
            & Q(cargo__indicativo__in=["S", "M"])
            & Q(cargo__tipo_lei_cargo__in=("EF", "CM", "FC"))
        ) | Q(cargo__pk__in=pks)

        return CargoQuadro.objects.filter(_filter).order_by("cargo__nome").distinct()

    @classmethod
    def get_code_job_position(cls, job_position_chart):
        code_job_position = ""
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

    @classmethod
    def get_job_position_chart_law_year(cls, job_position_chart):
        law_year = ""
        if job_position_chart and BaseSicapFile.publication_is_valid(
            job_position_chart.publicacao_criacao
        ):
            law_year = "%s%s" % (
                BaseSicapFile.format_number_law(
                    job_position_chart.publicacao_criacao.numero
                ),
                job_position_chart.publicacao_criacao.ano,
            )
        return law_year

    @classmethod
    def get_requested_job_position(cls):
        from collections import namedtuple

        Job = namedtuple("Job", "pk nome regime vinculo natureza escolaridade classe")
        job_requested = Job(
            pk=5001,
            nome="REQUISITADO",
            vinculo=1,
            regime=1,
            natureza=1,
            escolaridade=5,
            classe=1,
        )
        return job_requested


class WorkplaceFile(BaseSicapFile):

    verbose_name = "Lotações"

    def make_records(self):
        query = self.get_query()
        total = query.count()
        count = 1
        organ = AdministrativeUnitFile.get_administrative_unit()
        self.write_feedback()
        for workplace in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            record = WorkplaceRecord(
                "workplace",
                codigoLotacao=workplace.pk,
                codigoUnidadeAdministrativa=organ.pk,
                sigla=workplace.sigla,
                nome=workplace.nome,
            )
            self.record_add(record, workplace)

        return self.regs

    def get_query(self):
        q_filter = Q(organograma=True) | Q(pk__in=self.sicap_helper.get_workplaces())
        return Lotacao.objects.filter(q_filter)


class EmployeeFile(BaseSicapFile):

    verbose_name = "Servidores"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for employee in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
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
                birthdate = (
                    employee.pessoa_fisica.data_nascimento.strftime("%Y-%m-%d")
                    if employee.pessoa_fisica.data_nascimento
                    else ""
                )
                title_number = title_number.strip()
                record = EmployeeRecord(
                    "employee",
                    cpfServidor=employee.pessoa_fisica.cpf,
                    nome=employee.pessoa_fisica.nome,
                    rg=rg,
                    pcd=0,
                    rgExpedidor=organ_expedition,
                    rgExpedicao=date_rg,
                    # carteiraTrabalho=ctps if self.isdigit(ctps) else '',
                    numeroPisPasep=pis,
                    # carteiraTrabalhoSerie=ctps_series if self.isdigit(ctps_series) else '',
                    tituloEleitor=title_number,
                    tituloEleitorZona=title_zone,
                    tituloEleitorSecao=title_section,
                    tituloEleitorUf=title_state,
                    cnh=cnh,
                    dataNascimento=birthdate,
                    siglaPais="BR",
                    siglaEstado=state,
                    codigoMunicipio=locality,
                    escolaridade=self.get_level_education(employee),
                    sexo=self.get_gender(employee),
                    estadoCivil=self.get_civil_state(employee),
                    cpfConjuge="",
                    dataNascimentoConjuge="",
                    cpfMae="",
                    nomeMae=employee.pessoa_fisica.nome_mae,
                    dataNascimentoMae="",
                )
                self.record_add(record, employee)
            except Exception as err:
                raise Exception(err)

        return self.regs

    def get_query(self):

        query_filter = Q(pk__in=self.sicap_helper.get_employees())
        return (
            Servidor.objects.filter(
                type_by_possession__in=EmployeeFile.get_allowed_possessions()
            )
            .filter(query_filter)
            .order_by("pessoa_fisica__nome")
        )

    @classmethod
    def get_civil_state(cls, employee):
        parser_table_civil_state = {
            1: 1,  # solteiro
            2: 3,  # casado
            3: 5,  # viúvo
            4: 4,  # divorciado - separado judicialmente
            5: 4,  # divorciado
            6: 2,  # uniao estável
        }
        return parser_table_civil_state.get(employee.pessoa_fisica.estado_civil, "")

    @classmethod
    def get_gender(cls, employee):
        return 1 if employee.pessoa_fisica.sexo == "M" else 2

    @classmethod
    def get_level_education(cls, employee):
        parser_table_education = {
            1: 1,  # analfabeto
            2: 2,  # alfabetizado
            3: 3,  # fundamental
            4: 3,  # fundamental
            5: 4,  # medio
            6: 4,  # medio
            7: 5,  # superior
            8: 5,  # superior
            9: 6,  # pos
            10: 7,  # mestrado
            11: 8,  # doutorado
        }
        return parser_table_education.get(employee.pessoa_fisica.grau_instrucao, "")

    @classmethod
    def get_data_nationality(cls, employee):
        country = ""
        locality = ""
        state = ""
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
            if employee.pessoa_fisica.municipio_naturalidade.ibge:
                locality = employee.pessoa_fisica.municipio_naturalidade.ibge
        return country, locality, state

    @classmethod
    def person_documents_data(cls, employee):
        pis = ""
        cnh = ""
        ctps = ""
        ctps_series = ""
        title_number = ""
        title_zone = ""
        title_state = ""
        title_section = ""
        for document in Documento.objects.filter(
            naturalpersons=employee.pessoa_fisica.pk
        ):
            if document.tipo_documento == 6:
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
                        if doc_specific.valor:
                            locality = Localidade.objects.filter(
                                pk=int(doc_specific.valor)
                            )
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
        rg = ""
        date = ""
        organ_expedition = ""
        if employee.pessoa_fisica.rg:
            rg = employee.pessoa_fisica.rg
        if employee.pessoa_fisica.rg_data_expedicao:
            date = employee.pessoa_fisica.rg_data_expedicao.strftime("%Y-%m-%d")
        if employee.pessoa_fisica.rg_orgao:
            organ_expedition = employee.pessoa_fisica.rg_orgao
        elif employee.pessoa_fisica.rg_uf and employee.pessoa_fisica.rg_uf.sigla:
            organ_expedition = employee.pessoa_fisica.rg_uf.sigla
        return rg, date, organ_expedition

    @classmethod
    def get_allowed_possessions(cls):
        return [
            "EFE",
            "ECM",
            "EFC",
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "CMS",
            "REQ",
            "RCM",
            "RFC",
        ]

    @classmethod
    def get_exclude_employeers(cls):
        """
        Este método exclui servidores requisitados que recebem apenas auxilio pelo MPE.
        """
        possessions = [
            "EFE",
            "ECM",
            "EFC",
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "CMS",
            "REQ",
            "RCM",
            "RFC",
        ]
        return (
            pk
            for pk in MovimentacaoPosse.objects.exclude(
                servidor__type_by_possession__in=possessions
            ).values_list("servidor__pk", flat=True)
        )

    @classmethod
    def get_workplace_by_employee(cls, employee, sicap_helper):
        workplace = ""
        if employee.workplace_by_date(sicap_helper.date_start):
            return employee.workplace_by_date(sicap_helper.date_start)
        elif employee._workplace_by_date_employee(
            date=sicap_helper.date_start, main=False
        ):
            return employee._workplace_by_date_employee(
                date=sicap_helper.date_start, main=False
            )
        elif employee.get_workplace_only().exists():
            return employee.get_workplace_only().first()
        else:
            return Lotacao.objects.filter(sigla="PGJ-TO").last()

    @classmethod
    def get_admission_by_period(cls, sicap_helper, employee):
        possession = employee.get_posses_ativas(
            sicap_helper.date_start, sicap_helper.date_end
        )
        if possession:
            if (
                possession.filter(quadro__cargo__tipo_lei_cargo="EF").exists()
                and not possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists()
            ):
                return possession.filter(quadro__cargo__tipo_lei_cargo="EF").first()
            elif (
                possession.filter(requestmove__isnull=False).exists()
                and not possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists()
            ):
                return possession.filter(requestmove__isnull=False).first()
            elif possession.filter(quadro__cargo__tipo_lei_cargo="CM"):
                return possession.filter(quadro__cargo__tipo_lei_cargo="CM").first()
        if not possession:
            possession = employee.posses.exclude(
                quadro__cargo__tipo_lei_cargo__in=["FC", "EL"]
            ).order_by("-data_exercicio")
            if (
                possession.filter(quadro__cargo__tipo_lei_cargo="EF").exists()
                and not possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists()
            ):
                return possession.filter(quadro__cargo__tipo_lei_cargo="EF").first()
            elif (
                possession.filter(requestmove__isnull=False).exists()
                and not possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists()
            ):
                return possession.filter(requestmove__isnull=False).first()
            elif possession.filter(quadro__cargo__tipo_lei_cargo="CM"):
                return possession.filter(quadro__cargo__tipo_lei_cargo="CM").first()

        return possession

    @classmethod
    def employee_job_act(cls, sicap_helper, employee):
        """Este método retorna dados do ato de admissão, cargo do periodo, e pk da admissão.
        Recebe o Sicap Helper e um Sevidor.

        Retorna:
            - Ato de admissão formatado para o Sicap, PK da publicação e tipo do ato.
                * Para requisitados sem cargo em comissão retorna o ato referente a requisição
            - PK do cargo do periodo
            - PK da posse

        """
        act = ""
        act_pk = ""
        act_type = 99
        job_code = ""
        possession = None

        try:
            possession = employee.get_posses_ativas(
                sicap_helper.date_start, sicap_helper.date_end
            )
            if not possession:
                possession = employee.posses.exclude(
                    quadro__cargo__tipo_lei_cargo__in=("FC", "EL")
                ).order_by("-data_exercicio")

            if possession.filter(quadro__cargo__tipo_lei_cargo="EF").exists():
                ef = possession.filter(quadro__cargo__tipo_lei_cargo="EF").first()
                if BaseSicapFile.publication_is_valid(ef.publicacao_movimentacao):
                    act = "%s%s" % (
                        BaseSicapFile.format_number_law(
                            ef.publicacao_movimentacao.numero
                        ),
                        ef.publicacao_movimentacao.ano,
                    )
                    act_pk = ef.publicacao_movimentacao.pk
                    act_type = ActFile.parse_act_type(ef.publicacao_movimentacao.tipo)
                else:
                    if (
                        ef.publicacao_movimentacao
                        and type(ef.publicacao_movimentacao.numero) == str
                    ):
                        act = "999999" + str(ef.publicacao_movimentacao.ano)
                    else:
                        act = {
                            "error": f"Número do Ato Inválido - {ef.publicacao_movimentacao}"
                        }

                possession = ef
                job_code = ef.quadro.cargo.pk if ef.quadro and ef.quadro.cargo else ""
            elif (
                possession.filter(requestmove__isnull=False).exists()
                and not possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists()
            ):
                ac = employee.get_requestmove_at(
                    sicap_helper.date_start, sicap_helper.date_end
                ).last()
                if not ac:
                    ac = (
                        RequestMove.objects.filter(servidor=employee)
                        .exclude(data_exercicio__gt=sicap_helper.date_end)
                        .order_by("-data_desligamento")
                        .last()
                    )
                if ac:
                    if BaseSicapFile.publication_is_valid(ac.publicacao_movimentacao):
                        act = "%s%s" % (
                            BaseSicapFile.format_number_law(
                                ac.publicacao_movimentacao.numero
                            ),
                            ac.publicacao_movimentacao.ano,
                        )
                        act_pk = ac.publicacao_movimentacao.pk
                        act_type = ActFile.parse_act_type(
                            ac.publicacao_movimentacao.tipo
                        )
                    else:
                        if ac.publicacao_movimentacao:
                            act = {
                                "error": f"Número do Ato Inválido - {ac.publicacao_movimentacao}"
                            }
                        else:
                            act = {"error": f"Posse não possui ato cadastrado. {ac}"}
                    job_code = JobPositionFile.get_requested_job_position().pk
                    possession = ac
                else:
                    error_msg = {"error": "Requisição não cadastrada"}
                    act_pk = error_msg
                    act_type = error_msg
                    possession = error_msg
                    job_code = error_msg
            elif possession.filter(quadro__cargo__tipo_lei_cargo="CM").exists():
                cm = possession.filter(quadro__cargo__tipo_lei_cargo="CM").first()
                if BaseSicapFile.publication_is_valid(cm.publicacao_movimentacao):
                    act = "%s%s" % (
                        BaseSicapFile.format_number_law(
                            cm.publicacao_movimentacao.numero
                        ),
                        cm.publicacao_movimentacao.ano,
                    )
                    act_pk = cm.publicacao_movimentacao.pk
                    act_type = ActFile.parse_act_type(cm.publicacao_movimentacao.tipo)
                else:
                    act = {
                        "error": f"Número do Ato Inválido - {cm.publicacao_movimentacao}"
                    }
                possession = cm
                job_code = cm.quadro.cargo.pk if cm.quadro and cm.quadro.cargo else ""
        except Exception as err:
            log.exception(employee)
            log.exception(err)

        return act, job_code, act_pk, possession, act_type


class AdmissionFile(BaseSicapFile):

    verbose_name = "Admissões"

    def __init__(self, sicap_helper, **kwargs):
        super(AdmissionFile, self).__init__(sicap_helper, **kwargs)
        self.commissions = []

    def make_records(self):
        query_original = self.get_query().distinct()
        total = query_original.count()
        count = 1
        self.write_feedback()

        for instance in query_original.order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        ):
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            self.add_admission(instance)

        query = (
            MovimentacaoPosse.objects.exclude(
                pk__in=(pk for pk in query_original.values_list("pk", flat=True))
            )
            .filter(pk__in=self.commissions)
            .filter(
                servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions()
            )
        )
        total = query.count()
        count = 1
        self.write_feedback()
        for instance in query.order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        ):
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            self.add_admission(instance)

    def add_admission(self, instance):
        if (
            not (
                instance.servidor.member_type_by_possession
                and instance.servidor.posses.count() > 1
                and instance.movimentacaoposse.quadro.cargo.tipo_lei_cargo != "CM"
            )
            or instance.pk in self.sicap_helper.get_possessions()
        ):

            admission_act = ""
            admission_date = ""
            admission_date_exercise = ""

            type_adm = self.parser_table_type_adm(
                instance.quadro.cargo.tipo_lei_cargo if instance.quadro else "AC"
            )

            job_position_code = instance.quadro.cargo.pk

            workplace = EmployeeFile.get_workplace_by_employee(
                instance.servidor, self.sicap_helper
            )

            organ_origin = ""
            organ_remuneration = ""
            socialsecurity_required = ""
            socialsecurity_cnpj_required = ""
            publicconcurrence_number = ""
            act = ""

            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                admission_date = (
                    instance.data_posse.strftime("%Y-%m-%d")
                    if instance.data_posse
                    else ""
                )
                admission_date_exercise = (
                    instance.data_exercicio.strftime("%Y-%m-%d")
                    if instance.data_exercicio
                    else ""
                )
                act = instance.publicacao_movimentacao

            if instance.quadro and instance.quadro.cargo.tipo_lei_cargo == "EF":
                publicconcurrence_number = self.get_publicconcurrency(instance.servidor)

            if hasattr(instance, "requestmove"):
                job_position_code = JobPositionFile.get_requested_job_position().pk
                request_move = instance.requestmove
                if request_move.organ_origin:
                    if request_move.organ_origin.pessoa_juridica:
                        organ_origin = request_move.organ_origin.pessoa_juridica.cnpj
                    else:
                        organ_origin = {"error": "Orgão de origem não cadastrado"}
                organ_remuneration = self.get_onus_by_ac(request_move, organ_origin)
                ssc = instance.servidor.get_socialsecurity_by_validity(
                    range=NewDateRange(
                        self.sicap_helper.date_start, self.sicap_helper.date_end
                    )
                )
                if not ssc:
                    ssc = instance.servidor.get_socialsecurity_by_validity()
                socialsecurity_required = (
                    1 if ssc and ssc.get_regime_display() == "RPPS" else 2
                )
                socialsecurity_cnpj_required = (
                    ssc.organ.cnpj if socialsecurity_required == 1 else ""
                )
                admission_date_exercise = (
                    request_move.data_exercicio if request_move.data_exercicio else ""
                )
                admission_date = (
                    request_move.data_exercicio if request_move.data_exercicio else ""
                )
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        request_move.publicacao_movimentacao.numero
                    ),
                    request_move.publicacao_movimentacao.ano,
                )
                act = request_move.publicacao_movimentacao

            if instance.quadro and instance.quadro.cargo.tipo_lei_cargo == "CM":
                have_comission = self.is_ac_with_cm(instance.servidor)
                if have_comission:
                    self.commissions.append(have_comission)

            workplace = workplace.lotacao.pk if workplace and workplace.lotacao else ""
            obs = ""
            if admission_act[:-4] == "999999":
                obs = "Nos atos administrativos editados à época não haviam numeração de documentos"

            record = AdmissionRecord(
                "admission",
                matriculaServidor=instance.servidor.matricula,
                codigoLotacao=workplace,
                numeroAto=admission_act,
                tipoAto=ActFile.parse_act_type(act.tipo) if act else "",
                cpfServidor=instance.servidor.pessoa_fisica.cpf,
                tipoAdmissao=type_adm,
                numeroEdital=publicconcurrence_number,
                numeroInscricao="",
                codigoCargo=job_position_code,
                prorrogacaoContrato="",
                contratoSuspenso="",
                dataPosse=admission_date,
                dataExercicio=admission_date_exercise,
                dataInicio=admission_date_exercise,
                dataFim="",
                contratoValor="",
                contratoMotivo="",
                cnpjOrgaoOrigemCedido=organ_origin,
                cessaoCnpjOrgaoRemuneracao=organ_remuneration,
                efetivoEmpregoPublico="",
                formaEmpregoPublico="",
                previdenciaRequisitado=socialsecurity_required,
                cnpjRppsRequisitado=socialsecurity_cnpj_required,
                observacao=obs,
            )
            if self.record_add(record, instance):
                if job_position_code:
                    self.sicap_helper.add_job_position(job_position_code)
                if act:
                    self.sicap_helper.add_act(act.pk)
                self.sicap_helper.add_employee(instance.servidor.pk)
                if workplace:
                    self.sicap_helper.add_workplace(workplace)

    def is_ac_with_cm(self, employee):
        ac = employee.get_requestmove_at(
            self.sicap_helper.date_start, self.sicap_helper.date_end
        ).last()
        if not ac:
            ac = (
                RequestMove.objects.filter(servidor=employee)
                .exclude(data_exercicio__gt=self.sicap_helper.date_end)
                .order_by("-data_desligamento")
                .last()
            )

        return ac.pk if ac else None

    def get_query(self):
        filter_exclude = Q(servidor__pk__in=EmployeeFile.get_exclude_employeers())
        filter_possession = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
            & ~Q(quadro__cargo__tipo_lei_cargo__in=("FC", "EL"))
            & ~Q(my_type="movimentacaoposse", quadro__cargo__tipo_lei_cargo="AC")
        ) | Q(pk__in=self.sicap_helper.get_possessions())

        query = MovimentacaoPosse.objects.filter(filter_possession)
        return query.exclude(filter_exclude)

    def get_publicconcurrency(self, employee):
        error = {"error": f"Dados do concurso obrigatório"}
        query = (
            MovimentacaoPosse.objects.exclude(public_concurrence=None)
            .filter(servidor=employee)
            .last()
        )
        return (
            query.public_concurrence.number_tce
            if query and query.public_concurrence
            else error
        )

    def get_onus_by_ac(self, possession=None, origin=None):
        if possession and origin and possession.onus:
            return (
                origin
                if possession.onus == 1
                else AdministrativeUnitFile.get_administrative_unit().pessoa_juridica.cnpj
            )
        else:
            return {"error": f"Dados do onus obrigatório"}

    def parser_table_type_adm(self, type):
        parser_table_type_adm = {"EF": 1, "CM": 2, "EL": 5, "ES": 6, "AC": 8}

        return parser_table_type_adm.get(type, "")


class DismissalRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Desligamento"


class DismissalFile(BaseSicapFile):

    verbose_name = "Desligamento"

    def make_records(self):
        query = self.get_query()
        total = query.count()
        count = 1
        self.write_feedback()

        for instance in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            admission_act = ""
            admission_act_type = ""
            if instance.movimentacao_posse and BaseSicapFile.publication_is_valid(
                instance.movimentacao_posse.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.movimentacao_posse.publicacao_movimentacao.numero
                    ),
                    instance.movimentacao_posse.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.movimentacao_posse.publicacao_movimentacao.tipo
                )
            dismissal_act = ""
            dismissal_act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                dismissal_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                dismissal_act_type = ActFile.parse_act_type(
                    instance.publicacao_movimentacao.tipo
                )
            log.debug(instance.servidor)

            if hasattr(instance.movimentacao_posse, "requestmove"):
                job_position_code = JobPositionFile.get_requested_job_position().pk
            elif instance.movimentacao_posse and instance.movimentacao_posse.quadro:
                job_position_code = instance.movimentacao_posse.quadro.cargo.pk
            elif instance.tipo_desligamento in (21, 13):  # fim tsve
                job_position_code = 5001

            type_dism = self.parser_type_dism(
                instance.tipo_desligamento if instance.tipo_desligamento else 0
            )
            date_dismissal = instance.data_desligamento.strftime("%Y-%m-%d")

            record = DismissalRecord(
                "dismissal",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargo=job_position_code,
                numeroAto=dismissal_act,
                tipoDesligamento=type_dism,
                dataDesligamento=date_dismissal,
                tipoAto=dismissal_act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if instance.movimentacao_posse:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.movimentacao_posse)

                    if instance.movimentacao_posse.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.movimentacao_posse.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):
        q_filter = Q(
            Q(data_desligamento__gte=self.sicap_helper.date_start)
            & Q(data_desligamento__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
            & ~Q(tipo_desligamento=12)
            & ~Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo__in=("FC", "EL"))
            & ~Q(
                movimentacao_posse__my_type="movimentacaoposse",
                movimentacao_posse__quadro__cargo__tipo_lei_cargo="AC",
            )
        ) | Q(pk__in=self.sicap_helper._fires)

        filter_exclude = Q(servidor__pk__in=EmployeeFile.get_exclude_employeers())

        return (
            MovimentacaoDesligamento.objects.filter(q_filter)
            .exclude(filter_exclude)
            .distinct()
            .order_by(
                "servidor__pessoa_fisica__nome",
                "publicacao_movimentacao__data_vigencia",
            )
        )

    def parser_type_dism(self, value):

        parser_table_type_dism = {
            1: 1,
            2: 1,
            3: 1,
            4: 2,
            5: 2,
            6: 3,
            7: 4,
            8: 5,
            9: 6,
            10: 7,
            11: 8,
            13: 1,
            14: 2,
            15: 2,
            16: 2,
            17: 2,
            20: 1,
            21: 1,
        }
        return parser_table_type_dism.get(value, "")


class ReadaptationRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Readaptacao"


class ReadaptationFile(BaseSicapFile):

    verbose_name = "Readaptação"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            admission_act = ""
            admission_act_type = ""
            if instance.posse_anterior and BaseSicapFile.publication_is_valid(
                instance.posse_anterior.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.posse_anterior.publicacao_movimentacao.numero
                    ),
                    instance.posse_anterior.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.posse_anterior.publicacao_movimentacao
                )
            act = ""
            act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            job_position_code_adm = ""
            if (
                instance.posse_anterior
                and instance.posse_anterior.quadro
                and instance.posse_anterior.quadro.cargo
            ):
                job_position_code_adm = instance.posse_anterior.quadro.cargo.pk

            record = ReadaptationRecord(
                "readaptation",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargoAdmissao=job_position_code_adm,
                numeroAto=act,
                codigoCargo=(
                    instance.quadro.cargo.pk
                    if instance.quadro and instance.quadro.cargo
                    else 0
                ),
                dataInicio=(
                    instance.data_exercicio.strftime("%Y-%m-%d")
                    if instance.data_exercicio
                    else ""
                ),
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if instance.posse_anterior:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.posse_anterior)

                    if instance.posse_anterior.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.posse_anterior.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):
        filter_ = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & ~Q(quadro__cargo__tipo_lei_cargo="FC")
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoReadaptacao.objects.filter(filter_).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class ReappointmentRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Reconducao"


class ReappointmentFile(BaseSicapFile):

    verbose_name = "Recondução"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            admission_act = ""
            admission_act_type = ""
            if instance.posse_anterior and BaseSicapFile.publication_is_valid(
                instance.posse_anterior.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.posse_anterior.publicacao_movimentacao.numero
                    ),
                    instance.posse_anterior.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.posse_anterior.publicacao_movimentacao
                )
            act = ""
            act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            job_position_code_adm = 0
            if (
                instance.posse_anterior
                and instance.posse_anterior.quadro
                and instance.posse_anterior.quadro.cargo
            ):
                job_position_code_adm = instance.posse_anterior.quadro.cargo.pk

            record = ReappointmentRecord(
                "reappointment",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargoAdmissao=job_position_code_adm,
                numeroAto=act,
                codigoCargo=(
                    instance.quadro.cargo.pk
                    if instance.quadro and instance.quadro.cargo
                    else 0
                ),
                dataExercicio=(
                    instance.data_exercicio.strftime("%Y-%m-%d")
                    if instance.data_exercicio
                    else ""
                ),
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )

            if self.record_add(record, instance):
                if instance.posse_anterior:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.posse_anterior)

                    if instance.posse_anterior.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.posse_anterior.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):
        filter_ = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoReconducao.objects.filter(filter_).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class ReintegrationRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Reintegracao"


class ReintegrationFile(BaseSicapFile):

    verbose_name = "Reintegração"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            admission_act = ""
            admission_act_type = ""
            if instance.posse_anterior and BaseSicapFile.publication_is_valid(
                instance.posse_anterior.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.posse_anterior.publicacao_movimentacao.numero
                    ),
                    instance.posse_anterior.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.posse_anterior.publicacao_movimentacao
                )
            act = ""
            act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            job_position_code_adm = 0
            if (
                instance.posse_anterior
                and instance.posse_anterior.quadro
                and instance.posse_anterior.quadro.cargo
            ):
                job_position_code_adm = instance.posse_anterior.quadro.cargo.pk

            record = ReintegrationRecord(
                "reintegration",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargoAdmissao=job_position_code_adm,
                numeroAto=act,
                codigoCargo=(
                    instance.quadro.cargo.pk
                    if instance.quadro and instance.quadro.cargo
                    else 0
                ),
                dataExercicio=(
                    instance.data_exercicio.strftime("%Y-%m-%d")
                    if instance.data_exercicio
                    else ""
                ),
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if instance.posse_anterior:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.posse_anterior)

                    if instance.posse_anterior.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.posse_anterior.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):
        filter_ = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoReintegracao.objects.filter(filter_).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class RetirementRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Aposentadoria"


class RetirementFile(BaseSicapFile):

    verbose_name = "Aposentadoria"

    def make_records(self):

        parser_yes_no = {1: 1, 2: 0}  # SIM  # NÃO

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            admission_act_type = ""
            admission_act = ""
            if instance.movimentacao_posse and BaseSicapFile.publication_is_valid(
                instance.movimentacao_posse.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.movimentacao_posse.publicacao_movimentacao.numero
                    ),
                    instance.movimentacao_posse.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.movimentacao_posse.publicacao_movimentacao.numero
                )
            retirement_act = ""

            act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                retirement_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)

            job_position_code = (
                instance.movimentacao_posse.quadro.cargo.pk
                if instance.movimentacao_posse
                else ""
            )
            type_dism = self.parser_table_type_ret(instance.tipo_aposentadoria)
            reversion = parser_yes_no.get(instance.reversao, "0")
            date_retirement = instance.data_desligamento.strftime("%Y-%m-%d")

            record = RetirementRecord(
                "retirement",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                numeroAto=retirement_act,
                dataAposentadoria=date_retirement,
                tipoAposentadoria=type_dism,
                reversao=reversion,
                atoReversao="",
                dataReversao="",
                revisao="0",
                compensassaoPrevidenciaria="0",
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
                numeroAtoReversao="",
                tipoAtoReversao="",
                codigoCargo=self.get_job_position(instance.servidor),
                cpfServidor=instance.servidor.pessoa_fisica.cpf,
                cnpjUnidadeGestoraOrigem=AdministrativeUnitFile.get_administrative_unit().pessoa_juridica.cnpj,
            )

            if self.record_add(record, instance):
                if instance.movimentacao_posse:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.movimentacao_posse)

                    if instance.movimentacao_posse.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.movimentacao_posse.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):

        filter_ = Q(
            Q(data_desligamento__gte=self.sicap_helper.date_start)
            & Q(data_desligamento__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoAposentadoria.objects.filter(filter_).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )

    def parser_table_type_ret(self, value):
        parser_table_type_ret = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 8}
        return parser_table_type_ret.get(value, "")

    def get_job_position(self, employee):
        possession = employee.get_posses_ativas(
            self.sicap_helper.date_start, self.sicap_helper.date_end
        ).last()
        if not possession:
            possession = (
                employee.posses.exclude(
                    quadro__cargo__tipo_lei_cargo__in=["FC", "EL", "CM"]
                )
                .order_by("-data_exercicio")
                .first()
            )

        return (
            possession.quadro.cargo.pk
            if possession and possession.quadro and possession.quadro.cargo
            else ""
        )


class LicenseRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Licenca"


class LicenseFile(BaseSicapFile):

    verbose_name = "Licenças"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            act = ""
            act_type = ""
            admission_act_type = ""

            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)

            (
                admission_act,
                job_code,
                admission_act_pk,
                possession,
                admission_act_type,
            ) = EmployeeFile.employee_job_act(self.sicap_helper, instance.servidor)

            record = LicenseRecord(
                "license",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargo=job_code,
                numeroAto=act,
                licencaMotivo=self.parse_license(instance.tipo),
                dataInicio=(
                    instance.data_inicio.strftime("%Y-%m-%d")
                    if instance.data_inicio
                    else ""
                ),
                dataFim=(
                    instance.data_fim.strftime("%Y-%m-%d") if instance.data_fim else ""
                ),
                remunerado=1 if instance.remunerado else 0,
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if possession:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(possession)

                if admission_act_pk:
                    self.sicap_helper.add_act(admission_act_pk)

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def parse_license(self, value):

        table = {
            8: 1,  # Tratamento Saude
            12: 2,  # Maternidade
            11: 3,  # doença pessoa da familia
            13: 4,  # adocao tutoria
            14: 5,  # afastamento conjuge
            15: 6,  # serviço militar
            16: 7,  # atividade politica
            17: 8,  # capacitacao
            19: 9,  # mandato classista
            20: 10,  # outro orgao
            21: 11,  # mandato eletivo
            22: 12,  # estudar
            23: 13,  # missao oficial
            18: 14,  # interesse particular
        }

        return table.get(value, "")

    def get_departure_with_threedays(self):
        q = BaseLicencaAfastamento.objects.annotate(
            days_cache=Count(F("data_fim") - F("data_inicio"))
        ).filter(days__gt=3)
        return q.filter

    def get_query(self):

        filter_extension = (
            Q(prorrogacao__data_inicio__gte=self.sicap_helper.date_start)
            & Q(prorrogacao__data_inicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        filter_ = (
            (
                Q(data_inicio__gte=self.sicap_helper.date_start)
                & Q(data_inicio__lte=self.sicap_helper.date_end)
            )
            | filter_extension
        ) & ~Q(estado=CANCELADO)

        # Filtrar licenças Doença Pessoa na Familia e Afastamento Conjuge com mais de 3 dias
        q_1 = (
            BaseLicencaAfastamento.objects.filter(tipo__in=[11, 14])
            .filter(filter_)
            .annotate(days_cache=Count(F("data_fim") - F("data_inicio")))
            .filter(days_cache__gt=3)
        )

        # Filtrar licenças restantes
        filter_with_types = Q(tipo__in=[8, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23])
        q_2 = BaseLicencaAfastamento.objects.filter(filter_with_types).filter(filter_)

        return (q_1 | q_2).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class FunctionRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Funcao"


class FunctionFile(BaseSicapFile):

    verbose_name = "Funções"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()

        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            act = ""
            admission_act = ""
            act_type = ""
            admission_act_type = ""

            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            admission_ = EmployeeFile.get_admission_by_period(
                self.sicap_helper, instance.servidor
            )
            if admission_ and BaseSicapFile.publication_is_valid(
                admission_.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        admission_.publicacao_movimentacao.numero
                    ),
                    admission_.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    admission_.publicacao_movimentacao.tipo
                )
            job_position = (
                instance.quadro.cargo.pk
                if instance.quadro and instance.quadro.cargo
                else ""
            )
            job_position_admission = (
                admission_.quadro.cargo.pk
                if admission_.quadro and admission_.quadro.cargo
                else ""
            )

            record = FunctionRecord(
                "function",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargoAdmissao=job_position_admission,
                numeroAto=act,
                codigoCargo=job_position,
                dataInicio=instance.data_exercicio.strftime("%Y-%m-%d"),
                recebeComissao=0,
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if admission_:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(admission_)

                    if admission_.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(admission_.publicacao_movimentacao.pk)

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):

        filter_possession = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & Q(quadro__cargo__tipo_lei_cargo="FC")
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoPosse.objects.filter(filter_possession).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class AssignmentRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Cessao"


class AssignmentFile(BaseSicapFile):

    verbose_name = "Cessão"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()

        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            act = ""
            admission_act = ""
            act_type = ""
            admission_act_type = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            admission_ = EmployeeFile.get_admission_by_period(
                self.sicap_helper, instance.servidor
            )
            if admission_ and BaseSicapFile.publication_is_valid(
                admission_.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        admission_.publicacao_movimentacao.numero
                    ),
                    admission_.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    admission_.publicacao_movimentacao.tipo
                )

            job_position_admission = (
                admission_.quadro.cargo.pk
                if admission_.quadro and admission_.quadro.cargo
                else ""
            )
            cnpj_destination = (
                instance.orgao.pessoa_juridica.cnpj
                if instance.orgao and instance.orgao.pessoa_juridica
                else ""
            )
            record = AssignmentRecord(
                "assignment",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargo=job_position_admission,
                numeroAto=act,
                cnpjOrgaoDestino=cnpj_destination,
                dataInicio=instance.data_inicio,
                dataFim=instance.data_fim,
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if admission_:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(admission_)

                    if admission_.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(admission_.publicacao_movimentacao.pk)

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

    def get_query(self):
        filter_p = (
            Q(prorrogacao__data_inicio__gte=self.sicap_helper.date_start)
            & Q(prorrogacao__data_inicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        filter_moved_away_local = (
            (
                Q(data_inicio__gte=self.sicap_helper.date_start)
                & Q(data_inicio__lte=self.sicap_helper.date_end)
            )
            | filter_p
        ) & ~Q(estado=CANCELADO)

        return AfastamentoOutroOrgao.objects.filter(filter_moved_away_local).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class AvailabilityRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Disponibilidade"


class AvailabilityFile(BaseSicapFile):

    verbose_name = "Disponibilidade"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            act_type = ""
            admission_act_type = ""

            admission_act = ""
            if instance.posse and BaseSicapFile.publication_is_valid(
                instance.posse.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.posse.publicacao_movimentacao.numero
                    ),
                    instance.posse.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.posse.publicacao_movimentacao.tipo
                )
            act = ""
            if BaseSicapFile.publication_is_valid(instance.publicacao_movimentacao):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            job_position_code_adm = ""
            if instance.posse and instance.posse.quadro and instance.posse.quadro.cargo:
                job_position_code_adm = instance.posse.quadro.cargo.pk

            record = AvailabilityRecord(
                "availability",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargo=job_position_code_adm,
                numeroAto=act,
                dataDisponibilidade=(
                    instance.data_inicio.strftime("%Y-%m-%d")
                    if instance.data_inicio
                    else ""
                ),
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if instance.posse:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.posse)

                    if instance.posse.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.posse.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):

        filter_p = (
            Q(prorrogacao__data_inicio__gte=self.sicap_helper.date_start)
            & Q(prorrogacao__data_inicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        filter_all = (
            (
                Q(data_inicio__gte=self.sicap_helper.date_start)
                & Q(data_inicio__lte=self.sicap_helper.date_end)
            )
            | filter_p
        ) & ~Q(estado=CANCELADO)

        return AfastamentoDisponibilidade.objects.filter(filter_all).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class UtilizationRecord(Record):
    _protocol = SICAP
    _marker = "Aproveitamento"


class UtilizationFile(BaseSicapFile):

    verbose_name = "Aproveitamento"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            admission_act_type = ""
            admission_act = ""

            admission_act = ""
            if instance.posse_anterior and BaseSicapFile.publication_is_valid(
                instance.posse_anterior.publicacao_movimentacao
            ):
                admission_act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.posse_anterior.publicacao_movimentacao.numero
                    ),
                    instance.posse_anterior.publicacao_movimentacao.ano,
                )
                admission_act_type = ActFile.parse_act_type(
                    instance.posse_anterior.publicacao_movimentacao.tipo
                )
            act = ""
            act_type = ""
            if instance.publicacao_movimentacao and BaseSicapFile.publication_is_valid(
                instance.publicacao_movimentacao
            ):
                act = "%s%s" % (
                    BaseSicapFile.format_number_law(
                        instance.publicacao_movimentacao.numero
                    ),
                    instance.publicacao_movimentacao.ano,
                )
                act_type = ActFile.parse_act_type(instance.publicacao_movimentacao.tipo)
            job_position_code_adm = ""
            if (
                instance.posse_anterior
                and instance.posse_anterior.quadro
                and instance.posse_anterior.quadro.cargo
            ):
                job_position_code_adm = instance.posse_anterior.quadro.cargo.pk

            record = UtilizationRecord(
                "utilization",
                matriculaServidor=instance.servidor.matricula,
                numeroAtoAdmissao=admission_act,
                codigoCargoAdmissao=job_position_code_adm,
                numeroAto=act,
                codigoCargo=(
                    instance.quadro.cargo.pk
                    if instance.quadro and instance.quadro.cargo
                    else 0
                ),
                dataAproveitamento=(
                    instance.data_exercicio.strftime("%Y-%m-%d")
                    if instance.data_exercicio
                    else ""
                ),
                tipoAto=act_type,
                tipoAtoAdmissao=admission_act_type,
            )
            if self.record_add(record, instance):
                if instance.posse_anterior:
                    # adcionando admissao na lista
                    self.sicap_helper.add_possession(instance.posse_anterior)

                    if instance.posse_anterior.publicacao_movimentacao:
                        # adicionando ato de adimissão
                        self.sicap_helper.add_act(
                            instance.posse_anterior.publicacao_movimentacao.pk
                        )

                if instance.publicacao_movimentacao:
                    # adicionando ato de desligamento
                    self.sicap_helper.add_act(instance.publicacao_movimentacao.pk)

        return self.regs

    def get_query(self):

        filter_ = Q(
            Q(data_exercicio__gte=self.sicap_helper.date_start)
            & Q(data_exercicio__lte=self.sicap_helper.date_end)
            & Q(servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions())
        )

        return MovimentacaoAproveitamento.objects.filter(filter_).order_by(
            "servidor__pessoa_fisica__nome", "publicacao_movimentacao__data_vigencia"
        )


class SheetBase(BaseSicapFile):

    verbose_name = "Aproveitamento"

    def get_query(self):
        # Excluindo servidores que não possuem vinculo com o MPE
        filter_exclude = Q(servidor__pk__in=EmployeeFile.get_exclude_employeers())

        query = (
            FolhaEvento.objects.filter(
                ~Q(evento__genre_event__config_transparency=None)
                & Q(
                    servidor__type_by_possession__in=EmployeeFile.get_allowed_possessions()
                )
                & Q(folha__periodo__mes__gte=self.sicap_helper.month_start)
                & Q(
                    folha__periodo__mes__lte=(
                        13
                        if self.sicap_helper.month_end == 12
                        else self.sicap_helper.month_end
                    )
                )
                & Q(folha__periodo__ano=self.sicap_helper.year)
            )
            .exclude(filter_exclude)
            .order_by("servidor", "folha__periodo__mes")
        )
        if self.sicap_helper.months:
            query = query.filter(
                folha__periodo__mes__in=self.sicap_helper.months, status="CT"
            )
        return query.exclude(status="NC")


class SheetItemRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "FolhaItem"


class SheetItemFile(SheetBase):

    verbose_name = "Folha Item"

    def make_records(self):
        query = Evento.objects.filter(
            pk__in=self.get_query().values("evento").distinct()
        )

        total = query.count()
        count = 1
        self.write_feedback()
        for event in query:
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            no_remuneration = ""

            record = SheetItemRecord(
                "sheet_item",
                codigoFolhaItemESocial=self.get_esocial_code_self(event),
                codigoFolhaItem=event.pk,
                descricao=event.titulo,
                incidePrevidenciaGeral=self.rgps_in(event),
                incidePrevidenciaRPPS=self.rpps_in(event),
                incideIRRF=self.irrf_in(event),
                motivoFolhaSemRemuneracao=no_remuneration,
            )
            self.record_add(record, event)

        return self.regs

    def get_esocial_code_self(self, event):
        return self.get_esocial_code(self.sicap_helper, event)

    @classmethod
    def get_esocial_code(cls, sicap_helper, event):
        code = event.configs.current_in(
            sicap_helper.date_start, sicap_helper.date_end
        ).last()
        if code and code.nature_event:
            return code.nature_event.code
        else:
            return ""

    def rpps_in(self, event):
        rpps = "0"
        if event.aplica_em.filter(
            event__genre_event__genre_number__in=[
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
            ]
        ).exists():
            rpps = 1

        return rpps

    def rgps_in(self, event):
        rgps = 0
        if event.aplica_em.filter(
            event__genre_event__genre_number__in=[910, 911]
        ).exists():
            rgps = 1

        return rgps

    def irrf_in(self, event):
        if event.aplica_em.filter(
            event__genre_event__genre_number__in=[999, 992, 991]
        ).exists():
            return 1
        else:
            return 0


class SheetRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "FolhaPagamento"


class SheetFile(SheetBase):

    verbose_name = "Folha de Pagamento"

    def make_records(self):

        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for sheet_event in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            if not self.only_pass(sheet_event):
                try:
                    act, job_code, act_pk, possession, act_type = (
                        EmployeeFile.employee_job_act(
                            self.sicap_helper, sheet_event.servidor
                        )
                    )
                    ref_month = (
                        12
                        if sheet_event.reference_month == 13
                        else sheet_event.reference_month
                    )
                    ssc = sheet_event.servidor.get_socialsecurity_by_validity(
                        range=NewDateRange(
                            self.sicap_helper.date_start, self.sicap_helper.date_end
                        )
                    )
                    if not ssc:
                        ssc = sheet_event.servidor.get_socialsecurity_by_validity()

                    ir_discount = (
                        "%.2f" % sheet_event.valor_base
                        if self.is_irrf(sheet_event)
                        else ""
                    )

                    record = SheetRecord(
                        "sheet",
                        matriculaServidor=sheet_event.servidor.matricula,
                        numeroAto=act,
                        tipoAto=act_type,
                        codigoCargo=job_code,
                        codigoFolhaItem=sheet_event.evento.pk,
                        tipoFolha=self.get_type_sheet(sheet_event),
                        competencia="%s-%s-%s"
                        % (sheet_event.reference_year, str(ref_month).zfill(2), "01"),
                        valor="%.2f" % sheet_event.valor,
                        complemento="",
                        aliquotaDesconto="",
                        aliquotaDescontoPrevidenciario=self.socialsecurity_aliquot(
                            sheet_event
                        ),
                        baseDescontoPrevidenciario=self.socialsecurity_base(
                            sheet_event
                        ),
                        aliquotaContribuicaoPatronal=(
                            ("%.2f" % sheet_event.employer_contribution)
                            if sheet_event.employer_contribution
                            else ""
                        ),
                        baseDescontoIr=ir_discount,
                        regimePrevidenciario=1 if ssc and ssc.regime == 1 else 2,
                        observacao="",
                        jornadaSemanal=self.get_workload(sheet_event.servidor),
                    )

                    if self.record_add(
                        record,
                        sheet_event,
                        custom_msg=f"Arquivo Folha de Pagamento: {sheet_event.servidor} ({sheet_event.pk}) - Erro(s):\n",
                    ):
                        if act_pk:
                            self.sicap_helper.add_act(act_pk)

                        if possession:
                            self.sicap_helper.add_possession(possession)
                        self.sicap_helper.add_employee(sheet_event.servidor.pk)
                        if job_code:
                            self.sicap_helper.add_job_position(job_code)

                except Exception as err:
                    msg = f"Folha de Pagamento - Servidor:{sheet_event.servidor} - {sheet_event.pk} - Erro: {err}"
                    print(msg)
                    if self.task:
                        self.task.info(msg=f"{msg}", type_of=3)

    def socialsecurity_base(self, sheet_event):
        if self.is_social_security(sheet_event):
            if sheet_event.valor_base:
                return "%.2f" % sheet_event.valor_base
            else:
                return "%.2f" % sheet_event.valor
        else:
            return ""

    def socialsecurity_aliquot(self, sheet_event):
        if self.is_social_security(sheet_event):
            if sheet_event.pct:
                return "%.2f" % sheet_event.pct
            else:
                if sheet_event.valor_base:
                    return "%.2f" % ((100 * sheet_event.valor) / sheet_event.valor_base)
                else:
                    ssc = sheet_event.servidor.get_socialsecurity_by_validity(
                        range=NewDateRange(
                            self.sicap_helper.date_start, self.sicap_helper.date_end
                        )
                    )
                    ss = (
                        SocialSecurity.objects.filter(
                            legal_person=sheet_event.servidor.organ_social_security_employee(),
                            socialsecurity_regime=ssc.regime,
                        )
                        .currents_at(self.sicap_helper.date_start)
                        .order_by("-start_validity")
                        .first()
                    )
                    if ss:
                        r = ss.ranges.first()
                        return r.percentage if r else ""
                    else:
                        ss = SocialSecurity.objects.filter(
                            legal_person=sheet_event.servidor.organ_social_security_employee(),
                            socialsecurity_regime=ssc.regime,
                        ).last()
                        r = ss.ranges.first()
                        return r.percentage if r else ""
        else:
            return ""

    def is_irrf(self, sheet_event):
        code = SheetItemFile.get_esocial_code(self.sicap_helper, sheet_event.evento)
        if code and code == "9203":
            return True

        return False

    def is_social_security(self, sheet_event):
        code = SheetItemFile.get_esocial_code(self.sicap_helper, sheet_event.evento)
        if code and code == "9201":
            return True

        return False

    def get_type_sheet(self, sheet_event):
        if sheet_event.folha.tipo_folha.numero == "0001":
            return 1
        elif sheet_event.folha.tipo_folha.numero == "0021":
            return 4
        elif sheet_event.folha.tipo_folha.numero == "0003":
            return 5
        else:
            return 12

    def get_workload(self, employee):
        parser_workload_sicap = {20: 1, 30: 2, 35: 3, 40: 4, 60: 5, 88: 6, 99: 9}
        workload = ""
        workloads = CargaHoraria.objects.filter(servidor=employee, data_fim=None)
        if workloads.exists():
            workload = int(workloads.last().quantidade)
        return parser_workload_sicap.get(workload, 3)

    def only_pass(self, sheet_event):
        # Verifica se o servidor está recebendo apenas a verba de PASS e se possui desligamento
        have_other_events = sheet_event.contracheque.lancamentos.exclude(
            evento__genre_event__genre_number="094"
        ).exists()
        shutdown = (
            sheet_event.servidor.data_desligamento
            and sheet_event.servidor.data_desligamento < self.sicap_helper.date_start
        )
        if shutdown:
            if not have_other_events:
                return True

            if sheet_event.servidor.aposentado:
                return True

            if sheet_event.servidor.situacao_funcional == "Falecido":
                return True
        return False


class PublicConcurrenceRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Edital"


class PublicConcurrenceFile(BaseSicapFile):

    verbose_name = "Edital"

    def make_records(self):
        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1

            record = PublicConcurrenceRecord(
                "public_concurrence",
                tipoEdital=1,
                numeroEdital=instance.number_tce,
                veiculoPublicacao="",
                dataPublicacao=(
                    instance.date_public.strftime("%Y-%m-%d")
                    if instance.date_public
                    else ""
                ),
                dataInicioInscricoes="",
                dataFimInscricoes="",
                prazoValidade="",
                cnpjEmpresaOrganizadora="",
            )
            self.record_add(record, instance)

    def get_query(self):
        query = PublicConcurrence.objects.filter()
        return query


class SocialSecurityDemonstrativeRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "DemonstrativoPrevidenciario"


class SocialSecurityDemonstrativeFile(BaseSicapFile):

    verbose_name = "Demonstrativo Previdenciário"

    def make_records(self):
        organ = AdministrativeUnitFile.get_administrative_unit()
        total = self.get_query().count()
        count = 1
        self.write_feedback()
        for instance in self.get_query():
            self.write_feedback(progress=((100.0 * float(count)) / float(total)))
            count += 1
            rat_fap = (
                self.get_fap_rat()
                if instance.get_socialsecurity_regime_display() == "RGPS"
                else ""
            )
            employeer_contribution = (
                float(instance.percentage_of_employer) + float(rat_fap)
                if rat_fap
                else instance.percentage_of_employer
            )

            for ss in instance.ranges.all():
                record = SocialSecurityDemonstrativeRecord(
                    "socialsecurity_demonstrative",
                    cnpj=organ.pessoa_juridica.cnpj,
                    periodoReferencia=self.sicap_helper.date_start,
                    regimePrevidencia=(
                        1
                        if instance.get_socialsecurity_regime_display() == "RGPS"
                        else 2
                    ),
                    cnpjRppsRequisitado=(
                        instance.legal_person.cnpj if instance.legal_person else ""
                    ),
                    baseCalculo=ss.percentage,
                    aliquotaPatronal=instance.percentage_of_employer,
                    aliquotaRatFap=rat_fap,
                    contribuicaoPatronal=employeer_contribution,
                )
                self.record_add(record, instance)

    def get_query(self):
        query = SocialSecurity.objects.filter(
            Q(end_validity__lte=self.sicap_helper.date_start) | Q(end_validity=None)
        )
        return query

    def get_fap_rat(self):
        return FatorFap.vigente_em(self.sicap_helper.date_end) + FatorRat.vigente_em(
            self.sicap_helper.date_end
        )


class SocialSecurityGatheringRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "RecolhimentoPrevidenciario"


class SocialSecurityGatheringFile(BaseSicapFile):

    verbose_name = "Recolhimento Previdenciário"

    def make_records(self):
        self.write_feedback()
        query = self.get_query()
        total = len(query)
        if total > 0:
            count = 1
            for instance in query:
                self.write_feedback(progress=((100.0 * float(count)) / float(total)))
                count += 1
                record = SocialSecurityGatheringRecord(
                    "socialsecurity_gathering",
                    cnpjOrgaoDestino=instance["cnpj"],
                    anoCompetencia=self.sicap_helper.date_start.year,
                    mesCompetencia=self.sicap_helper.date_start.month,
                    dataPagamento=instance["payment_date"],
                    numeroPagamento=instance["payment_number"],
                    regimePrevidenciario=instance["regime"],
                    valorPago=instance["payment_value"],
                    houvePagamento=1,
                )
                self.record_add(
                    record, instance, custom_msg="Recolhimento Previdenciário\n"
                )
        else:
            self.write_feedback(progress=((100.0 * float(1)) / float(1)))
            record = SocialSecurityGatheringRecord(
                "socialsecurity_gathering",
                houvePagamento=0,
            )
            self.regs.append(record)
            warn = "Arquivo de Recolhimento Previdenciário está sendo gerado sem dados!"
            if self.task:
                self.task.info(msg=warn, type_of=2)
            else:
                print(warn)

    def get_query(self):
        file_return = self.read_gathering_file()
        query = []
        for q in file_return:
            ss = SocialSecurity.objects.filter(legal_person__cnpj=q["cnpj"]).last()
            if ss:
                regime = 1 if ss.socialsecurity_regime == 1 else 2
                q.update({"regime": regime})
                query.append(q)
        return query

    def read_gathering_file(self):
        data = []
        paymentfile_ = File.objects.filter(pk=self.sicap_helper.paymentfile).last()
        if paymentfile_:
            try:
                with codecs.open(
                    paymentfile_.absolute_path, encoding="utf-8"
                ) as csvfile:
                    for row in csvfile.readlines():
                        row = self.remove_chars(row)
                        row_value = row.split("|")
                        if len(row_value) > 0 and str(row_value[0]).lower() != "data":
                            data.append(
                                {
                                    "payment_date": row_value[0],
                                    "payment_number": row_value[1],
                                    "payment_value": row_value[2],
                                    "cnpj": row_value[3],
                                }
                            )
            except Exception as err:
                error = "Erro ao carregar arquivo de recolhimento previdenciário, verifique o arquivo!"
                if self.task:
                    self.task.info(msg=error, type_of=3)
                    self.task.info(msg=err, type_of=3)
                else:
                    print(error)
                    print(err)
        return data

    def remove_chars(self, text):
        text = text.replace("R$ ", "")
        text = text.replace(" ", "")
        text = text.replace(".", "")
        text = text.replace(",", ".")
        text = text.replace("\n", "")
        return text


class ActRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Ato"


class AdministrativeUnitRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "UnidadeAdministrativa"


class JobPositionRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Cargo"


class LawRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Lei"


class WorkplaceRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Lotacao"


class EmployeeRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Servidor"


class AdmissionRecord(BaseSicapRecord):
    _protocol = SICAP
    _marker = "Admissao"
