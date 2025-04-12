/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.TabelaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.avaliacao.TabelaRestful',

    width: 500,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Numero',
                        name: 'numero_formatado',
                        value: 'indefinido'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Publicação",
                        allowBlank: true,
                        rest: "rh.publicacao.Restful",
                        name: "publicacao"
                    },
                    {
                        fieldLabel: 'Data de vigencia',
                        xtype: 'datefield',
                        name: 'data_vigencia',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    }
});
