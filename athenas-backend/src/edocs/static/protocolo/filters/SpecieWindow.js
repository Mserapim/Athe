
Ext._define('edocs.protocolo.filters.SpecieWindow', {
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
                        name: 'protocolo__tipo_documento',
                        rest: 'edocs.protocolo.TipoDocumentoRestful',
                        fieldLabel: 'Tipo de documento',
                        width: 395,
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
                title: 'Selecionar origem do documento'
            }
        );

        edocs.protocolo.filters.SpecieWindow.superclass.constructor.call(this, cfg);
    }
});
