/**
 *
 **/
Ext._define('edocs.processo.config.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getFormPanel: function(record) {
        if(!this._formPanel)
            this._formPanel = Ext._create('edocs.processo.config.Panel', {
                region: 'center',
                frame: true,
                values: record,
                oId: record.pk,
            });

        return this._formPanel;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Configuração e-PAD',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getFormPanel(cfg.values),

                ]
            }
        );

        edocs.processo.config.Manager.superclass.constructor.call(this, cfg);
    }
});

