Ext._define('rh.gfp.estrutura_salarial.CargosEstruturaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.CargosEstruturaRestful',

    width: 600,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                bodyStyle:'padding:5px',
                items: [
                    Ext._create('core.fields.AutocompleteField', {
                        fieldLabel: 'Cargo',
                        name: 'cargo',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.jobposition.Restful',
                    }),
                    Ext._create('core.fields.AutocompleteField', {
                        fieldLabel: 'Publicação',
                        name: 'publicacao',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.publicacao.Restful',
                    }),{
                        xtype:'datefield',
                        fieldLabel: 'Início vigência',
                        name: 'data_vigencia_inicio',
                    },{
                        xtype:'datefield',
                        fieldLabel: 'Fim vigência',
                        name: 'data_vigencia_fim',
                    },
                ],

            });

        return this._formPanel;
    },
});
