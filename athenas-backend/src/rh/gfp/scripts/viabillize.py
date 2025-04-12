# -*- coding: utf-8 -*-

import codecs
import os

from datetime import date
from dateutil.relativedelta import relativedelta

from contrib.utils import getLogger
from django.db.models import Q
from rh.models import MovimentacaoDesligamento, MovimentacaoPosse
from rh.gfp.models import Evento, Folha

log = getLogger("VIABILLIZE")

"""
1. RODAR MIGRATE GFP
2. ATUALIZAR CARATER DE EVENTOS:
   2.1 OS QUE SAO MENSALIDADES(que não possui fim previsto) PARA "MENSALIDADE"
   2.2 OS QUE SAO CONSIGNAÇÕES PARA "CONSIGNAÇÃO"
3. ATUALIZAR O CAMPO "MARGEM" DE TIPO_FOLHA PARA O PERCENTUAL DA MERGEM CONSIGNADA. EX.: NORMAL= 30%
"""

DIR = os.environ.get("HOME")


# def verificar_consignatarios():
#     # Verificar eventos e consignatarios
#     from rh.gfp.models import Evento
#     from django.db.models import Q

#     Evento.objects.filter(Q(titulo__icontains='MENSAL', carater=0)).update(carater=6)
#     Evento.objects.filter(Q(aplica_consignado=True, carater=0)).update(carater=7)
#     Evento.objects.filter(Q(titulo__icontains='ASAMP', carater=0)).update(carater=7)
#     Evento.objects.filter(Q(titulo__icontains='ATMP', carater=0)).update(carater=7)

#     for e in Evento.objects.filter(Q(carater__in=[6, 7]) | Q(aplica_consignado=True)):
#         print '\n%-50s' % e,
#         consigs = e.em_plano.filter(tipo=1, folha_tipo=101, ano_calendario=2013)
#         if consigs.count() == 1:
#             e.consignatario = consigs.get().pessoa_juridica
#             e.save()
#             print e.consignatario.cnpj, ':', 'OK',
#         elif consigs.count() > 0:
#             for pc in consigs:
#                 print pc.pessoa_juridica.cnpj,


def cadastro_eventos(dir_="/home/raysonsilva/"):
    # ANEXO I - CADASTRO DE EVENTOS
    print("COLETANDO INFORMAÇÔES...")
    lines = []
    for e in Evento.objects.filter(Q(carater__in=[6, 7])):
        lines.append(
            "%s|%s|%s|%s|%s|%s|%s\r\n"
            % (
                e.numero,
                "",
                e.titulo,
                ("True" if e.porcentagem else "False"),
                (e.get_base_de_calculo_display() if e.porcentagem else ""),
                (("%s%%" % e.porcentagem) if e.porcentagem else ""),
                ("True" if e.carater == 6 else "False"),
            )
        )
    print("OK")
    print("CRIANDO ARQUIVO [CADASTRO DE EVENTOS]... ")
    with codecs.open(os.path.join(dir_, "cadastro_eventos.txt"), "w", "utf-8") as fd:
        fd.writelines(lines)
    print("OK")


# ----------------------------------------------------------------------------


def cadastro_funcional(folha, dir_="/home/raysonsilva/"):
    # ANEXO II - CADASTRO FUNCIONAL
    lines = []
    print("COLETANDO INFORMAÇÔES...")
    if 0 < folha.tipo_folha.margem <= 100:
        for cc in folha.paychecks.all().order_by("servidor"):
            try:
                endereco = (
                    cc.servidor.pessoa_fisica.address.all()[0]
                    if cc.servidor.pessoa_fisica.address.all()
                    else None
                )
                desligamento = {"data": "", "motivo": ""}
                if folha.tipo_folha.margem < 100:
                    # Folhas que podem ser totalmente consignadas, normalmente
                    if not cc.servidor.get_posses_ativas(cc.folha.date_range.last):
                        mov_desligamento = cc.servidor.posses.latest(
                            "data_desligamento"
                        ).desligamento
                        desligamento["data"] = mov_desligamento.data_desligamento
                        desligamento["motivo"] = mov_desligamento.get_opcao_display()
                elif folha.tipo_folha.margem == 100:
                    data_limite = date.today()
                    for fe in cc.lancamentos.filter(evento__tipo="P", prazo__gt=0):
                        dt = date(
                            fe.contracheque.folha.periodo.ano,
                            fe.contracheque.folha.periodo.mes,
                            5,
                        ) + relativedelta(months=int(fe.prazo - fe.qnt))
                        if dt > data_limite:
                            data_limite = dt
                    desligamento["data"] = data_limite
                    desligamento["motivo"] = "FIM DO BENEFÍCIO"

                lines.append(
                    "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\r\n"
                    % (
                        cc.servidor.pessoa_fisica,
                        "%s%s"
                        % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura),
                        cc.servidor.data_exercicio,
                        cc.servidor.pessoa_fisica.cpf,
                        cc.servidor.pessoa_fisica.rg,
                        cc.servidor.pessoa_fisica.rg_orgao,
                        cc.servidor.pessoa_fisica.rg_uf,
                        cc.servidor.pessoa_fisica.rg_data_expedicao,
                        (
                            cc.servidor.pessoa_fisica.phone.all()[0]
                            if cc.servidor.pessoa_fisica.phone.all()
                            else "(63) 3216-7600"
                        ),
                        endereco.logradouro if endereco else "",
                        endereco.numero if endereco else "",
                        endereco.bairro if endereco else "",
                        (
                            endereco.municipio.nome
                            if endereco and endereco.municipio
                            else ""
                        ),
                        endereco.cep if endereco else "",
                        (
                            endereco.municipio.estado.sigla
                            if endereco
                            and endereco.municipio
                            and endereco.municipio.estado
                            else ""
                        ),
                        cc.folha.tipo_folha,
                        "EFETIVO" if cc.servidor.is_efetivo else "COMISSIONADO",
                        cc.cargo_eletivo or cc.cargo_comissao or cc.cargo_efetivo or "",
                        cc.lotacao or "",
                        cc.situacao_previdenciaria or "",
                        desligamento["data"],
                        desligamento["motivo"],
                        cc.margem_consignada_total,
                        "%02d%04d" % (cc.folha.periodo.mes, cc.folha.periodo.ano),
                    )
                )
            except (
                MovimentacaoPosse.DoesNotExist,
                MovimentacaoDesligamento.DoesNotExist,
            ):
                print("ERRO: %s" % cc)
            except Exception as e:
                log.exception(e)
                raise e
    print("OK")
    print(
        "CRIANDO ARQUIVO [CADASTRO FUNCIONAL - %s]... " % folha.tipo_folha.abreviatura
    )
    with codecs.open(
        os.path.join(dir_, "cadastro_funcional_%s.txt" % folha.tipo_folha.abreviatura),
        "w",
        "utf-8",
    ) as fd:
        fd.writelines(lines)
    print("OK")


# ----------------------------------------------------------------------------


def arquivo_retorno(folha, dir_="/home/raysonsilva/"):
    # ANEXO III - ARQUIVO RETORNO
    lines = []
    print("COLETANDO INFORMAÇÔES...")
    for cc in folha.paychecks.all().order_by("servidor"):
        for fe in cc.lancamentos.filter(Q(evento__carater__in=[6, 7])):
            try:
                lines.append(
                    "%s|%s|%s|%s|%s|%s\r\n"
                    % (
                        "%02d%04d" % (cc.folha.periodo.mes, cc.folha.periodo.ano),
                        fe.evento.numero,
                        "%s%s"
                        % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura),
                        int(fe.qnt) if fe.evento.carater == 7 else 1,
                        int(fe.prazo),
                        fe.valor,
                    )
                    # unicode(fe.evento)
                )
            except Exception as e:
                raise e
    print("OK")
    print("CRIANDO ARQUIVO [RETORNO - %s]... " % folha.tipo_folha.abreviatura)
    with codecs.open(
        os.path.join(dir_, "arquivo_retorno_%s.txt" % folha.tipo_folha.abreviatura),
        "w",
        "utf-8",
    ) as fd:
        fd.writelines(lines)
    print("OK")


def cadastro_bases(folha, dir_="/home/raysonsilva/"):
    # ANEXO IV - CADASTRO DE BASES
    lines = []
    matriculas = {}
    print("COLETANDO INFORMAÇÔES...")
    for cc in folha.paychecks.all().order_by("servidor"):
        for fe in cc.lancamentos.filter(
            Q(evento__carater__in=[6]) & Q(evento__porcentagem__gt=0)
        ):
            if cc.servidor.matricula not in matriculas:
                matriculas[cc.servidor.matricula] = []
            if fe.evento.base_de_calculo not in matriculas[cc.servidor.matricula]:
                matriculas[cc.servidor.matricula].append(fe.evento.base_de_calculo)
                try:
                    lines.append(
                        "%s|%s|%s|%s\r\n"
                        % (
                            "%02d%04d" % (cc.folha.periodo.mes, cc.folha.periodo.ano),
                            "%s%s"
                            % (cc.servidor.matricula, cc.folha.tipo_folha.abreviatura),
                            fe.evento.get_base_de_calculo_display(),
                            fe.valor_base,
                        )
                    )
                except Exception as e:
                    raise e
    print("OK")
    print("CRIANDO ARQUIVO [CADASTRO DE BASES - %s]... " % folha.tipo_folha.abreviatura)
    with codecs.open(
        os.path.join(dir_, "cadastro_bases_%s.txt" % folha.tipo_folha.abreviatura),
        "w",
        "utf-8",
    ) as fd:
        fd.writelines(lines)
    print("OK")


def create_arquivo_viabillize(ano, mes):

    for folha in Folha.objects.filter(
        periodo__ano=ano, periodo__mes=mes, tipo_folha__margem__gt=0, status__in=[4, 3]
    ):
        print(">>>>>>>>>>>> %s " % folha)
        dir_name = "%s/%s" % (
            DIR,
            "viabillize_mpto/%s%02d%04d/"
            % (
                folha.tipo_folha.abreviatura or folha.tipo_folha.titulo,
                folha.periodo.mes,
                folha.periodo.ano,
            ),
        )
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        cadastro_eventos(dir_name)
        cadastro_funcional(folha, dir_name)
        cadastro_bases(folha, dir_name)
        arquivo_retorno(folha, dir_name)
        print(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % dir_name)
    else:
        print("<<<<<<<<< NENHUMA FOLHA PROCESSADA PARA ENVIAR...")
