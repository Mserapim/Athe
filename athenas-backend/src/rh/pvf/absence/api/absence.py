# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required
import json
from rh.pvf.absence.models import (
    BloodDonationAbsence,
    FamilyHealthTreatmentAbsence,
    HealthTreatmentAbsence,
    MarriageAbsence,
    MaternityAbsence,
    MourningAbsence,
    PaternityAbsence,
    PoliticalActivityAbsence,
    PrivateInterestAbsence,
    TrainingAbsence,
)
from standard.models import Choice


log = getLogger(__name__)


class PVFAbsence(RestfulDRY):

    def extract_params(self, params, signature=[]):
        params_new = {}
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                except:
                    params_new.update({key: params[key]})
        return params_new


class PVFFamilyHealthTreatmentAbsence(PVFAbsence):

    _model = FamilyHealthTreatmentAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.pvf.absence.familyhealthtreatment.Manage")'
        )

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "medical_certificate": self.request.POST.get("medical_certificate"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "person": self.request.POST.get("person"),
                "degree_kinship": self.request.POST.get("degree_kinship"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
                "days": self.request.POST.get("days"),
                "cid": self.request.POST.get("cid"),
            }
        )

        try:
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
                FamilyHealthTreatmentAbsence.create_family_health(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFHealthTreatmentAbsence(PVFAbsence):

    _model = HealthTreatmentAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.healthtreatment.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "employee": self.request.POST.get("employee"),
                "end_date": self.request.POST.get("end_date"),
                "medical_certificate": self.request.POST.get("medical_certificate"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
                "days": self.request.POST.get("days", 0),
                "hours": (
                    0
                    if not self.request.POST.get("hours", 0)
                    else self.request.POST.get("hours", 0)
                ),
                "cid": self.request.POST.get("cid", None),
            }
        )

        try:
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
                HealthTreatmentAbsence.create_leave_health(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFMarriageAbsence(PVFAbsence):

    _model = MarriageAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.marriage.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "marriage_certificate": self.request.POST.get("marriage_certificate"),
                "person": self.request.POST.get("person"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                MarriageAbsence.create_marriage(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFMaternityAbsence(PVFAbsence):

    _model = MaternityAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.maternity.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        dependent_type = ""
        is_incoming_tax = False

        if self.request.POST.get("dependent_type"):
            dependent_type = Choice.objects.get(
                name="DEPENDENT_TYPE",
                app_label="rh",
                label=self.request.POST.get("dependent_type"),
            ).value

        if self.request.POST.get("is_incoming_tax") == "true":
            is_incoming_tax = True

        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "dependent": self.request.POST.get("dependent"),
                "birth_certificate": self.request.POST.get("birth_certificate"),
                "is_childcare_assistence": self.request.POST.get(
                    "is_childcare_assistence"
                ),
                "is_incoming_tax": is_incoming_tax,
                "dependent_type": dependent_type,
                "capacity": self.request.POST.get("capacity"),
                "incapacity": self.request.POST.get("incapacity"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                MaternityAbsence.create_maternity(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFMourningAbsence(PVFAbsence):

    _model = MourningAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.mourning.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "death_certificate": self.request.POST.get("death_certificate"),
                "family_bond": self.request.POST.get("family_bond"),
                "person": self.request.POST.get("person"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                MourningAbsence.create_mourning(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFPaternityAbsence(PVFAbsence):

    _model = PaternityAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.paternity.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        dependent_type = ""
        is_incoming_tax = False

        if self.request.POST.get("dependent_type"):
            dependent_type = Choice.objects.get(
                name="DEPENDENT_TYPE",
                app_label="rh",
                label=self.request.POST.get("dependent_type"),
            ).value

        if self.request.POST.get("is_incoming_tax") == "true":
            is_incoming_tax = True

        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "dependent": self.request.POST.get("dependent"),
                "birth_certificate": self.request.POST.get("birth_certificate"),
                "is_childcare_assistence": self.request.POST.get(
                    "is_childcare_assistence"
                ),
                "is_incoming_tax": is_incoming_tax,
                "dependent_type": dependent_type,
                "capacity": self.request.POST.get("capacity"),
                "incapacity": self.request.POST.get("incapacity"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                PaternityAbsence.create_paternity(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFPoliticalActivityAbsence(PVFAbsence):

    _model = PoliticalActivityAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.politicalactivity.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "location": self.request.POST.get("location"),
                "elective_office": self.request.POST.get("elective_office"),
                "political_party": self.request.POST.get("political_party"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                PoliticalActivityAbsence.create_political_activity(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFPrivateInterestAbsence(PVFAbsence):

    _model = PrivateInterestAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.privateinterest.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                PrivateInterestAbsence.create_private_interest(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFTrainingAbsence(PVFAbsence):

    _model = TrainingAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.training.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "end_date": self.request.POST.get("end_date"),
                "observation": self.request.POST.get("observation"),
                "institution": self.request.POST.get("institution"),
                "curse": self.request.POST.get("curse"),
                "start_date": self.request.POST.get("start_date"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                TrainingAbsence.create_training(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class PVFBloodDonationAbsence(PVFAbsence):
    _model = BloodDonationAbsence

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.absence.blood_donation.Manage")')

    @login_required("JSON")
    def save(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        params = {}
        params.update(
            {
                "blood_donation_certificate": self.request.POST.get(
                    "blood_donation_certificate"
                ),
                "observation": self.request.POST.get("observation"),
                "start_date": self.request.POST.get("start_date"),
                "days": self.request.POST.get("days"),
                "substitutes": self.extract_params(self.request.POST, ["substitutes"]),
            }
        )

        try:
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
                self._model.create_absence(params)
                rst.update(
                    {
                        "success": True,
                        "message": "Registro Criado com Sucesso",
                    }
                )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
