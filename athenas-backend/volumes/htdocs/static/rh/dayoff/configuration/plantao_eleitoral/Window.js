Ext._define('rh.dayoff.configuration.plantao_eleitoral.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.dayoff.configuration.plantao_eleitoral.Restful',

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "titulo",
                        fieldLabel: "Título",
                        xtype: "textfield",
                        allowBlank: false
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Turno',
                        allowBlank: false,
                        lazyRender: true,
                        name: 'turno',
                        hiddenName: 'turno',
                        choiceId: 'dayoff.CONFIGURACAO_ELEITORAL_TURNO_CHOICE',
                        
                    },
                    {
                        name: "data",
                        fieldLabel: "Data",
                        xtype: "datefield",
                        allowBlank: false
                    },
                    {
                        name: "ativo",
                        fieldLabel: "Ativo",
                        xtype: "checkbox",
                        allowBlank: false,
                        checked: true,
                    },
                ],
            });

        return this._formPanel;
    },
});
