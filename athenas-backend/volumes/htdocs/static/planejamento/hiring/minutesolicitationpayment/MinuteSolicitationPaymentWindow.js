Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationPaymentWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitation.MinuteSolicitationPaymentRestful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel){
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelAlign: 'top',
                items: [
                    this.getCommitmentNote(cfg),
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "textfield",
                                        maxLength: 100,
                                        allowBlank: true,
                                        fieldLabel: "Nota Fiscal",
                                        name: "invoice",
                                        anchor: '95%'
                                    },
                                ],
                            },
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "currencyfield",
                                        fieldLabel: "Valor (R$)",
                                        allowBlank: false,
                                        name: "value",
                                        width: 230
                                    },
                                ],
                            },
                        ]
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "datefield",
                                        allowBlank: true,
                                        fieldLabel: "Data inicial da referência",
                                        name: "start_reference_period",
                                        anchor: '95%'
                                    },
                                ],
                            },
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "datefield",
                                        allowBlank: true,
                                        fieldLabel: "Data final da referência",
                                        name: "end_reference_period",
                                        anchor: '98%'
                                    },
                                ],
                            },
                        ]
                    },
                    {
                        xtype: "ckeditor",
                        allowBlank: true,
                        fieldLabel: "Observação",
                        name: "observation",
                    },
            ]
            });
        }
        return this._formPanel;
    },

    getCommitmentNote: function(cfg){
        if(!this._commitmentNoteField){
            this._commitmentNoteField = Ext._create('core.fields.AutocompleteField',{
                fieldLabel: "NE",
                allowBlank: false,
                rest: "planning.hiring.minutesolicitation.MinuteSolicitationCommitmentNoteRestful",
                name: "commitmentnote",
                preFilter:[
                    {property:'solicitation__minute', value: cfg.params.minute, stage: 100},
                    {property:'parent', value: null, stage: 101},
                ]
            });
        }

        return this._commitmentNoteField;
    }
});

