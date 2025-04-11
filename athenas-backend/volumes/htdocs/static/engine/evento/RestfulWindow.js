/**
 *
 **/
Ext._define('engine.evento.RestfulWindow', {
    'extend': 'core.RestfulWindow',

    'rest': 'engine.evento.Restful',

    'width': 435,

    'getFormPanel': function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                'border': false,
                'frame': true,
                'items': [
                    {
                        'fieldLabel': 'Título',
                        'xtype': 'textfield',
                        'name': 'title',
                        'maxLenght': 100,
                        'allowBlank': false,
                        'width': 300
                    },
                    {
                        'fieldLabel': 'Inicia em',
                        'xtype': 'tk-datetimefield',
                        'name': 'start_date',
                        'allowBlank': false
                    },
                    {
                        'fieldLabel': 'Finaliza em',
                        'xtype': 'tk-datetimefield',
                        'name': 'end_date',
                        'allowBlank': true
                    },
                    {
                        'fieldLabel': 'Recurso',
                        'xtype': 'textfield',
                        'name': 'resource',
                        'maxLenght': 200,
                        'allowBlank': false,
                        'width': 300
                    },
                    {
                        'fieldLabel': 'Interface',
                        'xtype': 'textfield',
                        'name': 'interface',
                        'maxLenght': 200,
                        'allowBlank': false,
                        'width': 300
                    },
                ]
            });

        return this._formPanel;
    }
});
