# -*- coding: utf-8 -*-

import os
import threading
import xml.etree.ElementTree as ET
from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings

from contrib.decorator import login_required
from contrib.helpers import clear_to_ascii
from contrib.middleware import set_current_user
from contrib.utils import get_json_engine, getLogger, make_zipfile
from engine.models import TaskSession
from ged.models import Arquivo as FileGED
from rh.gfp import models as gfp_models
from rh.gfp.reports import GFPReturnFile
from rh.models import (
    MovimentacaoDesligamento,
    MovimentacaoPosse,
    Servidor,
    UnidadeAdministrativa,
)
from standard.models import Configuration

json = get_json_engine()

log = getLogger(__name__)


class GFPReturnViabillize(GFPReturnFile):
    """docstring for GFPReturnViabillize"""

    _generated_filename = "viabillize_mpto.zip"

    def __init__(self, *args, **kargs):
        log.debug("INIT GFPReturnViabillize")
        super(GFPReturnViabillize, self).__init__(*args, **kargs)
        self.query_entries = self.payroll.lancamentos.filter(
            evento__carater__in=[6, 7],
            contracheque__folha__tipo_folha__margem__gt=0,
            contracheque__folha__status__in=[4, 3],
            contracheque__pensioner=None,
        ).order_by("contracheque__servidor", "contracheque__folha")

        self.query_events = gfp_models.Evento.objects.filter(
            consignment_manager=True,
            active=True,
        ).order_by("numero")

        self.cfg = Configuration.get_or_create("gfp")
        self.uadm = UnidadeAdministrativa.objects.get(pk=int(self.cfg.get("orgao")))
        self.responsavel_gfp = Servidor.objects.get(
            pk=int(self.cfg.get("responsavel_gfp"))
        )
        self.email_gfp = self.cfg.get("email_gfp", "")
        self.fone_gfp = self.cfg.get("telefone_responsavel_gfp", "")
        self.payroll_identify = clear_to_ascii(
            self.payroll.tipo_folha.abreviatura or self.payroll.tipo_folha.titulo
        )

        log.debug("VIABILLIZE for %s" % self.payroll)

    def get_generate_filename(self):
        return "viabillize_%s_%s_%02d%04d.zip".lower() % (
            settings.ORGAN_IDENTIFIER,
            self.payroll_identify,
            self.payroll.periodo.mes,
            self.payroll.periodo.ano,
        )

    def generate_viabillizexml_file(self):
        root = ET.Element("ArquivoViabillize")
        cnpj = (
            self.uadm.pessoa_juridica.cnpj
            if self.uadm and self.uadm.pessoa_juridica
            else "00000000000000"
        )
        period = self.payroll.periodo

        ET.SubElement(root, "Versao").text = "1.0"
        ET.SubElement(root, "Consignante").text = str(self.uadm)
        ET.SubElement(root, "Cnpj").text = "%s.%s.%s/%s-%s" % (
            cnpj[0:2],
            cnpj[2:5],
            cnpj[5:8],
            cnpj[8:12],
            cnpj[12:14],
        )
        ET.SubElement(root, "Folha_Descricao").text = (
            str(self.payroll) if hasattr(self, "payroll") else "NORMAL"
        )
        ET.SubElement(root, "Folha_Referencia").text = "%02d%04d" % (
            period.mes,
            period.ano,
        )
        el_reponsible = ET.SubElement(root, "Responsavel")
        ET.SubElement(el_reponsible, "Nome").text = str(
            self.responsavel_gfp.pessoa_fisica
        )
        # '(%s) %s-%s' % ('(%s) %s-%s' % (self.fone_gfp[0:2], self.fone_gfp[2:6], self.fone_gfp[6:10]))
        ET.SubElement(el_reponsible, "Fone").text = "(63) 3215-7560"
        ET.SubElement(el_reponsible, "Email").text = self.email_gfp

        el_integration = ET.SubElement(root, "IntegracaoFopag")
        ET.SubElement(el_integration, "Sistema").text = "Athenas"
        ET.SubElement(el_integration, "Desenvolvedor").text = (
            settings.VIABILLIZE_DEV_NAME
        )
        ET.SubElement(el_integration, "Fone").text = settings.VIABILLIZE_DEV_FONE
        ET.SubElement(el_integration, "Email").text = settings.VIABILLIZE_DEV_EMAIL
        ET.SubElement(el_integration, "ControleDeParcelas").text = "true"
        ET.SubElement(el_integration, "NomeArquivoInclusao").text = (
            "@MES@ANO_EnvioInclusoes_%s.txt" % self.payroll_identify
        )
        ET.SubElement(el_integration, "CabecarioArquivoInclusao").text = (
            "@ANO;@MES;%s;" % self.payroll_identify
        )
        ET.SubElement(el_integration, "RegistroInclusao").text = (
            "I;%s;@ANO;@MES;@MATRICULA;@NOME;@RUBRICA_CODIGO;@PRAZO;@VALOR_PARCELA_DECIMAL;@NUMERO_PARCELA;@ALIQUOTA;;@CODIGOADF;@HEMENSALIDADE"
            % self.payroll_identify
        )
        ET.SubElement(el_integration, "NomeArquivoLiquidacao").text = (
            "@MES@ANO_EnvioLiquidacoes_%s.txt" % self.payroll_identify
        )
        ET.SubElement(el_integration, "CabecarioArquivoLiquidacao").text = (
            "@ANO;@MES;%s;" % self.payroll_identify
        )
        ET.SubElement(el_integration, "RegistroLiquidacao").text = (
            "E;%s;@ANO;@MES;@MATRICULA;@NOME;@RUBRICA_CODIGO;@PRAZO;@VALOR_PARCELA_DECIMAL;@NUMERO_PARCELA;@ALIQUOTA;;@CODIGOADF;@HEMENSALIDADE"
            % self.payroll_identify
        )
        ET.SubElement(el_integration, "InfoPrazoMensalidade").text = "1"

        el_integrationweb = ET.SubElement(root, "IntegracaoWeb")
        ET.SubElement(el_integrationweb, "DominioPortal").text = (
            settings.VIABILLIZE_DOMAIN_PORTAL
        )
        ET.SubElement(el_integrationweb, "ChaveHash").text = (
            settings.VIABILLIZE_SECRET_KEY
        )

        el_margins = ET.SubElement(root, "TiposDeMargens")

        cut_date = date(period.ano, period.mes, 1) + relativedelta(months=1, days=-1)

        first_margin_of_type = False

        q_margins = gfp_models.MarginConsignable.objects.filter(
            type_of_payroll=self.payroll.tipo_folha
        ).exclude(start_validity__gt=cut_date)

        # margins_ids = [m.pk for m in q_margins]

        type_ofs = []

        for mc in q_margins:
            mc_el = ET.SubElement(el_margins, "TipoMargem")
            ET.SubElement(mc_el, "Codigo").text = "%s" % mc.pk
            ET.SubElement(mc_el, "Descricao").text = str(mc.title)
            ET.SubElement(mc_el, "PrazoMaximo").text = "%s" % mc.maximum_installment
            ET.SubElement(mc_el, "CetMaximo").text = "%s" % mc.maximum_cet
            ET.SubElement(mc_el, "ServicoUnico").text = "false"
            events_mc_el = ET.SubElement(mc_el, "Rubricas")
            consigned_ids = [e.pk for e in mc.consigneds.all()]

            if mc.type_of_payroll.pk not in type_ofs:
                q_entries = self.query_events.all()
                type_ofs.append(mc.type_of_payroll.pk)
                first_margin_of_type = True
            else:
                q_entries = mc.consigneds.all()

            log.debug(
                "%s (%d): (%s) %s"
                % (mc, q_entries.count(), first_margin_of_type, consigned_ids)
            )

            for ev in q_entries:
                ev_consigned_other_margin = (
                    True
                    if ev.margins_consigneds.exclude(pk=mc.pk)
                    .filter(type_of_payroll=mc.type_of_payroll)
                    .exists()
                    else False
                )
                _id = (
                    ("%s%s" % (ev.numero, mc.type_of_payroll.abreviatura))
                    if not mc.type_of_payroll.principal
                    else ev.numero
                )
                if not ev_consigned_other_margin:
                    # useds_ids.append(_id)
                    log.debug("MC: %s EV: %s" % (mc, _id))
                    type_term = "INDETERMINADO"
                    if ev.carater == 7:
                        type_term = "FIXO"
                    elif ev.carater == 6:
                        type_term = "MENSALIDADE"
                    ev_el = ET.SubElement(events_mc_el, "Rubrica")
                    ET.SubElement(ev_el, "Codigo").text = _id
                    ET.SubElement(ev_el, "Descricao").text = str(ev.titulo)
                    ET.SubElement(ev_el, "TipoDePrazo").text = type_term
                    ET.SubElement(ev_el, "Aliquota").text = (
                        ("%s" % (ev.porcentagem or 0))
                        if ev.carater == 6 and ev.tipo_calculo in [1, 5]
                        else "0"
                    )
                    ET.SubElement(ev_el, "BaseAliquota").text = (
                        "%s" % ev.get_base_de_calculo_display()
                        if ev.base_de_calculo != 0
                        else ""
                    )
                    ET.SubElement(ev_el, "IncideNaMargem").text = (
                        "true" if ev.pk in consigned_ids else "false"
                    )

            first_margin_of_type = False

        el_consigneds = ET.SubElement(root, "LoteDeConsignados")

        consigned_files = self.generate_consigneds_files()
        for x in consigned_files:
            el_batch = ET.SubElement(el_consigneds, "LoteConsignados")
            ET.SubElement(el_batch, "NumeroLote").text = "%s" % x
            ET.SubElement(el_batch, "NomeArquivo").text = consigned_files[x]

        viabillize_file = ET.ElementTree(root)

        file_path = os.path.join(self.tmp_dir, "viabillize.xml")

        return self.create_file(file_path, viabillize_file, xml=True)

    def margins_to_elements(self):
        pass

    def generate_consigneds_files(self):
        count = file_id = 0

        file_name = "consignados_1.xml"

        root = el_consigneds = None

        files_createds = {}

        resgistrations = []

        # path = settings.BASE_DIR

        for cc in gfp_models.ContraCheque.objects.filter(
            folha=self.payroll, pensioner=None
        ).order_by("servidor"):
            # log.debug('C1: %d C2: %s' % (c2, count))
            # c2 += 1
            log.debug("VIABILLIZE: %s" % cc)
            payroll = cc.folha
            _id = "%s%s" % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura)
            if _id not in resgistrations:
                resgistrations.append(_id)

                if count % 500 == 0:
                    if file_id != 0:
                        file_name = "consignados_%d.xml" % file_id
                        file_path = os.path.join(self.tmp_dir, file_name)
                        consigneds_file = ET.ElementTree(root)
                        self.create_file(file_path, consigneds_file, xml=True)
                        files_createds[file_id] = file_name

                    # model_file = ET.parse('%s/rh/gfp/generators/viabillize/consignados.xml' % path)
                    file_id = (count // 500) + 1

                    root = ET.Element("LoteConsignados")

                    ET.SubElement(root, "NumeroLote").text = "%d" % file_id
                    ET.SubElement(root, "NomeArquivo").text = file_name

                    el_consigneds = ET.SubElement(root, "Consignados")

                el_employee = ET.SubElement(el_consigneds, "Consignado")
                el_attrs = ET.SubElement(el_employee, "Atributos")
                el_margins = ET.SubElement(el_employee, "Margens")
                el_payrolls = ET.SubElement(el_employee, "Folha")

                try:
                    endereco = cc.servidor.pessoa_fisica.address.first()
                    fone = cc.servidor.pessoa_fisica.phone.first()
                    desligamento = {"data": "", "motivo": ""}
                    if payroll.tipo_folha.margem < 100:
                        # Folhas que podem ser totalmente consignadas, normalmente
                        if not cc.servidor.get_posses_ativas(cc.folha.date_range.last):
                            mov_desligamento = cc.servidor.posses.latest(
                                "data_desligamento"
                            ).desligamento
                            desligamento["data"] = mov_desligamento.data_desligamento
                            desligamento["motivo"] = (
                                mov_desligamento.get_opcao_display()
                            )
                    elif payroll.tipo_folha.margem == 100:
                        data_limite = date.today()
                        for fe1 in cc.lancamentos.filter(evento__tipo="P", prazo__gt=0):
                            dt = date(
                                fe1.contracheque.folha.periodo.ano,
                                fe1.contracheque.folha.periodo.mes,
                                5,
                            ) + relativedelta(months=int(fe1.prazo - fe1.qnt))
                            if dt > data_limite:
                                data_limite = dt
                        desligamento["data"] = data_limite
                        desligamento["motivo"] = "FIM DO BENEFÍCIO"

                    if cc.servidor.is_acordo_cooperacao:
                        type_employee = "EFETIVO/REQUISITADO"
                    elif cc.servidor.is_efetivo:
                        type_employee = "EFETIVO"
                    else:
                        type_employee = "COMISSIONADO"

                    ET.SubElement(el_employee, "RN").text = "%s" % (count + 1)
                    ET.SubElement(el_employee, "ChaveMensal").text = _id
                    ET.SubElement(el_employee, "Cpf").text = (
                        cc.servidor.pessoa_fisica.cpf
                    )
                    ET.SubElement(el_employee, "Matricula").text = "%s" % _id
                    ET.SubElement(el_employee, "Nome").text = str(
                        cc.servidor.pessoa_fisica
                    )
                    ET.SubElement(el_employee, "Localizacao").text = str(
                        cc.lotacao or ""
                    )
                    ET.SubElement(el_employee, "TerminoVinculo").text = (
                        desligamento["data"].strftime("%d/%m/%Y")
                        if desligamento["data"]
                        else ""
                    )
                    ET.SubElement(el_employee, "MotivoTerminoVinculo").text = (
                        desligamento["motivo"]
                    )

                    ca1 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca1, "Atributo").text = "Admissao"
                    ET.SubElement(ca1, "Valor").text = (
                        cc.servidor.data_exercicio.strftime("%d/%m/%Y")
                    )
                    ca2 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca2, "Atributo").text = "Rg"
                    ET.SubElement(ca2, "Valor").text = cc.servidor.pessoa_fisica.rg
                    ca3 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca3, "Atributo").text = "Rg - Orgao"
                    ET.SubElement(ca3, "Valor").text = (
                        cc.servidor.pessoa_fisica.rg_orgao
                    )
                    ca4 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca4, "Atributo").text = "Rg - Uf"
                    ET.SubElement(ca4, "Valor").text = str(
                        cc.servidor.pessoa_fisica.rg_uf
                    )
                    ca5 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca5, "Atributo").text = "Rg - Expedicao"
                    ET.SubElement(ca5, "Valor").text = (
                        cc.servidor.pessoa_fisica.rg_data_expedicao.strftime("%d/%m/%Y")
                    )
                    ca6 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca6, "Atributo").text = "Telefone"
                    ET.SubElement(ca6, "Valor").text = str(fone or "(63) 3216-7600")
                    ca7 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca7, "Atributo").text = "Endereco"
                    ET.SubElement(ca7, "Valor").text = str(
                        endereco.logradouro if endereco else ""
                    )
                    ca8 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca8, "Atributo").text = "Numero"
                    ET.SubElement(ca8, "Valor").text = str(
                        endereco.numero if endereco else ""
                    )
                    ca9 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca9, "Atributo").text = "Bairro"
                    ET.SubElement(ca9, "Valor").text = str(
                        endereco.bairro if endereco else ""
                    )
                    ca10 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca10, "Atributo").text = "Cep"
                    ET.SubElement(ca10, "Valor").text = str(
                        endereco.cep if endereco else ""
                    )
                    ca11 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca11, "Atributo").text = "Cidade"
                    ET.SubElement(ca11, "Valor").text = str(
                        endereco.municipio.nome
                        if endereco and endereco.municipio
                        else ""
                    )
                    ca11 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca11, "Atributo").text = "Estado"
                    ET.SubElement(ca11, "Valor").text = str(
                        endereco.municipio.estado.sigla
                        if endereco and endereco.municipio and endereco.municipio.estado
                        else ""
                    )
                    ca12 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca12, "Atributo").text = "Vinculo"
                    ET.SubElement(ca12, "Valor").text = type_employee
                    ca13 = ET.SubElement(el_attrs, "ConsignadoAtributo")
                    ET.SubElement(ca13, "Atributo").text = "Cargo"
                    ET.SubElement(ca13, "Valor").text = str(
                        cc.cargo_eletivo or cc.cargo_comissao or cc.cargo_efetivo or ""
                    )

                    for mc in cc.margin_paychecks.all():
                        el_margin = ET.SubElement(el_margins, "ConsignadoMargem")
                        ET.SubElement(el_margin, "TipoMargemCodigo").text = (
                            "%s" % mc.margin.pk
                        )
                        ET.SubElement(el_margin, "MargemBruta").text = (
                            "%0.2f" % mc.total_value
                        )

                    for fe in cc.lancamentos.filter(
                        evento__carater__in=[6, 7],
                        status="CT",
                        evento__consignment_manager=True,
                        evento__active=True,
                    ).order_by("evento__numero"):
                        el_entry = ET.SubElement(el_payrolls, "ConsignadoFolha")
                        ET.SubElement(el_entry, "RubricaCodigo").text = (
                            (
                                "%s%s"
                                % (fe.evento.numero, cc.folha.tipo_folha.abreviatura)
                            )
                            if not cc.folha.tipo_folha.principal
                            else fe.evento.numero
                        )
                        ET.SubElement(el_entry, "NumeroParcelaAtual").text = (
                            "%s" % fe.parcela
                        )
                        ET.SubElement(el_entry, "NumeroParcelasTotais").text = (
                            "%s" % fe.prazo
                        )
                        ET.SubElement(el_entry, "Valor").text = "%0.2f" % fe.valor

                except (
                    MovimentacaoPosse.DoesNotExist,
                    MovimentacaoDesligamento.DoesNotExist,
                ) as e:
                    # print 'ERRO: %s' % cc
                    log.exception(e)
                except Exception as e:
                    log.exception(e)
                    raise e

                count += 1

        # file_id = (count % 500) + 1
        # file_id += 1
        if count % 500 != 0 and file_id != 0:
            file_name = "consignados_%d.xml" % file_id
            file_path = os.path.join(self.tmp_dir, file_name)
            consigneds_file = ET.ElementTree(root)
            self.create_file(file_path, consigneds_file, xml=True)
            files_createds[file_id] = file_name

        return files_createds

    def returned_events(self, query_entries=[]):
        # ANEXO III - ARQUIVO RETORNO
        lines = []
        # print 'COLETANDO INFORMAÇÔES...',
        # for cc in payroll.paychecks.all().order_by('servidor'):
        for fe in self.query_entries:
            try:
                lines.append(
                    "%s|%s|%s|%s|%s|%s\r\n"
                    % (
                        "%02d%04d"
                        % (
                            fe.contracheque.folha.periodo.mes,
                            fe.contracheque.folha.periodo.ano,
                        ),
                        fe.evento.numero,
                        "%s%s"
                        % (
                            fe.servidor.matricula,
                            fe.contracheque.folha.tipo_folha.abreviatura,
                        ),
                        int(fe.parcela) if fe.evento.carater == 7 else 1,
                        int(fe.prazo),
                        fe.valor,
                    )
                )
            except Exception as e:
                raise e

        # dir_path = '%s%02d%04d' % (payroll.tipo_folha, self.payroll.periodo.mes, self.payroll.periodo.ano)
        # file_path = os.path.join(self.tmp_dir, dir_path, 'arquivo_retorno_%s.txt' % payroll.tipo_folha)
        file_path = os.path.join(self.tmp_dir, "arquivo_retorno.txt")

        return self.create_file(file_path, lines)

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s" % (user, self.payroll, self.tmp_dir)
            )
            log.debug("PERIOD: %s" % self.payroll.periodo)
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivos Viabillize - %02d/%04d"
                % (self.payroll.periodo.mes, self.payroll.periodo.ano)
            )
            # for payroll in gfp_models.Folha.objects.filter(periodo=self.payroll.periodo,
            #                                                tipo_folha__margem__gt=0, status__in=[4, 3]):
            #     log.debug('>>>>>>>>>>>> %s ' % payroll)
            #     if not os.path.exists(self.tmp_dir):
            #         os.makedirs(self.tmp_dir)
            # self.registration_events()
            # self.functional_register()
            # self.bases_events()
            # self.returned_events()
            self.generate_viabillizexml_file()
            # else:
            #     log.debug('<<<<<<<<< NENHUMA FOLHA PROCESSADA PARA ENVIAR...')

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)

            zipfile = make_zipfile(
                os.path.join(self.tmp_dir, "..", self.get_generate_filename()),
                self.tmp_dir,
                False,
            )
            log.debug(">>>>>>>>>>>> ZIP GERADO: %s" % zipfile)
            gedfile = FileGED.from_filepath(zipfile, user, "application/zip", 1)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
