# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes:

:Classes:
  :class:`PTPortalRelatorios`.

"""

import calendar
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# from rh.gfp import models
# from rh.gfp.views import CustomAutocomplete
# from rh.gfp.dirf.models import Demonstrativo
# from rh.models import Servidor, Cargo
# from standard.views import AutoCompleteField
# from unicodedata import normalize
from django.db.models import Q

from contrib.decorator import is_public, login_required

# from django import forms
# from django.template.defaultfilters import slugify
# from contrib.extjs import ExtReportBuild, ExtWidget
from contrib.extjs import ExtWidget
from contrib.helpers import get_cross_domain_response
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.models import MovimentacaoAposentadoria, MovimentacaoPosse
from rh.utils import format_situacao_funcional


class PTPortalRelatorios(ExtWidget):
    """
    **Classe** para gerenciamento de relatórios de recursos humanos.

    :Métodos:
        :func:`json`,
        :func:`get_rh_reports`,
        :func:`get_licensed_servers`,
        :func:`normalize_licensed_servers`,
        :func:`get_retired_servers`,
        :func:`normalize_retired_servers`,
        :func:`get_ceded_servers`,
        :func:`normalize_ceded_servers`,
        :func:`get_commissioned_servers`,
        :func:`normalize_commissioned_servers`,
        :func:`get_effective_servers`,
        :func:`normalize_effective_servers`,
        :func:`get_prosecutors_servers`,
        :func:`normalize_prosecutors_servers`,
        :func:`make_pagination`,
        :func:`format_cargo`.
    """

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.transparencia.Reports()")

    @is_public()
    def get_rh_reports(self, args=[]):

        # Recupera parametros de busca definidos pelo usuario
        year = self.request.GET.get("year") or None
        month = self.request.GET.get("month") or None

        report_pk = self.request.GET.get("report_pk") or None
        show_details = self.request.GET.get("show_details") or None

        report_type = self.request.GET.get("report_type") or 0
        report_type = int(report_type)

        # Recupera parametros utilizados para paginacao
        pagination = self.request.GET.get("pagination", False)
        page_number = self.request.GET.get("page_number", 1)
        max_registers = self.request.GET.get("max_registers", 20)
        search_value = self.request.GET.get("search_value") or ""

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []
        result = {}
        pars = {}

        if show_details:

            # Especifica flag para buscar detalhes
            self.show_details = show_details

            pars = {
                "show_details": show_details,
                "report_pk": report_pk,
                "report_type": report_type,
            }

        else:

            # Especifica flag para não buscar detalhes
            self.show_details = False

            # Especifica data limite para consultas
            self.data_pesquisa = datetime(
                int(year), int(month), calendar.monthrange(int(year), int(month))[1]
            )

            pars = {
                "year": year,
                "month": month,
                "pagination": pagination,
                "page_number": page_number,
                "max_registers": max_registers,
                "search_value": search_value,
            }

        # Recupera informacoes da base de dados
        if report_type == 1:
            values = self.get_licensed_servers(pars, result)

        elif report_type == 2:
            values = self.get_retired_servers(pars, result)

        elif report_type == 3:
            values = self.get_ceded_servers(pars, result)

        elif report_type == 4:
            values = self.get_commissioned_servers(pars, result)

        elif report_type == 5:
            values = self.get_effective_servers(pars, result)

        elif report_type == 6:
            values = self.get_prosecutors_servers(pars, result)

        # Especifica quantidade de registros encontrados
        result.update(collection=values)
        result.update(count=len(values))

        # Configura respostas para requisicoes cross domain
        self.response["Content-Type"] = "text/javascript"
        # out = self.get_cross_domain_response(result)
        out = get_cross_domain_response(self, result)
        self.response.write(out)

    def get_licensed_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:
            licensed = BaseLicencaAfastamento.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_licensed_servers(licensed)

            result.update(details=details)

        # Filtra servidores afastados e licenciados
        elif pars.get("year") and pars.get("month"):
            values = BaseLicencaAfastamento.objects.filter(
                (
                    ~Q(licenca__licencainteresseparticular=None)
                    | ~Q(licenca__licencamandatoclassista=None)
                    | ~Q(licenca__licencaafastamentoconjuge=None)
                )
                & (
                    Q(data_inicio__lte=self.data_pesquisa)
                    & (Q(data_fim__gt=self.data_pesquisa) | Q(data_fim=None))
                )
                & Q(servidor__ativo=True)
                & Q(
                    servidor__pessoa_fisica__nome__contains=pars.get(
                        "search_value"
                    ).upper()
                )
            ).order_by("servidor")

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_licensed_servers(values)

        return values

    def normalize_licensed_servers(self, values):

        if self.show_details:

            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "natureza": format_situacao_funcional(values.situacao_funcional),
                "cargo": "",
                "data_inicio": values.data_inicio,
            }

            cargo = None
            posse_ef = values.servidor.posses.filter(quadro__cargo__tipo_lei_cargo="EF")
            posse_cm_fc = values.servidor.posses.filter(
                quadro__cargo__tipo_lei_cargo__in=("CM", "FC", "EL", "ES", "AC")
            )
            if posse_ef.count():
                cargo = posse_ef[0]

            elif posse_cm_fc.count():
                cargo = posse_cm_fc[0]

            if cargo:
                normalized["cargo"] = self.format_cargo(cargo)
                normalized["data_exercicio"] = cargo.data_exercicio

        else:
            normalized = []
            for item in values:
                data = {
                    "report_pk": item.pk,
                    "nome": item.servidor.pessoa_fisica.nome,
                    "natureza": format_situacao_funcional(item.situacao_funcional),
                }
                normalized.append(data)

        return normalized

    def get_retired_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:

            retired = MovimentacaoAposentadoria.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_retired_servers(retired)

            result.update(details=details)

        # Filtra servidores aposentados
        elif pars.get("year") and pars.get("month"):
            values = MovimentacaoAposentadoria.objects.filter(
                data_desligamento__lte=self.data_pesquisa,
                servidor__ativo=False,
                servidor__pessoa_fisica__data_obito__isnull=True,
                servidor__pessoa_fisica__nome__contains=pars.get(
                    "search_value"
                ).upper(),
            ).order_by("servidor")

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_retired_servers(values)

        return values

    def normalize_retired_servers(self, values):

        if self.show_details:

            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "data_desligamento": values.data_desligamento,
                "natureza": "",
                "cargo": "",
            }

            # Recupera dados sobre o cargo do servidor quando se aposentou
            posse = values.movimentacao_posse
            if posse:
                normalized["cargo"] = posse.quadro.cargo.nome
                if posse.quadro.especialidade:
                    normalized["cargo"] += " - %s" % (posse.quadro.especialidade)

            if values.servidor.is_promotor or values.servidor.is_procurador:
                normalized["natureza"] = "Membro"

            else:
                normalized["natureza"] = "Servidor"

        else:
            normalized = []
            for item in values:
                data = {
                    "report_pk": item.pk,
                    "nome": item.servidor.pessoa_fisica.nome,
                    "cargo": "",
                }

                # Adiciona cargo do servidor aposentado
                if item.movimentacao_posse:
                    data["cargo"] = self.format_cargo(item.movimentacao_posse)

                normalized.append(data)

        return normalized

    def get_ceded_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:

            ceded = AfastamentoOutroOrgao.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_ceded_servers(ceded)

            result.update(details=details)

        # Filtra servidores cedidos para outros orgãos
        elif pars.get("year") and pars.get("month"):

            values = AfastamentoOutroOrgao.objects.filter(
                (
                    Q(data_inicio__lte=self.data_pesquisa)
                    & (Q(data_fim__gt=self.data_pesquisa) | Q(data_fim=None))
                )
                & Q(
                    servidor__pessoa_fisica__nome__contains=pars.get(
                        "search_value"
                    ).upper()
                )
            ).order_by("orgao__nome", "servidor")

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_ceded_servers(values)

        return values

    def normalize_ceded_servers(self, values):

        if self.show_details:

            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "orgao_destino": values.orgao.nome,
                "data_exercicio": values.posse.data_exercicio,
                "natureza": "",
                "cargo": "",
            }

            # Recupera o cargo do servidor cedido
            if values.posse:
                normalized["cargo"] = self.format_cargo(values.posse)

            if values.transito_pela_folha is True or values.onus == 2:
                normalized["natureza"] = "Cedido com ônus para o requisitante"

        else:

            normalized = []
            for item in values:

                data = {
                    "report_pk": item.pk,
                    "nome": item.servidor.pessoa_fisica.nome,
                    "orgao_destino": item.orgao.nome,
                }
                normalized.append(data)

        return normalized

    def get_commissioned_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:

            commissioned = MovimentacaoPosse.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_commissioned_servers(commissioned)

            result.update(details=details)

        # Filtra servidores comissionados
        elif pars.get("year") and pars.get("month"):

            values = (
                MovimentacaoPosse.objects.filter(
                    ativo=True,
                    quadro__cargo__tipo_lei_cargo="CM",
                    data_exercicio__lte=self.data_pesquisa,
                    servidor__servidor_lotacao__designacao=False,
                    servidor__servidor_lotacao__ativo=True,
                    servidor__pessoa_fisica__nome__contains=pars.get(
                        "search_value"
                    ).upper(),
                )
                .distinct()
                .values("pk", "servidor__pessoa_fisica__nome", "quadro__cargo__nome")
                .order_by("servidor__pessoa_fisica__nome")
            )

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_commissioned_servers(values)

        return values

    def normalize_commissioned_servers(self, values):

        if self.show_details:
            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "cargo": values.quadro.cargo.nome,
                "lotacao": "",
                "localidade": "",
                "data_exercicio": values.data_exercicio,
                "is_efetivo": "",
                "cargo_efetivo": "",
            }
            lotacao = values.servidor.servidor_lotacao.latest("pk").lotacao
            if lotacao:
                normalized["lotacao"] = lotacao.nome
                normalized["localidade"] = lotacao.localidade.nome

            if values.servidor.is_efetivo:
                normalized["is_efetivo"] = "Sim"

                posses = values.servidor.posses.filter(
                    quadro__cargo__tipo_lei_cargo="EF"
                )
                if posses.count():
                    normalized["cargo_efetivo"] = self.format_cargo(posses[0])
                    normalized["data_exercicio_efetivo"] = posses[0].data_exercicio
            else:
                normalized["is_efetivo"] = "Não"

        else:
            normalized = []
            for item in values:

                data = {
                    "report_pk": item.get("pk"),
                    "nome": item.get("servidor__pessoa_fisica__nome"),
                    "cargo": item.get("quadro__cargo__nome"),
                }
                normalized.append(data)

        return normalized

    def get_effective_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:

            effective = MovimentacaoPosse.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_effective_servers(effective)

            result.update(details=details)

        # Filtra servidores efetivos
        elif pars.get("year") and pars.get("month"):

            values = (
                MovimentacaoPosse.objects.filter(
                    ativo=True,
                    servidor__tipo="S",
                    servidor__servidor_lotacao__designacao=False,
                    servidor__servidor_lotacao__ativo=True,
                    servidor__ativo=True,
                    quadro__cargo__tipo_lei_cargo="EF",
                    data_exercicio__lte=self.data_pesquisa,
                    servidor__pessoa_fisica__nome__contains=pars.get(
                        "search_value"
                    ).upper(),
                )
                .distinct()
                .values(
                    "pk",
                    "servidor__pessoa_fisica__nome",
                    "servidor__servidor_lotacao__lotacao__nome",
                    "servidor__servidor_lotacao__lotacao__order_nome",
                )
                .order_by(
                    "servidor__servidor_lotacao__lotacao__order_nome",
                    "servidor__pessoa_fisica__nome",
                )
            )

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_effective_servers(values)

        return values

    def normalize_effective_servers(self, values):

        if self.show_details:

            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "cargo": values.quadro.cargo.nome,
                "lotacao": "",
                "localidade": "",
                "data_exercicio": values.data_exercicio,
                "is_comis_func": "",
                "cargo_comis_func": "",
            }
            if values.quadro.especialidade:
                normalized["cargo"] += " - %s" % (values.quadro.especialidade.nome)

            lotacao = values.servidor.servidor_lotacao.latest("pk").lotacao
            if lotacao:
                normalized["lotacao"] = lotacao.nome
                normalized["localidade"] = lotacao.localidade.nome

            # Recupera cargo comissionados
            posses = values.servidor.posses.filter(
                quadro__cargo__tipo_lei_cargo__in=["CM", "FC"]
            )
            if posses.count():
                normalized["is_comis_func"] = "Sim"
                normalized["cargo_comis_func"] = posses.latest(
                    "data_exercicio"
                ).quadro.cargo.nome
                normalized["data_exercicio_comis_func"] = posses.latest(
                    "data_exercicio"
                ).data_exercicio
            else:
                normalized["is_comis_func"] = "Não"

        else:

            normalized = []
            for item in values:

                data = {
                    "report_pk": item.get("pk"),
                    "nome": item.get("servidor__pessoa_fisica__nome"),
                    # 'cargo': item.get('quadro__cargo__nome')
                    "lotacao": item.get("servidor__servidor_lotacao__lotacao__nome"),
                }

                # if item.get('quadro__especialidade__nome'):
                #     data['cargo'] += ' - %s' % (item.get('quadro__especialidade__nome'))

                normalized.append(data)

        return normalized

    def get_prosecutors_servers(self, pars, result):

        # Cria vetor para armazenar os resultados personalizados da consulta
        values = []

        if self.show_details:

            prosecutors = MovimentacaoPosse.objects.get(pk=pars.get("report_pk"))

            # Personaliza informacoes
            details = self.normalize_prosecutors_servers(prosecutors)

            result.update(details=details)

        # Filtra servidores efetivos
        elif pars.get("year") and pars.get("month"):

            # values = MovimentacaoPosse.objects.filter(
            #     ativo=True,
            #     servidor__tipo='S',
            #     servidor__servidor_lotacao__designacao=False,
            #     servidor__servidor_lotacao__ativo=True,
            #     servidor__ativo=True,
            #     quadro__cargo__tipo_lei_cargo='EF',
            #     data_exercicio__lte=self.data_pesquisa,
            #     servidor__pessoa_fisica__nome__contains=pars.get('search_value').upper()
            # ).distinct().values(
            #     'pk',
            #     'servidor__pessoa_fisica__nome',
            #     'quadro__cargo__nome',
            #     'quadro__especialidade__nome'
            # ).order_by('servidor__pessoa_fisica__nome')

            values = MovimentacaoPosse.objects.filter(
                ativo=True, servidor__tipo="M", quadro__cargo__tipo_lei_cargo="EF"
            ).order_by(
                "servidor__servidor_lotacao__lotacao__order_nome",
                "servidor__pessoa_fisica__nome",
            )

            # values = MovimentacaoPosse.objects.filter(
            #     ativo=True,
            #     servidor__tipo='M',
            #     # servidor__servidor_lotacao__designacao=False,
            #     # servidor__servidor_lotacao__ativo=True,
            #     servidor__ativo=True,
            #     quadro__cargo__tipo_lei_cargo='EF',
            #     data_exercicio__lte=self.data_pesquisa,
            #     servidor__pessoa_fisica__nome__contains=pars.get('search_value').upper()
            # ).values(
            #     'pk',
            #     'servidor__pessoa_fisica__nome',
            #     'servidor__servidor_lotacao__lotacao__nome',
            #     'servidor__servidor_lotacao__lotacao__order_nome',
            # ).distinct().order_by(
            #     'servidor__servidor_lotacao__lotacao__order_nome',
            #     'servidor__pessoa_fisica__nome'
            # )

            # Cria estrutura de paginacao dos resultados
            if pars.get("pagination"):
                values = self.make_pagination(
                    pars.get("max_registers"), pars.get("page_number"), values, result
                )

            # Personaliza informacoes
            values = self.normalize_prosecutors_servers(values)

        return values

    def normalize_prosecutors_servers(self, values):

        if self.show_details:

            normalized = {
                "nome": values.servidor.pessoa_fisica.nome,
                "matricula": values.servidor.matricula,
                "cargo": values.movimentacaoposse.quadro.cargo.nome,
                "lotacao": "",
                "localidade": "",
                "data_exercicio": values.data_exercicio,
            }
            # if values.quadro.especialidade:
            #     normalized['cargo'] += ' - %s' % (values.quadro.especialidade.nome)

            lotacao = values.servidor.servidor_lotacao.latest("pk").lotacao
            if lotacao:
                normalized["lotacao"] = lotacao.nome
                normalized["localidade"] = lotacao.localidade.nome

            # # Recupera cargo comissionados
            # posses = values.servidor.posses.filter(quadro__cargo__tipo_lei_cargo__in=['CM', 'FC'])
            # if posses.count():
            #     normalized['is_comis_func'] = 'Sim'
            #     normalized['cargo_comis_func'] = posses.latest('data_exercicio').quadro.cargo.nome
            #     normalized['data_exercicio_comis_func'] = posses.latest('data_exercicio').data_exercicio
            # else:
            #     normalized['is_comis_func'] = 'Não'

        else:

            normalized = []
            for item in values:

                # data = {
                #     'report_pk': item.get('pk'),
                #     'nome': item.get('servidor__pessoa_fisica__nome'),
                #     # 'cargo': item.get('quadro__cargo__nome')
                #     'lotacao': item.get('servidor__servidor_lotacao__lotacao__nome')
                # }

                data = {
                    "report_pk": item.pk,
                    "nome": item.servidor.pessoa_fisica.nome,
                    # 'cargo': item.get('quadro__cargo__nome')
                    "lotacao": "",
                }

                for designacao in item.servidor.work_locations:
                    if designacao:
                        data["lotacao"] = designacao.nome
                    # print des.nome

                    normalized.append(data)

        return normalized

    # def get_cross_domain_response(self, result):
    #     ''' Método para configurar respostas cross domain conforme definido pelo cliente.

    #         :param result: Estrutura de dados a ser serializada.
    #         :type args: Object

    #         :returns:  Object -- Objeto ou nome de função de Callback.
    #     '''

    #     # Verifica a necessidade de configuracao
    #     if 'callback' in self.request.REQUEST:
    #         out = u'%s(%s)' % (
    #             self.request.GET.get('callback'),
    #             json.dumps(result, cls=DjangoJSONEncoder)
    #         )

    #     # Prepara resposta simples em formato json
    #     else:
    #         out = ezjson.dump(result)

    #     return out

    def make_pagination(self, max_registers, page_number, values, result):

        # Executa paginacao
        paginator = Paginator(values, max_registers)
        try:
            response = paginator.page(page_number)
        except PageNotAnInteger:
            response = paginator.page(1)
        except EmptyPage:
            response = paginator.page(paginator.num_pages)

        # Informa detalhes sobre a paginacao
        page_details = {
            "total": response.paginator.count,
            "num_pages": response.paginator.num_pages,
            "number": response.number,
            "start_index": response.start_index(),
            "end_index": response.end_index(),
            "has_previous": response.has_previous(),
            "has_next": response.has_next(),
        }
        result.update(page=page_details)

        return response

    def format_cargo(self, cargo):
        formatado = ""
        if cargo:
            if cargo.quadro:
                formatado = cargo.quadro.cargo.nome
                if cargo.quadro.especialidade:
                    if hasattr(cargo.quadro.especialidade, "nome"):
                        formatado += " - %s" % (cargo.quadro.especialidade.nome)
                    else:
                        formatado += " - %s" % (cargo.quadro.especialidade)
            else:
                cargo = cargo.description_possession

        return formatado
