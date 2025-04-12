/**
 *
 **/
Ext._define('adm.patrimonio.entrada.NotaConveniolWindow', {
    extend: 'adm.patrimonio.entrada.NotaFiscalWindow',

    rest: 'adm.patrimonio.entrada.NotaConvenioRestful',

    tabHeight: 395,

    getTabForm: function() {
        if(!this._tabForm) {
            this._tabForm = adm.patrimonio.entrada.NotaConveniolWindow.superclass.getTabForm.call(this);

            this._tabForm.insert(1, {
                xtype: 'panel',
                layout: 'hbox',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'form',
                        width: 285,
                        items: {
                            xtype: 'datefield',
                            name: 'data_convenio',
                            fieldLabel: 'Data de Inicio'
                        }
                    },
                    {
                        xtype: 'panel',
                        layout: 'form',
                        labelWidth: 120,
                        flex: 1.0,
                        items: {
                            xtype: 'datefield',
                            name: 'data_fim_convenio',
                            fieldLabel: 'Data de Termino'
                        }
                    }
                ]
            });

            this._tabForm.insert(1, {
                xtype: 'textfield',
                fieldLabel: 'Numero do Convênio',
                name: 'codigo_convenio'
            });

            this._tabForm.insert(1, {
                xtype: 'rest-autocompletefield',
                fieldLabel: "Conveniada",
                allowBlank: true,
                rest: "rh.person.legalperson.Restful",
                name: "conveniada"
            });
        }

        return this._tabForm;
    }
});

adm.patrimonio.entrada.Grid.register(
    'nota-convenio',
    'Nota Físcal de Convênio',
    'icon-patrimonio icon-pat-nota-fiscal-convenio',
    'adm.patrimonio.entrada.NotaConveniolWindow'
);
