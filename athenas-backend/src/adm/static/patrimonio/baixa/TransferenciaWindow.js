/**
 *
 **/
Ext._define('adm.patrimonio.baixa.TransferenciaWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.TransferenciaRestful',

    getFormPanel: function() {
        if(!this._formPanel) {
            this._formPanel = adm.patrimonio.baixa.TransferenciaWindow.superclass.getFormPanel.call(this);

            this._formPanel.insert(1, {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Favorecido',
                allowBlank: true,
                rest: 'adm.patrimonio.parametro.ContaRestful',
                name: 'favorecido',
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    columnAction: false,
                    hideColumns: ['prefix', 'sufix']
                }
            });
        }

        return this._formPanel;
    }
});

adm.patrimonio.baixa.Grid.register(
    'nota-baixa-transferencia',
    'Nota de Transferência',
    'icon-patrimonio icon-pat-nota-baixa-transferencia',
    'adm.patrimonio.baixa.TransferenciaWindow'
);
