Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteRestful',
    width: 400,

    getFormPanel: function (cfg) {
        me = this;
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelAlign: 'top',
                listeners: {
                    render: function () {

                        if (cfg.params.solicitation) {
                            this.getForm().findField('solicitation').setValue(cfg.params.solicitation);
                            this.getForm().findField('solicitation').disable();
                        }
                        if (cfg.params.origin) {
                            this.getForm().findField('origin').setValue(cfg.params.origin);
                            this.getForm().findField('origin').disable();
                        }
                        if (cfg.params.kind) {
                            this.getForm().findField('kind').setValue(cfg.params.kind);
                            this.getForm().findField('kind').disable();
                        }
                        if (cfg.params.classification) {
                            this.getForm().findField('classification').setValue(cfg.params.classification);
                            this.getForm().findField('classification').disable();
                        }

                    }
                },

                items: [
                    this.getSolicitation(cfg),
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Origem do Empenho',
                        hiddenName: 'origin',
                        choiceId: 'contrato.MINUTE_COMMITMENT_ORIGIN',
                        anchor: '99%'
                    },
                    {
                        maxLength: 20,
                        allowBlank: false,
                        fieldLabel: "Número NE",
                        name: "number",
                        xtype: "textfield",
                        anchor: '99%'
                    },
                    {
                        xtype: "currencyfield",
                        fieldLabel: "Valor (R$)",
                        allowBlank: false,
                        name: "value",
                        width: 370
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo de NE',
                        hiddenName: 'kind',
                        choiceId: 'contrato.TIPO_NE',
                        anchor: '99%'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Classificação da NE',
                        hiddenName: 'classification',
                        choiceId: 'contrato.CLASSIFICACAO_NE',
                        anchor: '99%'
                    },

                ]
            });

        return this._formPanel;
    },

    getSolicitation: function (cfg) {
        if (!this._solicitationField) {
            this._solicitationField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Pedido',
                name: 'solicitation',
                rest: 'planning.hiring.minutesolicitation.MinuteSolicitationRestful',
                preFilter: [
                    { property: 'minute', value: cfg.params.minute, stage: 100 },
                    { property: 'situation__in', value: [3, 6, 7], stage: 101 },
                ]
            });
        }

        return this._solicitationField;
    },

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});

        planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteWindow.superclass.constructor.call(this, cfg);
    },
});
