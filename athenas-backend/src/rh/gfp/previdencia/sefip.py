# -*- coding: utf-8 -*-

import datetime
import re
import functools

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Sum


from contrib import protofile
from contrib.helpers import clear_to_ascii
from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.gfp.models import FatorRat, FolhaEvento, ContraCheque
from rh.gfp.previdencia.layouts_sefip import RegistroSefip
from rh.models import PIS_PASEP, Servidor, UnidadeAdministrativa
from standard.models import Configuration

log = getLogger(__name__)


# __name__ = u"SEFIP"
# __hid__ = ""

EVENTOS_INSS = getattr(settings, "EVENTOS_INSS", ["91000"])
EVENTOS_INSS_13 = getattr(settings, "EVENTOS_INSS_13", ["91000"])
EVENTOS_MATERNIDADE = getattr(settings, "EVENTOS_MATERNIDADE", ["91000"])


def cmp_pis(a, b):
    if a.info[6] < b.info[6]:
        return -1
    elif a.info[6] > b.info[6]:
        return 1
    else:
        return 0


class File(protofile.Protocol):

    def __str__(self):
        return "{0}".format(self.__extract_regs__())

    def __init__(self, payroll, task=None, log=None, code=115):
        self.code = code  # Informando se o arquivo a ser gerado é para
        super(File, self).__init__()

        log.info(
            "__INIT__ SEFIP EVENTOS %s %s %s" % (code, EVENTOS_INSS, EVENTOS_INSS_13)
        )

        cfg = Configuration.objects.get(application="gfp")

        self.nl = "\r\n"  # Adicionado para dar suporte ao programa do CEF de envio de arquivos de
        self.uadm = UnidadeAdministrativa.objects.get(pk=cfg.get("orgao"))
        self.uadm_address = self.uadm.address.first()

        self.observer = task
        # self.observer = conf.get('observer') if 'observer' in conf else None
        self.folha = payroll

        self.observer.set("pct", 0.0)
        # -----------somatorio salário maternidade --------------------
        q_entries_maternity = FolhaEvento.objects.filter(
            evento__genre_event__genre_number__in=[
                nev[0:3] for nev in EVENTOS_MATERNIDADE
            ]
        )
        if self.code == 115:
            q_entries_maternity = q_entries_maternity.filter(folha=self.folha).filter(
                evento__specie_event__specie_number="00"
            )
        elif self.code == 650:
            q_entries_maternity = (
                q_entries_maternity.exclude(folha=self.folha)
                .filter(
                    reference_year=self.folha.periodo.ano,
                    reference_month=self.folha.periodo.mes,
                )
                .exclude(evento__specie_event__specie_number="00")
            )
        tt = q_entries_maternity.aggregate(Sum("correct_valor"))
        total_salary_maternity = tt["correct_valor__sum"]

        # ---------------------------------------------------------------

        # Adicionando Header de Arquivo REG 00------------------------------------------
        config_header_arquivo = {
            "tipo_inscricao_responsavel": 1,  # CNPJ
            "inscricao_responsavel": self.uadm.pessoa_juridica.cnpj,  # CPF
            "nome_responsavel": clear_to_ascii(self.uadm.nome).replace("-", " "),
            "nome_contato": Servidor.objects.get(
                pk=cfg.get("responsavel_gfp", "")
            ).pessoa_fisica.nome,
            "logradouro": cfg.get("endereco_orgao", ""),
            "bairro": cfg.get("bairro_orgao", ""),
            "indicador_recolhimento_fgts": 1 if self.folha.periodo.mes != 13 else "",
            "cep": re.sub(r"(\.|-)", "", cfg.get("cep_orgao", "")),
            "cidade": self.uadm_address.municipio.nome,
            "uf": self.uadm_address.municipio.estado.sigla,
            "fone_contato": cfg.get("telefone_responsavel_orgao", ""),
            "competencia": "%04d%02d"
            % (self.folha.periodo.ano, self.folha.periodo.mes),
            "tipo_inscricao_fornecedor": 1,
            "inscricao_fornecedor": self.uadm.pessoa_juridica.cnpj,
            "site": cfg.get("email_gfp", ""),
            "cod_recolhimento": self.code,
        }

        self.observer.set("pctText", "Inserindo header de arquivo.")
        # Adicionando Registro de HEADER DE ARQUIVO Reg: 00
        self.regs.append(RegistroSefip("header-file-reg-00", **config_header_arquivo))

        # Adicionando Header de Arquivo REG 10------------------------------------------
        config_header_empresa = {
            "tipo_inscricao_empresa": 1,
            "inscricao_empresa": self.uadm.pessoa_juridica.cnpj,
            "nome_empresa": clear_to_ascii(self.uadm.nome),
            "logradouro": cfg.get("endereco_orgao", ""),
            "bairro": cfg.get("bairro_orgao", ""),
            "cep": re.sub(r"(\.|-)", "", cfg.get("cep_orgao", "")),
            "cidade": self.uadm_address.municipio.nome,
            "uf": self.uadm_address.municipio.estado.sigla,
            "fone_contato": cfg.get("telefone_responsavel_orgao", ""),
            # TODO Trazer o Fator RAT vigente
            "rat": FatorRat.vigente_em(
                datetime.date(
                    self.folha.periodo.ano, min(self.folha.periodo.mes, 12), 1
                )
            ),
            "salario_maternidade": float(total_salary_maternity or 0),
        }

        self.observer.set("pctText", "Inserindo header de arquivo.")
        # Adicionando Registro de HEADER DA EMPRESA Reg: 10
        self.regs.append(
            RegistroSefip("header-empresa-reg-10", **config_header_empresa)
        )
        # Adicionando Registros REG 30 ------------------------------------------
        """
        FIXME: Em momento de acerto esta consulta irá duplicar os registros do servidor, com diferenças no campo
        remuneracao_sem_13 e ainda a remuneracao_13 sempre ficara zerada em momento de acerto. Acredito que o mais
        correto seria o Query ter a lista de servidores e dentro do for ter outro for passado pelos eventos citados
        e ai sim dar a importancia de cada um.
        Outro problema foi a CBO deve haver uma forma de ver o cargo que o servidor estava no inicio do mes.
        """
        _eventos = EVENTOS_INSS + EVENTOS_INSS_13

        q_entries = FolhaEvento.objects.filter(
            evento__genre_event__genre_number__in=[nev[0:3] for nev in _eventos]
        )
        if self.code == 115:
            q_entries = q_entries.filter(folha=self.folha).filter(
                evento__specie_event__specie_number="00"
            )
        elif self.code == 650:
            q_entries = (
                q_entries.exclude(folha=self.folha)
                .filter(
                    reference_year=self.folha.periodo.ano,
                    reference_month=self.folha.periodo.mes,
                )
                .exclude(evento__specie_event__specie_number="00")
            )

        query = (
            ContraCheque.objects.filter(lancamentos__in=q_entries)
            .order_by("servidor")
            .distinct()
        )

        base_pct = query.count()
        passo_pct = 0
        regs = []
        contracheques = []

        if self.observer:
            self.observer["total"] = base_pct
            self.observer["pctText"] = "Contabilizando servidores"

        dr = NewDateRange.from_month(
            self.folha.periodo.ano, min(self.folha.periodo.mes, 12)
        )

        for cc in query:
            log.info(cc)
            q_depertures = cc.servidor.departures(dr.first, dr.last)

            passo_pct += 1

            if cc.servidor in contracheques:
                continue

            contracheques.append(cc.servidor)

            q_entries_cc = q_entries.filter(contracheque__servidor=cc.servidor)

            remuneracao_sem_13 = q_entries_cc.filter(
                evento__genre_event__genre_number__in=[nev[0:3] for nev in EVENTOS_INSS]
            )
            remuneracao_sem_13 = (
                remuneracao_sem_13.aggregate(valor_base=Sum("valor_base")).get(
                    "valor_base"
                )
                or 0.00
            )

            base_calculo_13 = q_entries_cc.filter(
                evento__genre_event__genre_number__in=[
                    nev[0:3] for nev in EVENTOS_INSS_13
                ]
            )
            base_calculo_13 = (
                base_calculo_13.aggregate(valor_base=Sum("valor_base")).get(
                    "valor_base"
                )
                or 0.00
            )

            last_cm = (
                cc.servidor.posses.filter(quadro__cargo__tipo_lei_cargo="CM")
                .order_by("data_exercicio")
                .last()
            )
            last_ef = (
                cc.servidor.posses.filter(
                    quadro__cargo__tipo_lei_cargo__in=["EF", "AC"]
                )
                .order_by("data_exercicio")
                .last()
            )
            comission = cc.cargo_comissao or (last_cm and last_cm.quadro.cargo)
            comission_config = comission.current_config if comission else None

            efective = cc.cargo_efetivo or (last_ef and last_ef.quadro.cargo)
            efective_config = efective.current_config if efective else None

            config_trabalhador = {
                "tipo_inscricao_empresa": 1,
                "inscricao_empresa": self.uadm.pessoa_juridica.cnpj,
                "pis_pasep_ci": (
                    cc.servidor.pessoa_fisica.documento.filter(
                        tipo_documento=PIS_PASEP
                    )[0].numero
                    if cc.servidor.pessoa_fisica.documento.filter(
                        tipo_documento=PIS_PASEP
                    ).count()
                    else None
                ),
                "data_admissao": cc.servidor.data_exercicio.strftime("%d%m%Y"),
                "data_nascimento": cc.servidor.pessoa_fisica.data_nascimento.strftime(
                    "%d%m%Y"
                ),
                "nome_trabalhador": clear_to_ascii(cc.servidor.pessoa_fisica.nome),
                "matricula_trabalhador": cc.servidor.matricula,
                "remuneracao_sem_13": float(
                    remuneracao_sem_13
                ),  # valor_base if cc.folha.periodo.mes != 13 else 0,
                "base_calculo_13": float(
                    base_calculo_13
                ),  # cc.valor_base if cc.folha.periodo.mes == 13 else 0,
                "cbo": "0%s"
                % (
                    comission_config.cbo.codigo[0:4]
                    if comission_config
                    else efective_config.cbo.codigo[0:4]
                ),
            }
            regs.append(  # Adicionando Registro de HEADER DA EMPRESA Reg: 10
                RegistroSefip("trabalhador-reg-30", **config_trabalhador)
            )
            # ----------------- MOVIMENTACOES ----------------------------
            # licenca_maternidade
            q_maternity = q_depertures.filter(tipo=12)
            lm = q_maternity.first()
            qevents_maternity = cc.lancamentos.filter(
                evento__numero__in=EVENTOS_MATERNIDADE
            )

            if qevents_maternity and lm:
                end_date = lm.data_inicio + relativedelta(days=119)
                if dr.first <= end_date:
                    # for fe in qevents_maternity:
                    #     total_salary_maternity += fe.
                    config_reg_32 = config_trabalhador
                    config_reg_32.update(
                        {
                            "cod_movimentacao": "Q1",
                            "data_movimentacao": lm.data_inicio.strftime("%d%m%Y"),
                        }
                    )
                    regs.append(  # Adicionando Registro 32
                        RegistroSefip("trabalhador-reg-32", **config_reg_32)
                    )
                    if end_date <= dr.last:
                        config_reg_32 = config_trabalhador
                        config_reg_32.update(
                            {
                                "cod_movimentacao": "Z1",
                                "data_movimentacao": end_date.strftime("%d%m%Y"),
                            }
                        )
                        regs.append(  # Adicionando Registro 32
                            RegistroSefip("trabalhador-reg-32", **config_reg_32)
                        )

            # -------------------------fim da licenca maternidade------------------------------------

            # Servidor desligado
            if cc.servidor.data_desligamento and cc.servidor.data_desligamento in [
                dr.first,
                dr.last,
            ]:
                config_reg_32 = config_trabalhador
                config_reg_32.update(
                    {
                        "cod_movimentacao": "J",
                        "data_movimentacao": cc.servidor.data_desligamento.strftime(
                            "%d%m%Y"
                        ),
                    }
                )
                regs.append(  # Adicionando Registro 32
                    RegistroSefip("trabalhador-reg-32", **config_reg_32)
                )

            self.observer["pct"] = passo_pct
            self.observer.set("pctText", "Registro %d de %d." % (passo_pct, base_pct))

        self.regs += sorted(regs, key=functools.cmp_to_key(cmp_pis))
        # Adicionando Trailer de Arquivo REG 90 ----------------------------
        config_trailler_arquivo = {}
        self.observer.set("pctText", "Inserindo trailer de arquivo.")
        self.regs.append(  # Adicionando Registro de TRAILER DE ARQUIVO Reg: 9
            RegistroSefip("triller-arquivo-reg-90", **config_trailler_arquivo)
        )
        self.observer.set("pctText", "Gerando arquivo SEFIP.")
        # ----------------------------------------------------------------------
