Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Restful',

    width: 600,

    getActionTypeField: function(cfg) {
        if(!this._actionTypeField) {
            this._actionTypeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "7.3 Ação de",
                allowBlank: true,
                rest: "judicial.taxonomy.LegalClassRestful",
                name: "action_type",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._actionTypeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 70,
                        items: [
                            this.getActionTypeField(cfg)
                            // {
                            //     xtype: 'choicefield',
                            //     fieldLabel: '7.3 Tipo da Ação',
                            //     hiddenName: 'action_type',
                            //     width: 455,
                            //     choiceId: 'inspection.ACTION_TYPE',
                            // },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 120,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: '7.4 Número do Feito',
                                name: 'action_number',
                                hideLabel: false,
                                width: 435,
                            },
                        ]
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: '7.5 Audiência de ',
                        hiddenName: 'audience_type',
                        width: 455,
                        choiceId: 'inspection.AUDIENCE_TYPE',
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.48,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'intimation',
                                        boxLabel: '7.6 Houve Intimação',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.52,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'presence',
                                        boxLabel: '7.7 Se fez presente ao ato',
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.48,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'questions',
                                        boxLabel: '7.8 Fez reperguntas',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.52,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'oral_manifestation',
                                        boxLabel: '7.9 Houve manifestação oral',
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
