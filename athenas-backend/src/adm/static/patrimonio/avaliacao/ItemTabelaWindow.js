/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemTabelaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.avaliacao.ItemTabelaRestful',

    width: 650,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 150,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Grupo',
                        name: 'grupo',
                        allowBlank: false,
                        rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',
                        readOnly: true
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Especie',
                        name: 'especie',
                        allowBlank: true,
                        rest: 'adm.patrimonio.parametro.EspecieRestful',
                        readOnly: true
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Vida útil',
                        name: 'vida_util',
                        allowBlank: false
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Taxa de Depreciação',
                        name: 'depreciacao',
                        allowBlank: false
                    },
                    {
                        xtype: 'numberfield',
                        fieldLabel: 'Valor Residual',
                        name: 'residual',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    }
});
