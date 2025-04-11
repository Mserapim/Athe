Ext._define('edocs.protocolo.requestform.fulltimehomeoffice.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormFullTimeHomeOffice',

    rest: 'edocs.protocolo.requestform.fulltimehomeoffice.Restful',

    width: 900,

    getStartDateField: function (cfg) {
        if (!this._startDateField) {
            this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Início do período de teletrabalho",
                name: "start_date",
                width: 200
            });
        }

        return this._startDateField;
    },

    getElderlyField: function (cfg) {
        if (!this._elderlyField) {
            this._elderlyField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Idosos',
                name: 'elderly',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._elderlyField;
    },

    getPregnantField: function (cfg) {
        if (!this._pregnantField) {
            this._pregnantField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Gestantes',
                name: 'pregnant',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._pregnantField;
    },

    getChronicDiseasesField: function (cfg) {
        if (!this._chronicDiseasesField) {
            this._chronicDiseasesField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Portadores de doenças crônicas: hipertensão e diabetes, doenças autoimunes, imunossupressoras, dentre outras',
                name: 'chronic_diseases',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._chronicDiseasesField;
    },

    getPneumopathyDiseasesField: function (cfg) {
        if (!this._pneumopathyDiseasesField) {
            this._pneumopathyDiseasesField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Portadores de pneumopatias: asma, bronquite e doença pulmonar obstrutiva crônica, dentre outras',
                name: 'pneumopathy_diseases',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._pneumopathyDiseasesField;
    },

    getKidneyDiseasesField: function (cfg) {
        if (!this._kidneyDiseasesField) {
            this._kidneyDiseasesField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Portadores de doenças renais',
                name: 'kidney_diseases',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._kidneyDiseasesField;
    },

    getCardiovascularDiseasesField: function (cfg) {
        if (!this._cardiovascularDiseasesField) {
            this._cardiovascularDiseasesField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Portadores de doenças cardiovasculares graves, insuficiência cardíaca, revascularizados, infartados',
                name: 'cardiovascular_diseases',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._cardiovascularDiseasesField;
    },

    getObeseField: function (cfg) {
        if (!this._obeseField) {
            this._obeseField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Pessoas com obesidade - IMC superior a 35 e outras comorbidades que possam agravar o estado geral de saúde em virtude do contágio pela COVID-19',
                name: 'obese',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._obeseField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                autoHeight: true,
                height: 'auto',
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '3px' },
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
                                        items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 60,
                                items: this.getSubjectField(cfg, {
                                    value: 'Requerimento de Teletrabalho Integral - Grupo de Risco',
                                    readOnly: true,
                                }),
                            },
                            this.getControlContainer(cfg),
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 190,
                                items: this.getStartDateField(cfg)
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        style: { marginBottom: '1px' },
                        title: 'Condição (Grupo de Risco)',
                        layout: 'form',
                        labelWidth: 1,
                        items: [
                            this.getElderlyField(cfg),
                            this.getPregnantField(cfg),
                            this.getChronicDiseasesField(cfg),
                            this.getPneumopathyDiseasesField(cfg),
                            this.getKidneyDiseasesField(cfg),
                            this.getCardiovascularDiseasesField(cfg),
                            this.getObeseField(cfg),
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
                height: 'auto',
                autoHeight: true,
                items: [
                    this.getMainPanel(cfg),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 200,
                        items: this.getAttachmentPanel(cfg)
                    }
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Teletrabalho Integral (Grupo de Risco)',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.fulltimehomeoffice.Window',
    specialType: 'fulltimehomeoffice',
    group: 'Teletrabalho'
});
