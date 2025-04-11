/**
 *
 **/
Ext._define('common.siatu.atendente.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.atendente.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 55,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Usuário",
                        labelWidth: 50,
                        allowBlank: true,
                        rest: "auth.UserRestful",
                        name: "usuario",
                        emptyText: 'Usuário',
                        gridConfig: {
                            configOrderToolBar: ['search', '->'],
                            hideColumns: ['pk', 'is_active', 'is_staff', 'is_superuser']
                        }
                    }
                ]
            });

        return this._formPanel;
    }
});
