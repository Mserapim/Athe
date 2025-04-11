Ext._define('corregedoria.scoretable.bandscoretable.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.scoretable.bandscoretable.Restful',

    width: 530,

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
                        labelWidth: 55,
                        items: [
                            {
                                xtype: 'textfield',
                                fieldLabel: 'Descrição',
                                name: 'label',
                                hideLabel: false,
                                width: 435,
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Faixa / Pontuação',
                        hideLabel: true,
                        autoHeight: true,
                        collapsible: false,
                        width: 500,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 80,
                                        columnWidth: 0.34,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'numberfield',
                                                fieldLabel: 'Início da Faixa',
                                                name: 'initial_value',
                                                hideLabel: false,
                                                width: 60,
                                                allowNegative: false,
                                                
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 77,
                                        columnWidth: 0.33,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'numberfield',
                                                fieldLabel: 'Final da Faixa',
                                                name: 'end_value',
                                                hideLabel: false,
                                                width: 60,
                                                allowBlank: true,
                                                allowNegative: false,
                                                
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 63,
                                        columnWidth: 0.33,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'numberfield',
                                                fieldLabel: 'Pontuação',
                                                name: 'score',
                                                hideLabel: false,
                                                width: 80,
                                                allowDecimals: false,
                                            },
                                        ]
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
