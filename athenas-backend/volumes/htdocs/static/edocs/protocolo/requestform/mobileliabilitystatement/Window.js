Ext._define('edocs.protocolo.requestform.mobileliabilitystatement.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormMobileLiabilityStatement',

    rest: 'edocs.protocolo.requestform.mobileliabilitystatement.Restful',

    width: 900,

    getImeiField: function (cfg) {
        if (!this._imeiField) {
            this._imeiField = Ext._create('Ext.form.TextField', {
                fieldLabel: "IMEI nº",
                name: "imei",
                width: 300,
                allowBlank: false
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
                allowBlank: false
            });
        }

        return this._phoneNumberField;
    },

    getDescriptionField: function (cfg) {
        if (!this._descriptionField) {
            this._descriptionField = Ext._create('Ext.Panel', {
                title: 'Descrição do bem',
                items: [{
                    xtype: 'ckeditor',
                    allowBlank: false,
                    height: 150,
                    anchor: '100%',
                    name: 'phone_description',
                    editorConfig: { toolbarStartupExpanded: true },
                    submitValue: true,
                }]
            });
        }

        return this._descriptionField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: false,
                border: false,
                layout: 'form',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'form',
                        frame: true,
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
                                        items: this.getDocumentTypeField('TERMO DE ENTREGA E RESPONSABILIDADE')  // mixin
                                    }
                                ]
                            },
                            this.getSubjectField(cfg, {
                                value: 'Termo de Entrega e Responsabilidade de Celular Institucional',
                                readOnly: true,
                            }),
                            this.getControlContainer(cfg),
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
                        ]
                    },
                    this.getDescriptionField(cfg),
                ]
            });

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
    title: 'Termo de Entrega e Responsabilidade (Celular)',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.mobileliabilitystatement.Window',
    specialType: 'mobileliabilitystatement',
    group: 'Celular Institucional'
});
