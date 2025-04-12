/**
 *
 **/
Ext._define('adm.patrimonio.parametro.ContaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.parametro.ContaRestful',

    width: 450,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                defaults: {
                    width: 315
                },
                items: [
                    {
                        fieldLabel: 'Tipo',
                        xtype: 'combo',
                        hiddenName: 'tipo',
                        store: [
                            [1, 'Controlado'],
                            [2, 'Relacionado']
                        ],
                        allowBlank: false,
                        value: 1,
                        triggerAction: 'all'
                    },
                    {
                        fieldLabel: 'Prefixo',
                        xtype: 'textfield',
                        name: 'prefix',
                        allowBlank: true
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Sequência',
                        name: 'sequencia',
                        allowBlank: false,
                        rest: 'adm.patrimonio.parametro.SequenciaRestful',
                        comboListeners: {
                            select: function() {
                                console.debug('aki');
                            }
                        }
                    },
                    {
                        fieldLabel: 'Sufixo',
                        xtype: 'textfield',
                        name: 'sufix',
                        allowBlank: true
                    },
                    {
                        fieldLabel: 'Título',
                        xtype: 'textarea',
                        name: 'titulo',
                        allowBlank: false
                    },
                    {
                        fieldLabel: 'Principal',
                        xtype: 'checkbox',
                        name: 'principal',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    }
});
