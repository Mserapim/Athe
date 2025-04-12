Ext._define('edocs.protocolo.requestform.debitauthorization.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormDebitAuthorization',

    rest: 'edocs.protocolo.requestform.debitauthorization.Restful',

    width: 900,

    getDebitPercentageField: function (cfg) {
        if (!this._debitPercentageField) {
            this._debitPercentageField = Ext._create('Ext.form.NumberField', {
                fieldLabel: "Débito (em %)",
                name: "debit_percentage",
                width: 200,
                allowBlank: true,
                maxLength: 5
            });
        }

        return this._debitPercentageField;
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
                        value: 'Autorização de Débito (Parceria Solidária II)',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getDebitPercentageField(cfg)
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 'auto',
                autoHeight: true,
                items: this.getMainPanel(cfg)
            });

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Autorização de Débito (Parceria Solidária II)',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.debitauthorization.Window',
    specialType: 'debitauthorization',
    group: 'Autorização de débitos',
});
