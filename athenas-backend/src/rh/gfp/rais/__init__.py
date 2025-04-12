# -*- coding: utf-8 -*-

from datetime import date, datetime

from django.conf import settings
from django.db.models import Q, Sum

from contrib import protofile
from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.helpers import clear_to_ascii
from contrib.utils import getLogger
from rh.afastamento.models import BaseLicencaAfastamento
from rh.gfp.models import Evento, FolhaEvento
from rh.models import Servidor, UnidadeAdministrativa
from standard.models import Configuration

MATRICULAS_DEBUG = [
    39001,
    23399,
    120513,
    # 126214,# 91108, 32201, 104210, 71707, 116812, 91608, 93708, 66607, 111511, 83408, 10892, 103410, 10792, 78607,
    # 105810, 66007, 4814088, 102010, 117912, 97809, 120513
]


log = getLogger(__name__)


class Registro(protofile.Record):

    @property
    @cache_return
    def _protocol(self):
        return File.get_config(self.ano_base)

    def __init__(self, ano_base, tipo, **kargs):
        """ """
        self.ano_base = ano_base
        self.range_ano_base = NewDateRange(
            date(self.ano_base, 1, 1), date(self.ano_base, 12, 31)
        )
        kargs.update(ano_base=ano_base)
        super(Registro, self).__init__(tipo, **kargs)


class RegistroServidor(Registro):
    evts13 = [x.numero for x in Evento.objects.filter(nature_of_event__code="5001")]
    _FERIAS_INDENIZADA = [
        "0147",
        "0152",
        "0213",
        "0221",
        "0223",
        "0226",
        "05300",
        "05400",
        "05500",
        "05600",
    ]
    _ACERTO_GRATIFICACAO_NATALINA = [
        "01700",
        "01702",
        "01707",
        "1302",
        "1780",
        "1305",
        "01500",
        "01501",
        "01502",
        "01506",
        "01706",
    ]
    _GRATIFICACAO_NATALINA = list(
        set(["1305", "01500", "01501", "01502", "01506", "5140", "01602", "49800"])
        | set(evts13)
    )
    _ADIANTAMENTO_GRATIFICACAO_NATALINA = [
        "0109",
        "01600",
        "01601",
        "01606",
        "01607",
        "01608",
    ]
    _ABONO_PASEP = ["0261"]
    _OUTROS_EVENTOS = [
        "03000",
        "03001",
        "03100",
        "03500",
        "03511",
        "03513",
        "03600",
        "03700",
        "04903",
        "0598",
        "0599",
        "06000",
        "06600",
        "06601",
        "06602",
        "06606",
        "06607",
        "06608",
        "06700",
        "06702",
        "06703",
        "06706",
        "5259",
        "5318",
        "5319",
        "5501",
    ]

    def get_posses(self):
        return self.servidor.get_posses_ativas(
            date(self.ano_base, 1, 1), date(self.ano_base, 12, 31)
        ).order_by("-data_exercicio")

    def posse_ef(self):
        return (
            self.get_posses()
            .filter(quadro__cargo__tipo_lei_cargo__in=("EF",))
            .order_by("-data_exercicio")
            .last()
        )

    def posse_ac(self):
        return self.get_posses().get(requestmove__isnull=False).requestmove

    def posse_cmfc(self):
        return (
            self.get_posses()
            .filter(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
            .order_by("-data_exercicio")
            .last()
        )

    def get_documento(self, doc, ifnone):
        pf = self.servidor.pessoa_fisica
        return (
            pf.documento.filter(tipo_documento=doc)[0]
            if pf.documento.filter(tipo_documento=doc).exists()
            else ifnone
        )

    @property
    @cache_return
    def ferias_indenizada(self):
        query = self.servidor.entries.filter(
            folha__periodo__ano=self.ano_base,
            evento__numero__in=self._FERIAS_INDENIZADA,
        )

        return float(query.aggregate(total=Sum("valor")).get("total") or 0)

    @property
    @cache_return
    def grau_instrucao(self):
        de_para = {
            1: 1,
            2: 2,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
            7: 8,
            8: 9,
            9: 9,
            10: 10,
            11: 11,
            12: 11,
            13: 11,
            14: 11,
        }

        return de_para.get(self.servidor.pessoa_fisica.grau_instrucao)

    @property
    @cache_return
    def data_admissao(self):
        return self.servidor.exercise_date.strftime("%d%m%Y")

    @property
    @cache_return
    def data_nascimento(self):
        return self.servidor.pessoa_fisica.data_nascimento.strftime("%d%m%Y")

    @property
    @cache_return
    def nacionalidade(self):
        return 10

    @property
    @cache_return
    def ctps(self):
        ctps = self.get_documento(3, None)

        return {
            "numero": (
                ctps.numero.replace(",", "").replace(".", "").replace("-", "")
                if ctps is not None and ctps.numero
                else 0
            ),
            "serie": (
                ctps.ctps_series.valor.replace(",", "")
                .replace(".", "")
                .replace("-", "")
                .zfill(5)
                if ctps is not None and ctps.ctps_series
                else ""
            ),
        }

    @property
    @cache_return
    def cbo(self):
        try:
            query = self.posse_ac()
        except:
            query = self.posse_ef()
        if not query:
            query = self.posse_cmfc()

        cbo = "0"
        if query:
            if query.quadro and query.quadro.cargo:
                cbo = query.quadro.cargo.current_config.cbo.codigo
            if hasattr(query, "requestmove"):
                cbo = query.requestmove.cbo.codigo if query.requestmove.cbo else "0"
        return cbo

    @property
    @cache_return
    def raca_cor(self):
        s = self.servidor
        # ATHENAS -> RAIS
        de_para_raca = {6: 2, 1: 8, 2: 6, 3: 4, 4: 1, 5: 9}

        return de_para_raca.get(s.pessoa_fisica.raca_cor, 0)

    @property
    @cache_return
    def pasep(self):
        pasep = self.get_documento(6, None)
        return pasep.numero if pasep is not None else 0

    @property
    @cache_return
    def salario_contratual(self):
        query = self.get_posses()
        range_posses = NewDateRange()
        salario = gratificacao = 0.0
        for p in query:
            range_posses += self.range_ano_base.intersect(
                NewDateRange(p.data_exercicio, p.data_desligamento)
            )

        if query.filter(requestmove__isnull=False).exists():
            log.info("Servidor %s é requisitado" % self.servidor)
            posse_ac = self.posse_ac()
            req = (
                posse_ac.periods.filter(data_inicio__lt=range_posses.last)
                .order_by("-data_inicio")
                .first()
                .request_move
            )
            encargos_financeiro = (
                req.encargos_financeiros.filter(data_inicio__lt=range_posses.last)
                .order_by("-data_inicio")
                .first()
            )
            salario = (
                float(encargos_financeiro.remuneracao) if encargos_financeiro else 0.0
            )
        elif query.filter(quadro__cargo__tipo_lei_cargo__in=("EF",)).exists():
            log.info("Servidor %s é efetivo" % self.servidor)
            posse_ef = self.posse_ef()
            if posse_ef.quadro.cargo.indicativo == "M":
                referencia = None
            else:
                prog = posse_ef.progressoes.filter().order_by("-data_vigencia")[0]
                referencia = prog.referencia_nivel2d
            sal = posse_ef.quadro.cargo.get_salarios(
                self.range_ano_base.first, self.range_ano_base.last, referencia
            )[0]
            salario = sal[1].valor
        if query.filter(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]).exists():
            log.info("Servidor %s é comissionado/função" % self.servidor)
            posse_cm_fc = self.posse_cmfc()
            sal = posse_cm_fc.quadro.cargo.get_salarios(
                self.range_ano_base.first, self.range_ano_base.last
            )[0]
            if sal[1].valor > salario:
                salario = sal[1].valor
            gratificacao = sal[1].gratificacao

        total = float(salario) + float(gratificacao)

        return total

    @property
    @cache_return
    def gratificacao_natalina(self):
        obj = {
            "mes_adiantamento": 0,
            "mes_final": 0,
            "valor_adiantamento": 0.00,
            "valor_final": 0.00,
        }

        # query = self.servidor.entries.filter(
        #     folha__periodo__ano = self.ano_base
        # )
        query = (
            FolhaEvento.objects.filter(contracheque__servidor=self.servidor)
            .filter(folha__periodo__ano=self.ano_base)
            .order_by("folha__periodo__mes")
        )
        q_adiantamento = query.filter(
            evento__numero__in=self._ADIANTAMENTO_GRATIFICACAO_NATALINA,
            folha__periodo__mes__lt=12,
            evento__tipo="P",
            status="CT",
        )

        if q_adiantamento:
            fe = q_adiantamento.first()
            # mes adiantamento
            obj.update(mes_adiantamento=fe.folha.periodo.mes)

            # valor adiantamento
            obj.update(
                valor_adiantamento=q_adiantamento.aggregate(total=Sum("value")).get(
                    "total", 0
                )
            )

        _GRATIFICACAO = self._ACERTO_GRATIFICACAO_NATALINA + self._GRATIFICACAO_NATALINA
        q_gratificacao = query.filter(evento__numero__in=_GRATIFICACAO)

        if q_gratificacao.filter(folha__periodo__mes=13).exists():
            mes_final = 12
        elif q_gratificacao.exists():
            mes_final = q_gratificacao.first().folha.periodo.mes
        else:
            mes_final = 0

        obj.update(
            {
                "mes_final": mes_final,
                "valor_final": q_gratificacao.aggregate(total=Sum("value")).get("total")
                or 0,
            }
        )

        if obj.get("valor_final") < 0:
            obj.update({"valor_final": 0.0})

        return obj

    @property
    @cache_return
    def sexo(self):
        s = self.servidor
        return 1 if s.pessoa_fisica.sexo == "M" else 2

    def remuneracao(self, mes):
        exclude_evento = (
            self._FERIAS_INDENIZADA
            + self._ACERTO_GRATIFICACAO_NATALINA
            + self._GRATIFICACAO_NATALINA
            + self._ADIANTAMENTO_GRATIFICACAO_NATALINA
            + self._ABONO_PASEP
            + self._OUTROS_EVENTOS
        )

        if self.desligamento.get("tipo") > 0:
            dmes = int(self.desligamento.get("data", "0000")[2:])
            # log.info('desligamento no mês %d' % dmes)
            if mes > dmes:
                return 0.00

        query = (
            FolhaEvento.objects.filter(contracheque__servidor=self.servidor)
            .filter(
                folha__periodo__ano=self.ano_base,
                folha__periodo__mes=mes,
                evento__carater__in=[1, 9, 13, 15, 21],
            )
            .exclude(folha__tipo_folha__carater=3)
            .exclude(evento__numero__in=exclude_evento)
        )

        total = float(query.aggregate(total=Sum("value")).get("total") or 0)
        return total if total >= 0 else 0

    @property
    @cache_return
    def municipio_trabalho(self):
        try:
            ibge = self.servidor.servidor_lotacao.get(
                ativo=True, designacao=False
            ).lotacao.localidade.ibge
        except:
            ibge = 0
        finally:
            return ibge if ibge is not None else 0

    @property
    @cache_return
    def tipo_admissao(self):
        tipo = 2
        for posse in self.get_posses().exclude(requestmove=None):
            tipo = (
                3
                if posse.requestmove.periods.exclude(
                    Q(data_inicio__gt=date(self.ano_base, 12, 31))
                    | Q(data_fim__lt=date(self.ano_base, 1, 1))
                )
                .filter(request_move__onus=1)
                .exists()
                else 4
            )
        return tipo

    @property
    @cache_return
    def desligamento(self):
        obj = {"tipo": 0, "data": ("0" * 4), "desligamento": None}

        if (
            self.get_posses().exists()
            and self.servidor.get_posses_ativas(date(self.ano_base, 12, 31)).exists()
            is False
        ):
            try:
                posse = self.get_posses().order_by("-data_desligamento")[0]
                desligamento = posse.desligamento
            except Exception as e:
                log.warn(
                    "não consegui definir o desligamento do servidor %s" % self.servidor
                )
                log.warn(
                    "Não consegui encontrar o desligamento para o servidor inativo %s"
                    % self.servidor
                )
                log.exception(e)
            else:
                obj = {
                    "tipo": 11 if desligamento.opcao == 2 else 21,
                    "data": desligamento.data_desligamento.strftime("%d%m"),
                    "desligamento": desligamento,
                }
        elif (
            self.servidor.posses.exclude(afastamento=None)
            .filter(
                afastamento__publicacao_movimentacao__data_vigencia__year=self.ano_base,
                afastamento__data_fim=None,
            )
            .exists()
            is True
        ):
            """
            Verifica se o servidor tem alguma cessão
            """
            query = self.servidor.posses.exclude(afastamento=None).filter(
                afastamento__publicacao_movimentacao__data_vigencia__year=self.ano_base,
                afastamento__data_fim=None,
            )

            cessao = None
            try:
                cessao = query.get().afastamento.get()
            except:
                cessao = (
                    query[0]
                    .afastamento.get(
                        Q(
                            publicacao_movimentacao__data_vigencia__range=[
                                date(self.ano_base, 1, 1),
                                date(self.ano_base, 12, 31),
                            ]
                        )
                    )
                    .filter(
                        Q(data_fim=None) | Q(data_fim__gt=date(self.ano_base, 12, 31))
                    )
                )
                log.warn(
                    "Servidor %s com mais de uma posse com cessão para outros orgão."
                    % self.servidor
                )
            finally:
                if cessao is not None:
                    pub = cessao.publicacao_movimentacao
                    obj = {
                        "tipo": 33,
                        "data": (
                            pub.data_vigencia.strftime("%d%m")
                            if pub.data_vigencia is not None
                            else ("0" * 6)
                        ),
                        "desligamento": cessao,
                    }
                else:
                    log.warn(
                        "Problema conseguindo informações da cessão do %s"
                        % self.servidor
                    )

        return obj

    @property
    @cache_return
    def afastamentos(self):
        obj = {1: {}, 2: {}, 3: {}, "total": 0}

        query = (
            BaseLicencaAfastamento.objects.filter(
                Q(servidor=self.servidor) & Q(remunerado=False)
            )
            .exclude(
                Q(data_fim__lt=date(self.ano_base, 1, 1))
                | Q(data_inicio__gt=date(self.ano_base, 12, 31))
            )
            .order_by("data_inicio")
        )

        range_afastamentos = NewDateRange()
        idx = 1
        for afa in query:

            if (
                hasattr(afa, "afastamento")
                and hasattr(afa.afastamento, "afastamentooutroorgao")
                and (
                    afa.afastamento.afastamentooutroorgao.onus == 1
                    or afa.afastamento.afastamentooutroorgao.transito_pela_folha is True
                )
            ):
                log.debug(
                    "AFASTAMENTO(%s/%s): %s - %s: %s"
                    % (
                        afa.afastamento.afastamentooutroorgao.onus,
                        afa.afastamento.afastamentooutroorgao.transito_pela_folha,
                        afa.data_inicio,
                        afa.data_fim,
                        afa,
                    )
                )
            else:
                log.debug(
                    "AFASTAMENTO: %s - %s: %s" % (afa.data_inicio, afa.data_fim, afa)
                )

                if idx <= 3:
                    range_afa = self.range_ano_base.intersect(
                        NewDateRange(afa.data_inicio, afa.data_fim)
                    )
                    obj[idx]["motivo"] = 70  # Licença sem remuneração
                    obj[idx]["inicio"] = range_afa.first.strftime("%d%m")
                    obj[idx]["fim"] = range_afa.last.strftime("%d%m")
                    range_afastamentos += range_afa
                    idx += 1

        obj["total"] = range_afastamentos.days

        return obj

    def categoria(self):
        return 302 if self.servidor.type_by_possession == "CMS" else 301

    def __init__(self, ano_base, servidor, sequence):
        self.servidor = servidor
        self.ano_base = ano_base
        self.range_ano_base = NewDateRange(
            date(self.ano_base, 1, 1), date(self.ano_base, 12, 31)
        )

        cfg = Configuration.get_or_create("gfp")
        uadm = UnidadeAdministrativa.objects.get(pk=cfg.get("orgao"))
        _ = clear_to_ascii
        log.debug(
            "%s (%s) %s"
            % (sequence, self.gratificacao_natalina.get("valor_final", 0.0), servidor)
        )
        s = self.servidor
        Registro.__init__(
            self,
            ano_base,
            "reg-02",
            **{
                "sequencial": sequence,
                "cnpj": uadm.pessoa_juridica.cnpj,
                "razao": _(uadm.pessoa_juridica.razao_social),
                "nome": _(s.pessoa_fisica.nome),
                "cpf": s.pessoa_fisica.cpf,
                "pasep": self.pasep,
                "data_admissao": self.data_admissao,
                "data_nascimento": self.data_nascimento,
                "nacionalidade": self.nacionalidade,
                "ctps_numero": self.ctps.get("numero") or 0,
                "ctps_serie": self.ctps.get("serie") or "",
                "tipo_admissao": self.tipo_admissao,
                "data_desligamento": self.desligamento.get("data"),
                "codigo_desligamento": self.desligamento.get("tipo"),
                "horas_semanais": 40,
                "cbo": self.cbo,
                "vinculo_empregaticio": 30,
                "grau_instrucao": self.grau_instrucao,
                "municipio_trabalho": self.municipio_trabalho,
                "salario_contratual": self.salario_contratual,
                "remuneracao_01": self.remuneracao(1),
                "remuneracao_02": self.remuneracao(2),
                "remuneracao_03": self.remuneracao(3),
                "remuneracao_04": self.remuneracao(4),
                "remuneracao_05": self.remuneracao(5),
                "remuneracao_06": self.remuneracao(6),
                "remuneracao_07": self.remuneracao(7),
                "remuneracao_08": self.remuneracao(8),
                "remuneracao_09": self.remuneracao(9),
                "remuneracao_10": self.remuneracao(10),
                "remuneracao_11": self.remuneracao(11),
                "remuneracao_12": self.remuneracao(12),
                "adiantamento_13": self.gratificacao_natalina.get("valor_adiantamento")
                or 0,
                "mes_adiantamento_13": self.gratificacao_natalina.get(
                    "mes_adiantamento"
                ),
                "remuneracao_13": self.gratificacao_natalina.get("valor_final") or 0,
                "mes_13": self.gratificacao_natalina.get("mes_final"),
                "afastamento_1_motivo": (
                    self.afastamentos.get(1).get("motivo")
                    if self.afastamentos.get(1)
                    else 0
                ),
                "afastamento_1_inicio": (
                    self.afastamentos.get(1).get("inicio")
                    if self.afastamentos.get(1)
                    else "0000"
                ),
                "afastamento_1_fim": (
                    self.afastamentos.get(1).get("fim")
                    if self.afastamentos.get(1)
                    else "0000"
                ),
                "afastamento_2_motivo": (
                    self.afastamentos.get(2).get("motivo")
                    if self.afastamentos.get(2)
                    else 0
                ),
                "afastamento_2_inicio": (
                    self.afastamentos.get(2).get("inicio")
                    if self.afastamentos.get(2)
                    else "0000"
                ),
                "afastamento_2_fim": (
                    self.afastamentos.get(2).get("fim")
                    if self.afastamentos.get(2)
                    else "0000"
                ),
                "afastamento_3_motivo": (
                    self.afastamentos.get(3).get("motivo")
                    if self.afastamentos.get(3)
                    else 0
                ),
                "afastamento_3_inicio": (
                    self.afastamentos.get(3).get("inicio")
                    if self.afastamentos.get(3)
                    else "0000"
                ),
                "afastamento_3_fim": (
                    self.afastamentos.get(3).get("fim")
                    if self.afastamentos.get(3)
                    else "0000"
                ),
                "afastamento_quantidade_dias": self.afastamentos.get("total"),
                "ferias_indenizado": self.ferias_indenizada,
                "raca_cor": self.raca_cor,
                "indicador_deficiencia": 2,
                "tipo_deficiencia": 0,
                "sexo": self.sexo,
                "matricula": s.matricula,
                "categoria": self.categoria(),
            }
        )


class File(protofile.Protocol):
    @staticmethod
    def get_config(ano_base):
        try:
            from rh.gfp.rais.config.cfg import Config
        except:
            Config = {}
        finally:
            return Config

    def __init__(self, base_year, rectifier=False, task=None, log=None):
        """ """
        log.debug("INIT File RAIS %s.%s" % (self.__module__, self.__class__.__name__))
        # chama o super construtor.
        protofile.Protocol.__init__(self)

        # log.debug(config)

        # carrega configurações
        self.observer = task if task else None

        # log.debug('RETIFICADORA: %s' % rectifier)

        cfg = Configuration.get_or_create("gfp")
        uadm = UnidadeAdministrativa.objects.get(pk=cfg.get("orgao"))
        _ = clear_to_ascii

        # Informações do responsavel pela empresa
        self.regs.append(
            Registro(
                base_year,
                "reg-00",
                **{
                    "sequencial": 1,
                    "cnpj": uadm.pessoa_juridica.cnpj,
                    "resp_cpf": uadm.responsavel.cpf,
                    "resp_razao": _(uadm.responsavel.nome),
                    "resp_nome": _(uadm.responsavel.nome),
                    "resp_logradouro": _(uadm.address.latest("pk").logradouro),
                    "resp_numero": _(uadm.responsavel.address.latest("pk").numero),
                    # 'resp_complemento': (uadm.responsavel.address.latest('pk').complemento),
                    "resp_bairro": _(uadm.responsavel.address.latest("pk").bairro),
                    "resp_cep": uadm.responsavel.address.latest("pk").cep.replace(
                        "-", ""
                    ),
                    "resp_cod_municipio": uadm.responsavel.address.latest(
                        "pk"
                    ).municipio.ibge,
                    "resp_municipio": _(
                        uadm.responsavel.address.latest("pk").municipio.nome
                    ),
                    "resp_uf": uadm.responsavel.address.latest(
                        "pk"
                    ).municipio.estado.sigla,
                    "resp_email": uadm.responsavel.email_institucional,
                    "resp_crea": 0,
                    "resp_nascimento": uadm.responsavel.data_nascimento.strftime(
                        "%d%m%Y"
                    ),
                    "indicador_retificadora": 2 if rectifier is False else 1,
                    "data_retificadora": (
                        "" if rectifier is False else datetime.now().strftime("%d%m%Y")
                    ),
                    "data_geracao": datetime.now().strftime("%d%m%Y"),
                }
            )
        )

        # Informações da Empresa
        self.regs.append(
            Registro(
                base_year,
                "reg-01",
                **{
                    "sequencial": 2,
                    "cnpj": uadm.pessoa_juridica.cnpj,
                    "razao": _(uadm.pessoa_juridica.razao_social),
                    "logradouro": _(uadm.address.latest("pk").logradouro),
                    "numero": _(uadm.address.latest("pk").numero),
                    "bairro": _(uadm.address.latest("pk").bairro),
                    # 'complemento': (uadm.address.latest('pk').complemento),
                    "cep": uadm.address.latest("pk").cep.replace("-", ""),
                    "cod_municipio": uadm.address.latest("pk").municipio.ibge,
                    "municipio": _(uadm.address.latest("pk").municipio.nome),
                    "uf": uadm.address.latest("pk").municipio.estado.sigla,
                }
            )
        )

        # Informações dos Funcionários e Colaboradores
        count = 0
        query = (
            Servidor.objects.filter(
                entries__folha__periodo__ano=base_year,
                entries__folha__tipo_folha__principal=True,
            )
            .exclude(type_by_possession__in=["SAP", "MAP", "MAP2", "APO", "BFP"])
            .no_requested_without_onus()
            .order_by("pessoa_fisica__nome")
            .distinct()
        )

        # if getattr(settings, 'DEBUG', False) is True and MATRICULAS_DEBUG:
        #     query = query.filter(matricula__in=MATRICULAS_DEBUG)

        total = float(query.count() or 0)
        position = 0
        servidores = []
        if self.observer:
            self.observer["total"] = total
            self.observer["pctText"] = "Contabilizando servidores"
        for s in query:
            position += 1

            # self.observer and self.observer['pct'], float(position / total))
            if self.observer:
                self.observer["pct"] = position

            # log.debug('PRE PROCESSANDO: %s' % s)
            if (
                s in servidores
                or not s.get_posses_ativas(
                    date(base_year, 1, 1), date(base_year, 12, 31)
                ).exists()
            ):
                continue

            # log.debug('ADICIONANDO: %s' % s)
            servidores.append(s)

            count += 1

            try:
                self.regs.append(RegistroServidor(base_year, s, (count + 2)))
            except Exception as e:
                print(e)
                self.observer.message("Erro processando a linha do servidor %s" % s)
                log.exception(e)

        # Informações da Empresa
        self.regs.append(
            Registro(
                base_year,
                "reg-09",
                **{
                    "sequencial": (count + 3),
                    "cnpj": uadm.pessoa_juridica.cnpj,
                    "count_tipo_1": 1,
                    "count_tipo_2": count,
                }
            )
        )
