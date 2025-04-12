Ext._define('edocs.protocolo.requestform.evaluation.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormEvaluation',

    rest: 'edocs.protocolo.requestform.evaluation.Restful',

    width: 900,

    autoScroll: true,

    getEmployeeField: function(cfg) {
        if (!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                anchor: '100%',
                allowBlank: false,
            });
        }

        return this._employeeField;
    },

    getComplianceActivitiesGoalsFieldSet: function(cfg) {
        if(this._complianceActivitiesGoals)
            return this._complianceActivitiesGoals

        this._complianceActivitiesGoals = Ext._create('Ext.form.FieldSet', {
            title: 'CUMPRIMENTO DAS ATIVIDADES E METAS',
            layout: 'anchor',
            style: {marginBottom: '10px'},
            items: [
                {
                    xtype: 'ckeditor',
                    name: 'cumpliance_activities_goals',
                    height: 150,
                    toolbarGroups: [
                        { name: 'styles', itens: ['Format'] },
                        { name: 'clipboard' },
                        { name: 'editing' },
                        { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                        {
                            name: 'paragraph',
                            groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                        }
                    ]
                },
            ]
        });

        return this._complianceActivitiesGoals;
    },

    getStartDateField: function(cfg) {
        if (!this._startDateField) {
            this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de início",
                name: "start_date",
                width: 200,
                allowBlank: false
            });
        }

        return this._startDateField;
    },

    getEndDateField: function(cfg) {
        if (!this._endDateField) {
            this._endDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de término",
                name: "end_date",
                width: 200,
                allowBlank: false
            });
        }

        return this._endDateField;
    },

    getQuestionnaireEvaluationFieldSet: function(cfg) {
        if(this._questionnaireEvaluation)
            return this._questionnaireEvaluation

        this._questionnaireEvaluation = Ext._create('Ext.form.FieldSet', {
            title: 'QUESTIONÁRIO DE AVALIAÇÃO',
            style: {marginBottom: '10px'},
            items: [
                {
                    xtype: 'fieldset',
                    title: 'O servidor cumpriu os prazos estabelecidos?',
                    items: [
                        {
                            xtype: 'radiogroup',
                            columns: 2,
                            name: 'employee_date_established',
                            hideLabel: true,
                            items: [
                                {
                                    xtype: 'radio',
                                    boxLabel: 'SIM',
                                    name: 'employee_date_established',
                                    inputValue: 1,
                                    checked: true,
                                },
                                {
                                    xtype: 'radio',
                                    boxLabel: 'NÃO',
                                    name: 'employee_date_established',
                                    inputValue: 0,
                                    checked: false,
                                },
                            ],
                        },
                    ]
                },
                {
                    xtype: 'fieldset',
                    title: 'O servidor cumpriu a jornada estabelecida?',
                    items: [
                        {
                            xtype: 'radiogroup',
                            columns: 2,
                            name: 'employee_working_established',
                            hideLabel: true,
                            items: [
                                {
                                    xtype: 'radio',
                                    boxLabel: 'SIM',
                                    name: 'employee_working_established',
                                    inputValue: 1,
                                    hideLabel: true,
                                    checked: true,
                                },
                                {
                                    xtype: 'radio',
                                    boxLabel: 'NÃO',
                                    name: 'employee_working_established',
                                    inputValue: 0,
                                    hideLabel: true,
                                    checked: false,
                                },
                            ],
                        },
                    ]
                },
                {
                    xtype: 'fieldset',
                    title: 'O servidor estava disponível através dos canais de comunicação no horário habitual de expediente?',
                    items: [
                        {
                            xtype: 'radiogroup',
                            columns: 2,
                            name: 'employee_available',
                            hideLabel: true,
                            items: [
                                {
                                    xtype: 'radio',
                                    boxLabel: 'SIM',
                                    name: 'employee_available',
                                    inputValue: 1,
                                    hideLabel: true,
                                    checked: true,
                                },
                                {
                                    xtype: 'radio',
                                    boxLabel: 'NÃO',
                                    name: 'employee_available',
                                    inputValue: 0,
                                    hideLabel: true,
                                    checked: false,
                                },
                            ],
                        },
                    ]
                },
                {
                    xtype: 'fieldset',
                    title: 'O servidor se adaptou ao teletrabalho?',
                    items: [
                        {
                            xtype: 'radiogroup',
                            columns: 2,
                            name: 'employee_addaption_working',
                            hideLabel: true,
                            items: [
                                {
                                    xtype: 'radio',
                                    boxLabel: 'SIM',
                                    name: 'employee_addaption_working',
                                    inputValue: 1,
                                    hideLabel: true,
                                    checked: true,
                                },
                                {
                                    xtype: 'radio',
                                    boxLabel: 'NÃO',
                                    name: 'employee_addaption_working',
                                    inputValue: 0,
                                    hideLabel: true,
                                    checked: false,
                                },
                            ],
                        },
                    ]
                },
                {
                    xtype: 'fieldset',
                    title: 'O servidor descumpriu algum dever a si estabelecido durante o teletrabalho?',
                    items: [
                        {
                            xtype: 'radiogroup',
                            columns: 2,
                            name: 'employee_disobey_working',
                            hideLabel: true,
                            items: [
                                {
                                    xtype: 'radio',
                                    boxLabel: 'SIM',
                                    name: 'employee_disobey_working',
                                    inputValue: 1,
                                    hideLabel: true,
                                    checked: true,
                                },
                                {
                                    xtype: 'radio',
                                    boxLabel: 'NÃO',
                                    name: 'employee_disobey_working',
                                    inputValue: 0,
                                    hideLabel: true,
                                    checked: false,
                                },
                            ],
                        },
                    ]
                },
                {
                    xtype: 'fieldset',
                    layout: 'anchor',
                    title: 'Em caso afirmativo da pergunta acima, elencar quais deveres foram descumpridos:',
                    items: [
                        {
                            xtype: 'ckeditor',
                            name: 'ask_affirmation_working',
                            height: 100,
                            toolbarGroups: [
                                { name: 'styles', itens: ['Format'] },
                                { name: 'clipboard' },
                                { name: 'editing' },
                                { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                                {
                                    name: 'paragraph',
                                    groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                }
                            ]

                        }
                    ]
                },
            ],
        });

        return this._questionnaireEvaluation;
    },

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
            items: [
                {
                    xtype: 'fieldset',
                    style: {marginBottom: '10px'},
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            labelWidth: 60,
                            items: this.getCodeField(cfg),
                        },
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.75,
                                    labelWidth: 60,
                                    items: this.getHomeCourtField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.25,
                                    labelWidth: 40,
                                    items: this.getDocumentTypeField('RELATÓRIO')  // mixin
                                }
                            ]
                        },
                        // {
                        //     xtype: 'container',
                        //     layout: 'form',
                        //     labelWidth: 60,
                        //     items: this.getSubjectField(cfg),
                        // },
                        this.getSubjectField(cfg, {
                            value: 'Relatório de Avaliação de Trabalho Remoto',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ]
                },
                {
                    xtype: 'fieldset',
                    title: 'SERVIDOR',
                    layout: 'form',
                    style: {marginBottom: '10px'},
                    labelWidth: 1,
                    items: this.getEmployeeField(cfg)
                },
                this.getComplianceActivitiesGoalsFieldSet(cfg),
                {
                    xtype: 'fieldset',
                    layout: 'hbox',
                    title: 'DATA DE APURAÇÃO',
                    style: {marginBottom: '10px'},
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 0.5,
                            labelWidth: 100,
                            items: this.getStartDateField(cfg)
                        },
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 0.5,
                            labelWidth: 100,
                            items: this.getEndDateField(cfg)
                        }
                    ]
                },
            ]
        });

        return this._mainPanel;
    },

    getQuestionnaireFormPanel: function(cfg) {
        if (this._questionnairePanel) {
            return this._questionnairePanel;
        }

        this._questionnairePanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
            items: [
                this.getQuestionnaireEvaluationFieldSet(cfg),
                {
                    xtype: 'fieldset',
                    style: { marginBottom: '1px' },
                    title: 'OBSERVAÇÕES',
                    layout: 'anchor',
                    labelWidth: 190,
                    items: [
                        {
                            xtype: 'ckeditor',
                            name: 'note',
                            height: 100,
                            toolbarGroups: [
                                { name: 'styles', itens: ['Format'] },
                                { name: 'clipboard' },
                                { name: 'editing' },
                                { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                                {
                                    name: 'paragraph',
                                    groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                }
                            ]
                        }
                    ]
                },
            ]
        });

        return this._questionnairePanel;
    },

    getInfoPanel: function (cfg) {
        if (this._mainFormPanel) {
            return this._mainFormPanel;
        }

        this._mainFormPanel = Ext._create('Ext.Panel', {
            title: 'Informações',
            frame: false,
            autoHeight: true,
            items: [
                this.getMainPanel(cfg)
            ],
        });

        return this._mainFormPanel;
    },

    getQuestionnairePanel: function (cfg) {
        if (this._questionarioFormPanel) {
            return this._questionarioFormPanel;
        }

        this._questionarioFormPanel = Ext._create('Ext.Panel', {
            title: 'Questionário',
            frame: false,
            autoHeight: true,
            items: [
                this.getQuestionnaireFormPanel(cfg)
            ],
        });

        return this._questionarioFormPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: [
                    this.getInfoPanel(cfg),
                    this.getQuestionnairePanel(cfg)
                ]
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: this.getTabPanel(cfg)
            });
        }

        return this._formPanel;
    }

});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Relatório de Avaliação de Trabalho Remoto',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.evaluation.Window',
    specialType: 'homeofficeforemployee',
    group: 'Teletrabalho'
});
