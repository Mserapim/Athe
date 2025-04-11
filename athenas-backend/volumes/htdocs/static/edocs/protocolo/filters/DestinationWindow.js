
Ext._define('edocs.protocolo.filters.DestinationWindow', {
    extend: 'edocs.protocolo.filters.FilterWindow',

    width: 550,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 120,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'servidor_destino',
                        rest: 'rh.employee.Restful',
                        fieldLabel: 'Servidor',
                        width: 395,
                        allowBlank: true
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'lotacao_destino',
                        rest: 'rh.workplace.Restful',
                        fieldLabel: 'Local',
                        width: 395,
                        allowBlank: true
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Selecionar destino do documento(Pessoa ou Local)'
            }
        );

        edocs.protocolo.filters.DestinationWindow.superclass.constructor.call(this, cfg);
    }
});
