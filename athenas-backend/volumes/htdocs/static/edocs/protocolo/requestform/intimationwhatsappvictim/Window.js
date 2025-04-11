Ext._define('edocs.protocolo.requestform.intimationwhatsappvictim.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestIntimationWhatsAppVictim',

    rest: 'edocs.protocolo.requestform.intimationwhatsappvictim.Restful',

    width: 900,

    getIntimateNameField: function (cfg) {
        if (!this._intimateNameField) {
            this._intimateNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome do indiciado(a)',
                name: 'name_intimate',
                width: 200,
                allowBlank: true
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
                allowBlank: true
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

    getVictimNameField: function (cfg) {
        if (!this._victimNameField) {
            this._victimNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome da vítima',
                name: 'name_victim',
                width: 200,
                allowBlank: true
            });
        }

        return this._victimNameField;
    },

    getVictimCpfField: function (cfg) {
        if (!this._victimCpfField) {
            this._victimCpfField = Ext._create('core.fields.CpfField', {
                fieldLabel: 'CPF da vítima',
                name: 'cpf_victim',
                width: 200,
                allowBlank: true
            });
        }

        return this._victimCpfField;
    },

    getVictimPanel: function (cfg) {
        if (this._victimPanel) {
            return this._victimPanel;
        }

        this._victimPanel = Ext._create('Ext.Panel', {
            title: 'Vítima',
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
                                    items: this.getVictimNameField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.5,
                                    items: this.getVictimCpfField(cfg)
                                },
                            ]
                        },
                    ],
                },
            ],
        });

        return this._victimPanel;
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
                            value: 'Intimação por WHATSAPP com Autenticidade Verificável para a Vítima',
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
                    this.getIntimatePanel(cfg),
                    this.getVictimPanel(cfg),
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Intimação por WHATSAPP com Autenticidade Verificável para a Vítima',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.intimationwhatsappvictim.Window',
    specialType: 'intimationwhatsappauthenticityverifiablevictim',
    group: 'Intimações'
});
