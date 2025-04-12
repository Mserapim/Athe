Ext._define('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartselectoral.Restful',

    width: 600,

    getActionTypeField: function(cfg) {
        if(!this._actionTypeField) {
            this._actionTypeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Ação de",
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

    getParttTypeField: function(cfg) {
        if(!this._partTypeField) {
            this._partTypeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Tipo de Peça",
                allowBlank: true,
                rest: "judicial.taxonomy.LegalMovimentRestful",
                name: "part_type",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._partTypeField;
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
                        labelWidth: 50,
                        items: [
                            this.getActionTypeField(cfg)
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 50,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Número',
                                name: 'action_number',
                                hideLabel: false,
                                width: 517,
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 75,
                        items: [
                            this.getParttTypeField(cfg)
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Cálculo da Pontuação',
                        hideLabel: true,
                        autoHeight: true,
                        collapsible: false,
                        width: 572,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 55,
                                        columnWidth: 0.85,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Relatório',
                                                name: 'report',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 400,
                                                height: 60,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 0.15,
                                        style: { paddingLeft: '5px' },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                columnWidth: 0.15,
                                                defaults: {
                                                    labelAlign: 'top',
                                                },
                                                layout: 'hbox',
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        items: [
                                                            {
                                                                xtype: 'numberfield',
                                                                fieldLabel: 'Nota',
                                                                value: 0,
                                                                minValue: 0,
                                                                maxValue: 1,
                                                                emptyText: 'Informe um valor entre 0.00 e 1.00',
                                                                name: 'report_score',
                                                                allowBlank: true,
                                                                hideLabel: false,
                                                                width: 75,
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight: true,
                                                style: {marginBottom: '5px', fontSize: '9px'},
                                                items: [
                                                    {
                                                        xtype: 'label',
                                                        text: 'Nota máxima: 1',
                                                    },
                                                ]
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
                                        labelWidth: 92,
                                        columnWidth: 0.85,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Fundamentação',
                                                name: 'basis',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 364,
                                                height: 60,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 0.15,
                                        style: { paddingLeft: '5px' },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                columnWidth: 0.15,
                                                defaults: {
                                                    labelAlign: 'top',
                                                },
                                                layout: 'hbox',
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        items: [
                                                            {
                                                                xtype: 'numberfield',
                                                                fieldLabel: 'Nota',
                                                                value: 0,
                                                                minValue: 0,
                                                                maxValue: 2,
                                                                emptyText: 'Informe um valor entre 0.00 e 2.00',
                                                                name: 'basis_score',
                                                                allowBlank: true,
                                                                hideLabel: false,
                                                                width: 75,
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight: true,
                                                style: {marginBottom: '5px', fontSize: '9px'},
                                                items: [
                                                    {
                                                        xtype: 'label',
                                                        text: 'Nota máxima: 2',
                                                    },
                                                ]
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
                                        columnWidth: 0.85,
                                        labelWidth: 40,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Provas',
                                                name: 'proof',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 415,
                                                height: 60,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 0.15,
                                        style: { paddingLeft: '5px' },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                columnWidth: 0.15,
                                                defaults: {
                                                    labelAlign: 'top',
                                                },
                                                layout: 'hbox',
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        items: [
                                                            {
                                                                xtype: 'numberfield',
                                                                fieldLabel: 'Nota',
                                                                value: 0,
                                                                minValue: 0,
                                                                maxValue: 1.5,
                                                                emptyText: 'Informe um valor entre 0.00 e 1.50',
                                                                name: 'proof_score',
                                                                allowBlank: true,
                                                                hideLabel: false,
                                                                width: 75,
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight: true,
                                                style: {marginBottom: '5px', fontSize: '9px'},
                                                items: [
                                                    {
                                                        xtype: 'label',
                                                        text: 'Nota máxima: 1.5',
                                                    },
                                                ]
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
                                        columnWidth: 0.85,
                                        labelWidth: 90,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Convencimento',
                                                name: 'convincily',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 365,
                                                height: 60,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 0.15,
                                        style: { paddingLeft: '5px' },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                columnWidth: 0.15,
                                                defaults: {
                                                    labelAlign: 'top',
                                                },
                                                layout: 'hbox',
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        items: [
                                                            {
                                                                xtype: 'numberfield',
                                                                fieldLabel: 'Nota',
                                                                value: 0,
                                                                minValue: 0,
                                                                maxValue: 1.5,
                                                                emptyText: 'Informe um valor entre 0.00 e 1.50',
                                                                name: 'convincily_score',
                                                                allowBlank: true,
                                                                hideLabel: false,
                                                                width: 75,
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight: true,
                                                style: {marginBottom: '5px', fontSize: '9px'},
                                                items: [
                                                    {
                                                        xtype: 'label',
                                                        text: 'Nota máxima: 1.5',
                                                    },
                                                ]
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
                                        columnWidth: 0.85,
                                        labelWidth: 55,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Redação',
                                                name: 'redaction',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 400,
                                                height: 60,
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        columnWidth: 0.15,
                                        style: { paddingLeft: '5px' },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                columnWidth: 0.15,
                                                defaults: {
                                                    labelAlign: 'top',
                                                },
                                                layout: 'hbox',
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        items: [
                                                            {
                                                                xtype: 'numberfield',
                                                                fieldLabel: 'Nota',
                                                                value: 0,
                                                                minValue: 0,
                                                                maxValue: 1,
                                                                emptyText: 'Informe um valor entre 0.00 e 1.00',
                                                                name: 'redaction_score',
                                                                allowBlank: true,
                                                                hideLabel: false,
                                                                width: 75,
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'panel',
                                                autoHeight: true,
                                                style: {marginBottom: '5px', fontSize: '9px'},
                                                items: [
                                                    {
                                                        xtype: 'label',
                                                        text: 'Nota máxima: 1',
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                            // {
                            //     xtype:'panel',
                            //     autoHeight:true,
                            //     labelWidth: 63,
                            //     layout: 'form',
                            //     items: [
                            //         {
                            //             xtype: 'numberfield',
                            //             fieldLabel: 'Pontuação',
                            //             value: 0,
                            //             minValue: 0,
                            //             maxValue: 7,
                            //             emptyText: 'Informe um valor entre 0.00 e 7.00. Ex.: 6.95',
                            //             name: 'score',
                            //             hideLabel: false,
                            //             allowBlank: true,
                            //             width: 300,
                            //         },
                            //     ]
                            // },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 77,
                        layout: 'form',
                        items: [
                            {
                                xtype: 'textarea',
                                fieldLabel: 'Observações',
                                name: 'observation',
                                hideLabel: false,
                                allowBlank: true,
                                width: 487,
                                height: 50,
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
