/**
 *
 **/
Ext._define('rh.pessoa.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.pessoa.Restful',

    // width: 400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'nome',
                        fieldLabel: 'Nome',
                        allowBlank: false,
                        width: 250,
                    }
                ]
            });

        return this._formPanel;
    }
});
