/**
 *
 **/
Ext._define('adm.patrimonio.baixa.Window', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.baixa.Restful',

    width: 550,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                defaults: {
                },
                labelWidth: 140,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Conta Patrimonial',
                        name: 'conta',
                        rest: 'adm.patrimonio.parametro.ContaRestful',
                        gridColumnAction: false
                    },
                    {
                        fieldLabel: 'Processo',
                        xtype: 'textfield',
                        name: 'processo'
                    },
                    {
                        fieldLabel: 'Documento',
                        xtype: 'textfield',
                        name: 'documento'
                    },
                    {
                        fieldLabel: 'Data do documento',
                        xtype: 'datefield',
                        name: 'data_documento'
                    },
                    {
                        fieldLabel: 'Nota de Lançamento',
                        xtype: 'textfield',
                        name: 'liquidacao'
                    },
                    {
                        fieldLabel: 'Data do Lançamento',
                        xtype: 'datefield',
                        name: 'data_liquidacao'
                    }
                ]
            });

        return this._formPanel;
    }
});
