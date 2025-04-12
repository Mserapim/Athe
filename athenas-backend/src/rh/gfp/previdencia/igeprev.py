# -*- coding: utf-8 -*-

import codecs
import os
from datetime import datetime
from zipfile import ZipFile

from django.conf import settings
from django.db.models import Q, Sum
from django.template.defaultfilters import slugify


from contrib.decorator import deprecated
from contrib.utils import DateUtils, getLogger
from rh.afastamento.models import ACTIVE, AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO
from rh.gfp.febrabam import Protocol
from rh.gfp.models import ContraCheque, Folha, FolhaEvento
from rh.gfp.previdencia import Registro
from rh.gfp.previdencia.layouts import IGEPREV
from rh.models import (
    DadoBancarioPessoa,
    Dependente,
    MovimentacaoAposentadoria,
    OrgaoGeral,
    PessoaFisica,
    Servidor,
)

unlink = None

if getattr(settings, "DEBUG", False) is True:

    def void(path):
        pass

    unlink = void
else:
    from os import unlink

log = getLogger(__name__)

__name__ = "Arquivos IGEPREV"
__hid__ = ""


def feedback(progress_message, progress, **kwargs):
    print("%s... %s" % (progress, progress_message % kwargs))


class IgeprevGenerator(object):

    def __init__(self, **kwargs):
        self.folha = kwargs.get("sheet", None)
        folha_ = Folha.objects.get(pk=self.folha)
        self.ano_referencia = kwargs.get("ano_referencia", folha_.periodo.ano)
        self.mes_referencia = kwargs.get("mes_referencia", folha_.periodo.mes)
        self.zip_name = kwargs.get("zip_name", self.get_zip_file())
        self.flush_file()
        self.feedback = kwargs.get("feedback", feedback)

    def write_feedback(self, progress=1, message_progress="", toprint=True):
        self.feedback(
            "%(message_progress)s", progress, message_progress=message_progress[0:99]
        )
        if toprint:
            print("%s... %s" % (progress, message_progress))

    @classmethod
    def cache_dir(cls):
        return settings.CACHE_PATH

    def flush_file(self):
        try:
            arquivo = open(
                "%s/%s"
                % (self.cache_dir(), IGEPREV["Erro-header"]["cfg"]["nome_arquivo"]),
                "w",
            )
            arquivo.write("")
            arquivo.close()
        except:
            pass

    def get_zip_name(self):
        return "mpeto-igeprev-%s-%s-%s.zip" % (
            (
                slugify(Folha.objects.get(pk=self.folha).tipo_folha)
                if self.folha
                else "mpeto-igeprev.zip"
            ),
            self.mes_referencia,
            self.ano_referencia,
        )

    def get_zip_file(self):
        return os.path.join(self.cache_dir(), self.get_zip_name())

    def gerador(self, importacao_completa=False, tfiles=[]):
        from rh.gfp.previdencia import arquivo
        from rh.gfp.previdencia import sisprev as sisprev_arquivo

        to_zip = []
        builders = {
            "abono_permanencia": None,
            "orgaos": arquivo.Orgao,
            "cargos": arquivo.Cargo,
            "unidades": arquivo.Unidade,
            "gruposalarial": arquivo.Grupo,
            "carreiras": arquivo.Carreira,
            "cargos_carreiras": arquivo.CargoCarreira,
            "servidores": arquivo.Servidor,
            "servidores_requisitados": arquivo.ServidorRequisitado,
            "proventos": arquivo.Remuneracao,
            "proventos_requisitados": arquivo.RemuneracaoRequisitado,
            "afastamentos": arquivo.Afastamento,
            "dependentes": arquivo.Dependente,
            "dependentes_requisitados": arquivo.DependenteRequisitado,
            "progressao": arquivo.Progressao,
            "dependentes_levantamento": arquivo.DependenteLevantamento,
            "servidores_levantamento": arquivo.ServidorLevantamento,
            "servidores_auditoriatce": arquivo.ServidorAuditoriaTce,
            "servidores_tce": arquivo.ServidorTce,
            "orgaos_sisprev": sisprev_arquivo.OrgaosSisprev,
            "unidades_sisprev": sisprev_arquivo.UnidadeSisprev,
            "lotacoes_sisprev": sisprev_arquivo.LotacoesSisprev,
            "cargos_sisprev": sisprev_arquivo.CargosSisprev,
            "fontepagadora_sisprev": sisprev_arquivo.FontePagadoraSisprev,
            "tipo_situacaofuncional_sisprev": sisprev_arquivo.TipoSituacaoFuncionalSisprev,
            "estadocivil_sisprev": sisprev_arquivo.EstadoCivilSisprev,
            "escolaridade_sisprev": sisprev_arquivo.EscolaridadeSisprev,
            "tipodependencia_sisprev": sisprev_arquivo.TipoDependenciaSisprev,
            "quadromilitares_sisprev": sisprev_arquivo.QuadroMilitaresSisprev,
            "pessoas_sisprev": sisprev_arquivo.PessoasSisprev,
            "segurados_sisprev": sisprev_arquivo.SeguradosSisprev,
            "seguradoscedidos_sisprev": sisprev_arquivo.SeguradosCedidosSisprev,
            "pessoasdependentes_sisprev": sisprev_arquivo.PessoasDependentesSisprev,
            "dependentes_sisprev": sisprev_arquivo.DependentesSisprev,
            "eventosrubricas_sisprev": sisprev_arquivo.EventosRubricasSisprev,
            "bancos_sisprev": sisprev_arquivo.BancosSisprev,
            "cargosocupados_sisprev": sisprev_arquivo.CargosOcupadosSisprev,
            "financeiro_sisprev": sisprev_arquivo.FinanceiroSisprev,
            "pensoesalimenticias_sisprev": sisprev_arquivo.PensoesAlimenticiasSisprev,
            "contribuicoesmensal_sisprev": sisprev_arquivo.ContribuicoesMensalSisprev,
            "contribuicoeshistorico_sisprev": sisprev_arquivo.ContribuicoesHistoricoSisprev,
            "contribuicoeshomologacao_sisprev": sisprev_arquivo.ContribuicoesHomologacaoSisprev,
        }

        if os.path.exists(self.get_zip_file()):
            os.unlink(self.get_zip_file())

        self.write_feedback(
            message_progress="Iniciando processo de geração de arquivos"
        )

        count = 0
        total = len(tfiles) if len(tfiles) > 0 else 1
        for mfile in tfiles:
            Builder = builders.get(mfile, None)
            count += 1

            self.write_feedback(
                progress=((100.0 * float(count)) / float(total)),
                message_progress="Gerando arquivos: %d de %d" % (count, total),
            )

            to_zip.append(["Erro-igeprev", "Erro-igeprev"])
            if Builder:
                builder = Builder(
                    feedback=self.feedback,
                    ano_referencia=self.ano_referencia,
                    mes_referencia=self.mes_referencia,
                    importacao_completa=importacao_completa,
                    sheet=self.folha,
                )
                if not builder._save_on_demand:
                    builder.save_file()

                to_zip.append([builder.get_file_name(), builder.get_arc_file_name()])
            else:
                log.warn("O gerador para o arquivo %s é desconhecido." % mfile)
        self.compact(to_zip)
        self.write_feedback(
            progress=100, message_progress="Geração de arquivos concluída."
        )

    def compact(self, to_zip_files):
        try:
            total = len(to_zip_files)
            count = 0
            self.write_feedback(message_progress="Iniciando compressão de arquivos.")
            for f in to_zip_files:
                try:
                    source = "%s/%s" % (self.cache_dir(), f[0])
                    zipfile_tmp = ZipFile(
                        "%s.zip" % os.path.join(self.cache_dir(), f[1]), "w"
                    )
                    zipfile_tmp.write(source, "%s.txt" % f[1])
                    zipfile_tmp.close()
                    try:
                        unlink(source)
                    except Exception as err:
                        log.exception(err)
                        print(err)
                except Exception as err:
                    log.exception(err)
                    print(err)
                count += 1
                self.write_feedback(
                    progress=((100.0 * float(count)) / float(total)),
                    message_progress="Comprimindo...%s" % f[1],
                )
            zipfile = ZipFile(self.get_zip_file(), "w")
            count = 0
            for f in to_zip_files:
                try:
                    zipfile.write(
                        "%s.zip" % os.path.join(self.cache_dir(), f[1]), "%s.zip" % f[1]
                    )
                except Exception as err:
                    log.exception(err)
                    print(err)
                count += 1
                self.write_feedback(
                    progress=((100.0 * float(count)) / float(total)),
                    message_progress="Comprimindo...",
                )
            zipfile.close()
            for f in to_zip_files:
                unlink("%s.zip" % os.path.join(self.cache_dir(), f[1]))
        except Exception as err:
            log.exception(err)
            print(err)


class Igeprev(Protocol):
    """
    Classe base para construção dos arquivos do IGEPREV.
    Considera-se que todas informações são extraídas em função do mês e ano de referência.
    """

    _file_name = ""
    _class_name = ""
    _ano_referencia = ""
    _mes_referencia = ""
    _data_referencia = None
    _importacao_completa = False
    _TODOS = 1
    _ATIVO = 2
    _INATIVO = 3
    _PENSIONISTA = 4
    observer = None
    folha = None
    _save_on_demand = False
    _encoding = "utf-8"
    _set_header = True

    def __init__(self, **conf):
        Protocol.__init__(self)
        self.conf(**conf)
        self.delete_file()
        self.write_feedback(message_progress="Gerando arquivo %s" % self.get_filename())
        if self._set_header:
            self.regs.append(
                Registro(
                    len(self.regs) + 1,
                    "%s-header" % self._class_name,
                    data_geracao=datetime.now().strftime("%d/%m/%Y"),
                )
            )
        self.adiciona_corpo()

    def conf(self, **conf):
        self._set_header = conf.get("_set_header", True)
        self._class_name = conf.get("class_name")
        self._importacao_completa = conf.get("importacao_completa", False)
        self._ano_referencia = int(conf.get("ano_referencia"))
        self._mes_referencia = int(conf.get("mes_referencia"))
        self._save_on_demand = conf.get("_save_on_demand", False)
        self.folha = int(conf.get("sheet"))
        self.set_data_referencia(self._ano_referencia, self._mes_referencia)
        self.set_filename("%s-header" % self._class_name)
        self.nl = "\r\n"
        self.feedback = conf.get("feedback", feedback)

    def write_feedback(self, progress=1, message_progress="", toprint=True):
        self.feedback(
            "%(message_progress)s", progress, message_progress=message_progress[0:99]
        )
        if toprint:
            print("%s... %s" % (progress, message_progress))

    @classmethod
    def cache_dir(cls):
        return settings.CACHE_PATH

    def query(self):
        return []

    def get_q_data_alteracao(self):
        """
        Este método retorna a regra para incluir informações que foram alteradas ou criadas
        @return Q -
        """
        return Q(
            data_alteracao__gte=self._data_referencia_inicio,
            data_alteracao__lte=self._data_referencia,
        )

    def adiciona_corpo(self):
        query = self.query()
        message_progress = "Inserindo %s." % self._class_name
        total = (
            query.count() if not isinstance(query, (list, dict, tuple)) else len(query)
        )
        count = 0
        try:
            for info in query:
                count += 1.0
                self.write_feedback(
                    progress=((100.0 * float(count)) / float(total)),
                    message_progress=message_progress,
                )
                self.add_registro(info)
        except Exception as err:
            log.exception(err)
        self.write_feedback(progress=100, message_progress=message_progress)

    def add_registro(self, info):
        pass

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def get_filename(self):
        return self._file_name

    def set_filename(self, key):
        """
        Este método define o nome do arquivo.
        """
        try:
            self._file_name = IGEPREV[key]["cfg"]["nome_arquivo"]
        except:
            self._file_name = "nome-nao-encontrado"

    def set_data_referencia(self, ano, mes):
        """
        Este método define a data de referência de acordo com ano e mês informados.
        Ex: 31/07/2011 para o ano=2011 e mês=7.
        @param int - ano.
        @param int - mes.
        """
        import calendar

        if mes in ("13", 13):
            mes = 12
        self._data_referencia = datetime(ano, mes, (calendar.monthrange(ano, mes))[1])
        self.set_data_referencia_inicio()

    def get_data_referencia(self):
        """
        Este método retorna a data do último dia do mês e ano de referência.
        Ex: 31/07/2011 para o ano=2011 e mês=7.
        @return datetime - data de referência.
        """
        return self._data_referencia

    @staticmethod
    def get_valor_from_table(tabela, key):
        valor = ""
        try:
            valor = tabela.get(key)
        except Exception:
            pass
        return valor

    @staticmethod
    def get_sheet(sheet):
        return sheet

    @staticmethod
    def get_description_sheet(sheet):
        parser = {
            21: "Décimo Terceiro",
            1: "Normal",
        }
        return parser.get(sheet)

    @staticmethod
    def get_orgao():
        """
        Este método retorna o valor padrão para o MPE-TO no IGEPREV.
        """
        return 991

    @deprecated
    @staticmethod
    def gera_codigo_igeprev(orgao):
        """
        Este método gera um código para um órgão que ainda não possua código.
        Ele verifica qual o último código do IGEPREV e cria um valor na sequência para evitar duplicidade.
        @param OrgaoGeral - orgao.
        @return boolean - True se der certo, False se ocorrer erro.
        """
        codigo = 0
        try:
            general_organs = OrgaoGeral.objects.filter().exclude(codigo_igeprev=None)
            if general_organs.exists():
                codigo = general_organs.order_by("-codigo_igeprev")[0].codigo_igeprev
            while not OrgaoGeral.objects.get(pk=orgao.pk).codigo_igeprev:
                try:
                    OrgaoGeral.objects.filter(pk=orgao.pk).update(codigo_igeprev=codigo)
                except Exception as err:
                    print(err)
                codigo += 1
        except:
            pass
        return codigo

    def set_data_referencia_inicio(self):
        self._data_referencia_inicio = datetime(
            self.get_data_referencia().year, self.get_data_referencia().month, 1
        )

    def get_data_referencia_inicio(self):
        return self._data_referencia_inicio

    def get_file_name(self):
        return "%s_" % self.get_filename()

    def get_arc_file_name(self):
        return "%s" % self.get_filename()

    def delete_file(self):
        try:
            filename = os.path.join(self.cache_dir(), self.get_file_name())
            print("Apagando arquivo %s..." % filename)
            log.info("Apagando arquivo %s..." % filename)
            os.unlink(filename)
        except Exception as err:
            log.exception(err)

    def save_file(self, mode="w", text=""):
        rst = False
        try:
            filename = os.path.join(self.cache_dir(), self.get_file_name())
            print("Criando arquivo %s..." % filename)
            log.info("Criando arquivo %s..." % filename)
            fd = codecs.open(filename, mode, self._encoding)
            if mode == "a":
                fd.write("\n")
        except Exception as err:
            log.exception(err)
        else:
            if not text:
                text = str(self)
            try:
                fd.write(text)
            except Exception as err:
                log.exception(err)
            fd.close()
            rst = True
        return rst


class BaseDados(object):

    _data_referencia = None
    _data_referencia_inicio = None
    _importacao_completa = False
    _protocolo = Registro._protocolo
    _type = None
    _objeto = None
    _obrigatoriedade = None

    def __init__(self, **conf):
        self._data_referencia = conf.get("data_referencia")
        self._data_referencia_inicio = conf.get("data_referencia_inicio")
        self._importacao_completa = conf.get("importacao_completa")
        self._type = conf.get("type")

    def get_obrigatoriedade_label(self, key, linha):
        """

        @param str - key, identificador da linha do campo.
        @return boolean - True caso seja obrigatório, False de outa forma.
        """
        try:
            if self.get_obrigatoriedade_campo_layout(key, linha) in (
                "1*",
                "2*",
                "3*",
                "4*",
                "5*",
                "6*",
                "7*",
            ):
                return True
        except:
            pass
        return False

    def get_obrigatoriedade_campo_layout(self, label, linha):
        """
        Este método retorna a configuração de obrigatoriedade do campo conforme o layout.
        """
        try:
            if self.protocolo[self._type][linha]["label"] == label:
                return self.protocolo[self._type][linha]["obrigatorio"]
        except:
            pass
        return "0"

    def compara_obrigatoriedade(self, **kwargs):
        if self._objeto != kwargs["objeto"]:
            self._objeto = kwargs["objeto"]
            obrigatoriedade_label = self.get_obrigatoriedade_label(
                kwargs["label"], kwargs["linha"]
            )
            if self.get_obrigatoriedade_objeto(self._objeto) == obrigatoriedade_label:
                self._obrigatoriedade = obrigatoriedade_label
            else:
                self._obrigatoriedade = ""
        return self._obrigatoriedade

    def get_obrigatoriedade_objeto(self, objeto):
        """
        Este método pode receber Servidor ou PessoaFisica em objeto.
        A partir das informações a obrigatoriedade é definida.
        Os valores podem ser: 1-para todos; 2-ativos; 3-inativos; 4-pensionistas.
        @param Servidor/PessoaFisica/AfastamentoOutroOrgao - objeto.
        @param datetime - data_referencia.
        """
        tipo = "1*"
        try:
            if isinstance(objeto, Servidor):
                if objeto.ativo:
                    tipo = "2*"
                elif MovimentacaoAposentadoria.objects.filter(
                    Q(servidor=objeto)
                    & Q(data_desligamento__gte=self.get_data_referencia_inicio()),
                    Q(data_desligamento__lte=self.get_data_referencia()),
                ):
                    tipo = "3*"
            elif isinstance(objeto, PessoaFisica):
                if objeto.pensao_pensionista.filter(
                    data_inicio__gte=self.get_data_referencia_inicio(),
                    data_fim__lte=self.get_data_referencia(),
                ):
                    tipo = "4*"
            elif isinstance(objeto, Dependente):
                tipo = "4*"
            elif isinstance(objeto, AfastamentoOutroOrgao):
                if objeto.afastamento in (1, 2):
                    tipo = "6*"
                elif objeto.afastamento in (3, 4):
                    tipo = "7*"
        except:
            pass
        return tipo


class Dados(BaseDados):

    def __init__(self, **conf):
        super(Dados, self).__init__(**conf)

    def get_telefone(self, objeto):
        """
        Este método retorna o ddd, telefone da pessoa física.
        @param Instancia - objeto que possui telefone.
        @return str - ddd, telefone.
        """
        ddd = ""
        telefone = ""
        try:
            ddd = objeto.phone.all().order_by("-pk")[0].numero[0:2]
            telefone = objeto.phone.all().order_by("-pk")[0].numero[3:]
        except:
            pass
        return ddd, telefone

    def get_endereco(self, objeto):
        """
        Este método retorna o endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return Endereco - endereco.
        """
        endereco = None
        try:
            endereco = objeto.address.filter().order_by("-pk")[0]
        except:
            pass
        return endereco

    def get_bairro(self, **kwargs):
        """
        Este método retorna o bairro do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - bairro.
        """
        objeto = kwargs["objeto"]
        bairro = ""
        try:
            bairro = self.get_endereco(objeto).bairro
        except:
            pass
        if bairro == "":
            bairro = self.compara_obrigatoriedade(**kwargs)
        return bairro

    def get_municipio(self, **kwargs):
        """
        Este método retorna o município do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - município.
        """
        objeto = kwargs["objeto"]
        municipio = ""
        try:
            municipio = str(self.get_endereco(objeto).municipio)
        except:
            pass
        if municipio == "":
            municipio = self.compara_obrigatoriedade(**kwargs)
        return municipio

    def get_uf(self, **kwargs):
        """
        Este método retorna o uf do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - uf.
        """
        objeto = kwargs["objeto"]
        uf = ""
        try:
            uf = self.get_endereco(objeto).municipio.estado.sigla
        except:
            pass
        if uf == "":
            uf = self.compara_obrigatoriedade(**kwargs)
        return uf

    def get_pais(self, **kwargs):
        """
        Este método retorna o país do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - país.
        """
        objeto = kwargs["objeto"]
        pais = ""
        try:
            pais = str(self.get_endereco(objeto).municipio.estado.pais)
        except:
            pass
        if pais == "":
            pais = self.compara_obrigatoriedade(**kwargs)
        return pais

    def get_cep(self, **kwargs):
        """
        Este método retorna o cep do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - cep.
        """
        objeto = kwargs["objeto"]
        cep = ""
        try:
            cep = self.get_endereco(objeto).cep
        except:
            pass
        if cep == "":
            cep = self.compara_obrigatoriedade(**kwargs)
        return cep

    def get_tipo_logradouro(self, **kwargs):
        """
        Este método retorna o tipo do logradouro do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - tipo do logradouro.
        """
        objeto = kwargs["objeto"]
        tipo_logradouro = ""
        try:
            tipo_logradouro = self.get_endereco(objeto).tipo_logradouro
        except:
            pass
        if tipo_logradouro == "":
            tipo_logradouro = self.compara_obrigatoriedade(**kwargs)
        return tipo_logradouro

    def get_logradouro(self, **kwargs):
        """
        Este método retorna o logradouro do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - logradouro.
        """
        objeto = kwargs["objeto"]
        logradouro = ""
        try:
            logradouro = self.get_endereco(objeto).logradouro
        except:
            pass
        if logradouro == "":
            logradouro = self.compara_obrigatoriedade(**kwargs)
        return logradouro

    def get_quadra(self, **kwargs):
        """
        Este método retorna q quadra do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - quadra.
        """
        quadra = "-"
        return quadra

    def get_lote(self, **kwargs):
        """
        Este método retorna o lote do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - lote.
        """
        lote = ""
        if lote == "":
            lote = self.compara_obrigatoriedade(**kwargs)
        return lote

    def get_numero(self, **kwargs):
        """
        Este método retorna o número do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - número do endereço.
        """
        objeto = kwargs["objeto"]
        numero = ""
        try:
            numero = self.get_endereco(objeto).numero
        except:
            pass
        if numero == "":
            numero = self.compara_obrigatoriedade(**kwargs)
        return numero

    def get_complemento(self, **kwargs):
        """
        Este método retorna o bairro complemento do endereço da pessoa física.
        @param Instancia - objeto que possui Endereco.
        @return str - complemento do endereço da pessoa física.
        """
        objeto = kwargs["objeto"]
        complemento = ""
        try:
            complemento = self.get_endereco(objeto).complemento
        except:
            pass
        return complemento


class DadosOrgao(Dados):

    def get_filename(self):
        return "ARQUIVO_ORGAOS.txt"

    @staticmethod
    def get_poder(orgao):
        """
        Este método retorna o poder do órgão.
        @param OrgaoGeral - orgao.
        @return int - poder.
        """
        poder = None
        if orgao:
            try:
                poder = orgao.poder
            except:
                pass
        return poder

    @staticmethod
    def get_codigo(orgao):
        """
        Este método retorna o código IGEPREV do órgão.
        Caso seja necessário, gera um código a partir do último,
        conforme especificação em @Igeprev.gera_codigo_igeprev.
        @param OrgaoGeral - orgao.
        @return int - codigo.
        """
        codigo = None
        if orgao:
            codigo = orgao.codigo_igeprev
        return codigo

    @staticmethod
    def get_nome(orgao):
        nome = ""
        try:
            nome = orgao.nome
        except Exception:
            pass
        return nome

    @staticmethod
    def get_razao(orgao):
        razao = ""
        try:
            razao = str(orgao.pessoa_juridica.razao_social)
        except Exception:
            pass
        return razao

    @staticmethod
    def get_sigla(orgao):
        sigla = ""
        try:
            sigla = orgao.sigla
        except Exception:
            pass
        return sigla

    @staticmethod
    def get_cnpj(orgao):
        cnpj = ""
        try:
            cnpj = orgao.pessoa_juridica.cnpj
        except Exception:
            pass
        return cnpj


class DadosPessoa(Dados):

    def __init__(self, **conf):
        super(DadosPessoa, self).__init__(**conf)

    @staticmethod
    def get_nome(pessoa_fisica):
        """
        Este método retorna o nome da pessoa física.
        @param Pessoa - pessoa_fisica.
        @return str - nome.
        """
        nome = ""
        try:
            nome = str(pessoa_fisica)
        except Exception:
            pass
        return nome

    @staticmethod
    def get_cpf(pessoa_fisica):
        """
        Este método retorna o CPF da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - CPF.
        """
        cpf = ""
        try:
            cpf = pessoa_fisica.cpf
        except Exception:
            pass
        return cpf

    @staticmethod
    def get_identidade(pessoa_fisica):
        """
        Este método retorna o RG da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - RG.
        """
        rg = ""
        try:
            rg = pessoa_fisica.rg
        except Exception:
            pass
        return rg

    @staticmethod
    def get_uf_identidade(pessoa_fisica):
        """
        Este método retorna o RG da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - RG.
        """
        uf = ""
        try:
            uf = pessoa_fisica.rg_uf.sigla
        except Exception:
            pass
        return uf

    @staticmethod
    def get_data_identidade(pessoa_fisica):
        """
        Este método retorna a data de expedição do RG da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - data de expedição.
        """
        data_expedicao = ""
        try:
            data_expedicao = DateUtils.date_to_str(pessoa_fisica.rg_data_expedicao)
        except Exception:
            pass
        return data_expedicao

    @staticmethod
    def get_numero_titulo_eleitor(pessoa_fisica):
        """
        Este método retorna o número do título de eleitor da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - número do título de eleitor.
        """
        numero = ""
        try:
            numero = pessoa_fisica.voter.numero
        except Exception:
            pass
        return numero

    @staticmethod
    def get_zona_titulo_eleitor(pessoa_fisica):
        """
        Este método retorna a zona do título de eleitor da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - zona do título de eleitor.
        """
        zona = ""
        try:
            zona = pessoa_fisica.voter.voter_zone.valor
        except Exception:
            pass
        return zona

    @staticmethod
    def get_secao_titulo_eleitor(pessoa_fisica):
        """
        Este método retorna a seção do título de eleitor da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - seção do título de eleitor.
        """
        secao = ""
        try:
            secao = pessoa_fisica.voter.voter_section.valor
        except Exception:
            pass
        return secao

    @staticmethod
    def get_uf_titulo_eleitor(pessoa_fisica):
        """
        Este método retorna a uf do título de eleitor da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - uf do título de eleitor.
        """
        uf = ""
        try:
            uf = pessoa_fisica.voter.estado_expedicao.sigla
        except Exception:
            pass
        return uf

    @staticmethod
    def get_municipio_naturalidade(pessoa_fisica):
        """
        Este método retorna o município de naturalidade da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - município de naturalidade.
        """
        naturalidade = ""
        try:
            naturalidade = str(pessoa_fisica.municipio_naturalidade)
        except Exception:
            pass
        return naturalidade

    @staticmethod
    def get_uf_naturalidade(pessoa_fisica):
        """
        Este método retorna o Estado de naturalidade da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - Estado de naturalidade.
        """
        uf = ""
        try:
            uf = pessoa_fisica.municipio_naturalidade.estado.sigla
        except Exception:
            pass
        return uf

    @staticmethod
    def get_data_nascimento(pessoa_fisica):
        """
        Este método retorna a data de nascimento da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - data de nascimento.
        """
        data_nascimento = ""
        try:
            data_nascimento = DateUtils.date_to_str(pessoa_fisica.data_nascimento)
        except Exception:
            pass
        return data_nascimento

    @staticmethod
    def get_sexo(pessoa_fisica):
        """
        Este método retorna o sexo da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - sexo.
        """
        sexo = ""
        try:
            sexo = pessoa_fisica.sexo
        except Exception:
            pass
        return sexo

    @staticmethod
    def get_estado_civil(pessoa_fisica):
        """
        Este método retorna o estado civil da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - estado civil.
        """
        return pessoa_fisica.estado_civil

    @staticmethod
    def get_pis_pasep(pessoa_fisica):
        """
        Este método retorna o pis/pasep da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - pis_pasep.
        """
        pis_pasep = ""
        try:
            pis_pasep = pessoa_fisica.pis_pasep.numero
        except Exception:
            pass
        return int(pis_pasep) if pis_pasep != "" else pis_pasep

    @staticmethod
    def get_email(pessoa_fisica):
        """
        Este método retorna o email institucional da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - email.
        """
        email = ""
        try:
            email = pessoa_fisica.email_institucional
        except Exception:
            pass
        return email

    @staticmethod
    def get_data_obito(pessoa_fisica):
        """
        Este método retorna a data do óbito da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - data do óbito.
        """
        data_obito = ""
        try:
            data_obito = DateUtils.date_to_str(pessoa_fisica.data_obito)
        except Exception:
            pass
        return data_obito

    @staticmethod
    def get_nome_mae(pessoa_fisica):
        """
        Este método retorna o nome da mãe da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - nome da mãe.
        """
        nome_mae = ""
        try:
            nome_mae = pessoa_fisica.nome_mae
        except Exception:
            pass
        return nome_mae

    @staticmethod
    def get_nome_pai(pessoa_fisica):
        """
        Este método retorna o nome da pai da pessoa física.
        @param PessoaFisica - pessoa_fisica.
        @return str - nome da pai.
        """
        nome_pai = ""
        try:
            nome_pai = pessoa_fisica.nome_pai
        except Exception:
            pass
        return nome_pai

    @staticmethod
    def get_grau_instrucao(pessoa_fisica):
        """
        Este método retorna o grau de instrução do servidor.
        @param Servidor - servidor.
        @return str - grau de instrução.
        """
        grau_instrucao = 12
        try:
            grau_instrucao = pessoa_fisica.grau_instrucao
        except Exception:
            pass
        if grau_instrucao in (13, 14, None):
            grau_instrucao = 12
        return grau_instrucao

    def get_dado_bancario_pessoa_vigente(self, pessoa_fisica):
        """
        Este método retorna o DadoBancarioPessoa vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return DadoBancarioPessoa - dado_bancario_pessoa.
        """
        dado_bancario_pessoa = None
        try:
            dado_bancario_pessoa = DadoBancarioPessoa.objects.filter(
                dado_bancario_folhas__data_vigencia__gte=self._data_referencia_inicio,
                dado_bancario_folhas__data_vigencia__lte=self._data_referencia,
                pessoa=pessoa_fisica,
                dado_bancario_folhas__principal=True,
            ).order_by("-dado_bancario_folhas__data_vigencia")[0]
        except Exception:
            pass
        return dado_bancario_pessoa

    def get_banco(self, **kwargs):
        """
        Este método retorna o banco a partir do DadoBancarioPessoa vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return str - banco.
        """
        numero = ""
        try:
            numero = self.get_dado_bancario_pessoa_vigente(
                kwargs["objeto"]
            ).banco.numero
        except Exception:
            pass
        if numero == "":
            numero = self.compara_obrigatoriedade(**kwargs)
        return numero

    def get_agencia(self, **kwargs):
        """
        Este método retorna a agência a partir do DadoBancarioPessoa vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return str - agencia.
        """
        agencia = ""
        try:
            agencia = self.get_dado_bancario_pessoa_vigente(
                kwargs["objeto"]
            ).banco.agencia
        except Exception:
            pass
        if agencia == "":
            agencia = self.compara_obrigatoriedade(**kwargs)
        return agencia

    def get_dv_agencia(self, **kwargs):
        """
        Este método retorna o dígito verificador da agência a partir do DadoBancarioPessoa
            vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return str - dv da agencia.
        """
        dv_agencia = ""
        try:
            dv_agencia = self.get_dado_bancario_pessoa_vigente(
                kwargs["objeto"]
            ).banco.dv_agencia
        except Exception:
            pass
        dv_agencia = (
            self.compara_obrigatoriedade(**kwargs) if dv_agencia == "" else dv_agencia
        )
        return dv_agencia

    def get_conta(self, **kwargs):
        """
        Este método retorna a conta a partir do DadoBancarioPessoa vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return str - conta.
        """
        conta = ""
        try:
            conta = self.get_dado_bancario_pessoa_vigente(kwargs["objeto"]).banco.conta
        except Exception:
            pass
        conta = self.compara_obrigatoriedade(**kwargs) if conta == "" else conta
        return conta

    def get_dv_conta(self, **kwargs):
        """
        Este método retorna o dígito verificador da agência a partir do DadoBancarioPessoa
            vigente no ano e no mês de referência.
        @param PessoaFisica - pessoa_fisica.
        @param datetime - data_referencia.
        @return str - dv da conta.
        """
        dv_conta = ""
        try:
            dv_conta = self.get_dado_bancario_pessoa_vigente(
                kwargs["objeto"]
            ).banco.dv_conta
        except Exception:
            pass
        dv_conta = (
            self.compara_obrigatoriedade(**kwargs) if dv_conta == "" else dv_conta
        )
        return dv_conta


class DadosServidor(DadosPessoa):

    def __init__(self, **conf):
        self.current_possession = {}
        super(DadosServidor, self).__init__(**conf)

    def get_filename(self):
        return "ARQUIVO_SERVIDOR.txt"

    @staticmethod
    def get_matricula(servidor):
        """
        Este método retorna a matrícula do servidor.
        @param Servidor - servidor.
        @return str - matrícula.
        """
        matricula = ""
        try:
            matricula = str(servidor.matricula)
        except Exception:
            pass
        return matricula

    @staticmethod
    def get_registry_origin(employee):
        """
        Este método retorna a matrícula de origem do servidor.
        Caso não exista será retornado a matrícula.
        @param Servidor - servidor.
        @return str - matrícula.
        """
        registry = str(employee.matricula)
        if employee.matricula_origem:
            registry = str(employee.matricula_origem)
        return registry

    def get_posses(self, servidor):
        posses_ativas = None
        try:
            if self._importacao_completa:
                posses_ativas = servidor.posses.filter().exclude(
                    Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))
                )
            else:
                if servidor.member_type_by_possession:
                    posses_ativas = servidor.posses
                else:
                    posses_ativas = servidor.get_posses_ativas(
                        data_inicio=self._data_referencia,
                        data_fim=datetime(
                            self._data_referencia.year, self._data_referencia.month, 1
                        ).date(),
                    )
                    if not posses_ativas.exists():
                        posses_ativas = servidor.posses
                if (
                    not servidor.get_posses_ativas(
                        data_inicio=self._data_referencia,
                        data_fim=datetime(
                            self._data_referencia.year, self._data_referencia.month, 1
                        ).date(),
                    )
                    .filter(quadro__cargo__tipo_lei_cargo="AC")
                    .exists()
                ):
                    posses_ativas = posses_ativas.exclude(
                        Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))
                    )
        except Exception as err:
            log.exception(err)
        return posses_ativas

    @staticmethod
    def filter_comissao_funcao():
        return Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))

    def get_primeira_posse(self, servidor):
        """
        Retorna a primeira posse do servidor.
        """
        return self.get_posses(servidor).order_by("data_exercicio")[0]

    def get_posse_atual(self, servidor):
        """
        Este método retorna a posse atual do servidor.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - posse atual.
        """
        posse_atual = self.current_possession.get(servidor.matricula, None)
        try:
            if not posse_atual:
                posses_ativas = self.get_posses(servidor)
                if servidor.member_type_by_possession:
                    # posse_atual = posses_ativas.order_by('data_exercicio')[0]
                    posse_atual = posses_ativas.latest("data_exercicio")
                else:
                    posse_atual = (
                        posses_ativas.exclude(
                            Q(quadro__cargo__tipo_lei_cargo__in=("CM"))
                        )[0]
                        if posses_ativas.exists()
                        else None
                    )
                if not posse_atual:
                    cache = servidor.posses.exclude(
                        Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL"))
                    )
                    posse_atual = (
                        cache.latest("data_exercicio") if cache.exists() else None
                    )
                self.current_possession.update({servidor.matricula: posse_atual})
        except Exception as err:
            log.exception(err)
        return posse_atual

    def verifica_requisicao(self, servidor):
        requisicao = None
        try:
            requisicao = servidor.movimentacaopessoal_set.filter(
                Q(movimentacaorequisicao__ativo=True)
            )[0].movimentacaorequisicao
        except Exception:
            pass
        return requisicao

    def get_cargo_atual(self, servidor):
        """
        Este método retorna o cargo atual do servidor.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - o cargo atual.
        """
        posse_atual = self.get_posse_atual(servidor)
        cargo_atual = (
            DadosCargo.get_codigo(posse_atual.quadro.cargo) if posse_atual else ""
        )
        return cargo_atual

    def get_data_posse(self, servidor):
        """
        Este método retorna a data da posse atual do servidor.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - data da posse atual.
        """
        data_posse = ""
        try:
            data_posse = (
                DateUtils.date_to_str(self.get_primeira_posse(servidor).data_exercicio)
                if servidor.member_type_by_possession
                else DateUtils.date_to_str(
                    self.get_posse_atual(servidor).data_exercicio
                )
            )
        except Exception:
            pass
        return data_posse

    def get_orgao_atual(self, servidor):
        """
        Este método retorna o órgão atual do servidor. Considerando se há alguma cessão ativa do mesmo,
        até o mês de referência.
        Utiliza 991 como código padrão, pois é o valor utilizado, para o MPE-TO, no IGEPREV.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - código do órgão atual.
        """
        orgao_atual = Igeprev.get_orgao()
        try:
            mov_cessao = self.get_cessao(servidor)
            if mov_cessao:
                orgao_atual = DadosOrgao.get_codigo(mov_cessao[0].orgao_destino)
        except Exception:
            pass
        return orgao_atual

    def get_requisicao(self, servidor):
        mov_requisicao = None
        try:
            mov_requisicao = (
                servidor.movimentacaopessoal_set.filter(
                    movimentacaorequisicao__periodo__data_inicio__lte=self._data_referencia,
                    movimentacaorequisicao__periodo__data_fim__gte=self._data_referencia_inicio,
                )
                .latest("movimentacaorequisicao__periodo__data_inicio")
                .movimentacaorequisicao
            )
        except Exception:
            pass
        return mov_requisicao

    def get_cessao(self, servidor):
        mov_cessao = None
        try:
            q = Q(
                servidor=servidor,
                publicacao_movimentacao__data_vigencia__gte=self._data_referencia_inicio,
                data_fim__lte=self._data_referencia,
            )
            if self._importacao_completa:
                q = Q(servidor=servidor, ativo=True)
            mov_cessao = (
                AfastamentoOutroOrgao.objects.filter(q)
                .exclude(estado=CANCELADO)
                .order_by("-data_fim")
            )
        except Exception:
            pass
        return mov_cessao

    def get_orgao_origem(self, servidor):
        """
        Este método retorna o órgão de origem do servidor. Considerando se há alguma requisição ativa do mesmo,
        até o mês de referência.
        Utiliza 991 como código padrão, pois é o valor utilizado, para o MPE-TO, no IGEPREV.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - código do órgão de origem.
        """
        orgao_origem = Igeprev.get_orgao()
        try:
            mov_requisicao = self.get_requisicao(servidor)
            if mov_requisicao:
                orgao_origem = DadosOrgao.get_codigo(mov_requisicao[0].orgao_origem)
        except Exception:
            pass
        return orgao_origem

    @deprecated
    def get_lotacao(self, servidor):
        """
        Este método retorna a lotação em função da data de referência.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - código da lotação.
        """
        lotacao = self.get_lotacao_competencia(servidor)
        if not lotacao:
            servidor_lotacao = servidor.workplace
            if servidor_lotacao.exists():
                lotacao = DadosOrgao.get_codigo(
                    servidor_lotacao.latest("data_vigencia_inicio").lotacao
                )
        return str(lotacao)

    @deprecated
    def get_lotacao_competencia(self, servidor):
        """
        Este método retorna a lotação em função da data de referência.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - código da lotação.
        """
        lotacao = None
        servidor_lotacao = servidor.workplace.exclude(
            data_vigencia_inicio__gt=self._data_referencia
        )
        if servidor_lotacao.exists():
            lotacao = DadosOrgao.get_codigo(
                servidor_lotacao.latest("data_vigencia_inicio").lotacao
            )
        return lotacao

    def get_vinculo_ente(self, servidor):
        """
        Este método retorn o vínculo que o servidor possui com outro servidor.
        @param Servidor - servidor.
        @return str - vinculo.
        """
        vinculo = 3
        try:
            if self._importacao_completa:
                servidor_vinculo = servidor.servidor_vinculo.filter()
            else:
                servidor_vinculo = servidor.servidor_vinculo.filter(
                    data_alteracao__gte=self._data_referencia_inicio,
                    data_alteracao__lte=self._data_referencia,
                )
            if servidor_vinculo:
                vinculo = servidor_vinculo[0].vinculo
        except Exception:
            pass
        return vinculo

    def get_situacao_previdenciaria(self, servidor):
        """
        Este método retorna a situação previdenciária do servidor de acordo com a tabela 01 do manual do
        IGEPREV(ver @igeprev.const).
        @param Servidor - servidor
        """
        return servidor.get_situacao_previdenciaria(
            self._data_referencia_inicio,
            self._data_referencia,
            self._importacao_completa,
        )

    def get_situacao_funcional(self, servidor):
        parser = {
            # 0 EM EXERCÍCIO
            "ATIVO": 0,
            "ATIVO_AUS_SANGUE": 0,
            "ATIVO_AUS_ELEITOR": 0,
            "ATIVO_AUS_CASAMENTO": 0,
            "ATIVO_AUS_NASCIMENTO": 0,
            "ATIVO_AUS_FALECIMENTO": 0,
            "ATIVO_AUS_CONCLUSAO": 0,
            "ATIVO_FERIAS": 0,
            "ATIVO_VIAGEM": 0,
            "ATIVO_RECESSO": 0,
            "ATIVO_FOLGA_ELEITORAL": 0,
            "ATIVO_ATUACAO_GRUPO_TRAB": 0,
            "ATIVO_DESEMPENHO_FUNCAO": 0,
            "ATIVO_PLANTAO": 0,
            # 1 EXONERADO
            "INATIVO_EXONERADO_PEDIDO": 1,
            "INATIVO_EXONERADO_OFICIO": 1,
            # 4 CEDIDO COM ONUS
            "ATIVO_AFA_OUT_ORG_ONUS_MP": 4,
            # 5 CEDIDO SEM ONUS
            "ATIVO_AFA_OUT_ORG_SEM_ONUS_MP": 5,
            # 8 DEMITIDO
            "INATIVO_DEMITIDO": 8,
            # 9 EM DISPONIBILIDADE
            "ATIVO_DISPONIBILIDADE": 9,
            # 10 SEM VINCULO
            "NOT_FOUND": 10,
        }
        situacao_funcional = parser.get(servidor.situacao_funcional_cache, 10)
        if situacao_funcional == 10:
            if servidor.categoria in ("RFC", "RCM"):
                # 6 REQUISITADO COM ONUS
                situacao_funcional = 6
            elif servidor.categoria in ("REQ",):
                # 7 REQUISITADO SEM ONUS
                situacao_funcional = 7
            else:
                base = BaseLicencaAfastamento.objects.filter(
                    Q(estado=ACTIVE) & ~Q(afastamento=None) & ~Q(licenca=None)
                )
                if base.count():
                    # 2 LICENCIADO SEM REMUNERAÇÃ
                    # 3 LICENCIADO COM REMUNERAÇÃ0
                    situacao_funcional = 3 if base.remuneracao is True else 2
        return situacao_funcional

    def get_data_exoneracao(self, servidor):
        data_exoneracao = ""
        try:
            requisicao = self.verifica_requisicao(servidor)
            if requisicao:
                data_exoneracao = DateUtils.date_to_str(
                    requisicao.periodo.filter().order_by("data_inicio")[0].data_fim
                )
            elif self._importacao_completa:
                data_exoneracao = DateUtils.date_to_str(
                    servidor.movimentacaopessoal_set.filter().order_by(
                        "-movimentacaodesligamento__data_desligamento"
                    )[0]
                )
            else:
                data_exoneracao = DateUtils.date_to_str(
                    servidor.movimentacaopessoal_set.filter(
                        movimentacaodesligamento__data_desligamento__gte=self._data_referencia_inicio,
                        movimentacaodesligamento__data_desligamento__lte=self._data_referencia,
                    ).order_by("-movimentacaodesligamento__data_desligamento")[0]
                )
        except:
            pass
        return data_exoneracao

    def get_data_inicio_funcao(self, servidor):
        """
        Este método retorna a data de exercício do servidor.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - data de início.
        """
        data_exercicio = ""
        try:
            data_exercicio = DateUtils.date_to_str(
                self.get_posse_atual(servidor).data_exercicio
            )
        except Exception:
            pass
        return data_exercicio

    @staticmethod
    def get_data_ingresso_servico_publico(servidor):
        return ""

    def get_data_ingresso_carreira(self, servidor):
        """
        Este método retorna a data de ingresso na carreira.
        @param Servidor - servidor.
        @param datetime - data_referencia.
        @return str - data de ingresso.
        """
        data = ""
        posses_ativas = self.get_posses(servidor)
        try:
            if posses_ativas:
                data = self.get_data_inicio_funcao(servidor)
        except Exception:
            pass
        return data

    def get_aposentadoria(self, servidor):
        movimentacao = None
        try:
            if not self._importacao_completa:
                movimentacao = servidor.movimentacaopessoal_set.filter(
                    ~Q(movimentacaoaposentadoria=None)
                    & Q(data_desligamento__gte=self._data_referencia_inicio),
                    Q(data_desligamento__lte=self._data_referencia),
                )[0]
            else:
                movimentacao = servidor.movimentacaopessoal_set.filter(
                    ~Q(movimentacaoaposentadoria=None)
                )[0]
        except Exception:
            pass
        return movimentacao

    def get_tipo_beneficio(self, **kwargs):
        tipo = ""
        tipo_aposentadoria = 0
        try:
            tipo_aposentadoria = self.get_aposentadoria(
                kwargs["objeto"]
            ).tipo_aposentadoria
        except Exception:
            pass
        if tipo_aposentadoria == 1:
            tipo = 4
        elif tipo_aposentadoria == 3:
            tipo = 2
        elif tipo_aposentadoria == 4:
            tipo = 1
        elif tipo_aposentadoria == 5:
            tipo = 3
        tipo = self.compara_obrigatoriedade(**kwargs) if tipo == "" else tipo
        return tipo

    def get_data_requerimento_beneficio(self, **kwargs):
        data = ""
        try:
            data = DateUtils.date_to_str(
                self.get_aposentadoria(
                    kwargs["objeto"]
                ).publicacao_movimentacao.data_expedicao
            )
        except Exception:
            pass
        data = self.compara_obrigatoriedade(**kwargs) if data == "" else data
        return data

    def get_data_concessao_beneficio(self, **kwargs):
        data = ""
        try:
            data = DateUtils.date_to_str(
                self.get_aposentadoria(
                    servidor=kwargs["objeto"]
                ).publicacao_movimentacao.data_vigencia
            )
        except Exception:
            pass
        data = self.compara_obrigatoriedade(**kwargs) if data == "" else data
        return data

    @staticmethod
    def get_valor_inicial_beneficio(servidor):
        valor = ""
        return valor

    def get_classe_beneficio(self, **kwargs):
        classe = ""
        classe = self.compara_obrigatoriedade(**kwargs) if classe == "" else classe
        return classe

    def get_numero_ato_inativos(self, **kwargs):
        numero = ""
        numero = self.compara_obrigatoriedade(**kwargs) if numero == "" else numero
        return numero

    def get_data_ato_inativos(self, **kwargs):
        data = ""
        data = self.compara_obrigatoriedade(**kwargs) if data == "" else data
        return data

    def get_numero_publicacao_ato_inativos(self, **kwargs):
        numero = ""
        numero = self.compara_obrigatoriedade(**kwargs) if numero == "" else numero
        return numero

    def get_data_publicacao_ato_inativos(self, **kwargs):
        data = ""
        data = self.compara_obrigatoriedade(**kwargs) if data == "" else data
        return data

    @staticmethod
    def get_motivo_beneficio_militar(servidor):
        return ""

    def get_progressao_salarial(self, servidor):
        progressao = None
        try:
            if self._importacao_completa:
                progressao = servidor.movimentacaopessoal_set.filter()[
                    0
                ].movimentacaoprogressao
            else:
                progressao = servidor.movimentacaopessoal_set.filter(
                    movimentacaoprogressao__data__gte=self._data_referencia_inicio,
                    movimentacaoprogressao__data__lte=self._data_referencia,
                )[0].movimentacaoprogressao
        except Exception:
            pass
        return progressao

    def get_classe_salarial_atual(self, servidor):
        classe = ""
        try:
            classe = self.get_contra_cheque_normal(
                servidor
            ).referencia_salarial_efetivo.vertical
        except Exception:
            pass
        return classe

    def get_referencia_salarial_atual(self, servidor):
        referencia = ""
        try:
            referencia = self.get_contra_cheque_normal(
                servidor
            ).referencia_salarial_efetivo.horizontal
            referencia = self.get_contra_cheque_normal(
                servidor
            ).referencia_salarial_efetivo.horizontal
        except Exception:
            pass
        return referencia

    def get_cargo_origem(self, servidor):
        cargo = None
        try:
            cargo = self.get_cargo_atual(servidor)
        except Exception:
            pass
        return cargo

    def get_data_posse_origem(self, servidor):
        data = ""
        try:
            data = self.get_data_posse(servidor)
        except Exception:
            pass
        return data

    def get_contra_cheque_normal(self, servidor):
        try:
            return servidor.paychecks.get(
                folha__periodo__mes=self._data_referencia.month,
                folha__periodo__ano=self._data_referencia.year,
                folha__tipo_folha__principal=True,
            )
        except ContraCheque.DoesNotExist:
            log.info("Não existe folha principal!")
        except Exception:
            pass
        return None


class DadosCarreira(BaseDados):

    def get_filename(self):
        return "ARQUIVO_CARREIRAS.txt"

    @staticmethod
    def get_codigo(carreira):
        codigo = None
        try:
            codigo = carreira.pk
        except Exception:
            pass
        return codigo

    @staticmethod
    def get_descricao(carreira):
        return str(carreira)


class DadosCargoCarreira(BaseDados):

    @staticmethod
    def get_poder(cargo):
        """
        Este método retorna o poder do cargo.
        @param OrgaoGeral - orgao.
        @return int - poder.
        """
        poder = None
        if cargo:
            try:
                poder = cargo.poder
            except Exception:
                pass
        return poder

    @staticmethod
    def get_orgao(cargo):
        orgao = None
        try:
            orgao = DadosOrgao.get_codigo(cargo.unidade_administrativa)
        except Exception:
            pass
        orgao = Igeprev.get_orgao() if orgao is None else orgao
        return orgao

    @staticmethod
    def get_carreira(cargo):
        """
        Este método retorna o código da carreira.
        @param Cargo - cargo.
        @return int - carreira.
        """
        carreira = None
        try:
            carreira = cargo.carreira.pk
        except Exception:
            pass
        return carreira

    @staticmethod
    def get_cargo(cargo):
        """
        Este método retorna o código do cargo.
        @param Cargo - Cargo.
        @return int - codigo.
        """
        codigo = None
        try:
            codigo = str(cargo.codigo)
        except Exception:
            pass
        return codigo


class DadosRemuneracao(BaseDados):

    _mes_referencia = None

    def __init__(self, **conf):
        super(DadosRemuneracao, self).__init__(**conf)

    @staticmethod
    def get_tipo_participante(servidor):
        """
        Este método retornar o tipo do participante: S-SERVIDOR, P-PENSIONISTA.
        No caso do MP sempre será S, pois esta instutuição não paga pensionista(aposentado).
        """
        return "S"

    def get_tipo_remuneracao(self, servidor):
        if self._mes_referencia == 13:
            return 13
        return 1

    @staticmethod
    def get_salario_bruto(remuneracao):
        salario = ""
        return salario

    @staticmethod
    def get_salario_liquido(remuneracao):
        liquido = ""
        try:
            liquido = remuneracao.valor
        except Exception:
            pass
        return liquido

    @staticmethod
    def get_contribuicao_patronal(remuneracao):
        patronal = ""
        try:
            patronal = remuneracao.patronal
        except Exception:
            pass
        return patronal

    @staticmethod
    def get_contribuicao_segurado(remuneracao):
        contribuicao = ""
        return contribuicao

    @staticmethod
    def get_salario_contribuicao(servidor):
        contribuicao = ""
        return contribuicao

    def calculo(self, servidor, folha, event_to_filter=[]):
        try:
            bruto = 0
            desconto = 0
            patronal = 0
            liquido = 0
            valor_base = 0
            contribuicao = 0
            valor_irrf = 0
            paycheck = (
                servidor.paychecks.filter(
                    pensioner=None,
                    folha__periodo__mes=(
                        self._data_referencia.month
                        if self._mes_referencia != 13
                        else 13
                    ),
                    folha__periodo__ano=self._data_referencia.year,
                    folha__pk=folha,
                )
                .exclude(status__in=(4, 5))
                .latest("pk")
            )
            for folha_evento in paycheck.lancamentos.all():
                if folha_evento.evento.tipo == "P" and folha_evento.evento.carater in [
                    1,
                    9,
                    13,
                    15,
                    21,
                ]:
                    bruto += folha_evento.valor
                else:
                    desconto += folha_evento.valor

                if folha_evento.evento.numero == "99900":
                    valor_irrf += folha_evento.valor

            try:
                folha_evento = paycheck.lancamentos.filter(
                    evento__genre_event__genre_number__in=event_to_filter
                )
                for fe in folha_evento:
                    valor_base += fe.valor_base
                    contribuicao += fe.value
                    patronal += fe.employer_contribution
            except Exception as err:
                log.exception(err)
        except ContraCheque.DoesNotExist:
            log.info("Não existe folha principal!")
        except Exception as err:
            log.exception(err)
        return bruto, liquido, valor_base, contribuicao, patronal, valor_irrf

    @classmethod
    def remuner(cls, servidor, folha):
        return (
            FolhaEvento.objects.filter(
                contracheque__servidor=servidor,
                contracheque__folha=folha,
                evento__carater__in=[1, 9, 13, 15, 21],
            )
            .aggregate(valor=Sum("value"))
            .get("valor")
            or 0
        )

    @classmethod
    def remunera(cls, servidor, folha):
        return FolhaEvento.objects.get(
            contracheque__servidor=servidor,
            contracheque__folha=folha,
            evento__numero__in=["90000", "90500"],
        ).valor_base

    @classmethod
    def fundo(cls, folhaevento):
        if folhaevento.evento.numero == "90000":
            return 2
        elif folhaevento.evento.numero == "90500":
            return 1
        return 0

    @classmethod
    def tempo_anterior_rgps(cls, servidor):
        days = 0
        if hasattr(servidor.pessoa_fisica, "retirementprevision"):
            days = servidor.pessoa_fisica.retirementprevision.rgps_liquid_days or 0
        return int(days)

    @classmethod
    def tempo_outro_rpps(cls, servidor):
        return 0


class DadosAfastamento(BaseDados):

    def __init__(self, **conf):
        super(DadosAfastamento, self).__init__(**conf)

    def get_orgao_destino(self, **kwargs):
        orgao_destino = ""
        try:
            orgao_destino = DadosOrgao.get_codigo(kwargs["objeto"].orgao_destino)
        except Exception:
            pass
        orgao_destino = (
            self.compara_obrigatoriedade(**kwargs)
            if orgao_destino == ""
            else orgao_destino
        )
        return orgao_destino

    @staticmethod
    def get_cargo_destino(afastamento):
        cargo = ""
        try:
            cargo = DadosCargo.get_codigo(afastamento.quadro_destino.cargo)
        except Exception:
            pass
        return cargo

    @staticmethod
    def get_data_inicio(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(afastamento.data_inicio)
        except Exception:
            pass
        return data

    @staticmethod
    def get_data_fim(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(afastamento.data_fim)
        except Exception:
            pass
        return data

    @staticmethod
    def get_codigo(afastamento):
        codigo = ""
        if hasattr(afastamento, "afastamento"):
            if hasattr(afastamento.afastamento, "afastamentomandatoeletivo"):
                # 5: u'MANDATO ELETIVO',
                codigo = 5
            elif hasattr(afastamento.afastamento, "afastamentooutroorgao"):
                # 1: u'A DISPOSIÇÃO COM ONUS PARA O REQUISITANTE',
                # 2: u'A DISPOSIÇÃO COM ONUS PARA O ORIGEM',
                codigo = (
                    2 if afastamento.afastamento.afastamentooutroorgao.onus == 1 else 1
                )
        elif hasattr(afastamento, "licenca"):
            if hasattr(afastamento.licenca, "licencaafastamentoconjuge"):
                # 4: u'LICENÇA PARA ACOMPANHAMENTO DE CÔNJUGE',
                codigo = 4
            elif hasattr(afastamento.licenca, "licencainteresseparticular"):
                # 3: u'LICENÇA PARA TRATAR DE INTERESSES PARTICULARES',
                codigo = 3
            elif hasattr(afastamento.licenca, "licencamandatoclassista"):
                # 6: u'REPRESENTAÇÃO SINDICAL',
                codigo = 6
        return codigo

    def get_ato(self, **kwargs):
        numero = ""
        try:
            numero = kwargs["objeto"].publicacao_movimentacao.numero
        except Exception:
            pass
        numero = self.compara_obrigatoriedade(**kwargs) if numero == "" else numero
        return numero

    @staticmethod
    def get_data_publicacao_do(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(
                afastamento.publicacao_movimentacao.data_publicacao
            )
        except Exception:
            pass
        return data

    @staticmethod
    def get_numero_publicacao_do(afastamento):
        numero = ""
        try:
            numero = afastamento.publicacao_movimentacao.numero_publicacao
        except Exception:
            pass
        return numero

    @staticmethod
    def get_data_revogacao(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(afastamento.publicacao_revogacao.data_vigencia)
        except Exception:
            pass
        return data

    @staticmethod
    def get_data_retorno(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(afastamento.data_retorno)
        except Exception:
            pass
        return data

    @staticmethod
    def get_data_publicacao_do_revogacao(afastamento):
        data = ""
        try:
            data = DateUtils.date_to_str(
                afastamento.publicacao_revogacao.data_publicacao
            )
        except Exception:
            pass
        return data

    @staticmethod
    def get_numero_publicacao_do_revogacao(afastamento):
        numero = ""
        try:
            numero = afastamento.publicacao_revogacao.numero
        except Exception:
            pass
        return numero

    def get_opcao_contribuicao(self, **kwargs):
        contribuicao = 2
        try:
            contribuicao = kwargs["objeto"].contribuicao
        except Exception:
            pass
        opcao_contribuicao = (
            self.compara_obrigatoriedade(**kwargs) if contribuicao else ""
        )
        return opcao_contribuicao


class DadosDependente(DadosPessoa):

    @staticmethod
    def get_tipo_capacidade(dependente):
        return dependente.capacidade

    @staticmethod
    def get_grau_parentesco(dependente):
        grau = ""
        try:
            grau = dependente.grau_parentesco
        except Exception:
            pass
        if grau == 1:
            grau = 2
        elif grau == 2:
            grau = 3
        elif grau == 3:
            grau = 0
        elif grau == 4:
            grau = 5
        elif grau == 5:
            grau = 8
        elif grau == 6:
            grau = 4
        elif grau == 7:
            grau = 6
        elif grau == 8:
            grau = 7
        elif grau == 9:
            grau = 1
        elif grau == 10:
            grau = 9
        return grau

    @staticmethod
    def get_data_inicio_dependente(dependente):
        data = ""
        try:
            data = DateUtils.date_to_str(dependente.data_inicio)
        except Exception:
            pass
        return data

    @staticmethod
    def get_motivo_inicio_dependente(dependente):
        motivo = ""
        try:
            motivo = dependente.motivo_inicio_dependencia
        except Exception:
            pass
        return motivo

    @staticmethod
    def get_data_termino_dependencia(dependente):
        data = ""
        try:
            data = DateUtils.date_to_str(dependente.data_fim)
        except Exception:
            pass
        return data

    @staticmethod
    def get_motivo_fim_dependencia(dependente):
        motivo = ""
        try:
            motivo = dependente.motivo_fim_dependencia
        except Exception:
            pass
        return motivo

    @staticmethod
    def get_tipo_dependencia(dependente):
        tipo = ""
        try:
            tipo = dependente.tipo
        except Exception:
            pass
        return tipo

    @staticmethod
    def get_tipo_beneficio(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_percentual_pensao(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_matricula_pensionista(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_concessao(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_termino_concessao(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_requerimento_concessao(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_valor_inicial(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_classe_beneficio(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_numero_ato(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_ato(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_numero_publicacao_do_ato(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_publicacao_do_ato(dependente):
        """
        Este método retorna valor apenas para pensionista.
        """
        return ""

    @staticmethod
    def get_data_prevista_termino_dependencia(dependente):
        return DadosDependente.get_data_termino_dependencia(dependente)


class DadosUnidade(DadosOrgao):

    def get_filename(self):
        return "ARQUIVO_UNIDADES.txt"


class DadosCargo(BaseDados):

    @staticmethod
    def get_poder(cargo):
        """
        Este método retorna o poder do cargo.
        @param OrgaoGeral - orgao.
        @return int - poder.
        """
        poder = None
        if cargo:
            try:
                poder = cargo.poder
            except Exception:
                pass
        return poder

    @staticmethod
    def get_orgao(cargo):
        """
        Este método retorna o código do órgão.
        @param Cargo - cargo.
        @return int - codigo
        """
        orgao = None
        try:
            orgao = DadosOrgao.get_codigo(cargo.unidade_administrativa)
        except Exception:
            pass
        if orgao is None:
            orgao = Igeprev.get_orgao()
        return orgao

    @staticmethod
    def get_codigo(cargo):
        """
        Este método retorna o código do cargo.
        @param Cargo - cargo.
        @return unicode - codigo
        """
        codigo = ""
        try:
            codigo = str(cargo.codigo)
        except Exception:
            pass
        return codigo

    @staticmethod
    def get_descricao(cargo):
        """
        Este método retorna a descrição do cargo.
        @param Cargo - cargo.
        @return unicode - descricao.
        """
        descricao = ""
        try:
            descricao = str(cargo)
        except Exception:
            pass
        return descricao

    @staticmethod
    def get_cargo_quadro(cargo):
        cargo_quadro = ""
        try:
            cargo_quadro = cargo.quadros.filter()[0]
        except Exception:
            pass
        return cargo_quadro

    @staticmethod
    def get_data_inicio_cargo(cargo):
        """
        Este método retorna a data de início da vigência do cargo.
        @param Cargo - cargo.
        @return str - data.
        """
        data_inicio = ""
        try:
            data_inicio = DateUtils.date_to_str(
                DadosCargo.get_cargo_quadro(cargo).publicacao_criacao.data_vigencia
            )
        except Exception:
            try:
                data_inicio = DateUtils.date_to_str(cargo.data_alteracao)
            except Exception:
                pass
        return data_inicio

    @staticmethod
    def get_data_fim(cargo):
        """
        Este método retorna a data de fim da vigência do cargo.
        @param Cargo - cargo.
        @return str - data.
        """
        data_fim = ""
        try:
            data_fim = DateUtils.date_to_str(
                DadosCargo.get_cargo_quadro(cargo).publicacao_extincao.data_vigencia
            )
        except Exception:
            pass
        return data_fim

    @staticmethod
    def get_nome_grupo_salarial(cargo):
        """
        Este método retorna o nome do grupo salarial relacionado ao cargo.
        @param Cargo - cargo.
        @return unicode - grupo_salarial.
        """
        grupo_salarial = ""
        try:
            grupo_salarial = DadosGrupoSalarial.get_nome(
                cargo.salarios_do_cargo.filter()[0].salario
            )
        except Exception:
            pass
        return grupo_salarial


class DadosProgressao:

    @staticmethod
    def get_cargo(progressao):
        return progressao.movimentacao_posse.quadro.cargo.codigo

    @staticmethod
    def get_data_posse(progressao):
        # MODIFICANDO PARA DATA EXERCÍCIO CONFORME SOLICITAÇÃO DO IGEPREV
        # return DateUtils.date_to_str(progressao.movimentacao_posse.data_posse)
        return DateUtils.date_to_str(progressao.movimentacao_posse.data_exercicio)

    @staticmethod
    def get_data_inicio_vigencia(progressao):
        data = ""
        try:
            data = DateUtils.date_to_str(progressao.data_vigencia)
        except Exception:
            pass
        return data

    @staticmethod
    def get_data_fim_vigencia(progressao):
        data = ""
        try:
            data = DateUtils.date_to_str(progressao.data_vigencia_fim)
        except Exception:
            pass
        return data

    @staticmethod
    def get_grupo_salario(progressao):
        return DadosGrupoSalarial.get_nome(progressao.salario)

    @staticmethod
    def get_classe(progressao):
        return DadosGrupoSalarial.get_classe(progressao.salario)

    @staticmethod
    def get_referencia(progressao):
        return DadosGrupoSalarial.get_referencia(progressao.salario)

    @staticmethod
    def get_salario(progressao):
        return DadosGrupoSalarial.get_salario(progressao.salario)


class DadosGrupoSalarial:

    @staticmethod
    def get_poder(salario):
        """
        Este método retorna o poder do órgão.
        @param OrgaoGeral - orgao.
        @return int - poder.
        """
        poder = None
        if salario:
            try:
                poder = salario.referencia_nivel2d.cargos.filter()[0].poder
            except Exception:
                pass
        return poder

    @staticmethod
    def get_nome(salario):
        nome = ""
        try:
            nome = str(salario.tabela_salarial.estrutura_salarial.codigo)
        except Exception:
            pass
        return nome

    @staticmethod
    def get_descricao(salario):
        return DadosGrupoSalarial.get_nome(salario)

    @staticmethod
    def get_classe(salario):
        classe = ""
        try:
            classe = str(salario.referencia_nivel2d.nivel_vertical.valor)
        except Exception:
            pass
        return classe

    @staticmethod
    def get_referencia(salario):
        referencia = "1"
        try:
            referencia = str(salario.referencia_nivel2d.nivel_horizontal.valor)
        except Exception:
            pass
        return referencia

    @staticmethod
    def get_data_inicio(salario):
        data_inicio = ""
        try:
            data_inicio = DateUtils.date_to_str(salario.tabela_salarial.start_validity)
        except Exception:
            pass
        return data_inicio

    @staticmethod
    def get_data_fim(salario):
        data_fim = ""
        try:
            data_fim = (
                DateUtils.date_to_str(salario.tabela_salarial.end_validity)
                if salario.tabela_salarial.end_validity
                else ""
            )
        except Exception:
            pass
        return data_fim

    @staticmethod
    def get_salario(salario):
        valor = ""
        try:
            valor = salario.valor
        except Exception:
            pass
        return valor
