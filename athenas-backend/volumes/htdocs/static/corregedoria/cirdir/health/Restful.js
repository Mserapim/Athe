Ext._define('corregedoria.cirdir.health.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRHealth',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.health.Restful.superclass.getFields.call(this, cfg).concat([
              {type: "string", name: "unicode" },
              {type: "auto", name: "icons" },

              {type: "string", name: "physical_exam_blood_pressure" },
              {type: "string", name: "physical_exam_imc" },
              {type: "string", name: "physical_exam_abdominal_circumference" },
              {type: "string", name: "physical_exam_pulse" },
              {type: "string", name: "physical_exam_other" },
              {type: "auto", name: "ingestion_candy" },
              {type: "auto", name: "ingestion_pasta" },
              {type: "auto", name: "ingestion_fruit" },
              {type: "auto", name: "ingestion_vegetable" },
              {type: "auto", name: "ingestion_beef" },
              {type: "auto", name: "ingestion_fry" },
              {type: "auto", name: "ingestion_supplement" },

              {type: "auto", name: "family_health_problems" },
              {type: "string", name: "family_health_problems_other" },
              {type: "auto", name: "health_problems" },
              {type: "string", name: "health_problems_other" },
              {type: "auto", name: "life_habits" },
              {type: "string", name: "life_habits_other" },
              {type: "auto", name: "immunization" },
              {type: "auto", name: "medicament" },
              {type: "string", name: "medicament_other" },
              {type: "auto", name: "physical_activity" },
              {type: "auto", name: "has_pain" },
              {type: "auto", name: "local_pain" },
              {type: "string", name: "local_pain_other" },

              {type: "auto", name: "strength_at_work" },

              {type: "auto", name: "work_chair_seat_adjustment" },
              {type: "auto", name: "work_chair_height_adjustment" },
              {type: "auto", name: "work_chair_tilt_adjustment" },
              {type: "auto", name: "work_chair_has_rod" },
              {type: "auto", name: "work_chair_foot_support" },
              {type: "auto", name: "work_chair_regulates_when_sitting" },
              {type: "auto", name: "work_chair_supports_back" },
              {type: "auto", name: "work_chair_use_rods" },

              {type: "auto", name: "uses_2_screens" },
              {type: "auto", name: "pause_for_rest" },
              {type: "auto", name: "sitting_time" },

              {type: "auto", name: "dental_evaluation" },
              {type: "auto", name: "medical_consultation" },
              {type: "string", name: "medical_consultation_specialty" },
              {type: "auto", name: "conducted_examinations" },
              {type: "string", name: "conducted_examinations_which" },

              {type: "auto", name: "medical_license_higher_3_days_last_2_years" },
              {type: "auto", name: "medical_license_less_3_days_last_year" },
              {type: "auto", name: "medical_license_family_support" },


              {type: "auto", name: "job_satisfaction" },
              {type: "auto", name: "job_exhaustion" },
              {type: "auto", name: "job_relationship" },
              {type: "auto", name: "job_relationship_boss" },
              {type: "string", name: "better_at_work" },
              {type: "string", name: "less_at_work" },
              {type: "auto", name: "leisure_actions" },
              {type: "auto", name: "difficulty_sleeping" },
              {type: "auto", name: "planning_future" },
              {type: "auto", name: "stress_or_anxiety_major_problem" },
              {type: "auto", name: "depression_or_frustration_major_problem" },
              {type: "auto", name: "enjoyed_the_vacation" },

              {type: "auto", name: "satisfied_service" },
              {type: "string", name: "satisfied_service_justify" },

              {type: "string", name: "topics_of_interest" },
              {type: "string", name: "observations" },

              {type: "bool", name: "authorization_health" },

              {type: "string", name: "integrant_unicode" },
              {type: "int", name: "integrant" },

            ]);
        return this._fields;
    }
});
