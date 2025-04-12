# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils
from rh.afastamento.api.baselicencaafastamento import AFABaseLicencaAfastamentoRestful
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
import json


log = getLogger(__name__)


class AFAManagerRestful(AFABaseLicencaAfastamentoRestful):

    full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    force_persist_boolean_fields = (
        [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields
    )

    def _get_user_department_perm(self):
        department = "rh"
        if (
            get_current_user().has_perm("afastamento.ver_membros")
            and get_current_user().has_perm("afastamento.ver_servidores") is False
        ):
            department = "expediente"

        log.debug("department %s" % department)
        return department

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('rh.afastamento.Manager', {department:'%s'})"
            % self._get_user_department_perm()
        )

    def _define_employee_type(self, employee_type):
        if (
            not get_current_user().has_perm("afastamento.ver_membros")
            and "M" in employee_type
        ):
            employee_type.remove("M")
        if (
            not get_current_user().has_perm("afastamento.ver_servidores")
            and "S" in employee_type
        ):
            employee_type.remove("S")
        # return employee_type

        lista_type_by_possessions = []

        if "M" in employee_type:
            lista_type_by_possessions.append("MBR")
            lista_type_by_possessions.append("MEL")
            lista_type_by_possessions.append("MCM")
            lista_type_by_possessions.append("MEC")
            lista_type_by_possessions.append("MBR2")
            lista_type_by_possessions.append("MEL2")
            lista_type_by_possessions.append("MCM2")
            lista_type_by_possessions.append("MEC2")
        if "S" in employee_type:
            lista_type_by_possessions.append("EFE")
            lista_type_by_possessions.append("ECM")
            lista_type_by_possessions.append("CMS")
            lista_type_by_possessions.append("REQ")
            lista_type_by_possessions.append("RCM")
            lista_type_by_possessions.append("CTR")
            lista_type_by_possessions.append("RFC")
            lista_type_by_possessions.append("EFC")
            lista_type_by_possessions.append("REX")
        if "T" in employee_type:
            lista_type_by_possessions.append("TCR")
        if "E" in employee_type:
            lista_type_by_possessions.append("EST")
        if "V" in employee_type:
            lista_type_by_possessions.append("VOL")
        if "R" in employee_type:
            lista_type_by_possessions.append("RES")

        log.info(lista_type_by_possessions)
        return lista_type_by_possessions

    def _make_query(self, query):
        employee_type = []
        situation = []
        change = []
        type_class = []
        pk = None
        try:
            flist = json.loads(self.get_params().get("filter", "[]"))
            for item in flist:
                if item.get("property") == "servidor__tipo__in":
                    employee_type = item.get("value")
                if item.get("property") == "estado__in":
                    situation = item.get("value")
                if item.get("property") == "alteracao__in":
                    change = item.get("value")
                if item.get("property") == "tipo__in":
                    type_class = item.get("value")
                elif item.get("property") == "pk":
                    pk = item.get("value")
        except Exception as err:
            raise Exception(
                "Error tratando as chaves de parametros %s não foi encontrada" % err
            )
        employee_type = self._define_employee_type(employee_type)
        query = query.filter(servidor__type_by_possession__in=employee_type)
        query = query.filter(estado__in=situation)
        query = query.filter(tipo__in=type_class)
        if len(change) > 0:
            query = query.filter(alteracao__in=change)
        return query

    def get_query(self):
        query = super(AFAManagerRestful, self).get_query()
        return self._make_query(query).order_by("-data_inicio")

    def model_to_dict(self, instance):
        _dict_ = super(AFAManagerRestful, self).model_to_dict(instance)
        _dict_.update({"employee_type": instance.servidor.tipo})
        _dict_.update({"employee_registry": instance.servidor.matricula})
        _dict_.update({"employee_pk": instance.servidor.pk})
        _dict_.update({"employee_cpf": instance.servidor.pessoa_fisica.cpf})
        return _dict_

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

            status = []
            scheduled = record.pending_period
            days = record.pending_period_days
            if not scheduled and days == float("-inf"):
                days = "Período com data fim não definida."
            status.append(
                "Possui Substituição/Inativação"
                if scheduled
                else ("Substituição/Inativação período pendente: %s" % days)
            )
            for substitution in record.substituicao.filter():
                if not substitution.designation_substituted:
                    status.append(
                        "Designação de servidor substituído não encontrado %s"
                        % substitution.servidor_substituido
                    )
                    break
                if (
                    substitution.substituicao_finalizada() or substitution.is_active()
                ) and not substitution.designation_substitute:
                    status.append(
                        "Designação de servidor substituto não encontrado %s"
                        % (substitution.servidor)
                    )
                    break
                if (
                    substitution.substituicao_finalizada()
                    and substitution.designation_substitute
                    and not substitution.designation_substitute.is_finished()
                ):
                    status.append(
                        "Designação de servidor substituto não finalizada %s"
                        % (substitution.designation_substitute)
                    )
                    break

            rst.append(
                {
                    "Status": ", ".join(status),
                    "eSocial": (
                        "SIM"
                        if record.event_esocial and record.event_esocial != 0
                        else "NÂO"
                    ),
                    "Servidor": record.servidor,
                    "Situação": record.get_estado_display() or "",
                    "Motivo": record.get_motivo_display() or "",
                    "Tipo de alteração": record.get_alteracao_display() or "",
                    "Início ": DateUtils.date_to_str(record.data_inicio),
                    "Prevista Fim": DateUtils.date_to_str(record.data_prevista),
                    "Fim": DateUtils.date_to_str(record.data_fim),
                    "Criado por": record.created_by,
                    "Criado em": DateUtils.date_to_str(record.created_at),
                    "Modificado por": record.modified_by,
                    "Modificado em": DateUtils.date_to_str(record.modified_at),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class AFACouncilManagerRestful(AFAManagerRestful):

    # full_text_index = () + AFABaseLicencaAfastamentoRestful.full_text_index

    # exclude_fields = [] + AFABaseLicencaAfastamentoRestful.exclude_fields

    # force_persist_boolean_fields = [] + AFABaseLicencaAfastamentoRestful.force_persist_boolean_fields

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('rh.afastamento.council.Manage', {department:'%s'})"
            % self._get_user_department_perm()
        )


class AFAManagerEmployeeRestful(AFAManagerRestful):

    full_text_index = () + AFAManagerRestful.full_text_index

    exclude_fields = [] + AFAManagerRestful.exclude_fields

    force_persist_boolean_fields = [] + AFAManagerRestful.force_persist_boolean_fields

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('rh.afastamento.ManagerEmployee', {department:'%s'})"
            % self._get_user_department_perm()
        )

    def _define_employee_type(self, employee_type):
        return [employee_from_user(get_current_user()).tipo]

    def get_query(self):
        query = (
            super(AFAManagerRestful, self)
            .get_query()
            .filter(servidor__pk=employee_from_user(get_current_user()).pk)
        )
        return self._make_query(query).order_by("-data_inicio")
