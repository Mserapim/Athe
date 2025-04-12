# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes REST para o common.siatu.

:Classes:
  :class:`SiatuConfiguration`,
  :class:`SiatuDistribuicaoAutomatica`

"""

import calendar
import json
import re
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.template import loader

from common.siatu.models import (
    Anexo,
    Atendente,
    AtendentesServicos,
    Avaliacao,
    BaseConhecimento,
    Chamado,
    ConfigEmailAtendente,
    ConfigEmailSolicitante,
    DistribuicaoAutomatica,
    Gerente,
    ItemBaseConhecimento,
    Modelo,
    Objeto,
    Reincidencia,
    Servico,
    Solicitacao,
    Status,
    Terceirizada,
    TerceiroInterno,
    Transferencia,
)
from contrib import extjs
from edocs.protocolo.models import Protocolo
from contrib.controller import DefaultController
from contrib.helpers import clear_bug_fix_ext_editor
from contrib.newrest import Restful, RestfulTree
from contrib.nil import nil_unicode
from contrib.utils import DateUtils, employee_from_user, getLogger, person_from_user
from engine.notification.models import Message, Notification
from ged.models import Arquivo
from rh.models import OrgaoGeral
from standard.models import Configuration

log = getLogger(__name__)

SERVICO_CHOICES = (
    (1, "Administrativo"),
    (2, "Informática"),
    (3, "Banco de Dados"),
    (4, "Suporte Técnico/Manutenção de Informática"),
    (5, "Sistemas de informação"),
    (6, "Redes e comunicação"),
    (7, "Manutenção Administrativa"),
)


class __Helper:

    def telefone_usuario(self, args=[]):
        rst = {"success": False, "values": {}}

        qs = Solicitacao.objects.filter(solicitante_id=args[0]).exclude(telefone="")
        if qs.exists():
            telefone = qs.first().telefone
            rst.update(success=True, values={"telefone": telefone})
        else:
            person = person_from_user(User.objects.get(pk=args[0]))
            if person and person.phone.filter(tipo_telefone=5).exists():
                telefone = person.phone.first(tipo_telefone=5)
                rst.update(success=True, values={"telefone": telefone.numero})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class SiatuModelo(Restful):

    _model = Modelo

    force_upper = False

    full_text_index = ("descricao__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            descricao=instance.descricao,
            informatica=instance.informatica,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "informatica" in params:
            if params.get("informatica") == "true":
                params.update(informatica=True)
            elif params.get("informatica") == "false":
                params.update(informatica=False)
            else:
                params.update(informatica=None)

        if "descricao" in params:
            if params.get("descricao", "") == "":
                raise Exception("Informe uma descrição")

        log.debug(params)

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.BaseConhecimento.modelo.Manager")'
        )


class SiatuObjeto(Restful):

    _model = Objeto

    force_upper = False

    full_text_index = ("descricao__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            descricao=instance.descricao,
            informatica=instance.informatica,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(self.__class__, self).get_params(*args, **kargs)

        if "informatica" in params:
            params.update(informatica=True)
        else:
            params.update(informatica=False)

        if "descricao" in params:
            if params.get("descricao", "") == "":
                raise Exception("Informe uma descrição")

        if "modelos" in params:
            modelos = params.get("modelos", "")
            if modelos == "":
                modelos = []
            else:
                if isinstance(modelos, (list, tuple)) is False:
                    modelos = [modelos]
            params.update(modelos=[Modelo.objects.get(pk=m) for m in modelos])

        log.debug(params)

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.BaseConhecimento.objeto.Manager")'
        )


class SiatuBaseConhecimento(Restful):

    _model = BaseConhecimento

    force_upper = False

    full_text_index = (
        "problema__icontains",
        # 'solucao__icontains',
        "objeto__descricao__icontains",
        "modelo__descricao__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            objeto=instance.objeto.pk,
            objeto_string=instance.objeto.descricao,
            modelo=instance.modelo.pk if instance.modelo is not None else None,
            modelo_string=(
                instance.modelo.descricao if instance.modelo is not None else None
            ),
            problema=instance.problema,
            solucao=instance.solucao,
            arquivo=instance.arquivo.pk if instance.arquivo is not None else None,
            filename=(
                instance.arquivo.filename if instance.arquivo is not None else None
            ),
            permalink=(
                instance.arquivo.permalink() if instance.arquivo is not None else None
            ),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuBaseConhecimento, self).get_params(*args, **kargs)
        log.debug(params)

        if "objeto" in params:
            if params.get("objeto", "") == "":
                raise Exception("Favor informar um objeto")
            params.update(objeto=Objeto.objects.get(pk=params.get("objeto", 0)))

        if "modelo" in params:
            if params.get("modelo", "") == "":
                raise Exception("Favor informar um modelo")
            params.update(modelo=Modelo.objects.get(pk=params.get("modelo", 0)))

        if "arquivo" in params:
            if (params.get("arquivo", "0") == "0") or (params.get("arquivo", "") == ""):
                del params["arquivo"]
            else:
                params.update(arquivo=Arquivo.objects.get(pk=params.get("arquivo", 0)))

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.siatu.BaseConhecimento.Manager")')


class SiatuItemBaseConhecimento(Restful):

    _model = ItemBaseConhecimento

    force_upper = False

    full_text_index = (
        "base_conhecimento__problema__icontains",
        "base_conhecimento__solucao__icontains",
        "base_conhecimento__objeto__descricao__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            base_conhecimento=instance.base_conhecimento.pk,
            objeto=instance.base_conhecimento.objeto.pk,
            objeto_string=instance.base_conhecimento.objeto.descricao,
            modelo_string=(
                instance.base_conhecimento.modelo.descricao
                if instance.base_conhecimento.modelo is not None
                else None
            ),
            problema=instance.base_conhecimento.problema,
            solucao=instance.base_conhecimento.solucao,
            info=instance.info,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuItemBaseConhecimento, self).get_params(*args, **kargs)

        if "chamado" in params:
            params.update(chamado=Chamado.objects.get(pk=params.get("chamado", 0)))

        if "base_conhecimento" in params:
            params.update(
                base_conhecimento=BaseConhecimento.objects.get(
                    pk=params.get("base_conhecimento", 0)
                )
            )
        if self.Model.objects.filter(
            chamado=params.get("chamado"),
            base_conhecimento=params.get("base_conhecimento"),
        ).exists():
            raise Exception("Este item já está cadastrado")

        return params


class SiatuConfiguration(Restful):
    """
    **Classe** para acessar a configuração padrão de envio de emails.
    """

    _model = Configuration

    force_upper = False

    def json(self, args=[]):
        cfg = Configuration.get_or_create("siatu")
        values = {
            "pk": cfg.pk,
            "solicitante_aguardando_avaliacao": cfg.get(
                "solicitante_aguardando_avaliacao"
            ),
            "solicitante_transferido_atendente": cfg.get(
                "solicitante_transferido_atendente"
            ),
            "solicitante_garantia": cfg.get("solicitante_garantia"),
            "solicitante_terceirizada": cfg.get("solicitante_terceirizada"),
            "solicitante_viagem": cfg.get("solicitante_viagem"),
            "atendente_transferido_atendente": cfg.get(
                "atendente_transferido_atendente"
            ),
            "atendente_apos_avaliacao": cfg.get("atendente_apos_avaliacao"),
        }
        dicio = {"values": values}
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.configuration.email.Manager", %s)'
            % json.dumps(dicio)
        )

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            slug=instance.application,
            solicitante_aguardando_avaliacao=instance.get(
                "solicitante_aguardando_avaliacao"
            ),
            solicitante_transferido_atendente=instance.get(
                "solicitante_transferido_atendente"
            ),
            solicitante_garantia=instance.get("solicitante_garantia"),
            solicitante_terceirizada=instance.get("solicitante_terceirizada"),
            solicitante_viagem=instance.get("solicitante_viagem"),
            atendente_transferido_atendente=instance.get(
                "atendente_transferido_atendente"
            ),
            atendente_apos_avaliacao=instance.get("atendente_apos_avaliacao"),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuConfiguration, self).get_params(*args, **kargs)
        cfg = Configuration.get_or_create("siatu")
        if "solicitante_aguardando_avaliacao" in params:
            cfg.set("solicitante_aguardando_avaliacao", 1)
            del params["solicitante_aguardando_avaliacao"]
        else:
            cfg.set("solicitante_aguardando_avaliacao", 0)

        if "solicitante_transferido_atendente" in params:
            cfg.set("solicitante_transferido_atendente", 1)
            del params["solicitante_transferido_atendente"]
        else:
            cfg.set("solicitante_transferido_atendente", 0)

        if "solicitante_garantia" in params:
            cfg.set("solicitante_garantia", 1)
            del params["solicitante_garantia"]
        else:
            cfg.set("solicitante_garantia", 0)

        if "solicitante_terceirizada" in params:
            cfg.set("solicitante_terceirizada", 1)
            del params["solicitante_terceirizada"]
        else:
            cfg.set("solicitante_terceirizada", 0)

        if "solicitante_viagem" in params:
            cfg.set("solicitante_viagem", 1)
            del params["solicitante_viagem"]
        else:
            cfg.set("solicitante_viagem", 0)

        if "atendente_transferido_atendente" in params:
            cfg.set("atendente_transferido_atendente", 1)
            del params["atendente_transferido_atendente"]
        else:
            cfg.set("atendente_transferido_atendente", 0)

        if "atendente_apos_avaliacao" in params:
            cfg.set("atendente_apos_avaliacao", 1)
            del params["atendente_apos_avaliacao"]
        else:
            cfg.set("atendente_apos_avaliacao", 0)

        return params


class SiatuDistribuicaoAutomatica(Restful):
    """
    **Classe** para configurar a distribuição automática.
    """

    _model = DistribuicaoAutomatica

    force_upper = False

    def get_gerente(self):
        filtro = Gerente.objects.filter(usuario=self.request.user)
        gerente = filtro[0] if len(filtro) > 0 else 0
        return gerente

    def get_listServicosGerente(self):
        gerente = self.get_gerente()
        if gerente == 0:
            return []
        lista = [s.pk for s in gerente.lista_total_servicos()]

        return lista

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.configuration.distribuicao.Manager",'
            " {lista_servicos: %s})" % self.get_listServicosGerente()
        )

    def get_params(self, *args, **kargs):
        params = super(SiatuDistribuicaoAutomatica, self).get_params(*args, **kargs)

        tipo_atendimento = []

        if "servico" in params:
            servico = Servico.objects.get(pk=params.get("servico"))
            del params["servico"]
            try:
                gerente = Gerente.objects.get(usuario=self.request.user)
                if (servico in gerente.lista_total_servicos()) is False:
                    log.warn("Usuário não é gerente do servico %s" % servico)
                    raise Exception(
                        "Operação não permitida - usuário não é gerente do serviço %s"
                        % servico
                    )
            except Gerente.DoesNotExist:
                log.warn(
                    "Usuário não é gerente e teve acesso à tela Distribuição Automática"
                )
                raise Exception("Operação não permitida - usuário não é gerente")

        if "solicitantes" in params:
            solicitantes = params.get("solicitantes", [])
            if solicitantes == "":
                solicitantes = []
            if not isinstance(solicitantes, (list, tuple)):
                solicitantes = [solicitantes]
            params.update(
                solicitantes=[User.objects.get(pk=i) for i in solicitantes],
            )

        (
            tipo_atendimento.append("1")
            if "sistema" in params
            else tipo_atendimento.append("0")
        )
        (
            tipo_atendimento.append("1")
            if "email" in params
            else tipo_atendimento.append("0")
        )
        (
            tipo_atendimento.append("1")
            if "telefone" in params
            else tipo_atendimento.append("0")
        )
        (
            tipo_atendimento.append("1")
            if "documento" in params
            else tipo_atendimento.append("0")
        )
        (
            tipo_atendimento.append("1")
            if "verbal" in params
            else tipo_atendimento.append("0")
        )

        tipo_atendimento = DistribuicaoAutomatica.list_to_comma(tipo_atendimento)

        params.update(tipo_atendimento=tipo_atendimento)

        return params

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            servico_unicode=str(instance.servico),
            solicitantes=list(instance.solicitantes.values_list("pk", flat=True)),
        )
        for tipo in Solicitacao.TIPO_CHOICES:
            try:
                _dict_.update(
                    {tipo[1].lower(): instance.get_tipo_atendimento()[tipo[0]]},
                )
            except Exception:
                _dict_.update(
                    {tipo[1].lower(): "0"},
                )
        return _dict_


class SiatuServico(RestfulTree):

    _model = Servico

    force_upper = False

    folder_index = "servico_superior"

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        for attr in ("servico_superior",):
            if attr in params:
                if params.get(attr) != "":
                    field = getattr(self.Model, attr)
                    query = field.get_queryset()

                    try:
                        params.update({attr: query.get(pk=params.get(attr))})
                    except Exception as e:
                        log.exception(e)
                        raise e
                else:
                    params.update({attr: None})

        return params

    def first_last_date_month(self):
        n_date = datetime.today()
        month, year = n_date.month, n_date.year
        firstweekday, last_day = calendar.monthrange(year, month)
        # log.info([date(n_date.year, n_date.month, 1), date(n_date.year, n_date.month, last_day)])
        return [
            date(n_date.year, n_date.month, 1),
            date(n_date.year, n_date.month, last_day),
        ]

    def action_satisfacao_servico(self, args=[]):
        """Action que retorna o grau de satisfacao de um servico"""
        obj = {
            "result": {},
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            servico = self.Model.objects.get(pk=args[0])
            otimo = (
                servico.chamados.filter(avaliacao__satisfacao=5)
                .exclude(avaliacao__avaliacao_neutra=True)
                .count()
            )
            bom = (
                servico.chamados.filter(avaliacao__satisfacao=4)
                .exclude(avaliacao__avaliacao_neutra=True)
                .count()
            )
            regular = (
                servico.chamados.filter(avaliacao__satisfacao=3)
                .exclude(avaliacao__avaliacao_neutra=True)
                .count()
            )
            ruim = (
                servico.chamados.filter(avaliacao__satisfacao=2)
                .exclude(avaliacao__avaliacao_neutra=True)
                .count()
            )
            pessimo = (
                servico.chamados.filter(avaliacao__satisfacao=1)
                .exclude(avaliacao__avaliacao_neutra=True)
                .count()
            )

            all_sub_services = []
            all_sub_services.extend(servico.subservicos.all())
            for i in all_sub_services:
                all_sub_services.extend(i.subservicos.all())
                otimo = (
                    otimo
                    + i.chamados.filter(avaliacao__satisfacao=5)
                    .exclude(avaliacao__avaliacao_neutra=True)
                    .count()
                )
                bom = (
                    bom
                    + i.chamados.filter(avaliacao__satisfacao=4)
                    .exclude(avaliacao__avaliacao_neutra=True)
                    .count()
                )
                regular = (
                    regular
                    + i.chamados.filter(avaliacao__satisfacao=3)
                    .exclude(avaliacao__avaliacao_neutra=True)
                    .count()
                )
                ruim = (
                    ruim
                    + i.chamados.filter(avaliacao__satisfacao=2)
                    .exclude(avaliacao__avaliacao_neutra=True)
                    .count()
                )
                pessimo = (
                    pessimo
                    + i.chamados.filter(avaliacao__satisfacao=1)
                    .exclude(avaliacao__avaliacao_neutra=True)
                    .count()
                )

            satisfacao = {
                "Ótimo": otimo,
                "Bom": bom,
                "Regular": regular,
                "Ruim": ruim,
                "Péssimo": pessimo,
            }
            maioria = max(satisfacao, key=satisfacao.get)
            avaliacoes = [otimo, bom, regular, ruim, pessimo]

            try:
                percentual = float(max(avaliacoes)) / sum(avaliacoes) * 100
            except ZeroDivisionError:
                percentual = 0
                maioria = "Ótimo"

            try:
                perc_Otimo = "%.1f%s" % (
                    (float(avaliacoes[0]) / sum(avaliacoes) * 100),
                    "%",
                )
                perc_Bom = "%.1f%s" % (
                    (float(avaliacoes[1]) / sum(avaliacoes) * 100),
                    "%",
                )
                perc_Regular = "%.1f%s" % (
                    (float(avaliacoes[2]) / sum(avaliacoes) * 100),
                    "%",
                )
                perc_Ruim = "%.1f%s" % (
                    (float(avaliacoes[3]) / sum(avaliacoes) * 100),
                    "%",
                )
                perc_Pessimo = "%.1f%s" % (
                    (float(avaliacoes[4]) / sum(avaliacoes) * 100),
                    "%",
                )
            except ZeroDivisionError:
                perc_Otimo = perc_Bom = perc_Regular = perc_Ruim = perc_Pessimo = "0 %"

            todos = (
                "O: "
                + perc_Otimo
                + " B: "
                + perc_Bom
                + " R: "
                + perc_Regular
                + " R: "
                + perc_Ruim
                + " P: "
                + perc_Pessimo
            )

            percentual = "%.1f%s" % ((percentual), "%")

            # icons = {
            #     'Ótimo': '<div class="icon-siatu128 icon-siatu128-otimo128" title="Ótimo"></div>',
            #     'Bom': '<div class="icon-siatu128 icon-siatu128-bom128" title="Bom"></div>',
            #     'Regular': '<div class="icon-siatu128 icon-siatu128-regular128" title="Regular"></div>',
            #     'Ruim': '<div class="icon-siatu128 icon-siatu128-ruim128" title="Ruim"></div>',
            #     'Péssimo': '<div class="icon-siatu128 icon-siatu128-pessimo128" title="Péssimo"></div>'
            # }
            icons = {
                "Ótimo": '<div class="icon-siatu50 icon-siatu50-otimo50" title="Ótimo"></div>',
                "Bom": '<div class="icon-siatu50 icon-siatu50-bom50" title="Bom"></div>',
                "Regular": '<div class="icon-siatu50 icon-siatu50-regular50" title="Regular"></div>',
                "Ruim": '<div class="icon-siatu50 icon-siatu50-ruim50" title="Ruim"></div>',
                "Péssimo": '<div class="icon-siatu50 icon-siatu50-pessimo50" title="Péssimo"></div>',
            }

            maioria = icons.get(maioria)

            chamado = Chamado.objects.get(pk=args[1])
            atendentes_aptos = chamado.atendentes_aptos()

            qtd_chamados_hj = Chamado.objects.filter(
                servico__in=[servico.id],
                data_fila_atendimento__year=datetime.today().year,
                data_fila_atendimento__month=datetime.today().month,
                data_fila_atendimento__day=datetime.today().day,
            ).count()

            # CALCULA A QUANTIDADE DE CHAMADOS ABERTOS NO MÊS
            qtd_chamado_mes = Status.objects.filter(
                chamado__servico__in=[servico.id],
                status__in=[1],
                data_inicio__year=datetime.today().year,
                data_inicio__month=datetime.today().month,
            ).count()
            # log.info('>>> CHAMADOS NO MES: %s ' % qtd_chamado_mes)

            chamados_abertos = servico.chamados.filter(
                status_atual__status__in=[1, 2]
            ).count()

            result = {
                "nome": "Área avaliada: %s" % servico.nome,
                "maioria": maioria,
                "percentual": percentual,
                "texto": todos,
                "atendentes": atendentes_aptos.count(),
                "chamados_hoje": "%s chamado(s)" % qtd_chamados_hj,
                "chamados_mes": "%s chamado(s)" % qtd_chamado_mes,
                "chamados_abertos": "%s chamado(s)" % chamados_abertos,
            }

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(
                {
                    "result": result,
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            nome=nil_unicode(instance.nome, None),
        )
        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.siatu.servico.Manager")')


class SiatuServicoGerente(RestfulTree):
    """
    **Classe** para fornecer acesso ao gerenciamento de serviço com permissão de gerente.
    """

    _model = Servico

    def get_gerente(self):
        filtro = Gerente.objects.filter(usuario=self.request.user)
        gerente = filtro[0] if len(filtro) > 0 else 0
        return gerente

    def get_listServicosGerente(self):
        gerente = self.get_gerente()
        if gerente == 0:
            return []
        lista = [s.pk for s in gerente.lista_total_servicos()]

        return lista

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.servico.ManagerGerente",'
            " {lista_servicos: %s})" % self.get_listServicosGerente()
        )


class SiatuAtendente(Restful):

    _model = Atendente

    force_upper = False

    force_orm_single = True

    full_text_index = ("usuario__username__icontains",)

    def action_pedir_chamado(self, args=[]):
        """Action para um atendente pedir mais um chamado."""
        rst = {
            "success": False,
            "message": "Não foi processado ainda",
        }
        try:
            atendente = Atendente.objects.get(usuario=self.request.user)
            servidor = employee_from_user(self.request.user)

            if atendente.tem_chamado_aguardando_atendimento() is True:
                raise Exception("Favor atender os chamados pendentes primeiro")
            if not servidor:
                raise Exception("Erro: Atendente não é servidor ativo")
            if servidor.workplace_current is None:
                raise Exception("Erro: Atendente não possui lotacao atual")

            chamados_a_receber = []
            for servico in atendente.servicos_vinculados.all():
                for fila in servico.filas.filter(
                    localidade=servidor.workplace_current.localidade.nome.upper()
                ):
                    if fila.chamados.exists() is True:
                        chamados_da_fila = fila.chamados.order_by(
                            "nao_urgente", "-urgente", "-rank", "data_fila_atendimento"
                        )
                        for c in chamados_da_fila:
                            # se o atendente logado esta apto a receber chamado dessa fila entao coloca na lista
                            # inserindo apenas os que ele pode de fato receber
                            # estao fora os chamados reincidentes que o atendente esta associado ao ch. anterior
                            if (
                                c.atendentes_aptos().filter(pk=atendente.pk).exists()
                                is True
                            ):
                                chamados_a_receber.append(c)

            chamados = Chamado.objects.filter(pk__in=[c.pk for c in chamados_a_receber])

            if chamados.exists() is True:
                # distribui o primeiro chamado da lista ordenada
                ch = chamados.order_by(
                    "nao_urgente", "-urgente", "-rank", "data_fila_atendimento"
                )[0]
                ch.atendentes.add(atendente)
                ch.fila = None
                ch.data_fila_atendimento = datetime.now()
                ch.save(system=True)
            else:
                raise Exception(
                    "Não há chamados que você possa receber automaticamente"
                )

        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update({"success": True, "message": "Processado com sucesso!"})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def action_atendentes_not_in_chamado(self, args=[]):
        """Action que retorna os atendentes que não estão vinculados a um chamado."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            chamado = Chamado.objects.get(pk=args[0])
            lista_total_atendentes = [
                a.pk for a in chamado.servico.lista_total_atendentes()
            ]

            query = self.Model.objects.filter(pk__in=lista_total_atendentes)
            query = query.exclude(chamados=chamado)

            if "keyword" in self.request.POST:
                query = self.do_full_text_filter(query)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def action_atendentes_not_in_service(self, args=[]):
        """Action que retorna os atendentes que não estão vinculados a um serviço."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            query = self.Model.objects.exclude(servicos_vinculados=args[0])

            if "keyword" in self.request.POST:
                query = self.do_full_text_filter(query)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)

        servidor = employee_from_user(instance.usuario)

        _dict_.update(
            busy=instance.icon_busy,
            username=instance.usuario.username,
            nome=(
                servidor.pessoa_fisica.nome
                if servidor is not None
                else instance.usuario.username
            ),
            notificacao_receber_chamado=instance.notificacao_receber_chamado,
            servicos_vinculados=list(
                instance.servicos_vinculados.values_list("pk", flat=True)
            ),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuAtendente, self).get_params(*args, **kargs)

        if "usuario" in params:
            if params.get("usuario", "") == "":
                raise Exception("Favor informar um usuário")
            params.update(usuario=User.objects.get(pk=params.get("usuario", 0)))
            if self.Model.objects.filter(usuario=params.get("usuario")).exists():
                raise Exception("Este atendente já está cadastrado")

        if "servicos_vinculados" in params:
            params.update(
                servicos_vinculados=[
                    Servico.objects.get(pk=i)
                    for i in params.get("servicos_vinculados", 0)
                ]
            )

        if "notificacao_receber_chamado" in params:
            params.update(notificacao_receber_chamado=True)
        else:
            params.update(notificacao_receber_chamado=False)

        log.debug(params)
        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.atendente.Manager",'
            " {concluido: %d})" % (Status.CONCLUIDO)
        )


class SiatuServicoAtendentes(RestfulTree):
    """
    **Classe** para fornecer recursos da relação entre serviços e atendentes.
    """

    _model = AtendentesServicos

    force_upper = False

    full_text_index = ("atendente__usuario__username__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            busy=instance.atendente.icon_busy,
            username=instance.atendente.usuario.username,
            nome=instance.atendente.usuario.get_full_name(),
            distribuicao_automatica=instance.distribuicao_automatica,
            icon_dist=instance.icon_dist_aut,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuServicoAtendentes, self).get_params(*args, **kargs)

        if "atendente" in params:
            if params.get("atendente") != "":
                field = getattr(self.Model, "atendente")

                query = field.get_queryset()

                try:
                    params.update(atendente=query.get(pk=params.get("atendente")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(atendente=None)

        if "servico" in params:
            if params.get("servico") != "":
                field = getattr(self.Model, "servico")

                query = field.get_queryset()

                try:
                    servico = query.get(pk=params.get("servico"))
                    params.update(servico=servico)

                    if self.request.user.has_perm("siatu.admin") is False:
                        gerente = Gerente.objects.get(usuario=self.request.user)
                        if (servico in gerente.lista_total_servicos()) is False:
                            log.warn("Usuário não é gerente do servico %s" % servico)
                            raise Exception(
                                "Operação não permitida - usuário não é gerente do serviço %s"
                                % servico
                            )
                except Gerente.DoesNotExist:
                    log.warn(
                        "Usuário não é gerente e teve acesso à tela Gerenciamento de Serviços para gerentes"
                    )
                    raise Exception("Operação não permitida - usuário não é gerente")

                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(servico=None)

        if "distribuicao_automatica" in params:
            if params.get("distribuicao_automatica") == "true":
                params.update(distribuicao_automatica=True)
            elif params.get("distribuicao_automatica") == "false":
                params.update(distribuicao_automatica=False)

        log.debug(params)
        return params


class SiatuGerente(Restful):

    _model = Gerente

    force_upper = False

    force_orm_single = True

    full_text_index = ("usuario__username__icontains",)

    def action_gerentes_not_in_service(self, args=[]):
        """Action que retorna os atendentes que não estão vinculados a um serviço."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            query = self.Model.objects.exclude(servicos_vinculados=args[0])

            if "keyword" in self.request.POST:
                query = self.do_full_text_filter(query)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            username=instance.usuario.username,
            nome=instance.usuario.get_full_name(),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuGerente, self).get_params(*args, **kargs)
        log.debug(params)
        if "usuario" in params:
            if params.get("usuario", "") == "":
                raise Exception("Favor informar um usuário")
            params.update(usuario=User.objects.get(pk=params.get("usuario", 0)))

        log.debug(params)
        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.siatu.gerente.Manager")')


class SiatuSolicitacao(Restful, __Helper):

    _model = Solicitacao

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        lotacao = None

        servidor = employee_from_user(instance.solicitante)
        if servidor:
            lotacao = servidor.workplace_by_date()
            if lotacao:
                lotacao = lotacao.nome
            else:
                lotacao = "Sem lotação vigente"
        else:
            lotacao = "Servidor não encontrado"

        _dict_.update(
            solicitante=instance.solicitante.pk,
            solicitante_username=instance.solicitante.username,
            solicitante_lotacao=lotacao,
            telefone=instance.telefone,
            servico=instance.servico.pk,
            servico_unicode=str(instance.servico),
            tipo=instance.tipo,
            tipo_display=instance.get_tipo_display(),
            descricao_problema=instance.descricao_problema,
            reincidencia=instance.reincidencia,
            chamado=instance.chamado.pk if instance.chamado is not None else None,
            chamado_anterior=(
                instance.chamado_anterior.pk
                if instance.chamado_anterior is not None
                else None
            ),
        )
        return _dict_

    def telefone_usuario(self, args=[]):
        rst = {"success": False, "values": {}}

        qs = Solicitacao.objects.filter(solicitante_id=args[0], telefone__regex=r"^.+")
        if qs.exists():
            telefone = qs[0].telefone
            if telefone:
                rst.update(success=True, values={"telefone": telefone})
        else:
            usuario = User.objects.get(pk=args[0])
            if usuario:
                servidor = usuario.servidor
                telefone = servidor.pessoa_fisica.phone.filter(tipo_telefone=5)
                if telefone:
                    rst.update(success=True, values={"telefone": telefone[0].numero})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = super(SiatuSolicitacao, self).get_params(*args, **kargs)
        log.debug(params)

        if "servico" in params:
            if params.get("servico", "") == "":
                raise Exception("Favor informar um serviço")
            try:
                params.update(servico=Servico.objects.get(pk=params.get("servico", 0)))
            except Servico.DoesNotExist as e:
                log.exception(e)
                raise Exception("Serviço inexistente")

        if "solicitante" in params:
            if params.get("solicitante", "") == "":
                raise Exception("Favor informar um solicitante")
            params.update(solicitante=User.objects.get(pk=params.get("solicitante", 0)))
        else:
            params.update(solicitante=self.request.user)

        if "orgao_geral_origem" in params:
            if params.get("orgao_geral_origem", "") == "":
                raise Exception(
                    "Favor informar uma Lotação para qual o chamado será aberto!"
                )
            try:
                params.update(
                    orgao_geral_origem=OrgaoGeral.objects.get(
                        pk=params.get("orgao_geral_origem", 0)
                    )
                )
            except OrgaoGeral.DoesNotExist as e:
                log.exception(e)
                raise Exception("Orgão Geral inexistente")
        else:
            user_solicitante = params.get("solicitante")
            params.update(
                orgao_geral_origem=user_solicitante.servidor.workplace_current
            )

        if "tipo" in params:
            if params.get("tipo", "") == "":
                raise Exception("Favor informar um tipo")
            params.update(tipo=int(params.get("tipo")))

        if "telefone" in params:
            if params.get("telefone", "") == "":
                raise Exception("Favor informar um Telefone")
            params.update(telefone=int(params.get("telefone")))

        if "descricao_problema" in params:
            if params.get("descricao_problema", "") == "":
                raise Exception("Favor informar um problema")

        if "gerente" in params:
            del params["gerente"]

        if "concluido" in params:
            del params["concluido"]

        if "lista_servicos" in params:
            del params["lista_servicos"]

        if "possui_chamados_avaliar" in params:
            del params["possui_chamados_avaliar"]

        if "chamado_anterior" in params:
            if params.get("chamado_anterior", "") == "":
                raise Exception("Favor informar o chamado anterior")
            params.update(
                chamado_anterior=Chamado.objects.get(
                    pk=params.get("chamado_anterior", 0)
                )
            )

        if "reincidencia" in params:
            params.update(reincidencia=params.get("reincidencia").lower() == "on")

        params.update(usuario=self.request.user)

        return params


class SiatuAvaliacao(Restful):

    _model = Avaliacao

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            sugestao=instance.sugestao,
            chamado=instance.chamado.pk,
            replica=instance.replica,
            satisfacao_display=instance.get_satisfacao_display(),
            presteza_display=instance.get_presteza_display(),
            esclarecimento_display=instance.get_esclarecimento_display(),
            tempo_display=instance.get_tempo_display(),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuAvaliacao, self).get_params(*args, **kargs)
        log.debug(params)
        if "chamado" in params:
            if params.get("presteza", "") == "":
                raise Exception("Favor avaliar o item presteza no atendimento")

            if params.get("esclarecimento", "") == "":
                raise Exception("Favor avaliar o item esclarecimento")

            if params.get("tempo", "") == "":
                raise Exception("Favor avaliar o item tempo decorrido")

            if params.get("satisfacao", "") == "":
                raise Exception("Favor informar a classificação geral do atendimento")

            params.update(satisfacao=int(params.get("satisfacao") or 0))

            if (params.get("satisfacao") < 4) and (params.get("sugestao", "") == ""):
                raise Exception("Favor informar uma sugestão")

            params.update(chamado=Chamado.objects.get(pk=params.get("chamado", 0)))
        log.debug(params)
        return params

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("siatu.admin") is False:
            if self.request.user.has_perm("siatu.gerente") is False:
                if self.request.user.has_perm("siatu.atendente") is False:
                    query = query.none()
                else:
                    atendente = Atendente.objects.filter(usuario=self.request.user)
                    chamados = []
                    if atendente.exists():
                        atendente = atendente[0]
                        chamados = Chamado.objects.filter(atendentes=atendente)
                    query = query.filter(chamado__in=chamados)

        return query

    def neutralizar_chamado(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            avaliacao = self._model.objects.get(
                chamado__pk=int(self.request.POST.get("pk"))
            )
            justificativa = self.request.POST.get("justificativa_netra")
            if len(justificativa) < 26:
                rst.update(
                    success=False, message="Favor informar uma justificativa maior"
                )
                # raise Exception('Favor informar uma justificativa maior')
            else:
                avaliacao.neutraliza_avalicao(justificativa)
                rst.update(success=True, message="Procedimento realizado com sucesso.")
        except Avaliacao.DoesNotExist:
            rst.update(message="Avaliação não encontrada!")
        except Exception as e:
            rst.update(message=str(e))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class SiatuReincidencia(Restful):

    _model = Reincidencia

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            opiniao_atendente=instance.opiniao_atendente,
            confirm_atendente=instance.confirm_atendente,
            motivo_gerente=instance.motivo_gerente,
            parecer=instance.parecer,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuReincidencia, self).get_params(*args, **kargs)

        if "atendente" in params:
            if "confirm_atendente" in params:
                if params.get("confirm_atendente", "") == "Yes":
                    params.update(confirm_atendente=True)
                else:
                    params.update(confirm_atendente=False)
        if "gerente" in params:
            if "parecer" in params:
                if params.get("parecer", "") == "Yes":
                    params.update(parecer=True)
                else:
                    params.update(parecer=False)
        log.debug(params)
        return params

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("siatu.admin") is False:
            if self.request.user.has_perm("siatu.gerente") is False:
                if self.request.user.has_perm("siatu.atendente") is False:
                    query = query.none()

        return query


class SiatuTerceirizada(Restful):

    _model = Terceirizada

    force_upper = False

    full_text_index = ("nome__icontains",)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            nome=instance.nome,
            cnpj=instance.cnpj,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuTerceirizada, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor preencher os campos obrigatórios")

        return params

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.siatu.terceirizada.Manager")')


class SiatuTerceiroInterno(Restful):

    _model = TerceiroInterno

    force_upper = False

    full_text_index = ("nome__icontains",)

    def action_terceiros_not_in_chamado(self, args=[]):
        """Action que retorna os terceiros que não estão vinculados a um chamado."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            chamado = Chamado.objects.get(pk=args[0])

            query = self.Model.objects.exclude(chamados=chamado)

            if "keyword" in self.request.POST:
                query = self.do_full_text_filter(query)
            query = query.exclude(status=2)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            busy=instance.icon_busy,
            nome=instance.nome,
            cpf=instance.cpf,
            telefone=instance.telefone,
            endereco=instance.endereco,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuTerceiroInterno, self).get_params(*args, **kargs)

        if "nome" in params:
            if params.get("nome", "") == "":
                raise Exception("Favor preencher os campos obrigatórios")

        return params

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("siatu.admin") is False:
            if self.request.user.has_perm("siatu.gerente") is False:
                if self.request.user.has_perm("siatu.atendente") is False:
                    chamados = Chamado.objects.filter(
                        solicitacao__solicitante=self.request.user
                    )
                    query = query.filter(chamados__in=chamados).distinct()

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.siatu.terceiro.Manager")')


class SiatuChamado(Restful, __Helper):

    _model = Chamado

    force_upper = False

    full_text_index = (
        "solicitacao__solicitante__username__icontains",
        "servico__nome__icontains",
        "cache_numero__icontains",
        "solicitacao__descricao_problema__icontains",
        "solicitacao__solicitante__servidor__lotacoes__nome__icontains",
    )

    force_orm_single = True

    def get_atendente(self):
        filtro = Atendente.objects.filter(usuario=self.request.user)
        atendente = filtro[0].pk if len(filtro) > 0 else 0
        return atendente

    def telefone_usuario(self, args=[]):
        rst = {"success": False, "values": {}}
        user_id = args[0] if args else self.request.user.pk
        qs = Solicitacao.objects.filter(solicitante_id=user_id, telefone__regex=r"^.+")
        if qs.exists():
            telefone = qs[0].telefone
            if telefone:
                rst.update(success=True, values={"telefone": telefone})
        else:
            user = User.objects.filter(pk=user_id).first()
            servidor = employee_from_user(user)
            if servidor:
                telefone = servidor.pessoa_fisica.phone.filter(tipo_telefone=5)
                if telefone.exists():
                    rst.update(success=True, values={"telefone": telefone[0].numero})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def action_transf_waiting(self, args=[]):
        """Action que retorna as transferências a espera do aceite do atendente logado."""
        obj = {
            "success": False,
            "message": "Não foi processado ainda",
            "count": 0,
            "collection": [],
        }
        try:
            transferencias = Transferencia.objects.filter(
                aceito_por__isnull=True,
                cancelado=False,
                atendente_posterior=self.get_atendente(),
            ).exclude(atendente_anterior=self.get_atendente())

            query = self.Model.objects.filter(
                pk__in=transferencias.values_list("chamado", flat=True)
            )

            if "keyword" in self.request.POST:
                query = self.do_full_text_filter(query)

        except Exception as e:
            obj.update(message=str(e))
            log.exception(e)
        else:
            obj.update(count=query.count())
            obj.update(
                {
                    "collection": [self.model_to_dict(record) for record in query],
                    "success": True,
                    "message": "Processado com sucesso!",
                }
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(obj)

    def fill_instance_m2m(self, instance, values):
        # if instance.status_atual.status == models.Status.CONCLUIDO or instance.status_atual.status == models.Status.AGUARDANDO_AVALIACAO:
        #     log.warn("Operação não permitida - chamado concluído")
        #     raise Exception(u"Operação não permitida - chamado concluido")
        fields = [f.name for f in instance._meta.many_to_many]
        old_atendentes = list(instance.atendentes.values_list("pk", flat=True))

        for key, value in list(values.items()):
            field = getattr(instance, key, None)
            if key in fields and isinstance(value, (tuple, list, set)):
                field.clear()
                for item in value:
                    field.add(item)

                if key == "atendentes" or key == "terceiro_interno":
                    if not Status.objects.filter(
                        status=Status.AGUARDANDO_ATENDIMENTO, chamado=instance
                    ).exists():
                        s = Status(
                            status=Status.AGUARDANDO_ATENDIMENTO,
                            data_inicio=datetime.now(),
                            chamado=instance,
                        )
                        s.save()
                if key == "atendentes":
                    # Enviar notificação para atendentes novos
                    at_novos = instance.atendentes.exclude(pk__in=old_atendentes)
                    log.info("Enviando email para atendentes - recebimento de chamado")
                    try:
                        for atendente_novo in at_novos:
                            if atendente_novo.notificacao_receber_chamado is True:
                                msg = Message.objects.get(mid="siatu-atendente-recebe")
                                servidor_atendente = employee_from_user(
                                    atendente_novo.usuario
                                )
                                Notification.notify(
                                    msg,
                                    servidor_atendente,
                                    types=["SYS", "EMAIL"],
                                    chamado=instance.cache_numero,
                                )
                                log.info("Email enviado com sucesso")
                            else:
                                log.info("Envio de email desativado")
                    except Exception as e:
                        log.info("Email não enviado")
                        log.exception(e)
                    # Fim envio notificação para atendentes novos

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        # pos = posicao na fila
        posicao = None
        tipo_fila = None

        # Mostrar posicao na fila unica caso chamado esteja em uma Fila Unica
        if instance.fila is not None:
            try:
                chamados = list(
                    instance.fila.chamados.order_by(
                        "nao_urgente", "-urgente", "-rank", "data_fila_atendimento"
                    )
                )
                posicao = chamados.index(instance) + 1
                tl = instance.fila.localidade
                if tl:
                    tipo_fila = tl
            except Exception:
                pass
        else:
            if instance.atendentes.all().exists() is True:
                # Mostrar posicao na fila individual do atendente caso o chamado esteja associado a um atendente
                for a in instance.atendentes.all():
                    chamados = Chamado.objects.filter(
                        atendentes=a, status_atual__status=Status.AGUARDANDO_ATENDIMENTO
                    )
                    chamados = list(
                        chamados.order_by(
                            "nao_urgente", "-urgente", "-rank", "data_fila_atendimento"
                        )
                    )
                    try:
                        qt = chamados.index(instance)
                        posicao = (
                            qt if ((posicao is None) or (qt < posicao)) else posicao
                        )
                        s = employee_from_user(
                            instance.atendentes.first().usuario, only_active=False
                        )
                        lot = (
                            s.workplace_current.localidade.nome
                            if s.workplace_current
                            else ""
                        )
                        if lot:
                            tipo_fila = "Atendente - " + lot
                    except ValueError:
                        # Caso em que o chamado ja atribuido a atendente nao esta no status Aguardando Atendimento
                        posicao = None
                posicao = posicao if posicao is None else posicao + 1
            else:
                if instance.terceiro_interno.exists() is True:
                    for a in instance.terceiro_interno.all():
                        chamados = Chamado.objects.filter(
                            terceiro_interno=a,
                            status_atual__status=Status.AGUARDANDO_ATENDIMENTO,
                        )
                        chamados = list(
                            chamados.order_by(
                                "nao_urgente",
                                "-urgente",
                                "-rank",
                                "data_fila_atendimento",
                            )
                        )
                        try:
                            qt = chamados.index(instance)
                            posicao = (
                                qt if ((posicao is None) or (qt < posicao)) else posicao
                            )
                        except ValueError:
                            # Caso em que o chamado ja atribuido a terceiro nao esta no status Aguardando Atendimento
                            posicao = None
                    posicao = posicao if posicao is None else posicao + 1

        tempo_decorrido = instance.tempo_decorrido_chamado

        try:
            avaliacao = instance.avaliacao.get_satisfacao_display()
            avaliacao_pk = instance.avaliacao.pk
            replica_avaliacao = instance.avaliacao.replica
        except Exception:
            avaliacao = None
            avaliacao_pk = None
            replica_avaliacao = ""

        # Somente haverá no máximo uma transferência ativa, por causa do controle a cada inserção
        transf_ativa = instance.transferencias.filter(
            aceito_por__isnull=True, cancelado=False
        )
        transf_ativa = transf_ativa[0].pk if transf_ativa.exists() else None

        s = employee_from_user(instance.solicitacao.solicitante)
        if s:
            m = s.membro
            n = s.pessoa_fisica.nome
            lot = s.workplace_by_date()
            if not lot:
                log.info(
                    "Chamado n.%s não possui lotação definida", instance.cache_numero
                )
            c = lot.localidade.nome if lot else "Sem lotação vigente"
            lotacao = lot.nome if (lot is not None) else "Sem lotação vigente"
            cidade = c if (lot is not None) else "Não encontrada"
            membro = "Sim" if (m) else "Não"
            nome = n if (n) else "Ñão encontrado"
        else:
            lotacao = ""
            cidade = ""
            membro = ""
            nome = "Servidor não encontrado"

        _dict_.update(
            identificacao=instance.cache_numero,
            solicitacao=instance.solicitacao.pk,
            solicitante=instance.solicitacao.solicitante.pk,
            solicitante_username=instance.solicitacao.solicitante.username,
            solicitante_nome=nome,
            solicitante_cidade=cidade,
            solicitante_lotacao=lotacao,
            solicitante_membro=membro,
            telefone=instance.solicitacao.telefone,
            servico=instance.servico.pk,
            servico_atendentes=[
                a.pk for a in instance.servico.lista_total_atendentes()
            ],
            servico_unicode=str(instance.servico),
            transf_ativa=transf_ativa,
            icon_status=instance.icons,
            status_atual=str(instance.status_atual),
            tempo_decorrido=(
                tempo_decorrido
                if (tempo_decorrido and instance.cancelado is False)
                else "0d 0h 0s"
            ),
            avaliacao=avaliacao,
            avaliacao_pk=avaliacao_pk,
            replicado=False if replica_avaliacao is None else True,
            problema_solicitante=instance.solicitacao.descricao_problema,
            fila=posicao,
            tipo_fila=tipo_fila,
            cancelado=instance.cancelado,
            motivo_cancelado=instance.motivo_cancelado,
            urgente=instance.urgente,
            rank=instance.rank,
            motivo_urgencia=instance.motivo_urgencia,
            atendentes=list(instance.atendentes.values_list("pk", flat=True)),
            atendente_unicode=(
                " ".join([a.usuario.username for a in instance.atendentes.all()])
                if instance.atendentes.count()
                else ""
            ),
            terceiro_interno=list(
                instance.terceiro_interno.values_list("pk", flat=True)
            ),
            solicitante_aguardando_avaliacao=instance.cfg_email_solicitante.aguardando_avaliacao,
            solicitante_transferido_atendente=instance.cfg_email_solicitante.transferido_atendente,
            solicitante_garantia=instance.cfg_email_solicitante.garantia,
            solicitante_terceirizada=instance.cfg_email_solicitante.terceirizada,
            solicitante_viagem=instance.cfg_email_solicitante.viagem,
            atendente_transferido_atendente=instance.cfg_email_atendente.transferido_atendente,
            atendente_apos_avaliacao=instance.cfg_email_atendente.apos_avaliacao,
            reincidencia=instance.reincidencia.pk if instance.reincidencia else None,
            reincidencia_confirm_atendente=(
                instance.reincidencia.confirm_atendente
                if instance.reincidencia
                else None
            ),
            reincidencia_parecer=(
                instance.reincidencia.parecer if instance.reincidencia else None
            ),
            chamado_anterior=(
                instance.chamado_anterior.cache_numero
                if instance.chamado_anterior
                else None
            ),
            chamado_anterior_numero=(
                instance.chamado_anterior.cache_numero
                if instance.chamado_anterior is not None
                else None
            ),
            chamado_anterior_atendente=(
                ", ".join(
                    [
                        a.usuario.username
                        for a in instance.chamado_anterior.atendentes.all()
                    ]
                )
                if instance.chamado_anterior
                else None
            ),
            chamado_anterior_problema=(
                instance.chamado_anterior.solicitacao.descricao_problema
                if instance.chamado_anterior
                else None
            ),
            chamado_anterior_relatorio=(
                instance.chamado_anterior.relatorio
                if instance.chamado_anterior
                else None
            ),
            chamado_anterior_pk=(
                instance.chamado_anterior.pk if instance.chamado_anterior else None
            ),
            nao_institucional=instance.nao_institucional,
            relatorio=instance.relatorio,
            relatorio_display=clear_bug_fix_ext_editor(
                instance.relatorio.replace("<p>", "").replace("</p>", "")
                if instance.relatorio
                else ""
            ),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuChamado, self).get_params(*args, **kargs)
        if "cancelado" in params:
            if params.get("cancelado") == "off":
                del params["cancelado"]

            if params.get("cancelado") == "true":
                if params.get("motivo_cancelado", "") == "":
                    raise Exception("Informe o motivo do cancelamento.")
                params.update(cancelado=True)

        if "solicitacao" in params:
            del params["solicitacao"]

        if "avaliacao" in params:
            del params["avaliacao"]

        if "servico" in params:
            try:
                params.update(servico=Servico.objects.get(pk=params.get("servico", 0)))
            except Servico.DoesNotExist as e:
                log.exception(e)
                raise Exception("Serviço inexistente")

        if "atendentes" in params:
            atendentes = params.get("atendentes", [])
            if atendentes == "":
                atendentes = []
                params.update(data_fila_atendimento=None)
            else:
                params.update(data_fila_atendimento=datetime.now(), fila=None)
                if not isinstance(atendentes, (list, tuple)):
                    atendentes = [atendentes]
            params.update(
                atendentes=[Atendente.objects.get(pk=i) for i in atendentes],
            )
        if "cfg_email_solicitante" in params:
            params.update(
                cfg_email_solicitante=ConfigEmailSolicitante.objects.get_or_create(
                    aguardando_avaliacao=params.get(
                        "solicitante_aguardando_avaliacao", False
                    ),
                    transferido_atendente=params.get(
                        "solicitante_transferido_atendente", False
                    ),
                    garantia=params.get("solicitante_garantia", False),
                    terceirizada=params.get("solicitante_terceirizada", False),
                    viagem=params.get("solicitante_viagem", False),
                )[0]
            )
        if "cfg_email_atendente" in params:
            params.update(
                cfg_email_atendente=ConfigEmailAtendente.objects.get_or_create(
                    transferido_atendente=params.get(
                        "atendente_transferido_atendente", False
                    ),
                    apos_avaliacao=params.get("atendente_apos_avaliacao", False),
                )[0]
            )

        if "chamado_anterior" in params:
            params.update(
                chamado_anterior=Chamado.objects.get(
                    pk=params.get("chamado_anterior", 0)
                )
            )

        if "terceiro_interno" in params:
            terceiros = params.get("terceiro_interno", [])
            if not isinstance(terceiros, (list, tuple)):
                if terceiros == "":
                    terceiros = []
                else:
                    terceiros = [terceiros]
            params.update(
                terceiro_interno=[TerceiroInterno.objects.get(pk=i) for i in terceiros],
            )

        if "urgente" in params:
            log.info(params.get("urgente"))
            if params.get("motivo_urgencia", "") == "":
                raise Exception("Favor informar um motivo")
            if params.get("urgente") == "false":
                params.update(urgente=False)
            elif params.get("urgente") == "true":
                params.update(urgente=True)

        if "itens_base_conhecimento" in params:
            itens = params.get("itens_base_conhecimento", [])
            if not isinstance(itens, (list, tuple)):
                itens = [itens]
            params.update(
                itens_base_conhecimento=[
                    BaseConhecimento.objects.get(pk=i) for i in itens
                ],
            )
        if "nao_institucional" in params:
            if params.get("nao_institucional", "") == "true":
                params.update(nao_institucional=True)
            else:
                params.update(nao_institucional=False)
        if "relatorio" in params:
            if params.get("relatorio", "") == "":
                raise Exception("Preencha o relatório antes de salvar.")

        log.debug(params)
        return params

    def get_query(self):
        query = super(self.__class__, self).get_query()

        if self.request.user.has_perm("siatu.admin") is False:
            gerente = Gerente.objects.filter(usuario=self.request.user)
            atendente = Atendente.objects.filter(usuario=self.request.user)

            if self.request.user.has_perm("siatu.gerente") is True:
                servicos = (
                    [s.pk for s in gerente[0].lista_total_servicos()]
                    if gerente.exists()
                    else []
                )
                qst = Q(
                    Q(servico__in=servicos)
                    | Q(solicitacao__solicitante=self.request.user)
                )
                if atendente.exists():
                    atendente = atendente[0]
                    qst = Q(qst | Q(atendentes=atendente))

                return query.filter(qst)

            if self.request.user.has_perm("siatu.atendente") is True:
                qst = Q(solicitacao__solicitante=self.request.user)
                if atendente.exists():
                    atendente = atendente[0]
                    return query.filter(qst | Q(atendentes=atendente))

            # Permissão Básico - Não é admin, gerente ou atendente
            query = query.all()
            # query = query.filter(solicitacao__solicitante=self.request.user)

        return query

    def nao_urgente(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            self.log.info(self.request.POST)
            user = self.request.user.servidor
            self.log.info(user)
            for chamado in self._model.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            ):
                chamado.nao_urgente = True
                chamado.nao_urgente_por = user
                chamado.save()

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def history(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            self.log.info(self.request.POST)
            today = datetime.now()
            meses = {
                1: "Janeiro",
                2: "Fevereiro",
                3: "Março",
                4: "Abril",
                5: "Maio",
                6: "Junho",
                7: "Julho",
                8: "Agosto",
                9: "Setembro",
                10: "Outubro",
                11: "Novembro",
                12: "Dezembro",
            }

            today1 = today - relativedelta(months=6)
            today2 = today - relativedelta(months=5)
            today3 = today - relativedelta(months=4)
            today4 = today - relativedelta(months=3)
            today5 = today - relativedelta(months=2)
            today6 = today - relativedelta(months=1)

            qtd_chamado_mes1 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today1.year,
                data_inicio__month=today1.month,
            ).count()

            qtd_chamado_mes2 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today2.year,
                data_inicio__month=today2.month,
            ).count()

            qtd_chamado_mes3 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today3.year,
                data_inicio__month=today3.month,
            ).count()

            qtd_chamado_mes4 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today4.year,
                data_inicio__month=today4.month,
            ).count()

            qtd_chamado_mes5 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today5.year,
                data_inicio__month=today5.month,
            ).count()

            qtd_chamado_mes6 = Status.objects.filter(
                chamado__servico__in=[self.request.POST.get("servico")],
                status__in=[1],
                data_inicio__year=today6.year,
                data_inicio__month=today6.month,
            ).count()

            dados = (
                "%s &nbsp; &nbsp; em %s de %s <br> %s\
                &nbsp; &nbsp; em %s de %s <br> %s\
                &nbsp; &nbsp; em %s de %s <br> %s\
                &nbsp; &nbsp; em %s de %s <br> %s\
                &nbsp; &nbsp; em %s de %s <br> %s\
                &nbsp; &nbsp; em %s de %s"
                % (
                    qtd_chamado_mes1,
                    meses.get(today1.month),
                    today1.year,
                    qtd_chamado_mes2,
                    meses.get(today2.month),
                    today2.year,
                    qtd_chamado_mes3,
                    meses.get(today3.month),
                    today3.year,
                    qtd_chamado_mes4,
                    meses.get(today4.month),
                    today4.year,
                    qtd_chamado_mes5,
                    meses.get(today5.month),
                    today5.year,
                    qtd_chamado_mes6,
                    meses.get(today6.month),
                    today6.year,
                )
            )

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True, message="Dados persistidos com sucesso!", total=dados
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.chamado.Manager", {concluido: %d, all_status: %s})'
            % (Status.CONCLUIDO, Status.get_all_status())
        )

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "document": {
                "content": "Somente um teste",
            },
        }

        try:
            log.info(args[0])
            chamado = self._model.objects.get(pk=args[0])
            rst.update(
                success=True,
                document={
                    # 'content': chamado.rend,
                    "content": chamado.render_process,
                },
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não foi possível encontrar o documento. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def renderer_document_to_print(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            protocol = (
                self.get_query()
                .filter(movimentacoes=self.request.GET.get("movement"))
                .first()
            )
        except Protocolo.DoesNotExist:
            rst.update(
                message="Este doumento não existe ou nunca foi compartilhado com você."
            )
            self.response.write(
                loader.get_template("chamado/print/base.html").render(rst)
            )
        except Exception:
            self.response.write("<h1>Not found</h1>")
        else:
            if protocol:
                tpl = loader.get_template("chamado/print/base.html")
                movement = protocol.movimentacoes.filter(
                    pk=self.request.GET.get("movement")
                ).first()
                if not movement.is_received:
                    self.response.write(
                        tpl.render(
                            {
                                "document": loader.get_template(
                                    "chamado/not-preview.html"
                                ).render({"protocol": protocol, "movement": movement}),
                                "appends": [],
                            }
                        )
                    )
                else:
                    self.response.write(
                        tpl.render(
                            {
                                "document": protocol.rendered,
                                "appends": protocol.appends_of_document,
                            }
                        )
                    )
            else:
                self.response.write("<h1>Not found</h1>")


class SiatuChamadoSolicitante(Restful):

    def qtde_chamados_avaliar(self):
        chamados = Chamado.objects.filter(
            solicitacao__solicitante=self.request.user,
            status_atual__status=Status.AGUARDANDO_AVALIACAO,
        )

        return chamados.count()

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.chamado.ManagerSolicitante",'
            " {solicitante: %d, aguardando_avaliacao: %d, qtde_chamados_avaliar: %d, concluido: %d})"
            % (
                self.request.user.pk,
                Status.AGUARDANDO_AVALIACAO,
                self.qtde_chamados_avaliar(),
                Status.CONCLUIDO,
            )
        )


class SiatuChamadoAtendente(Restful):

    def get_atendente(self):
        filtro = Atendente.objects.filter(usuario=self.request.user)
        atendente = filtro[0].pk if len(filtro) > 0 else 0
        return atendente

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.chamado.ManagerAtendente", {atendente: %d, concluido: %d})'
            % (self.get_atendente(), Status.CONCLUIDO)
        )


class SiatuChamadoGerente(Restful):

    def get_gerente(self):
        filtro = Gerente.objects.filter(usuario=self.request.user)
        gerente = filtro[0] if len(filtro) > 0 else 0
        return gerente

    def get_listServicosGerente(self):
        gerente = self.get_gerente()
        if gerente == 0:
            return []
        lista = [s.pk for s in gerente.lista_total_servicos()]

        return lista

    def get_list_all_service(self):
        lista = [s.pk for s in Servico.objects.all().order_by("id")]

        return lista

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.chamado.ManagerGerente",'
            " {lista_servicos: %s, lista_todos_servicos: %s, concluido: %d, all_status: %s})"
            % (
                self.get_listServicosGerente(),
                self.get_list_all_service(),
                Status.CONCLUIDO,
                Status.get_all_status(),
            )
        )


class SiatuAnexo(Restful):

    _model = Anexo

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            chamado=instance.chamado.pk,
            arquivo=instance.arquivo.pk,
            usuario=instance.arquivo.user.username,
            filename=instance.arquivo.filename,
            permalink=(
                instance.arquivo.permalink() if instance.arquivo is not None else None
            ),
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuAnexo, self).get_params(*args, **kargs)

        if "chamado" in params:
            params.update(chamado=Chamado.objects.get(pk=params.get("chamado", 0)))

        if "arquivo" in params:
            if params.get("arquivo", "") == "":
                raise Exception("Favor informar um arquivo")
            params.update(arquivo=Arquivo.objects.get(pk=params.get("arquivo", 0)))
        return params


class SiatuTransferencia(Restful):

    _model = Transferencia

    force_upper = False

    full_text_index = ()

    def fill_instance_m2m(self, instance, values):
        fields = [f.name for f in instance._meta.many_to_many]

        for key, value in list(values.items()):
            field = getattr(instance, key, None)
            if key in fields and isinstance(value, (tuple, list, set)):
                field.clear()
                for item in value:
                    field.add(item)

        if (instance.aceito_por is not None) and (instance.cancelado is False):
            c = instance.chamado
            c.data_fila_atendimento = datetime.now()
            c.fila = None
            c.save()
            s = Status(
                status=Status.TRANSFERIDO_ATENDENTE,
                data_inicio=datetime.now(),
                chamado=c,
                motivo=instance.motivo,
            )
            s.save()
            s = Status(
                status=Status.AGUARDANDO_ATENDIMENTO,
                data_inicio=datetime.now(),
                chamado=c,
            )
            s.save()
            c.atendentes.clear()
            for item in instance.atendente_posterior.all():
                c.atendentes.add(item)

            # Enviar notificação para atendentes novos
            at_novos = instance.atendente_posterior.exclude(
                pk__in=instance.atendente_anterior.values_list("pk", flat=True)
            )
            log.info("Enviando email para atendentes - recebimento de chamado")
            try:
                for atendente_novo in at_novos:
                    if atendente_novo.notificacao_receber_chamado is True:
                        msg = Message.objects.get(mid="siatu-atendente-recebe")
                        servidor_atendente = employee_from_user(atendente_novo.usuario)
                        Notification.notify(
                            msg,
                            servidor_atendente,
                            types=["SYS", "EMAIL"],
                            chamado=instance.chamado.cache_numero,
                        )
                        log.info("Email enviado com sucesso")
                    else:
                        log.info("Envio de email desativado")
            except Exception as e:
                log.info("Email não enviado")
                log.exception(e)
            # Fim envio notificação para atendentes novos
        else:
            if values.get("resposta", "") == "":
                try:
                    log.debug(
                        "Enviando email para atendente - notificar pedido de transferencia"
                    )
                    atendente = instance.atendente_posterior.exclude(
                        pk__in=[a.pk for a in instance.atendente_anterior.all()]
                    )[0]
                    atendente_servidor = employee_from_user(atendente.usuario)
                    msg = Message.objects.get(mid="siatu-pedido-transferencia")
                    Notification.notify(
                        msg,
                        atendente_servidor,
                        chamado=instance.chamado.cache_numero,
                        atendente=instance.pedido_por.username,
                    )
                    log.info("Email enviado com sucesso")
                except Exception as e:
                    log.info("Email não enviado")
                    log.exception(e)

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            atendente_anterior=list(
                instance.atendente_anterior.values_list("pk", flat=True)
            ),
            atendente_posterior=list(
                instance.atendente_posterior.values_list("pk", flat=True)
            ),
            motivo=instance.motivo,
            pedido_por=instance.pedido_por.username,
            aceito_por=(
                instance.aceito_por.username
                if instance.aceito_por is not None
                else None
            ),
            data_pedido=DateUtils.datetime_to_str(instance.data_pedido),
            data_aceite=(
                DateUtils.datetime_to_str(instance.data_aceite)
                if instance.data_aceite is not None
                else None
            ),
            chamado=instance.chamado.pk,
            cancelado=instance.cancelado,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuTransferencia, self).get_params(*args, **kargs)
        for k in list(params.keys()):
            if k.startswith("ext-comp"):
                del params[k]

        if "chamado" in params:
            params.update(chamado=Chamado.objects.get(pk=params.get("chamado", 0)))
            status = params.get("chamado").status_atual.status
            if status != Status.VIAGEM:
                if status != Status.GARANTIA and status != Status.TERCEIRIZADA:
                    if (
                        status != Status.EM_ATENDIMENTO
                        and status != Status.AGUARDANDO_ATENDIMENTO
                    ):
                        if (
                            status != Status.AGUARDANDO_ENTREGA
                            and status != Status.MANUTENCAO
                        ):
                            raise Exception(
                                "O status atual do chamado não permite transferí-lo"
                            )

        if "insert" in params:
            del params["insert"]
            if "atendente_posterior" not in params:
                raise Exception("Não houve modificações")
            if params.get("atendente_posterior", "") == "":
                raise Exception("Favor informar um atendente")
            if params.get("motivo", "") == "":
                raise Exception("Favor informar um motivo")

            params.update(
                pedido_por=self.request.user,
                data_pedido=datetime.now(),
                atendente_anterior=list(params.get("chamado").atendentes.all()),
            )
            if "super_user" in params:
                # usuario logado eh gerente ou admin
                params.update(
                    aceito_por=self.request.user,
                    data_aceite=datetime.now(),
                )
                if "atendente_posterior" in params:
                    atendentes = params.get("atendente_posterior", [])
                    if not isinstance(atendentes, (list, tuple)):
                        atendentes = [atendentes]
                    params.update(
                        atendente_posterior=[
                            Atendente.objects.get(pk=i) for i in atendentes
                        ],
                    )
            else:
                # usuario logado eh atendente do chamado
                if "atendente_posterior" in params:
                    lista_atendente = list(params.get("chamado").atendentes.all())
                    posterior = Atendente.objects.get(
                        pk=params.get("atendente_posterior", 0)
                    )
                    if posterior in lista_atendente:
                        raise Exception("Atendente já está associado ao chamado")

                    lista_atendente.remove(
                        Atendente.objects.get(usuario=self.request.user)
                    )
                    lista_atendente.append(posterior)
                    params.update(
                        atendente_posterior=lista_atendente,
                    )
            # Cancelando transferencia anterior pendente se houver
            chamado = params.get("chamado", "")
            if chamado != "":
                lista = chamado.transferencias.filter(
                    aceito_por__isnull=True, cancelado=False
                )
                for t in lista:
                    t.cancelado = True
                    t.save()

        if "resposta" in params:
            if params.get("resposta", "") == "Yes":
                params.update(
                    aceito_por=self.request.user,
                    data_aceite=datetime.now(),
                )
            else:
                params.update(cancelado=True)

        log.debug(params)
        return params


class SiatuStatus(Restful):

    _model = Status

    force_upper = False

    full_text_index = ()

    def model_to_dict(self, instance):
        _dict_ = Restful.model_to_dict(self, instance)
        _dict_.update(
            status=instance.status,
            icon=instance.icon,
            status_display=instance.get_status_display(),
            data_inicio=DateUtils.datetime_to_str(instance.data_inicio),
            previsao_fim=(
                DateUtils.date_to_str(instance.previsao_fim)
                if instance.previsao_fim is not None
                else None
            ),
            chamado=instance.chamado.pk,
            terceirizada=(
                instance.terceirizada.pk if instance.terceirizada is not None else None
            ),
            terceirizada_string=(
                instance.terceirizada.nome
                if instance.terceirizada is not None
                else None
            ),
            motivo=instance.motivo,
        )
        return _dict_

    def get_params(self, *args, **kargs):
        params = super(SiatuStatus, self).get_params(*args, **kargs)
        if "insert" in params:
            del params["insert"]
            params.update(data_inicio=datetime.now())
        if "chamado" in params:
            try:
                params.update(chamado=Chamado.objects.get(pk=params.get("chamado", 0)))
            except Exception:
                raise Exception("Parâmetro chamado não encontrado")

        if "status" in params:
            if params.get("status", "") == "":
                raise Exception("Favor informar um status")
            if int(params.get("status", "")) == Status.AGUARDANDO_AVALIACAO:
                # if(params.get('chamado').base_conhecimento.count() == 0):
                #     raise Exception(u'Favor associar pelo menos um item da base de conhecimento ao chamado')
                if params.get("chamado").reincidencia:
                    if (
                        not params.get("chamado").reincidencia.confirm_atendente
                        and params.get("chamado").reincidencia.parecer is None
                    ):
                        log.warn("Falta parecer do gerente sobre reincidência")
                        raise Exception("Falta parecer do gerente sobre reincidência!")

        if "terceirizada" in params:
            if params.get("terceirizada", "") == "":
                raise Exception("Favor informar uma terceirizada")
            params.update(
                terceirizada=Terceirizada.objects.get(pk=params.get("terceirizada", 0))
            )

        if "previsao_fim" in params:
            if params.get("previsao_fim", "") == "":
                if int(params.get("status")) == Status.TERCEIRIZADA:
                    raise Exception("Favor informar uma previsão")
                if int(params.get("status")) == Status.GARANTIA:
                    raise Exception("Favor informar uma previsão")
                if int(params.get("status")) == Status.VIAGEM:
                    raise Exception("Favor informar uma previsão")

                params.update(previsao_fim=None)
            else:
                previsao = DateUtils.str_to_date(params.get("previsao_fim"))
                if previsao < datetime.now().date():
                    raise Exception("Informe uma previsão válida")
                params.update(previsao_fim=previsao)

        return params


class SiatuConfiguracao(DefaultController):
    def eval_value(self, value):
        if re.match(r"^\[.*\]$", value):
            return eval(value)
        else:
            return value

    def read(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("siatu")
            log.info(cfg)
            rst.update(
                config={
                    item.key: self.eval_value(item.value) for item in cfg.items.all()
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def write(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        cfg = Configuration.get_or_create("siatu")

        cfg.set(self.request.POST.get("property"), self.request.POST.get("value"))

        self.response.write(json.dumps(rst))

    def save(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}
        try:
            cfg = Configuration.get_or_create("siatu")
            for attr in self.request.POST:
                cfg.set(attr, self.request.POST.get(attr))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True)

        self.response.write(json.dumps(rst))

    def json(self, args=[]):
        self.response.write('Ext._create("common.siatu.ConfigurationManage")')


def get_choice_standard(ch):
    choice = list(ch)
    choice.insert(0, ("0", "TODOS"))
    return choice


class SiatuReportQtdAtendimento(extjs.ExtReportBuild):

    report_src = "/to/mpe/common/siatu/atendimentos_qtde/main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/common/siatu/atendimentos_qtde/",
        }
    ]

    titles = {"TITLE": "Relatórios", "SUB_TITLE": "Relatório Quantidade Atendimentos"}

    class Form(forms.Form):
        data_inicial = forms.DateField(
            label="Data Inicial",
        )
        data_final = forms.DateField(
            label="Data Final",
        )
        servico = forms.ChoiceField(
            label="Tipo de Serviço", choices=SERVICO_CHOICES, required=False
        )

    def get_generated_filename(self):
        dic = dict(SERVICO_CHOICES)
        report = (
            "relatorio-qtd-atendimentos-%s.pdf"
            % dic.get(int(self.request.GET["servico"]))
            if self.request.GET["servico"]
            else "relatorio-qtd-atendimentos.pdf"
        )
        report = report.encode("utf-8")
        return report


class SiatuReportConsolidadoPeriodo(extjs.ExtReportBuild):

    report_src = "/to/mpe/common/siatu/atendentes_consolidado/graficos/siatu_main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/common/siatu/atendentes_consolidado/graficos/",
        }
    ]

    titles = {
        "TITLE": "Relatórios",
        "SUB_TITLE": "Relatório de Atendentes Consolidado por Período",
    }

    class Form(forms.Form):
        servico = forms.ChoiceField(
            label="Tipo de Serviço",
            choices=get_choice_standard(SERVICO_CHOICES),
            required=False,
        )
        ano = forms.CharField(
            label="Ano",
        )

    def get_generated_filename(self):
        report = "relatorio-atendimentos-consolidado.pdf"
        report = report.encode("utf-8")
        return report


class SiatuReportAttendanceDescription(DefaultController):
    """
    Construção da tela de geração do relatório
    Relatório Atendimentos Descrição.
    """

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.reports.AttendanceDescriptionManager")'
        )


class SiatuReportNumberOfAttendancesPerAttendant(DefaultController):
    """
    Construção da tela de geração do relatório
    Relatório Quantidade de Atendimentos Por Atendentes.
    """

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.reports.NumberOfAttendancesPerAttendantManager")'
        )


class SiatuReportAttendanceAvaliationConcept(DefaultController):
    """
    Construção da tela de geração do relatório
    Relatório Conceitos de Avaliações de Atendimentos.
    """

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.reports.AttendanceAvaliationConceptManager")'
        )


class SiatuReportAttendanceAvaliationGraphics(DefaultController):
    """
    Construção da tela de geração do relatório
    Relatório Gráficos de Avaliações de Atendimentos.
    """

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.siatu.reports.AttendanceAvaliationGraphicsManager")'
        )
