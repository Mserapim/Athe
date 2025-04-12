from rest_framework.serializers import ModelSerializer
from rh.afastamento.models import CID, CIDCode
from rh.pvf.models import PortalRequestAbsence
from rh.pvf.absence.models import (
    HealthTreatmentAbsence,
    FamilyHealthTreatmentAbsence,
    MaternityAbsence,
    PaternityAbsence,
    MourningAbsence,
    MarriageAbsence,
    BloodDonationAbsence,
)
from contrib.utils import getLogger
from contrib.daterange import NewDateRange
from datetime import datetime
from rh.pvf.apiv2.utils.base import formart_date_str, cria_solicitacao_aux_creche_ir
from rh.pvf.const import *
import json

log = getLogger(__name__)


class PVFRequestAbsenceSerializer(ModelSerializer):
    """
    Classe serializer base para criação da solicitação de afastamentos
    """

    portal_request_type = None

    class Meta:
        model = PortalRequestAbsence
        fields = ["type_of_request", "date", "employee_name", "approver", "status_name"]

    def extract_params(self, params, signature=[]):
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

    def get_days(self, data):
        if data.get("start_date") and data.get("end_date"):
            format = "%Y-%m-%dT%H:%M:%S.%f"
            date_str_s = data.get("start_date").replace("Z", "")
            date_str_e = data.get("end_date").replace("Z", "")
            start_date = datetime.strptime(date_str_s, format).date()
            end_date = datetime.strptime(date_str_e, format).date()
            return NewDateRange(start_date, end_date).days
        return None

    def return_success_instance(self, instance):
        return {
            "success": True,
            "message": "Registro criado com sucesso",
            "data": {
                "pk": instance.pk,
                "type_of_request": instance.type_of_request,
                "date": instance.date,
                "employee_name": instance.employee_name,
                "approver": instance.set_custom_approver,
                "status_name": instance.status_name,
                "criar_solicitacao_creche_ir": cria_solicitacao_aux_creche_ir(instance),
            },
        }


class PVFPreValidacaoAfastamentoSerializador(PVFRequestAbsenceSerializer):
    """
    Classe serializer da pré validação de afastamentos
    """

    class Meta:
        model = PortalRequestAbsence
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
                }
            )
            instancia = PortalRequestAbsence()
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


class CIDCodeSerializer(ModelSerializer):
    class Meta:
        model = CIDCode
        fields = ["code"]


class CIDSerializer(ModelSerializer):
    cid_code = CIDCodeSerializer(many=True)

    class Meta:
        model = CID
        fields = ["chapter", "code", "description", "cid_code"]


class PVFHealthTreatmentAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para crição de afastamento de licença para tratamento de saúde
    """

    cid = CIDSerializer()

    class Meta:
        model = HealthTreatmentAbsence
        fields = [
            "medical_certificate",
            "start_date",
            "end_date",
            "days",
            "hours",
            "cid",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            days = self.get_days(data)
            hours = data.get("hours", 0)
            start_date = formart_date_str(data.get("start_date"))
            end_date = (
                formart_date_str(data.get("end_date")) if not hours else start_date
            )
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days,
                    "medical_certificate": data.get("medical_certificate"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                    "hours": hours,
                    "cid": data.get("cid"),
                }
            )
            instance = self.Meta.model.create_leave_health(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFHealtFamiliyDeseaseSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de afastamento para licença em doença em pessoa da família
    """

    cid = CIDSerializer()

    class Meta:
        model = FamilyHealthTreatmentAbsence
        fields = [
            "medical_certificate",
            "person",
            "person_name",
            "degree_kinship",
            "degree_kinship_label",
            "start_date",
            "end_date",
            "days",
            "cid",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            days = self.get_days(data)
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days,
                    "person": data.get("person"),
                    "degree_kinship": data.get("degree_kinship"),
                    "cid": data.get("cid"),
                    "medical_certificate": data.get("medical_certificate"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                }
            )
            instance = self.Meta.model.create_family_health(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFMaternityAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de afastamento de licença maternidade
    """

    class Meta:
        model = MaternityAbsence
        fields = [
            "birth_certificate",
            "dependent",
            "dependent_name",
            "is_childcare_assistence",
            "is_incoming_tax",
            "capacity",
            "capacity_label",
            "incapacity",
            "dependent_type",
            "dependent_type_label",
            "start_date",
            "end_date",
            "days",
            "classificacao",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "dependent": data.get("dependent"),
                    "dependent_type": data.get("dependent_type"),
                    "birth_certificate": data.get("birth_certificate"),
                    "is_childcare_assistence": data.get("is_childcare_assistence"),
                    "capacity": data.get("capacity"),
                    "incapacity": data.get("incapacity"),
                    "is_incoming_tax": data.get("is_incoming_tax"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                    "classificacao": data.get("classificacao"),
                }
            )
            instance = self.Meta.model.create_maternity(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFBirthAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de afastamento de licença parternidade
    """

    class Meta:
        model = PaternityAbsence
        fields = [
            "birth_certificate",
            "dependent",
            "dependent_name",
            "is_childcare_assistence",
            "is_incoming_tax",
            "capacity",
            "capacity_label",
            "incapacity",
            "dependent_type",
            "dependent_type_label",
            "start_date",
            "end_date",
            "days",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "dependent": data.get("dependent"),
                    "dependent_type": data.get("dependent_type"),
                    "birth_certificate": data.get("birth_certificate"),
                    "is_childcare_assistence": data.get("is_childcare_assistence"),
                    "capacity": data.get("capacity"),
                    "incapacity": data.get("incapacity"),
                    "is_incoming_tax": data.get("is_incoming_tax"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                }
            )
            instance = self.Meta.model.create_paternity(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFDeathAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de afastamento de licença luto
    """

    class Meta:
        model = MourningAbsence
        fields = [
            "death_certificate",
            "family_bond",
            "family_bond_label",
            "person",
            "person_name",
            "start_date",
            "end_date",
            "days",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "person": data.get("person"),
                    "family_bond": data.get("family_bond"),
                    "death_certificate": data.get("death_certificate"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                }
            )
            instance = self.Meta.model.create_mourning(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFMarriageAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de afastamento de licença luto
    """

    class Meta:
        model = MarriageAbsence
        fields = [
            "marriage_certificate",
            "person",
            "person_name",
            "start_date",
            "end_date",
            "days",
        ]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "person": data.get("person"),
                    "marriage_certificate": data.get("marriage_certificate"),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                }
            )
            instance = self.Meta.model.create_marriage(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst


class PVFBloodDonationAbsenceSerializer(PVFRequestAbsenceSerializer):
    """
    Classe serializer para criação de ausência por doação de sangue
    """

    class Meta:
        model = BloodDonationAbsence
        fields = ["blood_donation_certificate", "start_date", "end_date", "days"]

    def create(self, data):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        params = {}
        try:
            days = self.get_days(data)
            start_date = formart_date_str(data.get("start_date"))
            end_date = formart_date_str(data.get("end_date"))
            params.update(
                {
                    "days": days,
                    "start_date": start_date,
                    "end_date": end_date,
                    "blood_donation_certificate": data.get(
                        "blood_donation_certificate"
                    ),
                    "substitutes": self.extract_params(data, ["substitutes"]),
                    "observation": data.get("observation"),
                }
            )
            instance = self.Meta.model.create_absence(params)
            rst.update(self.return_success_instance(instance))

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        return rst
