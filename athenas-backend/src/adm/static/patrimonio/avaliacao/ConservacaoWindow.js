/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ConservacaoWindow', {
    extend: 'adm.patrimonio.avaliacao.ParametroWindow',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        fieldLabel: 'Conceito',
                        hiddenName: 'variavel',
                        xtype: 'combo',
                        store: [
                            [1, 'Novo'],
                            [2, 'Bom'],
                            [3, 'Regular'],
                            [4, 'Inservivel'],
                        ],
                        value: 1,
                        lazyRender: true,
                        typeAhead: true,
                        width: 100,
                        mode: 'local',
                        triggerAction: 'all'
                    },
                    {
                        fieldLabel: 'Valor',
                        xtype: 'numberfield',
                        width: 60,
                        name: 'valor',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    }
});
