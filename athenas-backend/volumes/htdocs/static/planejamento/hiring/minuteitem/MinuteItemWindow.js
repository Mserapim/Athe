Ext._define('planning.hiring.minuteitem.MinuteItemWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minuteitem.MinuteItemRestful',
    width: 1000,

    getMainTab: function (cfg) {
        if (!this._mainTab) {
            this._mainTab = Ext._create('Ext.Panel', {
                title: 'Item',
                labelAlign: 'top',
                frame: true,
                layout: 'form',
                flex: 1.0,
                height: 570,
                items: [
                    this.getMinuteItemGroup(),
                    {

                        fieldLabel: "Grupo ou Item",
                        xtype: "textfield",
                        name: "group",
                        allowBlank: false,
                        listeners: {
                            render: function () {
                                this.hide();
                            }
                        }
                    },
                    {
                        layout: 'column',
                        labelAlign: 'top',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        fieldLabel: "Item ou Linha",
                                        xtype: "textfield",
                                        allowBlank: false,
                                        name: "line",
                                        anchor: '90%',
                                        listeners: {
                                            scope: this,
                                            render: function (field) {
                                                field.focus(false, 500);

                                                if (this.oId != undefined) {
                                                    if (this.getFormPanel().getForm().findField('line').value == '') {
                                                        var setline = this.getFormPanel().getForm().findField('group').getValue();
                                                        this.getFormPanel().getForm().findField('line').setValue(setline);
                                                    }
                                                }

                                            }
                                        }
                                    },
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'radiogroup',
                                        fieldLabel: 'Gera contrato? ',
                                        columns: 2,
                                        anchor: '50%',
                                        items: [
                                            {
                                                xtype: 'radio',
                                                inputValue: 'True',
                                                boxLabel: 'Sim',
                                                checked: this.values.generate_agreement == true,
                                                name: 'generate_agreement'
                                            },
                                            {
                                                xtype: 'radio',
                                                inputValue: 'False',
                                                boxLabel: 'Não',
                                                checked: this.values.generate_agreement == false,
                                                name: 'generate_agreement',
                                            },
                                        ]
                                    },
                                ]
                            }

                        ]
                    },
                    {
                        fieldLabel: "Descrição",
                        xtype: "ckeditor",
                        allowBlank: false,
                        name: "description",
                        height: 120,
                        width: 470,
                        startupFocus: false
                    },
                    {
                        fieldLabel: "Marca/Modelo",
                        xtype: "textfield",
                        allowBlank: true,
                        name: "brand",
                        width: '97%',
                    },
                    {
                        layout: 'column',
                        labelAlign: 'top',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                {
                                    fieldLabel: "Quantidade",
                                    xtype: "numberfield",
                                    name: "quantity",
                                    width: '97%',
                                }
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                {
                                    fieldLabel: 'Unidade de Medida',
                                    xtype: 'choicefield',
                                    hiddenName: 'unit_measure',
                                    choiceId: 'contrato.MINUTE_ITEM_UNIT_MEASURE',
                                    editable: true,
                                    width: 230
                                }

                            }
                        ]
                    },
                    {
                        layout: 'column',
                        labelAlign: 'top',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                {
                                    fieldLabel: "Valor Unitário",
                                    xtype: 'currencyfield',
                                    name: "unitary_value",
                                    width: 230
                                }
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items:
                                    this.getTotalValueField()
                            }
                        ]
                    },
                ]

            });

        }

        return this._mainTab;
    },

    getMinuteItemGroup: function () {
        if (!this._minuteItemGroup) {
            this._minuteItemGroup = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Grupo",
                allowBlank: true,
                rest: "planning.hiring.minuteitem.MinuteItemRestful",
                name: "parent",
                autoLoad: true,
                listeners: {
                    scope: this,
                    render: function () {
                        this.getMinuteItemGroup().setPreFilter([
                            { property: 'minute', value: this.params.minute, stage: 100 },
                            // Não haverá mais unit_measure vazio
                            // { property: 'unit_measure', value: null, stage: 101 },
                            { property: 'quantity', value: null, stage: 101 },
                            { property: 'unitary_value', value: null, stage: 102 },
                        ]);
                    }
                }

            });

        }

        return this._minuteItemGroup;
    },

    getMinuteItemPanel: function (cfg) {
        if (!this._minuteSolicitationPanel) {
            this._minuteSolicitationPanel = Ext._create('Ext.Panel', {
                title: 'Itens',
                layout: 'hbox',
                height: 560,
                items: [
                    this.getMainTab(cfg),
                    this.getComplementaryDescriptionGrid(),
                ],
            });
        }

        return this._minuteSolicitationPanel;
    },

    getTotalValueField: function () {
        if (!this._totalValueField)
            this._totalValueField = Ext._create('Ext.form.DisplayField', {
                fieldLabel: "Valor Total",
                name: "total_value",
            });

        return this._totalValueField;
    },

    getComplementaryDescriptionGrid: function () {
        if (!this._complementaryDescriptionTab)
            this._complementaryDescriptionTab = Ext._create('planning.hiring.minuteitem.MinuteItemComplementaryDescriptionGrid', {
                region: 'center',
                hideItemsToolbar: ['search', 'download'],
                title: 'Descrição Complementar',
                height: 570,
                flex: 1.0,
            });

        return this._complementaryDescriptionTab;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    new Ext._create('Ext.TabPanel', {
                        activeTab: 0,
                        items: [
                            this.getMinuteItemPanel(cfg),
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    minuteItem: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._minuteItem = value;

            if (observe)
                this.observeMinuteItem();
        }

        return this._minuteItem;
    },

    observeMinuteItem: function () {
        var value = this.minuteItem();

        if (value) {

            this.getComplementaryDescriptionGrid().enable();
            this.getComplementaryDescriptionGrid().setParam('minuteitem', value);
            this.getComplementaryDescriptionGrid().setFilterProperty('minuteitem', value, 0);

            Ext.Ajax.request({
                scope: this,
                url: toolkit.util.Normalize.controller_action(
                    'PHMMinuteItem',
                    'total_value_display'
                ),
                params: {
                    pk: value
                },
                success: function (response) {
                    var rst = Ext.decode(response.responseText);
                    this.getTotalValueField().setValue(rst.total_value_display);
                },
                failure: function (response) {
                    Ext.Msg.show({
                        title: 'Buscando valor total',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }

            });
        } else {
            /* Descrição complementar */
            this.getComplementaryDescriptionGrid().disable();
            this.getComplementaryDescriptionGrid().setParam('minuteitem', 0);
            this.getComplementaryDescriptionGrid().setFilterProperty('minuteitem', value, 0, false);
            this.getComplementaryDescriptionGrid().getStore().removeAll();
        }
    },

    getButtons: function (cfg) {

        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if (cfg.action == 'create')
                this._buttons = [{
                    text: 'Novo',
                    scope: this,
                    handler: function () {
                        this.action = 'create';
                        var parent = this.getFormPanel().getForm().findField('parent').getValue();
                        this.getFormPanel().getForm().reset();
                        this.getFormPanel().getForm().findField('line').focus();
                        this.getComplementaryDescriptionGrid().disable();
                        this.getComplementaryDescriptionGrid().setParam('minuteitem', 0);
                        this.getComplementaryDescriptionGrid().setFilterProperty('minuteitem', 0, 0, false);
                        this.getComplementaryDescriptionGrid().getStore().removeAll();
                        this.getFormPanel().getForm().findField('parent').setValue(parent);
                    }
                }].concat(this._buttons);

            if (!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    tabIndex: 3,
                    handler: function () {
                        this.save(false);
                    },

                }].concat(this._buttons);



        }

        return this._buttons;
    },
    constructor: function (cfg) {
        cfg = cfg || {};

        if (cfg.action == 'update')
            this.values = cfg.values;
        else
            this.values = { 'generate_agreement': null };

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.minuteItem(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }

        });

        planning.hiring.minuteitem.MinuteItemWindow.superclass.constructor.call(this, cfg);

        this.minuteItem(cfg.oId === undefined ? null : cfg.oId);
    }
});
