Ext._define('corregedoria.prontuary.individualperformance.institutionalcontribution.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.prontuary.individualperformance.institutionalcontribution.Restful',

    width: 630,

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.prontuary.individualperformance.institutionalcontribution.attachments.Grid', {
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

    observer: function() {
        if (this.oId) {
            this.getAttachmentsGrid().enable();
            this.getAttachmentsGrid().params = {detailinstitutionalcontribution: this.oId,};
        } else {
            this.getAttachmentsGrid().disable();
        }
        this.getAttachmentsGrid().setFilterProperty('detailinstitutionalcontribution_id', this.oId, 100);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 75,
                        items: [
                            {
                                xtype: 'textarea',
                                fieldLabel: 'Contribuição',
                                name: 'contribution',
                                width: 521,

                            }
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
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
                    this.observer();
                }
            }
        });
        corregedoria.prontuary.individualperformance.institutionalcontribution.Window.superclass.constructor.call(this, cfg);
        this.observer();
    },

});
