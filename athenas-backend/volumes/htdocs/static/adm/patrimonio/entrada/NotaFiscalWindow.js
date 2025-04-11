/**
 *
 **/
Ext._define('adm.patrimonio.entrada.NotaFiscalWindow', {
    extend: 'adm.patrimonio.entrada.Window',

    rest: 'adm.patrimonio.entrada.NotaFiscalRestful',

    tabHeight: 315,

    getTabForm: function() {
        if(!this._tabForm) {
            this._tabForm = adm.patrimonio.entrada.NotaFiscalWindow.superclass.getTabForm.call(this);

            this._tabForm.insert(2, {
                xtype: 'textfield',
                fieldLabel: 'Número da Nota',
                name: 'numero',
                allowBlank: false
            });
        }

        return this._tabForm;
    }
});

adm.patrimonio.entrada.Grid.register(
    'nota-fiscal',
    'Nota Físcal',
    'icon-patrimonio icon-pat-nota-fiscal',
    'adm.patrimonio.entrada.NotaFiscalWindow'
);
