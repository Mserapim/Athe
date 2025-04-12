# -*- coding: utf-8 -*-


import codecs
import hashlib
import os
import threading

from contrib import extjs
from contrib.controller import CommandController, ContentType, DefaultController
from contrib.decorator import deprecated, login_required
from contrib.middleware import get_current_user, set_current_user
from contrib.restful import Restful
from contrib.utils import DateUtils, get_json_engine, getLogger, int_to_roman
from dateutil import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.template.defaultfilters import slugify
from engine.api.controller import CommandControllerTaskViewer
from engine.mq.models import Task
from ged.models import Arquivo as File
from rh.gfp.dirf.models import Declaracao
from rh.gfp.models import (
    DadoBancarioServidorFolha,
    Evento,
    Folha,
    FolhaEvento,
    FolhaMensagem,
    FolhaModelo,
    FolhaTipo,
    Periodo,
)
from rh.gfp.previdencia.igeprev import IgeprevGenerator
from rh.gfp.previdencia.task.igeprev import generator as igeprev_generator
from rh.gfp.tasks import (
    process_copy_credit_accounts,
    process_load_file,
    process_recalculate_payroll,
)
from rh.models import (
    Cargo,
    PessoaFisica,
    PessoaJuridica,
    Servidor,
    UnidadeAdministrativa,
    Banco,
)
from standard.models import Choice, ClassCode, Configuration, RunCodeManager
from functools import partial

unlink = None

if getattr(settings, "DEBUG", False) is True:

    def void(path):
        pass

    unlink = void
else:
    from os import unlink

json = get_json_engine()
log = getLogger(__name__)


class CustomAutocomplete(extjs.ExtWidget):

    @login_required("JSON")
    def autocomplete(self, args=[]):
        obj = {"result": []}
        qs = []
        model = None

        if len(args) == 1:
            if args[0] == "Folha":
                months = []

                for month in Choice.get_choices_for("rh", "MONTHS"):
                    try:
                        month[1].lower().index(self.request.POST["query"].lower())
                        months.append(month[0])
                    except:
                        pass

                if len(args) == 2 and args[1] == "fechado":
                    qs.append(Q(fechado=True))
                    qs.append(Q(periodo__ano__icontains=self.request.POST["query"]))
                    qs.append(
                        Q(tipo_folha__titulo__icontains=self.request.POST["query"])
                    )
                    qs.append(Q(periodo__mes__in=months))
                else:
                    qs.append(Q(periodo__ano__icontains=self.request.POST["query"]))
                    qs.append(
                        Q(tipo_folha__titulo__icontains=self.request.POST["query"])
                    )
                    qs.append(Q(periodo__mes__in=months))
                model = Folha
            elif args[0] == "Servidor":
                qs.append(Q(pessoa_fisica__nome__icontains=self.request.POST["query"]))
                qs.append(Q(matricula__icontains=self.request.POST["query"]))
                model = Servidor
            elif args[0] == "Evento":
                qs.append(Q(numero__icontains=self.request.POST["query"]))
                qs.append(Q(titulo__icontains=self.request.POST["query"]))
                model = Evento
            elif args[0] == "Cargo":
                qs.append(Q(codigo__icontains=self.request.POST["query"]))
                qs.append(Q(descricao__icontains=self.request.POST["query"]))
                qs.append(Q(nome__icontains=self.request.POST["query"]))
                model = Cargo
            elif args[0] == "UnidadeAdministrativa":
                qs.append(Q(nome__icontains=self.request.POST["query"]))
                qs.append(
                    Q(pessoa_juridica__nome__icontains=self.request.POST["query"])
                )
                qs.append(
                    Q(pessoa_juridica__cnpj__icontains=self.request.POST["query"])
                )
                qs.append(
                    Q(
                        pessoa_juridica__razao_social__icontains=self.request.POST[
                            "query"
                        ]
                    )
                )
                model = UnidadeAdministrativa
            elif args[0] == "PessoaJuridica":
                qs.append(Q(nome__icontains=self.request.POST["query"]))
                qs.append(Q(cnpj__icontains=self.request.POST["query"]))
                qs.append(Q(razao_social__icontains=self.request.POST["query"]))
                model = PessoaJuridica
            elif args[0] == "Declaracao":
                qs.append(
                    Q(
                        demonstrativos__pessoa_fisica__nome__icontains=self.request.POST[
                            "query"
                        ]
                    )
                )
                qs.append(
                    Q(
                        demonstrativos__pessoa_fisica__cpf__icontains=self.request.POST[
                            "query"
                        ]
                    )
                )
                model = Declaracao

        if model is not None:
            q = None
            for qN in qs:
                q = qN if q is None else Q(q | qN)
            obj["result"] = [
                {"id": row.pk, "description": str(row)}
                for row in model.objects.filter(q)
            ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def check_permission(self, user, action, app_label, object_name):
        perm = "%(app_label)s.%(action)s_%(object_name)s" % vars()
        perm = perm.lower()

        log.info("check %s permission for %s" % (perm, user))
        if user.has_perm(perm) is True:
            log.info("user %s has permission %s" % (user, perm))
            return True
        else:
            log.warn("permission %s dained for %s" % (perm, user))
            return False


class GFPFolhaMensagemRestful(Restful):

    model = FolhaMensagem

    def to_dict(self, qdict):
        d = Restful.to_dict(self, qdict)

        if "servidor" in list(d.keys()):
            try:
                s = Servidor.objects.get(pk=self.request.POST.get("servidor"))
            except Exception as e:
                self.log.exception(e)
                s = None
            finally:
                d.update(servidor=s)

        if "folha" in list(d.keys()):
            try:
                f = Folha.objects.get(pk=self.request.POST.get("folha"))
            except Exception as e:
                self.log.exception(e)
                f = None
            finally:
                d.update(folha=f)

        return d


class GFPConfiguracao(CustomAutocomplete):

    cfg = None

    def commit(self, args=[]):
        obj = {"success": True, "message": "Nada foi feito ainda."}

        try:
            cfg = Configuration.objects.get(application="gfp")
        except:
            obj.update(success=False)
            obj.update(message="")
        else:
            cfg.set("orgao", self.request.POST.get("orgao", ""))
            cfg.set("responsavel_orgao", self.request.POST.get("responsavel_orgao", ""))
            cfg.set("bairro_orgao", self.request.POST.get("bairro_orgao", ""))
            cfg.set("endereco_orgao", self.request.POST.get("endereco_orgao", ""))
            cfg.set("cep_orgao", self.request.POST.get("cep_orgao", ""))
            cfg.set("complemento_orgao", self.request.POST.get("complemento_orgao", ""))
            cfg.set(
                "telefone_responsavel_orgao",
                self.request.POST.get("telefone_responsavel_orgao", ""),
            )

            cfg.set("class_trib", self.request.POST.get("class_trib", ""))
            cfg.set("nat_jurid", self.request.POST.get("nat_jurid", ""))
            cfg.set("nr_siafi", self.request.POST.get("nr_siafi", ""))
            cfg.set(
                "cod_ente_federativo", self.request.POST.get("cod_ente_federativo", "")
            )
            cfg.set("cod_munic", self.request.POST.get("cod_munic", ""))
            cfg.set("ind_rpps", self.request.POST.get("ind_rpps", ""))
            cfg.set("subteto", self.request.POST.get("subteto", ""))
            cfg.set("vr_subteto", self.request.POST.get("vr_subteto", ""))
            cfg.set("aliq_rat", self.request.POST.get("aliq_rat", ""))
            cfg.set("fap", self.request.POST.get("fap", ""))
            cfg.set("aliq_rat_ajust", self.request.POST.get("aliq_rat_ajust", ""))

            cfg.set("responsavel_gfp", self.request.POST.get("responsavel_gfp", ""))
            cfg.set("email_gfp", self.request.POST.get("email_gfp", ""))
            cfg.set(
                "telefone_responsavel_gfp",
                self.request.POST.get("telefone_responsavel_gfp", ""),
            )
            cfg.set("fax_gfp", self.request.POST.get("fax_gfp", ""))
            cfg.set("inss", self.request.POST.get("inss", ""))

            obj.update(success=True)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.gfp.Configuracao()")

    @login_required("JSON")
    def get_configurations(self, args=[]):
        obj = {"success": True, "message": "Nada foi feito ainda"}

        cfg = Configuration.get_or_create(application="gfp")

        instituicao = {
            "orgao": cfg.get("orgao", ""),
            "responsavel": cfg.get("responsavel_orgao", ""),
            "telefone": cfg.get("telefone_responsavel_orgao", ""),
            "cep": cfg.get("cep_orgao", ""),
            "endereco": cfg.get("endereco_orgao", ""),
            "bairro": cfg.get("bairro_orgao", ""),
            "complemento": cfg.get("complemento_orgao", ""),
            "class_trib": cfg.get("class_trib", ""),
            "nat_jurid": cfg.get("nat_jurid", ""),
            "nr_siafi": cfg.get("nr_siafi", ""),
            "cod_ente_federativo": cfg.get("cod_ente_federativo", ""),
            "cod_munic": cfg.get("cod_munic", ""),
            "ind_rpps": cfg.get("ind_rpps", ""),
            "subteto": cfg.get("subteto", ""),
            "vr_subteto": cfg.get("vr_subteto", ""),
            "aliq_rat": cfg.get("aliq_rat", ""),
            "fap": cfg.get("fap", ""),
            "aliq_rat_ajust": cfg.get("aliq_rat_ajust", ""),
        }

        folha = {
            "responsavel": cfg.get("responsavel_gfp", ""),
            "telefone": cfg.get("telefone_responsavel_gfp", ""),
            "fax": cfg.get("fax_gfp", ""),
            "email": cfg.get("email_gfp", ""),
            "folha": cfg.get("folha", ""),
            "inss": cfg.get("inss", ""),
        }

        obj.update(instituicao=instituicao)
        obj.update(folha=folha)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPControlador(CustomAutocomplete, extjs.ExtWidget):

    def get_message(self, args=[]):
        obj = {}

        can = self.check_permission(
            self.request.user, "change", Folha._meta.app_label, Folha._meta.object_name
        )
        if can is False:
            obj.update(
                message="Você não tem permissão para alterar %s."
                % Folha._meta.object_name
            )
        else:
            try:
                folha = Folha.objects.get(pk=int(self.request.POST.get("folha")))
            except:
                obj.update(
                    {
                        "success": False,
                        "message": "A folha informada não foi encontrada.",
                    }
                )
            else:
                try:
                    m = FolhaMensagem.objects.get(folha=folha, servidor=None)
                except:
                    m = FolhaMensagem(folha=folha)
                    m.save()
                finally:
                    obj.update(
                        {
                            "success": True,
                            "pk": m.pk,
                            "folha": m.folha.pk,
                            "texto": m.texto,
                        }
                    )

        self.response.write(json.encode(obj))

    def folha_info_report(self, args=[]):
        obj = {}

        try:
            f = Folha.objects.get(pk=int(self.request.POST.get("pk")))
        except:
            obj = {
                "message": "Não consegui encontrar a folha de pagamento desejada.",
                "success": False,
            }
        else:
            if self.request.POST.get("tipo") == "1":
                obj = {
                    "success": True,
                    "periodo": f.periodo.pk,
                    "folhatipo": f.tipo_folha.pk,
                }
            elif self.request.POST.get("tipo") == "2":
                obj = {
                    "success": True,
                    "mes": f.periodo.mes,
                    "ano": f.periodo.ano,
                    "folhatipo": f.tipo_folha.pk,
                }
            elif self.request.POST.get("tipo") == "3":
                obj = {
                    "success": True,
                    "periodo": f.periodo.pk,
                    "tipo_folha": f.tipo_folha.pk,
                }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def confirm_pendencia_folha(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                Folha._meta.app_label,
                Folha._meta.object_name,
            )
            if can is False:
                obj.update(
                    message="Você não tem permissão para alterar %s."
                    % Folha._meta.object_name
                )
            else:
                user = get_current_user()
                is_rh = user.has_perm("gfp.can_validate_event_payroll")
                is_ci = user.has_perm("gfp.can_validate_event_internal_control")

                folha = Folha.objects.get(pk=int(self.request.POST.get("pk")))
                fevs = folha.lancamentos.all()

                if is_rh and is_ci:
                    fevs = fevs.filter(
                        Q(confirma_folha=None) | Q(confirma_controle=None)
                    )
                elif is_rh and not is_ci:
                    fevs = fevs.filter(confirma_folha=None)
                elif is_ci and not is_ci:
                    fevs = fevs.filter(confirma_controle=None)

                obj.update(count=fevs.count())
                if is_rh is True:
                    # fevs.update(confirma_folha=self.request.user, dt_confirma_folha=datetime.now())
                    for fev in fevs:
                        fev.confirma("RH", self.request.user)
                        fev.save()
                if is_ci is True:
                    # fevs.update(confirma_controle = self.request.user, dt_confirma_controle = datetime.now())
                    for fev in fevs:
                        fev.confirma("CI", self.request.user)
                        fev.save()

                    folha.ci_por = self.request.user
                    folha.ci = True
                    folha.save()

                obj.update(success=True)
        except Exception as e:
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def confirm(self, args=[]):
        """
        PERMISSOES EXIGIDAS:
            can_validate_event_payroll: Validar eventos pendentes na folha de pagamento
            can_validate_event_internal_control: Validar eventos pendentes no controle interno
        """
        obj = {"success": False, "message": "Nada foi feito ainda."}

        # servidor.lotacoes.filter(sigla__in=getattr(settings, 'SIGLAS_LOTACAO', {}).get('RH-FOLHA', ['GFP'])).exists()
        is_rh = self.request.user.has_perm("gfp.can_validate_event_payroll")
        # servidor.lotacoes.filter(sigla__in=getattr(settings, 'SIGLAS_LOTACAO', {}).get('CI', ['CI'])).exists()
        is_ci = self.request.user.has_perm("gfp.can_validate_event_internal_control")
        fevs = []
        if is_rh or is_ci:
            if "folhaeventos" in self.request.POST:
                fevs = FolhaEvento.objects.filter(
                    pk__in=self.request.POST.getlist("folhaeventos")
                )
            elif "folha" in self.request.POST and "servidor" in self.request.POST:
                fevs = FolhaEvento.objects.filter(
                    folha=Folha.objects.get(pk=int(self.request.POST.get("folha"))),
                    servidor=Servidor.objects.get(
                        pk=int(self.request.POST.get("servidor"))
                    ),
                )
            elif "folha" in self.request.POST and "evento" in self.request.POST:
                fevs = FolhaEvento.objects.filter(
                    folha=Folha.objects.get(pk=int(self.request.POST.get("folha"))),
                )
                if self.request.POST.get("evento"):
                    fevs = fevs.filter(evento=self.request.POST.get("evento"))
            elif "fes" in self.request.POST:
                fevs = FolhaEvento.objects.filter(
                    pk__in=self.request.POST.getlist("fes")
                )

            fevs = fevs.filter(Q(confirma_folha=None) | Q(confirma_controle=None))

        else:
            obj.update(message="Você não tem permissão para confirmar eventos.")

        sid = transaction.savepoint()
        is_rh is True and self.log.info("O servidor é do RH")
        is_ci is True and self.log.info("O servidor é do Controle Interno")
        try:
            count = 0
            for fev in fevs:
                count += 1 if (is_rh is True) or (is_ci is True) else 0
                is_rh is True and fev.confirma("RH", self.request.user)
                is_ci is True and fev.confirma("CI", self.request.user)
                fev.save()
        except Exception as e:
            obj.update(message=str(e))
            transaction.savepoint_rollback(sid)
        else:
            obj.update(count=count)
            obj.update(success=(count > 0))
            transaction.savepoint_commit(sid)

        self.response["content-type"] = "text/json"
        self.response.write(json.encode(obj))

    def lock_paycheck(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            can = self.check_permission(
                self.request.user,
                "change",
                Folha._meta.app_label,
                Folha._meta.object_name,
            )
            if can is False:
                obj.update(
                    message="Você não tem permissão para bloquear/desbloquear %s."
                    % Folha._meta.object_name
                )
            else:
                lock = True if self.request.POST.get("lock") == "true" else False
                Folha.objects.filter(pk=int(self.request.POST.get("pk"))).update(
                    paycheck_locked=lock
                )
                obj.update(success=True)
        except Folha.DoesNotExist:
            obj.update(message="Não consegui localizar a folha desejada.")
        except Exception as e:
            obj.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update_status_folha(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        can = self.check_permission(
            self.request.user, "change", Folha._meta.app_label, Folha._meta.object_name
        )
        if can is False:
            obj.update(
                message="Você não tem permissão para alterar %s."
                % Folha._meta.object_name
            )
        else:
            try:
                f = Folha.objects.get(pk=int(self.request.POST.get("pk")))
                f.change_status(int(self.request.POST.get("status")))
            except Folha.DoesNotExist:
                obj.update(message="Não consegui localizar a folha desejada.")
            except Exception as e:
                obj.update(message=str(e))
            else:
                obj.update(success=True)
                obj.update(
                    folha={"pk": f.pk, "description": str(f), "status": f.status}
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_folha_info(self, args=[]):
        obj = {}

        try:
            f = Folha.objects.get(pk=int(self.request.POST.get("pk")))
        except:
            obj = {
                "mes": None,
                "ano": None,
                "tipo_folha": None,
                "periodo": None,
                "success": False,
            }
        else:
            obj = {
                "mes": f.periodo.mes,
                "ano": f.periodo.ano,
                "tipo_folha": f.tipo_folha.pk,
                "periodo": f.periodo.pk,
                "success": True,
            }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_dirf_ano(self, args=[]):
        obj = {}
        root = []
        registred = []

        for p in Periodo.objects.values("ano").annotate(Count("ano")):
            if p.get("ano") not in registred:
                root.append(
                    {
                        "pk": p.get("ano"),
                        "description": p.get("ano"),
                        "dialect": "Lei123",
                    }
                )
                registred.append(p.get("ano"))

        obj.update(root=root)

        Periodo.objects.values("ano").annotate(Count("ano"))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_status_folha(self, folha):
        obj = [
            {
                "iconCls": "%s"
                % (
                    {
                        1: "icon-core icon-core-run",
                        2: "icon-core icon-core-waiting",
                        3: "icon-fopag icon-closed-padlock",
                        4: "icon-fopag icon-stamp-arrow",
                    }.get(folha.status)
                ),
                "alt": folha.get_status_display(),
                "title": folha.get_status_display(),
            }
        ]

        if folha.lancamentos.filter(
            Q(confirma_folha=None) | Q(confirma_controle=None)
        ).exists():
            obj.append(
                {
                    "iconCls": "icon-fopag icon-attention",
                    "alt": "Esta folha ainda tem pendencias.",
                    "title": "Esta folha ainda tem pendencias.",
                }
            )
        else:
            obj.append(
                {
                    "iconCls": "icon-core icon-core-success",
                    "alt": "Esta folha não tem pendencias.",
                    "title": "Esta folha não tem pendencias.",
                }
            )

        return obj

    def json_prepare_float(self, number):
        if number is None:
            return 0.00
        elif number == 0.00:
            return 0.00
        else:
            try:
                return float(number)
            except:
                return 0.00

    @login_required("JSON")
    def anos_folha(self, args=[]):
        obj = {"root": []}

        if "only" not in args:
            obj.get("root").append({"pk": 0, "description": "TODOS"})

        for p in (
            Folha.objects.order_by("-periodo__ano").values("periodo__ano").distinct()
        ):
            obj.get("root").append(
                {"pk": p.get("periodo__ano"), "description": p.get("periodo__ano")}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def tipos_folha(self, args=[]):
        obj = {"root": []}

        obj.get("root").append({"pk": 0, "description": "TODOS"})

        for p in (
            Folha.objects.order_by("tipo_folha")
            .values("tipo_folha", "tipo_folha__titulo")
            .distinct()
        ):
            obj.get("root").append(
                {"pk": p.get("tipo_folha"), "description": p.get("tipo_folha__titulo")}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def folhas(self, args=[]):
        obj = {}

        folhas = Folha.objects.all()

        folhas = (
            folhas.filter(periodo__ano=self.request.POST.get("periodo__ano"))
            if "periodo__ano" in self.request.POST
            else folhas
        )
        folhas = (
            folhas.filter(periodo__mes=self.request.POST.get("periodo__mes"))
            if "periodo__mes" in self.request.POST
            else folhas
        )
        folhas = (
            folhas.filter(tipo_folha=self.request.POST.get("tipo_folha"))
            if "tipo_folha" in self.request.POST
            else folhas
        )
        folhas = (
            folhas.filter(status=self.request.POST.get("status"))
            if "status" in self.request.POST
            else folhas
        )

        obj.update(totalRows=folhas.count())

        if "start" in self.request.POST:
            start = int(self.request.POST.get("start"))
            end = start + int(self.request.POST.get("limit"))
        else:
            start = 0
            end = 50

        folhas = folhas.order_by("-periodo__ano", "-periodo__mes", "tipo_folha")
        folhas = folhas[start:end]

        roots = []

        for f in folhas:
            paychecks = (
                f.paychecks.values("servidor__type_by_possession")
                .annotate(dcount=Count("servidor__type_by_possession"))
                .order_by()
            )
            types = [p["servidor__type_by_possession"] for p in paychecks]
            choices = Choice.objects.filter(active=True, cvalue__in=types)
            types_by_possession_filtered = [c.value for c in choices]

            roots.append(
                {
                    "pk": f.pk,
                    "description": str(f),
                    "tipo_folha": str(f.tipo_folha),
                    "periodo": str(f.periodo),
                    "periodo_pk": f.periodo.pk,
                    "status": self.get_status_folha(f),
                    "fechado_por": (
                        "%s - %s"
                        % (
                            f.fechado_por,
                            (
                                DateUtils.date_to_str(f.dt_fechamento)
                                if f.dt_fechamento
                                else ""
                            ),
                        )
                        if f.fechado_por is not None
                        else "--"
                    ),
                    "validado_por": (
                        "%s - %s"
                        % (f.ci_por, DateUtils.date_to_str(f.dt_ci) if f.dt_ci else "")
                        if f.ci_por is not None
                        else "--"
                    ),
                    "processado_por": (
                        "%s - %s"
                        % (
                            f.processado_por,
                            (
                                DateUtils.date_to_str(f.dt_processado)
                                if f.dt_processado
                                else ""
                            ),
                        )
                        if f.processado_por is not None
                        else "--"
                    ),
                    "data_pagamento": (
                        DateUtils.date_to_str(f.dt_pagamento)
                        if f.dt_pagamento is not None
                        else ""
                    ),
                    "pendencia_folha": f.lancamentos.filter(
                        confirma_folha=None
                    ).count(),
                    "pendencia_controle": f.lancamentos.filter(
                        confirma_controle=None
                    ).count(),
                    "paycheck_locked": f.paycheck_locked,
                    "complement": f"COMPL. {f.complement}" if f.complement else "",
                    "types_by_possession_filtered": types_by_possession_filtered,
                    "folha_anterior": f.folha_anterior.pk if f.folha_anterior else "",
                    "servidores": [],
                }
            )

        obj.update(root=roots)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gfp.Controlador()")

    @login_required("JSON")
    def store(self, args=[]):
        obj = {"result": []}

        if "model" in self.request.POST:
            if self.request.POST["model"] == "FolhaTipo":
                query = FolhaTipo.objects.all()
            elif self.request.POST["model"] == "Banco":
                query = Banco.objects.filter(tem_convenio=1)

            for row in query:
                obj["result"].append({"id": row.pk, "description": str(row)})
        else:
            obj["result"].append({"id": "", "description": "Erro realizando consulta."})

        self.response.write(json.encode(obj))

    @login_required("JSON")
    def recalc(self, args=[]):
        obj = {"success": True}

        payroll = Folha.objects.get(
            tipo_folha=FolhaTipo.objects.get(pk=int(self.request.POST["folha_tipo"])),
            periodo__mes=self.request.POST["folha_mes"],
            periodo__ano=self.request.POST["folha_ano"],
        )

        user = get_current_user()

        Task.start(
            process_recalculate_payroll,
            description="Recalculo da folha %s" % payroll,
            payroll_id=payroll.pk,
            user=user.id,
        )

        self.response.write(json.encode(obj))

    @login_required("JSON")
    @deprecated
    def copy(self, args=[]):
        obj = {"success": True}

        def process(request, base, new, log):

            set_current_user(request.user)

            log.debug("INIT PROCESS COPY...")
            # base.copy_to(
            #     to=new,
            #     to_exists=(created is False),
            #     to_can_clear=('remover' in request.REQUEST),
            # )

        base_payroll = new_payroll = None
        try:
            base_payroll = Folha.objects.get(
                periodo__ano=int(self.request.POST.get("base_ano")),
                periodo__mes=int(self.request.POST.get("base_mes")),
                tipo_folha__pk=int(self.request.POST.get("base_tipo")),
            )

            periodo_to, p_created = Periodo.objects.get_or_create(
                ano=int(self.request.POST.get("copia_ano")),
                mes=int(self.request.POST.get("copia_mes")),
                defaults={
                    "salario_minimo": base_payroll.periodo.salario_minimo,
                    "salario_teto_adm": base_payroll.periodo.salario_teto_adm,
                    "salario_teto_membros": base_payroll.periodo.salario_teto_membros,
                    "salario_familia": base_payroll.periodo.salario_familia,
                    "auxilio_creche": base_payroll.periodo.auxilio_creche,
                    "auxilio_alimentacao": base_payroll.periodo.auxilio_alimentacao,
                },
            )

            new_payroll, created = Folha.objects.get_or_create(
                periodo=periodo_to,
                tipo_folha=FolhaTipo.objects.get(
                    pk=int(self.request.POST.get("copia_tipo"))
                ),
                defaults={
                    # TODO Procurar um configuração para a data provável de pagamento
                    "dt_pagamento": (
                        (base_payroll.dt_fechamento + relativedelta(months=1))
                        if base_payroll.dt_fechamento
                        else None
                    )
                },
            )

        except Folha.DoesNotExist:
            raise Exception("A folha base não existe. Selecione uma folha de origem!")
        except Exception as e:
            log.exception(e)
        else:
            t = threading.Thread(
                target=process, args=(self.request, base_payroll, new_payroll, self.log)
            )
            t.start()

        self.response.write(json.encode(obj))

    @login_required("JSON")
    def pendencies(self, args=[]):
        obj = {}

        query = (
            FolhaEvento.objects.filter(
                contracheque__folha=self.request.POST.get("folha")
            )
            .filter(Q(confirma_controle=None) | Q(confirma_folha=None))
            .order_by("contracheque__servidor")
        )

        is_rh = self.request.user.has_perm("gfp.can_validate_event_payroll")
        is_ci = self.request.user.has_perm("gfp.can_validate_event_internal_control")

        if not is_rh:
            self.log.debug(
                "%s has not perm gfp.can_validate_event_payroll" % self.request.user
            )
            query = query.exclude(Q(confirma_folha=None) & ~Q(confirma_controle=None))

        if not is_ci:
            self.log.debug(
                "%s has not perm gfp.can_validate_event_internal_control"
                % self.request.user
            )
            query = query.exclude(~Q(confirma_folha=None) & Q(confirma_controle=None))

        if "evento" in self.request.POST and self.request.POST.get("evento"):
            query = query.filter(evento=self.request.POST.get("evento"))

        obj.update(totalRows=query.count())

        if "start" in self.request.POST:
            start = int(self.request.POST.get("start"))
            end = start + int(self.request.POST.get("limit"))
        else:
            start = 0
            end = 50

        folha_eventos = query[start:end]
        obj.update(
            root=[
                {
                    # 'status': self.status_lancamento(fe),
                    "pk": fe.pk,
                    "lancamento": fe.get_lancamento_display(),
                    "tipo": fe.evento.get_tipo_display(),
                    "valor": self.json_prepare_float(fe.valor or 0),
                    "valor_base": self.json_prepare_float(fe.valor_base or 0),
                    "patronal": self.json_prepare_float(fe.patronal or 0),
                    "pct": self.json_prepare_float(fe.pct or 0) if fe.pct else "",
                    "qnt": self.json_prepare_float(fe.qnt) if not fe.prazo_desc else "",
                    "qnt_max": self.json_prepare_float(fe.qnt_max),
                    "base_previdencia": self.json_prepare_float(fe.base_previdencia),
                    "parcela": self.json_prepare_float(fe.parcela),
                    "prazo": self.json_prepare_float(fe.prazo_desc),
                    "evento__pk": fe.evento.pk,
                    "evento__automatico": fe.evento.automatico
                    and (fe.classcode and True or False),
                    "servidor": str(fe.contracheque.servidor),
                    "evento": str(fe.evento),
                    "info": fe.info,
                    "reference_month": (
                        self.json_prepare_float(fe.reference_month or 0)
                        if fe.reference_month
                        else ""
                    ),
                    "reference_year": (
                        self.json_prepare_float(fe.reference_year or 0)
                        if fe.reference_year
                        else ""
                    ),
                }
                for fe in folha_eventos
            ]
        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    @deprecated
    def apply_model(self, args=[]):
        obj = {"success": True}

        folha = Folha.objects.get(
            periodo__mes=self.request.POST.get("folha_mes"),
            periodo__ano=self.request.POST.get("folha_ano"),
            tipo_folha__pk=self.request.POST.get("folha_tipo"),
        )
        # folha = Folha.objects.get(pk=self.request.POST.get('folha'))
        model = FolhaModelo.objects.get(pk=self.request.POST.get("folha_modelo"))

        def process(request, folha, model, log):
            # SETTING USER FOR LOCAL

            set_current_user(request.user)

            log.debug("INIT PROCESS APPLY MODEL...")
            folha.apply_model(model)

        t = threading.Thread(target=process, args=(self.request, folha, model, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def get_loaders_file(self, args=[]):
        obj = {"success": True, "men": []}
        for obj in RunCodeManager.get_choices(typeof="LOADER"):
            obj.menu.append({"path": obj[0], "title": obj[1]})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def load_file(self, args=[]):
        obj = {"success": True}

        can = self.check_permission(
            self.request.user, "change", Folha._meta.app_label, Folha._meta.object_name
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % Folha._meta.object_name,
            )
        else:
            payroll = Folha.objects.get(pk=self.request.POST.get("payroll"))
            classcode = ClassCode.objects.get(pk=self.request.POST.get("loader"))
            file_ = File.objects.get(pk=self.request.POST.get("file"))
            event = (
                Evento.objects.get(pk=self.request.POST.get("event"))
                if "event" in self.request.POST and self.request.POST.get("event")
                else None
            )
            log.debug("%s:%s:%s:%s" % (payroll, classcode.path, file_.filename, event))
            create_paycheck = (
                True
                if "create" in self.request.POST and self.request.POST.get("create")
                else False
            )
            # loader = GFPLoader.objects.get()

            set_current_user(self.request.user)
            Loader = classcode.cls(
                file_.absolute_path, payroll, create=create_paycheck, evento=event
            )
            try:
                Loader.pre_validate()
                obj["message"] = "Iniciando carregamento de arquivo."
            except Exception as e:
                obj["message"] = str(e)
                obj["success"] = False
                log.exception(e)
            else:
                Task.start(
                    process_load_file,
                    loader=classcode.pk,
                    payroll=payroll.pk,
                    path=file_.absolute_path,
                    user=get_current_user().pk,
                    create=create_paycheck,
                    event=event,
                )

                # t = threading.Thread(target=process,
                #                      args=(self.request, file_.absolute_path, payroll, classcode.cls),
                #                      kwargs={'event': event, 'create': create_paycheck})
                # t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GFPGeradorArquivoCredito(CommandControllerTaskViewer):

    _description = "Geração de arquivo de crédito"

    @ContentType("text/plain")
    def getFile(self, args=[]):
        sid = self.request.GET.get("sid")

        try:
            f = Folha.objects.get(
                tipo_folha=int(self.request.GET.get("folha_tipo")),
                periodo__mes=int(self.request.GET.get("folha_mes")),
                periodo__ano=int(self.request.GET.get("folha_ano")),
            )

            b = Banco.objects.get(pk=int(self.request.GET.get("banco")))
        except Exception as e:
            self.log.exception(e)
            filename = "banco"
        else:
            filename = "%(sigla)s-%(mes)s-%(ano)s-%(tipo_folha)s" % {
                "sigla": b.nome,
                "mes": f.periodo.get_mes_display(),
                "ano": f.periodo.ano,
                "tipo_folha": str(f.tipo_folha),
            }

        self.response["content-disposition"] = "attachment; filename=%s.txt" % slugify(
            filename
        )
        with open("/tmp/ccb_%s" % sid, "r") as fd:
            for data in iter(partial(fd.read, 8192), b""):
                self.response.write(data)

        unlink("/tmp/ccb_%s" % sid)

    def build(self):
        from rh.gfp.febrabam import lang

        self.log.debug("-----------------TESTE------------------------")

        self.log.info(self.request)

        set_current_user(User.objects.get(username="athenas"))

        self.set("done", False)

        try:
            folha = Folha.objects.get(
                tipo_folha=FolhaTipo.objects.get(pk=int(self.get("folha_tipo"))),
                periodo__mes=int(self.get("folha_mes")),
                periodo__ano=int(self.get("folha_ano")),
            )

            b = Banco.objects.get(pk=int(self.get("banco")))
            banco = lang.get_protocol(b.numero)

            fb = banco.File(
                {
                    "observer": self,
                    "folha": folha,
                    "data_compromisso": folha.dt_pagamento,
                    "lote": 0,  # FIXME: Colocar o Lote no formulário
                }
            )

            fd = open("/tmp/ccb_%s" % self.request.POST.get("sid"), "w")
            fd.write(str(fb))
            fd.close()
        except Exception as e:
            self.log.exception(e)

        self.set("done", True)

    def start(self, args=[]):
        log.info(self.request)
        t = threading.Thread(
            target=self.build
        )  # , args=(self.request.user, log))  # args=(self.request.user, log)
        t.setDaemon(True)
        t.start()


class GFPCopyCreditoConta(CommandController):

    def start(self, args=[]):
        from_ = int(self.get("from"))
        to_ = int(self.get("to"))
        log.debug(self.get("vigencia"))
        vigencia = self.get("vigencia")

        Task.start(
            process_copy_credit_accounts,
            user=self.request.user.id,
            from_tipo=from_,
            to_tipo=to_,
            vigencia=vigencia,
        )


class GFPSocialSecurityWindowFileGenerator(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            "new toolkit.rh.gfp.paycheck.socialsecurity.WindowFileGenerator()"
        )

    def renderer(self, data):
        import json

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    @login_required(type="JSON")
    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        try:
            Task.start(
                igeprev_generator,
                sheet=self.request.POST.get("sheet"),
                user=get_current_user().pk,
                success="""<p>
                    Arquivo
                    <span style="font-weight:bold">IGEPREV %(igeprev)s</span>
                    foi gerado com sucesso. Para fazer o download clique no
                    <a href="/athenas/GFPSocialSecurityWindowFileGenerator/file/?uuid=%(uuid)s">link</a>.
                    </p>
                    <p>
                    Este arquivo está disponível para download até dia
                    <span style="font-weight:bold">%(deadline)s</span>
                    </p>""",
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            sheet = Folha.objects.get(pk=self.request.POST.get("sheet"))
            rst.update(
                success=True,
                message="Arquivo do IGEPREV %s-%s requisitado com sucesso, \
                        você será avisado quando o mesmo for concluído."
                % (sheet.periodo.mes, sheet.periodo.ano),
            )
        self.renderer(rst)

    def file(self, args=[]):
        import json
        from rh.gfp.previdencia.igeprev import IgeprevGenerator

        cache_path = IgeprevGenerator.cache_dir()
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")

                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )

                with open(os.path.join(cache_path, filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo do IGEPREV não está pronto ou não foi solicitado.\
                                                     </h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo do IGEPREV para o usuário\
                                                   logado.</h1>"
            )


class GFPGeradorIgeprev(CommandController):

    ano_referencia = None
    mes_referencia = None

    def json(self, args=[]):
        self.response.write("new toolkit.gfp.GeradorIgeprev()")

    @ContentType("application/zip")
    def getFile(self, args=[]):
        self.response["content-disposition"] = "attachment; filename=%s.zip" % slugify(
            self.get_zipfilename()
        )
        with open(self.get_zipfile(self.get_zipfilename()), "r") as fd:
            for data in iter(partial(fd.read, 8192), b""):
                self.response.write(data)
        unlink(self.get_zipfile(self.get_zipfilename()))

    def get_zipfilename(self):
        name = "mpeto-igeprev-%s-%s-%s" % (
            (
                slugify(Folha.objects.get(pk=self.request.GET.get("folha")).tipo_folha)
                if self.request.GET.get("folha")
                else "mpeto-igeprev"
            ),
            self.request.GET.get("mes"),
            self.request.GET.get("ano"),
        )
        return name

    def get_zipfile(self, zip_name=None):
        name = "%s.zip" % zip_name if zip_name is not None else "mpeto-igeprev"
        return os.path.join(settings.CACHE_PATH, name)

    def builder(self):
        self.set("done", False)
        try:
            tfiles = [
                "orgaos_sisprev",
                "unidades_sisprev",
                "lotacoes_sisprev",
                "cargos_sisprev",
                "fontepagadora_sisprev",
                "tipo_situacaofuncional_sisprev",
                "estadocivil_sisprev",
                "escolaridade_sisprev",
                "tipodependencia_sisprev",
                "quadromilitares_sisprev",
                "pessoas_sisprev",
                "segurados_sisprev",
                "seguradoscedidos_sisprev",
                "pessoasdependentes_sisprev",
                "dependentes_sisprev",
                "eventosrubricas_sisprev",
                "bancos_sisprev",
                "cargosocupados_sisprev",
                "financeiro_sisprev",
                "pensoesalimenticias_sisprev",
                "contribuicoesmensal_sisprev",
            ]
            IgeprevGenerator(
                sheet=self.get("folha"),
                ano_referencia=self.get("ano"),
                mes_referencia=self.get("mes"),
            ).gerador(
                tfiles=tfiles,
                importacao_completa=(
                    True if self.get("importacao_completa") == "on" else False
                ),
            )
        except Exception as e:
            self.log.exception(e)
            self.set("pctGeral", 1.0)
            self.set("pctGeralText", "Ocorreram erros na geração dos arquivos.")

        self.set("done", True)

    def start(self, args=[]):
        t = threading.Thread(target=self.builder)
        t.setDaemon(True)
        t.start()


class GFPViabillize(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        servidor = self.request.user.servidor
        chave = settings.VIABILLIZE_SECRET_KEY
        h = hashlib.new("md5")
        h.update(f"{servidor.matricula}{chave}".encode())

        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            "new rh.gfp.extern.Viabillize({matricula:'%s', pw:'%s'})"
            % (servidor.matricula, h.hexdigest())
        )
