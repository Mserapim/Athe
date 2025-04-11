Ext._define('edocs.protocolo.requestform.healthcareallowance.activeemployee.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFHealthcareActiveEmployee',

    rest: 'edocs.protocolo.requestform.healthcareallowance.activeemployee.Restful',

    width: 900,

    getRequestTypeField: function (cfg) {
        return this.getChoiceFieldSet({
            title: 'Tipo de requerimento',
            name: 'request_type',
            value: (cfg.values || {}).request_type,
            choiceId: 'requestform.HEALTHCARE_ACTIVE_EMP_REQTYPE',
        });
    },

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
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
                                    items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                                },
                            ]
                        },
                        this.getSubjectField(cfg, {
                            value: 'Requerimento PASS - Programa de Assistência à Saúde Suplementar',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
                this.getRequestTypeField(cfg),
            ],
        });

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (this._formPanel) {
            return this._formPanel;
        }

        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            items: [
                this.getMainPanel(cfg),
                {
                    layout: 'vbox',
                    border: false,
                    height: 200,
                    items: this.getAttachmentPanel(cfg)
                },
            ],
        });

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento PASS - Programa de Assistência à Saúde Suplementar',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.healthcareallowance.activeemployee.Window',
    specialType: 'healthcareallowanceforactiveemployee',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
