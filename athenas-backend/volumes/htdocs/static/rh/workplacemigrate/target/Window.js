Ext._define('rh.workplacemigrate.target.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.workplacemigrate.target.Restful',

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Migração de Lotação',
                        allowBlank: true,
                        rest: 'rh.workplacemigrate.Restful',
                        name: 'workplace_migrate',
                        readOnly: true
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        hiddenName: 'type_of_target',
                        choiceId: 'rh.APP_TO_MIGRATE',
                    },
                ]
            });
        return this._formPanel;
    },
});

