
Ext._define('edocs.protocolo.filters.InterestedWindow', {
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
                        name: 'protocolo__interessado',
                        rest: 'rh.person.Restful',
                        fieldLabel: 'Interessado',
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
                title: 'Selecionar interessado'
            }
        );

        edocs.protocolo.filters.InterestedWindow.superclass.constructor.call(this, cfg);
    }
});
