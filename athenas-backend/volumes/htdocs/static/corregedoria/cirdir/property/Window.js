Ext._define('corregedoria.cirdir.property.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.property.Restful',

    width: 800,

    getIRSCodeField: function(cfg) {
        if(!this._irscodeField) {
            this._irscodeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Classificação IR',
                allowBlank: true,
                rest: "corregedoria.cirdir.irscode.Restful",
                name: "irscode",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                    preFilter: [
                          { property: 'type_irscode', value: 1, stage: 100 },
                    ],
                }
            });
        }
        return this._irscodeField;
    },

    getCountryField: function(cfg) {
        if(!this._countryField) {
            this._countryField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'País',
                allowBlank: true,
                rest: "rh.country.Restful",
                name: "country",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._countryField;
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
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 30,
                                columnWidth: 0.20,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tipo',
                                        hiddenName: 'kind',
                                        width: 105,
                                        choiceId: 'cirdir.KIND',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 85,
                                columnWidth: 0.80,
                                items: [
                                    this.getIRSCodeField(cfg),
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 60,
                        items: [
                            {
                                xtype: 'htmleditor',
                                fieldLabel: 'Descrição',
                                name: "description",
                                height: 125,
                                width: 707,
                                enableLinks: false,
                                enableLists: false,
                                enableFont: false,
                                enableColors: false,
                                enableSourceEdit: false,
                                enableFontSize: false,
                                enableAlignments: false,
                                style: {fontSize: '11px'},
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
                                labelWidth: 125,
                                columnWidth: 0.35,
                                items: [
                                    {
                                        xtype: 'currencyfield',
                                        decimalPrecision: 2,
                                        fieldLabel: 'Valor em 31/12/'+(cfg.params.year-1),
                                        allowBlank: false,
                                        allowDecimals: true,
                                        name: 'current_value',
                                        width: 120,
                                        style: {
                                          textAlign: 'right',
                                        }
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 25,
                                columnWidth: 0.30,
                                items: [
                                    this.getCountryField(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        corregedoria.cirdir.property.Window.superclass.constructor.call(this, cfg);
    },

});
