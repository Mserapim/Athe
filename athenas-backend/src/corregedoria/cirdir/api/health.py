# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from contrib.nil import nil_pk, nil_unicode
from corregedoria.cirdir.models import Health
from standard.models import Choice

log = getLogger(__name__)


class CIRDIRHealth(RestfulDRY):

    force_upper = False

    full_text_index = [
        "controlinformation__employee__pessoa_fisica__nome__icontains",
    ]

    _model = Health

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.health.healtharea.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRHealth, self).model_to_dict(instance)
        _dict_.update(
            {
                "unicode": str(instance),
                "icons": instance.icons,
                "authorization_health": instance.controlinformation.authorization_health,
                "evaluate_unicode": instance.created_at.strftime("%Y%m%d%H%M%S%s"),
                "has_recommendation_pending": instance.has_recommendation_pending_confirmation,
                "integrant_unicode": nil_unicode(
                    instance.controlinformation.employee, None
                ),
                "integrant": nil_pk(instance.controlinformation.employee, None),
            }
        )
        return _dict_

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:

            full = self.request.GET.get("full", 0)
            instance = Health.objects.get(pk=self.request.GET.get("pk"))

        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                content=instance.rendered_evaluation if full else instance.rendered,
            )
        self.renderer(rst)

    def rendered_evaluation(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "content": "Sem informações",
        }
        try:

            health = Health.objects.get(pk=self.request.GET.get("pk"))
        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))
        else:

            rst.update(success=True, content=health.rendered_evaluation)
        self.renderer(rst)

    def get_arrayparams(self, params, name, choicefield=None):
        ret = []
        radioitem = params.get(name)
        if radioitem:
            ret.append(int(radioitem))
        else:
            for n in Choice.objects.filter(app_label="cirdir_health", name=choicefield):
                checkitem = params.get(name + str(n.value))
                if checkitem:
                    ret.append(int(checkitem))
        return ",".join(str(e) for e in ret)

    def save(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            params = self.request.POST
            health_pk = int(params.get("health_pk", 0) or 0)
            controlinformation = params.get("controlinformation")
            physical_exam_blood_pressure = params.get("physical_exam_blood_pressure")
            physical_exam_imc = params.get("physical_exam_imc")
            physical_exam_abdominal_circumference = params.get(
                "physical_exam_abdominal_circumference"
            )
            physical_exam_pulse = params.get("physical_exam_pulse")
            physical_exam_other = params.get("physical_exam_other")
            ingestion_candy = self.get_arrayparams(params, "ingestion_candy")
            ingestion_pasta = self.get_arrayparams(params, "ingestion_pasta")
            ingestion_fruit = self.get_arrayparams(params, "ingestion_fruit")
            ingestion_vegetable = self.get_arrayparams(params, "ingestion_vegetable")
            ingestion_beef = self.get_arrayparams(params, "ingestion_beef")
            ingestion_fry = self.get_arrayparams(params, "ingestion_fry")
            ingestion_supplement = self.get_arrayparams(params, "ingestion_supplement")
            family_health_problems = self.get_arrayparams(
                params, "family_health_problems", "HEALTH_PROBLEMS"
            )
            family_health_problems_other = params.get("family_health_problems_other")
            health_problems = self.get_arrayparams(
                params, "health_problems", "HEALTH_PROBLEMS"
            )
            health_problems_other = params.get("health_problems_other")
            life_habits = self.get_arrayparams(params, "life_habits", "LIFE_HABITS")
            life_habits_other = params.get("life_habits_other")
            immunization = self.get_arrayparams(params, "immunization")
            medicament = self.get_arrayparams(params, "medicament", "MEDICAMENT")
            medicament_other = params.get("medicament_other")
            physical_activity = self.get_arrayparams(params, "physical_activity")
            has_pain = self.get_arrayparams(params, "has_pain")
            local_pain = self.get_arrayparams(params, "local_pain", "LOCAL_PAIN")
            local_pain_other = params.get("local_pain_other")

            strength_at_work = self.get_arrayparams(
                params, "strength_at_work", "FREQUENCY"
            )

            work_chair_seat_adjustment = self.get_arrayparams(
                params, "work_chair_seat_adjustment"
            )
            work_chair_height_adjustment = self.get_arrayparams(
                params, "work_chair_height_adjustment"
            )
            work_chair_tilt_adjustment = self.get_arrayparams(
                params, "work_chair_tilt_adjustment"
            )
            work_chair_has_rod = self.get_arrayparams(params, "work_chair_has_rod")
            work_chair_foot_support = self.get_arrayparams(
                params, "work_chair_foot_support"
            )
            work_chair_regulates_when_sitting = self.get_arrayparams(
                params, "work_chair_regulates_when_sitting"
            )
            work_chair_supports_back = self.get_arrayparams(
                params, "work_chair_supports_back"
            )
            work_chair_use_rods = self.get_arrayparams(params, "work_chair_use_rods")

            uses_2_screens = self.get_arrayparams(params, "uses_2_screens")
            pause_for_rest = self.get_arrayparams(params, "pause_for_rest")
            sitting_time = self.get_arrayparams(params, "sitting_time")

            dental_evaluation = self.get_arrayparams(params, "dental_evaluation")
            medical_consultation = self.get_arrayparams(params, "medical_consultation")
            medical_consultation_specialty = params.get(
                "medical_consultation_specialty"
            )
            conducted_examinations = self.get_arrayparams(
                params, "conducted_examinations"
            )
            conducted_examinations_which = params.get("conducted_examinations_which")

            medical_license_higher_3_days_last_2_years = self.get_arrayparams(
                params, "medical_license_higher_3_days_last_2_years"
            )
            medical_license_less_3_days_last_year = self.get_arrayparams(
                params, "medical_license_less_3_days_last_year"
            )
            medical_license_family_support = self.get_arrayparams(
                params, "medical_license_family_support"
            )

            job_satisfaction = self.get_arrayparams(params, "job_satisfaction")
            job_exhaustion = self.get_arrayparams(params, "job_exhaustion")
            job_relationship = self.get_arrayparams(params, "job_relationship")
            job_relationship_boss = self.get_arrayparams(
                params, "job_relationship_boss"
            )
            better_at_work = params.get("better_at_work")
            less_at_work = params.get("less_at_work")
            leisure_actions = self.get_arrayparams(params, "leisure_actions")
            difficulty_sleeping = self.get_arrayparams(params, "difficulty_sleeping")
            planning_future = self.get_arrayparams(params, "planning_future")
            stress_or_anxiety_major_problem = self.get_arrayparams(
                params, "stress_or_anxiety_major_problem"
            )
            depression_or_frustration_major_problem = self.get_arrayparams(
                params, "depression_or_frustration_major_problem"
            )
            enjoyed_the_vacation = self.get_arrayparams(
                params, "enjoyed_the_vacation", "YEAR_TIME"
            )

            satisfied_service = self.get_arrayparams(
                params,
                "satisfied_service",
            )
            satisfied_service_justify = params.get("satisfied_service_justify")

            topics_of_interest = params.get("topics_of_interest")
            observations = params.get("observations")

            health = Health.objects.filter(pk=health_pk).first()
            if health is None:
                health = Health()
                health.controlinformation_id = controlinformation
            health.physical_exam_blood_pressure = physical_exam_blood_pressure
            health.physical_exam_imc = physical_exam_imc
            health.physical_exam_abdominal_circumference = (
                physical_exam_abdominal_circumference
            )
            health.physical_exam_pulse = physical_exam_pulse
            health.physical_exam_other = physical_exam_other
            health.ingestion_candy = ingestion_candy
            health.ingestion_pasta = ingestion_pasta
            health.ingestion_fruit = ingestion_fruit
            health.ingestion_vegetable = ingestion_vegetable
            health.ingestion_beef = ingestion_beef
            health.ingestion_fry = ingestion_fry
            health.ingestion_supplement = ingestion_supplement
            health.family_health_problems = family_health_problems
            health.family_health_problems_other = family_health_problems_other
            health.health_problems = health_problems
            health.health_problems_other = health_problems_other
            health.life_habits = life_habits
            health.life_habits_other = life_habits_other
            health.immunization = immunization
            health.medicament = medicament
            health.medicament_other = medicament_other
            health.physical_activity = physical_activity
            health.has_pain = has_pain
            health.local_pain = local_pain
            health.local_pain_other = local_pain_other

            health.strength_at_work = strength_at_work

            health.work_chair_seat_adjustment = work_chair_seat_adjustment
            health.work_chair_height_adjustment = work_chair_height_adjustment
            health.work_chair_tilt_adjustment = work_chair_tilt_adjustment
            health.work_chair_has_rod = work_chair_has_rod
            health.work_chair_foot_support = work_chair_foot_support
            health.work_chair_regulates_when_sitting = work_chair_regulates_when_sitting
            health.work_chair_supports_back = work_chair_supports_back
            health.work_chair_use_rods = work_chair_use_rods

            health.uses_2_screens = uses_2_screens
            health.pause_for_rest = pause_for_rest
            health.sitting_time = sitting_time

            health.dental_evaluation = dental_evaluation
            health.medical_consultation = medical_consultation
            health.medical_consultation_specialty = medical_consultation_specialty
            health.conducted_examinations = conducted_examinations
            health.conducted_examinations_which = conducted_examinations_which

            health.medical_license_higher_3_days_last_2_years = (
                medical_license_higher_3_days_last_2_years
            )
            health.medical_license_less_3_days_last_year = (
                medical_license_less_3_days_last_year
            )
            health.medical_license_family_support = medical_license_family_support

            health.job_satisfaction = job_satisfaction
            health.job_exhaustion = job_exhaustion
            health.job_relationship = job_relationship
            health.job_relationship_boss = job_relationship_boss
            health.better_at_work = better_at_work
            health.less_at_work = less_at_work
            health.leisure_actions = leisure_actions
            health.difficulty_sleeping = difficulty_sleeping
            health.planning_future = planning_future
            health.stress_or_anxiety_major_problem = stress_or_anxiety_major_problem
            health.depression_or_frustration_major_problem = (
                depression_or_frustration_major_problem
            )
            health.enjoyed_the_vacation = enjoyed_the_vacation

            health.satisfied_service = satisfied_service
            health.satisfied_service_justify = satisfied_service_justify

            health.topics_of_interest = topics_of_interest
            health.observations = observations

            health.save(health_area=params.get("health_area"))

        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="SRDIR foi adicionado com sucesso.",
            )
        return self.renderer(rst)

    def delete(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            params = self.request.POST
            health_pk = int(params.get("health_pk", 0) or 0)
            health = Health.objects.filter(pk=health_pk).first()
            health.delete(health_area=params.get("health_area"))
        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="SRDIR foi removido com sucesso.",
            )
        return self.renderer(rst)

    def associate(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            params = self.request.POST
            health_pks = params.get("health_pk")[:-1].split(",")
            evaluator_pk = params.get("evaluator_pk")
            for data in Health.objects.filter(pk__in=health_pks):
                data.evaluator_id = evaluator_pk
                data.save(health_area=True)
        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="Associação realizada com sucesso.",
            )
        return self.renderer(rst)

    def disassociate(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:
            params = self.request.POST
            health_pks = params.get("health_pk")[:-1].split(",")
            evaluator_pk = params.get("evaluator_pk")
            for data in Health.objects.filter(pk__in=health_pks):
                data.evaluator = None
                data.evaluation = None
                data.save(health_area=True)
        except Exception as e:
            rst.update(
                success=False,
                message=str(e),
            )
        else:
            rst.update(
                success=True,
                message="Associação realizada com sucesso.",
            )
        return self.renderer(rst)

    def evaluation_pending_store(self, args=[]):

        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.evaluation_pending_query()

            if len(args) == 0:
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                count = query.count()
                query = self.do_page(query)

                rst.update(
                    success=True,
                    count=count,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.filter(pk=args[0]).first()

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def evaluation_pending_query(self):
        if get_current_user().has_perm("cirdir.can_management_health_area"):
            return (
                self.Model.objects.filter(
                    health_assessments__isnull=False,
                    health_assessments__signed_at__isnull=True,
                )
                .order_by("id")
                .distinct("id")
            )

        else:
            return self.Model.objects.none()

    # def confirm_information(self, args=[]):
    #     rst = {
    #         'success': False,
    #         'message': 'nada foi feito ainda',
    #         'content': 'Sem informações',
    #     }
    #     try:
    #         instance = self._model.objects.get(pk=self.request.POST.get('pk'))
    #         instance.confirm_information()
    #     except self.Model.DoesNotExist as e:
    #         rst.update(
    #             message=u'Não consegui encontrar o documento desejado. Verifique as condições de acesso.'
    #         )
    #     except Exception as e:
    #         rst.update(
    #             message=str(e)
    #         )
    #     else:
    #         rst.update(
    #             success=True,
    #             message=u'informação confirmada'
    #         )
    #     self.renderer(rst)
