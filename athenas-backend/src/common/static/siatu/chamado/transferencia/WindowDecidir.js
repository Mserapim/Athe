/**
 *
 **/
Ext._define('common.siatu.transferencia.WindowDecidir', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.transferencia.Restful',

    // width: 400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 200,
                items: [
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Aceita a transferência do chamado',
                        columns: 1,
                        items: [
                            {
                                xtype:'radio',
                                inputValue:'Yes',
                                boxLabel: 'Sim',
                                name: 'resposta'
                            },
                            {
                                xtype:'radio',
                                inputValue:'No',
                                boxLabel: 'Não',
                                checked: true,
                                name: 'resposta'
                            }
                        ]
                    }

                ]
            });

        return this._formPanel;
    }
});
