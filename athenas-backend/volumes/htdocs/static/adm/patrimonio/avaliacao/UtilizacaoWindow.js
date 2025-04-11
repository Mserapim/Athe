/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.UtilizacaoWindow', {
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
                            [1, 'Menos de um ano'],
                            [2, '1 ano'],
                            [3, '2 anos'],
                            [4, '3 anos'],
                            [5, '4 anos'],
                            [6, '5 anos'],
                            [7, '6 anos'],
                            [8, '7 anos'],
                            [9, '8 anos'],
                            [10, '9 anos'],
                            [11, '10 anos ou mais'],
                        ],
                        value: 1,
                        lazyRender: true,
                        typeAhead: true,
                        width: 150,
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
