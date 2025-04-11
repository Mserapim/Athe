Ext._define('rh.gfp.estrutura_salarial.ReferenciaSalarioWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.ReferenciaSalarioRestful',

    width: 600,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                bodyStyle:'padding:5px',
                items: [
                    Ext._create('core.fields.AutocompleteField', {
                        fieldLabel: 'Referência',
                        name: 'referencia_nivel2d',
                        displayField: 'sigla_cache',
                        allowBlank: false,
                        rest: 'rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful',
                        // readOnly: true,
                    }),
                    {
                        xtype:'numberfield',
                        fieldLabel: 'Valor',
                        name: 'valor',
                    },{
                        xtype:'numberfield',
                        fieldLabel: 'Gratificação',
                        name: 'gratificacao',
                    },{
                        xtype:'numberfield',
                        fieldLabel: 'Valor Membro',
                        name: 'valor_membro',
                    },{
                        xtype:'numberfield',
                        fieldLabel: 'Gratif. Membro',
                        name: 'gratificacao_membro',
                    },
                ],

            });

        return this._formPanel;
    },
});
