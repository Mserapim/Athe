from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from rh.pvf.models import (
    PVFRegularVacation,
    PVFSolicitacaoEstagiario,
    PVFSolicitacaoResidente,
    PortalRequestUsufruct,
    PVFIndividualVacation,
    PVFElectoralSlack,
    PVFForensicRecess,
    PVFServerShift,
    PVFIntershipCompetition,
    PVFCompClearanceMembers,
    PVFCompVactionMembers,
    PVFSubstitutePromoterContest,
    PVFBloodDonation,
)
from contrib.utils import getLogger
from rh.pvf.const import *
from rest_framework import serializers
from rh.dayoff.models import AcquisitionPeriod, Usufruct
from datetime import datetime
from rh.pvf.apiv2.utils.base import formart_date_str
import json

log = getLogger(__name__)


class PVFAcquisitionPeriodSerializer(ModelSerializer):
    """
    classe serializer dos períodos aquisitivos das solicitações de usufrutos
    """

    group_period_unicode = serializers.CharField(source="get_texto_group_period")
    saldo_venda = serializers.IntegerField(source="get_saldo_venda")
    data_corte_venda = serializers.DateField(source="get_data_corte_venda")
    saldo_agendado_vendido = serializers.SerializerMethodField()
    total_venda_anexo = serializers.IntegerField(source="get_total_venda_anexo")

    class Meta:
        model = AcquisitionPeriod
        fields = [
            "pk",
            "group_period",
            "group_period_name",
            "status",
            "status_name",
            "days",
            "sale_usufruct",
            "balance_available",
            "start_date_acquisition",
            "end_date_acquisition",
            "start_date_fruition",
            "group_period_unicode",
            "saldo_venda",
            "data_corte_venda",
            "saldo_agendado_vendido",
            "total_venda_anexo",
        ]

    def get_saldo_agendado_vendido(self, obj):
        return obj.booked_days_cache + obj.paid_days_cache


class PVFUsufructSerializer(ModelSerializer):
    """
    classe serializer dos usufrutos marcados
    """

    class Meta:
        model = Usufruct
        fields = [
            "pk",
            "start_date",
            "end_date",
            "days",
            "type_usufruct",
            "payment_competence",
            "payment_installments",
            "numero_parcela",
        ]

    def payment(self, params):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            usufruct_pk = params.get("pk", None)
            competence = params.get("payment_competence", None)
            qtd_parcel = str(params.get("payment_installments", ""))
            usufruct = Usufruct.objects.filter(pk=usufruct_pk).first()

            try:
                competence_list = competence.split("/", 1)
            except Exception as e:
                log.error(e)

            if (
                usufruct
                and not usufruct.start_date
                and qtd_parcel.isdigit()
                and qtd_parcel not in [item[0] for item in Usufruct.INSTALLMENTS_CHOICE]
            ):
                rst["message"] = (
                    "A quantidade de parcelas deve ser um número entre 1 a 99"
                )

            if competence and (
                (
                    not competence_list[0].isdigit()
                    or int(competence_list[0])
                    not in [item[0] for item in Usufruct.MONTH_CHOICE]
                )
                or (
                    not competence_list[1].isdigit()
                    or int(competence_list[1])
                    not in [item[0] for item in Usufruct.YEAR_CHOICES]
                )
            ):
                rst["message"] = "A competência deve ser informado no formato MM/AAAA"

            elif usufruct.payments.exists():
                rst["message"] = (
                    "Não é permitido alterar Data de Pagamento de usufruto/venda vinculado a um pagamento da folha."
                )
            else:
                month = None
                year = None
                parcels = None
                if competence:
                    month = int(competence_list[0])
                    year = int(competence_list[1])
                if qtd_parcel:
                    parcels = int(qtd_parcel)
                if usufruct:
                    try:
                        usufruct.payment_month = month
                        usufruct.payment_year = year
                        usufruct.payment_installments = parcels
                        usufruct.save_base()
                    except Exception as e:
                        log.error(e)
                        rst["message"] = f"Falha ao salvar pagamento do usufruto {e}"

                    rst = {"success": True, "message": "Pagamento salvo com sucesso"}

                else:
                    rst["message"] = "Usufruto não localizado"
        except Exception as err:
            log.error(err)
            rst.update({"message": str(err)})

        return rst


class PVFVacationConfigSerializer(Serializer):
    """
    classe serializer das combinações de férias das solicitações de usufrutos
    """

    type_usufruct = serializers.IntegerField()
    total_days = serializers.IntegerField()
    options = serializers.ListField()


class PVFRequestUsufructSerializer(ModelSerializer):
    """
    Classe serializer base para criação dos usufrutos
    """

    portal_request_type = None
    sub_type_usufruct = None

    class Meta:
        model = PortalRequestUsufruct
        fields = [
            "pk",
            "type_of_request",
            "date",
            "employee_name",
            "approver_name",
            "status_name",
            "get_parcel_number",
            "acquisitive_period",
        ]

    def extract_params_usufruct(self, params, signature=[], portal_request_type=None):
        params_new = {}
        parcel_number = None
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(
                            values.get("start_date")
                        )
                        values["end_date"] = formart_date_str(values["end_date"])
                        if values["start_date"] is None:
                            values.pop("start_date", None)
                        if values["end_date"] is None:
                            values.pop("end_date", None)
                        values["days"] = int(values["days"])
                        values["sale_usufruct"] = int(values["sale_usufruct"])

                        if portal_request_type == 2:  # Férias Individuais(Membros)
                            if (
                                "parcel_number" in values
                                and values["parcel_number"] != None
                            ):
                                parcel_number = int(values["parcel_number"])

                except:
                    params_new.update({key: params[key]})
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(
                            values.get("start_date")
                        )
                        values["end_date"] = formart_date_str(values["end_date"])
                        if values["start_date"] is None:
                            values.pop("start_date", None)
                        if values["end_date"] is None:
                            values.pop("end_date", None)
                        values["sale_usufruct"] = int(values["sale_usufruct"])
                        values["days"] = int(values["days"])
                        if portal_request_type == 2:  # Férias Individuais(Membros)
                            if (
                                "parcel_number" in values
                                and values["parcel_number"] != None
                            ):
                                parcel_number = int(values["parcel_number"])

        return params_new, parcel_number

    def extract_params_substitute(self, params, signature=[]):
        params_new = {}
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(values["start_date"])
                        values["end_date"] = formart_date_str(values["end_date"])

                except:
                    params_new.update({key: params[key]})
                    for values in params_new[key]:
                        values["start_date"] = formart_date_str(values["start_date"])
                        values["end_date"] = formart_date_str(values["end_date"])

        return params_new

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            (
                [item.pop("parcel_number", None) for item in data["usufructs_in"]]
                if self.portal_request_type != 2
                else data
            )
            usufruct_params, parcel_number = self.extract_params_usufruct(
                data, ["usufructs_in"], self.portal_request_type
            )
            subsitute_params = self.extract_params_substitute(data, ["substitutes"])
            params.update(
                {
                    "usufructs_in": usufruct_params,
                    "observation": data.get("observation"),
                    "type_usufruct": self.sub_type_usufruct,
                    "substitutes": subsitute_params,
                    "parcel_number": parcel_number,
                }
            )
            instance = self.Meta.model.create_request_usufruct(
                params, self.portal_request_type
            )
            rst.update(
                {
                    "success": True,
                    "message": "Registro criado com sucesso",
                    "data": {
                        "pk": instance.pk,
                        "type_of_request": instance.type_of_request,
                        "date": instance.date,
                        "employee_name": instance.employee_name,
                        "approver": instance.set_custom_approver,
                        "status_name": instance.status_name,
                        "parcel_number": instance.get_parcel_number,
                        "acquisitive_period": instance.acquisitive_period,
                    },
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFPreValidacaoUsufrutoSerializador(PVFRequestUsufructSerializer):
    """
    Classe serializer da pré validação de usufrutos
    """

    class Meta:
        model = PortalRequestUsufruct
        fields = []

    def pre_validacao(self, dados):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            data_inicio = formart_date_str(dados.get("start_date"))
            data_fim = formart_date_str(dados.get("end_date"))
            params.update(
                {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "tipo_usufruto": dados.get("type_usufruct"),
                }
            )
            instancia = PortalRequestUsufruct()
            instancia.pre_validacao(params)
            rst.update(
                {
                    "success": True,
                    "message": "Dados validado com sucesso",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        return rst


class PVFRegularVacationSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de férias regulamentares
    """

    portal_request_type = PORTAL_REGULAR_VACATION_TYPE
    sub_type_usufruct = REGULAR_VACATIONS

    class Meta:
        model = PVFRegularVacation
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFIndividualVacationSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de férias individuais
    """

    portal_request_type = PORTAL_INDIVIDUAL_VACATION_TYPE
    sub_type_usufruct = INDIVIDUAL_VACATION

    class Meta:
        model = PVFIndividualVacation
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFElectoralSlackSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de folga eleitoral
    """

    portal_request_type = PORTAL_ELECTORAL_SLACK_TYPE
    sub_type_usufruct = ELECTORAL_SLACK

    class Meta:
        model = PVFElectoralSlack
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFForensicRecessSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de recesso forense
    """

    portal_request_type = PORTAL_FORENSIC_RECESS_TYPE
    sub_type_usufruct = FORENSIC_RECESS

    class Meta:
        model = PVFForensicRecess
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFServerShiftSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de plantão servidores
    """

    portal_request_type = PORTAL_SERVER_SHIFT_TYPE
    sub_type_usufruct = ONCALL_BONUS_SERVERS

    class Meta:
        model = PVFServerShift
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFIntershipCompetitionSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de concurso de estagiário
    """

    portal_request_type = PORTAL_INTERNSHIP_COMPETITION_TYPE
    sub_type_usufruct = INTERNSHIP_COMPETITION

    class Meta:
        model = PVFIntershipCompetition
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFCompClearanceMembersSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de folgas compensatória de membros
    """

    portal_request_type = PORTAL_COMP_CLEARANCE_MEMBERS_TYPE
    sub_type_usufruct = COMP_CLEARANCE_MEMBERS

    class Meta:
        model = PVFCompClearanceMembers
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFCompVactionMembersSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de recesso forense de membros
    """

    portal_request_type = PORTAL_COMP_VACATION_MEMBERS_TYPE
    sub_type_usufruct = COMP_VACATION_MEMBERS

    class Meta:
        model = PVFCompVactionMembers
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFSubstitutePromoterContestSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de concurso de promotor substituto
    """

    portal_request_type = PORTAL_SUBSTITUTE_PROMOTER_CONTEST_TYPE
    sub_type_usufruct = SUBSTITUTE_PROMOTER_CONTEST

    class Meta:
        model = PVFSubstitutePromoterContest
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFBloodDonationtSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de concurso de promotor substituto
    """

    portal_request_type = PORTAL_BLOOD_DONATION_TYPE
    sub_type_usufruct = BLOOD_DONATION_USUFRUCT

    class Meta:
        model = PVFBloodDonation
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFSolicitacaoEstagiarioSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de recesso de estagiário
    """

    portal_request_type = PORTAL_INTERNS_RECESS_TYPE
    sub_type_usufruct = INTERNS_RECESS

    class Meta:
        model = PVFSolicitacaoEstagiario
        fields = PVFRequestUsufructSerializer.Meta.fields


class PVFSolicitacaoResidenteSerializer(PVFRequestUsufructSerializer):
    """
    Classe serializer para crição de usufruto de recesso de residente
    """

    portal_request_type = PORTAL_RESIDENTS_RECESS_TYPE
    sub_type_usufruct = RESIDENTS_RECESS

    class Meta:
        model = PVFSolicitacaoResidente
        fields = PVFRequestUsufructSerializer.Meta.fields
