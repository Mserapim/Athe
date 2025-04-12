/**
 *
 **/
Ext._define('rh.pessoa.juridica.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.pessoa.juridica.Restful',

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
                    },
                    {
                        xtype: 'textfield',
                        name: 'cnpj',
                        fieldLabel: 'Cnpj',
                        maxLength: 18,
                        allowBlank: false,
                        width: 250,
                        maskRe: /^[0-9-.\\/]*$/,
                    }
                ]
            });

        return this._formPanel;
    }
});
