/**
 *
 **/
Ext._define('edocs.processo.referencia.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.referencia.Restful',

    width: 450,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'referenciado',
                        fieldLabel: 'Processo',
                        allowBlank: false,
                        rest: 'edocs.processo.consulta.processoComumRestful',
                    },
                    {
                        xtype: 'combo',
                        fieldLabel: 'Tipo',
                        hiddenName: 'tipo',
                        width: 355,
                        triggerAction: 'all',
                        allowBlank: false,
                        store: [
                            [1, 'Anexação'],
                            [2, 'Apensação'],
                            [3, 'Desapensação']
                        ],
                    },
                    {
                        width: 356,
                        xtype: 'textarea',
                        name: 'descricao',
                        fieldLabel: 'Descricao',
                        allowBlank: false,
                    },
                ]
            });

        return this._formPanel;
    }
});
