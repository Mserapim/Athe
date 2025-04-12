/**
 *
 **/
Ext._define('edocs.processo.situacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.situacao.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        width: 240,
                        xtype: 'textfield',
                        name: 'nome',
                        fieldLabel: 'Situação',
                        allowBlank: false,
                    },
                ]
            });

        return this._formPanel;
    }
});
