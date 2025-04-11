/**
 *
 **/
Ext._define('adm.patrimonio.baixa.DoacaoWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.DoacaoRestful',

    getFormPanel: function() {
        if(!this._formPanel) {
            this._formPanel = adm.patrimonio.baixa.DoacaoWindow.superclass.getFormPanel.call(this);

            this._formPanel.insert(1, {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Favorecido',
                allowBlank: true,
                rest: 'rh.person.Restful',
                name: 'favorecido',
                displayField: 'nome',
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    columnAction: false,
                }
            });
        }

        return this._formPanel;
    }
});

adm.patrimonio.baixa.Grid.register(
    'nota-baixa-doacao',
    'Nota de Doação',
    'icon-patrimonio icon-pat-nota-baixa-doacao',
    'adm.patrimonio.baixa.DoacaoWindow'
);
