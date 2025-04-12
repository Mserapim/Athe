
Ext._define('planning.hiring.manager.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.manager.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Fiscal",
                        name: "user",
                        xtype: "rest-autocompletefield",
                        rest: "auth.UserRestful"
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Função",
                        name: "tipo",
                        choiceId: "contrato.TIPO_GESTOR",
                        xtype: "choicefield",
                        hiddenName: "tipo"
                    },
                ]
            });

        return this._formPanel;
    },
});
