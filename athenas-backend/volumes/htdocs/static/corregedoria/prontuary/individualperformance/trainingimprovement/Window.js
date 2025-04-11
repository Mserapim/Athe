Ext._define('corregedoria.prontuary.individualperformance.trainingimprovement.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.trainingimprovement.Restful',

    width: 630,

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.prontuary.individualperformance.trainingimprovement.attachments.Grid', {
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
            this.getAttachmentsGrid().params = {detailtrainingimprovement: this.oId,};
        } else {
            this.getAttachmentsGrid().disable();
        }
        this.getAttachmentsGrid().setFilterProperty('detailtrainingimprovement_id', this.oId, 100);
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
                        labelWidth: 65,
                        items: [
                            {
                                xtype: 'textarea',
                                fieldLabel: 'Publicação',
                                name: 'publication',
                                width: 530,

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
                                        id: 'publication_type',
                                        hiddenName: 'publication_type',
                                        width: 180,
                                        choiceId: 'prontuary.PUBLICATION_TYPE',
                                        listeners: {
                                            scope: this,
                                            render: function(){
                                                if (Ext.getCmp('publication_type').value==1) {
                                                    Ext.getCmp('score').disable();
                                                } else {
                                                    Ext.getCmp('score').enable();
                                                }
                                            },
                                            select: function(index){
                                                if (index.value==1) {
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
                                        name: 'date_publication',
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
                    this.getAttachmentsGrid(cfg),
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
        corregedoria.prontuary.individualperformance.trainingimprovement.Window.superclass.constructor.call(this, cfg);
        this.observer(cfg);
    },

});
