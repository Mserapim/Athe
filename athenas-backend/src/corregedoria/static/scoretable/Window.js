Ext._define('corregedoria.scoretable.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.scoretable.Restful',

    width: 600,

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
                        labelWidth: 120,
                        items: [
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'Tabela de Pontuação',
                                hiddenName: 'score_table',
                                width: 440,
                                choiceId: 'corregedoria.SCORE_TABLE',
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 100,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Regulamentação',
                                name: 'ordination',
                                hideLabel: false,
                                width: 460,
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
                                labelWidth: 35,
                                columnWidth: 0.43,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Início',
                                        name: 'initial_validity',
                                        allowBlank: false,
                                        width: 160,
                                        blankText: 'Data da Inspeção precisa ser preenchida.',
                                    },
                                ]

                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 33,
                                columnWidth: 0.43,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Final',
                                        name: 'final_validity',
                                        width: 160,
                                        blankText: 'Data da Inspeção precisa ser preenchida.',
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.14,
                                items: [
                                    {
                                        xtype: 'checkbox',
                                        name: 'active',
                                        boxLabel: 'Ativo',
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
