
Ext._define('edocs.protocolo.filters.SendedByWindow', {
    extend: 'edocs.protocolo.filters.FilterWindow',

    width: 550,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'servidor_origem',
                        rest: 'rh.employee.Restful',
                        fieldLabel: 'Remetente',
                        width: 415,
                        allowBlank: false
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
                title: 'Selecionar remetente'
            }
        );

        edocs.protocolo.filters.SendedByWindow.superclass.constructor.call(this, cfg);
    }
});
