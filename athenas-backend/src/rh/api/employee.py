# -*- coding: utf-8 -*-

import datetime
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Max, Min, Q, ProtectedError
from django.utils.functional import partition

from auditoria.models import LineLog
from contrib.controller import ContentType
from contrib.decorator import login_required
from contrib.extjs import QueryDict
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_date, nil_pk
from contrib.utils import DateUtils, employee_from_user, getLogger
from ged.models import Arquivo
from rh.const import (
    CNH,
    CNH_CATEGORIA,
    CNH_FIRST_DATE,
    CTPS,
    CTPS_SERIE,
    NIS,
    PIS_PASEP,
    PROFESSIONAL_COUNCIL,
    PROFESSIONAL_COUNCIL_ISSUER,
    RESERVISTA,
    RESERVISTA_CLASSE,
    RIC,
    RIC_ISSUER,
    RNE,
    RNE_ISSUER,
    STABLE_BONDING,
    TITULO_ELEITOR,
    TITULO_ELEITOR_MUNICIPIO,
    TITULO_ELEITOR_SECAO,
    TITULO_ELEITOR_ZONA,
)
from rh.gfp.models import ContraCheque, EstruturaTabelaSalarial
from rh.models import (
    DocsDataSpecificSpecialized,
    DocumentSpecialized,
    Estado,
    Localidade,
    Lotacao,
    Molestia,
    MovimentacaoPosse,
    NaturalPersonSpecializedEmployee,
    PessoaFisica,
    PessoaJuridica,
    Relationship,
    Servidor,
    ServidorLotacao,
    ServidorVinculo,
    SocialSecurityConfig,
    Trainee,
    Pais,
    DeclaracaoAtividade,
    MovimentacaoSubstituicao,
)
from rh.utils import format_situacao_funcional

log = getLogger(__name__)


def departament_verify():
    if (
        get_current_user().has_perm("afastamento.ver_membros")
        and get_current_user().has_perm("afastamento.ver_servidores") is False
    ):
        return "expediente"
    return "rh"


class RHEmployeeRestful(RestfulDRY):
    _model = Servidor

    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__iexact",
    )

    exclude_fields = (
        "capacidade",
        "incapacidade",
        "curso",
        "numero_cartao_ponto",
        "classificacao",
        "data_registro",
        "vpi",
        "notificacoes",
        "molestia",
        "lotacoes",
        "data_alteracao",
        "situacao_funcional_cache",
        "categoria_cache",
    )

    force_persist_field_boolean = True

    @ContentType("text/javascript")
    def change_user(self, args=[]):
        rst = {"message": "Nada foi feito ainda", "success": False}

        try:
            with transaction.atomic():
                self._read_special_verb()
                employee = (
                    self.Model.objects.get(pk=self.request.PUT.get("employee"))
                    if self.request.PUT.get("employee") != ""
                    else None
                )
                user = User.objects.get(pk=self.request.PUT.get("user"))

                self.Model.unlink_user(user)
                employee and employee.link_user(user)
        except Servidor.DoesNotExist:
            rst.update(message="Não consegui encontrar o servidor especificado.")
        except User.DoesNotExist:
            rst.update(message="Não consegui encontrar o usuário especificado.")
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Dados persistidos com sucesso.")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.employee.Manager")')

    def model_to_dict(self, instance):
        params = super(RHEmployeeRestful, self).model_to_dict(instance)
        # XXX -->> MPMT Verificar alterações do merge 27/06/2022
        # params.update({'data_posse': None})
        # params.update({'data_exercicio': nil_date(instance.data_exercicio, '')})
        # params.update({'data_desligamento': nil_date(instance.dismissal_date, '')})
        # log.info(f'{instance.data_exercicio} {instance.dismissal_date}')

        first_possession_date = instance.first_possession_date
        params.update(
            {
                "data_posse": (
                    DateUtils.date_to_str(first_possession_date)
                    if first_possession_date
                    else None
                )
            }
        )
        params.update(
            {
                "data_exercicio": (
                    DateUtils.date_to_str(instance.exercise_date)
                    if instance.exercise_date
                    else None
                )
            }
        )
        params.update(
            {
                "data_desligamento": (
                    DateUtils.date_to_str(instance.termination_date)
                    if instance.termination_date
                    else None
                )
            }
        )
        params.update({"social_name": instance.pessoa_fisica.social_name or ""})
        effective = ""
        commission = ""
        elective = ""

        possessions = instance.posses_ativas
        if not instance.ativo:
            possessions = instance.posses

        effectives = possessions.filter(quadro__cargo__tipo_lei_cargo="EF")
        if effectives.exists():
            ef = effectives.latest("data_exercicio")
            effective = ef.quadro
        if instance.ativo or (not effective):
            commissions = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
            )
            if commissions.exists():
                cm = commissions.latest("data_exercicio")
                commission = cm.quadro
            electives = possessions.filter(quadro__cargo__tipo_lei_cargo="EL")
            if electives.exists():
                elective = electives.latest("data_exercicio").quadro

        if not effective and not commission:
            effective = "Não encontrado"
            commission = "Não encontrado"

        departures = instance.departures().first()
        params.update({"departure_unicode": ""})
        if departures:
            params.update({"departure_unicode": departures.__str_restful__()})

        params.update({"effective_unicode": str(effective)})
        params.update({"commission_unicode": str(commission)})
        params.update({"elective_unicode": str(elective)})
        inactive = " (Desligado)" if not instance.ativo else ""
        params.update(
            {
                "unicode_status": f"{instance} - {instance.get_type_by_possession_display()}{inactive}"
            }
        )
        return params

    def export(self, args=[]):
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)

        rst = []
        for record in query:

            first_possession_date = record.first_possession_date

            efetivo = "Não encontrado"
            comissionado = "Não encontrado"
            eletivo = "Não encontrado"

            possessions = record.posses_ativas
            if not record.ativo:
                possessions = record.posses

            efetivos = possessions.filter(quadro__cargo__tipo_lei_cargo="EF")
            if efetivos.exists():
                ef = efetivos.latest("data_exercicio")
                efetivo = ef.quadro
            if record.ativo or (not efetivo):
                comissionados = possessions.filter(
                    quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
                )
                if comissionados.exists():
                    cm = comissionados.latest("data_exercicio")
                    comissionado = cm.quadro
                eletivos = possessions.filter(quadro__cargo__tipo_lei_cargo="EL")
                if eletivos.exists():
                    eletivo = eletivos.latest("data_exercicio").quadro

            departures = record.departures().first()

            rst.append(
                {
                    "Ativo": "SIM" if record.ativo else "Não",
                    "Previdenciário": "",
                    "Matricula": record.matricula,
                    "Nome": record.pessoa_fisica.social_name or "",
                    "Tipo": record.get_type_by_possession_display() or "",
                    "Criação": DateUtils.date_to_str(record.created_at),
                    "Posse": (
                        DateUtils.date_to_str(first_possession_date)
                        if first_possession_date
                        else ""
                    ),
                    "Exercício": (
                        DateUtils.date_to_str(record.exercise_date)
                        if record.exercise_date
                        else ""
                    ),
                    "Desligamento": (
                        DateUtils.date_to_str(record.termination_date)
                        if record.termination_date
                        else ""
                    ),
                    "Afastamento": departures or "",
                    "Cargo Efetivo": efetivo,
                    "Cargo Comissão": comissionado,
                    "Cargo Eletivo": eletivo,
                    "eSocial": (
                        "SIM"
                        if record.event_esocial and record.event_esocial != 0
                        else "NÃO"
                    ),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class RHEmployeeSubstitutesRestful(RHEmployeeRestful):

    @login_required("JSON")
    def get_substitutes(self, args=[]):
        rst = {
            "success": False,
            "message": "Não foi executado nada ainda.",
            "result": [],
        }
        try:
            params = self.get_params(self.request.POST, check_case=True)
            pk = []
            registry = []
            try:
                if (
                    isinstance(params.get("employee_substituted"), (list, tuple))
                    is False
                ):
                    pk = [params.get("employee_substituted")]
                else:
                    pk = params.get("employee_substituted", [])
                employee = Servidor.objects.get(pk__in=pk)
                for employee in employee.my_substitute_employee():
                    registry.append(employee.matricula)
            except Exception:
                pass
            try:
                if (
                    isinstance(params.get("workplace_substituted"), (list, tuple))
                    is False
                ):
                    pk = [params.get("workplace_substituted")]
                else:
                    pk = params.get("workplace_substituted", [])
                substituted = Lotacao.objects.get(pk=pk)
                replacements = substituted.replacement_replaceds.filter().distinct()
                replacements_employee = Servidor.objects.filter(
                    pk__in=replacements.values(
                        "substitute__servidores_lotacao__servidor__pk"
                    ),
                    tipo="M",
                    ativo=True,
                )
                for employee in replacements_employee.filter().distinct():
                    registry.append(employee.matricula)
            except Exception:
                pass

            rst.update({"result": registry})

            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_substitutes_unicode(self, employee):
        identify = {"registry": employee.matricula, "order": 0}
        try:
            params = self.get_params()
            try:
                pk = json.loads(params.get("employee_substituted", "0"))
                substituted = Servidor.objects.get(pk=pk)
                for (
                    employee_workplace
                ) in substituted.my_replacement_employee_workplace().filter(
                    servidor=employee
                ):
                    rpl = substituted.my_replacement_substitute(
                        workplace=employee_workplace.lotacao,
                        employee=employee_workplace.servidor,
                    )
                    if rpl.exists():
                        rpl = rpl.earliest("order")
                        identify.update({"order": rpl.order})
            except Exception:
                pass
            try:
                pk = json.loads(params.get("workplace_substituted", "0"))
                substituted = Lotacao.objects.get(pk=pk)
                rs = substituted.my_substitute_by_employee_order(employee)
                identify.update(rs)
            except Exception:
                pass
        except Exception as err:
            log.exception(err)
        return identify

    def model_to_dict(self, instance):
        params = super(RHEmployeeRestful, self).model_to_dict(instance)
        identify = self.get_substitutes_unicode(instance)
        if len(identify):
            params.update({"unicode": "%s - %s" % (identify.get("order"), instance)})
        return params


class RHEmployeePendingExercises(RHEmployeeRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.managerbyemployee.pendingexercises.Manage", {departament: "%s"})'
            % departament_verify()
        )

    def get_query(self):
        query = (
            super(RHEmployeePendingExercises, self)
            .get_query()
            .exclude(pk__in=Servidor.employee_with_exercises())
        )
        if get_current_user().has_perm(
            "afastamento.ver_membros"
        ) and not get_current_user().has_perm("afastamento.ver_servidores"):
            query = query.filter(tipo="M")
        return query


class RHEmployeeWorkplaceRestful(RestfulDRY):

    _model = ServidorLotacao

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__chefe_imediato__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__icontains",
        "servidor__pessoa_fisica__rg__icontains",
        "servidor__matricula__icontains",
        "servidor__matricula_origem__icontains",
        "servidor__numero_cartao_ponto__icontains",
        "servidor__tipo__icontains",
        "lotacao__nome__icontains",
        "lotacao__sigla__icontains",
        "lotacao__responsavel__pessoa_fisica__nome__icontains",
    )

    exclude_fields = ["auditablemixins_ptr", "audittimestampmodel_ptr"]

    force_persist_boolean_fields = ["ativo", "designacao", "provisorio"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.workplace.Manage")')

    def get_query(self):
        return super(RHEmployeeWorkplaceRestful, self).get_query()

    def model_to_dict(self, instance):
        params = super(RHEmployeeWorkplaceRestful, self).model_to_dict(instance)
        params.update(
            {
                "created_by_departure_unicode": (
                    f"{instance.created_by_departure.servidor} - {instance.created_by_departure.__str_restful__()}"
                    if instance.created_by_departure
                    else ""
                )
            }
        )
        params.update(
            {
                "changed_by_departure_unicode": (
                    instance.changed_by_departure.__str_restful__()
                    if instance.changed_by_departure
                    else ""
                )
            }
        )
        params.update(
            {
                "chefe_imediato_unicode": (
                    str(instance.servidor.chefe_imediato)
                    if instance.servidor.chefe_imediato
                    else ""
                )
            }
        )
        params.update(
            {
                "chefe_lotacao_unicode": (
                    str(instance.lotacao.responsavel)
                    if instance.lotacao and instance.lotacao.responsavel
                    else ""
                )
            }
        )
        params.update(
            {
                "quadro_unicode": (
                    str(instance.movimentacao_posse.description_possession)
                    if instance.movimentacao_posse
                    else ""
                )
            }
        )
        owner = instance.lotacao.owner.first() or "" if instance.lotacao else ""
        params.update({"owner_employee_unicode": str(owner)})

        type_by_possession = instance.servidor.type_by_possession
        params.update({"type_by_possession": str(type_by_possession)})

        situation_icons = {
            True: "icon-core-success",
            False: "icon-core-delete",
        }

        obj = []
        icon_situation = {
            "iconCls": "icon-core %s" % situation_icons.get(instance.ativo),
            "title": "Ativo" if instance.ativo else "Encerrado",
        }
        icon_main = {
            "iconCls": (
                "icon-core %s" % "icon-core-document-arrow"
                if instance.main
                else "icon-core-blank"
            ),
            "title": "Principal" if instance.main else "",
        }
        icon_responsible = {
            "iconCls": (
                "icon-core %s" % "icon-core-add-selected"
                if instance.responsible
                else "icon-core-blank"
            ),
            "title": "Responsável" if instance.responsible else "Não é Responsável",
        }
        icon_owner = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-admin"
                if instance.owner
                else "icon-core-blank"
            ),
            "title": "Titular" if instance.owner else "Não é titular",
        }
        icon_coordinator = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-run"
                if instance.coordinator
                else "icon-core-blank"
            ),
            "title": "Coordenador" if instance.coordinator else "",
        }
        icon_dimensionamento = {
            "iconCls": (
                "icon-core %s" % "icon-rh icon-core-main"
                if instance.lotacao.dimensionamento
                else "icon-core-blank"
            ),
            "title": "Dimensionamento BI" if instance.lotacao.dimensionamento else "",
        }

        with_prejudice = False
        without_prejudice = False
        action_collaborating = False
        action_helping = False
        action_adjunct = False

        if instance.prejudice == 1:
            with_prejudice = True
        elif instance.prejudice == 2:
            without_prejudice = True

        if instance.action == 1:
            action_helping = True
        elif instance.action == 2:
            action_collaborating = True
        elif instance.action == 3:
            action_adjunct = True

        icon_with_prejudice = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-minus"
                if with_prejudice
                else "icon-core-blank"
            ),
            "title": "Com prejuizo" if with_prejudice else "",
        }
        icon_without_prejudice = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-update-manage"
                if without_prejudice
                else "icon-core-blank"
            ),
            "title": "Sem prejuizo" if without_prejudice else "",
        }
        icon_action_collaborating = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-set-employee"
                if action_collaborating
                else "icon-core-blank"
            ),
            "title": "Colaborando" if action_collaborating else "",
        }
        icon_action_helping = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-users"
                if action_helping
                else "icon-core-blank"
            ),
            "title": "Coadjuvando" if action_helping else "",
        }
        icon_action_adjunct = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-balloons"
                if action_adjunct
                else "icon-core-blank"
            ),
            "title": "Adjunto" if action_adjunct else "",
        }
        icon_acumulative = {
            "iconCls": (
                "icon-core %s" % "icon-fopag icon-arrow-repeat"
                if instance.cumulativa
                else "icon-core-blank"
            ),
            "title": "Cumulativa" if instance.cumulativa else "",
        }

        if (
            MovimentacaoSubstituicao.objects.filter(
                designation_substitute__pk=instance.pk
            ).count()
            > 0
        ):
            with_substitute = True
        else:
            with_substitute = False
        icon_substitute = {
            "icon": (
                "/athenas/static/rh/images/folha-pendencia.png"
                if with_substitute
                else ""
            ),
            "title": (
                "Para esta ocorrência existe substituto indicado, lembre-se de ajusta-los se for necessário."
                if with_substitute
                else ""
            ),
            "alt": (
                "Para esta ocorrência existe substituto indicado, lembre-se de ajusta-los se for necessário."
                if with_substitute
                else ""
            ),
        }

        icon_partial_responsible = {
            "iconCls": (
                "icon-core %s" % "icon-core icon-core-add-all"
                if instance.partial_responsible
                else "icon-core-blank"
            ),
            "title": "Responsável Parcial" if instance.partial_responsible else "",
        }

        obj.append(icon_situation)
        obj.append(icon_main)
        obj.append(icon_responsible)
        obj.append(icon_owner)
        obj.append(icon_coordinator)
        obj.append(icon_partial_responsible)
        obj.append(icon_with_prejudice)
        obj.append(icon_without_prejudice)
        obj.append(icon_action_collaborating)
        obj.append(icon_action_helping)
        obj.append(icon_action_adjunct)
        obj.append(icon_substitute)
        obj.append(icon_acumulative)
        obj.append(icon_dimensionamento)

        params.update({"icons": obj})
        return params

    @login_required("JSON")
    def create_work_assignment(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            pk = self.request.POST.get("pk", False)
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                if pk:
                    inst = self.Model.objects.get(pk=pk)
                    inst.create_work_assignment()
                    rst.update(
                        {
                            "success": True,
                            "message": "Exercício criado com sucesso.",
                        }
                    )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def set_main(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        log.debug("set_main")
        try:
            pk = self.request.POST.get("pk", False)
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                if pk:
                    inst = self.Model.objects.get(pk=pk)
                    log.debug("call set_main")
                    inst.action_set_main(not inst.main)
                    rst.update(
                        {
                            "success": True,
                            "message": "Principal modificado com sucesso.",
                        }
                    )
        except Exception as err:
            log.exception(err)
            rst.update({"message": err})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def work_assignment_rtsi_information(self, args=[]):
        """
        :py:function:: work_locations(self)
        This method returns all work assignments from username supplied by POST method.
            {
                'success': true,
                'message': 'success',
                'result': [
                    {
                        'username': 'test',
                        'work_assignment': [{
                            'pk': 1,
                            'initials': 'tst,
                            'unicode': 'test',
                        }]
                    }
                ]
            }
        :rtype: json
        :return: json
        """
        rst = {"success": True, "message": "success", "result": []}
        try:
            result = []
            username = self.request.POST.get("username", "")
            if not username:
                raise Exception("Username not supplied")
            employee = Servidor.objects.filter(user__username=username, ativo=True)
            if not employee.exists():
                raise Exception("Employee not found for username %s" % username)
            employee = employee.last()
            for work_assignment in employee._raw_locations(active=True, option=2):
                result.append(
                    {
                        "pk": work_assignment.pk,
                        "initials": work_assignment.lotacao.sigla,
                        "unicode": work_assignment,
                    }
                )
            rst.get("result").append({"username": username, "work_assignment": result})
        except Exception as err:
            log.exception(err)
            rst.update(
                {
                    "message": err,
                    "success": False,
                }
            )
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para criar %s."
                % self.Model._meta.object_name
            )
        else:
            try:
                params = self.get_params(self.request.POST, check_case=True)
                inst = self.factoryModel(**params)

                if self.use_full_clean:
                    inst.full_clean()

                inst.save()
                self.fill_instance_m2m(inst, params)
            except ValidationError as e:
                log.exception(e)
                rst.update(
                    errors=[
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ],
                    message="Alguns campos não foram preenchidos corretamente.",
                )
            except Exception as e:
                try:
                    errors = [
                        {"field": key, "values": value}
                        for key, value in e.message_dict.items()
                    ]
                    rst.update(message=str(errors[0]["values"][0]))
                except:
                    rst.update(message=str(e))
                log.exception(e)
            else:
                posses = inst.servidor.posses_ativas.filter().exists()
                if posses:
                    rst.update(
                        {
                            "success": False,
                            "message": "Dados salvos com sucesso! *Obs: Existem posses ativas, por favor, verifique se há lotação cadastrada e se contém os dados corretos.",
                            "instance": self.model_to_dict(inst),
                        }
                    )
                else:
                    rst.update(
                        {
                            "success": True,
                            "message": "Dados persistido com sucesso.",
                            "instance": self.model_to_dict(inst),
                        }
                    )

        return rst


class RHManagerWorkplaceRestful(RHEmployeeWorkplaceRestful):

    def do_put(self, pk=None):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )

        if can is False:
            rst.update(
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name
            )
        else:
            inst = self.get_instance_model(pk)
            if inst.from_substitution:
                rst.update(
                    {
                        "success": False,
                        "message": "ALTERAÇÕES ou EXCLUSÃO de Designação de Substituição deverão ser realizadas SOMENTE pelo Gestor de Afastamentos - Substituições.",
                    }
                )
            else:
                rst.update(
                    self.do_put_multi()
                    if "filter" in self.request.PUT
                    else self.do_put_single(pk)
                )

        return rst

    def do_delete_single(self, pk):
        rst = {"success": False}

        try:
            inst = self.get_instance_model(pk)
        except self.Model.DoesNotExist:
            rst.update(message="Item não encontrado para remoção.")
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            if inst.from_substitution:
                rst.update(
                    {
                        "message": "ALTERAÇÕES ou EXCLUSÃO de Designação de Substituição deverão ser realizadas SOMENTE pelo Gestor de Afastamentos - Substituições.",
                    }
                )
            else:
                try:
                    inst.delete()
                except ProtectedError:
                    rst.update(
                        message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
                    )
                except Exception as e:
                    rst.update(message=str(e))
                    log.exception(e)
                else:
                    rst.update({"message": "Removido com sucesso!", "success": True})

        return rst

    def do_delete_multi(self):
        rst = {"success": False}

        try:
            query = self.do_filter(self.get_query())
            query = query.filter(from_substitution=False)

            rst.update(count=query.count())
            with transaction.atomic():
                if (
                    self.force_orm_single is False
                    and getattr(self, "force_orm_delete_single", False) is False
                ):
                    query.delete()
                else:
                    [obj.delete() for obj in query]
        except ProtectedError:
            rst.update(
                message="Não posso remover os itens selecionados, pois, eles estão ligados a outros itens."
            )
        except Exception as e:
            rst.update(message=str(e))
            log.exception(e)
        else:
            rst.update(
                {
                    "success": True,
                    "message": "Dados removidos com sucesso. Obs.: foram removidos somente os registros que NÃO são de SUBSTITUIÇÃO.",
                }
            )

        return rst


class RHEmployeeWorkplaceOwnerLocationRestful(RHEmployeeWorkplaceRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.workplace.OwnerLocationManage")')

    def get_query(self):
        query = super(RHEmployeeWorkplaceOwnerLocationRestful, self).get_query()
        employee = None
        try:
            flist = json.loads(self.get_params().get("filter", "[]"))
            for item in flist:
                if item.get("property") == "servidor__id":
                    employee = Servidor.objects.get(pk=item.get("value"))
        except Exception as err:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % err
            )
        if employee and employee.membro:
            query = employee._raw_locations().filter(owner=True)
        return query.order_by("-data_vigencia_inicio")


class RHEmployeeWorkplaceMemberRestful(RHEmployeeWorkplaceRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.workplace.member.Manage")')

    def get_query(self):
        return (
            super(RHEmployeeWorkplaceMemberRestful, self)
            .get_query()
            .filter(servidor__tipo="M")
        )


class RHEmployeeWorkplaceMemberDetail(RHEmployeeRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.workplace.member.Detail")')

    def get_query(self):
        return super(RHEmployeeWorkplaceMemberDetail, self).get_query().filter(tipo="M")


class RHEmployeeWorkplaceByEmployeeManage(RHEmployeeRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.managerbyemployee.Manage", {departament: "%s"})'
            % departament_verify
        )


class RHTraineeExerciseRestful(RHEmployeeRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.trainee.exercise.Manage")',
        )


class RHCollaboratorRestful(RHEmployeeRestful):

    def get_query(self):
        return (
            super(RHCollaboratorRestful, self)
            .get_query()
            .filter(tipo__in=["E", "T", "V", "X"])
        )

    def model_to_dict(self, instance):
        params = super(RHCollaboratorRestful, self).model_to_dict(instance)
        params.update(
            {
                "cpf": instance.pessoa_fisica.cpf if instance.pessoa_fisica else "----",
                "date_born": (
                    nil_date(instance.pessoa_fisica.data_nascimento, "")
                    if instance.pessoa_fisica
                    else ""
                ),
            }
        )
        return params


class RHOutsourcedRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="T")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {"matriculaFieldBlocked": self.get_matricula_field_blocked()}
        ext_create = f"Ext._create('rh.employee.outsourced.Manage', {params})"
        self.response.write(ext_create)


class RHOutsourcedExerciseRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="T")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.outsourced.exercise.Manage")')


class RHApprenticeRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="A")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {"matriculaFieldBlocked": self.get_matricula_field_blocked()}
        ext_create = f"Ext._create('rh.employee.apprentice.Manage', {params})"
        self.response.write(ext_create)


class RHApprenticeExerciseRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="A")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.apprentice.exercise.Manage")')


class RHVoluntaryRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="V")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {"matriculaFieldBlocked": self.get_matricula_field_blocked()}
        ext_create = f"Ext._create('rh.employee.voluntary.Manage', {params})"
        self.response.write(ext_create)


class RHExternalRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="X")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {"matriculaFieldBlocked": self.get_matricula_field_blocked()}
        ext_create = f"Ext._create('rh.employee.external.Manage', {params})"
        self.response.write(ext_create)


# class RHRetiree(RestfulDRY):

#     _model = Retiree

#     full_text_index = (
#         'matricula__icontains',
#         'matricula_origem__icontains',
#         'pessoa_fisica__nome__icontains',
#         'pessoa_fisica__cpf__icontains',
#         'pessoa_fisica__rg__icontains',
#         'pessoa_fisica__email_institucional__icontains',
#         'pessoa_fisica__address__logradouro__icontains',
#         'pessoa_fisica__phone__numero__icontains',
#     )

#     exclude_fields = ['servidor_ptr']

#     def json(self, args=[]):
#         self.response['content-type'] = 'text/javascript'
#         self.response.write('Ext._create("rh.employee.retiree.Manage")')


class RHVoluntaryExerciseRestful(RHCollaboratorRestful):

    def get_query(self):
        return super(RHCollaboratorRestful, self).get_query().filter(tipo="V")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.voluntary.exercise.Manage")')


class RHTrainee(RestfulDRY):

    _model = Trainee

    full_text_index = (
        "matricula__icontains",
        "matricula_origem__icontains",
        "numero_cartao_ponto__icontains",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__icontains",
        "pessoa_fisica__rg__icontains",
        "pessoa_fisica__email_institucional__icontains",
        "pessoa_fisica__address__logradouro__icontains",
        "pessoa_fisica__phone__numero__icontains",
    )

    exclude_fields = ["servidor_ptr"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {"matriculaFieldBlocked": self.get_matricula_field_blocked()}
        ext_create = f"Ext._create('rh.employee.trainee.Manage', {params})"
        self.response.write(ext_create)


class RHLinkToEmployee(RestfulDRY):

    _model = ServidorVinculo

    full_text_index = (
        "servidor__matricula__icontains",
        "servidor_vinculado__matricula__icontains",
        "servidor__pessoa_fisica__nome__icontains",
        "servidor_vinculado__pessoa_fisica__nome__icontains",
        "servidor__pessoa_fisica__cpf__icontains",
        "servidor_vinculado__pessoa_fisica__cpf__icontains",
    )

    exclude_fields = ["servidor_ptr"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.employee.linktoemployee.Manage")')


class RHEmployeeSpecialized(RHEmployeeRestful):

    full_text_index = (
        "matricula__iexact",
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__social_name__icontains",
        "pessoa_fisica__cpf__iexact",
    )

    @classmethod
    def _concat_obj(cls, obj, obj_par):
        errors = obj_par.get("errors", {})
        for err in errors:
            obj["success"] = False
            obj["errors"].update({err: errors.get(err)})
        return obj

    @classmethod
    def _concat_validation_error(cls, obj, validation_error):
        validation_error = dict(validation_error)
        obj["success"] = False
        for key in validation_error:
            obj["errors"].update({"message_err": validation_error.get(key)})
        return obj

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        params = {
            "departament": departament_verify(),
            "organIdentifier": settings.ORGAN_IDENTIFIER,
            "matriculaFieldBlocked": self.get_matricula_field_blocked(),
        }
        ext_create = f"Ext._create('rh.employee.specialized.Manage', {params})"
        self.response.write(ext_create)

    @login_required("JSON")
    def foto_resizelink(self, args=[]):
        rst = {
            "success": False,
            "message": "Não foi executado nada ainda.",
            "foto_link": "",
        }
        try:
            params = self.get_params(self.request.POST, check_case=True)
            pk = params.get("pk", None)
            if pk:
                rst.update(
                    {"foto_link": Arquivo.objects.get(pk=pk).resizelink((85, 113))}
                )
            rst["success"] = True
            rst["message"] = "Sucesso."
        except Exception as err:
            log.exception(err)
            rst["message"] = err

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def model_to_dict(self, instance):
        params = super(RHEmployeeSpecialized, self).model_to_dict(instance)

        cnh = instance.pessoa_fisica.cnh
        cnh_categoria = cnh.cnh_category if cnh else None
        cnh_first_date = cnh.cnh_first_date if cnh else None
        ctps = instance.pessoa_fisica.ctps
        serie_ctps = ctps.ctps_series if ctps else None
        pis_pasep = instance.pessoa_fisica.pis_pasep
        reservista = instance.pessoa_fisica.reservist
        classe_reservista = reservista.reservist_class if reservista else None
        professional_council = instance.pessoa_fisica.professional_council
        professional_council_issuer = ""
        professional_council_number = ""
        professional_council_state = ""
        professional_council_expedition_date = ""
        professional_council_validity_date = ""
        if professional_council:
            professional_council_issuer = (
                professional_council.professional_council_issuer
            )
            professional_council_issuer = (
                professional_council_issuer.valor if professional_council_issuer else ""
            )
            professional_council_number = professional_council.numero
            professional_council_state = nil_pk(
                professional_council.estado_expedicao, None
            )
            professional_council_expedition_date = nil_date(
                professional_council.data_expedicao, None
            )
            professional_council_validity_date = nil_date(
                professional_council.data_validade, None
            )
        voter = instance.pessoa_fisica.voter
        zona_titulo = voter.voter_zone if voter else None
        secao_titulo = voter.voter_section if voter else None
        municipio_titulo = voter.voter_city_local if voter else None
        nis = instance.pessoa_fisica.nis

        try:
            disease = instance.molestia
        except:
            disease = None

        params.update(
            {
                "employeePk": nil_pk(instance, None),
                "is_member": instance.is_member,
                "naturalPersonPk": nil_pk(instance.pessoa_fisica, None),
                "nome": str(instance.pessoa_fisica) or "",
                "social_name": instance.pessoa_fisica.social_name or "",
                "sexo": str(instance.pessoa_fisica.sexo) or "",
                "raca_cor": str(instance.pessoa_fisica.raca_cor) or "",
                "estado_civil": str(instance.pessoa_fisica.estado_civil) or "",
                "immigrant_residence_time": str(
                    instance.pessoa_fisica.immigrant_residence_time
                )
                or "",
                "immigrant_entry_condition": str(
                    instance.pessoa_fisica.immigrant_entry_condition
                )
                or "",
                "quota_system": str(instance.quota_system) or "",
                "grau_instrucao": str(instance.pessoa_fisica.grau_instrucao) or "",
                "sexual_orientation": str(instance.pessoa_fisica.sexual_orientation)
                or "",
                "municipio_naturalidade": nil_pk(
                    instance.pessoa_fisica.municipio_naturalidade, None
                ),
                "nationality": nil_pk(instance.pessoa_fisica.nationality, None),
                "nationality_birth": nil_pk(
                    instance.pessoa_fisica.nationality_birth, None
                ),
                "email_institucional": instance.pessoa_fisica.email_institucional or "",
                "email_pessoal": instance.pessoa_fisica.email_pessoal or "",
                "data_nascimento": str(instance.pessoa_fisica.data_nascimento) or "",
                "data_obito": str(instance.pessoa_fisica.data_obito) or "",
                "sangue": str(instance.pessoa_fisica.sangue) or "",
                "fator_rh": str(instance.pessoa_fisica.fator_rh) or "",
                "doador": instance.pessoa_fisica.doador,
                "nome_pai": instance.pessoa_fisica.nome_pai or "",
                "nome_mae": instance.pessoa_fisica.nome_mae or "",
                "nome_conjuge": instance.pessoa_fisica.nome_conjuge or "",
                "cpf": str(instance.pessoa_fisica.cpf) or "",
                "rg": instance.pessoa_fisica.rg or "",
                "rg_orgao": str(instance.pessoa_fisica.rg_orgao) or "",
                "rg_data_expedicao": str(instance.pessoa_fisica.rg_data_expedicao)
                or "",
                "rg_uf": nil_pk(instance.pessoa_fisica.rg_uf, None),
                "foto": nil_pk(instance.pessoa_fisica.foto, None),
                "foto_link": (
                    instance.pessoa_fisica.foto.resizelink((85, 113))
                    if instance.pessoa_fisica.foto
                    else ""
                ),
                "foto_unicode": str(instance.pessoa_fisica.foto) or "",
                "nis": nis.numero if nis else "",
                "cnh": str(cnh.numero) if cnh else "",
                "cnh_categoria": str(cnh_categoria.valor) if cnh_categoria else "",
                "cnh_expedition_date": nil_date(
                    cnh.data_expedicao if cnh else None, None
                ),
                "cnh_validity_date": nil_date(cnh.data_validade if cnh else None, None),
                "cnh_first_date": str(cnh_first_date.valor) if cnh_first_date else "",
                "cnh_state": nil_pk(cnh.estado_expedicao if cnh else None, None),
                "ctps": str(ctps.numero) if ctps else None,
                "serie_ctps": str(serie_ctps.valor) if serie_ctps else None,
                "ctps_state": nil_pk(ctps.estado_expedicao if ctps else None, None),
                "pis_pasep": str(pis_pasep.numero) if pis_pasep else "",
                "reservista": reservista.numero if reservista else "",
                "classe_reservista": (
                    classe_reservista.valor if classe_reservista else ""
                ),
                "professional_council": professional_council_number,
                "professional_council_state": professional_council_state,
                "professional_council_expedition_date": professional_council_expedition_date,
                "professional_council_validity_date": professional_council_validity_date,
                "professional_council_issuer": professional_council_issuer,
                "titulo_eleitor": voter.numero if voter else "",
                "zona_titulo": zona_titulo.valor if zona_titulo else "",
                "secao_titulo": secao_titulo.valor if secao_titulo else "",
                "municipio_titulo": nil_pk(municipio_titulo, None),
                "molestia": nil_pk(disease, None),
                "job_position_efective": "",
                "progression_efective": "",
                "job_position_commission": "",
                "reference_commission": "",
                "job_position_elective": "",
                "reference_elective": "",
                "employee_status": "",
                "type_by_possession_display": "",
                "situation_functional_information": "",
                "workplace_information": "",
                "work_assignment_information": "",
                "probationary_stage_information": "",
                "date_stability_information": "",
                "genero": instance.pessoa_fisica.genero or "",
                "organ_identifier": settings.ORGAN_IDENTIFIER,
            }
        )
        try:
            workplace_information = "Lotação não existe ou não está ativa"
            work_assignment_information = "Exercício não existe ou não está ativa"
            for sl in instance.workplace_only:
                workplace_information = "{} {}".format(workplace_information, sl)
            for sl in instance.work_assignment:
                work_assignment_information += " " + "{}".format(sl)

            situation_functional_information = format_situacao_funcional(
                instance.situacao_funcional_cache
            )
            if instance.pessoa_fisica.data_obito:
                situation_functional_information += " - Falecido"

            reference_ef = None
            date_progression = None
            possessions = instance.posses_ativas
            possession_ef = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("EF", "AC")
            )
            if possession_ef.exists():
                possession_ef = possession_ef.last()
                reference_ef = (
                    ContraCheque._get_referencia_from_posse(
                        possessions.get(quadro__cargo__tipo_lei_cargo="EF")
                    )
                    if instance.is_efetivo
                    else None
                )
                progressions = possession_ef.progressoes.exclude(
                    data_inicio_vigencia__gt=datetime.datetime.now()
                )
                if progressions.exists() and not instance.membro:
                    date_progression = progressions.latest(
                        "data_inicio_vigencia"
                    ).data_inicio_vigencia
                elif instance.membro and possession_ef:
                    date_progression = possession_ef.data_posse

            possession_cmfc = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
            )
            if possession_cmfc.exists():
                possession_cmfc = possession_cmfc.last()
            else:
                possession_cmfc = None
            possession_el = possessions.filter(
                quadro__cargo__tipo_lei_cargo__in=("EL",)
            )
            if possession_el.exists():
                possession_el = possession_el.last()
            else:
                possession_el = None

            reference_cmfc = self._get_progression_info(possession_cmfc)

            job_position_efective = ""
            if possession_ef:
                job_position_efective = "{} - Posse: {} - Exercício: {}".format(
                    possession_ef.quadro,
                    nil_date(possession_ef.data_posse, ""),
                    nil_date(possession_ef.data_exercicio, ""),
                )
            progression_efective = ""
            if reference_ef and date_progression:
                progression_efective = "{} - Início: {}".format(
                    reference_ef.sigla_cache, nil_date(date_progression, "")
                )

            job_position_commission = ""
            reference_commission = ""
            if possession_cmfc:
                job_position_commission = "{} - Posse: {} - Exercício: {}".format(
                    possession_cmfc.quadro,
                    nil_date(possession_cmfc.data_posse, ""),
                    nil_date(possession_cmfc.data_exercicio, ""),
                )
                if reference_cmfc:
                    reference_commission = "{} - Início: {}".format(
                        reference_cmfc, nil_date(possession_cmfc.data_posse, "")
                    )

            job_position_elective = ""
            reference_elective = ""
            if possession_el:
                job_position_elective = "{} - Posse: {} - Exercício: {}".format(
                    possession_el.quadro,
                    nil_date(possession_el.data_posse, ""),
                    nil_date(possession_el.data_exercicio, ""),
                )
                if reference_cmfc:
                    reference_elective = "{} - Início: %s".format(
                        reference_ef, nil_date(possession_el.data_posse, "")
                    )

            params.update(
                {
                    "job_position_efective": job_position_efective,
                    "progression_efective": progression_efective,
                    "job_position_commission": job_position_commission,
                    "reference_commission": reference_commission,
                    "job_position_elective": job_position_elective,
                    "reference_elective": reference_elective,
                    "employee_status": "Ativo" if instance.ativo else "Inativo",
                    "type_by_possession_display": instance.get_type_by_possession_display(),
                    "situation_functional_information": situation_functional_information,
                    "work_assignment_information": work_assignment_information,
                    "probationary_stage_information": (
                        "" if not instance.is_efetivo else "Em processamento"
                    ),
                    "date_stability_information": (
                        "" if not instance.is_efetivo else "Em processamento"
                    ),
                }
            )

            situation_icons = {
                True: "icon-status",
                False: "icon-status-busy",
            }

            obj = []
            icon_situation = {
                "iconCls": "icon-fopag  %s"
                % situation_icons.get(bool(instance.regime_social_security)),
                "title": (
                    "Configuração Previdênciaria Existente"
                    if bool(instance.regime_social_security)
                    else "Sem Configuração Previdênciaria"
                ),
            }
            obj.append(icon_situation)
            params.update({"icons": obj})
        except Exception as err:
            log.exception(err)
        return params

    def _get_progression_info(self, possession):
        reference = None
        try:
            if possession:
                rs = EstruturaTabelaSalarial.salarios(possession.quadro.cargo)
                reference = rs[0][1] if rs else None
        except Exception as err:
            log.exception(err)
        return reference

    def do_put_single(self, pk=None):
        """Atualiza uma instância."""
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        log.debug("do_put_single")
        inst = None
        try:
            log.debug(
                "COUNT UPDATE FOR %s [%s,]: %s"
                % (self.Model.__name__, pk, self.Model.objects.filter(pk=pk).count())
            )
            querydict = self.request.PUT
            querydict = (
                querydict
                if querydict is not None
                else getattr(self.request, self.request.method, QueryDict("", False))
            )

            servidor = self.Model.objects.get(pk=pk)
            if (
                settings.ORGAN_IDENTIFIER == "mpmt"
                and servidor.type_by_possession != querydict.get("type_by_possession")
                and (
                    servidor.type_by_possession != "EFC"
                    and querydict.get("type_by_possession") != "EFE"
                )
                and (
                    servidor.type_by_possession != "EFE"
                    and querydict.get("type_by_possession") != "EFC"
                )
            ):
                raise Exception(
                    {"message_err": "Não é permitido alterar Tipo de Servidor"}
                )
            elif (
                servidor.type_by_possession == "EFC"
                and querydict.get("type_by_possession") == "EFE"
                or servidor.type_by_possession == "EFE"
                and querydict.get("type_by_possession") == "EFC"
            ):
                _querydict = querydict.copy()
                _querydict.update({"type_by_possession": servidor.type_by_possession})
                querydict = _querydict

            log.debug(querydict)
            obj = self._employee_commit(querydict=querydict)
            inst = Servidor.objects.get(pk=int(obj.get("employeePk")))
        except Exception as err:
            log.exception(err)
            rst.update(message=f"{err.args[0]['message_err']}")
        except ValidationError as err:
            log.exception(err)
            message = "Alguns campos não foram preenchidos corretamente."
            if err.message_dict.get("message_err", None):
                message = err.message_dict.get("message_err")
            rst.update(
                errors=[
                    {"field": key, "values": value}
                    for key, value in list(err.message_dict.items())
                ],
                message=message,
            )
        else:
            rst.update(
                {
                    "success": True,
                    "message": "Dados persistido com sucesso.",
                    "instance": self.model_to_dict(inst),
                }
            )
        return rst

    def do_post(self):
        """Executa uma requisição POST.

        :returns: Dicionário com mensagem de sucesso ou falha e uma instância.
        """
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        can = self.check_permission(
            self.request.user,
            "add",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        log.debug("do_post")
        inst = None
        try:
            if can is False:
                rst.update(
                    message="Você não tem permissão para criar %s."
                    % self.Model._meta.object_name
                )
            else:
                querydict = self.request.POST
                querydict = (
                    querydict
                    if querydict is not None
                    else getattr(
                        self.request, self.request.method, QueryDict("", False)
                    )
                )
                log.debug(querydict)
                obj = self._employee_commit(querydict=querydict)
                inst = Servidor.objects.get(pk=int(obj.get("employeePk")))
        except Exception as e:
            log.exception(e)
            if e.args[0]["message_err"]:
                rst.update(message=f"{e.args[0]['message_err']}")
        except ValidationError as e:
            log.exception(e)
            rst.update(
                errors=[
                    {"field": key, "values": value}
                    for key, value in list(err.message_dict.items())
                ],
                message=message,
            )
        else:
            rst.update(
                {
                    "success": True,
                    "message": "Dados persistido com sucesso.",
                    "instance": self.model_to_dict(inst),
                }
            )
        return rst

    def _search_natural_person(
        self, employee_pk=None, natural_person_pk=None, rg=None, cpf=None
    ):
        natural_person = None
        if natural_person_pk:
            natural_person = PessoaFisica.objects.get(pk=int(natural_person_pk))
            self.log.warn("Utilizando Pessoa Física enviada: %s" % natural_person)
        if not natural_person and employee_pk:
            natural_person = Servidor.objects.get(pk=int(employee_pk)).pessoa_fisica
            self.log.warn(
                "Utilizando Pessoa Física(%s) a partir do Servidor(%s)"
                % (natural_person, employee_pk)
            )
        if not natural_person:
            rst_cpf = None
            if cpf:
                rst_cpf = PessoaFisica.objects.filter(cpf=cpf)
                natural_person = rst_cpf.last()
                self.log.warn(
                    "Utilizando Pessoa Física(%s) a partir do CPF(%s)."
                    % (natural_person, cpf)
                )
        if not natural_person:
            self.log.warn(
                "Pessoa Física não encontrada! A partir de agora será criado um novo cadastro."
            )
        return natural_person

    def _search_employee(self, pk, registry):
        employee = None
        if pk:
            employee = Servidor.objects.filter(pk=int(pk)).last()
        if registry and not employee:
            employee = Servidor.objects.filter(matricula=registry).last()
        return employee

    @login_required(type="JSON")
    def _employee_commit(self, querydict={}):
        obj = {
            "success": True,
            "errors": {},
            "employeePk": None,
            "naturalPersonPk": None,
            "matricula": None,
        }

        if (
            not querydict.get("pis_pasep", None)
            and querydict.get("type_by_possession", None) == "CMS"
        ):
            msg_err = "Dados de servidor não persistidos. PIS/PASEP não informado."
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"message_err": msg_err}
            )

        linelog = LineLog(level=71, status=1)
        linelog.read_request(self.request)
        obj_naturalperson = {"success": False, "errors": {}}
        obj_document = {"success": False, "errors": {}}
        obj_employee = {"success": False, "errors": {}}

        employee = self._search_employee(
            querydict.get("employeePk", None), querydict.get("matricula", None)
        )
        natural_person = self._search_natural_person(
            employee_pk=querydict.get("employeePk", None),
            natural_person_pk=querydict.get("naturalPersonPk", None),
            rg=querydict.get("rg", None),
            cpf=querydict.get("cpf", None),
        )

        did_save_documents = False
        if natural_person:
            obj_document = RHEmployeeSpecialized._save_document(
                natural_person, querydict
            )
            did_save_documents = True

        natural_person, obj_naturalperson = (
            RHEmployeeSpecialized._save_natural_person_employee(
                natural_person, querydict
            )
        )
        self._exibe_erros(obj_naturalperson, linelog, natural_person, employee)

        if natural_person:
            obj.update({"naturalPersonPk": natural_person.pk})
            if not did_save_documents:
                obj_document = RHEmployeeSpecialized._save_document(
                    natural_person, querydict
                )
                self._exibe_erros(obj_document, linelog, natural_person, employee)
            natural_person.clean()
            if obj_document.get("success") and obj_naturalperson.get("success"):
                employee, obj_employee = self._save_employee(
                    employee, natural_person, querydict
                )
            self._exibe_erros(obj_employee, linelog, natural_person, employee)

        if employee:
            obj.update({"employeePk": employee.pk, "matricula": employee.matricula})
        RHEmployeeSpecialized._concat_obj(obj, obj_naturalperson)
        RHEmployeeSpecialized._concat_obj(obj, obj_document)
        RHEmployeeSpecialized._concat_obj(obj, obj_employee)

        self._exibe_erros(obj, linelog, natural_person, employee)
        return obj

    def _exibe_erros(self, obj, linelog, natural_person, employee):
        validation_error = {}
        if obj.get("success") is False:
            linelog.status = 0
            err = ""
            errors = dict(obj.get("errors", []))
            for key in errors:
                validation_error.update({key: errors.get(key)})
                err += " - %s" % errors.get(key)
            linelog.json_description["messageException"] = err
            if validation_error:
                if natural_person:
                    validation_error.update({"naturalPersonPk": natural_person.pk})
                if employee:
                    if employee.pk:
                        validation_error.update({"employeePk": employee.pk})
                    if employee.matricula:
                        validation_error.update({"matricula": employee.matricula})
                try:
                    if "message_err" in validation_error:
                        dict_validation_error = dict(validation_error["message_err"])
                        mss_validation_error = []
                        for key in dict_validation_error:
                            mss_validation_error.append(
                                f"{mss_validation_error}{key}: {dict_validation_error[key]}"
                            )
                        validation_error["message_err"] = mss_validation_error[0]
                    raise Exception(validation_error)
                except:
                    raise Exception(validation_error)

    @classmethod
    def _save_natural_person_employee(self, natural_person, querydict={}):
        if natural_person:
            natural_person = NaturalPersonSpecializedEmployee.objects.get(
                pk=natural_person.pk
            )
        obj = {"success": True, "errors": {}}
        nome = querydict.get("nome", None)
        social_name = querydict.get("social_name", None)
        genero = querydict.get("genero", None)
        cpf = querydict.get("cpf", None)
        rg = querydict.get("rg", None)
        sexo = querydict.get("sexo", None)
        sangue = querydict.get("sangue", None)
        estado_civil = querydict.get("estado_civil") or None
        immigrant_residence_time = querydict.get("immigrant_residence_time") or None
        immigrant_entry_condition = querydict.get("immigrant_entry_condition") or None
        sexual_orientation = querydict.get("sexual_orientation", None)
        nationality = None
        try:
            nationality = Pais.objects.get(pk=int(querydict.get("nationality")))
        except Exception:
            pass
        nationality_birth = None
        try:
            nationality_birth = Pais.objects.get(
                pk=int(querydict.get("nationality_birth"))
            )
        except Exception:
            pass
        municipio_naturalidade = None
        try:
            municipio_naturalidade = Localidade.objects.get(
                pk=int(querydict.get("municipio_naturalidade"))
            )
        except Exception:
            pass
        raca_cor = querydict.get("raca_cor", None)
        email_institucional = querydict.get("email_institucional", None)
        email_pessoal = querydict.get("email_pessoal", None)
        data_nascimento = None
        try:
            if querydict.get("data_nascimento", None):
                data_nascimento = DateUtils.str_to_date(
                    querydict.get("data_nascimento", None)
                )
        except Exception:
            pass
        data_obito = None
        try:
            if querydict.get("data_obito", None):
                data_obito = DateUtils.str_to_date(querydict.get("data_obito", None))
        except Exception:
            pass
        rg_orgao = querydict.get("rg_orgao", None)
        rg_data_expedicao = None
        try:
            if querydict.get("rg_data_expedicao", None):
                rg_data_expedicao = DateUtils.str_to_date(
                    querydict.get("rg_data_expedicao", None)
                )
        except Exception:
            pass
        rg_uf = None
        try:
            rg_uf = Estado.objects.get(pk=int(querydict.get("rg_uf", None)))
        except Exception:
            pass
        fator_rh = querydict.get("fator_rh", None)

        if querydict.get("doador") == "off" or querydict.get("doador") == "on":
            doador = False if querydict.get("doador") == "off" else True
        else:
            doador = querydict.get("doador", False)
        nome_pai = querydict.get("nome_pai", None)
        nome_mae = querydict.get("nome_mae", None)
        nome_conjuge = querydict.get("nome_conjuge", None)
        foto = None
        try:
            foto = Arquivo.objects.get(pk=querydict.get("foto", None))
        except Exception:
            pass
        grau_instrucao = querydict.get("grau_instrucao", None)
        try:
            if not natural_person:
                natural_person = NaturalPersonSpecializedEmployee(
                    nome=nome,
                    social_name=social_name,
                    estado_civil=estado_civil,
                    immigrant_residence_time=immigrant_residence_time,
                    immigrant_entry_condition=immigrant_entry_condition,
                    sexual_orientation=sexual_orientation,
                    raca_cor=raca_cor,
                    doador=doador,
                    cpf=cpf,
                    rg=rg,
                    sexo=sexo,
                    sangue=sangue,
                    municipio_naturalidade=municipio_naturalidade,
                    nationality=nationality,
                    nationality_birth=nationality_birth,
                    email_institucional=email_institucional,
                    email_pessoal=email_pessoal,
                    data_nascimento=data_nascimento,
                    data_obito=data_obito,
                    rg_orgao=rg_orgao,
                    rg_data_expedicao=rg_data_expedicao,
                    rg_uf=rg_uf,
                    fator_rh=fator_rh,
                    nome_pai=nome_pai,
                    nome_mae=nome_mae,
                    nome_conjuge=nome_conjuge,
                    foto=foto,
                    grau_instrucao=grau_instrucao,
                    genero=genero,
                )
                natural_person.clean_fields()
                natural_person.clean()
                natural_person.save()
            else:
                natural_person.nome = nome
                natural_person.social_name = social_name
                natural_person.cpf = cpf
                natural_person.rg = rg
                natural_person.sexo = sexo
                natural_person.sangue = sangue
                natural_person.estado_civil = estado_civil
                natural_person.immigrant_residence_time = immigrant_residence_time
                natural_person.immigrant_entry_condition = immigrant_entry_condition
                natural_person.sexual_orientation = sexual_orientation
                natural_person.municipio_naturalidade = municipio_naturalidade
                natural_person.nationality = nationality
                natural_person.nationality_birth = nationality_birth
                natural_person.raca_cor = raca_cor
                natural_person.email_institucional = email_institucional
                natural_person.email_pessoal = email_pessoal
                natural_person.data_nascimento = data_nascimento
                natural_person.data_obito = data_obito
                natural_person.rg_orgao = rg_orgao
                natural_person.rg_data_expedicao = rg_data_expedicao
                natural_person.rg_uf = rg_uf
                natural_person.fator_rh = fator_rh
                natural_person.doador = doador
                natural_person.nome_pai = nome_pai
                natural_person.nome_mae = nome_mae
                natural_person.nome_conjuge = nome_conjuge
                natural_person.foto = foto
                natural_person.grau_instrucao = grau_instrucao
                natural_person.genero = genero
                natural_person.clean_fields()
                natural_person.clean()
                natural_person.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"message_err": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return natural_person, obj

    def _save_employee(self, employee=None, natural_person=None, querydict={}):
        obj = {"success": True, "errors": {}}
        permission = False
        registry = querydict.get("matricula", None)
        quota_system = querydict.get("quota_system", None)

        try:
            permission = get_current_user().has_perm(
                "rh.add_servidor"
            ) or get_current_user().has_perm("rh.change_servidor")
            if not permission:
                raise Exception("Você não possui permissão para manipular servidor!")
            if not natural_person:
                raise Exception(
                    "Dados de servidor não persistidos. Pessoa Física não encontrada."
                )
            elif not registry and not settings.CLASSCODE_AUTO_REGISTRATION_NUMBER_SLUG:
                raise ValidationError(
                    {
                        "matricula": "Dados de servidor não persistidos. Matrícula não informada."
                    }
                )
            log.debug(querydict)
            type_by_possession = querydict.get("type_by_possession", None)
            log.debug(f"type_by_possession {type_by_possession}")
            matricula_origem = querydict.get("matricula_origem", None)
            tipo = querydict.get("tipo", None)
            numero_cartao_ponto = querydict.get("numero_cartao_ponto", None)
            numero_cartao_ponto = (
                None if numero_cartao_ponto == "" else numero_cartao_ponto
            )

            chefe_imediato = querydict.get("chefe_imediato", None)
            chefe_imediato = (
                Servidor.objects.get(pk=int(chefe_imediato)) if chefe_imediato else None
            )
            log.debug(chefe_imediato)

            category_esocial = querydict.get("category_esocial") or None
            posicao_concurso = querydict.get("posicao_concurso") or None

            data_referencia_ferias = querydict.get("data_referencia_ferias", None)
            if data_referencia_ferias:
                data_referencia_ferias = DateUtils.str_to_date(data_referencia_ferias)
            else:
                data_referencia_ferias = None

            molestia = querydict.get("molestia", None)
            if molestia:
                molestia = Molestia.objects.get(pk=int(molestia))
            else:
                molestia = None

            classificacao = None
            if not employee:
                self.log.warn("Servidor não possui instância e será persistido.")
                employee = Servidor(
                    type_by_possession=type_by_possession,
                    pessoa_fisica=natural_person,
                    data_referencia_ferias=data_referencia_ferias,
                    matricula=registry,
                    # tipo=tipo,
                    matricula_origem=matricula_origem,
                    numero_cartao_ponto=numero_cartao_ponto,
                    classificacao=classificacao,
                    molestia=molestia,
                    chefe_imediato=chefe_imediato,
                    category_esocial=category_esocial,
                    posicao_concurso=posicao_concurso,
                    quota_system=quota_system,
                )
                employee.clean_fields()
                employee.save()
            else:
                self.log.warn("Servidor será atualizado.")
                employee.type_by_possession = type_by_possession
                employee.data_referencia_ferias = data_referencia_ferias
                employee.matricula = registry
                employee.matricula_origem = matricula_origem
                employee.numero_cartao_ponto = numero_cartao_ponto
                employee.classificacao = classificacao
                employee.molestia = molestia
                employee.chefe_imediato = chefe_imediato
                employee.category_esocial = category_esocial
                employee.posicao_concurso = posicao_concurso
                employee.quota_system = quota_system
                employee.clean_fields()
                employee.save()
        except Exception as err:
            RHEmployeeSpecialized._concat_validation_error(obj, {"message_err": err})
            self.log.exception(err)
        except ValidationError as err:
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return employee, obj

    @classmethod
    def _save_document(self, natural_person, querydict={}):
        obj_final = {"success": True, "errors": {}}

        uniao_estavel, obj = RHEmployeeSpecialized._save_doc_uniao_estavel(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        titulo_eleitor, obj = RHEmployeeSpecialized._save_doc_voter(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        cnh, obj = RHEmployeeSpecialized._save_doc_cnh(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        professional_council, obj = (
            RHEmployeeSpecialized._save_doc_professional_council(
                natural_person, querydict=querydict
            )
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        ctps, obj = RHEmployeeSpecialized._save_doc_ctps(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        pis_pasep, obj = RHEmployeeSpecialized._save_doc_pis_pasep(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        nis, obj = RHEmployeeSpecialized._save_doc_nis(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        reservista, obj = RHEmployeeSpecialized._save_doc_reservist(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        ric, obj = RHEmployeeSpecialized._save_doc_ric(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        rne, obj = RHEmployeeSpecialized._save_doc_rne(
            natural_person, querydict=querydict
        )
        RHEmployeeSpecialized._concat_obj(obj_final, obj)

        return obj_final

    @classmethod
    def _save_doc_cnh(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.cnh
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("cnh", None)
        data_validade = None
        if querydict.get("cnh_validity_date", None):
            data_validade = DateUtils.str_to_date(querydict.get("cnh_validity_date"))
        expedition_date = None
        if querydict.get("cnh_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                querydict.get("cnh_expedition_date")
            )
        state = querydict.get("cnh_state", None)
        if state:
            state = Estado.objects.get(pk=int(state)) if state else None
        else:
            state = None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=CNH,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=data_validade,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            elif number:
                document.numero = number
                document.data_expedicao = expedition_date
                document.data_validade = data_validade
                document.estado_expedicao = state
                document.save(validate_mandatory=False)
            elif document:
                document.delete()
                document = None

            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_cnh_category(document, querydict)[1]
            )
            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_cnh_first_date(document, querydict)[1]
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"cnh": str(err)})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_cnh_category(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.cnh_category
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("cnh_categoria")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CNH_CATEGORIA, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"cnh_categoria": str(err)}
            )
        return data_spec, obj

    @classmethod
    def _save_cnh_first_date(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.cnh_first_date
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("cnh_first_date")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CNH_FIRST_DATE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"cnh_first_date": str(err)}
            )
        return data_spec, obj

    @classmethod
    def _save_doc_ctps(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.ctps
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("ctps", None)
        state = querydict.get("ctps_state", None)
        if state:
            state = Estado.objects.get(pk=int(state)) if state else None
        else:
            state = None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=CTPS,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            elif number:
                document.numero = number
                document.estado_expedicao = state
                document.save(validate_mandatory=False)
            elif document:
                document.delete()
                document = None

            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_ctps_series(document, querydict)[1]
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"ctps": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_ctps_series(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.ctps_series
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("serie_ctps", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=CTPS_SERIE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"serie_ctps": err})
        return data_spec, obj

    @classmethod
    def _save_doc_pis_pasep(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.pis_pasep
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("pis_pasep", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=PIS_PASEP,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save()
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"message_err": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_doc_uniao_estavel(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.uniao_estavel
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("uniao_estavel", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=STABLE_BONDING,
                        numero=number,
                        data_expedicao=datetime.datetime.now(),
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save()
                    natural_person.documento.add(document)
            else:
                document.data_expedicao = datetime.datetime.now()
                document.data_validade = None
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"uniao_estavel": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_doc_nis(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.nis
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("nis", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=NIS,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save()
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"nis": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_doc_reservist(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.reservist
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("reservista", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RESERVISTA,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=None,
                        natural_person=natural_person,
                    )
                    document.save()
                    document.clean()
                    natural_person.documento.add(document)
            elif number:
                document.numero = number
                document.save()
            elif document:
                document.delete()
                document = None

            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_reservist_class(document, querydict)[1]
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"reservista": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_reservist_class(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.reservist_class
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("classe_reservista", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RESERVISTA_CLASSE, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"classe_reservista": err}
            )
        return data_spec, obj

    @classmethod
    def _save_doc_professional_council(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.professional_council
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        try:
            number = querydict.get("professional_council")
            validity_date = None
            if querydict.get("professional_council_validity_date", None):
                validity_date = DateUtils.str_to_date(
                    querydict.get("professional_council_validity_date")
                )
            expedition_date = None
            if querydict.get("professional_council_expedition_date"):
                expedition_date = DateUtils.str_to_date(
                    querydict.get("professional_council_expedition_date")
                )
            state = querydict.get("professional_council_state", None)
            if state:
                state = Estado.objects.get(pk=int(state)) if state else None
            else:
                state = None

            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=PROFESSIONAL_COUNCIL,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=validity_date,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            elif number:
                document.numero = number
                document.data_expedicao = expedition_date
                document.data_validade = validity_date
                document.estado_expedicao = state
                document.save(validate_mandatory=False)
            elif document:
                document.delete()
                document = None

            RHEmployeeSpecialized._concat_obj(
                obj,
                RHEmployeeSpecialized._save_doc_professional_council_issuer(
                    document, querydict
                )[1],
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            self.log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"professional_council": err}
            )
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_doc_professional_council_issuer(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.professional_council_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("professional_council_issuer", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=PROFESSIONAL_COUNCIL_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"professional_council_issuer": err}
            )
        return data_spec, obj

    @classmethod
    def _save_doc_voter(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.voter
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)
        number = querydict.get("titulo_eleitor", None)
        city = querydict.get("municipio_titulo", None)
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=TITULO_ELEITOR,
                        numero=number,
                        data_expedicao=None,
                        data_validade=None,
                        estado_expedicao=(
                            Localidade.objects.get(pk=int(city)).estado
                            if city
                            else None
                        ),
                        natural_person=natural_person,
                    )
                    document.naturalperson = natural_person
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.save(validate_mandatory=False)

            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_voter_zone(document, querydict)[1]
            )
            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_voter_section(document, querydict)[1]
            )
            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_voter_city(document, querydict)[1]
            )

            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"titulo_eleitor": "Não foi possível salvar título eleitor!"}
            )
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_voter_zone(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.voter_zone
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("zona_titulo", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_ZONA, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"zona_titulo": err})
        return data_spec, obj

    @classmethod
    def _save_voter_section(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.voter_section
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("secao_titulo")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_SECAO, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"secao_titulo": err})
        return data_spec, obj

    @classmethod
    def _save_voter_city(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.voter_city
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("municipio_titulo")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=TITULO_ELEITOR_MUNICIPIO, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(
                obj, {"municipio_titulo": err}
            )
        return data_spec, obj

    @classmethod
    def _save_doc_ric(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.ric
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("ric", None)
        expedition_date = None
        if querydict.get("ric_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                querydict.get("ric_expedition_date")
            )
        state = querydict.get("ric_state", None)
        if state:
            state = Estado.objects.get(pk=querydict.get("ric_state"))
        else:
            state = None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RIC,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.estado_expedicao = state
                document.save(validate_mandatory=False)
            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_ric_issuer(document, querydict)[1]
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"ric": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_ric_issuer(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.ric_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("ric_issuer")
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RIC_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            self.log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"ric_issuer": err})
        return data_spec, obj

    @classmethod
    def _save_doc_rne(self, natural_person, querydict={}):
        obj = {"success": True, "errors": {}}
        document = natural_person.rne
        if document:
            document = DocumentSpecialized.objects.get(pk=document.pk)

        number = querydict.get("rne", None)
        expedition_date = None
        if querydict.get("rne_expedition_date"):
            expedition_date = DateUtils.str_to_date(
                querydict.get("rne_expedition_date")
            )
        state = None
        if state:
            state = Estado.objects.get(pk=querydict.get("rne_state", None))
        else:
            state = None
        try:
            if not document:
                if number:
                    document = DocumentSpecialized(
                        tipo_documento=RNE,
                        numero=number,
                        data_expedicao=expedition_date,
                        data_validade=None,
                        estado_expedicao=state,
                        natural_person=natural_person,
                    )
                    document.clean()
                    document.save(validate_mandatory=False)
                    natural_person.documento.add(document)
            else:
                document.numero = number
                document.data_expedicao = expedition_date
                document.estado_expedicao = state
                document.save(validate_mandatory=False)
            RHEmployeeSpecialized._concat_obj(
                obj, RHEmployeeSpecialized._save_rne_issuer(document, querydict)[1]
            )
            if document:
                document.clean()
                document.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"rne": err})
        except ValidationError as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, err)
        return document, obj

    @classmethod
    def _save_rne_issuer(self, document, querydict={}):
        obj = {"success": True, "errors": {}}
        data_spec = None
        if document:
            data_spec = document.rne_issuer
            if data_spec:
                data_spec = DocsDataSpecificSpecialized.objects.get(pk=data_spec.pk)

        value = querydict.get("rne_issuer", None)
        try:
            if not data_spec:
                if value:
                    data_spec = DocsDataSpecificSpecialized(
                        especificidade=RNE_ISSUER, valor=value
                    )
                    data_spec.save()
                    document.dados_especificos.add(data_spec)
            else:
                data_spec.valor = value
                data_spec.save()
        except Exception as err:
            log.exception(err)
            RHEmployeeSpecialized._concat_validation_error(obj, {"rne_issuer": err})
        return data_spec, obj


class RHExercisesMoreThanOne(RHEmployeeWorkplaceRestful):

    full_text_index = () + RHEmployeeWorkplaceRestful.full_text_index

    exclude_fields = [] + RHEmployeeWorkplaceRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + RHEmployeeWorkplaceRestful.force_persist_boolean_fields
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.employee.workplace.exercisesmorethanone.Manager")'
        )

    def get_query(self):
        query = super(RHExercisesMoreThanOne, self).get_query()
        pks = []
        for workplace in Lotacao.objects.filter(
            servidores_lotacao__ativo=True,
            servidores_lotacao__designacao=True,
            servidores_lotacao__servidor__tipo="M",
        ).annotate(Count("servidores_lotacao")):
            if workplace.servidores_lotacao__count > 1:
                pks += [
                    emp.get("pk")
                    for emp in workplace.servidores_lotacao.filter(
                        ativo=True, designacao=True, servidor__tipo="M"
                    ).values("pk")
                ]
        return query.filter(pk__in=pks)


class RHRelationship(RestfulDRY):
    _model = Relationship

    full_text_index = (
        "giver__matricula__icontains",
        "receiver__matricula__icontains",
        "workplace__nome__icontains",
        "app__icontains",
    )

    exclude_fields = [
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
    ]

    force_persist_field_boolean = True

    def receivers(self, *args):
        obj = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "count": 0,
            "collection": [],
        }

        try:
            employee = employee_from_user(get_current_user())
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e.args[0]))
        else:
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=Servidor.objects.filter(chefe_imediato=employee).count(),
                collection=[
                    {"pk": s.pk, "description": s}
                    for s in Servidor.objects.filter(chefe_imediato=employee)
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def workplacesResponsible(self, *args):
        obj = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "count": 0,
            "collection": [],
        }

        giver_pk = self.request.POST.get("giver", None)
        employee = None

        try:
            employee = (
                Servidor.objects.get(pk=int(self.request.POST.get("giver")))
                if giver_pk
                else employee_from_user(get_current_user())
            )
        except Exception as e:
            log.exception(e)
            obj.update(message="{}".format(e.args[0]))
        else:
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=Lotacao.objects.filter(responsavel=employee).count(),
                collection=[
                    {"pk": lot.pk, "description": "%s" % lot}
                    for lot in Lotacao.objects.filter(responsavel=employee)
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def get_query(self):
        queryset = super(RHRelationship, self).get_query()

        queryset = Relationship.objects.filter(
            Q(giver=self.request.user.servidor)
            | Q(
                workplace__in=Lotacao.objects.filter(
                    responsavel=employee_from_user(get_current_user())
                )
            )
        )

        return queryset

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.employee.relationship.Manager")')


class RHRelationshipAdmin(RHRelationship):
    def get_query(self):
        queryset = super(RHRelationship, self).get_query()

        return queryset

    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render('Ext._create("rh.employee.relationship.Admin.Manager")')
