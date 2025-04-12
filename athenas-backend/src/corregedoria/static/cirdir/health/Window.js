Ext._define('corregedoria.cirdir.health.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.health.Restful',

    width: 1000,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                layout: 'form',
                height: 575,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                items: [
                    {
                      xtype:'fieldset',
                      title: '1. Exame Físico',
                      labelWidth: 150,
                      items:[
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'column',
                              items: [
                                  {
                                      xtype:'panel',
                                      autoHeight:true,
                                      layout: 'form',
                                      labelWidth: 105,
                                      columnWidth: 0.23,
                                      items: [
                                          {
                                              xtype: 'textfield',
                                              fieldLabel: 'a) Pressão Arterial',
                                              name: 'physical_exam_blood_pressure',
                                              width: 90,
                                          },
                                      ]
                                  },
                                  {
                                      xtype:'panel',
                                      autoHeight:true,
                                      layout: 'form',
                                      labelWidth: 190,
                                      columnWidth: 0.33,
                                      items: [
                                          {
                                              xtype: 'textfield',
                                              fieldLabel: 'b) IMC (Índice de Massa Corpórea)',
                                              name: 'physical_exam_imc',
                                              width: 90,
                                          },
                                      ]
                                  },
                                  {
                                      xtype:'panel',
                                      autoHeight:true,
                                      layout: 'form',
                                      labelWidth: 160,
                                      columnWidth: 0.29,
                                      items: [
                                          {
                                              xtype: 'textfield',
                                              fieldLabel: 'c) Circunferência Abdominal',
                                              name: 'physical_exam_abdominal_circumference',
                                              width: 90,
                                          },
                                      ]
                                  },
                                  {
                                      xtype:'panel',
                                      autoHeight:true,
                                      layout: 'form',
                                      labelWidth: 47,
                                      columnWidth: 0.15,
                                      items: [
                                          {
                                              xtype: 'textfield',
                                              fieldLabel: 'd) Pulso',
                                              name: 'physical_exam_pulse',
                                              width: 85,
                                          },
                                      ]
                                  },
                              ]
                          },
                          {
                              xtype:'panel',
                              autoHeight:true,
                              layout: 'form',
                              labelWidth: 55,
                              items: [
                                  {
                                      xtype: 'textfield',
                                      fieldLabel: 'e) Outros',
                                      name: 'physical_exam_other',
                                      width: 865,
                                  },
                              ]
                          },
                      ]
                    },
                    {
                          xtype:'fieldset',
                          title: '2. Frequência semanal de ingestão de alimentos, conforme categorias a seguir',
                          labelAlign: 'top',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 35,
                                  checkconfig: {
                                      name: "ingestion_candy",
                                      fieldLabel: '<b>Doce</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_candy) ? cfg.values.ingestion_candy : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 40,
                                  checkconfig: {
                                      name: "ingestion_pasta",
                                      fieldLabel: '<b>Massa</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_pasta) ? cfg.values.ingestion_pasta : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 40,
                                  checkconfig: {
                                      name: "ingestion_fruit",
                                      fieldLabel: '<b>Frutas</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_fruit) ? cfg.values.ingestion_fruit : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 110,
                                  checkconfig: {
                                      name: "ingestion_vegetable",
                                      fieldLabel: '<b>Vegetais/Legumes</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_vegetable) ? cfg.values.ingestion_vegetable : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 35,
                                  checkconfig: {
                                      name: "ingestion_beef",
                                      fieldLabel: '<b>Carne</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_beef) ? cfg.values.ingestion_beef : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 40,
                                  checkconfig: {
                                      name: "ingestion_fry",
                                      fieldLabel: '<b>Fritura</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_fry) ? cfg.values.ingestion_fry : [],
                                  },
                              },
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  labelWidth: 70,
                                  checkconfig: {
                                      name: "ingestion_supplement",
                                      fieldLabel: '<b>Suplemento</b>',
                                      choiceId: "cirdir_health.FREQUENCY_INGESTION",
                                      columns: 5,
                                      items_db: (cfg.values.ingestion_supplement) ? cfg.values.ingestion_supplement : [],
                                  },
                              },
                          ]
                    },


                    {
                          xtype:'fieldset',
                          title: '3. Alguém na sua família apresenta ou já apresentou alguma das condições abaixo?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  checkconfig: {
                                      name: "family_health_problems",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.HEALTH_PROBLEMS",
                                      columns: 5,
                                      items_db: (cfg.values.family_health_problems) ? cfg.values.family_health_problems : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 40,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Outros',
                                          name: 'family_health_problems_other',
                                          width: 880,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '4. Você apresenta ou já apresentou alguma das condições abaixo?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  checkconfig: {
                                      name: "health_problems",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.HEALTH_PROBLEMS",
                                      columns: 5,
                                      items_db: (cfg.values.health_problems) ? cfg.values.health_problems : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 40,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Outros',
                                          name: 'health_problems_other',
                                          width: 880,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '5. Hábitos de vida',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  checkconfig: {
                                      name: "life_habits",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.LIFE_HABITS",
                                      columns: 5,
                                      items_db: (cfg.values.life_habits) ? cfg.values.life_habits : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 40,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Outros',
                                          name: 'life_habits_other',
                                          width: 880,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '6. Imunização (cartão de vacina)',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "immunization",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.IMMUNIZATION",
                                      columns: 3,
                                      items_db: (cfg.values.immunization) ? cfg.values.immunization : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '7. Uso de medicamentos',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  checkconfig: {
                                      name: "medicament",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.MEDICAMENT",
                                      columns: 2,
                                      items_db: (cfg.values.medicament) ? cfg.values.medicament : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 40,
                                  columnWidth: 0.23,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Outros',
                                          name: 'medicament_other',
                                          width: 880,
                                      },
                                  ]
                              },
                          ]
                    },


                    {
                          xtype:'fieldset',
                          title: '8. Você realiza atividade física com qual frequência?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "physical_activity",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY_WEEK",
                                      columns: 4,
                                      items_db: (cfg.values.physical_activity) ? cfg.values.physical_activity : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '9. Você sente dor ou fadiga durante o trabalho?',
                          items:[
                              {
                                  xtype: 'radiogroup',
                                  hideLabel: true,
                                  columns: 1,
                                  items: [
                                      {boxLabel: 'a) Não', name: 'has_pain', inputValue: 1, checked: cfg.values.has_pain == 1 ? true : false, },
                                      {boxLabel: 'b) Sim. A dor e/ou fadiga só aparece no <u>final</u> da jornada de trabalho, e cessa à noite e nos dias de folga.', name: 'has_pain', inputValue: 2, checked: cfg.values.has_pain == 2 ? true : false, },
                                      {boxLabel: 'c) Sim. A dor e/ou fadiga aparece no <u>início</u> da jornada de trabalho e não melhora como o repouso.', name: 'has_pain', inputValue: 3, checked: cfg.values.has_pain == 3 ? true : false, },
                                      {boxLabel: 'd) Sim. Além da dor e/ou fadiga, há também fraqueza e dificuldade para realizar atividades laborais e domésticas.', name: 'has_pain', inputValue: 4, checked: cfg.values.has_pain == 4 ? true : false, },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '10. A dor citada acima é recorrente (crônica)? Em quais regiões?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  checkconfig: {
                                      name: "local_pain",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.LOCAL_PAIN",
                                      columns: 4,
                                      items_db: (cfg.values.local_pain) ? cfg.values.local_pain : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 40,
                                  columnWidth: 0.23,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Outros',
                                          name: 'local_pain_other',
                                          width: 880,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '11. A sua atividades exige que você faça muita força física como, por exemplo, levantar 5 ou mais quilos?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "strength_at_work",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY",
                                      columns: 5,
                                      items_db: (cfg.values.strength_at_work) ? cfg.values.strength_at_work : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '12. A cadeira que você utiliza no trabalho, oferece prossibilidades de ajustes, tais como:',
                          items:[
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 185,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Regulagem de altura do assento',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_seat_adjustment', inputValue: 1, checked: cfg.values.work_chair_seat_adjustment == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_seat_adjustment', inputValue: 2, checked: cfg.values.work_chair_seat_adjustment == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 185,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Regulagem de altura do encosto',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_height_adjustment', inputValue: 1, checked: cfg.values.work_chair_height_adjustment == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_height_adjustment', inputValue: 2, checked: cfg.values.work_chair_height_adjustment == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 210,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Regulagem de inclinação do encosto',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_tilt_adjustment', inputValue: 1, checked: cfg.values.work_chair_tilt_adjustment == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_tilt_adjustment', inputValue: 2, checked: cfg.values.work_chair_tilt_adjustment == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 105,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Base com rodízios',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_has_rod', inputValue: 1, checked: cfg.values.work_chair_has_rod == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_has_rod', inputValue: 2, checked: cfg.values.work_chair_has_rod == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 125,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Permite apoiar os pés',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_foot_support', inputValue: 1, checked: cfg.values.work_chair_foot_support == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_foot_support', inputValue: 2, checked: cfg.values.work_chair_foot_support == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 280,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Você ajusta a cadeira antes de começar a trabalhar',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_regulates_when_sitting', inputValue: 1, checked: cfg.values.work_chair_regulates_when_sitting == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_regulates_when_sitting', inputValue: 2, checked: cfg.values.work_chair_regulates_when_sitting == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 170,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Apoia as costas no encosto',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_supports_back', inputValue: 1, checked: cfg.values.work_chair_supports_back == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_supports_back', inputValue: 2, checked: cfg.values.work_chair_supports_back == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 455,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Você utiliza os rodízios da cadeira para rodar o tronco e pegar objetos distantes',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'work_chair_use_rods', inputValue: 1, checked: cfg.values.work_chair_use_rods == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'work_chair_use_rods', inputValue: 2, checked: cfg.values.work_chair_use_rods == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },


                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 220,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Você utiliza duas telas de computador',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'uses_2_screens', inputValue: 1, checked: cfg.values.uses_2_screens == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'uses_2_screens', inputValue: 2, checked: cfg.values.uses_2_screens == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 660,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Durante a jornada de trabalho você realiza pausas para descanso de movimentos repetitivos, a cada 1 hora de trabalho',
                                          columns: 2,
                                          width: 100,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: 'Sim', name: 'pause_for_rest', inputValue: 1, checked: cfg.values.pause_for_rest == 1 ? true : false, },
                                              {boxLabel: 'Não', name: 'pause_for_rest', inputValue: 2, checked: cfg.values.pause_for_rest == 2 ? true : false, },
                                          ]
                                      },
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 330,
                                  items: [
                                      {
                                          xtype: 'radiogroup',
                                          fieldLabel: 'Quanto tempo fica sentado(a), sem se levantar da cadeira',
                                          columns: 4,
                                          width: 400,
                                          labelSeparator: '?',
                                          items: [
                                              {boxLabel: '1 hora', name: 'sitting_time', inputValue: 1, checked: cfg.values.sitting_time == 1 ? true : false, },
                                              {boxLabel: '2 horas', name: 'sitting_time', inputValue: 2, checked: cfg.values.sitting_time == 2 ? true : false, },
                                              {boxLabel: '3 horas', name: 'sitting_time', inputValue: 3, checked: cfg.values.sitting_time == 3 ? true : false, },
                                              {boxLabel: 'Ou mais horas', name: 'sitting_time', inputValue: 4, checked: cfg.values.sitting_time == 4 ? true : false, },
                                          ]
                                      },
                                  ]
                              },

                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '13. Última avaliação odontológica',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "dental_evaluation",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.YEAR_TIME",
                                      columns: 3,
                                      items_db: (cfg.values.dental_evaluation) ? cfg.values.dental_evaluation : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '14: Consulta médica',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "medical_consultation",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.YEAR_TIME",
                                      columns: 3,
                                      items_db: (cfg.values.medical_consultation) ? cfg.values.medical_consultation : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 108,
                                  columnWidth: 0.23,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Qual especialidade',
                                          name: 'medical_consultation_specialty',
                                          width: 812,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '15. Quando realizou exames?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "conducted_examinations",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.YEAR_TIME",
                                      columns: 3,
                                      items_db: (cfg.values.conducted_examinations) ? cfg.values.conducted_examinations : [],
                                  },
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 33,
                                  columnWidth: 0.23,
                                  items: [
                                      {
                                          xtype: 'textfield',
                                          fieldLabel: 'Quais',
                                          name: 'conducted_examinations_which',
                                          width: 887,
                                      },
                                  ]
                              },
                          ]
                    },

                    {
                          xtype:'fieldset',
                          title: '16. Você já precisou se afastar do serviço nos últimos 02 anos por motivo de saúde, por um período superior a 03 dias?',
                          items:[
                              {
                                  xtype: 'radiogroup',
                                  hideLabel: true,
                                  columns: 2,
                                  width: 150,
                                  items: [
                                      {boxLabel: 'Sim', name: 'medical_license_higher_3_days_last_2_years', inputValue: 1, checked: cfg.values.medical_license_higher_3_days_last_2_years == 1 ? true : false,},
                                      {boxLabel: 'Não', name: 'medical_license_higher_3_days_last_2_years', inputValue: 2, checked: cfg.values.medical_license_higher_3_days_last_2_years == 2 ? true : false,},
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '17. Você precisou  ficar sem vir ao trabalho por menos de 03 dias no último ano por motivo de saúde?',
                          items:[
                              {
                                  xtype: 'radiogroup',
                                  hideLabel: true,
                                  columns: 2,
                                  width: 150,
                                  items: [
                                      {boxLabel: 'Sim', name: 'medical_license_less_3_days_last_year', inputValue: 1, checked: cfg.values.medical_license_less_3_days_last_year == 1 ? true : false,},
                                      {boxLabel: 'Não', name: 'medical_license_less_3_days_last_year', inputValue: 2, checked: cfg.values.medical_license_less_3_days_last_year == 2 ? true : false,},
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '18. Você já precisou se afastar do serviço nos últimos 02 anos por motivo de doença em pessoa da família?',
                          items:[
                              {
                                  xtype: 'radiogroup',
                                  hideLabel: true,
                                  columns: 2,
                                  width: 150,
                                  items: [
                                      {boxLabel: 'Sim', name: 'medical_license_family_support', inputValue: 1, checked: cfg.values.medical_license_family_support == 1 ? true : false,},
                                      {boxLabel: 'Não', name: 'medical_license_family_support', inputValue: 2, checked: cfg.values.medical_license_family_support == 2 ? true : false,},
                                  ]
                              },
                          ]
                    },

                    {
                          xtype:'fieldset',
                          title: '19. Com que frequência você se sente satisfeito no exercício de sua função?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "job_satisfaction",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY",
                                      columns: 5,
                                      items_db: (cfg.values.job_satisfaction) ? cfg.values.job_satisfaction : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '20. Quantos dias, no último mês, você se sentiu esgotado física e/ou, mentalmente ao final do expediente de trabalho?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "job_exhaustion",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.DAYS_PERIOD",
                                      columns: 5,
                                      items_db: (cfg.values.job_exhaustion) ? cfg.values.job_exhaustion : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '21. Como você considera o seu relacionamento com colegas do setor?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "job_relationship",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.SATISFACTION",
                                      columns: 4,
                                      items_db: (cfg.values.job_relationship) ? cfg.values.job_relationship : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '22. Como você considera o seu relacionamento com as chefias mediata e imediata?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "job_relationship_boss",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.SATISFACTION",
                                      columns: 4,
                                      items_db: (cfg.values.job_relationship_boss) ? cfg.values.job_relationship_boss : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '23. O que mais te agrada em trabalhar nesta Instituição?',
                          items:[
                              {
                                  xtype: 'textarea',
                                  hideLabel: true,
                                  name: 'better_at_work',
                                  width: 930,
                                  height: 60,
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '24. O que menos te agrada em trabalhar nesta Instituição?',
                          items:[
                              {
                                  xtype: 'textarea',
                                  hideLabel: true,
                                  name: 'less_at_work',
                                  width: 930,
                                  height: 60,
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '25. Quando está fora do ambiente de trabalho, com que frequência você se engaja em ações de lazer?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "leisure_actions",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY",
                                      columns: 5,
                                      items_db: (cfg.values.leisure_actions) ? cfg.values.leisure_actions : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '26. Com que frequência você tem dificuldades para dormir à noite (tanto para iniciar a dormir, quanto para manter-se dormindo pelas horas necessárias)?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "difficulty_sleeping",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY",
                                      columns: 5,
                                      items_db: (cfg.values.difficulty_sleeping) ? cfg.values.difficulty_sleeping : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '27. Você planeja ações pessoais para o futuro com que frequência?',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "planning_future",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.FREQUENCY",
                                      columns: 5,
                                      items_db: (cfg.values.planning_future) ? cfg.values.planning_future : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '28. O estresse ou a ansiedade são minhas principais dificuldades atualmente.',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "stress_or_anxiety_major_problem",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.CONCORDANCE_LEVEL",
                                      columns: 5,
                                      items_db: (cfg.values.stress_or_anxiety_major_problem) ? cfg.values.stress_or_anxiety_major_problem : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '29. A depressão ou fustração são minhas principais dificuldades atualmente.',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "depression_or_frustration_major_problem",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.CONCORDANCE_LEVEL",
                                      columns: 5,
                                      items_db: (cfg.values.depression_or_frustration_major_problem) ? cfg.values.depression_or_frustration_major_problem : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '30. Usufruiu férias',
                          items:[
                              {
                                  xtype: "checkboxchoicefield",
                                  singleSelection: true,
                                  checkconfig: {
                                      name: "enjoyed_the_vacation",
                                      hideLabel: true,
                                      choiceId: "cirdir_health.YEAR_TIME",
                                      columns: 3,
                                      items_db: (cfg.values.enjoyed_the_vacation) ? cfg.values.enjoyed_the_vacation : [],
                                  },
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '31. Você se sente satisfeito com o serviço que presta?',
                          items:[
                              {
                                  xtype: 'radiogroup',
                                  hideLabel: true,
                                  columns: 2,
                                  width: 150,
                                  items: [
                                      {boxLabel: 'Sim', name: 'satisfied_service', inputValue: 1, checked: cfg.values.satisfied_service == 1 ? true : false,},
                                      {boxLabel: 'Não', name: 'satisfied_service', inputValue: 2, checked: cfg.values.satisfied_service == 2 ? true : false,},
                                  ]
                              },
                              {
                                  xtype:'panel',
                                  autoHeight:true,
                                  layout: 'form',
                                  labelWidth: 58,
                                  columnWidth: 0.23,
                                  items: [
                                      {
                                          xtype: 'textarea',
                                          fieldLabel: 'Justifique',
                                          name: 'satisfied_service_justify',
                                          width: 863,
                                          height: 60,
                                      },
                                  ]
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '32. Indique temas que você gostaria de obter informações',
                          items:[
                              {
                                  xtype: 'textarea',
                                  hideLabel: true,
                                  name: 'topics_of_interest',
                                  width: 930,
                                  height: 60,
                              },
                          ]
                    },
                    {
                          xtype:'fieldset',
                          title: '33. Observações',
                          items:[
                              {
                                  xtype: 'textarea',
                                  hideLabel: true,
                                  name: 'observations',
                                  width: 930,
                                  height: 60,
                              },
                          ]
                    },
                ]
            });

        return this._formPanel;
    },

    save: function() {
        var values = this.getFormPanel().getForm().getValues();
        values.health_pk = this.oId;
        values.health_area = this.params.health_area;
        values.controlinformation = this.params.controlinformation;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Salvando dados de saúde...'});
        mask.show();
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('CIRDIRHealth', 'save'),
            callback: function() {
                this.params.mainGrid.getStore().reload();
                mask.hide();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Salvar',
                    msg: rst.message,
                    icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
                if (rst.success == true) {
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                }
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Salvar',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            params: values,
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
        });
        corregedoria.cirdir.health.Window.superclass.constructor.call(this, cfg);
    },


});
