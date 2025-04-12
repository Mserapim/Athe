Ext._define('edocs.protocolo.requestform.mobilereturnstatement.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormMobileReturnStatement',

    rest: 'edocs.protocolo.requestform.mobilereturnstatement.Restful',

    width: 900,

    getImeiField: function (cfg) {
        if (!this._imeiField) {
            this._imeiField = Ext._create('Ext.form.TextField', {
                fieldLabel: "IMEI nº",
                name: "imei",
                width: 300,
                allowBlank: false,
            });
        }

        return this._imeiField;
    },

    getPhoneNumberField: function (cfg) {
        if (!this._phoneNumberField) {
            this._phoneNumberField = Ext._create('Ext.form.TextField', {
                fieldLabel: "Nº da linha",
                name: "phone_number",
                width: 300,
                allowBlank: false,
            });
        }

        return this._phoneNumberField;
    },

    getPhoneDescriptionField: function (cfg) {
        if (!this._phoneDescriptionField) {
            this._phoneDescriptionField = Ext._create('Ext.form.TextField', {
                fieldLabel: "Modelo",
                name: "phone_description",
                anchor: '99%',
                allowBlank: false,
                maxLength: 256,
            });
        }

        return this._phoneDescriptionField;
    },

    getSuccessorField: function (cfg) {
        if (!this._successorField) {
            this._successorField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Servidor',
                name: 'successor',
                rest: 'rh.employee.Restful',
                anchor: '100%',
                allowBlank: false,
            });
        }

        return this._successorField;
    },

    getBatteryChargerField: function (cfg) {
        if (!this._batteryChargerField) {
            this._batteryChargerField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Carregador de bateria',
                hideLabel: true,
                name: 'returned_battery_charger',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._batteryChargerField;
    },

    getHeadphoneField: function (cfg) {
        if (!this._headphoneField) {
            this._headphoneField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Fone de ouvido',
                hideLabel: true,
                name: 'returned_headphone',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._headphoneField;
    },

    getSIMEjectorField: function (cfg) {
        if (!this._simEjectorField) {
            this._simEjectorField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Extrator de chip',
                hideLabel: true,
                name: 'returned_sim_ejector',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._simEjectorField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                labelWidth: 90,
                items: [
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '3px' },
                        items: [
                            this.getCodeField(cfg),
                            {
                                xtype: 'container',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 2.75,
                                        items: this.getHomeCourtField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.25,
                                        labelWidth: 50,
                                        items: this.getDocumentTypeField('TERMO DE DEVOLUÇÃO')  // mixin
                                    }
                                ]
                            },
                            this.getSubjectField(cfg, {
                                value: 'Termo de Devolução de Celular Institucional',
                                readOnly: true,
                            }),
                            this.getControlContainer(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '1px' },
                        title: 'Informações do bem',
                        layout: 'form',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.0,
                                        items: this.getImeiField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.0,
                                        labelWidth: 85,
                                        items: this.getPhoneNumberField(cfg)
                                    }
                                ]
                            },
                            this.getPhoneDescriptionField(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '1px' },
                        title: 'Acessórios entregues',
                        layout: 'form',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'hbox',
                                defaults: {
                                    style: {
                                        marginRight: '25px',
                                        position: 'static',
                                        float: 'left'
                                    },
                                },
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        items: this.getBatteryChargerField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        items: this.getHeadphoneField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        items: this.getSIMEjectorField(cfg)
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '1px' },
                        title: 'Guarda temporária',
                        layout: 'form',
                        items: [
                            this.getSuccessorField(cfg),
                        ]
                    }
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getMainPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Termo de Devolução (Celular)',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.mobilereturnstatement.Window',
    specialType: 'mobilereturnstatement',
    group: 'Celular Institucional'
});
