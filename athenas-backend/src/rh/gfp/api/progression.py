# -*- coding: utf-8 -*-

import datetime

from contrib.daterange import NewDateRange
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger

from rh.gfp.models import (
    ExtensionSalaryProgression,
    MovimentacaoProgressao as SalaryProgression,
    ProgressionDocument,
    HorizontalProgressionConfig,
)
from rh.models import Publicacao as Publication
from rh.pvf.models import PortalRequestProgression, PortalRequestProgressionH

from rh.pvf.const import (
    STS_REJECTED,
    STS_EFFECTIVE,
    STS_CANCELED_DGP,
    STS_CANCELED_APPLICANT,
)

# from dateutil.relativedelta import relativedelta


log = getLogger(__name__)


class GFPManagerProgression(RestfulDRY):

    _model = SalaryProgression

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
    )

    exclude_fields = [
        "modified_by",
        "created_by",
        "created_at",
        "modified_at",
        "movimentacaopessoal_ptr",
    ]

    def extend(self, args=[]):
        rst = {"success": False, "message": "", "extended": []}

        progressions = self._model.objects.filter(
            pk__in=self.request.POST.getlist("progression")
        )
        date_new = self.request.POST.get("date_new", None)
        date_reference = self.request.POST.get("date_reference", None)
        for prog in progressions:
            try:
                if self.get_request_progress_h(prog):
                    raise Exception(
                        "Existe uma solicitação de Progressão Horizontal em andamento."
                    )
                motivo = self.request.POST.get("motivo")
                prog.extend(motivo, date_new, date_reference)
            except Exception as e:
                rst["success"] = False
                rst["message"] += "%s<br>" % e

        rst["success"] = False if rst["message"] else True

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def forward(self, args=[]):
        rst = {"success": False, "message": "", "errors": []}

        prog = self._model.objects.get(pk__in=self.request.POST.getlist("progression"))
        publication = Publication.objects.get(pk=self.request.POST.get("publication"))

        try:
            if self.get_request_progress_h(prog):
                raise Exception(
                    "Existe uma solicitação de Progressão Horizontal em andamento."
                )
            if (
                prog.portal_request_progression.exists()
                and prog.portal_request_progression.last().status == 4
            ):
                prog.forward(publication)
            else:
                if (
                    prog.portal_request_progression.exists()
                    and prog.portal_request_progression.last().status == 4
                ):
                    prog.forward(publication)
                else:
                    raise Exception(
                        f"Progressão: {prog} - {prog.servidor} não possui Solicitação de Progressão Efetivada no VDF."
                    )
        except Exception as e:
            rst["success"] = False
            rst["message"] += "%s<br>" % e

        rst["success"] = False if rst["message"] else True

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_request_progress_h(self, prog):
        return (
            PortalRequestProgressionH.objects.filter(
                employee=prog.servidor,
            )
            .exclude(
                status__in=[
                    STS_REJECTED,
                    STS_EFFECTIVE,
                    STS_CANCELED_DGP,
                    STS_CANCELED_APPLICANT,
                ]
            )
            .exists()
        )

    def request_progression(self, args=[]):
        rst = {"success": False, "message": "", "errors": []}

        progressions = self._model.objects.filter(
            pk__in=self.request.POST.getlist("progression")
        )

        try:
            for prog in progressions:
                if not prog.portal_request_progression.exists():
                    if self.get_request_progress_h(prog):
                        raise Exception(
                            "Existe uma solicitação de Progressão Horizontal em andamento."
                        )
                    PortalRequestProgression.create(prog)
                elif (
                    prog.portal_request_progression.last().status == 9
                    and prog.portal_request_progression.last().step_current == 8
                ):
                    prp = prog.portal_request_progression.last()
                    prp.resend_request(prog)
                else:
                    raise Exception(
                        "Só é possível reenviar a solicitação quando algum Aprovador a Devolve ao Solicitante."
                    )
            rst["success"] = True
            rst["message"] = "Solicitação criada com sucesso."
        except Exception as e:
            rst["success"] = False
            rst["message"] += "%s<br>" % e

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_icons(self, instance):
        date_status = {"iconCls": "icon-fopag icon-status-away", "title": "Liberada"}
        requirements_status = {
            "iconCls": "icon-fopag icon-exclamation-circle",
            "title": "Requisitos em avaliação",
        }
        stability_status = {
            "iconCls": "icon-fopag icon-user-active",
            "title": "Servidor estável",
        }
        step_current_p_v = {"iconCls": "", "title": ""}
        step_current_p_h = {"iconCls": "", "title": ""}

        cute_range = NewDateRange.from_month(
            datetime.datetime.now().year, datetime.datetime.now().month
        )

        if not instance.expected_date:
            date_status = {
                "iconCls": "icon-fopag icon-status-block",
                "title": "Bloqueada",
            }
        elif instance.expected_date < cute_range.first:
            date_status = {
                "iconCls": "icon-fopag icon-status-busy",
                "title": "Atrasada",
            }
        elif instance.expected_date > cute_range.last:
            date_status = {
                "iconCls": "icon-fopag icon-status-offline",
                "title": "Aguardando...",
            }

        if instance.requirements["unfit"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-red",
                "title": "<br>".join(instance.requirements["unfit"]),
            }
        elif instance.requirements["block"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-black",
                "title": "<br>".join(instance.requirements["block"]),
            }
        elif instance.requirements["wait"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-circle",
                "title": "<br>".join(instance.requirements["block"]),
            }
        else:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-green",
                "title": "Requisitos satisfeitos",
            }

        if instance.referencia_nivel2d.ordem == 1:
            stability_status = {
                "iconCls": "icon-fopag icon-user-silhouette",
                "title": "Servidor em estágio",
            }

        if instance.portal_request_progression.last():
            if (
                instance.portal_request_progression.last().status == 5
                or instance.portal_request_progression.last().status == 7
            ):
                step_current_p_v = {"iconCls": "", "title": ""}
            elif instance.portal_request_progression.last().status == 4:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-forward-progression",
                    "title": "V - Efetivado",
                }
            elif (
                instance.portal_request_progression.last().status == 9
                and instance.portal_request_progression.last().step_current == 8
            ):
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-timer",
                    "title": "V - Aguardando Envio",
                }
            elif instance.portal_request_progression.last().step_current == 10:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-not-stable-employee",
                    "title": "V - Aguardando Aprovação: Assessoria Jurídica (1º)",
                }
            elif instance.portal_request_progression.last().step_current == 11:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-user-detective",
                    "title": "V - Aguardando Aprovação: Diretor Geral",
                }
            elif instance.portal_request_progression.last().step_current == 12:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-stabilization",
                    "title": "V - Aguardando Aprovação: Assessoria Jurídica (2º)",
                }

        if instance.portal_request_progression_h.last():
            if (
                instance.portal_request_progression_h.last().status == 5
                or instance.portal_request_progression_h.last().status == 7
            ):
                step_current_p_h = {"iconCls": "", "title": ""}
            elif instance.portal_request_progression_h.last().status == 4:
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-user-timer",
                    "title": "H - Efetivado",
                }
            elif (
                instance.portal_request_progression_h.last().status == 9
                and instance.portal_request_progression_h.last().step_current == 8
            ):
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-user-timer",
                    "title": "H - Aguardando Envio",
                }
            elif instance.portal_request_progression_h.last().step_current == 13:
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-user-timer",
                    "title": "H - Aguardando Efetivação: Gerência de Desenvolvimento",
                }

        return [
            date_status,
            requirements_status,
            stability_status,
            step_current_p_v,
            step_current_p_h,
        ]

    def get_query(self):
        query = (
            self._model.objects.filter(
                data_fim_vigencia=None,
                # servidor__tipo='S',
                servidor__ativo=True,
                expected_date__isnull=False,
                ativo=True,
            )
            .exclude(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="CM")
            .order_by("expected_date", "movimentacao_posse__servidor")
        )
        filtered = (x.pk for x in query if x.next_type_progression != "V")
        return query.filter(pk__in=filtered)

    def model_to_dict(self, instance):
        _dict = super(GFPManagerProgression, self).model_to_dict(instance)
        _dict.update(
            {
                "icons": self.get_icons(instance),
                "extends": ExtensionSalaryProgression.objects.filter(
                    progression__servidor=instance.servidor,
                    progression__referencia_nivel2d=instance.referencia_nivel2d,
                ).count(),
                "next_reference": "%s" % instance.next_reference,
            }
        )
        return _dict

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.progression.SalaryProgressionManage")')


class GFPStabilizationManager(RestfulDRY):

    _model = SalaryProgression
    exclude_fields = [
        "modified_by",
        "created_by",
        "created_at",
        "modified_at",
        "movimentacaopessoal_ptr",
    ]

    def get_query(self):
        return self._model.objects.filter(
            data_fim_vigencia=None, progressao_anterior=None, servidor__tipo="S"
        ).order_by("-data_referencia")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.progression.SalaryProgressionManage")')


class GFPProgressionDocument(RestfulDRY):

    _model = ProgressionDocument

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.progression.document.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            custom_approver_current=instance.get_doc_origin_display(
                instance.doc_origin
            ),
        )

        return rst


class GFPHorizontalProgConfig(RestfulDRY):

    _model = HorizontalProgressionConfig

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.progression.horizontal_config.Manage")'
        )


class GFPHorizontalProgressionSolicitation(RestfulDRY):

    _model = SalaryProgression

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
    )

    exclude_fields = [
        "modified_by",
        "created_by",
        "created_at",
        "modified_at",
        "movimentacaopessoal_ptr",
    ]

    def get_icons(self, instance):
        date_status = {"iconCls": "icon-fopag icon-status-away", "title": "Liberada"}
        requirements_status = {
            "iconCls": "icon-fopag icon-exclamation-circle",
            "title": "Requisitos em avaliação",
        }
        stability_status = {
            "iconCls": "icon-fopag icon-user-active",
            "title": "Servidor estável",
        }
        step_current_p_v = {"iconCls": "", "title": ""}
        step_current_p_h = {"iconCls": "", "title": ""}

        cute_range = NewDateRange.from_month(
            datetime.datetime.now().year, datetime.datetime.now().month
        )

        if not instance.expected_date:
            date_status = {
                "iconCls": "icon-fopag icon-status-block",
                "title": "Bloqueada",
            }
        elif instance.expected_date < cute_range.first:
            date_status = {
                "iconCls": "icon-fopag icon-status-busy",
                "title": "Atrasada",
            }
        elif instance.expected_date > cute_range.last:
            date_status = {
                "iconCls": "icon-fopag icon-status-offline",
                "title": "Aguardando...",
            }

        if instance.requirements["unfit"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-red",
                "title": "<br>".join(instance.requirements["unfit"]),
            }
        elif instance.requirements["block"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-black",
                "title": "<br>".join(instance.requirements["block"]),
            }
        elif instance.requirements["wait"]:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-circle",
                "title": "<br>".join(instance.requirements["block"]),
            }
        else:
            requirements_status = {
                "iconCls": "icon-fopag icon-exclamation-green",
                "title": "Requisitos satisfeitos",
            }

        if instance.referencia_nivel2d.ordem == 1:
            stability_status = {
                "iconCls": "icon-fopag icon-user-silhouette",
                "title": "Servidor em estágio",
            }

        if instance.portal_request_progression.first():
            if (
                instance.portal_request_progression.last().status == 5
                or instance.portal_request_progression.last().status == 7
            ):
                step_current_p_v = {"iconCls": "", "title": ""}
            elif instance.portal_request_progression.first().status == 4:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-forward-progression",
                    "title": "V - Efetivado",
                }
            elif (
                instance.portal_request_progression.first().status == 9
                and instance.portal_request_progression.first().step_current == 8
            ):
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-timer",
                    "title": "V - Aguardando Envio",
                }
            elif instance.portal_request_progression.first().step_current == 10:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-not-stable-employee",
                    "title": "V - Aguardando Aprovação: Assessoria Jurídica (1º)",
                }
            elif instance.portal_request_progression.first().step_current == 11:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-user-detective",
                    "title": "V - Aguardando Aprovação: Diretor Geral",
                }
            elif instance.portal_request_progression.first().step_current == 12:
                step_current_p_v = {
                    "iconCls": "icon-fopag icon-stabilization",
                    "title": "V - Aguardando Aprovação: Assessoria Jurídica (2º)",
                }

        if instance.portal_request_progression_h.first():
            if (
                instance.portal_request_progression_h.last().status == 5
                or instance.portal_request_progression_h.last().status == 7
            ):
                step_current_p_h = {"iconCls": "", "title": ""}
            elif instance.portal_request_progression_h.first().status == 4:
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-timer",
                    "title": "H - Efetivado",
                }
            elif (
                instance.portal_request_progression_h.first().status == 9
                and instance.portal_request_progression_h.first().step_current == 8
            ):
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-timer",
                    "title": "H - Aguardando Envio",
                }
            elif instance.portal_request_progression_h.first().step_current == 13:
                step_current_p_h = {
                    "iconCls": "icon-fopag icon-timer",
                    "title": "H - Aguardando Efetivação: Gerência de Desenvolvimento",
                }

        return [
            date_status,
            requirements_status,
            stability_status,
            step_current_p_v,
            step_current_p_h,
        ]

    def get_query(self):
        query = (
            self._model.objects.filter(
                data_fim_vigencia=None,
                servidor__ativo=True,
                expected_date__isnull=False,
                ativo=True,
            )
            .exclude(referencia_nivel2d__cargos_estrutura__cargo__tipo_lei_cargo="CM")
            .order_by("expected_date", "movimentacao_posse__servidor")
        )
        return query

    def model_to_dict(self, instance):
        _dict = super(GFPHorizontalProgressionSolicitation, self).model_to_dict(
            instance
        )
        _dict.update(
            {
                "icons": self.get_icons(instance),
                "extends": ExtensionSalaryProgression.objects.filter(
                    progression__servidor=instance.servidor,
                    progression__referencia_nivel2d=instance.referencia_nivel2d,
                ).count(),
                "next_reference": "%s" % instance.next_reference,
            }
        )
        return _dict

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.progression.horizontal_solicitation.Manage")'
        )
