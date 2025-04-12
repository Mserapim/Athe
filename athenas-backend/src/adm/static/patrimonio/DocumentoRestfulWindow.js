/**
 *
 **/
Ext._define('adm.patrimonio.DocumentoRestfulWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.DocumentoRestful',

    width: 450,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                   width: 315
                },
                items: [
                    {
                        fieldLabel: 'Título',
                        name: 'titulo',
                        xtype: 'textfield'
                    },
                    {
                        fieldLabel: 'Arquivo',
                        name: 'data',
                        hiddenName: 'data',
                        xtype: 'ged-fileuploadfield'
                    }
                ]
            });

        return this._formPanel;
    }
});
