/**
 *
 **/
Ext._define('adm.patrimonio.baixa.AlienacaoWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.AlienacaoRestful',

    getFormPanel: function() {
        if(!this._formPanel) {
            this._formPanel = adm.patrimonio.baixa.AlienacaoWindow.superclass.getFormPanel.call(this);

            this._formPanel.insert(1, {
                xtype: 'rest-autocompletefield',
                fieldLabel: "Arrematador",
                allowBlank: true,
                rest: 'rh.person.Restful',
                name: 'arrematante',
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
    'nota-baixa-alienacao',
    'Nota de Alienação',
    'icon-patrimonio icon-pat-nota-baixa-alienacao',
    'adm.patrimonio.baixa.AlienacaoWindow'
);
