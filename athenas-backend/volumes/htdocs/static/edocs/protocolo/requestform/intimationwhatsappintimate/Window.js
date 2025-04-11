Ext._define('edocs.protocolo.requestform.intimationwhatsappintimate.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestIntimationWhatsAppIntimate',

    rest: 'edocs.protocolo.requestform.intimationwhatsappintimate.Restful',

    width: 900,

    getIntimateNameField: function (cfg) {
        if (!this._intimateNameField) {
            this._intimateNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome do indiciado(a)',
                name: 'name_intimate',
                width: 200,
                allowBlank: false
            });
        }

        return this._intimateNameField;
    },

    getIntimateCpfField: function (cfg) {
        if (!this._intimateCpfField) {
            this._intimateCpfField = Ext._create('core.fields.CpfField', {
                fieldLabel: 'CPF do indiciado(a)',
                name: 'cpf_intimate',
                width: 200,
                allowBlank: false
            });
        }

        return this._intimateCpfField;
    },

    getIntimatePanel: function (cfg) {
        if (this._intimatePanel) {
            return this._intimatePanel;
        }

        this._intimatePanel = Ext._create('Ext.Panel', {
            title: 'Indiciado(a)',
            frame: true,
            layout: 'form',
            labelWidth: 110,
            items: [
                {
                    xtype: 'fieldset',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.5,
                                    items: this.getIntimateNameField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.5,
                                    items: this.getIntimateCpfField(cfg)
                                },
                            ]
                        },
                    ],
                },
            ],
        });

        return this._intimatePanel;
    }, 

    getInqueryPoliceField: function (cfg) {
        if (!this._inqueryPoliceField) {
            this._inqueryPoliceField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nº Inquérito Policial',
                name: 'number_inquiry_police',
                anchor: '50%',
                allowBlank: false
            });
        }

        return this._inqueryPoliceField;
    },

    getInqueryPolicePanel: function (cfg) {
        if (this._inqueryPolicePanel) {
            return this._inqueryPolicePanel;
        }

        this._inqueryPolicePanel = Ext._create('Ext.Panel', {
            title: 'Inquérito Policial',
            frame: true,
            layout: 'form',
            labelWidth: 120,
            items: [
                {
                    xtype: 'fieldset',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: 
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.75,
                                    items: this.getInqueryPoliceField(cfg)
                                },
                        },
                    ],
                },
            ],
        });

        return this._inqueryPolicePanel;
    }, 


    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            title: 'Informações',
            frame: true,
            layout: 'form',
            labelWidth: 90,
            items: [
                {
                    xtype: 'fieldset',
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
                                    style: 'margin-left: 15px',
                                    layout: 'form',
                                    flex: 1.25,
                                    labelWidth: 30,
                                    items: this.getDocumentTypeField('INTIMAÇÃO')  // mixin
                                },
                            ]
                        },
                        this.getSubjectField(cfg, {
                            value: 'Intimação por WHATSAPP com Autenticidade Verificável para o Indiciado(a)',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
            ],
        });

        return this._mainPanel;
    },


    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    this.getMainPanel(cfg),
                    this.getInqueryPolicePanel(cfg),
                    this.getIntimatePanel(cfg)
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Intimação por WHATSAPP com Autenticidade Verificável para o Indiciado(a)',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.intimationwhatsappintimate.Window',
    specialType: 'intimationwhatsappauthenticityverifiableintimate',
    group: 'Intimações'
});
