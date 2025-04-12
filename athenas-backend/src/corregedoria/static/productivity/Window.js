Ext._define('corregedoria.productivity.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.productivity.Restful',

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
                        labelWidth: 110,
                        items: [
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'Produtividade',
                                hiddenName: 'productivity',
                                width: 440,
                                choiceId: 'raf.PRODUCTIVITY',
                            },
                        ]
                    },
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
                ]
            });

        return this._formPanel;
    },
});
