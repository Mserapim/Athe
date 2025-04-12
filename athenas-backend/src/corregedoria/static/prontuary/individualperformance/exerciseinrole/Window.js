Ext._define('corregedoria.prontuary.individualperformance.exerciseinrole.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.exerciseinrole.Restful',

    width: 630,

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.prontuary.individualperformance.exerciseinrole.attachments.Grid', {
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
            this.getAttachmentsGrid().params = {detailexerciseinrole: this.oId,};
        } else {
            this.getAttachmentsGrid().disable();
        }
        this.getAttachmentsGrid().setFilterProperty('detailexerciseinrole_id', this.oId, 100);
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
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 80,
                                columnWidth: 0.85,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Cargo/Função',
                                        name: 'role',
                                        width: 420,

                                    }
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 80,
                                columnWidth: 0.15,
                                items: [
                                    {
                                        xtype: 'button',
                                        text: 'Importar...',
                                        scope: this,
                                        width: 90,
                                        handler: function() {
                                            Ext.Msg.show({
                                                title: 'Importação...',
                                                msg: 'Em desenvolvimento...',
                                                icon: Ext.Msg.INFO,
                                                buttons: Ext.Msg.OK
                                            });
                                        },
                                    }
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
                                columnWidth: 0.25,
                                labelWidth: 35,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Início',
                                        width: 100,
                                        name: 'date_initial',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.75,
                                labelWidth: 25,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Ato',
                                        name: 'act_initial',
                                        width: 420,

                                    }
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
                                columnWidth: 0.25,
                                labelWidth: 25,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Fim',
                                        width: 100,
                                        name: 'date_final',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.75,
                                labelWidth: 25,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Ato',
                                        name: 'act_final',
                                        width: 420,

                                    }
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
        corregedoria.prontuary.individualperformance.exerciseinrole.Window.superclass.constructor.call(this, cfg);
        this.observer(cfg);
    },

});
