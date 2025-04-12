Ext._define('edocs.protocolo.requestform.transitpass.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormTransitPass',

    rest: 'edocs.protocolo.requestform.transitpass.Restful',

    width: 900,

    getRequestTypeField: function (cfg) {
        if (!this._requestTypeField) {
            this._requestTypeField = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'request_type',
                fieldLabel: 'Tipo requerimento',
                triggerAction: 'all',
                editable: false,
                allowBlank: false,
                anchor: '99%',
                mode: 'local',
                store: [
                    ['0', 'Autorização de desconto'],
                    ['1', 'Suspensão de desconto'],
                ]
            });
        }

        return this._requestTypeField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
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
                                items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento Vale Transporte',
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
                                items: this.getContactNumberField(cfg, { width: '80%' })
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.0,
                                labelWidth: 120,
                                items: this.getRequestTypeField(cfg)
                            }
                        ]
                    },
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
                items: this.getMainPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Vale Transporte',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.transitpass.Window',
    specialType: 'transitpass',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
