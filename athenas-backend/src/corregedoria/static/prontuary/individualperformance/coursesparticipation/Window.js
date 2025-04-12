Ext._define('corregedoria.prontuary.individualperformance.coursesparticipation.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.coursesparticipation.Restful',

    width: 630,

    getDeparturesGrid: function(cfg) {
        if(!this._departuresField)
            this._departuresField = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Afastamentos',
                hideLabel: true,
                name: 'studydepartures',
                // displayField: 'unicode',
                allowBlank: true,
                relatedname: 'departures',
                rest: this.rest,
                sourceRest: 'rh.afastamento.afastamentoestudar.Restful',
                oId: this.oId || cfg.oId,
                width: 605,
                height: 300,
                border: false,
                hideSelectButton: true,
            });
            this._departuresField.getAddField().gridConfig = {
                columnAction: false,
                hideItemsToolbar:['add', 'edit', 'remove', 'download',],
                hideColumns: [
                    'instituicao', 'instituicao_unicode', 'curso', 'curso_unicode', 'localidade', 'localidade_unicode', 'icons', 'situation_unicode',
                    'alteracao_display', 'unicode', 'publicacao_fim_unicode', 'suspensao_contagem_ferias_display', 'suspensao_estagio_prob_display',
                    'efetivo_exercicio_display', 'prorroga_progressao_display', 'agendado_arquimedes_display', 'concessao_durante_estagio_prob_display',
                    'tipo_display', 'remunerado_display', 'annotation_class', 'created_by_unicode', 'created_at', 'modified_by_unicode', 'modified_at',
                ],
                hiddenFilter: true,
            };
        return this._departuresField;
    },

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.prontuary.individualperformance.coursesparticipation.attachments.Grid', {
                region: 'center',
                layout: 'form',
                title: 'Anexos',
                border: true,
                height: 300,
                disabled: true,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
            });
        }
        return this._attachmentsGrid;
    },

    getListIndicationField: function(cfg) {
        if(!this._listIndicationField) {
            this._listIndicationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Edital",
                allowBlank: true,
                rest: "corregedoria.prontuary.individualperformance.listindication.Restful",
                name: "used_edital",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'remove', 'edit', 'download', '-'],
                    hideColumns: ['icons',],
                    hiddenFilter: true,
                    preFilter: [
                        {property: 'listindication__prontuary_id', value: cfg.params.prontuary, stage: 100},
                        {property: 'list_figuration', value: 2, stage: 101},
                    ],
                }
            });
        }
        return this._listIndicationField;
    },

    observer: function(cfg) {
        if (this.oId) {
            this.getAttachmentsGrid().enable();
            this.getAttachmentsGrid().params = {detailcoursesparticipation: this.oId,};
            this.getDeparturesGrid().enable();
            this.getDeparturesGrid().getAddField().setPreFilter([{property: 'servidor_id', value: cfg.params.employee_id, stage: 101}]);
        } else {
            this.getAttachmentsGrid().disable();
            this.getDeparturesGrid().disable();
        }
        this.getAttachmentsGrid().setFilterProperty('detailcoursesparticipation_id', this.oId, 100);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 110,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 35,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Curso',
                                name: 'course',
                                width: 560,

                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.4,
                                labelWidth: 27,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tipo',
                                        id: 'course_level',
                                        hiddenName: 'course_level',
                                        width: 180,
                                        choiceId: 'prontuary.COURSE_LEVEL',
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('course_level').value==4) {
                                                    Ext.getCmp('score').disable();
                                                } else {
                                                    Ext.getCmp('score').enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value==4) {
                                                    Ext.getCmp('score').disable();
                                                } else {
                                                    Ext.getCmp('score').enable();
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.25,
                                labelWidth: 32,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data',
                                        width: 100,
                                        name: 'date_course',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.35,
                                labelWidth: 80,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        fieldLabel: 'Carga Horária',
                                        width: 100,
                                        name: 'workload',
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.65,
                                labelWidth: 65,
                                items: [
                                    {
                                        xtype: 'numberfield',
                                        id: 'score',
                                        fieldLabel: 'Pontuação',
                                        width: 100,
                                        name: 'score',
                                        allowDecimals: false,
                                        allowNegative: false,
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.35,
                                labelWidth: 125,
                                items: [
                                    {
                                        xtype: 'combo',
                                        hiddenName: 'validated',
                                        fieldLabel: 'Válido para pontuação',
                                        width: 75,
                                        editable: false,
                                        triggerAction: 'all',
                                        store: [
                                            [1, ''],
                                            [2, 'SIM'],
                                            [3, 'NÃO'],
                                        ],
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 35,
                        items: [
                            this.getListIndicationField(cfg),
                        ]
                    },
                    {
                        xtype:'tabpanel',
                        activeTab: 0,
                        border: false,
                        items: [
                            this.getDeparturesGrid(cfg),
                            this.getAttachmentsGrid(cfg),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.observer(cfg);
                }
            }
        });
        corregedoria.prontuary.individualperformance.coursesparticipation.Window.superclass.constructor.call(this, cfg);
        this.observer(cfg);
    },

});
